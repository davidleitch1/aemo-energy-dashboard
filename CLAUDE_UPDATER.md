# AEMO Data Updater Documentation

## Latest Updates (July 2025)

### Implementation Status ⚠️ BACKFILL ISSUES
The AEMO Data Updater has been successfully separated into a standalone repository:
- **Repository**: https://github.com/davidleitch1/aemo-data-updater
- **Location**: `/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/aemo-data-updater/`
- ✅ All four collectors implemented for real-time data
- ✅ SMS price alerts fully integrated (Twilio)
- ✅ Email alerts for new DUIDs (iCloud)
- ✅ Cross-machine compatibility added using Path.home()
- ✅ Status dashboard UI on port 5011
- ✅ Production credentials configured in .env file
- ⚠️ Data repair/backfill not working for price data (July 2025)
- ❌ Fix Missing Data button in dashboard is not operational (July 2025)
- ✅ Transmission backfill previously worked for weeks of data

### Current Issues - RESOLVED (July 2025)

#### Price Data Status ✅
- **Real-time collection**: Working perfectly - updates every 5 minutes
- **Data coverage**: 99.3% complete (288/290 intervals in last 24 hours)
- **Missing intervals**: Only 2 gaps from yesterday (16:40 and 16:50)
- **Latest data**: Always up-to-date within 5-10 minutes

#### Root Cause Analysis - Price Backfill
The investigation revealed multiple issues that have been fixed:

1. **Wrong Data Table**:
   - Backfill was looking for `DISPATCH,PRICE` table
   - Real-time uses `DREGION` table (different format)
   - Fixed: Updated `_parse_dispatch_csv()` to parse DREGION data

2. **URL Case Sensitivity**:
   - Backfill used `/CURRENT/` (uppercase)
   - Real-time uses `/Current/` (lowercase)
   - Fixed: Aligned URLs to use correct case

3. **Wrong Archive URL**:
   - Price data is in `Dispatch_Reports` archive
   - Config incorrectly pointed to `DispatchIS_Reports`
   - Fixed: Updated archive URL

4. **Performance Issue**:
   - Backfill still times out checking many files
   - Not critical since real-time works perfectly
   - Only affects historical gap filling

#### Generation Backfill - TODO
- **Status**: No backfill method implemented
- **Impact**: Cannot recover historical generation data
- **Next Priority**: Implement generation backfill capability

### Dashboard Auto-Refresh Issue (July 2025)

#### Problem
The `run_dashboard.py` status dashboard lacks auto-refresh functionality. Attempted implementations failed with:
- `RuntimeError: no running event loop` when using `pn.state.add_periodic_callback()`
- `AttributeError: 'Button' object has no attribute 'periodic_callback'`

#### Root Cause
Panel's periodic callbacks require an active Bokeh/Tornado server event loop, which isn't available when setting up the dashboard layout. The callbacks must be added after the server starts.

#### Attempted Solutions
1. **Direct periodic callback**: Failed - no event loop at creation time
2. **Using pn.state.onload()**: Failed - still no event loop
3. **Button periodic_callback**: Failed - Button widgets don't have this method

#### Current Status
Dashboard works with manual refresh button only. Auto-refresh temporarily disabled.

### Key Implementation Differences

#### Collector Patterns
The codebase has two different collector patterns:

1. **Old Pattern** (Price & Generation):
   - Direct implementation without BaseCollector inheritance
   - Synchronous methods (no async/await)
   - Constructor: `PriceCollector()` with no parameters
   - Methods: `load_historical_data()`, `update()`, `get_latest_urls()`

2. **New Pattern** (Transmission & Rooftop):
   - Inherit from BaseCollector abstract class
   - Async methods throughout
   - Constructor: `TransmissionCollector(config)` with config dict
   - Methods: `load_existing_data()`, `collect_once()`, `get_latest_urls()`

#### URL Structure Differences

Each data type has unique URL patterns:

