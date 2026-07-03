import os


class Config:
    def __init__(self):
        self.load_config()

    def load_config(self):
        """Load configuration from environment variables or use defaults."""
        self.MONITOR_URL = os.getenv("MONITOR_URL", "http://192.168.0.246")
        self.REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "30"))  # seconds
        self.DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8050"))
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"

        # Dashboard configuration
        self.DASHBOARD_TITLE = os.getenv("DASHBOARD_TITLE", "Network Monitor Dashboard")
        self.CHART_HEIGHT = int(os.getenv("CHART_HEIGHT", "400"))


# Global configuration instance
config = Config()
