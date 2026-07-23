from __future__ import annotations

import atexit
from datetime import datetime, timezone

import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

import config
from data_sources import build_default_manager
from reliability import SourceSnapshot


SOURCE_LABELS = {
    "weather": "Open-Meteo",
    "stocks": "Yahoo Finance",
    "crypto": "CoinGecko",
    "news": "Hacker News",
}


app = Dash(__name__)
app.title = "Realtime Data Reliability Dashboard"
server = app.server

data_manager = build_default_manager()
data_manager.start()
atexit.register(data_manager.stop)


def _format_time(value: datetime | None) -> str:
    if value is None:
        return "Never"
    return value.astimezone().strftime("%H:%M:%S")


def _age_seconds(value: datetime | None) -> str:
    if value is None:
        return "—"
    age = max(0, (datetime.now(timezone.utc) - value).total_seconds())
    return f"{age:.0f}s"


def _status_badge(snapshot: SourceSnapshot) -> html.Span:
    return html.Span(
        snapshot.status,
        className=f"status-badge status-{snapshot.status}",
        title=snapshot.message or "",
    )


def _empty_panel(message: str) -> html.Div:
    return html.Div(message, className="empty-state")


def _health_table(snapshots: dict[str, SourceSnapshot]) -> html.Div:
    if not snapshots:
        return _empty_panel("Waiting for the first polling cycle.")

    rows = []
    for name in SOURCE_LABELS:
        snapshot = snapshots.get(name)
        if snapshot is None:
            continue
        rows.append(
            html.Tr(
                [
                    html.Td(SOURCE_LABELS[name]),
                    html.Td(_status_badge(snapshot)),
                    html.Td(f"{snapshot.latency_ms} ms"),
                    html.Td(_format_time(snapshot.last_success_at)),
                    html.Td(_age_seconds(snapshot.last_success_at)),
                ]
            )
        )

    return html.Div(
        html.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Source"),
                            html.Th("State"),
                            html.Th("Latency"),
                            html.Th("Last success"),
                            html.Th("Age"),
                        ]
                    )
                ),
                html.Tbody(rows),
            ],
            className="health-table",
        ),
        className="table-scroll",
    )


def _market_panel(snapshots: dict[str, SourceSnapshot]) -> html.Div:
    stock_snapshot = snapshots.get("stocks")
    crypto_snapshot = snapshots.get("crypto")
    if not stock_snapshot and not crypto_snapshot:
        return _empty_panel("Market data has not arrived yet.")

    quote_rows = []
    if stock_snapshot and stock_snapshot.data:
        for quote in stock_snapshot.data:
            change = quote["change_percent"]
            change_text = "—" if change is None else f"{change:+.2f}%"
            change_class = (
                ""
                if change is None
                else "value-up"
                if change >= 0
                else "value-down"
            )
            quote_rows.append(
                html.Tr(
                    [
                        html.Td(quote["symbol"]),
                        html.Td(f"{quote['price']:,.2f} {quote['currency']}"),
                        html.Td(change_text, className=change_class),
                        html.Td(quote["market_state"].title()),
                    ]
                )
            )

    bitcoin = _empty_panel("Bitcoin data is unavailable.")
    if crypto_snapshot and crypto_snapshot.data:
        change = crypto_snapshot.data["change_24h_percent"]
        bitcoin = html.Div(
            [
                html.Div("Bitcoin", className="metric-label"),
                html.Div(
                    f"${crypto_snapshot.data['price_usd']:,.2f}",
                    className="metric-value",
                ),
                html.Div(
                    f"{change:+.2f}% over 24 hours",
                    className="value-up" if change >= 0 else "value-down",
                ),
            ],
            className="metric-block",
        )

    return html.Div(
        [
            html.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Symbol"),
                                html.Th("Price"),
                                html.Th("Change"),
                                html.Th("Market"),
                            ]
                        )
                    ),
                    html.Tbody(quote_rows),
                ],
                className="market-table",
            )
            if quote_rows
            else _empty_panel("Stock quotes are unavailable."),
            bitcoin,
        ],
        className="market-content",
    )