1. **Price Data**:
   - URL: `http://nemweb.com.au/Reports/Current/Dispatch_Reports/`
   - Note: Different from CLAUDE docs which incorrectly show DispatchIS_Reports
   - Data format: Long format (REGIONID, RRP columns)

2. **Generation Data**:
   - URL: `http://nemweb.com.au/Reports/CURRENT/Dispatch_SCADA/`
   - ~470 DUIDs per timestamp
   - Requires gen_info.pkl for DUID mappings

3. **Transmission Data**:
   - Uses same URL as price but different table (DISPATCHINTERCONNECTORRES)
   - Archive has nested ZIP structure (daily→5-minute)

4. **Rooftop Solar**:
   - 30-minute source data → 5-minute conversion
   - Algorithm: `((6-j)*current + j*next) / 6`
   - Archive files are weekly (Thursdays)

### Important Notes for Maintenance

1. **Data Freshness Alerts**:
   - Price/Gen/Transmission: 30-minute threshold
   - Rooftop Solar: Should be 90 minutes (data only updates every 30 min)

2. **File Paths**:
   - Now uses `Path.home()` for cross-machine compatibility
   - Works on any Mac with same iCloud account

3. **Unknown DUIDs**:
   - Generation collector tracks ~48 unknown DUIDs
   - Email alerts need to be configured for new DUIDs

## Overview

The AEMO Data Updater is a standalone service responsible for downloading and maintaining electricity market data from NEMWEB. It runs continuously, collecting data every 5 minutes and storing it in parquet files for efficient access by the dashboard and other applications.

## Data Sources and URLs

### Generation SCADA (5-minute)
- **URL**: `http://nemweb.com.au/Reports/CURRENT/Dispatch_SCADA/`
- **Files**: `PUBLIC_DISPATCHSCADA_YYYYMMDDHHMM_*.zip`
- **Contains**: Unit-level generation data for all DUIDs
- **Update Frequency**: Every 5 minutes

### Spot Prices (5-minute)
- **URL**: `http://nemweb.com.au/Reports/CURRENT/DispatchIS_Reports/`
- **Files**: `PUBLIC_DISPATCH_YYYYMMDDHHMM_*.zip`
- **Contains**: Regional reference prices (RRP)
- **Update Frequency**: Every 5 minutes

### Rooftop Solar (30-minute)
- **URL**: `http://nemweb.com.au/Reports/Current/ROOFTOP_PV/ACTUAL/`
- **Files**: `PUBLIC_ROOFTOP_PV_ACTUAL_MEASUREMENT_YYYYMMDDHHMM_*.zip`
- **Contains**: Rooftop solar generation by region
- **Update Frequency**: Every 30 minutes
- **Processing**: Converts 30-minute data to 5-minute intervals using weighted interpolation

### Transmission Flows (5-minute)
- **CURRENT URL**: `http://nemweb.com.au/Reports/CURRENT/DispatchIS_Reports/`
- **ARCHIVE URL**: `https://www.nemweb.com.au/REPORTS/ARCHIVE/DispatchIS_Reports/`
- **Files**: `PUBLIC_DISPATCHIS_YYYYMMDDHHMM_*.zip` (current) or `PUBLIC_DISPATCHIS_YYYYMMDD.zip` (archive)
- **Contains**: Interconnector flow data (DISPATCHINTERCONNECTORRES table)
- **Update Frequency**: Every 5 minutes

## Critical Implementation Notes

### REQUIRED: User-Agent Headers
NEMWEB servers require proper User-Agent headers to prevent 403 Forbidden errors:

```python
headers = {
    'User-Agent': 'AEMO Dashboard Data Collector'
}
response = requests.get(url, headers=headers, timeout=30)
```

**⚠️ IMPORTANT: Without User-Agent headers, requests will fail with 403 errors**

### Archive Structure (for Transmission Backfill)

The archive has a nested ZIP structure:

1. **Daily Archive Files**:
   - Format: `PUBLIC_DISPATCHIS_YYYYMMDD.zip`
   - Example: `PUBLIC_DISPATCHIS_20250708.zip`
   - Contains: 288 nested ZIP files (one per 5-minute interval)

