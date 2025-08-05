import os
from typing import Any, Dict


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
        self.MAX_HISTORY_DAYS = int(os.getenv("MAX_HISTORY_DAYS", "7"))

        # Display options
        self.SHOW_GRID = os.getenv("SHOW_GRID", "True").lower() == "true"
        self.CHART_HEIGHT = int(os.getenv("CHART_HEIGHT", "400"))

    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary."""
        return {
            "MONITOR_URL": self.MONITOR_URL,
            "REFRESH_INTERVAL": self.REFRESH_INTERVAL,
            "DASHBOARD_PORT": self.DASHBOARD_PORT,
            "DEBUG": self.DEBUG,
            "DASHBOARD_TITLE": self.DASHBOARD_TITLE,
            "MAX_HISTORY_DAYS": self.MAX_HISTORY_DAYS,
            "SHOW_GRID": self.SHOW_GRID,
            "CHART_HEIGHT": self.CHART_HEIGHT,
        }

    def update_config(self, key: str, value: Any):
        """Update a configuration value."""
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise ValueError(f"Unknown configuration key: {key}")


# Global configuration instance
config = Config()
