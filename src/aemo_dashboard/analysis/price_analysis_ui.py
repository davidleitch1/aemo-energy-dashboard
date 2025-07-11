"""
Price Analysis UI Components - User interface for flexible price analysis

This module provides Panel components for the Average Price Analysis tab,
including hierarchy selection and tabulator display.
"""

import pandas as pd
import panel as pn
from typing import Dict, List, Optional
import param
from datetime import datetime, timedelta

from .price_analysis import PriceAnalysisMotor
from ..shared.logging_config import get_logger

logger = get_logger(__name__)

class PriceAnalysisUI(param.Parameterized):
    """UI component for price analysis with flexible aggregation"""
    
    # Parameters for reactive UI
    selected_hierarchy = param.String(default="Fuel → Region → DUID")
    refresh_data = param.Boolean(default=False)
    start_date = param.Date(default=None)
    end_date = param.Date(default=None)
    
    def __init__(self):
        super().__init__()
        self.motor = PriceAnalysisMotor()
        self.data_loaded = False
        self.current_data = pd.DataFrame()
        
        # Initialize the motor
        self._initialize_motor()
        
        # Create UI components
        self.hierarchy_selector = None
        self.tabulator_table = None
        self.tabulator_container = None  # Container for dynamic tabulator updates
        self.detail_table = None  # Table for DUID details
        self.detail_container = None  # Container for detail table
        self.status_text = None
        self.start_date_picker = None
        self.end_date_picker = None
        self.date_preset_buttons = None
        self.apply_date_button = None
        self.create_ui_components()
        
        logger.info("Price Analysis UI initialized")
    
    def _initialize_motor(self):
        """Initialize the calculation motor with data"""
        try:
            logger.info("Loading data into calculation motor...")
            if self.motor.load_data():
                if self.motor.standardize_columns():
                    if self.motor.integrate_data():
                        self.data_loaded = True
                        logger.info("Data successfully loaded and integrated")
                    else:
                        logger.error("Failed to integrate data")
                else:
                    logger.error("Failed to standardize columns")
            else:
                logger.error("Failed to load data")
        except Exception as e:
            logger.error(f"Error initializing motor: {e}")
            self.data_loaded = False
    
    def create_ui_components(self):
        """Create the UI components"""
        
        # Status indicator
        if self.data_loaded:
            status_msg = "✅ Data loaded successfully"
            overlap_start = self.motor.integrated_data['settlementdate'].min()
            overlap_end = self.motor.integrated_data['settlementdate'].max()
            overlap_days = (overlap_end - overlap_start).days
            status_msg += f" | Data period: {overlap_start.strftime('%Y-%m-%d')} to {overlap_end.strftime('%Y-%m-%d')} ({overlap_days} days)"
            status_msg += f" | Records: {len(self.motor.integrated_data):,}"
        else:
            status_msg = "❌ Failed to load data"
        
        self.status_text = pn.pane.Markdown(f"**Status:** {status_msg}")
        
        # Hierarchy selector
        if self.data_loaded:
            available_hierarchies = self.motor.get_available_hierarchies()
            self.hierarchy_selector = pn.widgets.Select(
                name="Aggregation Hierarchy",
                value=list(available_hierarchies.keys())[0],
                options=list(available_hierarchies.keys()),
                width=300
            )
            self.selected_hierarchy = self.hierarchy_selector.value
            
            # Watch for changes
            self.hierarchy_selector.param.watch(self._on_hierarchy_change, 'value')
            
            # Date range controls
            self._create_date_controls()
            
            # Refresh button
            self.refresh_button = pn.widgets.Button(
                name="Refresh Analysis",
                button_type="primary",
                width=150
            )
            self.refresh_button.on_click(self._on_refresh_click)
            
            # Calculate initial data
            self._calculate_and_update_table()
            
        else:
            self.hierarchy_selector = pn.pane.Markdown("**Data loading failed - hierarchy selection unavailable**")
            self.tabulator_table = pn.pane.Markdown("**Cannot display table without data**")
            self.tabulator_container = pn.Column(self.tabulator_table, sizing_mode='stretch_width')
            self.detail_container = pn.Column(sizing_mode='stretch_width')
    
    def _create_date_controls(self):
        """Create date range selection controls"""
        try:
            # Get available date range
            available_start, available_end = self.motor.get_available_date_range()
            
            if available_start and available_end:
                start_dt = datetime.strptime(available_start, '%Y-%m-%d').date()
                end_dt = datetime.strptime(available_end, '%Y-%m-%d').date()
                
                # Date pickers
                self.start_date_picker = pn.widgets.DatePicker(
                    name="Start Date",
                    value=start_dt,
                    start=start_dt,
                    end=end_dt,
                    width=150
                )
                
                self.end_date_picker = pn.widgets.DatePicker(
                    name="End Date", 
                    value=end_dt,
                    start=start_dt,
                    end=end_dt,
                    width=150
                )
                
                # Quick preset buttons
                self.preset_7d_button = pn.widgets.Button(
                    name="Last 7 Days",
                    button_type="light",
                    width=100
                )
                self.preset_7d_button.on_click(lambda event: self._apply_date_preset(7))
                
                self.preset_30d_button = pn.widgets.Button(
                    name="Last 30 Days", 
                    button_type="light",
                    width=100
                )
                self.preset_30d_button.on_click(lambda event: self._apply_date_preset(30))
                
                self.preset_all_button = pn.widgets.Button(
                    name="All Data",
                    button_type="light", 
                    width=100
                )
                self.preset_all_button.on_click(lambda event: self._apply_date_preset(None))
                
                # Apply button
                self.apply_date_button = pn.widgets.Button(
                    name="Apply Date Filter",
                    button_type="primary",
                    width=150
                )
                self.apply_date_button.on_click(self._on_apply_date_filter)
                
                logger.info(f"Date controls created for range: {available_start} to {available_end}")
                
            else:
                logger.warning("No date range available - creating disabled controls")
                self.start_date_picker = pn.pane.Markdown("**Date selection unavailable**")
                self.end_date_picker = pn.pane.Markdown("")
                self.apply_date_button = pn.pane.Markdown("")
                
        except Exception as e:
            logger.error(f"Error creating date controls: {e}")
            self.start_date_picker = pn.pane.Markdown("**Date controls error**")
            self.end_date_picker = pn.pane.Markdown("")
            self.apply_date_button = pn.pane.Markdown("")
    
    def _apply_date_preset(self, days: Optional[int]):
        """Apply a date preset (7 days, 30 days, or all data)"""
        try:
            available_start, available_end = self.motor.get_available_date_range()
            if not available_start or not available_end:
                return
                
            end_dt = datetime.strptime(available_end, '%Y-%m-%d').date()
            
            if days is None:
                # All data
                start_dt = datetime.strptime(available_start, '%Y-%m-%d').date()
            else:
                # Last N days
                start_dt = end_dt - timedelta(days=days-1)
                # Don't go before the earliest available date
                earliest_dt = datetime.strptime(available_start, '%Y-%m-%d').date()
                start_dt = max(start_dt, earliest_dt)
            
            # Update the date pickers
            self.start_date_picker.value = start_dt
            self.end_date_picker.value = end_dt
            
            logger.info(f"Applied date preset: {days} days -> {start_dt} to {end_dt}")
            
        except Exception as e:
            logger.error(f"Error applying date preset: {e}")
    
    def _on_apply_date_filter(self, event):
        """Handle apply date filter button click"""
        try:
            start_date_str = self.start_date_picker.value.strftime('%Y-%m-%d') if self.start_date_picker.value else None
            end_date_str = self.end_date_picker.value.strftime('%Y-%m-%d') if self.end_date_picker.value else None
            
            logger.info(f"Applying date filter: {start_date_str} to {end_date_str}")
            
            # Reload data with date filter
            if self.motor.load_data():
                if self.motor.standardize_columns():
                    if self.motor.integrate_data(start_date_str, end_date_str):
                        self.data_loaded = True
                        
                        # Force complete rebuild of the table with new filtered data
                        self._calculate_and_update_table()
                        
                        # Update status
                        if len(self.motor.integrated_data) > 0:
                            filtered_start = self.motor.integrated_data['settlementdate'].min()
                            filtered_end = self.motor.integrated_data['settlementdate'].max()
                            filtered_days = (filtered_end - filtered_start).days
                            status_msg = f"✅ Date filter applied | Period: {filtered_start.strftime('%Y-%m-%d')} to {filtered_end.strftime('%Y-%m-%d')} ({filtered_days} days)"
                            status_msg += f" | Records: {len(self.motor.integrated_data):,}"
                        else:
                            status_msg = "⚠️ No data found for selected date range"
                        
                        self.status_text.object = f"**Status:** {status_msg}"
                        logger.info("Date filter applied successfully")
                    else:
                        logger.error("Failed to integrate data with date filter")
                else:
                    logger.error("Failed to standardize columns for date filtering")
            else:
                logger.error("Failed to reload data for date filtering")
                
        except Exception as e:
            logger.error(f"Error applying date filter: {e}")
    
    def _on_hierarchy_change(self, event):
        """Handle hierarchy selection change"""
        self.selected_hierarchy = event.new
        logger.info(f"Hierarchy changed to: {self.selected_hierarchy}")
        self._calculate_and_update_table()
    
    def _on_refresh_click(self, event):
        """Handle refresh button click"""
        logger.info("Refreshing analysis data...")
        self._initialize_motor()
        if self.data_loaded:
            self._calculate_and_update_table()
            # Update status
            overlap_start = self.motor.integrated_data['settlementdate'].min()
            overlap_end = self.motor.integrated_data['settlementdate'].max()
            overlap_days = (overlap_end - overlap_start).days
            status_msg = f"✅ Data refreshed successfully | Data period: {overlap_start.strftime('%Y-%m-%d')} to {overlap_end.strftime('%Y-%m-%d')} ({overlap_days} days)"
            status_msg += f" | Records: {len(self.motor.integrated_data):,}"
            self.status_text.object = f"**Status:** {status_msg}"
    
    def _calculate_and_update_table(self):
        """Calculate aggregated data and update the table"""
        if not self.data_loaded:
            return
        
        try:
            logger.info(f"Calculating aggregations for hierarchy: {self.selected_hierarchy}")
            
            # Get hierarchy columns
            available_hierarchies = self.motor.get_available_hierarchies()
            hierarchy_columns = available_hierarchies[self.selected_hierarchy]
            
            # Calculate aggregated data
            aggregated_data = self.motor.calculate_aggregated_prices(hierarchy_columns)
            
            # Sort the data according to the hierarchy order for proper display
            if not aggregated_data.empty and hierarchy_columns:
                # Sort by all hierarchy columns to ensure proper ordering
                try:
                    aggregated_data = aggregated_data.sort_values(hierarchy_columns)
                    logger.info(f"Data sorted by hierarchy: {hierarchy_columns}")
                except Exception as e:
                    logger.warning(f"Could not sort by all hierarchy columns: {e}")
                    # Fallback to sorting by available columns
                    available_sort_cols = [col for col in hierarchy_columns if col in aggregated_data.columns]
                    if available_sort_cols:
                        aggregated_data = aggregated_data.sort_values(available_sort_cols)
            
            if aggregated_data.empty:
                self.tabulator_table = pn.pane.Markdown("**No data available for selected hierarchy**")
                if self.tabulator_container is None:
                    self.tabulator_container = pn.Column(self.tabulator_table, sizing_mode='stretch_width')
                else:
                    self.tabulator_container.clear()
                    self.tabulator_container.append(self.tabulator_table)
                return
            
            # Create tabulator table with proper grouping (aggregated data without DUID)
            if len(hierarchy_columns) > 1:
                # Multi-level grouping: Use Panel's groupby with aggregated data
                self.tabulator_table = pn.widgets.Tabulator(
                    value=aggregated_data,  # Use the aggregated DataFrame
                    groupby=hierarchy_columns,  # Panel handles the multi-level grouping
                    pagination=None,  # Disable pagination for scrolling
                    sizing_mode='stretch_width',
                    height=600,
                    show_index=False,
                    sortable=True,
                    selectable=1,
                    configuration={
                        'groupStartOpen': False,  # Start with groups collapsed
                        'groupToggleElement': 'header',  # Make entire header clickable to toggle
                        'virtualDomBuffer': 300  # Enable virtual scrolling for performance
                    }
                )
            else:
                # Simple table without grouping
                self.tabulator_table = pn.widgets.Tabulator(
                    value=aggregated_data,
                    pagination=None,  # Disable pagination for scrolling
                    sizing_mode='stretch_width',
                    height=600,
                    show_index=False,
                    sortable=True,
                    selectable=1,
                    configuration={
                        'virtualDomBuffer': 300,  # Enable virtual scrolling for performance
                        'initialSort': [  # Set initial sort order based on hierarchy
                            {'column': col, 'dir': 'asc'} for col in hierarchy_columns
                        ] if hierarchy_columns else []
                    }
                )
            
            # Create detail table showing individual DUIDs
            detail_data = self.motor.calculate_duid_details(hierarchy_columns)
            if not detail_data.empty and len(hierarchy_columns) > 1:
                self.detail_table = pn.widgets.Tabulator(
                    value=detail_data,
                    pagination=None,
                    sizing_mode='stretch_width',
                    height=400,
                    show_index=False,
                    sortable=True,
                    selectable=1,
                    configuration={
                        'virtualDomBuffer': 300
                    }
                )
                
                # Create or update detail container
                if self.detail_container is None:
                    self.detail_container = pn.Column(
                        "### Individual DUID Details",
                        self.detail_table,
                        sizing_mode='stretch_width'
                    )
                else:
                    self.detail_container.clear()
                    self.detail_container.extend([
                        "### Individual DUID Details",
                        self.detail_table
                    ])
            else:
                if self.detail_container is None:
                    self.detail_container = pn.Column(sizing_mode='stretch_width')
                else:
                    self.detail_container.clear()
            
            # Create or update the tabulator container
            if self.tabulator_container is None:
                self.tabulator_container = pn.Column(self.tabulator_table, sizing_mode='stretch_width')
            else:
                # Update the container with the new tabulator
                self.tabulator_container.clear()
                self.tabulator_container.append(self.tabulator_table)
            
            logger.info(f"Table updated with {len(aggregated_data)} aggregated rows and {len(detail_data)} DUID details")
            
        except Exception as e:
            logger.error(f"Error calculating aggregations: {e}")
            error_msg = pn.pane.Markdown(f"**Error calculating data:** {e}")
            self.tabulator_table = error_msg
            if self.tabulator_container is None:
                self.tabulator_container = pn.Column(error_msg, sizing_mode='stretch_width')
            else:
                self.tabulator_container.clear()
                self.tabulator_container.append(error_msg)
    
    def _get_tabulator_columns(self, hierarchy_columns: List[str]) -> Dict:
        """Configure tabulator columns based on hierarchy"""
        
        # Base columns for hierarchy - ensure consistent ordering and visibility
        columns = {}
        
        # Always show hierarchy columns in a logical order regardless of selected hierarchy
        hierarchy_order = ['Region', 'Fuel', 'duid']  # Logical display order
        
        for i, col in enumerate(hierarchy_columns):
            # Determine if this is the primary grouping column (first in hierarchy)
            is_primary = (i == 0)
            
            if col == 'duid':
                columns[col] = {
                    'title': 'DUID', 
                    'width': 120, 
                    'frozen': is_primary,
                    'headerSort': True
                }
            elif col == 'Region':
                columns[col] = {
                    'title': 'Region', 
                    'width': 80, 
                    'frozen': is_primary,
                    'headerSort': True
                }
            elif col == 'Fuel':
                columns[col] = {
                    'title': 'Fuel Type', 
                    'width': 100, 
                    'frozen': is_primary,
                    'headerSort': True
                }
            else:
                columns[col] = {
                    'title': col.title(), 
                    'width': 100, 
                    'frozen': is_primary,
                    'headerSort': True
                }
        
        # Performance columns
        columns.update({
            'generation_mwh': {
                'title': 'Generation (MWh)', 
                'width': 130,
                'formatter': 'money',
                'formatterParams': {'precision': 1, 'symbol': '', 'symbolAfter': ' MWh'}
            },
            'total_revenue_dollars': {
                'title': 'Total Revenue ($)', 
                'width': 140,
                'formatter': 'money',
                'formatterParams': {'precision': 0, 'symbol': '$', 'thousand': ','}
            },
            'average_price_per_mwh': {
                'title': 'Avg Price ($/MWh)', 
                'width': 140,
                'formatter': 'money',
                'formatterParams': {'precision': 2, 'symbol': '$', 'symbolAfter': '/MWh'}
            },
            'capacity_mw': {
                'title': 'Capacity (MW)', 
                'width': 120,
                'formatter': 'money',
                'formatterParams': {'precision': 0, 'symbol': '', 'symbolAfter': ' MW'}
            },
            'capacity_utilization_pct': {
                'title': 'Capacity Utilization (%)', 
                'width': 150,
                'formatter': 'money',
                'formatterParams': {'precision': 1, 'symbol': '', 'symbolAfter': '%'}
            },
            'record_count': {
                'title': 'Data Points', 
                'width': 100,
                'formatter': 'money',
                'formatterParams': {'precision': 0, 'thousand': ','}
            },
            'start_date': {
                'title': 'Start Date', 
                'width': 100,
                'formatter': 'datetime',
                'formatterParams': {'outputFormat': 'YYYY-MM-DD'}
            },
            'end_date': {
                'title': 'End Date', 
                'width': 100,
                'formatter': 'datetime',
                'formatterParams': {'outputFormat': 'YYYY-MM-DD'}
            }
        })
        
        return columns
    
    def create_layout(self) -> pn.layout.Tabs:
        """Create the complete UI layout"""
        
        if not self.data_loaded:
            return pn.Column(
                "# Average Price Analysis",
                self.status_text,
                pn.pane.Markdown("**❌ Cannot load price analysis - please check data files**"),
                sizing_mode='stretch_width'
            )
        
        # Create date range panel
        if hasattr(self, 'start_date_picker') and hasattr(self.start_date_picker, 'value'):
            date_presets_row = pn.Row(
                self.preset_7d_button,
                self.preset_30d_button, 
                self.preset_all_button,
                sizing_mode='stretch_width'
            )
            
            date_range_panel = pn.Column(
                "### Date Range",
                pn.Row(
                    self.start_date_picker,
                    self.end_date_picker,
                    sizing_mode='stretch_width'
                ),
                pn.pane.Markdown("**Quick Presets:**"),
                date_presets_row,
                self.apply_date_button,
                width=350
            )
        else:
            date_range_panel = pn.pane.Markdown("**Date range controls unavailable**")
        
        # Create aggregation panel  
        aggregation_panel = pn.Column(
            "### Aggregation",
            self.hierarchy_selector,
            self.refresh_button,
            width=350
        )
        
        # Create info panel
        info_panel = pn.pane.Markdown("""
        **About Average Price Analysis:**
        
        This analysis calculates weighted average electricity prices by aggregating:
        - **Revenue**: Generation (MW) × Price ($/MWh) × 5-minute intervals
        - **Average Price**: Total Revenue ÷ Total Generation (MWh)
        - **Capacity Factor**: Generation ÷ (Capacity × Hours) × 100%
        
        Choose different aggregation hierarchies to explore the data from different perspectives.
        """, width=400)
        
        # Main content
        main_content = pn.Column(
            "# Average Price Analysis",
            self.status_text,
            pn.Spacer(height=10),
            pn.Row(
                pn.Column(
                    "## Controls",
                    date_range_panel,
                    pn.Spacer(height=15),
                    aggregation_panel,
                    pn.Spacer(height=15),
                    info_panel,
                    width=450
                ),
                pn.Column(
                    "## Aggregated Results",
                    self.tabulator_container,
                    pn.Spacer(height=20),
                    self.detail_container,
                    sizing_mode='stretch_width'
                ),
                sizing_mode='stretch_width'
            ),
            sizing_mode='stretch_width'
        )
        
        return main_content

# Factory function for easy integration
def create_price_analysis_tab() -> pn.layout.Column:
    """Create a price analysis tab for integration into the dashboard"""
    ui = PriceAnalysisUI()
    return ui.create_layout()