#!/usr/bin/env python3
"""
Network Monitor Dashboard - Main Entry Point

This dashboard connects to a network monitoring device and displays:
- Current status of all monitored targets
- Historical ping response times and packet loss
- File browser for available log files

Usage:
    python main.py [--url URL] [--port PORT] [--debug]

Environment Variables:
    MONITOR_URL: URL of the monitoring device (default: http://192.168.0.246)
    DASHBOARD_PORT: Port for the dashboard web server (default: 8050)
    DEBUG: Enable debug mode (default: False)
"""

import argparse
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dashboard import NetworkDashboard
from config import config


def main():
    parser = argparse.ArgumentParser(description='Network Monitor Dashboard')
    parser.add_argument('--url', help='Monitor device URL', default=config.MONITOR_URL)
    parser.add_argument('--port', type=int, help='Dashboard port', default=config.DASHBOARD_PORT)
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--refresh', type=int, help='Refresh interval in seconds', default=config.REFRESH_INTERVAL)
    
    args = parser.parse_args()
    
    # Update configuration with command line arguments
    config.MONITOR_URL = args.url
    config.REFRESH_INTERVAL = args.refresh
    
    # Create and run dashboard
    dashboard = NetworkDashboard()
    
    try:
        dashboard.run(debug=args.debug, port=args.port)
    except KeyboardInterrupt:
        print("\nShutting down dashboard...")
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