2. **Nested 5-Minute Files** (inside daily ZIP):
   - Format: `PUBLIC_DISPATCHIS_YYYYMMDDHHMM_*.zip`
   - Example: `PUBLIC_DISPATCHIS_202507081205_0000000471017670.zip`
   - Contains: One CSV file with the same name but `.CSV` extension

3. **Data Extraction Process**:
```python
with zipfile.ZipFile(BytesIO(response.content)) as daily_zip:
    # Lists 288 5-minute ZIP files
    nested_zips = [f for f in daily_zip.namelist() if f.endswith('.zip')]
    
    # Process each 5-minute ZIP
    for nested_zip_name in nested_zips:
        with daily_zip.open(nested_zip_name) as nested_file:
            with zipfile.ZipFile(nested_file) as minute_zip:
                # Get the CSV file
                csv_files = [f for f in minute_zip.namelist() if f.endswith('.CSV')]
                with minute_zip.open(csv_files[0]) as csv_file:
                    # Parse CSV content
```

## Parquet File Locations

All data files are stored in parquet format for efficient querying:

```
/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/
├── aemo-energy-dashboard/
│   └── data/
│       ├── gen_output.parquet          # Generation data (~13MB, growing ~0.6MB/day)
│       ├── spot_hist.parquet           # Price data (~0.3MB)
│       └── gen_info.pkl                # DUID mappings (static reference)
├── rooftop_solar.parquet               # Rooftop solar data
└── transmission_flows.parquet          # Transmission interconnector data
```

## Data Formats

### Generation Data (gen_output.parquet)
```python
columns = ['settlementdate', 'duid', 'scadavalue']
# settlementdate: datetime64[ns] - 5-minute intervals
# duid: string - Dispatchable Unit Identifier
# scadavalue: float64 - Generation in MW
```

### Price Data (spot_hist.parquet)
```python
columns = ['SETTLEMENTDATE', 'REGIONID', 'RRP']
# SETTLEMENTDATE: datetime64[ns] - 5-minute intervals
# REGIONID: string - NSW1, QLD1, SA1, TAS1, VIC1
# RRP: float64 - Regional Reference Price in $/MWh
```

### Rooftop Solar (rooftop_solar.parquet)
```python
columns = ['settlementdate', 'NSW1', 'QLD1', 'SA1', 'TAS1', 'VIC1', ...]
# settlementdate: datetime64[ns] - 5-minute intervals (converted from 30-min)
# Region columns: float64 - Generation in MW by region
```

### Transmission Flows (transmission_flows.parquet)
```python
columns = ['settlementdate', 'interconnectorid', 'meteredmwflow', 
           'mwflow', 'exportlimit', 'importlimit', 'mwlosses']
# settlementdate: datetime64[ns] - 5-minute intervals
# interconnectorid: string - e.g., NSW1-QLD1, VIC1-NSW1
# meteredmwflow: float64 - Actual flow in MW
# exportlimit/importlimit: float64 - Flow limits in MW
```

## Transmission Flow Direction Logic

### Interconnector Naming Convention
- Interconnectors are named FROM-TO (e.g., VIC1-NSW1, NSW1-QLD1)
- The first region is the "FROM" region
- The second region is the "TO" region

### METEREDMWFLOW Sign Convention
- **Positive flow**: Energy flows in the interconnector's named direction (FROM → TO)
- **Negative flow**: Energy flows in reverse direction (TO → FROM)
- Example: For VIC1-NSW1, positive = VIC exports to NSW, negative = NSW exports to VIC

