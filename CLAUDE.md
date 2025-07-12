# AEMO Energy Dashboard - Development Notes

## Current Status ✅ FULLY OPERATIONAL - RESTRUCTURED DESIGN

The dashboard is now fully functional with three main tabs (Generation by Fuel tab restructured):

### ✅ **Generation by Fuel Tab** - RESTRUCTURED DESIGN
- **Status:** Working perfectly with new layout structure
- **New Layout:** Region selector moved to left side, charts in subtabs on right side
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

### 🎯 **Next Priority: Station Analysis Tab**

## New Feature: Station Analysis Tab

### Overview
Add a fourth tab focused on individual station/DUID analysis with detailed performance metrics and time-of-day patterns.

### Core Features

#### 1. **Station Search Interface**
```
┌─ Station Search ────────────────────────────────┐
│ Search by Station Name or DUID:                │
│ [🔍 Type station name or DUID...        ] [Go] │
│                                                 │
│ Suggestions:                                    │
│ • Eraring Power Station (ERARING)              │ 
│ • Loy Yang A (LOYA1, LOYA2, LOYA3, LOYA4)     │
│ • Taralga Wind Farm (TARALGA1)                │
└─────────────────────────────────────────────────┘
```

**Requirements:**
- **Approximate Search:** Fuzzy matching for station names and DUIDs
- **Auto-suggestions:** Dropdown with matching results as user types
- **Multiple DUIDs:** Handle stations with multiple units (e.g., Loy Yang A has 4 units)
- **Search History:** Recent searches for quick access

#### 2. **Time Period Controls**
```
┌─ Time Period Selection ─────────────────────────┐
│ Date Range:  [2025-06-18] to [2025-07-12]      │
│ Quick Presets: [Last 7 Days] [Last 30 Days]    │
│               [Last 3 Months] [All Data]       │
└─────────────────────────────────────────────────┘
```

**Requirements:** 
- Reuse existing date selector components from Price Analysis tab
- Same preset buttons and date picker functionality

#### 3. **Chart 1: Time Series Analysis**
```
┌─ Performance Over Time ─────────────────────────┐
│                                                 │
│  Revenue ($M) ┌─────────────────────────────┐   │
│      150      │ ████████                    │   │
│      100      │ ████████████████            │   │
│       50      │ ████████████████████████    │   │
│        0      └─────────────────────────────┘   │
│                                                 │
│  Price ($/MWh)┌─────────────────────────────┐   │
│      400      │ ▲                           │   │
│      200      │ ▲  ▲    ▲                   │   │
│        0      │ ▲  ▲ ▲▲ ▲ ▲▲▲▲▲             │   │
│               └─────────────────────────────┘   │
│                                                 │
│  Generation   ┌─────────────────────────────┐   │
│  (MWh)   800  │ ████████████████████████    │   │
│          400  │ ████████████████████████    │   │
│            0  └─────────────────────────────┘   │
│                Jun 18    Jul 1     Jul 12      │
└─────────────────────────────────────────────────┘
```

**Requirements:**
- **Triple-panel Chart:** Revenue (top), Price (middle), Generation (bottom)
- **Interactive:** Linked zooming and panning across all three panels
- **Hover Tooltips:** Show exact values with timestamp
- **Time Aggregation:** User selectable (5-min, hourly, daily averages)

#### 4. **Chart 2: Time-of-Day Analysis**
```
┌─ Average Performance by Time of Day ────────────┐
│                                                 │
│  Avg Values   ┌─────────────────────────────┐   │
│               │     ████████                │   │
│               │   ████████████              │   │
│               │ ████████████████            │   │
│               └─────────────────────────────┘   │
│               00:00   06:00   12:00   18:00    │
│                                                 │
│ Legend: ■ Generation (MWh)  ■ Revenue ($K)      │
│         ○ Price ($/MWh)                         │
└─────────────────────────────────────────────────┘
```

**Requirements:**
- **24-Hour View:** X-axis shows hours 00:00 to 23:59
- **Multiple Metrics:** Generation, Revenue, Price overlaid with different scales
- **Mean Calculation:** Average values across the entire selected time period
- **Dual Y-Axis:** Left axis for Generation/Revenue, right axis for Price

