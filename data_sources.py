from __future__ import annotations

from typing import Any, Callable

import requests

import config
from reliability import DataManager, FetchResult


Fetcher = Callable[[], Any]


def _session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Realtime-Dashboard/1.0 "
                "(https://github.com/Alicia-YYC/Realtime-Dashboard)"
            )
        }
    )
    return session


class WeatherSource:
    endpoint = "https://api.open-meteo.com/v1/forecast"

    def __init__(
        self,
        location: str,
        latitude: float,
        longitude: float,
        timeout: float,
    ) -> None:
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
        self.timeout = timeout
        self.session = _session()

    def __call__(self) -> dict[str, Any]:
        response = self.session.get(
            self.endpoint,
            params={
                "latitude": self.latitude,
                "longitude": self.longitude,
                "current": (
                    "temperature_2m,relative_humidity_2m,"
                    "apparent_temperature,weather_code"
                ),
                "timezone": "auto",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        current = response.json()["current"]
        return {
            "location": self.location,
            "temperature_c": current["temperature_2m"],
            "feels_like_c": current["apparent_temperature"],
            "humidity_percent": current["relative_humidity_2m"],
            "weather_code": current["weather_code"],
            "observed_at": current["time"],
        }


class StockSource:
    endpoint = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

    def __init__(self, symbols: tuple[str, ...], timeout: float) -> None:
        self.symbols = symbols
        self.timeout = timeout
        self.session = _session()

    def __call__(self) -> FetchResult:
        quotes: list[dict[str, Any]] = []
        failures: list[str] = []

        for symbol in self.symbols:
            try:
                response = self.session.get(
                    self.endpoint.format(symbol=symbol),
                    params={"range": "1d", "interval": "5m"},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                result = response.json()["chart"]["result"][0]
                metadata = result["meta"]
                price = metadata.get("regularMarketPrice")
                previous_close = metadata.get("chartPreviousClose")

                if price is None:
                    raise ValueError("price was missing from the response")

                change_percent = None
                if previous_close:
                    change_percent = (price - previous_close) / previous_close * 100

                quotes.append(
                    {
                        "symbol": symbol,
                        "price": float(price),
                        "change_percent": change_percent,
                        "currency": metadata.get("currency", "USD"),
                        "market_state": metadata.get("marketState", "UNKNOWN"),
                    }
                )
            except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
                failures.append(f"{symbol}: {exc}")

        if not quotes:
            raise RuntimeError("; ".join(failures) or "no stock quotes were returned")

        warning = None
        if failures:
            warning = f"{len(failures)} of {len(self.symbols)} symbols failed"

        return FetchResult(data=quotes, warning=warning)


class CryptoSource:
    endpoint = "https://api.coingecko.com/api/v3/simple/price"

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout
        self.session = _session()

    def __call__(self) -> dict[str, Any]:
        response = self.session.get(
            self.endpoint,
            params={
                "ids": "bitcoin",
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        bitcoin = response.json()["bitcoin"]
        return {
            "price_usd": float(bitcoin["usd"]),
            "change_24h_percent": float(bitcoin["usd_24h_change"]),
        }


class HackerNewsSource:
    top_stories_endpoint = "https://hacker-news.firebaseio.com/v0/topstories.json"
    item_endpoint = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"

    def __init__(self, timeout: float, limit: int = 5) -> None:
        self.timeout = timeout
        self.limit = limit
        self.session = _session()

    def __call__(self) -> FetchResult:
        response = self.session.get(self.top_stories_endpoint, timeout=self.timeout)
        response.raise_for_status()
        story_ids = response.json()[: self.limit]

        stories: list[dict[str, Any]] = []
        failures = 0
        for item_id in story_ids:
            try:
                item_response = self.session.get(
                    self.item_endpoint.format(item_id=item_id),
                    timeout=self.timeout,
                )
                item_response.raise_for_status()
                item = item_response.json()
                stories.append(
                    {
                        "title": item["title"],
                        "url": item.get(
                            "url",
                            f"https://news.ycombinator.com/item?id={item_id}",
                        ),
                        "score": item.get("score"),
                    }
                )
            except (requests.RequestException, KeyError, TypeError):
                failures += 1

        if not stories:
            raise RuntimeError("no Hacker News stories were returned")

        warning = f"{failures} story requests failed" if failures else None
        return FetchResult(data=stories, warning=warning)


def build_default_manager() -> DataManager:
    timeout = config.REQUEST_TIMEOUT_SECONDS
    sources: dict[str, Fetcher] = {
        "weather": WeatherSource(
            location=config.WEATHER_LOCATION,
            latitude=config.WEATHER_LATITUDE,
            longitude=config.WEATHER_LONGITUDE,
            timeout=timeout,
        ),
        "stocks": StockSource(config.STOCK_SYMBOLS, timeout),
        "crypto": CryptoSource(timeout),
        "news": HackerNewsSource(timeout),
    }
    return DataManager(
        sources=sources,
        poll_interval_seconds=config.POLL_INTERVAL_SECONDS,
        history_limit=config.HISTORY_LIMIT,
    )