### Interconnector Mapping
```python
interconnector_mapping = {
    'N-Q-MNSP1': {'from': 'NSW1', 'to': 'QLD1', 'name': 'NSW-QLD'},
    'NSW1-QLD1': {'from': 'NSW1', 'to': 'QLD1', 'name': 'NSW-QLD'},
    'VIC1-NSW1': {'from': 'VIC1', 'to': 'NSW1', 'name': 'VIC-NSW'},
    'V-SA': {'from': 'VIC1', 'to': 'SA1', 'name': 'VIC-SA'},
    'V-S-MNSP1': {'from': 'VIC1', 'to': 'SA1', 'name': 'VIC-SA'},
    'T-V-MNSP1': {'from': 'TAS1', 'to': 'VIC1', 'name': 'TAS-VIC'},
    # ... etc
}
```

## Update Process

### Combined Update Service
The `aemo-combined-update` service runs continuously:

1. **Initialization**: Creates updater instances for generation, price, rooftop, and transmission
2. **Main Loop**: Every 4.5 minutes (270 seconds):
   - Runs generation update (5-min data)
   - Runs price update (5-min data)
   - Runs rooftop update (30-min data, converted to 5-min)
   - Runs transmission update (5-min data)
3. **Error Handling**: Each updater fails independently, service continues

### Data Integrity Checks
The updater should perform:
- Check for missing time periods
- Validate data ranges (e.g., generation >= 0)
- Remove duplicates based on timestamp + identifier
- Maintain data retention policy (e.g., 30 days)

### Backfill Capability
For filling historical gaps:
- Check both CURRENT and ARCHIVE directories
- Handle nested ZIP structure for archives
- Merge with existing data without duplicates
- Process in date order to maintain consistency

## Running the Updater

### Start the Service
```bash
# Run as a background service
nohup python -m aemo_dashboard.combined.update_all > updater.log 2>&1 &

# Or use the installed script
aemo-combined-update
```

### Check Status
```bash
# Check if running
ps aux | grep aemo-combined-update

# View logs
tail -f /path/to/logs/aemo_dashboard.log
```

### Stop the Service
```bash
# Find and kill the process
pkill -f aemo-combined-update
```

## Troubleshooting

### 403 Forbidden Errors
- Always include User-Agent headers in requests
- Check URL format matches current NEMWEB structure
- Verify base URLs haven't changed

### Missing Data
- Run data integrity check to identify gaps
- Use backfill functionality for historical data
- Check both CURRENT and ARCHIVE directories

### Performance Issues
- Monitor file sizes - implement retention policy
- Use efficient parquet append operations
- Consider separate process for backfill operations

## Alert Systems

### SMS Price Alerts (Twilio) ✅ PRODUCTION READY

#### Overview
The AEMO Data Updater includes sophisticated SMS price alert functionality that sends notifications when electricity prices exceed critical thresholds. This system is inherited from the proven working price updater and fully integrated into the new collector system.

#### Current Configuration (Production)
```bash
ENABLE_SMS_ALERTS=true
TWILIO_ACCOUNT_SID=your_twilio_account_sid  # Get from Twilio console
TWILIO_AUTH_TOKEN=your_twilio_auth_token    # Get from Twilio console
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx            # Your Twilio phone number
MY_PHONE_NUMBER=+61xxxxxxxxx                # Your mobile number for alerts
```

#### Alert Triggers
- **High Price Alert**: Sent when price goes above $1,000/MWh
- **Extreme Price Alert**: Sent when price goes above $10,000/MWh (with 🚨 emoji)  
- **Recovery Alert**: Sent when price drops below $300/MWh after being high

#### Alert Examples
**High Price Alert:**
```
ITK price alert ⚠️ NSW1 HIGH PRICE: $1500.00/MWh at 14:35 on 14/07/2025. Threshold: $1000.0
```

**Extreme Price Alert:**
```
ITK price alert 🚨🚨🚨 SA1 EXTREME PRICE: $12000.00/MWh at 15:20 on 14/07/2025. Threshold: $1000.0
```

**Recovery Alert:**
```
ITK price alert ✅ NSW1 PRICE RECOVERED: $250.00/MWh at 16:45 on 14/07/2025. Below $300.0. Duration: 2h 10m
```

