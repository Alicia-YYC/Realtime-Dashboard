# Real-Time Data Dashboard

A modern, responsive real-time data visualization dashboard built with Python Dash framework. This dashboard provides live monitoring of stocks, weather, cryptocurrencies, and news feeds with a clean, professional business minimalist design.

![Dashboard Preview](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Dashboard Preview](https://img.shields.io/badge/Dash-2.17.1+-green.svg)
![Dashboard Preview](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **📈 Real-time Stock Monitoring** - Live tracking of major stocks (AAPL, GOOGL, MSFT, TSLA, AMZN, NVDA)
- **🌤️ Weather Information** - Current weather data with OpenWeatherMap integration
- **₿ Cryptocurrency Tracker** - Real-time Bitcoin price monitoring
- **📰 News Feed** - Live updates from Hacker News
- **⚡ System Status** - Real-time system performance monitoring
- **🔄 Auto-refresh** - Automatic data updates every 30 seconds
- **🎨 Responsive Design** - Clean business minimalist interface
- **📱 Mobile Friendly** - Optimized for all screen sizes

## 🛠️ Technology Stack

- **Backend Framework**: Python Dash
- **Data Visualization**: Plotly
- **Data Processing**: Pandas
- **Stock Data**: Yahoo Finance (yfinance)
- **Weather API**: OpenWeatherMap
- **Web Scraping**: BeautifulSoup4
- **System Monitoring**: psutil
- **Styling**: Custom CSS with modern design principles

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/realtime-dashboard.git
   cd realtime-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

4. **Open your browser**
   Navigate to `http://127.0.0.1:8050`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```env
WEATHER_API_KEY=your_openweathermap_api_key
```

### Customization

Edit `config.py` to customize:

- **Stock Symbols**: Add/remove stocks to monitor
- **Update Interval**: Change data refresh frequency (default: 30 seconds)
- **API Endpoints**: Modify data source URLs
- **App Settings**: Host, port, and debug mode

```python
# Example configuration
STOCK_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA']
UPDATE_INTERVAL = 30  # seconds
APP_HOST = '127.0.0.1'
APP_PORT = 8050
```

## 📁 Project Structure

```
realtime-dashboard/
├── app.py              # Main Dash application
├── config.py           # Configuration settings
├── data_sources.py     # Data fetching and management
├── run.py              # Application launcher
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── assets/
    └── styles.css      # Custom styling
```

## 🔧 API Integration

### Stock Data
- **Source**: Yahoo Finance (yfinance)
- **Features**: Real-time prices, change percentages, volume
- **Rate Limit**: Subject to Yahoo Finance API limits
- **No API Key Required**: Free to use

### Weather Data
- **Source**: OpenWeatherMap
- **Features**: Current temperature, conditions, humidity
- **API Key**: Required (free tier available)
- **Rate Limit**: 1000 calls/day (free tier)

### News Data
- **Source**: Hacker News
- **Features**: Top stories, real-time updates
- **No API Key Required**: Web scraping based
- **Rate Limit**: Respectful scraping practices

### Cryptocurrency
- **Source**: CoinMarketCap
- **Features**: Bitcoin price, market cap
- **No API Key Required**: Web scraping based
- **Rate Limit**: Respectful scraping practices

## 🎨 Customization

### Theme Switching

The dashboard supports multiple visual themes:

1. **Business Minimalist** (Default)
   - Professional color scheme
   - Clean typography
   - Subtle shadows and borders

2. **Custom Themes**
   - Modify `assets/styles.css`
   - Update color variables
   - Adjust component styling

### Adding New Data Sources

1. **Create data fetching function** in `data_sources.py`
2. **Add callback function** in `app.py`
3. **Update layout** to display new data
4. **Configure** in `config.py`

## 📊 Data Update Schedule

- **Stocks**: Every 30 seconds
- **Weather**: Every 30 seconds
- **Cryptocurrency**: Every 30 seconds
- **News**: Every 30 seconds
- **System Status**: Every 30 seconds
- **Current Time**: Every second

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Windows
   netstat -ano | findstr :8050
   taskkill /PID <PID> /F
   
   # Linux/Mac
   lsof -ti:8050 | xargs kill -9
   ```

2. **API Rate Limits**
   - Stock data: Wait for rate limit reset
   - Weather API: Check API key and limits
   - News: Reduce update frequency

3. **Dependencies Issues**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

### Error Handling

The dashboard includes comprehensive error handling:
- Graceful fallbacks for API failures
- User-friendly error messages
- Automatic retry mechanisms
- Offline data simulation

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

1. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/realtime-dashboard.git
   cd realtime-dashboard
   ```

2. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8
   ```

3. **Run tests** (when available)
   ```bash
   pytest
   ```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Dash](https://dash.plotly.com/) - Web application framework
- [Plotly](https://plotly.com/) - Interactive plotting library
- [Yahoo Finance](https://finance.yahoo.com/) - Stock data provider
- [OpenWeatherMap](https://openweathermap.org/) - Weather data API
- [Hacker News](https://news.ycombinator.com/) - News source

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/realtime-dashboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/realtime-dashboard/discussions)
- **Email**: your-email@example.com

## 🔮 Roadmap

- [ ] Additional stock exchanges support
- [ ] Historical data charts
- [ ] User authentication
- [ ] Custom dashboard layouts
- [ ] Export functionality
- [ ] Mobile app version
- [ ] Real-time alerts
- [ ] Social media integration

---

**⭐ If you find this project helpful, please give it a star!**

**Made with ❤️ by [Your Name]**
