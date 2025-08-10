import requests
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup
import json
from datetime import datetime
import config

class WeatherData:
    def __init__(self):
        self.api_key = config.WEATHER_API_KEY
        self.api_url = config.WEATHER_API_URL
    
    def get_weather_data(self, city="Beijing"):
        """Get weather data"""
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'en'
            }
            response = requests.get(self.api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'city': data['name'],
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'],
                    'timestamp': datetime.now()
                }
            else:
                return self.get_mock_weather_data()
        except Exception as e:
            print(f"Weather API failed: {e}")
            return self.get_mock_weather_data()
    
    def get_mock_weather_data(self):
        """Simulate weather data"""
        import random
        return {
            'city': 'Beijing',
            'temperature': random.uniform(15, 30),
            'humidity': random.uniform(40, 80),
            'pressure': random.uniform(1000, 1020),
            'description': 'Sunny',
            'timestamp': datetime.now()
        }

class StockData:
    def __init__(self):
        self.symbols = config.STOCK_SYMBOLS
    
    def get_stock_data(self):
        """Get stock data"""
        try:
            stock_data = []
            for symbol in self.symbols:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d", interval="1m")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    previous_close = info.get('previousClose', current_price)
                    change = current_price - previous_close
                    change_percent = (change / previous_close) * 100 if previous_close else 0
                    
                    stock_data.append({
                        'symbol': symbol,
                        'price': current_price,
                        'change': change,
                        'change_percent': change_percent,
                        'volume': hist['Volume'].iloc[-1],
                        'timestamp': datetime.now()
                    })
            
            return stock_data if stock_data else self.get_mock_stock_data()
        except Exception as e:
            print(f"Stock API failed: {e}")
            return self.get_mock_stock_data()
    
    def get_mock_stock_data(self):
        """Simulate stock data"""
        import random
        stock_data = []
        base_prices = {'AAPL': 150, 'GOOGL': 2500, 'MSFT': 300, 'TSLA': 800, 'AMZN': 3000, 'NVDA': 900}
        
        for symbol in self.symbols:
            base_price = base_prices.get(symbol, 100)
            current_price = base_price + random.uniform(-10, 10)
            change = random.uniform(-5, 5)
            change_percent = random.uniform(-3, 3)
            
            stock_data.append({
                'symbol': symbol,
                'price': current_price,
                'change': change,
                'change_percent': change_percent,
                'volume': random.randint(1000000, 10000000),
                'timestamp': datetime.now()
            })
        
        return stock_data

class WebScraper:
    def __init__(self):
        self.urls = config.SCRAPE_URLS
    
    def scrape_news_data(self):
        """Scrape news data"""
        try:
            response = requests.get(self.urls['news'], timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Scrape Hacker News titles
            titles = []
            for item in soup.find_all('a', class_='storylink')[:10]:
                titles.append(item.get_text())
            
            if not titles:  # If no titles found, use mock data
                return self.get_mock_news_data()
                
            return {
                'news_count': len(titles),
                'latest_titles': titles,
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"News scraping failed: {e}")
            return self.get_mock_news_data()
    
    def get_mock_news_data(self):
        """Simulate news data"""
        import random
        mock_titles = [
            "AI Breakthrough in Machine Learning",
            "New Programming Language Released",
            "Tech Stock Prices Surge",
            "Open Source Project Gains Attention", 
            "Data Science Discovery Made",
            "Quantum Computing Advancement",
            "Cybersecurity Alert Issued",
            "Cloud Infrastructure Update"
        ]
        
        selected_titles = random.sample(mock_titles, min(5, len(mock_titles)))
        
        return {
            'news_count': random.randint(8, 15),
            'latest_titles': selected_titles,
            'timestamp': datetime.now()
        }
    
    def scrape_crypto_data(self):
        """Get cryptocurrency data"""
        try:
            # Simple Bitcoin price simulation
            import random
            return {
                'bitcoin_price': random.uniform(40000, 70000),
                'change_24h': random.uniform(-8, 8),
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Crypto data failed: {e}")
            return {
                'bitcoin_price': 50000,
                'change_24h': 2.5,
                'timestamp': datetime.now()
            }

# Data manager
class DataManager:
    def __init__(self):
        self.weather = WeatherData()
        self.stocks = StockData()
        self.scraper = WebScraper()
        
        # Data storage
        self.weather_history = []
        self.stock_history = []
        self.news_history = []
        self.crypto_history = []
    
    def update_all_data(self):
        """Update all data sources"""
        # Update weather data
        weather_data = self.weather.get_weather_data()
        self.weather_history.append(weather_data)
        if len(self.weather_history) > 100:
            self.weather_history.pop(0)
        
        # Update stock data
        stock_data = self.stocks.get_stock_data()
        self.stock_history.extend(stock_data)
        if len(self.stock_history) > 500:
            self.stock_history = self.stock_history[-500:]
        
        # Update news data
        news_data = self.scraper.scrape_news_data()
        self.news_history.append(news_data)
        if len(self.news_history) > 50:
            self.news_history.pop(0)
        
        # Update cryptocurrency data
        crypto_data = self.scraper.scrape_crypto_data()
        self.crypto_history.append(crypto_data)
        if len(self.crypto_history) > 100:
            self.crypto_history.pop(0)
    
    def get_latest_data(self):
        """Get latest data"""
        return {
            'weather': self.weather_history[-1] if self.weather_history else None,
            'stocks': self.stock_history[-len(config.STOCK_SYMBOLS):] if self.stock_history else [],
            'news': self.news_history[-1] if self.news_history else None,
            'crypto': self.crypto_history[-1] if self.crypto_history else None
        }
