AEMO_spot is the directory where I am developing a dashboard that updates and provides electricity price and generation data. The data is mostly obtained from Nemweb. The main files at the moment are '/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/aemo-spot-dashboard/update_spot.py' and '/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/aemo-spot-dashboard/display_spot.py'. These programs download prices every 5 minutes and then display them.

Another file '/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/genhist/gen_dash.py' downloads and displays generation data by fuel class.

gen_dash is supposed to send me emails for missing DUIDs but at the moment I'm not receiving emails.

I don't want to mess with the running code right now, but I think I would like to move the three files and their development up to my git_hub account in a fresh repository  maybe put them all in in the one uv environment. 

1. Then I would like to fix the email functionality. 
2. Then I would like to move one of the figures in the gen dash, the one that displays capacity utilisation to a separate tab in the app. In due course there will be more tabs and more components to the dashboard. 
3. Then I would like to add transmission flows into the generation by fuel class treating the net flow into or out of a region as a fuel like batteries that can either be positive(inflow) or negative(outflow). 
4. The logs for all the code can be written to the one log file. This will make it easier to 

Before making significant changes to the code you will review the latest official holoviz panel documentation. The dashboard and its components should use the "material " template as discussed in a recent holoviz blog post. In addition generally when presenting data in tables try to use the latest version of the tabulator widget within the dashboard.

When we start a session you will yourself do a fresh review of the code to make yourself familiar with its functionality

Before making substantial changes to code check with me and use good git procedure so that we can revert to earlier versions.
	Before making substantial changes to code or implementing new functionality think carefully and make a detailed plan with check box stages.
	If you have 2 or 3 goes at a task but it still doesnt work. Pause think carefully, go back to the documentation and consider carefully whether the approach is correct or whether an alternative approach might be better. After considering an alternative again think carefully whether it really is better.

Since electricity volume is extensive and is updated every 5 minutes I generally prefer to keep it in parquet files.
When changes are made to the dashboard run the dashboard at local host and look at the output, possibly using playwright to make sure its readable and has the functionality we designed.

There will be more added to the dashboard over time.

## About transmission

To access 5-minute transmission flow data from the Australian Energy Market Operator (AEMO), you can utilize the NEMWeb platform, which provides detailed dispatch data, including interconnector flows.

### **Accessing 5-Minute Interconnector Flow Data**

The primary source for 5-minute interconnector flow data is the DISPATCHINTERCONNECTORRES table. This dataset includes: 

- **METEREDMWFLOW**: Actual measured flow in megawatts (MW) from SCADA systems.
- **MWFLOW**: Target flow for the upcoming 5-minute interval.
- **EXPORTLIMIT** and **IMPORTLIMIT**: Calculated limits for energy export and import.
- **MWLOSSES**: Calculated losses in MW. 

This data is updated every 5 minutes and is publicly accessible. 

### **Retrieving the Data**

You can download the dispatch data files from AEMO's NEMWeb portal. The files are available in ZIP format and contain CSV files with the relevant data. The filenames typically follow this pattern:()

PUBLIC_DISPATCHIS_YYYYMMDDHHMM_*.ZIP

### **Automating Data Retrieval**

To automate the process of downloading and storing this data every 5 minutes, you can write a script in a programming language like Python. Here's a basic outline:

1. **Set up a scheduler**: Use a task scheduler (like cron on Unix systems) to run your script every 5 minutes.()
2. **Download the latest file**: Your script should construct the URL for the latest dispatch file based on the current date and time, then download and extract the ZIP file.()
3. **Parse the CSV**: Extract the DISPATCHINTERCONNECTORRES data from the CSV file. 
4. **Store the data**: Save the extracted data to your local storage or a database for further analysis.()

Ensure your script includes error handling to manage potential issues like network errors or missing files.()

### **Additional Resources**

- **MMS Data Model Report**: Provides detailed information on the structure and fields of the DISPATCHINTERCONNECTORRES table. 
- **AEMO's Dispatch Data Page**: Offers access to various dispatch-related datasets and documentation. 

# AEMO Energy Dashboard - Development Notes

## ✅ **Current Status: FULLY OPERATIONAL - ALL CORE FEATURES COMPLETE**

The dashboard is now a comprehensive energy market analysis platform with four main tabs and advanced features:

### ✅ **Generation by Fuel Tab** 
- **Status:** Working perfectly with integrated layout
- **Layout:** Region selector on left side, chart subtabs on right side
- **Subtabs:** 
  - **Generation Stack:** Interactive stacked area chart showing generation by fuel type
  - **Capacity Utilization:** Capacity utilization percentages by fuel type  
