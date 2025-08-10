# Configuration file
import os
from dotenv import load_dotenv

load_dotenv()

# API configuration
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', 'your_weather_api_key')
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# Stock API configuration (using yfinance, no API key required)
STOCK_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA']

# Web scraping target websites
SCRAPE_URLS = {
    'news': 'https://news.ycombinator.com/',
    'bitcoin': 'https://coinmarketcap.com/currencies/bitcoin/'
}

# Update interval (seconds)
UPDATE_INTERVAL = 30

# Application configuration
APP_HOST = '127.0.0.1'
APP_PORT = 8050
DEBUG = True
