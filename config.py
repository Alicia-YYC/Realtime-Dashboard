import os

from dotenv import load_dotenv


load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: str) -> tuple[str, ...]:
    value = os.getenv(name, default)
    return tuple(item.strip().upper() for item in value.split(",") if item.strip())


APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8050"))
DEBUG = _env_bool("DEBUG")

POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "8"))
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "120"))

STOCK_SYMBOLS = _env_list("STOCK_SYMBOLS", "AAPL,GOOGL,MSFT,NVDA")

WEATHER_LOCATION = os.getenv("WEATHER_LOCATION", "Pittsburgh")
WEATHER_LATITUDE = float(os.getenv("WEATHER_LATITUDE", "40.4406"))
WEATHER_LONGITUDE = float(os.getenv("WEATHER_LONGITUDE", "-79.9959"))

