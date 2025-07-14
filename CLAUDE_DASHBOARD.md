# AEMO Energy Dashboard Documentation

## Overview

The AEMO Energy Dashboard is a web-based visualization platform for Australian electricity market data. It provides real-time and historical analysis of generation, prices, and transmission flows across the National Electricity Market (NEM).

## Dashboard Architecture

### Technology Stack
- **Framework**: Panel with HoloViews/hvPlot for interactive visualizations
- **Template**: Material design theme
- **Data Source**: Parquet files maintained by the AEMO Data Updater
- **Update Model**: Read-only access to parquet files (no downloads)

### Main Components

#### Generation by Fuel Tab
- **Purpose**: Shows electricity generation by fuel type in stacked area charts
- **Features**:
  - Region selector (NEM, NSW1, QLD1, SA1, TAS1, VIC1)
  - Time range selector (24 hours, 7 days, 30 days, All Data, Custom)
  - Subtabs: Generation Stack, Capacity Utilization
  - Integrated transmission flows as virtual "fuel" type
  - Rooftop solar displayed as separate band
- **Data**: 5-minute resolution from AEMO SCADA

#### Average Price Analysis Tab
- **Purpose**: Analyze prices and revenue by region and fuel type
- **Features**:
  - User-driven grouping (Region, Fuel combinations)
  - Multi-select filters for regions and fuels
  - Column selection (Gen GWh, Rev $M, Price $/MWh, etc.)
  - Hierarchical table with expandable fuel groups
  - Date range controls
- **Visualization**: Interactive Tabulator table

#### Station Analysis Tab
- **Purpose**: Detailed analysis of individual power stations or units
- **Features**:
  - Station vs DUID toggle
  - Fuzzy search with popular stations dropdown
  - Dual-axis charts (Generation MW + Price $/MWh)
  - Time series and time-of-day analysis
  - Performance metrics (revenue, capacity factor, etc.)
- **Smart Features**: Automatic DUID grouping for multi-unit stations

## Running the Dashboard

### Start Dashboard
```bash
cd /Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/aemo-energy-dashboard
source .venv/bin/activate
python -m src.aemo_dashboard.generation.gen_dash
```

### Access Dashboard
- URL: http://localhost:5010
- Title: "Nem Analysis"
- Footer: "Last Updated: [time] | data:AEMO, design ITK"

### Access Updater Status UI
- URL: http://localhost:5011
- Title: "AEMO Data Updater Status"
- Shows: Update status for all collectors (Generation, Price, Transmission, Rooftop)

### Stop Dashboard
```bash
# Find process
lsof -ti:5010

# Kill process
lsof -ti:5010 | xargs kill -9
```

## Configuration

### Environment Variables (.env)
```bash
# Data file locations (read-only access)
GEN_OUTPUT_FILE=/path/to/gen_output.parquet
SPOT_HIST_FILE=/path/to/spot_hist.parquet
TRANSMISSION_OUTPUT_FILE=/path/to/transmission_flows.parquet
ROOFTOP_SOLAR_FILE=/path/to/rooftop_solar.parquet

# Email alerts (dashboard-specific notifications)
ALERT_EMAIL=your-email@icloud.com
ALERT_PASSWORD=your-app-specific-password
RECIPIENT_EMAIL=recipient@example.com

# Dashboard settings
DEFAULT_REGION=NEM
UPDATE_INTERVAL_MINUTES=5
```

## Dashboard Features

### Time Range Selection
- **Quick Select Buttons**: Last 24 Hours, Last 7 Days, Last 30 Days, All Data
- **Custom Date Pickers**: For precise date range selection
- **Smart Display**: Context-aware x-axis labels (hours for day view, dates for week view)
- **Performance**: All data stays at 5-minute resolution (no resampling)

### Regional Analysis
- **NEM View**: Combined data for entire National Electricity Market
- **State Views**: Individual analysis for NSW, QLD, SA, TAS, VIC
- **Transmission Integration**: Shows interconnector flows as imports/exports

### Data Integration
- **Generation + Prices**: Automatic joining for revenue calculations
- **Capacity Factors**: Real-time utilization percentages
- **Station Grouping**: Smart DUID pattern matching (e.g., ER01-04 → Eraring)

## UI Components

### Color Scheme
```python
fuel_colors = {
    'Solar': '#FFD700',           # Gold
    'Rooftop Solar': '#FFF59D',   # Light yellow
    'Wind': '#87CEEB',            # Sky blue
    'Water': '#4682B4',           # Steel blue
    'Battery Storage': '#9370DB',  # Medium purple
    'Coal': '#8B4513',            # Saddle brown
    'Gas other': '#FF7F50',       # Coral
    'OCGT': '#FF6347',            # Tomato
    'CCGT': '#FF4500',            # Orange red
    'Biomass': '#228B22',         # Forest green
    'Other': '#A9A9A9',           # Dark gray
    'Transmission Flow': '#FFB6C1' # Light pink
}
```