#### 5. **Summary Statistics Table**
```
┌─ Station Performance Summary ───────────────────┐
│ Station: Eraring Power Station (ERARING)       │
│ Period: 2025-06-18 to 2025-07-12 (23 days)     │
│                                                 │
│ Metric                  │ Value      │ Rank    │
│ ──────────────────────────────────────────────  │
│ Total Generation (GWh)  │ 1,234.5    │ #3/528  │
│ Total Revenue ($M)      │ $87.2      │ #5/528  │  
│ Average Price ($/MWh)   │ $70.65     │ #45/528 │
│ Capacity Factor (%)     │ 67.8%      │ #12/528 │
│ Peak Generation (MW)    │ 2,640      │ Max Cap │
│ Peak Revenue Hour ($K)  │ $1,847     │ 14:30   │
│ Best Price Received     │ $1,234/MWh │ Jun 23  │
│ ──────────────────────────────────────────────  │
│ Total Operating Hours   │ 498.2      │ 90.4%   │ 
│ Zero Generation Hours   │ 53.8       │ 9.6%    │
└─────────────────────────────────────────────────┘
```

**Requirements:**
- **Key Performance Metrics:** Generation, Revenue, Price, Capacity Factor
- **Ranking:** Position relative to all other DUIDs in same period
- **Operational Statistics:** Operating hours, peak values, timing
- **Market Position:** Performance ranking within fuel class

## Implementation Plan: Station Analysis Tab

### Development Strategy

#### Phase 1: Core Infrastructure (Days 1-2)
**Objective:** Set up basic tab structure and data access patterns

**Tasks:**
1. **Create Module Structure**
   ```
   src/aemo_dashboard/station/
   ├── __init__.py
   ├── station_analysis.py      # Data processing engine
   ├── station_analysis_ui.py   # UI components
   └── station_search.py        # Search functionality
   ```

2. **Basic Tab Integration**
   - Add "Station Analysis" tab to main dashboard (`gen_dash.py`)
   - Import station UI component
   - Ensure consistent dark theme styling

3. **Data Access Setup**
   - Extend existing `PriceAnalysisMotor` or create `StationAnalysisMotor`
   - Reuse integrated generation + price data from existing system
   - Add DUID lookup functionality

#### Phase 2: Search Interface (Days 2-3)
**Objective:** Implement fuzzy search with auto-suggestions

**Key Components:**
1. **Search Engine (`station_search.py`)**
   ```python
   from fuzzywuzzy import fuzz
   import pandas as pd
   
   class StationSearchEngine:
       def __init__(self, gen_info_df):
           self.gen_info_df = gen_info_df
           self.search_index = self._build_search_index()
       
       def fuzzy_search(self, query, limit=10):
           # Implement fuzzy matching on station names and DUIDs
           
       def get_suggestions(self, partial_query):
           # Return auto-complete suggestions
   ```

2. **Search UI Components**
   - `AutocompleteInput` widget with dropdown suggestions
   - Recent searches storage (localStorage via Panel)
   - Search result display with station details

3. **Integration Points**
   - Connect to existing `gen_info.pkl` data
   - Use Panel's reactive programming for real-time suggestions

#### Phase 3: Time Series Charts (Days 3-5)
**Objective:** Create interactive time series visualization

**Technical Approach:**
1. **Reuse Date Controls**
   ```python
   # Import from existing price analysis
   from ..analysis.price_analysis_ui import create_date_controls
   
   # Or extract shared components to:
   # ..shared.date_controls import DateControlMixin
   ```

2. **Triple-Panel Chart Architecture**
   ```python
   import hvplot.pandas
   import holoviews as hv
   from holoviews import opts
   
   def create_time_series_chart(data_df, duid):
       # Revenue panel (top)
       revenue_chart = data_df.hvplot.area(
           x='settlementdate', y='revenue_5min',
           title=f'{duid} - Revenue Over Time',
           color='#ff7f0e', alpha=0.7
       )
       
       # Price panel (middle) 
       price_chart = data_df.hvplot.line(
           x='settlementdate', y='price',
           title=f'{duid} - Price Over Time',
           color='#d62728', line_width=2
       )
       
       # Generation panel (bottom)
       generation_chart = data_df.hvplot.area(
           x='settlementdate', y='scadavalue',
           title=f'{duid} - Generation Over Time', 
           color='#2ca02c', alpha=0.7
       )
       
       # Stack vertically with linked axes
       return (revenue_chart + price_chart + generation_chart).cols(1)
   ```

