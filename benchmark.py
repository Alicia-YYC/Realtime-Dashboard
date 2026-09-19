"""Measure full refresh cycles, saving all timings and source outcomes.

Live mode calls the application's four configured sources. Controlled mode
uses four simulated I/O-bound sources with fixed delays and no network calls.
Controlled results must never be presented as live-API performance.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import statistics
from time import perf_counter, sleep
from typing import Callable

from reliability import DataManager


def delayed_source(delay: float) -> Callable[[], dict]:
    def fetch() -> dict:
        sleep(delay)
        return {"simulated": True, "delay_seconds": delay}
    return fetch


def measure(manager: DataManager, concurrent: bool) -> dict:
    started = perf_counter()
    snapshots = manager.refresh_once(concurrent=concurrent)
    elapsed = perf_counter() - started
    return {
        "elapsed_seconds": elapsed,
        "all_healthy": bool(snapshots) and all(
            item.status == "healthy" for item in snapshots.values()
        ),
        "sources": {
            name: {
                "status": item.status,
                "latency_ms": item.latency_ms,
                "message": item.message,
            }
            for name, item in snapshots.items()
        },
    }


def summarize(pairs: list[dict]) -> dict:
    """Only compare pairs in which every source succeeded in both modes."""
    valid = [
        pair for pair in pairs
        if pair["sequential"]["all_healthy"] and pair["concurrent"]["all_healthy"]
    ]
    status_counts = {mode: Counter() for mode in ("sequential", "concurrent")}
    for pair in pairs:
        for mode, counts in status_counts.items():
            counts.update(source["status"] for source in pair[mode]["sources"].values())
    result = {
        "measured_pairs": len(pairs),
        "eligible_pairs": len(valid),
        "excluded_pairs": len(pairs) - len(valid),
        "source_status_counts": {mode: dict(counts) for mode, counts in status_counts.items()},
        "sequential_median_seconds": None,
        "concurrent_median_seconds": None,
        "median_refresh_reduction_percent": None,
        "speedup": None,
    }
    if valid:
        sequential = statistics.median(pair["sequential"]["elapsed_seconds"] for pair in valid)
        concurrent = statistics.median(pair["concurrent"]["elapsed_seconds"] for pair in valid)
        result.update({
            "sequential_median_seconds": sequential,
            "concurrent_median_seconds": concurrent,
            "median_refresh_reduction_percent": (1 - concurrent / sequential) * 100,
            "speedup": sequential / concurrent,
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("live", "controlled"), default="controlled")
    parser.add_argument("--rounds", type=int, default=10, help="Number of measured pairs")
    parser.add_argument("--warmup", type=int, default=1, help="Unmeasured pairs for connection warm-up")
    parser.add_argument("--pause", type=float, default=60.0, help="Seconds between live cycles (not timed)")
    parser.add_argument("--delays", type=float, nargs=4, default=[0.1, 0.2, 0.3, 0.4],
                        help="Controlled-mode simulated source delays, in seconds")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.rounds < 1 or args.warmup < 0 or args.pause < 0 or any(d <= 0 for d in args.delays):
        parser.error("rounds and delays must be positive; warmup and pause must be nonnegative")

    started_at = datetime.now(timezone.utc).isoformat()
    if args.mode == "live":
        import config
        from data_sources import build_default_manager
        # Separate managers give each mode its own requests.Session instances.
        managers = {mode: build_default_manager() for mode in ("sequential", "concurrent")}
        settings = {
            "stock_symbols": list(config.STOCK_SYMBOLS),
            "request_timeout_seconds": config.REQUEST_TIMEOUT_SECONDS,
            "weather_location": config.WEATHER_LOCATION,
            "weather_latitude": config.WEATHER_LATITUDE,
            "weather_longitude": config.WEATHER_LONGITUDE,
            "hacker_news_story_limit": 5,
            "pause_between_cycles_seconds": args.pause,
        }
    else:
        managers = {
            mode: DataManager({f"simulated_{i + 1}": delayed_source(delay)
                               for i, delay in enumerate(args.delays)})
            for mode in ("sequential", "concurrent")
        }
        settings = {"simulated_io_delays_seconds": args.delays, "network_requests": False}

    warmups, pairs = [], []
    for index in range(args.warmup + args.rounds):
        order = ["sequential", "concurrent"] if index % 2 == 0 else ["concurrent", "sequential"]
        pair = {"order": order}
        for mode in order:
            pair[mode] = measure(managers[mode], concurrent=(mode == "concurrent"))
            if args.mode == "live" and args.pause:
                sleep(args.pause)
        if index < args.warmup:
            warmups.append(pair)
            label = f"Warm-up {index + 1}"
        else:
            pairs.append(pair)
            label = f"Pair {len(pairs)}/{args.rounds}"
        print(f"{label}: sequential={pair['sequential']['elapsed_seconds']:.3f}s, "
              f"concurrent={pair['concurrent']['elapsed_seconds']:.3f}s, "
              f"all healthy={pair['sequential']['all_healthy'] and pair['concurrent']['all_healthy']}",
              flush=True)

    report = {
        "schema_version": 1,
        "mode": args.mode,
        "started_at_utc": started_at,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "settings": settings,
        "methodology": {
            "timed_scope": "DataManager.refresh_once including polling, snapshots, and history updates",
            "comparison": "same polling implementation with sequential vs ThreadPoolExecutor execution",
            "order": "alternates between sequential-first and concurrent-first",
            "eligibility": "all sources healthy in BOTH cycles of a measured pair",
            "formula": "100 * (1 - median(concurrent) / median(sequential)) over eligible pairs",
            "limitations": "single-process microbenchmark; not a production throughput or SLA measurement",
        },
        "warmup_pairs": warmups,
        "pairs": pairs,
        "summary": summarize(pairs),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Saved raw results to {args.output}")


if __name__ == "__main__":
    main()