### Chart Types
- **Stacked Area**: Generation by fuel type
- **Line Charts**: Capacity utilization, transmission flows
- **Dual-Axis**: Combined generation and price analysis
- **Tables**: Tabulator with hierarchical grouping

## Performance Optimization

### Data Loading
- **Caching**: 5-minute TTL for loaded data
- **Lazy Loading**: Only loads data when tab is viewed
- **Efficient Queries**: Filters data before visualization

### Chart Rendering
- **Smart Decimation**: Reduces points for large date ranges
- **Responsive Design**: Adjusts to browser window size
- **Interactive Tools**: Zoom, pan, hover tooltips

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
lsof -ti:5010 | xargs kill -9
```

#### Missing Data
- Check parquet file paths in .env
- Verify updater service is running
- Run data integrity check

#### Slow Performance
- Check data file sizes
- Reduce time range selection
- Clear browser cache

### Log Files
```bash
# View dashboard logs
tail -f logs/aemo_dashboard.log

# Check for errors
grep ERROR logs/aemo_dashboard.log
```

## Development Notes

### Code Organization
```
src/aemo_dashboard/
├── generation/
│   └── gen_dash.py          # Main dashboard file
├── analysis/
│   └── price_analysis_ui.py # Price analysis tab
├── station/
│   └── station_analysis_ui.py # Station analysis tab
├── shared/
│   ├── config.py            # Configuration
│   ├── logging_config.py    # Logging setup
│   └── email_alerts.py      # Alert system
└── diagnostics/
    └── data_validity_check.py # Data integrity checks
```

### Adding New Features

1. **New Tab**: Create UI module in appropriate directory
2. **Import in gen_dash.py**: Add to tab creation
3. **Data Access**: Use read-only parquet operations
4. **Styling**: Follow Material theme guidelines

### Testing
```bash
# Run dashboard locally
python -m src.aemo_dashboard.generation.gen_dash

# Check with playwright
playwright test dashboard_functionality.spec.js
```

## Future Enhancements

### Planned Features
1. **WebSocket Updates**: Real-time data refresh
2. **Export Functionality**: Download charts/data
3. **Comparison Mode**: Side-by-side analysis
4. **Forecasting**: Integration with pre-dispatch data
5. **Mobile Responsive**: Tablet/phone optimization

### Dashboard Extensions
1. **Transmission Tab**: Dedicated interconnector analysis
2. **Summary Dashboard**: Key metrics overview
3. **Alert Configuration**: User-defined thresholds
4. **Historical Comparison**: Year-over-year analysis
5. **Market Events**: Highlight price spikes/constraints

## Design System & Best Practices

### Material Design Implementation

Following the [HoloViz Panel Material UI announcement](https://blog.holoviz.org/posts/panel_material_ui_announcement/), we are implementing the new Material theme consistently across all dashboard components.

#### Key Material Theme Features
- **Comprehensive Component Set**: Over 70 Material UI-based components
- **Global Theme Configuration**: Using `theme_config` for consistent styling
- **Accessibility Support**: Built-in accessibility features for all components
- **API Compatibility**: Fully compatible with existing Panel code

#### Theme Configuration
```python
# Global theme configuration
pn.extension('tabulator', template='material')
pn.config.theme = 'dark'

