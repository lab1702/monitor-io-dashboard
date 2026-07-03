import os

MONITOR_URL = os.getenv("MONITOR_URL", "http://192.168.0.246")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "30"))  # seconds
DASHBOARD_TITLE = os.getenv("DASHBOARD_TITLE", "Network Monitor Dashboard")
CHART_HEIGHT = int(os.getenv("CHART_HEIGHT", "400"))
