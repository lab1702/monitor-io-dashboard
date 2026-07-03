# Network Monitor Dashboard

A Python-based web dashboard for monitoring network devices and visualizing network performance metrics. This dashboard connects to a network monitoring device and provides real-time status updates, historical data visualization, and file browsing capabilities.

## Features

- **Real-time Network Monitoring**: Live status updates of monitored network targets
- **Historical Data Visualization**: Interactive charts showing ping response times and packet loss over time
- **File Browser**: Browse and access log files from the monitoring device
- **Responsive Design**: Clean, modern interface that works on desktop and mobile
- **Configurable**: Extensive configuration options via environment variables or command-line arguments

## Requirements

- Python 3.13 or higher
- Network monitoring device accessible via HTTP

## Installation

1. Clone the repository:
   ```powershell
   git clone <repository-url>
   cd monitor-dashboard
   ```

2. Install dependencies:
   ```powershell
   pip install -e .
   ```

## Usage

### Basic Usage

Run the dashboard with default settings:
```powershell
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`. Set the port with
`streamlit run app.py --server.port=3000`. Monitor URL and refresh interval can
also be changed live from the sidebar. Toggle light/dark mode from Streamlit's
menu (top-right → Settings → Theme).

### Environment Variables

Configure the defaults using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MONITOR_URL` | `http://192.168.0.246` | URL of the monitoring device |
| `REFRESH_INTERVAL` | `30` | Auto-refresh interval in seconds |
| `DASHBOARD_TITLE` | `Network Monitor Dashboard` | Dashboard title |
| `CHART_HEIGHT` | `400` | Default chart height in pixels |

### Example with Environment Variables

Windows (PowerShell):
```powershell
$env:MONITOR_URL="http://192.168.1.100"
$env:REFRESH_INTERVAL="60"
streamlit run app.py
```

## Project Structure

```
monitor-dashboard/
├── app.py               # Streamlit web application (entry point)
├── pyproject.toml       # Project configuration and dependencies
├── src/
│   ├── config.py       # Configuration management
│   └── data_parser.py  # Data parsing and processing
└── README.md           # This file
```

## Development

### Adding Dependencies

Add new dependencies to `pyproject.toml`, then reinstall:

```powershell
pip install -e .
```

## Configuration Details

The dashboard connects to a network monitoring device that provides:
- Current status of monitored targets
- Historical ping data
- Log files for download

The monitoring device should be accessible via HTTP and provide the expected data format for proper visualization.

## Troubleshooting

### Common Issues

1. **Connection refused**: Ensure the monitoring device is running and accessible at the configured URL
2. **Port already in use**: Change the dashboard port with `streamlit run app.py --server.port=3000`
3. **No data displayed**: Check the monitoring device URL and ensure it's providing data in the expected format

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.