# Component-level theming
Card(
    content,
    theme_config={
        "palette": {"primary": {"main": "#1976d2"}},
        "typography": {"fontFamily": "Roboto"},
        "shape": {"borderRadius": 8}
    }
)
```

### Dashboard Design Principles (2025)

#### 1. Cognitive Load Minimization
- **Progressive Disclosure**: Start with overview, allow drill-down to details
- **5-Second Rule**: Essential information visible within 5 seconds
- **Clean Interface**: Minimize visual noise and focus on actionable metrics

#### 2. Visual Hierarchy & Information Architecture
- **Sequential Ordering**: Follow natural reading patterns (Z or F pattern)
- **Data Prioritization**: Essential metrics first, supporting data secondary
- **Consistent Visual Language**: Uniform colors, fonts, and chart types

#### 3. Accessibility & Internationalization
- **Screen Reader Support**: Proper ARIA labels and table headers
- **Color Accessibility**: High contrast ratios and color-blind friendly palettes
- **Global Support**: Multi-language and cultural considerations
- **Interactive Elements**: Touch-friendly for mobile, precise for desktop

#### 4. Performance Optimization
- **Real-time Capabilities**: Seamless updates for live data
- **Data Efficiency**: Batch API calls, implement caching strategies
- **Progressive Loading**: Load critical data first, defer secondary content
- **Client-side Operations**: Filter and sort locally when possible

#### 5. Interactive Design Patterns
- **User Control**: Empower users with filtering and customization
- **Cross-Dashboard Integration**: Seamless navigation between views
- **Contextual Actions**: Right-click menus, hover tooltips
- **Responsive Feedback**: Clear loading states and error handling

### Material Design Data Visualization Guidelines

#### Color System
```python
# Recommended color palette for energy data
fuel_colors = {
    'Solar': '#FFD700',           # Material Yellow 500
    'Rooftop Solar': '#FFF59D',   # Material Yellow 200
    'Wind': '#2196F3',            # Material Blue 500
    'Water': '#0D47A1',           # Material Blue 900
    'Battery Storage': '#9C27B0',  # Material Purple 500
    'Coal': '#5D4037',            # Material Brown 700
    'Gas other': '#FF5722',       # Material Deep Orange 500
    'OCGT': '#FF9800',            # Material Orange 500
    'CCGT': '#F57C00',            # Material Orange 700
    'Biomass': '#4CAF50',         # Material Green 500
    'Other': '#757575',           # Material Grey 600
    'Transmission Flow': '#E91E63' # Material Pink 500
}
```

#### Typography Scale
- **Headlines**: Roboto Medium, 24px (H1), 20px (H2), 16px (H3)
- **Body Text**: Roboto Regular, 14px
- **Captions**: Roboto Regular, 12px
- **Labels**: Roboto Medium, 12px

#### Layout & Spacing
- **Grid System**: 8dp base grid for consistent spacing
- **Card Elevation**: Use Material elevation system (1-8dp)
- **Margins**: 16dp for sections, 8dp for related elements
- **Responsive Breakpoints**: Mobile (<600px), Tablet (600-960px), Desktop (>960px)

### Component-Specific Guidelines

#### Chart Design
- **Consistent Axis Labels**: Always include units and proper scaling
- **Tooltip Information**: Show precise values and context
- **Animation**: Smooth transitions for data updates (200-300ms)
- **Interaction**: Pan, zoom, and selection capabilities

#### Table Design
- **Header Styling**: Material surface color with elevated appearance
- **Row Alternation**: Subtle background color differences
- **Sorting Indicators**: Clear visual feedback for active sorts
- **Pagination**: Material pagination component for large datasets

#### Navigation
- **Tab System**: Material tabs with clear active states
- **Breadcrumbs**: Show current location in complex hierarchies
- **Side Navigation**: Collapsible drawer for secondary actions

### Accessibility Requirements

#### Visual Accessibility
- **Contrast Ratios**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Color Independence**: Information conveyed through more than color alone
- **Focus Indicators**: Clear keyboard navigation paths
- **Scalable Text**: Support for 200% zoom without horizontal scrolling

#### Interaction Accessibility
- **Keyboard Navigation**: All functions accessible via keyboard
- **Screen Reader Support**: Proper semantic markup and ARIA labels
- **Touch Targets**: Minimum 44px touch targets for mobile
- **Error Messages**: Clear, actionable error descriptions

### Performance Targets

#### Loading Performance
- **Initial Load**: <3 seconds for basic dashboard view
- **Data Updates**: <500ms for filtered views
- **Chart Rendering**: <1 second for complex visualizations
- **Memory Usage**: Monitor for memory leaks in long-running sessions

#### Data Handling
- **Client-side Caching**: 5-15 minute TTL for data files
- **Lazy Loading**: Load charts only when tabs are viewed
- **Virtual Scrolling**: For tables with >1000 rows
- **Data Aggregation**: Pre-compute common aggregations

### Implementation Checklist

#### Material Theme Setup
- [ ] Configure global Material theme with dark mode support
- [ ] Implement consistent color palette across all components
- [ ] Apply Material typography scale to all text elements
- [ ] Use Material elevation system for card hierarchies

#### Accessibility Compliance
- [ ] Add ARIA labels to all interactive elements
- [ ] Ensure keyboard navigation works throughout interface
- [ ] Test with screen readers (NVDA, JAWS)
- [ ] Validate color contrast ratios meet WCAG 2.1 AA standards

#### Performance Optimization
- [ ] Implement lazy loading for non-critical components
- [ ] Add data caching with appropriate TTL values
- [ ] Monitor and optimize chart rendering performance
- [ ] Test on mobile devices for responsive behavior

#### User Experience
- [ ] Progressive disclosure from overview to details
- [ ] Clear loading states and error messages
- [ ] Consistent interaction patterns across all tabs
- [ ] User preference persistence (dark/light mode, column selections)

### Reference Implementation

For detailed implementation examples, see:
- **HoloViz Panel Material UI Blog**: https://blog.holoviz.org/posts/panel_material_ui_announcement/
- **Material Design 3 Guidelines**: https://m3.material.io/
- **Panel Material Theme Documentation**: Latest Panel documentation for Material theme configuration