import dash
import plotly.graph_objects as go
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State

from config import config
from data_parser import NetworkMonitorParser


class NetworkDashboard:
    def __init__(self):
        import os
        # Get the project root directory (parent of src)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        assets_path = os.path.join(project_root, "assets")
        
        self.app = dash.Dash(__name__, assets_folder=assets_path)
        self.parser = NetworkMonitorParser(config.MONITOR_URL)
        self.setup_layout()
        self.setup_callbacks()

    def get_chart_theme(self, is_dark=False):
        """Get chart theme configuration for light or dark mode."""
        font_family = "system-ui, -apple-system, sans-serif"
        if is_dark:
            template, fg, tick = "plotly_dark", "#ffffff", "#b0b0b0"
            grid, line = "rgba(128,128,128,0.3)", "rgba(128,128,128,0.4)"
            hover_bg, hover_border = "#2d2d2d", "#404040"
        else:
            template, fg, tick = "plotly_white", "#212529", "#6c757d"
            grid, line = "rgba(128,128,128,0.2)", "rgba(128,128,128,0.3)"
            hover_bg, hover_border = "#ffffff", "#dee2e6"

        axis = {
            "gridcolor": grid,
            "linecolor": line,
            "tickfont": {"color": tick},
            "title": {"font": {"color": fg}},
        }
        return {
            "template": template,
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": fg, "family": font_family},
            "colorway": ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"],
            "xaxis": axis,
            "yaxis": dict(axis),
            "hoverlabel": {
                "bgcolor": hover_bg,
                "bordercolor": hover_border,
                "font": {"color": fg, "family": font_family},
            },
        }

    def setup_layout(self):
        """Setup the dashboard layout."""
        self.app.layout = html.Div(
            [
                # Header
                html.Div(
                    [
                        html.H1(config.DASHBOARD_TITLE, className="dashboard-title"),
                    ]
                ),
                # Main Content Container
                html.Div(
                    [
                        # Configuration Section
                        html.Div(
                            [
                                html.Div([
                                    html.H3("⚙️ Configuration"),
                                    html.Button(
                                        "🌙", 
                                        id="theme-toggle-btn", 
                                        n_clicks=0,
                                        title="Toggle Dark Mode"
                                    )
                                ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
                                html.Div(
                                    [
                                        html.Label("Monitor URL:"),
                                        html.Div(
                                            [
                                                dcc.Input(
                                                    id="url-input",
                                                    type="text",
                                                    value=config.MONITOR_URL,
                                                    placeholder="Enter monitoring device URL",
                                                ),
                                                html.Button(
                                                    "Update URL",
                                                    id="update-url-btn",
                                                    n_clicks=0,
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "alignItems": "center",
                                                "gap": "1rem",
                                                "flexWrap": "wrap",
                                            },
                                        ),
                                        html.Div(
                                            id="url-status", style={"marginTop": "1rem"}
                                        ),
                                    ]
                                ),
                            ],
                            className="config-panel",
                        ),
                        # Current Status Section
                        html.Div(
                            [
                                html.H3("📊 Current Status"),
                                html.Div(id="current-status"),
                            ],
                            className="dashboard-section",
                        ),
                        # Historical Data Section
                        html.Div(
                            [
                                html.H3("📈 Historical Data"),
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id="file-dropdown",
                                            placeholder="Select a date to view historical data",
                                            className="dash-dropdown",
                                            style={"marginBottom": "1rem"},
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        dcc.Graph(
                                            id="ping-chart",
                                            config={
                                                "displayModeBar": False,
                                                "responsive": True,
                                            },
                                        ),
                                    ],
                                    style={"marginBottom": "1rem"},
                                ),
                                html.Div(
                                    [
                                        dcc.Graph(
                                            id="loss-chart",
                                            config={
                                                "displayModeBar": False,
                                                "responsive": True,
                                            },
                                        ),
                                    ]
                                ),
                            ],
                            className="dashboard-section",
                        ),
                    ],
                    style={"maxWidth": "1200px", "margin": "0 auto"},
                ),
                # Hidden Components
                dcc.Interval(
                    id="interval-component",
                    interval=config.REFRESH_INTERVAL * 1000,
                    n_intervals=0,
                ),
                dcc.Store(id="current-url", data=config.MONITOR_URL),
                dcc.Store(id="theme-store", data="light"),
                
            ],
            style={"minHeight": "100vh", "backgroundColor": "var(--bg-primary)"},
        )

    def setup_callbacks(self):
        """Setup dashboard callbacks."""
        
        # Theme toggle using Dash clientside callback
        self.app.clientside_callback(
            """
            function(n_clicks, current_theme) {
                if (n_clicks > 0) {
                    const newTheme = current_theme === 'dark' ? 'light' : 'dark';

                    // Apply theme to document
                    if (newTheme === 'dark') {
                        document.documentElement.setAttribute('data-theme', 'dark');
                        document.body.style.backgroundColor = '#1a1a1a';
                        document.body.style.color = '#ffffff';
                    } else {
                        document.documentElement.removeAttribute('data-theme');
                        document.body.style.backgroundColor = '#ffffff';
                        document.body.style.color = '#212529';
                    }
                    
                    // Update button
                    const button = document.getElementById('theme-toggle-btn');
                    if (button) {
                        button.innerHTML = newTheme === 'dark' ? '☀️' : '🌙';
                        button.title = newTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
                    }

                    return newTheme;
                }

                // Initialize on first load
                const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
                const initialTheme = prefersDark ? 'dark' : 'light';

                if (initialTheme === 'dark') {
                    document.documentElement.setAttribute('data-theme', 'dark');
                    document.body.style.backgroundColor = '#1a1a1a';
                    document.body.style.color = '#ffffff';
                } else {
                    document.documentElement.removeAttribute('data-theme');
                    document.body.style.backgroundColor = '#ffffff';
                    document.body.style.color = '#212529';
                }
                
                const button = document.getElementById('theme-toggle-btn');
                if (button) {
                    button.innerHTML = initialTheme === 'dark' ? '☀️' : '🌙';
                    button.title = initialTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
                }
                
                return initialTheme;
            }
            """,
            Output("theme-store", "data"),
            [Input("theme-toggle-btn", "n_clicks")],
            [State("theme-store", "data")]
        )

        @self.app.callback(
            [Output("current-url", "data"), Output("url-status", "children")],
            [Input("update-url-btn", "n_clicks")],
            [State("url-input", "value")],
        )
        def update_url(n_clicks, new_url):
            if n_clicks > 0 and new_url:
                try:
                    self.parser.base_url = new_url.rstrip("/")
                    return new_url, html.Div(
                        "✅ URL updated successfully!", className="status-success"
                    )
                except Exception as e:
                    return config.MONITOR_URL, html.Div(
                        f"❌ Error: {str(e)}", className="status-error"
                    )
            return config.MONITOR_URL, ""

        @self.app.callback(
            [
                Output("current-status", "children"),
                Output("file-dropdown", "options"),
            ],
            [Input("interval-component", "n_intervals"), Input("current-url", "data")],
        )
        def update_current_data(n, current_url):
            try:
                if current_url != self.parser.base_url:
                    self.parser.base_url = current_url

                # Get latest results
                latest_results = self.parser.parse_latest_results()

                # Create status cards
                status_cards = []
                for target, data in latest_results.items():
                    loss_pct = data.get("loss_percent", 0)

                    # Determine status and icon
                    if loss_pct == 0:
                        status_text = "🟢 Excellent"
                        status_class = "status-card status-good"
                    elif loss_pct < 25:
                        status_text = "🟡 Good"
                        status_class = "status-card status-warning"
                    elif loss_pct < 75:
                        status_text = "🟠 Warning"
                        status_class = "status-card status-warning"
                    else:
                        status_text = "🔴 Critical"
                        status_class = "status-card status-critical"

                    card_content = [
                        html.H5(target),
                        html.P(f"Status: {status_text}", style={"fontWeight": "bold"}),
                        html.P(f"📉 Loss: {loss_pct}%"),
                        html.P(
                            f"📦 Packets: {data.get('received', 0)}/{data.get('transmitted', 0)}"
                        ),
                    ]

                    if "avg_delay" in data:
                        card_content.append(
                            html.P(f"⏱️ Avg Delay: {data['avg_delay']:.1f}ms")
                        )

                    status_cards.append(html.Div(card_content, className=status_class))

                # Get file list for dropdown
                daily_files = self.parser.get_all_daily_files()
                file_options = [{"label": f, "value": f} for f in daily_files]

                return status_cards, file_options

            except Exception as e:
                error_msg = html.Div(
                    f"❌ Error fetching data: {str(e)}", className="status-error"
                )
                return error_msg, []

        @self.app.callback(
            [Output("ping-chart", "figure"), Output("loss-chart", "figure")],
            [Input("file-dropdown", "value"), Input("current-url", "data"), Input("theme-store", "data")],
        )
        def update_charts(selected_file, current_url, theme):
            if not selected_file:
                # Return empty charts
                empty_fig = go.Figure()
                chart_theme = self.get_chart_theme(is_dark=(theme == "dark"))
                empty_fig.update_layout(
                    title="📊 Select a date to view historical data",
                    height=300,
                    **chart_theme,
                )
                return empty_fig, empty_fig

            try:
                if current_url != self.parser.base_url:
                    self.parser.base_url = current_url

                df = self.parser.parse_daily_csv(selected_file)

                if df.empty:
                    empty_fig = go.Figure()
                    chart_theme = self.get_chart_theme(is_dark=(theme == "dark"))
                    empty_fig.update_layout(
                        title="📭 No data available for selected date",
                        height=300,
                        **chart_theme,
                    )
                    return empty_fig, empty_fig

                # Create ping time chart
                ping_fig = go.Figure()

                # Get active targets using improved column detection
                active_targets = self.parser.get_active_targets(df)

                for target_info in active_targets:
                    target_num = target_info["number"]
                    target_name = target_info["name"]
                    avg_delay_col = f"DelayAvg{target_num}"

                    if target_info["has_delay_data"] and avg_delay_col in df.columns:
                        # Filter out invalid delay values
                        valid_data = df[
                            df[avg_delay_col].notna() & (df[avg_delay_col] > 0)
                        ]
                        if not valid_data.empty:
                            ping_fig.add_trace(
                                go.Scatter(
                                    x=valid_data["DateTime"],
                                    y=valid_data[avg_delay_col],
                                    mode="lines",
                                    name=f"{target_name} - Avg Delay",
                                    line=dict(width=2),
                                )
                            )

                chart_theme = self.get_chart_theme(is_dark=(theme == "dark"))
                ping_fig.update_layout(
                    title={
                        "text": "📈 Ping Response Times Over Time",
                        "font": {"size": 18, "color": chart_theme["font"]["color"]},
                    },
                    xaxis_title="Time",
                    yaxis_title="Response Time (ms)",
                    height=config.CHART_HEIGHT,
                    showlegend=True,
                    hovermode="x unified",
                    margin=dict(t=60, b=60, l=60, r=60),
                    **chart_theme,
                )

                # Create packet loss chart
                loss_fig = go.Figure()

                for target_info in active_targets:
                    target_num = target_info["number"]
                    target_name = target_info["name"]
                    loss_col = f"LossPct{target_num}"

                    if target_info["has_loss_data"] and loss_col in df.columns:
                        # Filter out invalid loss values
                        valid_data = df[df[loss_col].notna()]
                        if not valid_data.empty:
                            loss_fig.add_trace(
                                go.Scatter(
                                    x=valid_data["DateTime"],
                                    y=valid_data[loss_col],
                                    mode="lines",
                                    name=f"{target_name} - Loss %",
                                    line=dict(width=2),
                                )
                            )

                loss_fig.update_layout(
                    title={
                        "text": "📉 Packet Loss Over Time",
                        "font": {"size": 18, "color": chart_theme["font"]["color"]},
                    },
                    xaxis_title="Time",
                    yaxis_title="Packet Loss (%)",
                    height=config.CHART_HEIGHT,
                    showlegend=True,
                    hovermode="x unified",
                    margin=dict(t=60, b=60, l=60, r=60),
                    **chart_theme,
                )

                return ping_fig, loss_fig

            except Exception as e:
                error_fig = go.Figure()
                chart_theme = self.get_chart_theme(is_dark=(theme == "dark"))
                error_fig.update_layout(
                    title=f"❌ Error loading data: {str(e)}", height=300, **chart_theme
                )
                return error_fig, error_fig

    def run(self, debug=None, port=None):
        """Run the dashboard."""
        debug = debug if debug is not None else config.DEBUG
        port = port if port is not None else config.DASHBOARD_PORT

        print("Starting Network Monitor Dashboard...")
        print(f"Monitor URL: {config.MONITOR_URL}")
        print(f"Dashboard URL: http://localhost:{port}")

        self.app.run(debug=debug, port=port, host="0.0.0.0")


if __name__ == "__main__":
    dashboard = NetworkDashboard()
    dashboard.run()
