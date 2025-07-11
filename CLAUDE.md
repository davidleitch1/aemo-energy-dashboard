# AEMO Energy Dashboard - Development Notes

## Current Status

The dashboard has three main tabs:
1. **Generation by Fuel** - Working well, shows stacked area chart
2. **Capacity Utilization** - Working, separate tab as requested
3. **Average Price Analysis** - Partially working but needs custom pivot table builder

## Next Priority: Custom Pivot Table Builder for Price Analysis

### Problem with Current Approach
The fixed hierarchy approach (`Fuel → Region → DUID`) doesn't work well because:
- Every DUID is unique, so grouping by `['Fuel', 'Region', 'duid']` creates individual groups
- Panel's `groupby` parameter and Tabulator.js `groupBy` both fail to create meaningful hierarchies
- Users want flexibility to analyze data from different perspectives

### Solution: User-Driven Pivot Table Builder

Replace the rigid "Aggregation Hierarchy" dropdown with flexible controls:

#### Grouping Controls
```
┌─ Grouping (select up to 3 levels) ──────────────┐
│ Group by (in order):                            │
│ ☑ Fuel        ☐ Region   ☐ Technology          │
│                                                 │
│ Then by:                                        │
│ ☐ Fuel        ☑ Region   ☐ Technology          │
│                                                 │
│ Then by:                                        │
│ ☐ Fuel        ☐ Region   ☐ Technology          │
└─────────────────────────────────────────────────┘
```

#### Column Selection
```
┌─ Display Columns ───────────────────────────────┐
│ Show in table:                                  │
│ ☑ Generation (MWh)                              │
│ ☑ Total Revenue ($)                             │
│ ☑ Average Price ($/MWh)                         │
│ ☐ Capacity (MW)                                 │
│ ☐ Capacity Utilization (%)                     │
└─────────────────────────────────────────────────┘
```

### Implementation Notes

#### Available Grouping Dimensions
- **Fuel** - Primary energy source (Coal, Gas, Solar, Wind, etc.)
- **Region** - Market region (NSW1, QLD1, SA1, TAS1, VIC1)
- **Technology** - Technology type (if available in DUID mapping)

**Note:** Owner should be a **display column**, not a grouping dimension, since users can sort on it using Tabulator's built-in sorting.

#### Excluded Columns
- **Record Count** - Not needed for user analysis
- **Date Range** - Not needed for user analysis (date filtering is handled separately)

#### Technical Implementation
1. **UI Components:**
   - Checkbox groups for grouping selection (max 3 levels)
   - Checkbox group for column selection
   - Apply button to rebuild table

2. **Data Processing:**
   - Dynamically build grouping hierarchy based on user selection
   - Aggregate data at the selected level
   - Only include selected columns in output
   - Use Panel's `groupby` parameter with user-defined hierarchy

3. **Benefits:**
   - Solves grouping issues (users define meaningful groupings)
   - Flexible analysis (view data by Fuel, Region, or combination)
   - Clean interface (only show relevant columns)
   - Scalable (easy to add new dimensions/columns)

### Files to Modify
- `src/aemo_dashboard/analysis/price_analysis_ui.py` - Replace hierarchy selector with checkbox controls
- `src/aemo_dashboard/analysis/price_analysis.py` - Add dynamic grouping method

### Example Use Cases
1. **Fuel Analysis:** Group by Fuel only → See total generation/revenue by fuel type
2. **Regional Analysis:** Group by Region only → See performance by market region  
3. **Detailed Analysis:** Group by Fuel → Region → See fuel performance within each region
4. **Technology Focus:** Group by Technology → Fuel → Compare technologies within fuel types

This approach transforms the Price Analysis tab from a rigid hierarchy viewer into a powerful, user-driven analytics tool.

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
- Navigate to "Average Price Analysis" tab to see custom pivot table builder

### Troubleshooting
- If port 5010 is in use: `lsof -ti:5010 | xargs kill -9`
- Check logs: `tail -f /Users/davidleitch/Library/Mobile\ Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/aemo-energy-dashboard/logs/aemo_dashboard.log`

