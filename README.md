# AEMO Energy Dashboard

Real-time Australian Energy Market (AEMO) electricity price and generation dashboard with automated data collection, visualization, and alert system.

## Features

- **Real-time Price Monitoring**: Downloads AEMO spot prices every 4 minutes
- **Generation Dashboard**: Interactive visualization of electricity generation by fuel type
- **Smart DUID Management**: Tracks unknown generation units with exception list
- **Email Alerts**: Automated notifications for new unknown DUIDs and price thresholds
- **SMS Alerts**: Optional Twilio integration for critical price alerts
- **Data Persistence**: Efficient parquet file storage for historical data
- **Modern UI**: Dark-themed Panel dashboards with interactive charts

## Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv package manager](https://github.com/astral-sh/uv)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/aemo-energy-dashboard.git
   cd aemo-energy-dashboard
   ```

2. **Set up the environment**
   ```bash
   uv sync
   ```

3. **Configure environment variables**
   ```bash
   cp .env.sample .env
   # Edit .env with your email credentials and preferences
   ```

4. **Test email configuration**
   ```bash
   uv run python scripts/test_email.py
   ```

### Configuration

Edit the `.env` file with your settings:

#### Data File Locations
The system supports two modes:

**Production Mode (Default)**: Uses existing data in iCloud directories
```bash
DATA_DIR=/Users/yourusername/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot
GEN_INFO_FILE=/path/to/existing/gen_info.pkl
GEN_OUTPUT_FILE=/path/to/existing/gen_output.parquet
SPOT_HIST_FILE=/path/to/existing/spot_hist.parquet
```

**Development Mode**: Uses local project data
```bash
# Comment out the above paths and use:
# DATA_DIR=./data
# (Other files will default to data/ directory)
```

#### Email and SMS Configuration

```bash
# Email alerts (required for DUID notifications)
ALERT_EMAIL=your-email@icloud.com
ALERT_PASSWORD=your-app-specific-password
SMTP_SERVER=smtp.mail.me.com
SMTP_PORT=587

# Optional: SMS alerts for price thresholds
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number
MY_PHONE_NUMBER=your-phone-number

# Dashboard settings
DEFAULT_REGION=NEM
DASHBOARD_PORT=5008
UPDATE_INTERVAL_MINUTES=4.5
```

## Usage

### Start the Generation Dashboard

```bash
uv run aemo-gen-dashboard
```

Access at: http://localhost:5008

### Run Spot Price Updater

```bash
uv run aemo-spot-update
```

### Start Spot Price Dashboard

```bash
uv run aemo-spot-display
```

### Manage DUID Exceptions

```bash
# List current exceptions
uv run aemo-manage-duids list

# Add a DUID to exception list
uv run aemo-manage-duids add NEWDUID1

# Remove from exception list  
uv run aemo-manage-duids remove OLDDUID1

# Clear all exceptions
uv run aemo-manage-duids clear
```

## Project Structure

```
aemo-energy-dashboard/
├── src/aemo_dashboard/
│   ├── spot_prices/          # Price monitoring and dashboard
│   │   ├── update_spot.py    # Automated price data collection
│   │   └── display_spot.py   # Price visualization dashboard
│   ├── generation/           # Generation monitoring and dashboard
│   │   └── gen_dash.py       # Generation dashboard with DUID management
│   └── shared/               # Common utilities
│       ├── config.py         # Centralized configuration
│       ├── logging_config.py # Unified logging
│       └── email_alerts.py   # Email notification system
├── scripts/                  # Utility scripts
│   ├── manage_duid_exceptions.py
│   └── test_email.py
├── data/                     # Data files (gitignored)
├── logs/                     # Log files (gitignored)
├── .env.sample              # Configuration template
└── pyproject.toml           # uv project configuration
```

## Data Sources

- **AEMO NEM Web**: Real-time dispatch data for prices and generation
- **Generation Info**: Static DUID-to-fuel mapping (gen_info.pkl)
- **Historical Data**: Parquet files for efficient time series storage

## Email Alert System

### DUID Alerts
- Automatically detects new unknown generation units (DUIDs)
- Sends detailed email with generation levels and timestamps
- Smart rate limiting (24-hour cooldown by default)
- Exception list to reduce noise from known unimportant DUIDs

### Price Alerts (Optional)
- SMS notifications via Twilio for extreme price events
- Configurable thresholds for high/low/extreme prices
- Recovery notifications when prices return to normal

## Dashboard Features

### Generation Dashboard
- **Fuel Type Visualization**: Stacked area charts showing generation by fuel
- **Capacity Utilization**: Line charts showing % utilization by fuel type
- **Region Selection**: Filter by NEM region (NSW1, QLD1, SA1, TAS1, VIC1)
- **Real-time Updates**: Auto-refresh every 4.5 minutes
- **Responsive Design**: Material Design theme with dark mode

### Spot Price Dashboard  
- **Real-time Prices**: 5-minute settlement price updates
- **Price History**: Smoothed charts with exponential weighted moving averages
- **Multi-region**: Support for all NEM regions
- **Alert Integration**: Visual indicators for price threshold breaches

## Development

### Running Tests
```bash
uv run pytest
```

### Code Formatting
```bash
uv run black src/
uv run isort src/
```

### Type Checking
```bash
uv run mypy src/
```

## Troubleshooting

### Email Setup for iCloud
1. Go to https://appleid.apple.com
2. Sign in and navigate to "Sign-In and Security"
3. Select "App-Specific Passwords"
4. Generate password for "AEMO Dashboard"
5. Use the 16-character password in your .env file

### Common Issues

**No email received:**
- Check spam folder
- Verify app-specific password
- Run `uv run python scripts/test_email.py`

**Dashboard not loading:**
- Check port 5008 is not in use
- Verify data files exist in data/ directory
- Check logs/ directory for error messages

**Missing DUIDs:**
- Update gen_info.pkl with latest AEMO generation information
- Use DUID management commands to add exceptions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: https://github.com/yourusername/aemo-energy-dashboard/issues
- **Documentation**: See docs/ directory
- **Email**: your-email@domain.com