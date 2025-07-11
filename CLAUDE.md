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