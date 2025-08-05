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

2. Install dependencies using uv (recommended):
   ```powershell
   uv sync
   ```

   Or using pip:
   ```powershell
   pip install -e .
   ```

## Usage

### Basic Usage

Run the dashboard with default settings:
```powershell
python main.py
```

The dashboard will be available at `http://localhost:8050`

### Command Line Options

```powershell
python main.py [OPTIONS]

Options:
  --url URL        Monitor device URL (default: http://192.168.0.246)
  --port PORT      Dashboard port (default: 8050)
  --refresh INT    Refresh interval in seconds (default: 30)
  --debug          Enable debug mode
  --help           Show help message
```

### Environment Variables

Configure the dashboard using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MONITOR_URL` | `http://192.168.0.246` | URL of the monitoring device |
| `DASHBOARD_PORT` | `8050` | Port for the dashboard web server |
| `REFRESH_INTERVAL` | `30` | Auto-refresh interval in seconds |
| `DEBUG` | `False` | Enable debug mode |
| `DASHBOARD_TITLE` | `Network Monitor Dashboard` | Dashboard title |
| `MAX_HISTORY_DAYS` | `7` | Maximum days of historical data to display |
| `SHOW_GRID` | `True` | Show grid lines on charts |
| `CHART_HEIGHT` | `400` | Default chart height in pixels |

### Example with Environment Variables

Windows (Command Prompt):
```cmd
set MONITOR_URL=http://192.168.1.100
set DASHBOARD_PORT=3000
set REFRESH_INTERVAL=60
python main.py
```

Windows (PowerShell):
```powershell
$env:MONITOR_URL="http://192.168.1.100"
$env:DASHBOARD_PORT="3000"
$env:REFRESH_INTERVAL="60"
python main.py
```

## Project Structure

```
monitor-dashboard/
├── main.py              # Main entry point
├── pyproject.toml       # Project configuration and dependencies
├── ruff.toml           # Code linting configuration
├── src/
│   ├── __init__.py
│   ├── config.py       # Configuration management
│   ├── dashboard.py    # Dash web application
│   └── data_parser.py  # Data parsing and processing
├── assets/
│   └── styles.css      # Custom CSS styles
└── README.md           # This file
```

## Development

### Code Quality

This project uses [Ruff](https://docs.astral.sh/ruff/) for code formatting and linting:

```powershell
# Run linting
uv run ruff check

# Format code
uv run ruff format
```

### Adding Dependencies

Add new dependencies to `pyproject.toml`:

```powershell
# Add a runtime dependency
uv add package-name

# Add a development dependency
uv add --group dev package-name
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
2. **Port already in use**: Change the dashboard port using `--port` or `DASHBOARD_PORT`
3. **No data displayed**: Check the monitoring device URL and ensure it's providing data in the expected format

### Debug Mode

Enable debug mode for detailed logging:
```powershell
python main.py --debug
```

Or set the environment variable:

Windows (Command Prompt):
```cmd
set DEBUG=true
python main.py
```

Windows (PowerShell):
```powershell
$env:DEBUG="true"
python main.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.