#### Technical Implementation
- **Integration Point**: `price_collector.py` line 266-272 (before logging new prices)
- **Module**: `twilio_price_alerts.py` (copied from working system)
- **State File**: `price_alert_state.pkl` (throttling and recovery tracking)
- **Cross-Machine**: Uses `Path.home()` for iCloud compatibility

### Email Alerts (iCloud) ✅ PRODUCTION READY  

#### Overview
Email alerts notify of new DUID discoveries in the generation data, indicating new power stations or generators entering the market.

#### Current Configuration (Production)
```bash
ENABLE_EMAIL_ALERTS=true
ALERT_EMAIL=your_email@example.com
ALERT_PASSWORD=your_app_specific_password  # App-specific password
RECIPIENT_EMAIL=recipient@example.com
SMTP_SERVER=smtp.mail.me.com              # For iCloud mail
SMTP_PORT=587
```

#### Use Cases
- **New DUID Discovery**: When generation collector finds unknown DUIDs
- **System Status**: Configuration test emails and health checks
- **Data Integrity**: Alerts for data quality issues

#### Technical Implementation
- **Integration**: Works with both new collectors and legacy generation dashboard
- **DUID Tracking**: Compares against known DUID mappings in `gen_info.pkl`
- **Exception Management**: Tracks DUIDs that should not trigger alerts
- **Cooldown**: 24-hour alert throttling to prevent spam

### Installation Requirements

#### For SMS Alerts
```bash
# Install Twilio dependency
uv pip install twilio>=8.0.0

# Or install with SMS support
uv pip install -e ".[sms]"
```

#### For Email Alerts
```bash
# No additional dependencies required
# Uses Python standard library smtplib
```

### Alert State Management
- **SMS State**: `price_alert_state.pkl` - tracks price thresholds and recovery
- **Email State**: Built into generation collector logic
- **Throttling**: Prevents spam with configurable cooldown periods
- **Cross-Machine**: All state files use `Path.home()` for portability

### Testing and Verification

#### Test SMS Alerts
```bash
# From status dashboard (port 5011)
# Click "Test Alerts" button

# Or programmatically
python -c "
from src.aemo_updater.alerts import AlertManager
from src.aemo_updater.config import get_config
manager = AlertManager(vars(get_config()))
print(manager.test_channels())
"
```

#### Test Email Alerts  
```bash
# Use the generation system test utility
cd /Users/davidleitch/.../genhist/
python test_email.py
```

### Production Deployment

#### Virtual Environment Setup
Virtual environments contain machine-specific binaries that cannot be synced between machines. On the production machine, create a fresh virtual environment:

```bash
# Navigate to the project directory (already synced via iCloud)
cd "/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/aemo-data-updater"

# Remove any existing .venv directory if present
rm -rf .venv

# Create fresh virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

#### Starting the Service

The project includes both a data collection service and a status dashboard:

1. **Status Dashboard** (port 5011):
   ```bash
   python run_dashboard.py
   ```
   - Access at http://localhost:5011
   - Shows real-time status of all collectors
   - Monitors data files but does NOT control the service

2. **Direct Service** (alternative):
   ```bash
   python -m aemo_updater service
   ```
   - Starts collectors immediately
   - Runs continuously in background

#### Credentials and Configuration
All alert credentials are configured in the `.env` file and will be automatically available on the production machine:
- Twilio SMS alerts (price thresholds)
- iCloud email alerts (new DUID discovery)
- Cross-machine paths using Path.home() for compatibility

## Future Enhancements

1. **Automated Backfill**: Detect and fill gaps automatically
2. **Data Validation**: Real-time anomaly detection
3. **Multi-Source Resilience**: Fallback to alternative sources
4. **Compression**: Periodic parquet file optimization
5. **Monitoring**: Health endpoints and metrics
6. **Enhanced Alerts**: Add generation failure and transmission limit alerts
7. **Extended History**: Add capability to download and store longer-term historical data using 30-minute intervals instead of 5-minute to reduce storage requirements