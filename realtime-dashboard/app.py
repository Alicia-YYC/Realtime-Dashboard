import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import config
from data_sources import DataManager

# Initialize Dash application
app = dash.Dash(__name__, external_stylesheets=['https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;700&display=swap'])
app.title = "Real-Time Data Visualization Dashboard"

# Initialize data manager
data_manager = DataManager()

# Define application layout
app.layout = html.Div([
    # Main title
    html.H1("🔴 REAL-TIME DATA DASHBOARD", className="dashboard-title"),
    
    # Status bar
    html.Div([
        html.Span(className="status-indicator"),
        html.Span("SYSTEM ONLINE", style={'color': '#3b82f6', 'font-family': 'Inter, sans-serif'}),
        html.Span(id="current-time", style={'float': 'right', 'color': '#64748b', 'font-family': 'Inter, sans-serif'})
    ], style={'text-align': 'center', 'padding': '10px', 'background': '#1a1a1a', 'margin': '10px'}),
    
    # First row: Weather and Cryptocurrency
    html.Div([
        html.Div([
            html.H3("🌤️ WEATHER MONITOR", className="card-title"),
            html.Div(id="weather-display")
        ], className="data-card", style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3("₿ CRYPTO TRACKER", className="card-title"),
            html.Div(id="crypto-display")
        ], className="data-card", style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ]),
    
    # Second row: Stock chart
    html.Div([
        html.H3("📈 STOCK MARKET LIVE", className="card-title"),
        dcc.Graph(id="stock-chart")
    ], className="chart-container"),
    
    # Third row: News and System information
    html.Div([
        html.Div([
            html.H3("📰 NEWS FEED", className="card-title"),
            html.Div(id="news-display")
        ], className="data-card", style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3("⚡ SYSTEM STATUS", className="card-title"),
            html.Div(id="system-display")
        ], className="data-card", style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ]),
    
    # Auto-refresh component
    dcc.Interval(
        id='interval-component',
        interval=config.UPDATE_INTERVAL * 1000,  # Convert to milliseconds
        n_intervals=0
    ),
    
    # Time update component
    dcc.Interval(
        id='time-interval',
        interval=1000,  # Update every second
        n_intervals=0
    )
], className="main-container")