- **Data:** Real-time AEMO generation data with 5-minute intervals
- **Region Control:** Left-side panel with region selector (NEM, NSW1, QLD1, SA1, TAS1, VIC1)
- **Data Integrity:** Fixed capacity calculations using SUMMED AEMO nameplate capacities

### ✅ **Average Price Analysis Tab**
- **Status:** Fully functional custom pivot table builder
- **Features:**
  - ✅ User-driven grouping system (Region, Fuel combinations)
  - ✅ Region filters (NSW1, QLD1, SA1, TAS1, VIC1) - all checked by default
  - ✅ Fuel filters (Coal, Gas, Solar, Wind, etc.) - all checked by default  
  - ✅ Column selection (Gen GWh, Rev $M, Price $/MWh, Util %, Cap MW, Station, Owner) - all checked by default
  - ✅ Hierarchical table with expandable fuel groups showing individual DUIDs
  - ✅ Date range controls (Last 7 Days, Last 30 Days, All Data, Custom Range)
  - ✅ Professional dark theme styling with proper contrast

### ✅ **Station Analysis Tab - COMPLETE WITH STATION/DUID SELECTION**
- **Status:** Fully operational with advanced aggregation features
- **Key Features:**
  - ✅ **Station vs DUID Toggle:** Users can analyze whole stations or individual units
  - ✅ **DUID-Based Grouping:** Automatic station discovery using DUID naming patterns (ER01,ER02,ER03,ER04 → "Eraring")
  - ✅ **Multi-Unit Aggregation:** Combines data from all units (e.g., Eraring's 4×720MW = 2,880MW total)
  - ✅ **Dual-Axis Charts:** Generation (MW) on left, Price ($/MWh) on right for both time series and time-of-day
  - ✅ **Smart Resampling:** Automatic hourly aggregation for longer periods, 5-minute for short periods
  - ✅ **Date Controls:** Last 7/30 Days, All Data presets with custom range picker - **WORKING FOR BOTH MODES**
  - ✅ **Performance Metrics:** Revenue, capacity factor, operating hours, peak values
  - ✅ **Search Interface:** Fuzzy search by station name or DUID with popular stations dropdown
  - ✅ **Chart Subtabs:** Time Series, Time-of-Day, Summary Statistics

### ✅ **Dashboard Infrastructure**
- **Title:** "Nem Analysis" with white text styling
- **Footer:** "Last Updated: [time] | data:AEMO, design ITK" with white text
- **Theme:** Professional dark theme with Material UI template
- **Data Integration:** 2.7M+ integrated generation+price records
- **Performance:** Optimized with smart data filtering and chart rendering

## 🎯 **Planned Dashboard Extensions**

### **Generation by Fuel Tab Enhancements**
- **Rooftop Solar Integration:** Add 30-minute rooftop solar data source to complement existing generation data
- **Transmission Flows:** Integrate interconnector flows as virtual "fuel" type (positive=inflow, negative=outflow)

### **New Tabs Required**
1. **Transmission Tab:** Dedicated analysis of interconnector flows between regions
2. **Comparison Tab:** Side-by-side comparison of stations, regions, or time periods  
3. **Summary Tab:** High-level dashboard with key metrics and trends

### **Future Data Sources**
- **30-minute Rooftop Solar:** AEMO's distributed generation data
- **5-minute Transmission:** DISPATCHINTERCONNECTORRES table from NEMWeb
- **Additional Metrics:** Market caps, constraint data, forecast accuracy

## Dashboard Control Commands

### Restart Dashboard
```bash
# Kill existing dashboard process
pkill -f "python -m aemo_dashboard"

# Start dashboard (run from src directory)
cd "/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/aemo-energy-dashboard/src" && uv run python -m aemo_dashboard.generation.gen_dash &
```

### Dashboard URLs
- Main dashboard: http://localhost:5010
- Dashboard title: "Nem Analysis" 
- Footer: "Last Updated: [time] | data:AEMO, design ITK"
- Four main tabs: Generation by Fuel | Average Price Analysis | Station Analysis

### Troubleshooting
- If port 5010 is in use: `lsof -ti:5010 | xargs kill -9`
- Check logs: `tail -f /Users/davidleitch/Library/Mobile\ Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/aemo-energy-dashboard/logs/aemo_dashboard.log`

## Technical Implementation Notes

### Station vs DUID Selection Architecture
```python
# DUID pattern recognition for station grouping
import re
match = re.match(r'^(.+?)(\d+)$', duid)
base_name = match.group(1)  # "ER" from "ER01", "GSTONE" from "GSTONE1"

# Multi-DUID data aggregation  
filter_target = ['ER01', 'ER02', 'ER03', 'ER04']  # Station mode
filter_target = 'ER01'  # DUID mode
```

### Data Integration Pipeline
- **Generation Data:** 5-minute SCADA values from AEMO dispatch
- **Price Data:** Regional reference prices (RRP) from spot market
- **DUID Mapping:** Station names, capacities, fuel types, ownership
- **Revenue Calculation:** Generation × Price × (5/60) hours

### Chart Implementation
- **Dual-Axis:** Bokeh with extra_y_ranges and LinearAxis
- **Time Series:** Smart hourly resampling for >2 day periods
- **Interactivity:** Linked zooming, hover tooltips, legend toggle

## Recent Major Achievements ✅

### All Critical Issues Resolved
- ✅ **Station Aggregation:** DUID-based grouping more reliable than site names
- ✅ **Date Controls:** Working properly for both station and DUID modes  
- ✅ **Dual-Axis Charts:** Proper Bokeh implementation with color-coded axes
- ✅ **UI Consistency:** White text styling, clean table display without index columns
- ✅ **Performance:** 25,000+ records filtered and analyzed in real-time for multi-unit stations
- ✅ **Data Quality:** Robust handling of 528 DUIDs across 420+ stations

The dashboard foundation is now solid and ready for the planned extensions (rooftop solar, transmission flows, and additional tabs).

## 🔧 **ROOFTOP SOLAR INTEGRATION - STATUS & ISSUES**

### ✅ **Current Status**
- **Integration Complete**: Rooftop solar now displays in both NEM and individual region views
- **Data Source**: AEMO 30-minute distributed PV data from `https://www.nemweb.com.au/Reports/Current/ROOFTOP_PV/ACTUAL/`
- **Visualization**: Lighter yellow band positioned after regular solar in fuel stack
- **Regional Support**: All main regions (NSW1, QLD1, SA1, TAS1, VIC1) plus NEM total

### 📁 **Data Locations**
- **Current Data Files**: `https://www.nemweb.com.au/Reports/Current/ROOFTOP_PV/ACTUAL/` (30-minute ZIP files)
  - **Coverage**: ~14 days of rolling data (673 files from June 29 - July 13)
  - **File Format**: `PUBLIC_ROOFTOP_PV_ACTUAL_MEASUREMENT_YYYYMMDDHHMMSS_*.zip`
  - **Update Frequency**: Every 30 minutes
- **Historical Archives**: `http://nemweb.com.au/Reports/Archive/ROOFTOP_PV/ACTUAL/` (weekly archives)
- **Local Storage**: `/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/rooftop_solar.parquet`
- **Update Module**: `/src/aemo_dashboard/rooftop/update_rooftop.py`

### ✅ **COMPLETED INVESTIGATION RESULTS**

#### **Issue 1: Data Coverage - RESOLVED**
- **Problem**: Missing rooftop data causing gaps in dashboard display
- **Solution**: Collected ALL 673 files from NEMWEB Current directory (June 29 - July 13)
- **Result**: Complete dataset with 4,038 records, 577 records in last 48 hours
- **Coverage**: Continuous data with QLD1 peaks up to 3,860 MW during midday

#### **Issue 2: 30-min to 5-min Conversion Algorithm - VERIFIED**
- **Method**: 6-period moving average with weighted interpolation
- **Formula**: `value = ((6-j)*current + j*next) / 6` for periods j=0..5
- **Test Results**: Algorithm produces realistic solar curves with smooth 167MW/5min transitions
- **Status**: ✅ Working correctly

#### **Issue 3: Automatic Update Loop - VERIFIED**
- **Status**: ✅ Running properly every 15 minutes
- **Evidence**: Log entries show successful downloads and processing
- **Coverage**: 15-minute cycle adequately captures 30-minute AEMO publications

### 🏆 **ROOFTOP SOLAR INTEGRATION STATUS: COMPLETE**

✅ **All rooftop solar issues resolved**
✅ **Complete dataset collected from NEMWEB**  
✅ **Dashboard displaying continuous rooftop data**
✅ **Update loop running automatically**
✅ **Algorithm verified and optimized**

### 💡 **MAINTENANCE NOTES**
1. **Data Source**: NEMWEB Current directory maintains ~14 days rolling history
2. **Update Frequency**: Every 15 minutes collects new 30-minute AEMO files
3. **Archive Access**: Use Archive directory for historical data beyond 14 days
4. **File Processing**: 100% success rate processing 673 files with 0 errors

## 📋 **SESSION SUMMARY: ROOFTOP SOLAR DATA INTEGRATION COMPLETE**

### **🎯 Problem Identified**
- User reported rooftop solar data gaps in dashboard screenshot
- Investigation revealed missing data coverage causing discontinuous yellow bands
- Only partial data available, missing crucial 14+ hours of recent rooftop generation

### **🔍 Investigation Results** 
- **Root Cause**: Previous data collection only captured 5 recent files (2 hours) instead of full available dataset
- **Data Available**: NEMWEB Current directory contained 673 files spanning 14 days (June 29 - July 13)
- **Coverage Gap**: Missing majority of historical rooftop data needed for 48-hour dashboard view

### **✅ Solution Implemented**
1. **Complete Data Collection**: Scraped and processed ALL 673 rooftop files from NEMWEB
   - **Source**: `https://www.nemweb.com.au/Reports/Current/ROOFTOP_PV/ACTUAL/`
   - **Coverage**: 14 days continuous data (June 29 00:30 - July 13 00:55)
   - **Success Rate**: 100% (673/673 files processed with 0 errors)

2. **Dataset Verification**: 
   - **Total Records**: 4,038 rooftop solar records
   - **Recent Coverage**: 577 records in last 48 hours (dashboard window)
   - **Peak Values**: QLD1 up to 3,860 MW during midday periods
   - **Data Quality**: Continuous timeline with no gaps

3. **Algorithm Validation**:
   - **30-min to 5-min Conversion**: ✅ Working correctly with realistic solar curves  
   - **Update Loop**: ✅ 15-minute cycle functioning properly
   - **Dashboard Integration**: ✅ Rooftop solar displaying in both NEM and regional views

### **🏆 Final Results**
- **Complete Dataset**: Built from 673 NEMWEB files spanning 14 days
- **Dashboard Display**: Continuous rooftop solar bands now visible in QLD1 and all regions
- **Automated Updates**: 15-minute cycle maintains current data collection
- **Documentation**: Updated CLAUDE.md with accurate file locations and process details

### **📁 Key File Locations**
- **Rooftop Data**: `/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/rooftop_solar.parquet`
- **Update Module**: `/src/aemo_dashboard/rooftop/update_rooftop.py`
- **Dashboard**: `/src/aemo_dashboard/generation/gen_dash.py`
- **NEMWEB Source**: `https://www.nemweb.com.au/Reports/Current/ROOFTOP_PV/ACTUAL/`

The rooftop solar integration is now **fully operational** with complete historical data and continuous updates. Dashboard displays smooth rooftop solar curves across all time periods with no data gaps.

---

# 🏗️ **ARCHITECTURAL REFACTORING PLAN: SERVICE SEPARATION**

## **Executive Summary**

Split the monolithic dashboard application into two independent services:
1. **Data Collection Service** - 24/7 background process for NEMWEB data collection
2. **Dashboard Application** - On-demand visualization interface

This separation will improve reliability, performance, and maintainability.

## **Current Architecture (Monolithic)**

### **Directory Structure**
```
aemo-energy-dashboard/
├── src/
│   └── aemo_dashboard/
│       ├── __init__.py
│       ├── __main__.py              # Entry point
│       ├── generation/
│       │   └── gen_dash.py          # MAIN FILE: Contains both data collection AND UI
│       ├── rooftop/
│       │   └── update_rooftop.py    # Rooftop data collection (30-min to 5-min conversion)
│       ├── analysis/
│       │   └── price_analysis_ui.py # Price analysis tab UI
│       ├── station/
│       │   └── station_analysis_ui.py # Station analysis tab UI
│       └── shared/
│           ├── config.py            # Configuration settings
│           ├── logging_config.py    # Logging setup
│           └── email_alerts.py      # Email notification system
├── data/
│   ├── gen_output.parquet          # Generation data (~13MB, growing ~0.6MB/day)
│   ├── spot_hist.parquet           # Price data (~0.3MB)
│   └── gen_info.pkl                # DUID mappings (static reference)
├── logs/
│   └── aemo_dashboard.log          # Combined logs
└── CLAUDE.md                       # This documentation file
```

**External Data Files:**
```
/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/
├── rooftop_solar.parquet           # Rooftop solar data
└── transmission_flows.parquet      # Transmission interconnector data
```

### **Current Data Flow**

1. **Single Process** runs `gen_dash.py` which:
   - Downloads NEMWEB data every 5 minutes (generation, prices)
   - Processes and saves to parquet files
   - Serves Panel dashboard on http://localhost:5010
   - Updates UI when users interact

2. **Problems with Current Architecture:**
   - Dashboard crash = data collection stops
   - Can't update UI without risking data pipeline
   - Heavy memory usage even when no users
   - Difficult to debug data vs UI issues
   - Single log file mixes data collection and UI events

## **Target Architecture (Service Separation)**

### **Proposed Directory Structure**
```
aemo-data-service/                   # NEW: Standalone data collection service
├── src/
│   └── aemo_data/
│       ├── __init__.py
│       ├── __main__.py             # Service entry point
│       ├── collectors/
│       │   ├── __init__.py
│       │   ├── base_collector.py   # Abstract base class
│       │   ├── generation.py       # 5-min generation data
│       │   ├── price.py            # 5-min spot prices
│       │   ├── rooftop.py          # 30-min rooftop solar
│       │   └── transmission.py     # 5-min interconnector flows
│       ├── processors/
│       │   ├── __init__.py
│       │   └── rooftop_converter.py # 30-min to 5-min conversion
│       ├── nemweb/
│       │   ├── __init__.py
│       │   ├── client.py           # NEMWEB HTTP client
│       │   └── parsers.py          # ZIP/CSV parsing utilities
│       ├── storage/
│       │   ├── __init__.py
│       │   └── parquet_manager.py  # Safe concurrent parquet operations
│       ├── service.py              # Main service orchestrator
│       └── config.py               # Service configuration
├── systemd/
│   └── aemo-data.service          # Linux service definition
├── scripts/
│   ├── install_service.sh         # Service installation script
│   └── check_health.py            # Health monitoring
├── logs/
│   └── aemo_data_service.log      # Data collection logs only
├── requirements.txt                # Minimal dependencies
└── README.md                       # Service documentation

aemo-dashboard/                      # MODIFIED: Pure visualization layer
├── src/
│   └── aemo_dashboard/
│       ├── __init__.py
│       ├── __main__.py             # Dashboard entry point
│       ├── data/
│       │   ├── __init__.py
│       │   └── loader.py           # Parquet file reader
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── generation_tab.py   # Generation by fuel UI
│       │   ├── price_tab.py        # Price analysis UI
│       │   ├── station_tab.py      # Station analysis UI
│       │   └── layout.py           # Main dashboard layout
│       ├── visualizations/
│       │   ├── __init__.py
│       │   ├── fuel_stack.py       # Stacked area charts
│       │   ├── price_charts.py     # Price visualizations
│       │   └── utilization.py      # Capacity utilization
│       └── config.py               # Dashboard configuration
├── logs/
│   └── aemo_dashboard_ui.log      # UI logs only
├── requirements.txt                # UI dependencies (panel, hvplot, etc)
└── README.md                       # Dashboard documentation

aemo-common/                         # NEW: Shared components
├── src/
│   └── aemo_common/
│       ├── __init__.py
│       ├── data_models.py         # Shared data structures
│       ├── constants.py           # DUID lists, fuel types, regions
│       ├── file_paths.py          # Centralized file path management
│       └── time_utils.py          # NEM time handling utilities
└── setup.py                        # Installable package
```

## **Implementation Plan**

### **Phase 1: Extract Data Collection (Week 1)**

**Task 1.1: Create Base Collector Architecture**
```python
# aemo_data/collectors/base_collector.py
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Dict, Any
import logging

class BaseCollector(ABC):
    """Abstract base class for all NEMWEB data collectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.output_file = config['output_file']
        self.update_interval = config.get('update_interval', 300)  # 5 minutes
        
    @abstractmethod
    async def fetch_latest_data(self) -> Optional[pd.DataFrame]:
        """Fetch latest data from NEMWEB"""
        pass
        
    @abstractmethod
    async def process_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Process raw data into final format"""
        pass
        
    async def collect_and_save(self) -> bool:
        """Main collection workflow"""
        try:
            # Fetch
            raw_data = await self.fetch_latest_data()
            if raw_data is None:
                return False
                
            # Process
            processed_data = await self.process_data(raw_data)
            
            # Save
            await self.save_to_parquet(processed_data)
            
            self.logger.info(f"Successfully collected {len(processed_data)} records")
            return True
            
        except Exception as e:
            self.logger.error(f"Collection failed: {e}")
            return False
    
    async def save_to_parquet(self, df: pd.DataFrame):
        """Thread-safe parquet writing"""
        from aemo_common.file_utils import safe_write_parquet
        safe_write_parquet(df, self.output_file)
```

**Task 1.2: Implement Generation Collector**
```python
# aemo_data/collectors/generation.py
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from .base_collector import BaseCollector

class GenerationCollector(BaseCollector):
    """Collects 5-minute generation SCADA data"""
    
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "http://nemweb.com.au/Reports/Current/Dispatch_SCADA/"
        
    async def fetch_latest_data(self) -> pd.DataFrame:
        """Download latest DISPATCHSCADA file"""
        # Find latest file
        latest_file = await self._find_latest_scada_file()
        if not latest_file:
            return None
            
        # Download and parse
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{latest_file}") as response:
                content = await response.read()
                
        # Extract CSV from ZIP
        df = self._parse_scada_zip(content)
        return df
        
    async def process_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Process SCADA data"""
        # Filter columns
        df = raw_data[['SETTLEMENTDATE', 'DUID', 'SCADAVALUE']].copy()
        
        # Rename columns
        df.columns = ['settlementdate', 'duid', 'scadavalue']
        
        # Convert timestamp
        df['settlementdate'] = pd.to_datetime(df['settlementdate'])
        
        # Merge with existing data
        existing = pd.read_parquet(self.output_file)
        combined = pd.concat([existing, df]).drop_duplicates(
            subset=['settlementdate', 'duid']
        )
        
        # Keep only recent data (configurable)
        cutoff = datetime.now() - timedelta(days=self.config.get('retention_days', 30))
        combined = combined[combined['settlementdate'] >= cutoff]
        
        return combined.sort_values(['settlementdate', 'duid'])
```

**Task 1.3: Create Service Orchestrator**
```python
# aemo_data/service.py
import asyncio
import signal
from typing import List
from .collectors import (
    GenerationCollector,
    PriceCollector,
    RooftopCollector,
    TransmissionCollector
)

class AEMODataService:
    """Main service that orchestrates all collectors"""
    
    def __init__(self, config):
        self.config = config
        self.collectors = self._initialize_collectors()
        self.running = True
        
    def _initialize_collectors(self) -> List[BaseCollector]:
        """Initialize all collectors with config"""
        return [
            GenerationCollector(self.config['generation']),
            PriceCollector(self.config['price']),
            RooftopCollector(self.config['rooftop']),
            TransmissionCollector(self.config['transmission'])
        ]
        
    async def run_forever(self):
        """Main service loop"""
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)
        
        while self.running:
            # Run all collectors
            tasks = [collector.collect_and_save() for collector in self.collectors]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            for collector, result in zip(self.collectors, results):
                if isinstance(result, Exception):
                    logger.error(f"{collector.__class__.__name__} failed: {result}")
                    
            # Wait for next interval
            await asyncio.sleep(self.config['update_interval'])
            
    def _shutdown(self, signum, frame):
        """Graceful shutdown"""
        logger.info("Shutdown signal received")
        self.running = False
```

### **Phase 2: Refactor Dashboard (Week 2)**

**Task 2.1: Create Data Loader**
```python
# aemo_dashboard/data/loader.py
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta

class DataLoader:
    """Loads data from parquet files for dashboard"""
    
    def __init__(self, config):
        self.config = config
        self.cache = {}
        self.cache_timestamp = {}
        
    def load_generation_data(self, 
                           hours_back: int = 48,
                           regions: Optional[List[str]] = None) -> pd.DataFrame:
        """Load generation data with caching"""
        
        cache_key = f"gen_{hours_back}_{regions}"
        
        # Check cache (5 minute TTL)
        if self._is_cache_valid(cache_key, ttl_minutes=5):
            return self.cache[cache_key]
            
        # Load from parquet
        df = pd.read_parquet(self.config['generation_file'])
        
        # Filter by time
        cutoff = datetime.now() - timedelta(hours=hours_back)
        df = df[df['settlementdate'] >= cutoff]
        
        # Filter by regions if specified
        if regions:
            # Join with DUID mapping to get regions
            duid_map = pd.read_pickle(self.config['duid_mapping_file'])
            df = df.merge(duid_map[['duid', 'region']], on='duid')
            df = df[df['region'].isin(regions)]
            
        # Update cache
        self.cache[cache_key] = df
        self.cache_timestamp[cache_key] = datetime.now()
        
        return df
        
    def _is_cache_valid(self, key: str, ttl_minutes: int) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        age = datetime.now() - self.cache_timestamp[key]
        return age.total_seconds() < (ttl_minutes * 60)
```

**Task 2.2: Refactor Generation Tab**
```python
# aemo_dashboard/ui/generation_tab.py
import panel as pn
import param
from ..data.loader import DataLoader
from ..visualizations.fuel_stack import create_fuel_stack_chart

class GenerationTab(param.Parameterized):
    """Generation by Fuel tab - pure UI component"""
    
    region = param.Selector(default='NEM', objects=['NEM', 'NSW1', 'QLD1', 'SA1', 'TAS1', 'VIC1'])
    time_window = param.Selector(default='48 hours', objects=['24 hours', '48 hours', '7 days'])
    
    def __init__(self, data_loader: DataLoader, **params):
        super().__init__(**params)
        self.data_loader = data_loader
        
    def create_layout(self):
        """Create the tab layout"""
        return pn.Row(
            self.create_controls(),
            self.create_chart_area()
        )
        
    @param.depends('region', 'time_window')
    def create_chart_area(self):
        """Create visualization area"""
        # Convert time window to hours
        hours = {'24 hours': 24, '48 hours': 48, '7 days': 168}[self.time_window]
        
        # Load data
        gen_data = self.data_loader.load_generation_data(
            hours_back=hours,
            regions=None if self.region == 'NEM' else [self.region]
        )
        
        # Create visualizations
        fuel_stack = create_fuel_stack_chart(gen_data, self.region)
        
        return pn.Column(
            "# Generation by Fuel Type",
            fuel_stack
        )
```

### **Phase 3: Deployment & Operations (Week 3)**

**Task 3.1: Create Systemd Service**
```ini
# systemd/aemo-data.service
[Unit]
Description=AEMO Data Collection Service
After=network.target

[Service]
Type=simple
User=aemo
Group=aemo
WorkingDirectory=/opt/aemo-data-service
Environment="PATH=/opt/aemo-data-service/venv/bin"
ExecStart=/opt/aemo-data-service/venv/bin/python -m aemo_data
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/aemo/data-service.log
StandardError=append:/var/log/aemo/data-service-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Task 3.2: Installation Script**
```bash
#!/bin/bash
# scripts/install_service.sh

# Create user
sudo useradd -r -s /bin/false aemo

# Create directories
sudo mkdir -p /opt/aemo-data-service
sudo mkdir -p /var/log/aemo
sudo mkdir -p /var/lib/aemo/data

# Set permissions
sudo chown -R aemo:aemo /opt/aemo-data-service
sudo chown -R aemo:aemo /var/log/aemo
sudo chown -R aemo:aemo /var/lib/aemo

# Install service
sudo cp systemd/aemo-data.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aemo-data.service
sudo systemctl start aemo-data.service
```

**Task 3.3: Health Monitoring**
```python
# scripts/check_health.py
#!/usr/bin/env python3
import sys
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

def check_data_freshness(file_path: Path, max_age_minutes: int = 10) -> bool:
    """Check if data file has recent updates"""
    if not file_path.exists():
        return False
        
    # Check file modification time
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    age = datetime.now() - mtime
    
    if age > timedelta(minutes=max_age_minutes):
        return False
        
    # Check actual data recency
    df = pd.read_parquet(file_path)
    if 'settlementdate' in df.columns:
        latest = pd.to_datetime(df['settlementdate']).max()
        data_age = datetime.now() - latest
        return data_age < timedelta(minutes=max_age_minutes)
        
    return True

def main():
    """Health check script for monitoring tools"""
    files_to_check = [
        ('/var/lib/aemo/data/gen_output.parquet', 10),
        ('/var/lib/aemo/data/spot_hist.parquet', 10),
        ('/var/lib/aemo/data/rooftop_solar.parquet', 35),  # 30-min data
    ]
    
    all_healthy = True
    
    for file_path, max_age in files_to_check:
        path = Path(file_path)
        if check_data_freshness(path, max_age):
            print(f"OK: {path.name}")
        else:
            print(f"FAIL: {path.name} - data too old or missing")
            all_healthy = False
            
    sys.exit(0 if all_healthy else 1)

if __name__ == "__main__":
    main()
```

## **Migration Guide**

### **Step 1: Prepare Environment**
```bash
# Clone repositories
git clone <repo-url> aemo-data-service
git clone <repo-url> aemo-dashboard

# Create virtual environments
cd aemo-data-service && python -m venv venv
cd aemo-dashboard && python -m venv venv
```

### **Step 2: Extract Collectors from Existing Code**

**From `gen_dash.py`, extract:**
- SCADA download logic → `generation.py`
- Price download logic → `price.py`
- File parsing utilities → `nemweb/parsers.py`

**From `update_rooftop.py`, move:**
- Entire module → `rooftop.py`
- 30-min conversion → `processors/rooftop_converter.py`

### **Step 3: Update Configuration**

**Old configuration (single file):**
```python
# shared/config.py
GEN_OUTPUT_FILE = BASE_PATH / 'gen_output.parquet'
UPDATE_INTERVAL = 5 * 60  # 5 minutes
```

**New configuration (split):**
```python
# aemo_data/config.py
DATA_CONFIG = {
    'generation': {
        'output_file': '/var/lib/aemo/data/gen_output.parquet',
        'update_interval': 300,
        'retention_days': 30
    },
    'price': {
        'output_file': '/var/lib/aemo/data/spot_hist.parquet',
        'update_interval': 300,
        'retention_days': 365
    }
}

# aemo_dashboard/config.py  
DASHBOARD_CONFIG = {
    'data_files': {
        'generation': '/var/lib/aemo/data/gen_output.parquet',
        'price': '/var/lib/aemo/data/spot_hist.parquet',
    },
    'cache_ttl': 300,  # 5 minutes
    'default_time_window': 48  # hours
}
```

### **Step 4: Testing Strategy**

1. **Unit Tests for Collectors**
```python
# tests/test_generation_collector.py
async def test_generation_collector():
    config = {'output_file': 'test.parquet', 'update_interval': 300}
    collector = GenerationCollector(config)
    
    # Mock NEMWEB response
    with aioresponses() as mocked:
        mocked.get(collector.base_url, body=sample_zip_content)
        
        result = await collector.collect_and_save()
        assert result == True
        assert Path('test.parquet').exists()
```

2. **Integration Tests**
```python
# tests/test_service_integration.py
async def test_full_collection_cycle():
    """Test all collectors together"""
    service = AEMODataService(test_config)
    
    # Run one cycle
    await service.run_one_cycle()
    
    # Verify all files updated
    for file_path in expected_files:
        assert Path(file_path).exists()
        assert check_data_freshness(Path(file_path))
```

3. **Load Testing**
```python
# tests/test_dashboard_performance.py
def test_dashboard_startup_time():
    """Dashboard should start in <2 seconds"""
    start = time.time()
    
    dashboard = AEMODashboard()
    dashboard.load_data()
    
    elapsed = time.time() - start
    assert elapsed < 2.0
```

## **Key Design Decisions**

### **1. Async Architecture**
- Use `asyncio` for concurrent data collection
- Non-blocking I/O for NEMWEB downloads
- Parallel collector execution

### **2. File Locking Strategy**
- Atomic writes using temp files + rename
- Pandas handles read locks automatically
- No explicit locking needed for parquet

### **3. Error Handling**
- Each collector fails independently
- Service continues if one collector fails
- Comprehensive logging for debugging

### **4. Data Retention**
- Configurable retention per data type
- Automatic cleanup of old data
- Prevents unbounded growth

### **5. Configuration Management**
- Separate configs for service vs dashboard
- Environment variable overrides
- Sensible defaults

## **Common Pitfalls to Avoid**

1. **Don't share database connections** between processes
2. **Don't use file locks** - use atomic operations instead
3. **Don't store state in memory** - use files for persistence
4. **Don't ignore timezone issues** - AEMO uses AEST not AEDT
5. **Don't poll too frequently** - respect NEMWEB rate limits

## **Success Metrics**

- **Data Service Uptime**: >99.9%
- **Data Freshness**: <10 minutes old
- **Dashboard Startup**: <2 seconds
- **Memory Usage**: <500MB for service, <2GB for dashboard
- **CPU Usage**: <5% average for service

## **Future Enhancements**

1. **Add Redis Cache** for faster dashboard queries
2. **Implement WebSocket updates** for real-time dashboard
3. **Add Prometheus metrics** for monitoring
4. **Create Docker containers** for easier deployment
5. **Add data validation** and anomaly detection

---

**This plan provides a complete roadmap for separating the data collection service from the dashboard UI. The implementation should proceed in phases, with thorough testing at each stage.**