3. **Linked Interactions**
   - Use HoloViews `streams` for synchronized zooming
   - Panel's `param.watch` for reactive updates
   - Bokeh's `SharedToolbar` for unified controls

#### Phase 4: Time-of-Day Analysis (Days 5-6)
**Objective:** Aggregate and visualize time-of-day patterns

**Data Processing Pipeline:**
```python
def calculate_time_of_day_averages(data_df):
    """Calculate mean values by hour of day across entire period"""
    
    # Extract hour from datetime
    data_df['hour'] = data_df['settlementdate'].dt.hour
    
    # Group by hour and calculate means
    hourly_stats = data_df.groupby('hour').agg({
        'scadavalue': 'mean',           # Average generation by hour
        'revenue_5min': 'mean',         # Average revenue by hour  
        'price': 'mean'                 # Average price by hour
    }).reset_index()
    
    return hourly_stats

def create_time_of_day_chart(hourly_data):
    """Create dual-axis chart showing time of day patterns"""
    
    # Primary axis: Generation and Revenue (similar scales)
    primary = hourly_data.hvplot.bar(
        x='hour', y=['scadavalue', 'revenue_5min'],
        title='Average Performance by Hour of Day',
        ylabel='Generation (MW) / Revenue ($/5min)',
        alpha=0.8, width=600, height=400
    )
    
    # Secondary axis: Price (different scale)
    secondary = hourly_data.hvplot.line(
        x='hour', y='price',
        color='red', line_width=3,
        ylabel='Price ($/MWh)'
    )
    
    # Overlay with dual y-axes
    return primary * secondary
```

#### Phase 5: Summary Statistics (Days 6-7)
**Objective:** Generate comprehensive performance metrics

**Statistics Engine:**
```python
class StationStatsCalculator:
    def __init__(self, station_data, all_stations_data):
        self.station_data = station_data
        self.all_stations_data = all_stations_data
    
    def calculate_performance_metrics(self):
        return {
            'total_generation_gwh': self.station_data['scadavalue'].sum() / 1000,
            'total_revenue_millions': self.station_data['revenue_5min'].sum() / 1_000_000,
            'average_price': self._weighted_average_price(),
            'capacity_factor': self._calculate_capacity_factor(),
            'ranking_generation': self._get_generation_ranking(),
            'peak_generation': self.station_data['scadavalue'].max(),
            'operating_hours': self._calculate_operating_hours(),
            'zero_generation_hours': self._calculate_zero_hours()
        }
    
    def _get_generation_ranking(self):
        # Rank this station against all others in same period
        pass
```

**UI Implementation:**
- Use Panel's `Tabulator` for the summary table
- Apply dark theme styling consistent with other tabs
- Include ranking badges and performance indicators

#### Phase 6: Integration & Polish (Days 7-8)
**Objective:** Final integration and user experience refinement

**Integration Tasks:**
1. **Add to Main Dashboard**
   ```python
   # In gen_dash.py
   from ..station.station_analysis_ui import create_station_analysis_tab
   
   station_tab = create_station_analysis_tab()
   tabs.append(("Station Analysis", station_tab))
   ```

2. **Consistent Styling**
   - Apply material template theme
   - Match color scheme and typography
   - Ensure responsive layout

3. **Performance Optimization**
   - Implement data caching for search results
   - Optimize chart rendering for large datasets
   - Add loading indicators for slow operations

### Required Dependencies

#### Python Packages (add to pyproject.toml)
```python
# Search functionality
fuzzywuzzy = "^0.18.0"
python-levenshtein = "^0.23.0"  # Speed up fuzzy matching

# Enhanced visualization (if not already included)
holoviews = "^1.18.0"
hvplot = "^0.9.0"
bokeh = "^3.3.0"
panel = "^1.3.0"

# NEW: Panel Material-UI (May 2025 release) for professional styling
panel-material-ui = "^1.0.0"  # Modern Material UI components with enhanced dark theme
```

#### Latest HoloViz 2024-2025 Updates Applied
- **Panel Material-UI (May 2025):** New extension providing professional Material UI components
- **Enhanced Dark Theme:** Improved theme inheritance and dynamic switching capabilities  
- **hvPlot 0.11:** DuckDB integration and automatic lat/lon conversion features
- **Panel 1.5.0+:** Latest interactive dashboard capabilities and performance improvements