## Custom Pivot Table Builder Implementation (COMPLETED)

### Final Status: ✅ Major Implementation Complete

The Price Analysis tab has been successfully transformed from a rigid hierarchy system into a flexible, user-driven pivot table builder. This implementation addresses the fundamental issue that every DUID creates its own group, making traditional grouping ineffective.

#### ✅ Completed Features

**1. Redesigned User Interface**
- **Category Selection:** Users select which dimensions to group by (Region, Fuel)
- **Region Filters:** Checkboxes to select which regions to include (NSW1, QLD1, SA1, TAS1, VIC1)  
- **Fuel Filters:** Checkboxes to select which fuel types to include (Coal, Gas, Solar, Wind, etc.)
- **Column Selection:** Choose which data columns to display with shorter titles
- **Apply Button:** Triggers recalculation with new selections

**2. Hierarchical DUID Display**
- ✅ Individual DUIDs are now properly nested under their parent groups
- ✅ Users can click on group headers (e.g., "Coal") to expand and see individual DUIDs
- ✅ Groups start collapsed by default for clean initial view
- ✅ Removed separate detail table - everything is in one hierarchical table

**3. Data Filtering System**
- ✅ Actual data filtering implemented (not just UI filtering)
- ✅ Region filters correctly limit data to selected regions only
- ✅ Fuel filters correctly limit data to selected fuel types only
- ✅ Filtered data maintains proper aggregations and calculations

**4. Formatting Improvements**
- ✅ Generation displayed in GWh (converted from MWh ÷ 1000)
- ✅ Revenue displayed in $millions (converted from dollars ÷ 1,000,000)
- ✅ Smart decimal rounding: 0 decimal places if >10, otherwise 1 decimal place
- ✅ Shorter column titles: "Generation (GWh)", "Revenue ($M)", "Avg Price ($/MWh)"
- ✅ Removed unnecessary `_row_type` column

**5. Technical Architecture**
- ✅ Flexible grouping system supports any combination of available dimensions
- ✅ Column mapping system handles UI names vs database column names  
- ✅ Proper data integration with filtering applied before aggregation
- ✅ Hierarchical data structure compatible with Panel's Tabulator groupby functionality

#### ⚠️ Known Issues Requiring Future Work

**1. Column Selection Logic**
- **Issue:** Column selection partially works but may not hide all unselected columns consistently
- **Impact:** Users see more columns than they selected
- **Priority:** Medium - functional but not polished

**2. Date Range Integration**
- **Issue:** Date filtering works but could be better integrated with the grouping controls
- **Impact:** Users need to apply date filters separately from grouping changes
- **Priority:** Low - workaround available

**3. Additional Formatting**
- **Issue:** Some edge cases in number formatting may need refinement
- **Impact:** Minor display inconsistencies in very large or very small numbers
- **Priority:** Low - cosmetic

#### Technical Implementation Details

**Key Files Modified:**
- `src/aemo_dashboard/analysis/price_analysis_ui.py` - Complete UI redesign
- `src/aemo_dashboard/analysis/price_analysis.py` - Added filtering and formatting logic

**Major Changes:**
1. **UI Redesign:** Replaced 3-level hierarchy selectors with category + filter approach
2. **Data Filtering:** Added region_filters and fuel_filters parameters throughout data pipeline  
3. **Hierarchical Display:** Modified `create_hierarchical_data()` to include DUID-level details in main table
4. **Formatting Pipeline:** Added transformation logic for GWh, $millions, and smart rounding
5. **Column Mapping:** Implemented mapping between UI column names and database column names

**User Workflow:**
1. Select grouping categories (e.g., "Fuel" + "Region")
2. Choose which regions/fuels to include via filter checkboxes
3. Select which data columns to display  
4. Click "Apply Grouping" to rebuild table
5. Expand/collapse groups to see individual DUIDs

