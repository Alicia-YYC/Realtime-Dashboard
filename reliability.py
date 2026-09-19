from __future__ import annotations

from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Event, RLock, Thread
from time import perf_counter
from typing import Any, Callable


Fetcher = Callable[[], Any]


@dataclass(frozen=True)
class FetchResult:
    data: Any
    warning: str | None = None


@dataclass(frozen=True)
class SourceSnapshot:
    source: str
    status: str
    data: Any
    checked_at: datetime
    last_success_at: datetime | None
    latency_ms: int
    message: str | None = None


class DataManager:
    def __init__(
        self,
        sources: dict[str, Fetcher],
        poll_interval_seconds: int = 60,
        history_limit: int = 120,
    ) -> None:
        self.sources = sources
        self.poll_interval_seconds = poll_interval_seconds
        self._snapshots: dict[str, SourceSnapshot] = {}
        self._history: dict[str, deque[dict[str, Any]]] = {
            name: deque(maxlen=history_limit) for name in sources
        }
        self._lock = RLock()
        self._stop_event = Event()
        self._thread: Thread | None = None

    def _fetch_one(self, name: str, fetcher: Fetcher) -> SourceSnapshot:
        checked_at = datetime.now(timezone.utc)
        started = perf_counter()

        try:
            raw_result = fetcher()
            result = (
                raw_result
                if isinstance(raw_result, FetchResult)
                else FetchResult(data=raw_result)
            )
            latency_ms = round((perf_counter() - started) * 1000)
            return SourceSnapshot(
                source=name,
                status="degraded" if result.warning else "healthy",
                data=result.data,
                checked_at=checked_at,
                last_success_at=checked_at,
                latency_ms=latency_ms,
                message=result.warning,
            )
        except Exception as exc:
            latency_ms = round((perf_counter() - started) * 1000)
            with self._lock:
                previous = self._snapshots.get(name)

            if previous and previous.data is not None:
                return SourceSnapshot(
                    source=name,
                    status="stale",
                    data=previous.data,
                    checked_at=checked_at,
                    last_success_at=previous.last_success_at,
                    latency_ms=latency_ms,
                    message=str(exc),
                )

            return SourceSnapshot(
                source=name,
                status="error",
                data=None,
                checked_at=checked_at,
                last_success_at=None,
                latency_ms=latency_ms,
                message=str(exc),
            )

    def refresh_once(self, *, concurrent: bool = True) -> dict[str, SourceSnapshot]:
        """Refresh all sources; sequential mode provides a benchmark baseline."""
        completed: dict[str, SourceSnapshot] = {}
        if concurrent:
            with ThreadPoolExecutor(max_workers=max(1, len(self.sources))) as executor:
                futures = {
                    executor.submit(self._fetch_one, name, fetcher): name
                    for name, fetcher in self.sources.items()
                }
                for future in as_completed(futures):
                    snapshot = future.result()
                    completed[snapshot.source] = snapshot
        else:
            completed = {
                name: self._fetch_one(name, fetcher)
                for name, fetcher in self.sources.items()
            }

        with self._lock:
            self._snapshots.update(completed)
            for name, snapshot in completed.items():
                self._history[name].append(
                    {
                        "checked_at": snapshot.checked_at,
                        "status": snapshot.status,
                        "latency_ms": snapshot.latency_ms,
                    }
                )
            return dict(self._snapshots)

    def get_snapshots(self) -> dict[str, SourceSnapshot]:
        with self._lock:
            return dict(self._snapshots)

    def get_health_history(self) -> dict[str, list[dict[str, Any]]]:
        with self._lock:
            return {name: list(records) for name, records in self._history.items()}

    def start(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._thread = Thread(
                target=self._poll,
                name="dashboard-data-poller",
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=2)

    def _poll(self) -> None:
        while not self._stop_event.is_set():
            started = perf_counter()
            self.refresh_once()
            elapsed = perf_counter() - started
            wait_seconds = max(0, self.poll_interval_seconds - elapsed)
            self._stop_event.wait(wait_seconds)