#### Shared Components to Extract
```python
# Create src/aemo_dashboard/shared/date_controls.py
class DateControlMixin:
    """Reusable date control components"""
    
    def create_date_range_controls(self):
        # Extract from price_analysis_ui.py
        pass
    
    def create_preset_buttons(self):
        # Extract preset button logic
        pass

# Create src/aemo_dashboard/shared/chart_themes.py  
def apply_dashboard_theme():
    """Consistent chart styling across all tabs"""
    hv.opts.defaults(
        hv.opts.Area(alpha=0.7, tools=['hover']),
        hv.opts.Line(line_width=2, tools=['hover']),
        hv.opts.Bars(alpha=0.8, tools=['hover'])
    )
```

### File Modification Plan

#### New Files to Create:
1. `src/aemo_dashboard/station/__init__.py`
2. `src/aemo_dashboard/station/station_analysis.py`
3. `src/aemo_dashboard/station/station_analysis_ui.py`
4. `src/aemo_dashboard/station/station_search.py`
5. `src/aemo_dashboard/shared/date_controls.py`
6. `src/aemo_dashboard/shared/chart_themes.py`

#### Files to Modify:
1. `src/aemo_dashboard/generation/gen_dash.py` - Add new tab
2. `pyproject.toml` - Add search dependencies
3. `src/aemo_dashboard/analysis/price_analysis_ui.py` - Extract shared components

### Development Best Practices

#### Code Organization
- **Separation of Concerns:** UI components separate from data processing
- **Reusable Components:** Extract common functionality to shared modules  
- **Consistent APIs:** Follow existing patterns for data loading and chart creation

#### Testing Strategy
- **Unit Tests:** Test search functionality and statistics calculations
- **Integration Tests:** Verify tab integration and data flow
- **Manual Testing:** Verify charts render correctly and interactions work

#### Documentation
- **Code Comments:** Document complex calculations and data transformations
- **User Guide:** Add station analysis instructions to dashboard help
- **Developer Notes:** Update CLAUDE.md with implementation details

This implementation plan provides a structured approach to building the Station Analysis tab while maximizing reuse of existing components and maintaining consistency with the current dashboard architecture.

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
- Three main tabs: Generation by Fuel | Average Price Analysis | Station Analysis

### Troubleshooting
- If port 5010 is in use: `lsof -ti:5010 | xargs kill -9`
- Check logs: `tail -f /Users/davidleitch/Library/Mobile\ Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/aemo-energy-dashboard/logs/aemo_dashboard.log`

## Recent Achievements ✅

### All Major Issues Resolved
- ✅ **Column Selector Bug Fixed:** All checkboxes now display as checked by default
- ✅ **Capacity Data Integrity:** Fixed >400% utilization issue using SUMMED AEMO capacities
- ✅ **Production Deployment:** Removed hardcoded paths, all imports use relative references
- ✅ **File Path Configuration:** Dashboard now uses config system for cross-platform compatibility
- ✅ **Price Analysis Functionality:** Fully working custom pivot table builder with hierarchical display
- ✅ **Professional UI Design:** Dark theme, proper contrast, intuitive user experience

## Recent Dashboard Restructuring ✅ COMPLETED

### Major Design Changes:
- **Dashboard Title:** Changed to "Nem Analysis" 
- **Footer Attribution:** Changed to "data:AEMO, design ITK"
- **Generation Tab Restructure:** 
  - Moved region selector from main dashboard into Generation by Fuel tab
  - Layout now matches Station Analysis pattern: controls on left, charts on right
  - Capacity Utilization moved from separate main tab to subtab within Generation by Fuel
- **Tab Structure:** Reduced from 4 main tabs to 3 main tabs with internal subtabs

### Current Status: Fully Operational with New Structure
The dashboard foundation is solid and all core functionality is working perfectly. 

## ✅ **Phase 1 Complete: Station Analysis Tab - Basic Infrastructure**

### **Implementation Status: OPERATIONAL**

The Station Analysis tab has been successfully added to the dashboard with core infrastructure:

#### ✅ **Completed Components:**

