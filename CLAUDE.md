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