# Callback function: Update current time
@app.callback(
    Output('current-time', 'children'),
    Input('time-interval', 'n_intervals')
)
def update_time(n):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Callback function: Update weather display
@app.callback(
    Output('weather-display', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_weather(n):
    latest_data = data_manager.get_latest_data()
    weather = latest_data.get('weather')
    
    if not weather:
        return html.Div("LOADING WEATHER DATA...", className="loading")
    
    return html.Div([
        html.Div([
            html.Span("CITY:", className="data-label"),
            html.Span(weather['city'], className="data-value")
        ], className="data-item"),
        html.Div([
            html.Span("TEMP:", className="data-label"),
            html.Span(f"{weather['temperature']:.1f}°C", className="data-value")
        ], className="data-item"),
        html.Div([
            html.Span("HUMIDITY:", className="data-label"),
            html.Span(f"{weather['humidity']}%", className="data-value")
        ], className="data-item"),
        html.Div([
            html.Span("PRESSURE:", className="data-label"),
            html.Span(f"{weather['pressure']} hPa", className="data-value")
        ], className="data-item"),
        html.Div([
            html.Span("STATUS:", className="data-label"),
            html.Span(weather['description'], className="data-value")
        ], className="data-item"),
        html.Div(f"LAST UPDATE: {weather['timestamp'].strftime('%H:%M:%S')}", className="update-time")
    ])

# Callback function: Update cryptocurrency display
@app.callback(
    Output('crypto-display', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_crypto(n):
    latest_data = data_manager.get_latest_data()
    crypto = latest_data.get('crypto')
    
    if not crypto:
        return html.Div("LOADING CRYPTO DATA...", className="loading")
    
    change_class = "positive" if crypto['change_24h'] >= 0 else "negative"
    change_symbol = "+" if crypto['change_24h'] >= 0 else ""
    
    return html.Div([
        html.Div([
            html.Span("BTC PRICE:", className="data-label"),
            html.Span(f"${crypto['bitcoin_price']:,.2f}", className="data-value")
        ], className="data-item"),
        html.Div([
            html.Span("24H CHANGE:", className="data-label"),
            html.Span(f"{change_symbol}{crypto['change_24h']:.2f}%", className=f"data-value {change_class}")
        ], className="data-item"),
        html.Div(f"LAST UPDATE: {crypto['timestamp'].strftime('%H:%M:%S')}", className="update-time")
    ])

# Callback function: Update stock chart
@app.callback(
    Output('stock-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_stock_chart(n):
    latest_data = data_manager.get_latest_data()
    stocks = latest_data.get('stocks', [])
    
    if not stocks:
        # Return empty chart
        fig = go.Figure()
        fig.update_layout(
            title="LOADING STOCK DATA...",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#64748b'
        )
        return fig
    
            # Create stock price bar chart
    symbols = [stock['symbol'] for stock in stocks]
    prices = [stock['price'] for stock in stocks]
    changes = [stock['change_percent'] for stock in stocks]
    
            # Set colors based on price changes
    colors = ['#10b981' if change >= 0 else '#ef4444' for change in changes]
    
    fig = go.Figure()
    
            # Add price bar chart
    fig.add_trace(go.Bar(
        x=symbols,
        y=prices,
        marker_color=colors,
        name="STOCK PRICE",
        text=[f"${price:.2f}<br>{change:+.2f}%" for price, change in zip(prices, changes)],
        textposition="outside"
    ))
    
    fig.update_layout(
        title={
            'text': "📈 LIVE STOCK PRICES",
            'x': 0.5,
            'font': {'color': '#1e293b', 'size': 18}
        },
        xaxis={
            'title': "SYMBOL",
            'color': '#64748b',
            'gridcolor': 'rgba(100,116,139,0.2)'
        },
        yaxis={
            'title': "PRICE (USD)",
            'color': '#64748b',
            'gridcolor': 'rgba(100,116,139,0.2)'
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif', 'color': '#64748b'},
        showlegend=False,
        margin=dict(t=60, b=40, l=40, r=40)
    )
    
    return fig

# Callback function: Update news display
@app.callback(
    Output('news-display', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_news(n):
    latest_data = data_manager.get_latest_data()
    news = latest_data.get('news')
    
    if not news:
        return html.Div("LOADING NEWS DATA...", className="loading")
    
    news_items = []
    for i, title in enumerate(news['latest_titles'][:5], 1):
        news_items.append(
            html.Div(f"{i}. {title[:60]}{'...' if len(title) > 60 else ''}", className="news-item")
        )
    
    return html.Div([
        html.Div([
            html.Span("NEWS COUNT:", className="data-label"),
            html.Span(str(news['news_count']), className="data-value")
        ], className="data-item"),
        html.Div("LATEST HEADLINES:", style={'color': '#3b82f6', 'margin': '10px 0 5px 0', 'font-weight': '600'}),
        html.Div(news_items),
        html.Div(f"LAST UPDATE: {news['timestamp'].strftime('%H:%M:%S')}", className="update-time")
    ])

# Callback function: Update system status
@app.callback(
    Output('system-display', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_system_status(n):
    import psutil
    import platform
    
    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return html.Div([
            html.Div([
                html.Span("OS:", className="data-label"),
                html.Span(platform.system(), className="data-value")
            ], className="data-item"),
            html.Div([
                html.Span("CPU USAGE:", className="data-label"),
                html.Span(f"{cpu_percent}%", className="data-value")
            ], className="data-item"),
            html.Div([
                html.Span("MEMORY:", className="data-label"),
                html.Span(f"{memory.percent}%", className="data-value")
            ], className="data-item"),
            html.Div([
                html.Span("DISK:", className="data-label"),
                html.Span(f"{disk.percent}%", className="data-value")
            ], className="data-item"),
            html.Div([
                html.Span("UPTIME:", className="data-label"),
                html.Span(f"{n * config.UPDATE_INTERVAL}s", className="data-value")
            ], className="data-item"),
            html.Div(f"LAST UPDATE: {datetime.now().strftime('%H:%M:%S')}", className="update-time")
        ])
    except Exception as e:
        return html.Div([
            html.Div("SYSTEM INFO ERROR", style={'color': '#ef4444'}),
            html.Div(f"ERROR: {str(e)}", className="system-info")
        ])

# Background data update thread
def background_data_update():
    """Background data update"""
    while True:
        try:
            data_manager.update_all_data()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] DATA UPDATE COMPLETE")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] DATA UPDATE FAILED: {e}")
        time.sleep(config.UPDATE_INTERVAL)

        # Start background data update thread
data_thread = threading.Thread(target=background_data_update, daemon=True)
data_thread.start()

# Initialize data
data_manager.update_all_data()

if __name__ == '__main__':
    print("🚀 LAUNCHING REAL-TIME DASHBOARD...")
    print(f"📊 ACCESS URL: http://{config.APP_HOST}:{config.APP_PORT}")
    print(f"🔄 UPDATE INTERVAL: {config.UPDATE_INTERVAL}s")
    print("🎯 Press Ctrl+C to EXIT")
    
    app.run_server(
        host=config.APP_HOST,
        port=config.APP_PORT,
        debug=config.DEBUG
    )