def _context_panel(snapshots: dict[str, SourceSnapshot]) -> html.Div:
    weather_snapshot = snapshots.get("weather")
    news_snapshot = snapshots.get("news")

    weather = _empty_panel("Weather data has not arrived yet.")
    if weather_snapshot and weather_snapshot.data:
        data = weather_snapshot.data
        weather = html.Div(
            [
                html.Div(data["location"], className="metric-label"),
                html.Div(
                    f"{data['temperature_c']:.1f}°C",
                    className="metric-value",
                ),
                html.Div(
                    (
                        f"Feels like {data['feels_like_c']:.1f}°C · "
                        f"{data['humidity_percent']:.0f}% humidity"
                    ),
                    className="metric-detail",
                ),
            ],
            className="metric-block",
        )

    stories = _empty_panel("News data has not arrived yet.")
    if news_snapshot and news_snapshot.data:
        stories = html.Ol(
            [
                html.Li(
                    html.A(
                        story["title"],
                        href=story["url"],
                        target="_blank",
                        rel="noreferrer",
                    )
                )
                for story in news_snapshot.data
            ],
            className="news-list",
        )

    return html.Div(
        [
            weather,
            html.Div("Top Hacker News stories", className="section-label"),
            stories,
        ]
    )


def _latency_figure(history: dict[str, list[dict]]) -> go.Figure:
    figure = go.Figure()
    for name, records in history.items():
        if not records:
            continue
        figure.add_trace(
            go.Scatter(
                x=[record["checked_at"] for record in records],
                y=[record["latency_ms"] for record in records],
                mode="lines+markers",
                name=SOURCE_LABELS.get(name, name),
                customdata=[record["status"] for record in records],
                hovertemplate=(
                    "%{fullData.name}<br>"
                    "%{x|%H:%M:%S}<br>"
                    "%{y} ms<br>"
                    "state: %{customdata}<extra></extra>"
                ),
            )
        )

    figure.update_layout(
        margin={"l": 48, "r": 20, "t": 16, "b": 40},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif", "color": "#475569"},
        legend={"orientation": "h", "y": 1.12, "x": 0},
        xaxis={"title": None, "gridcolor": "#e2e8f0"},
        yaxis={"title": "Fetch latency (ms)", "gridcolor": "#e2e8f0"},
        hovermode="x unified",
    )
    return figure


app.layout = html.Main(
    [
        html.Header(
            [
                html.Div("Data engineering project", className="eyebrow"),
                html.H1("Realtime Data Reliability Dashboard"),
                html.P(
                    (
                        "A local monitor for external APIs that exposes source health, "
                        "freshness, latency, and last-known-good data."
                    ),
                    className="subtitle",
                ),
                html.Div(
                    [
                        html.Span(
                            f"Polling every {config.POLL_INTERVAL_SECONDS} seconds"
                        ),
                        html.Span(id="render-time"),
                    ],
                    className="header-meta",
                ),
            ],
            className="page-header",
        ),
        html.Section(
            [
                html.Article(
                    [
                        html.H2("Source health"),
                        html.P(
                            "Failed requests remain visible instead of being replaced by random values.",
                            className="panel-description",
                        ),
                        html.Div(id="health-panel"),
                    ],
                    className="panel panel-wide",
                ),
                html.Article(
                    [
                        html.H2("Markets"),
                        html.Div(id="market-panel"),
                    ],
                    className="panel",
                ),
                html.Article(
                    [
                        html.H2("External context"),
                        html.Div(id="context-panel"),
                    ],
                    className="panel",
                ),
                html.Article(
                    [
                        html.H2("Source latency history"),
                        dcc.Graph(
                            id="latency-chart",
                            config={"displayModeBar": False},
                        ),
                    ],
                    className="panel panel-wide",
                ),
            ],
            className="dashboard-grid",
        ),
        dcc.Interval(id="ui-refresh", interval=2_000, n_intervals=0),
    ],
    className="page-shell",
)


@app.callback(
    Output("health-panel", "children"),
    Output("market-panel", "children"),
    Output("context-panel", "children"),
    Output("latency-chart", "figure"),
    Output("render-time", "children"),
    Input("ui-refresh", "n_intervals"),
)
def render_dashboard(_: int):
    snapshots = data_manager.get_snapshots()
    history = data_manager.get_health_history()
    return (
        _health_table(snapshots),
        _market_panel(snapshots),
        _context_panel(snapshots),
        _latency_figure(history),
        f"View refreshed at {datetime.now().astimezone():%H:%M:%S}",
    )


if __name__ == "__main__":
    app.run(host=config.APP_HOST, port=config.APP_PORT, debug=config.DEBUG)
