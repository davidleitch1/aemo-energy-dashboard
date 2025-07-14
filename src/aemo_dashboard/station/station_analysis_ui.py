"""
Station Analysis UI Components - User interface for individual station analysis.

This module provides Panel components for the Station Analysis tab, including
search interface, time series charts, time-of-day analysis, and summary statistics.
"""

import pandas as pd
import panel as pn
import param
import holoviews as hv
import hvplot.pandas
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .station_analysis import StationAnalysisMotor
from .station_search import StationSearchEngine
from ..shared.logging_config import get_logger

logger = get_logger(__name__)

class StationAnalysisUI(param.Parameterized):
    """UI component for station analysis"""
    
    # Parameters for reactive UI
    selected_duid = param.String(default='', doc="Currently selected DUID")
    selected_station_duids = param.List(default=[], doc="List of DUIDs for station mode")
    search_query = param.String(default='', doc="Current search query")
    start_date = param.Date(default=None, doc="Analysis start date")
    end_date = param.Date(default=None, doc="Analysis end date")
    analysis_mode = param.String(default='duid', doc="Analysis mode: 'duid' or 'station'")
    
    def __init__(self):
        super().__init__()
        self.motor = StationAnalysisMotor()
        self.search_engine = None
        self.data_loaded = False
        
        # UI components
        self.search_input = None
        self.search_results = None
        self.status_text = None
        self.date_controls = None
        self.time_series_chart = None
        self.time_of_day_chart = None
        self.summary_table = None
        
        # Initialize the motor and search engine
        self._initialize_components()
        
        # Set up reactive parameter watching
        self.param.watch(self._on_search_change, 'search_query')
        
        logger.info("Station Analysis UI initialized")
    
    def _initialize_components(self):
        """Initialize the analysis motor and search engine"""
        try:
            logger.info("Loading data into station analysis motor...")
            if self.motor.load_data():
                if self.motor.standardize_columns():
                    if self.motor.integrate_data():
                        self.data_loaded = True
                        # Initialize search engine with loaded DUID mapping
                        self.search_engine = StationSearchEngine(self.motor.duid_mapping)
                        logger.info("Station analysis components initialized successfully")
                    else:
                        logger.error("Failed to integrate data")
                else:
                    logger.error("Failed to standardize columns")
            else:
                logger.error("Failed to load data")
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            self.data_loaded = False
    
    def create_ui_components(self):
        """Create the main UI components"""
        
        # Status indicator
        if self.data_loaded:
            stats = self.search_engine.search_stats()
            status_msg = f"✅ Data loaded successfully | {stats['total_stations']} stations available"
            status_msg += f" | {len(stats['fuel_types'])} fuel types | {len(stats['regions'])} regions"
        else:
            status_msg = "❌ Failed to load data"
        
        self.status_text = pn.pane.Markdown(f"**Status:** {status_msg}")
        
        if not self.data_loaded:
            return pn.Column("## Station Analysis", self.status_text, 
                           pn.pane.Markdown("⚠️ Data loading failed. Please check logs and restart."))
        
        # Create individual UI sections
        search_section = self._create_search_section()
        date_section = self._create_date_controls()
        self.charts_section = self._create_charts_section()
        
        # Create title with white text
        title = pn.pane.HTML(
            "<h1 style='color: white; margin: 10px 0 5px 0; text-align: center;'>Station Analysis</h1>",
            sizing_mode='stretch_width'
        )
        
        # Layout the components (no footer needed on this tab)
        main_layout = pn.Column(
            title,
            self.status_text,
            pn.Row(
                pn.Column(search_section, date_section, width=300),
                self.charts_section,
                sizing_mode='stretch_width'
            ),
            sizing_mode='stretch_width'
        )
        
        return main_layout
    
    def _create_search_section(self):
        """Create the station search interface"""
        try:
            # Mode toggle - Station vs DUID analysis
            self.mode_toggle = pn.widgets.RadioButtonGroup(
                name="Analysis Mode:",
                options=["Individual Units (DUID)", "Whole Stations"],
                value="Individual Units (DUID)",
                button_type="primary",
                button_style="outline",
                width=280
            )
            self.mode_toggle.param.watch(self._on_mode_change, 'value')
            
            # Get popular stations for initial suggestions (DUID mode by default)
            popular_stations = self.search_engine.get_popular_stations(limit=50, mode=self.analysis_mode)
            station_options = ['Select a station...'] + [f"{station['display_name']}" for station in popular_stations]
            self.station_duids = [''] + [station.get('duid', station.get('duids', [''])[0]) for station in popular_stations]  # Keep DUID mapping
            
            # Station selector dropdown - this will automatically trigger search
            self.station_selector = pn.widgets.Select(
                name="Select Station:",
                options=station_options,
                value='Select a station...',
                width=280
            )
            
            # Bind station selection to reactive parameter
            self.station_selector.param.watch(self._on_station_select, 'value')
            
            # Search input for manual search
            self.search_input = pn.widgets.TextInput(
                name="Or Search by Name/DUID:",
                placeholder="Type station name or DUID...",
                width=280
            )
            
            # Bind search input to reactive parameter  
            self.search_input.param.watch(self._on_search_input, 'value')
            
            # Popular stations info
            popular_section = pn.pane.Markdown("""
            **Quick Access:**
            Use the dropdown above to select from popular stations, or type in the search box for fuzzy matching.
            
            **Major Stations Available:**
            - Eraring, Loy Yang A, Bayswater
            - Hazelwood, Yallourn, Torrens Island
            """)
            
            search_section = pn.Column(
                "### Station Search",
                self.mode_toggle,
                "#### Select Station/Unit:",
                self.station_selector,
                self.search_input,
                popular_section,
                width=300
            )
            
            return search_section
            
        except Exception as e:
            logger.error(f"Error creating search section: {e}")
            return pn.pane.Markdown("⚠️ Error creating search interface")
    
    def _create_date_controls(self):
        """Create reactive date range controls"""
        try:
            # Default to last 30 days
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            self.start_date = start_date
            self.end_date = end_date
            
            # Create reactive date pickers connected to class parameters
            self.start_picker = pn.widgets.DatePicker(
                name="Start Date:",
                value=start_date,
                width=140
            )
            
            self.end_picker = pn.widgets.DatePicker(
                name="End Date:",
                value=end_date,
                width=140
            )
            
            # Connect date pickers to reactive updates
            self.start_picker.param.watch(self._on_start_date_change, 'value')
            self.end_picker.param.watch(self._on_end_date_change, 'value')
            
            # Create preset button group with selection state
            self.preset_buttons = pn.widgets.RadioButtonGroup(
                name="Quick Select:",
                options=["Last 7 Days", "Last 30 Days", "All Data"],
                value="Last 30 Days",  # Default selection
                button_type="primary",
                button_style="outline",  # Only selected button will be filled
                width=280
            )
            
            # Connect preset buttons to reactive updates  
            self.preset_buttons.param.watch(self._on_preset_change, 'value')
            
            date_section = pn.Column(
                "### Time Period",
                self.start_picker,
                self.end_picker,
                self.preset_buttons,
                width=300
            )
            
            return date_section
            
        except Exception as e:
            logger.error(f"Error creating date controls: {e}")
            return pn.pane.Markdown("⚠️ Error creating date controls")
    
    def _create_charts_section(self):
        """Create the charts and analysis section"""
        try:
            # Placeholder content until a station is selected
            placeholder = pn.pane.Markdown("""
            ### Select a Station to Begin Analysis
            
            Use the search box on the left to find a station by name or DUID.
            
            **Available Analysis:**
            - 📈 Time series performance (Revenue, Price, Generation)
            - 🕐 Time-of-day patterns 
            - 📊 Performance statistics and rankings
            """)
            
            charts_section = pn.Column(
                placeholder,
                sizing_mode='stretch_width',
                min_height=600
            )
            
            return charts_section
            
        except Exception as e:
            logger.error(f"Error creating charts section: {e}")
            return pn.pane.Markdown("⚠️ Error creating charts section")
    
    def _on_station_select(self, event):
        """Handle station selection from dropdown"""
        try:
            selected_display = event.new
            if selected_display and selected_display != 'Select a station...':
                # Find the corresponding DUID(s) from the selection index
                selected_index = self.station_selector.options.index(selected_display)
                selection_data = self.station_duids[selected_index]
                
                if self.analysis_mode == 'station' and isinstance(selection_data, list):
                    # Station mode: selection_data is a list of DUIDs
                    self.selected_station_duids = selection_data
                    self.selected_duid = ''  # Clear single DUID
                    logger.info(f"Station selected: {selected_display} -> {len(selection_data)} units: {selection_data}")
                elif isinstance(selection_data, str) and selection_data:
                    # DUID mode: selection_data is a single DUID
                    self.selected_duid = selection_data
                    self.selected_station_duids = []  # Clear station DUIDs
                    logger.info(f"DUID selected: {selected_display} -> {selection_data}")
                else:
                    logger.warning(f"Invalid selection data: {selection_data}")
                    return
                
                self._update_station_analysis()
        except Exception as e:
            logger.error(f"Error handling station selection: {e}")
    
    def _on_search_input(self, event):
        """Handle manual search input"""
        try:
            query = event.new
            if query and len(query.strip()) >= 2:
                # Trigger search after short delay (debounce)
                self.search_query = query.strip()
        except Exception as e:
            logger.error(f"Error handling search input: {e}")
    
    def _on_search_change(self, event):
        """Handle search query parameter change (reactive)"""
        try:
            query = event.new
            if not query or len(query.strip()) < 2:
                return
            
            # Search for matching stations
            results = self.search_engine.fuzzy_search(query, limit=5)
            
            if results:
                # Use the best match
                best_match = results[0]
                self.selected_duid = best_match['duid']
                logger.info(f"Search result: {best_match['display_name']} ({self.selected_duid}) [score: {best_match['score']}]")
                
                # Update the analysis for this station
                self._update_station_analysis()
                
            else:
                logger.warning(f"No stations found for query: {query}")
                self._show_search_feedback(f"No stations found for '{query}'. Try searching for DUID or station name.")
                
        except Exception as e:
            logger.error(f"Error performing search: {e}")
    
    def _on_start_date_change(self, event):
        """Handle start date picker change"""
        try:
            new_start_date = event.new
            if new_start_date:
                self.start_date = new_start_date
                logger.info(f"Start date changed to: {new_start_date}")
                
                # Update analysis if we have a selected station or DUID
                if self.selected_duid or self.selected_station_duids:
                    self._update_station_analysis()
                    
        except Exception as e:
            logger.error(f"Error handling start date change: {e}")
    
    def _on_end_date_change(self, event):
        """Handle end date picker change"""
        try:
            new_end_date = event.new
            if new_end_date:
                self.end_date = new_end_date
                logger.info(f"End date changed to: {new_end_date}")
                
                # Update analysis if we have a selected station or DUID
                if self.selected_duid or self.selected_station_duids:
                    self._update_station_analysis()
                    
        except Exception as e:
            logger.error(f"Error handling end date change: {e}")
    
    def _on_preset_change(self, event):
        """Handle preset button group change"""
        try:
            preset = event.new
            logger.info(f"Preset selected: {preset}")
            
            # Calculate new date range based on preset
            end_date = datetime.now().date()
            
            if preset == "Last 7 Days":
                start_date = end_date - timedelta(days=7)
            elif preset == "Last 30 Days":
                start_date = end_date - timedelta(days=30)
            elif preset == "All Data":
                # Use earliest available data (approximate)
                start_date = datetime(2024, 1, 1).date()
            else:
                return
            
            # Update date pickers and class parameters
            self.start_date = start_date
            self.end_date = end_date
            
            # Update UI date pickers to reflect the change
            self.start_picker.value = start_date
            self.end_picker.value = end_date
            
            logger.info(f"Date range updated to: {start_date} to {end_date}")
            
            # Update analysis if we have a selected station or DUID
            if self.selected_duid or self.selected_station_duids:
                self._update_station_analysis()
                
        except Exception as e:
            logger.error(f"Error handling preset change: {e}")
    
    def _on_mode_change(self, event):
        """Handle analysis mode change (Station vs DUID)"""
        try:
            mode_display = event.new
            if mode_display == "Individual Units (DUID)":
                self.analysis_mode = 'duid'
            else:
                self.analysis_mode = 'station'
            
            logger.info(f"Analysis mode changed to: {self.analysis_mode}")
            
            # Update the station selector options based on new mode
            self._refresh_station_options()
            
        except Exception as e:
            logger.error(f"Error handling mode change: {e}")
    
    def _refresh_station_options(self):
        """Refresh station selector options based on current analysis mode"""
        try:
            # Get popular stations for the current mode
            popular_stations = self.search_engine.get_popular_stations(limit=50, mode=self.analysis_mode)
            
            if self.analysis_mode == 'station':
                station_options = ['Select a station...'] + [f"{station['display_name']}" for station in popular_stations]
                self.station_duids = [''] + [station.get('duids', []) for station in popular_stations]  # Keep DUID list mapping
            else:
                station_options = ['Select a station...'] + [f"{station['display_name']}" for station in popular_stations]
                self.station_duids = [''] + [station['duid'] for station in popular_stations]  # Keep single DUID mapping
            
            # Update the selector
            if hasattr(self, 'station_selector') and self.station_selector:
                self.station_selector.options = station_options
                self.station_selector.value = 'Select a station...'
            
            logger.info(f"Refreshed station options for {self.analysis_mode} mode: {len(station_options)-1} options")
            
        except Exception as e:
            logger.error(f"Error refreshing station options: {e}")
    
    def _show_search_feedback(self, message: str):
        """Show search feedback to user"""
        try:
            if hasattr(self, 'charts_section') and self.charts_section:
                feedback = pn.pane.Markdown(f"""
                ### Search Results
                
                {message}
                
                **Try searching for:**
                - Station name (e.g., "Eraring", "Loy Yang")
                - DUID (e.g., "ERARING", "LOYA1")
                - Partial matches work too!
                """)
                self.charts_section[0] = feedback
        except Exception as e:
            logger.error(f"Error showing search feedback: {e}")
    
    def _update_station_analysis(self):
        """Update analysis charts and tables for the selected station"""
        try:
            # Determine what to analyze based on mode
            if self.analysis_mode == 'station' and self.selected_station_duids:
                filter_target = self.selected_station_duids
                display_name = f"Station with {len(self.selected_station_duids)} units"
            elif self.selected_duid:
                filter_target = self.selected_duid
                display_name = self.selected_duid
            else:
                logger.warning("No station or DUID selected for analysis")
                return
            
            logger.info(f"Starting analysis for {display_name} in {self.analysis_mode} mode")
            
            # Filter data for the selected station/DUID(s)
            start_dt = datetime.combine(self.start_date, datetime.min.time()) if self.start_date else None
            end_dt = datetime.combine(self.end_date, datetime.max.time()) if self.end_date else None
            
            logger.info(f"Filtering data from {start_dt} to {end_dt}")
            
            if self.motor.filter_station_data(filter_target, start_dt, end_dt):
                
                logger.info(f"Successfully filtered {len(self.motor.station_data)} records for {self.selected_duid}")
                
                # Calculate metrics
                logger.info("Calculating performance metrics...")
                metrics = self.motor.calculate_performance_metrics()
                logger.info(f"Calculated metrics: {list(metrics.keys()) if metrics else 'None'}")
                
                # Calculate time-of-day averages
                logger.info("Calculating time-of-day averages...")
                time_of_day = self.motor.calculate_time_of_day_averages()
                logger.info(f"Time-of-day data shape: {time_of_day.shape if not time_of_day.empty else 'Empty'}")
                
                # Create components
                logger.info("Creating time series charts...")
                time_series_charts = self._create_time_series_charts()
                
                logger.info("Creating time-of-day chart...")
                time_of_day_chart = self._create_time_of_day_chart(time_of_day)
                
                logger.info("Creating summary statistics...")
                summary_stats = self._create_summary_statistics(metrics)
                
                # Update the charts section using proper Panel pattern
                if hasattr(self, 'charts_section') and self.charts_section:
                    # Get appropriate display name based on mode
                    if self.analysis_mode == 'station' and self.selected_station_duids:
                        # For station mode, use the first DUID to get station name
                        station_info = self.search_engine.get_station_info(self.selected_station_duids[0])
                        station_name = station_info.get('station_name', 'Unknown Station')
                        display_title = f"{station_name} (Station: {len(self.selected_station_duids)} units)"
                    else:
                        # For DUID mode
                        station_info = self.search_engine.get_station_info(self.selected_duid)
                        station_name = station_info.get('station_name', self.selected_duid)
                        display_title = f"{station_name} ({self.selected_duid})"
                    
                    logger.info(f"Updating charts section for {display_title}")
                    
                    # Create subtabs for different chart types
                    chart_subtabs = pn.Tabs(
                        ("Time Series", pn.Column(
                            "#### Generation & Price Over Time",
                            time_series_charts,
                            "#### Performance Statistics",
                            summary_stats,
                            sizing_mode='stretch_width'
                        )),
                        ("Time-of-Day", pn.Column(
                            "#### Average Performance by Hour",
                            time_of_day_chart,
                            sizing_mode='stretch_width'
                        )),
                        dynamic=True,
                        sizing_mode='stretch_width'
                    )
                    
                    new_content = pn.Column(
                        f"## {display_title}",
                        chart_subtabs,
                        sizing_mode='stretch_width'
                    )
                    
                    # Replace content using Panel's direct assignment pattern
                    # First check current length to debug repetition
                    logger.info(f"Charts section current length: {len(self.charts_section)}")
                    
                    # Clear all existing content and add new content
                    self.charts_section[:] = [new_content]
                    logger.info(f"Charts section updated - new length: {len(self.charts_section)}")
                
            else:
                logger.warning(f"No data available for {self.selected_duid} in the specified time period")
                self._show_search_feedback(f"No data available for {self.selected_duid} in the selected time period.")
                
        except Exception as e:
            logger.error(f"Error updating station analysis: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _create_time_series_charts(self):
        """Create dual-axis time series chart with smart resampling"""
        try:
            if self.motor.station_data is None or len(self.motor.station_data) == 0:
                return pn.pane.Markdown("No data available for time series analysis.")
            
            data = self.motor.station_data.copy()
            
            # Ensure settlementdate is properly formatted
            if data['settlementdate'].dtype != 'datetime64[ns]':
                data['settlementdate'] = pd.to_datetime(data['settlementdate'])
            
            # Set settlementdate as index for resampling
            data = data.set_index('settlementdate').sort_index()
            
            # Determine if we need resampling based on time period
            time_span = data.index.max() - data.index.min()
            time_span_days = time_span.total_seconds() / (24 * 3600)
            
            logger.info(f"Time span: {time_span_days:.1f} days")
            
            if time_span_days > 2:
                # Resample to hourly for longer periods
                logger.info("Resampling to hourly data for time series chart")
                chart_data = data.resample('1h').agg({
                    'price': 'mean',           # Average price per hour
                    'scadavalue': 'mean'       # Average generation per hour
                }).dropna()
                freq_label = "Hourly"
            else:
                # Use 5-minute data for short periods
                logger.info("Using 5-minute data for time series chart")
                chart_data = data[['price', 'scadavalue']].dropna()
                freq_label = "5-minute"
            
            if len(chart_data) == 0:
                return pn.pane.Markdown("No valid data for time series chart.")
            
            # Reset index to have settlementdate as a column for hvplot
            chart_data = chart_data.reset_index()
            
            logger.info(f"Chart data shape: {chart_data.shape}")
            logger.info(f"Chart data columns: {list(chart_data.columns)}")
            
            # Use Bokeh directly for proper dual-axis control
            from bokeh.plotting import figure
            from bokeh.models import LinearAxis, Range1d
            
            # Extract data
            timestamps = chart_data['settlementdate'].values
            generation = chart_data['scadavalue'].values
            prices = chart_data['price'].values
            
            # Get appropriate title based on mode
            if self.analysis_mode == 'station' and self.selected_station_duids:
                title = f'Station ({len(self.selected_station_duids)} units) - Generation & Price Over Time ({freq_label} Data)'
            else:
                title = f'{self.selected_duid} - Generation & Price Over Time ({freq_label} Data)'
            
            # Create figure with primary y-axis for generation
            p = figure(
                title=title,
                x_axis_type='datetime',
                width=900,
                height=400,
                tools='pan,wheel_zoom,box_zoom,reset,save,hover'
            )
            
            # Remove grid
            p.grid.visible = False
            
            # Primary axis (left) - Generation
            p.line(timestamps, generation, line_width=3, color='#2ca02c', legend_label='Generation (MW)')
            
            # Add capacity reference line if capacity data is available
            if hasattr(self.motor, 'station_data') and 'capacity_mw' in self.motor.station_data.columns:
                capacity_mw = self.motor.station_data['capacity_mw'].iloc[0]
                if capacity_mw > 0:
                    # Add horizontal dashed line for maximum capacity
                    p.line([timestamps[0], timestamps[-1]], [capacity_mw, capacity_mw], 
                           line_width=2, color='#2ca02c', line_dash='dashed', line_alpha=0.7,
                           legend_label=f'Max Capacity ({capacity_mw:.0f} MW)')
            
            # Set y-range to include capacity line
            y_max = max(generation) * 1.1
            if hasattr(self.motor, 'station_data') and 'capacity_mw' in self.motor.station_data.columns:
                capacity_mw = self.motor.station_data['capacity_mw'].iloc[0]
                if capacity_mw > 0:
                    y_max = max(y_max, capacity_mw * 1.05)  # 5% above capacity line
            
            p.y_range = Range1d(start=min(generation) * 0.9, end=y_max)
            p.yaxis.axis_label = 'Generation (MW)'
            p.yaxis.axis_label_text_color = '#2ca02c'
            
            # Secondary axis (right) - Price
            price_range = Range1d(start=min(prices) * 0.9, end=max(prices) * 1.1)
            p.extra_y_ranges = {'price': price_range}
            p.line(timestamps, prices, line_width=3, color='#d62728', legend_label='Price ($/MWh)', y_range_name='price')
            
            # Add secondary y-axis on the right
            price_axis = LinearAxis(y_range_name='price', axis_label='Price ($/MWh)')
            price_axis.axis_label_text_color = '#d62728'
            p.add_layout(price_axis, 'right')
            
            # Configure legend and axes
            p.legend.location = "top_left"
            p.legend.click_policy = "hide"
            p.xaxis.axis_label = 'Time'
            
            return pn.pane.Bokeh(p, sizing_mode='stretch_width')
            
        except Exception as e:
            logger.error(f"Error creating time series charts: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return pn.pane.Markdown(f"Error creating time series charts: {e}")
    
    def _create_time_of_day_chart(self, time_of_day_data):
        """Create time-of-day analysis chart with dual y-axes - two lines"""
        try:
            if time_of_day_data is None or len(time_of_day_data) == 0:
                return pn.pane.Markdown("No data available for time-of-day analysis.")
            
            # Use Bokeh directly for proper dual-axis control
            from bokeh.plotting import figure
            from bokeh.models import LinearAxis, Range1d
            
            # Extract data
            hours = time_of_day_data['hour'].values
            generation = time_of_day_data['scadavalue'].values
            prices = time_of_day_data['price'].values
            
            # Get appropriate title based on mode
            if self.analysis_mode == 'station' and self.selected_station_duids:
                title = f'Station ({len(self.selected_station_duids)} units) - Average Performance by Hour of Day'
            else:
                title = f'{self.selected_duid} - Average Performance by Hour of Day'
            
            # Create figure with primary y-axis for generation
            p = figure(
                title=title,
                width=700,
                height=400,
                tools='pan,wheel_zoom,box_zoom,reset,save,hover'
            )
            
            # Remove grid
            p.grid.visible = False
            
            # Primary axis (left) - Generation with line and markers
            p.line(hours, generation, line_width=4, color='#2ca02c', legend_label='Average Generation (MW)')
            p.scatter(hours, generation, size=8, color='#2ca02c')
            
            # Add capacity reference line if capacity data is available
            if hasattr(self.motor, 'station_data') and 'capacity_mw' in self.motor.station_data.columns:
                capacity_mw = self.motor.station_data['capacity_mw'].iloc[0]
                if capacity_mw > 0:
                    # Add horizontal dashed line for maximum capacity
                    p.line([0, 23], [capacity_mw, capacity_mw], 
                           line_width=2, color='#2ca02c', line_dash='dashed', line_alpha=0.7,
                           legend_label=f'Max Capacity ({capacity_mw:.0f} MW)')
            
            # Set y-range to include capacity line
            y_max = max(generation) * 1.1
            if hasattr(self.motor, 'station_data') and 'capacity_mw' in self.motor.station_data.columns:
                capacity_mw = self.motor.station_data['capacity_mw'].iloc[0]
                if capacity_mw > 0:
                    y_max = max(y_max, capacity_mw * 1.05)  # 5% above capacity line
            
            p.y_range = Range1d(start=min(generation) * 0.9, end=y_max)
            p.yaxis.axis_label = 'Average Generation (MW)'
            p.yaxis.axis_label_text_color = '#2ca02c'
            
            # Secondary axis (right) - Price with line and markers
            price_range = Range1d(start=min(prices) * 0.9, end=max(prices) * 1.1)
            p.extra_y_ranges = {'price': price_range}
            p.line(hours, prices, line_width=4, color='#d62728', legend_label='Average Price ($/MWh)', y_range_name='price')
            p.scatter(hours, prices, size=8, color='#d62728', y_range_name='price')
            
            # Add secondary y-axis on the right
            price_axis = LinearAxis(y_range_name='price', axis_label='Average Price ($/MWh)')
            price_axis.axis_label_text_color = '#d62728'
            p.add_layout(price_axis, 'right')
            
            # Configure legend and axes
            p.legend.location = "top_left"
            p.legend.click_policy = "hide"
            p.xaxis.axis_label = 'Hour of Day'
            p.xaxis.ticker = list(range(0, 24, 3))  # Show every 3 hours
            
            return pn.pane.Bokeh(p, sizing_mode='stretch_width')
            
        except Exception as e:
            logger.error(f"Error creating time-of-day chart: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return pn.pane.Markdown(f"Error creating time-of-day chart: {e}")
    
    def _create_summary_statistics(self, metrics):
        """Create summary statistics table"""
        try:
            if not metrics:
                return pn.pane.Markdown("No performance metrics available.")
            
            # Format metrics for display
            summary_data = []
            
            if 'total_generation_gwh' in metrics:
                summary_data.append(['Total Generation', f"{metrics['total_generation_gwh']:.1f} GWh"])
            
            if 'total_revenue_millions' in metrics:
                summary_data.append(['Total Revenue', f"${metrics['total_revenue_millions']:.1f}M"])
                
            if 'average_price' in metrics:
                summary_data.append(['Average Price', f"${metrics['average_price']:.2f}/MWh"])
                
            if 'capacity_factor' in metrics:
                summary_data.append(['Capacity Factor', f"{metrics['capacity_factor']:.1f}%"])
                
            if 'peak_generation' in metrics:
                summary_data.append(['Peak Generation', f"{metrics['peak_generation']:.1f} MW"])
                
            if 'operating_hours' in metrics:
                summary_data.append(['Operating Hours', f"{metrics['operating_hours']:.1f} hours"])
            
            # Create DataFrame for tabulator
            summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
            
            # Create tabulator widget without index column
            summary_table = pn.widgets.Tabulator(
                summary_df,
                pagination='remote',
                page_size=10,
                sizing_mode='stretch_width',
                height=300,
                theme='midnight',  # Dark theme
                show_index=False  # Remove index column
            )
            
            return summary_table
            
        except Exception as e:
            logger.error(f"Error creating summary statistics: {e}")
            return pn.pane.Markdown(f"Error creating summary statistics: {e}")

def create_station_analysis_tab():
    """
    Create and return the Station Analysis tab component.
    
    Returns:
        Panel component for the Station Analysis tab
    """
    try:
        logger.info("Creating Station Analysis tab...")
        ui = StationAnalysisUI()
        tab_content = ui.create_ui_components()
        logger.info("Station Analysis tab created successfully")
        return tab_content
        
    except Exception as e:
        logger.error(f"Error creating Station Analysis tab: {e}")
        return pn.pane.Markdown(f"""
        ## Station Analysis Tab Error
        
        Failed to create the Station Analysis tab: {e}
        
        Please check the logs for more details.
        """)