**1. Module Structure Created**
- ✅ `src/aemo_dashboard/station/__init__.py` - Module initialization
- ✅ `src/aemo_dashboard/station/station_analysis.py` - Data processing engine
- ✅ `src/aemo_dashboard/station/station_analysis_ui.py` - UI components
- ✅ `src/aemo_dashboard/station/station_search.py` - Fuzzy search functionality

**2. Data Integration Engine**
- ✅ **StationAnalysisMotor class** - Loads and integrates generation + price + DUID mapping data
- ✅ **Data pipeline** - Properly handles DataFrame format of gen_info.pkl 
- ✅ **Region mapping** - Links generation data to regions for price integration
- ✅ **Revenue calculation** - Computes 5-minute revenue (Generation × Price × time)

**3. Search Functionality**
- ✅ **StationSearchEngine class** - Fuzzy search using fuzzywuzzy
- ✅ **DataFrame compatibility** - Handles both DataFrame and dictionary DUID mappings
- ✅ **Auto-suggestions** - Popular stations list for quick access
- ✅ **Multi-field search** - Searches DUID, station name, and owner fields

**4. User Interface Components**
- ✅ **Search interface** - Text input with search button
- ✅ **Date controls** - Start/end date pickers with preset buttons (Last 7/30 Days, All Data)
- ✅ **Status display** - Shows data loading status and statistics (528 stations, 5 regions)
- ✅ **Popular stations** - Quick access to major generators (Eraring, Loy Yang A, etc.)

**5. Dashboard Integration**
- ✅ **Fourth tab added** - "Station Analysis" appears alongside existing tabs
- ✅ **Dependencies installed** - fuzzywuzzy and python-levenshtein for search
- ✅ **Error handling** - Graceful failure with meaningful error messages
- ✅ **Consistent styling** - Matches existing dark theme and layout

#### **Current Functionality:**
- ✅ Tab loads successfully in dashboard
- ✅ Status shows "Data loaded successfully | 528 stations available"
- ✅ Search interface appears with popular stations list
- ✅ Date controls functional with preset buttons
- ✅ Ready for user to search stations and begin analysis

#### **Files Modified:**
- `src/aemo_dashboard/generation/gen_dash.py` - Added Station Analysis tab import and integration
- `pyproject.toml` - Added fuzzywuzzy and python-levenshtein dependencies

## ⚠️ **Current Status: Phase 2 - Station Analysis Search Issues**

### **Problem Summary: Search Event Handling**

The Station Analysis tab loads successfully with 2.7M integrated records, but the search functionality has event handling issues:

#### **Issues Identified:**

**1. Original Button Click Problem**
- Panel button `on_click` events not firing properly in complex layouts
- `search_button.on_click(self._perform_search)` was not triggering
- Common issue with Panel reactive systems in nested components

**2. Dropdown Selection Error**
```
Error handling station selection: String parameter 'StationAnalysisUI.selected_duid' only takes a string value, not value of <class 'tuple'>.
```
- Station selector dropdown passing tuple `(duid, display_name)` instead of just `duid` 
- Parameter validation error preventing station selection

**3. Chart Display Not Updating**
- Search mechanism partially working (improved with reactive approach)
- Charts section not updating after successful station filtering
- UI component references not properly connected

#### **Progress Made:**
✅ **Data Integration Working:** 2.7M records successfully loaded and integrated  
✅ **Search Infrastructure:** StationSearchEngine finds stations correctly  
✅ **UI Components:** Search interface, date controls, and layout functional  
🔄 **Event Handling:** Partially fixed with reactive programming approach  
❌ **Chart Display:** Still not showing after station selection  

#### **Technical Root Causes:**

**Data Pipeline:** ✅ Working  
- `StationAnalysisMotor.load_data()` ✅ 3.1M generation records  
- `StationAnalysisMotor.integrate_data()` ✅ 2.7M integrated records  
- `StationSearchEngine.fuzzy_search()` ✅ Finds stations correctly  

**UI Event System:** 🔄 Partially Fixed  
- Button click events → **Fixed:** Replaced with reactive Select widget  
- Parameter validation → **Issue:** Dropdown passing tuple instead of string  
- Reactive updates → **Issue:** Chart components not updating properly  

**Chart Generation:** ❌ Not Working  
- `_update_station_analysis()` called but charts not displaying  
- `_create_time_series_charts()` not showing visual output  
- Panel layout updates not refreshing properly  