#### Example Use Cases Now Supported
- **Fuel Analysis:** Group by Fuel only, filter to specific regions → See fuel performance by region
- **Regional Focus:** Group by Region, filter to Coal only → See coal performance across regions
- **Multi-level:** Group by Fuel+Region, filter to NSW1+VIC1 → Detailed breakdown of two key markets
- **Custom Filtering:** Any combination of region/fuel filters with any grouping structure

This implementation successfully transforms the Price Analysis tab from a rigid, problematic hierarchy system into a powerful, flexible analytics tool that gives users full control over how they view and analyze the electricity market data.

## Next Development Phase: Enhanced User Experience

### Recently Completed ✅

#### 1. Complete UI Overhaul ✅ COMPLETED
**Major Achievement:** Successfully transformed the Price Analysis interface from a problematic rigid system into a comprehensive, user-friendly analytics dashboard.

**✅ Core Functionality Fixed:**
- **Column Selection Logic:** All 6 columns now work perfectly (Generation GWh, Revenue $M, Avg Price, Capacity Utilization %, Station Name, Owner)
- **Capacity Utilization:** Fixed missing column mapping (`'capacity_utilization': 'capacity_utilization_pct'`) - now displays correctly
- **Station Name & Owner:** Added DUID mapping to readable station names and company ownership data
- **Unified Update Button:** Replaced fragmented Apply buttons with single "Update Analysis" that handles all filters

**🎨 Professional UI Design:**
- **Dark Theme Integration:** Table styled with white text on black background matching dashboard theme
- **Column Headers:** Highlighted background (#404040) with proper contrast
- **Visual Date Feedback:** Active date preset buttons change color (primary vs light)
- **Dynamic Table Titles:** Shows "Last 7 Days", "Last 30 Days", "All Data", or "Custom Range" with date info
- **Increased Table Height:** From 600px to 800px for better data viewing

**🔄 Horizontal Layout Implementation:**
- **Side-by-Side Sections:** Region | Fuel | Columns arranged horizontally
- **Compact Design:** Shorter names ("Gen (GWh)", "Rev ($M)", "Price ($/MWh)", "Util (%)")
- **Checkbox Uncheck All:** Replaced buttons with checkboxes underneath each category header
- **Proper Vertical Lists:** Each section displays items vertically within its column

**🎛️ Enhanced User Experience:**
- **Smart Default Selection:** All regions, fuels, and default columns pre-selected
- **Quick Clear Options:** "Uncheck All" checkboxes for instant category clearing
- **Organized Controls:** Date range and actions in top row, filters below
- **Improved Spacing:** Better visual separation between sections

### Current Refinements Needed

#### 1. Layout Optimization 🎯 IN PROGRESS
**Current Status:** Horizontal layout working well but needs final polish
**Next Steps:**
- Make selection columns more compact/tighter spacing
- Move table back to right side of selectors (not below)
- Position table title on same row as status line
- Optimize space usage for professional dashboard appearance

#### 6. Visual Date Filter Feedback 🎨 LOW PRIORITY
**Requirement:** Date preset buttons (Last 7 Days, Last 30 Days, All Data) should change color when selected.
**Current Behavior:** Buttons don't show which date range is currently active.
**Expected Behavior:** Active date range button should be highlighted/different color.
**Benefit:** Clear visual feedback of current date filter state.
**Implementation:** Add button state management with active/inactive styling.

### Implementation Priority Order
1. **Fix Column Selection Logic** - Core functionality broken
2. **Add Capacity Utilization Column** - Important missing metric
3. **Unified Update Button** - Better UX flow
4. **Add Station Name Column** - User-friendly display
5. **Add Owner Column** - Additional analysis dimension  
6. **Date Filter Visual Feedback** - Polish/visual enhancement

### Technical Notes
- Column selection fix likely involves Tabulator `hidden_columns` parameter or DataFrame filtering
- New columns require updates to both UI options and data pipeline
- Unified button needs to combine date and grouping filter logic
- Station Name/Owner columns need proper mapping from DUID to gen_info.pkl data