#### **Next Steps Required:**

**Immediate Fixes Needed:**
1. **Fix Dropdown Value Error:**
   ```python
   # Change from:
   station_options = [('', 'Select a station...')] + [(station['duid'], station['display_name']) for station in popular_stations]
   
   # To:
   station_options = ['Select a station...'] + [station['duid'] for station in popular_stations]
   ```

2. **Fix Chart Component Updates:**
   - Debug why `self.charts_section[0] = new_content` not updating UI
   - May need to use Panel's `.replace()` or `.clear()` + `.append()` methods
   - Ensure chart objects are properly created and Panel-compatible

3. **Add Better Logging:**
   - Log each step of `_update_station_analysis()` process
   - Verify station data filtering returns records
   - Confirm chart creation succeeds before UI update

#### **Current Dashboard Status:**
- ✅ Main dashboard running on http://localhost:5010
- ✅ All four tabs: Generation by Fuel | Capacity Utilization | Average Price Analysis | Station Analysis
- ✅ Station Analysis tab loads with "✅ Data loaded successfully | 528 stations available"
- ✅ Search dropdown shows popular stations
- ⚠️ Station selection triggers parameter error
- ❌ Charts not displaying after station selection

## ✅ **Phase 2 Complete: Station Analysis Charts Working**

### **Major Progress Made:**
✅ **Dropdown Selection Fixed:** Station selection now works without parameter errors  
✅ **Chart Display Working:** Charts now appear after station selection  
✅ **Smart Resampling:** 23.5 days of data → 541 hourly points (6,426 5-min records)  
✅ **Performance Metrics Fixed:** All metrics calculate successfully  
✅ **Chart Repetition Eliminated:** Single clean chart display  

### **Current Issues Requiring Fixes:**

#### **1. Dual-Axis Chart Display Problem**
**Issue:** Time series chart shows only one y-axis (Generation MW) but needs both
**Expected:** Left y-axis: Generation (MW), Right y-axis: Price ($/MWh)
**Current:** HoloViews overlay not creating proper dual-axis display
**Fix Needed:** Properly configure dual y-axis with `.opts(yaxis='right')` for price series

#### **2. Time-of-Day Chart Inconsistency**  
**Issue:** Time-of-day chart should mirror time series chart with dual-axis
**Current:** Only shows generation bars + price line, but missing dual y-axis labels
**Expected:** Same two series (Generation + Price) with same dual y-axis configuration
**Fix Needed:** Apply same dual-axis pattern to time-of-day chart

#### **3. Date Selection Controls Not Functional**
**Issue:** Date pickers and preset buttons don't trigger data refresh
**Current:** Always shows full 30-day default period regardless of selection
**Expected:** Clicking "Last 7 Days" should reload analysis for past week only
**Fix Needed:** Connect date controls to reactive parameters and trigger `_update_station_analysis()`

#### **4. Preset Button Visual Feedback Missing**
**Issue:** Preset buttons (Last 7 Days, Last 30 Days, All Data) don't show selection state  
**Expected:** Selected button should have different color/style to indicate active choice
**Fix Needed:** Button group with selection state management

### **Technical Root Causes:**

**Dual-Axis Implementation:**
Current HoloViews overlay pattern not working properly:
```python
overlay = generation_line * price_line.opts(yaxis='right')
```
**Solution:** Use proper Bokeh dual-axis configuration or Panel/HoloViews layout approach

**Date Control Binding:**
Date picker widgets created but not connected to reactive parameters:
```python
start_picker = pn.widgets.DatePicker(value=start_date)  # Not connected
end_picker = pn.widgets.DatePicker(value=end_date)      # Not connected  
```
**Solution:** Connect with `param.watch()` and trigger analysis updates

**Button State Management:**
Buttons created without selection state tracking:
```python
pn.widgets.Button(name="Last 7 Days")  # No state management
```
**Solution:** Use `RadioButtonGroup` or implement custom button state logic

### **Next Phase: UI Control Integration**

**Priority Tasks:**
1. Fix dual-axis chart display (HoloViews configuration)
2. Implement working date range controls with reactive updates
3. Add preset button selection state and functionality  
4. Apply same dual-axis pattern to time-of-day chart
5. Test complete user workflow: station selection → date change → chart updates

**Current Status:** Charts display but controls need integration