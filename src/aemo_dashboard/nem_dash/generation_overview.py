"""
24-hour Generation Overview Component for Nem-dash tab
Fixed 24-hour stacked area chart showing NEM generation by fuel type
"""

import pandas as pd
import numpy as np
import panel as pn
import holoviews as hv
import hvplot.pandas
from datetime import datetime, timedelta

from ..shared.config import config
from ..shared.logging_config import get_logger

logger = get_logger(__name__)

# Configure HoloViews (ensure it's set up)
hv.extension('bokeh')

# Fuel colors consistent with main dashboard
FUEL_COLORS = {
    'Solar': '#FFD700',           # Gold
    'Rooftop Solar': '#FFF59D',   # Light yellow
    'Wind': '#00FF7F',            # Spring green - matches Generation tab
    'Water': '#00BFFF',           # Sky blue - matches Generation tab
    'Battery Storage': '#9370DB',  # Medium purple
    'Battery': '#9370DB',         # Medium purple (same as Battery Storage)
    'Coal': '#8B4513',            # Saddle brown
    'Gas other': '#FF7F50',       # Coral
    'OCGT': '#FF6347',            # Tomato
    'CCGT': '#FF4500',            # Orange red
    'Biomass': '#228B22',         # Forest green
    'Other': '#A9A9A9',           # Dark gray
    'Transmission Flow': '#FFB6C1' # Light pink
}

# HoloViews options for consistent styling
hv.opts.defaults(
    hv.opts.Area(
        width=1200,
        height=400,
        alpha=0.8,
        show_grid=False,
        toolbar='above'
    ),
    hv.opts.Overlay(
        show_grid=False,
        toolbar='above'
    )
)


def load_generation_data():
    """
    Load generation data for the last 24 hours
    """
    try:
        gen_file = config.gen_output_file
        logger.info(f"Loading generation data from: {gen_file}")
        
        if not gen_file.exists():
            logger.error(f"Generation file not found: {gen_file}")
            return pd.DataFrame()
        
        # Load generation data
        gen_data = pd.read_parquet(gen_file)
        logger.info(f"Loaded {len(gen_data)} generation records")
        logger.info(f"Generation data columns: {list(gen_data.columns)}")
        logger.info(f"Generation data dtypes: {gen_data.dtypes}")
        if not gen_data.empty:
            logger.info(f"Sample data: {gen_data.head(2).to_dict()}")
        
        # Filter for last 24 hours
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        logger.info(f"Date filter range: {start_time} to {end_time}")
        
        # Ensure SETTLEMENTDATE is datetime and in index
        if 'SETTLEMENTDATE' in gen_data.columns:
            gen_data['SETTLEMENTDATE'] = pd.to_datetime(gen_data['SETTLEMENTDATE'])
            gen_data = gen_data.set_index('SETTLEMENTDATE')
        elif not isinstance(gen_data.index, pd.DatetimeIndex):
            gen_data.index = pd.to_datetime(gen_data.index)
        
        # Check data date range before filtering
        logger.info(f"Data date range: {gen_data.index.min()} to {gen_data.index.max()}")
        
        # Filter for last 24 hours
        filtered_data = gen_data[
            (gen_data.index >= start_time) & (gen_data.index <= end_time)
        ]
        
        # If no data in last 24 hours, try last 7 days as fallback
        if len(filtered_data) == 0:
            logger.warning("No data in last 24 hours, trying last 7 days...")
            start_time_7d = end_time - timedelta(days=7)
            filtered_data = gen_data[
                (gen_data.index >= start_time_7d) & (gen_data.index <= end_time)
            ]
            logger.info(f"Found {len(filtered_data)} records in last 7 days")
            
            # If still no data with date filtering, just use the most recent data
            if len(filtered_data) == 0:
                logger.warning("Date filtering failed completely, using most recent data available...")
                filtered_data = gen_data.tail(288)  # Last 288 records (24 hours worth)
                logger.info(f"Using most recent {len(filtered_data)} records (ignoring dates)")
            elif len(filtered_data) > 0:
                # Take just the last 24 hours worth (288 records = 24h * 12 per hour)
                filtered_data = filtered_data.tail(288)
                logger.info(f"Using most recent {len(filtered_data)} records from 7-day range")
        
        logger.info(f"Filtered to {len(filtered_data)} records for last 24 hours")
        return filtered_data
        
    except Exception as e:
        logger.error(f"Error loading generation data: {e}")
        return pd.DataFrame()


def load_transmission_data():
    """
    Load transmission data for the last 24 hours
    """
    try:
        transmission_file = config.transmission_output_file
        logger.info(f"Loading transmission data from: {transmission_file}")
        
        if not transmission_file.exists():
            logger.warning(f"Transmission file not found: {transmission_file}")
            return pd.DataFrame()
        
        # Load transmission data
        transmission_data = pd.read_parquet(transmission_file)
        
        # Filter for last 24 hours
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # Ensure proper datetime index
        if 'SETTLEMENTDATE' in transmission_data.columns:
            transmission_data['SETTLEMENTDATE'] = pd.to_datetime(transmission_data['SETTLEMENTDATE'])
            transmission_data = transmission_data.set_index('SETTLEMENTDATE')
        elif not isinstance(transmission_data.index, pd.DatetimeIndex):
            transmission_data.index = pd.to_datetime(transmission_data.index)
        
        # Filter for last 24 hours
        filtered_transmission = transmission_data[
            (transmission_data.index >= start_time) & (transmission_data.index <= end_time)
        ]
        
        logger.info(f"Loaded {len(filtered_transmission)} transmission records for last 24 hours")
        return filtered_transmission
        
    except Exception as e:
        logger.error(f"Error loading transmission data: {e}")
        return pd.DataFrame()


def _convert_rooftop_30min_to_5min(df_30min):
    """
    Convert 30-minute rooftop solar data to 5-minute intervals using cubic spline interpolation
    """
    if df_30min.empty:
        return pd.DataFrame()
    
    try:
        # Ensure we have a datetime index
        if not isinstance(df_30min.index, pd.DatetimeIndex):
            if 'settlementdate' in df_30min.columns:
                df_30min = df_30min.set_index('settlementdate')
            elif 'SETTLEMENTDATE' in df_30min.columns:
                df_30min = df_30min.set_index('SETTLEMENTDATE')
        
        # Fill any NaN values with 0
        df_30min = df_30min.fillna(0)
        
        # Resample to 5-minute intervals and interpolate with cubic splines
        df_5min = df_30min.resample('5min').asfreq()
        
        # Apply cubic interpolation for smooth curves
        if len(df_30min) >= 4:
            df_5min = df_5min.interpolate(method='cubic', limit_direction='forward')
        else:
            df_5min = df_5min.interpolate(method='linear', limit_direction='forward')
        
        # Smart end-point handling: use trend from last few points
        if len(df_30min) >= 3:
            last_points = df_30min.tail(3)
            
            for col in df_30min.columns:
                values = last_points[col].values
                if len(values) >= 2 and values[-1] > 0:
                    # Calculate trend from last 2 points
                    trend_per_30min = values[-1] - values[-2]
                    trend_per_5min = trend_per_30min / 6
                    
                    # Find NaN values at the end that need extrapolation
                    last_valid_idx = df_5min[col].last_valid_index()
                    if last_valid_idx is not None:
                        mask = df_5min.index > last_valid_idx
                        num_periods = mask.sum()
                        
                        if num_periods > 0 and num_periods <= 6:
                            last_value = df_5min.loc[last_valid_idx, col]
                            for i, idx in enumerate(df_5min.index[mask]):
                                # Apply trend with decay
                                decay_factor = 0.9 ** i
                                new_value = last_value + (i + 1) * trend_per_5min * decay_factor
                                df_5min.loc[idx, col] = max(0, min(new_value, last_value * 1.5))
        
        # Fill any remaining NaN with forward-fill (limited to 6 periods)
        df_5min = df_5min.fillna(method='ffill', limit=6)
        df_5min = df_5min.fillna(0)
        df_5min = df_5min.clip(lower=0)
        
        logger.info(f"Converted {len(df_30min)} 30-min rooftop records to {len(df_5min)} 5-min records")
        return df_5min
        
    except Exception as e:
        logger.error(f"Error converting rooftop solar data: {e}")
        return df_30min

def load_rooftop_solar_data():
    """
    Load rooftop solar data for the last 24 hours
    """
    try:
        rooftop_file = config.rooftop_solar_file
        logger.info(f"Loading rooftop solar data from: {rooftop_file}")
        
        if not rooftop_file.exists():
            logger.warning(f"Rooftop solar file not found: {rooftop_file}")
            return pd.DataFrame()
        
        # Load rooftop solar data
        rooftop_data = pd.read_parquet(rooftop_file)
        
        # Ensure proper datetime handling
        if 'settlementdate' in rooftop_data.columns:
            rooftop_data['settlementdate'] = pd.to_datetime(rooftop_data['settlementdate'])
            rooftop_data = rooftop_data.set_index('settlementdate')
        elif 'SETTLEMENTDATE' in rooftop_data.columns:
            rooftop_data['SETTLEMENTDATE'] = pd.to_datetime(rooftop_data['SETTLEMENTDATE'])
            rooftop_data = rooftop_data.set_index('SETTLEMENTDATE')
        elif not isinstance(rooftop_data.index, pd.DatetimeIndex):
            rooftop_data.index = pd.to_datetime(rooftop_data.index)
        
        # Check if data is in 30-minute intervals
        if len(rooftop_data) > 1:
            # Calculate typical interval between consecutive timestamps
            time_diffs = rooftop_data.index.to_series().diff().dropna()
            median_interval = time_diffs.median()
            
            # If median interval is around 30 minutes, convert to 5-minute
            if median_interval >= timedelta(minutes=25) and median_interval <= timedelta(minutes=35):
                logger.info("Detected 30-minute rooftop solar data, converting to 5-minute intervals")
                rooftop_data = _convert_rooftop_30min_to_5min(rooftop_data)
            else:
                logger.info(f"Rooftop solar data appears to be in {median_interval.total_seconds()/60:.0f}-minute intervals")
        
        # Filter for last 24 hours
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # Filter for last 24 hours
        filtered_rooftop = rooftop_data[
            (rooftop_data.index >= start_time) & (rooftop_data.index <= end_time)
        ]
        
        logger.info(f"Loaded {len(filtered_rooftop)} rooftop solar records for last 24 hours")
        return filtered_rooftop
        
    except Exception as e:
        logger.error(f"Error loading rooftop solar data: {e}")
        return pd.DataFrame()


def prepare_generation_for_stacking(gen_data, transmission_data=None, rooftop_data=None):
    """
    Prepare generation data for stacked area chart
    Mirrors the logic from the main dashboard
    """
    try:
        if gen_data.empty:
            logger.warning("No generation data to prepare")
            return pd.DataFrame()
        
        # Check available columns and adapt
        logger.info(f"Generation data columns: {list(gen_data.columns)}")
        
        # Check if this is already processed data (from dashboard) or raw data
        fuel_columns = ['Solar', 'Wind', 'Water', 'Coal', 'Gas other', 'CCGT', 'OCGT', 'Battery Storage', 'Biomass']
        has_fuel_columns = any(col in gen_data.columns for col in fuel_columns)
        
        if has_fuel_columns:
            # This is already processed/pivoted data from dashboard - just rename index
            logger.info("Data is already processed by fuel type - using directly")
            pivot_df = gen_data.copy()
            
            # Ensure we have the time column as index
            if 'settlementdate' in pivot_df.columns:
                pivot_df = pivot_df.set_index('settlementdate')
            elif 'SETTLEMENTDATE' in pivot_df.columns:
                pivot_df = pivot_df.set_index('SETTLEMENTDATE')
            
            # Rename index for hvplot
            pivot_df.index.name = 'settlementdate'
            
            # Keep only fuel columns (remove any extra columns)
            # Include all possible fuel columns including Transmission Flow
            all_fuel_columns = fuel_columns + ['Rooftop Solar', 'Other', 'Transmission Flow', 'Transmission Exports']
            fuel_cols_present = [col for col in pivot_df.columns if col in all_fuel_columns]
            pivot_df = pivot_df[fuel_cols_present]
            
        elif 'FUEL_CAT' in gen_data.columns and 'MW' in gen_data.columns:
            # Raw format - use FUEL_CAT and MW
            logger.info("Raw data format - grouping by FUEL_CAT")
            pivot_df = gen_data.groupby(['SETTLEMENTDATE', 'FUEL_CAT'])['MW'].sum().unstack(fill_value=0)
        elif 'fuel' in gen_data.columns and 'scadavalue' in gen_data.columns:
            # Alternative raw format - use fuel and scadavalue
            logger.info("Raw data format - grouping by fuel")
            pivot_df = gen_data.groupby(['SETTLEMENTDATE', 'fuel'])['scadavalue'].sum().unstack(fill_value=0)
        else:
            logger.error(f"Cannot find suitable columns for grouping. Available: {list(gen_data.columns)}")
            return pd.DataFrame()
        
        # Ensure index is datetime
        if not isinstance(pivot_df.index, pd.DatetimeIndex):
            pivot_df.index = pd.to_datetime(pivot_df.index)
        
        # Rename index for hvplot
        pivot_df.index.name = 'settlementdate'
        
        # Add transmission flows if available
        if transmission_data is not None and not transmission_data.empty:
            try:
                # Calculate net transmission flows (simplified version)
                # Group by settlement date and calculate net flow for NEM
                transmission_grouped = transmission_data.groupby('SETTLEMENTDATE')['METEREDMWFLOW'].sum()
                
                # Align with generation data index
                net_flows = pd.DataFrame({
                    'net_transmission_mw': transmission_grouped
                }, index=transmission_grouped.index)
                
                # Reindex to match generation data
                if len(pivot_df) > 0:
                    transmission_series = net_flows.reindex(pivot_df.index, fill_value=0)['net_transmission_mw']
                    transmission_values = pd.to_numeric(transmission_series, errors='coerce').fillna(0)
                    
                    # Add transmission imports (positive values only)
                    pivot_df['Transmission Flow'] = pd.Series(
                        np.where(transmission_values.values > 0, transmission_values.values, 0),
                        index=transmission_values.index
                    )
                    
                    logger.info(f"Added transmission flows: max {pivot_df['Transmission Flow'].max():.1f}MW")
                
            except Exception as e:
                logger.error(f"Error adding transmission flows: {e}")
        
        # Add rooftop solar if available
        if rooftop_data is not None and not rooftop_data.empty:
            try:
                # Assume rooftop data has NEM total or sum regions
                if 'NEM' in rooftop_data.columns:
                    rooftop_series = rooftop_data['NEM']
                else:
                    # Sum all regions
                    rooftop_series = rooftop_data.sum(axis=1)
                
                # Align with generation data
                if len(pivot_df) > 0:
                    rooftop_aligned = rooftop_series.reindex(pivot_df.index)
                    
                    # Forward-fill missing values at the end (up to 2 hours)
                    # This handles the case where rooftop data is less recent than generation data
                    rooftop_aligned = rooftop_aligned.fillna(method='ffill', limit=24)  # 24 * 5min = 2 hours
                    
                    # Apply gentle decay for extended forward-fill periods
                    last_valid_idx = rooftop_aligned.last_valid_index()
                    if last_valid_idx is not None and last_valid_idx < rooftop_aligned.index[-1]:
                        # Calculate how many periods we're forward-filling
                        fill_start_pos = rooftop_aligned.index.get_loc(last_valid_idx) + 1
                        fill_periods = len(rooftop_aligned) - fill_start_pos
                        
                        if fill_periods > 0:
                            # Apply exponential decay for realism (solar decreases over time)
                            last_value = rooftop_aligned.iloc[fill_start_pos - 1]
                            decay_rate = 0.98  # 2% decay per 5-minute period
                            for i in range(fill_periods):
                                rooftop_aligned.iloc[fill_start_pos + i] = last_value * (decay_rate ** (i + 1))
                    
                    # Fill any remaining NaN with 0
                    rooftop_aligned = rooftop_aligned.fillna(0)
                    pivot_df['Rooftop Solar'] = rooftop_aligned
                    
                    logger.info(f"Added rooftop solar: max {pivot_df['Rooftop Solar'].max():.1f}MW")
                
            except Exception as e:
                logger.error(f"Error adding rooftop solar: {e}")
        
        # Ensure all values are positive for stacking EXCEPT Battery Storage
        # Battery Storage can be negative (charging) or positive (discharging)
        for col in pivot_df.columns:
            if col not in ['settlementdate', 'Battery Storage', 'Battery']:
                pivot_df[col] = pivot_df[col].clip(lower=0)
        
        logger.info(f"Prepared data shape: {pivot_df.shape}")
        logger.info(f"Fuel types: {list(pivot_df.columns)}")
        
        # Define preferred fuel order with battery near zero line
        preferred_order = [
            'Transmission Flow',     # At top of stack (positive values)
            'Solar', 
            'Rooftop Solar',
            'Wind', 
            'Other', 
            'Coal', 
            'CCGT', 
            'Gas other', 
            'OCGT', 
            'Water',
            'Battery Storage',       # Near zero line (can be negative for charging)
            'Battery',              # Alternative name for Battery Storage
            'Biomass'
        ]
        
        # Reorder columns based on preferred order, only including columns that exist
        available_fuels = [fuel for fuel in preferred_order if fuel in pivot_df.columns]
        
        # Add any remaining fuels not in the preferred order
        remaining_fuels = [col for col in pivot_df.columns if col not in available_fuels]
        final_order = available_fuels + remaining_fuels
        
        # Reorder the dataframe
        pivot_df = pivot_df[final_order]
        
        return pivot_df
        
    except Exception as e:
        logger.error(f"Error preparing generation data: {e}")
        return pd.DataFrame()


def create_24hour_generation_chart(pivot_df):
    """
    Create 24-hour stacked area chart with proper battery handling
    """
    try:
        if pivot_df.empty:
            return pn.pane.HTML(
                "<div style='width:800px;height:400px;display:flex;align-items:center;justify-content:center;'>"
                "<h3>No generation data available for last 24 hours</h3></div>",
                width=800, height=400
            )
        
        # Rename Battery Storage to Battery for consistency
        if 'Battery Storage' in pivot_df.columns:
            pivot_df = pivot_df.rename(columns={'Battery Storage': 'Battery'})
        
        # Get fuel types (exclude any index columns)
        fuel_types = [col for col in pivot_df.columns if col not in ['settlementdate']]
        
        if not fuel_types:
            return pn.pane.HTML(
                "<div style='width:800px;height:400px;display:flex;align-items:center;justify-content:center;'>"
                "<h3>No fuel type data available</h3></div>",
                width=800, height=400
            )
        
        # Separate positive and negative values for battery
        plot_data_positive = pivot_df.copy()
        battery_col = 'Battery'
        has_battery = battery_col in plot_data_positive.columns
        
        # Handle battery - only keep positive values in main plot
        if has_battery:
            plot_data_positive[battery_col] = plot_data_positive[battery_col].clip(lower=0)
        
        # Get fuel types for positive stacking (all fuels)
        positive_fuel_types = fuel_types
        
        # Create main stacked area plot with positive values
        main_plot = plot_data_positive.hvplot.area(
            x='settlementdate',
            y=positive_fuel_types,
            stacked=True,
            width=800,
            height=400,
            ylabel='Generation (MW)',
            xlabel='Time',
            color=[FUEL_COLORS.get(fuel, '#888888') for fuel in positive_fuel_types],
            alpha=0.8,
            hover_cols=['settlementdate'] + positive_fuel_types,
            legend='right'
        )
        
        # Check if we have negative battery values
        if has_battery and (pivot_df[battery_col].values < 0).any():
            # Create negative battery data
            plot_data_negative = pd.DataFrame(index=pivot_df.index)
            plot_data_negative['settlementdate'] = plot_data_negative.index
            plot_data_negative[battery_col] = pd.Series(
                np.where(pivot_df[battery_col].values < 0, pivot_df[battery_col].values, 0),
                index=pivot_df.index
            )
            
            # Create battery negative area plot
            battery_negative_plot = plot_data_negative.hvplot.area(
                x='settlementdate',
                y=battery_col,
                stacked=False,
                width=800,
                height=400,
                color=FUEL_COLORS.get('Battery', '#9370DB'),
                alpha=0.8,
                hover=True,
                legend=False  # Legend already shown in main plot
            )
            
            # Combine positive and negative plots
            area_plot = main_plot * battery_negative_plot
        else:
            area_plot = main_plot
        
        # Apply styling options
        area_plot = area_plot.opts(
            title="NEM Generation - Last 24 Hours",
            show_grid=False,
            toolbar='above',
            fontsize={'title': 14, 'labels': 12, 'xticks': 10, 'yticks': 10}
        )
        
        return pn.pane.HoloViews(area_plot, sizing_mode='fixed', width=800, height=400, 
                                css_classes=['chart-no-border'],
                                linked_axes=False)  # Disable axis linking to prevent UFuncTypeError
        
    except Exception as e:
        logger.error(f"Error creating generation chart: {e}")
        return pn.pane.HTML(
            f"<div style='width:800px;height:400px;display:flex;align-items:center;justify-content:center;'>"
            f"<h3>Error creating chart: {e}</h3></div>",
            width=800, height=400
        )


def create_generation_overview_component(dashboard_instance=None):
    """
    Create the complete 24-hour generation overview component
    """
    def update_generation_overview():
        try:
            # Try to use dashboard's processed data first if available
            if dashboard_instance and hasattr(dashboard_instance, 'process_data_for_region'):
                logger.info("Using dashboard's process_data_for_region() method")
                try:
                    # Use the dashboard's own method to get processed data
                    gen_data = dashboard_instance.process_data_for_region()
                    logger.info(f"Dashboard processed data shape: {gen_data.shape if not gen_data.empty else 'empty'}")
                    logger.info(f"Dashboard processed data columns: {list(gen_data.columns) if not gen_data.empty else 'none'}")
                    
                    if not gen_data.empty:
                        # This data is already processed by fuel type and filtered by the dashboard's time range
                        # Convert to format needed for stacking (add SETTLEMENTDATE column)
                        if gen_data.index.name == 'settlementdate':
                            gen_data = gen_data.reset_index()
                            gen_data['SETTLEMENTDATE'] = gen_data['settlementdate']
                        elif 'settlementdate' not in gen_data.columns:
                            gen_data = gen_data.reset_index()
                            gen_data['SETTLEMENTDATE'] = gen_data.index
                        
                        # Take last 24 hours worth (288 records = 24h * 12 per hour)
                        gen_data = gen_data.tail(288)
                        logger.info(f"Using dashboard processed data: {len(gen_data)} records (last 24h equivalent)")
                except Exception as e:
                    logger.error(f"Error using dashboard processed data: {e}")
                    gen_data = pd.DataFrame()
            else:
                # Fallback to loading data directly
                logger.info("Loading generation data directly")
                gen_data = load_generation_data()
            
            transmission_data = load_transmission_data()
            rooftop_data = load_rooftop_solar_data()
            
            # Prepare data for stacking
            pivot_df = prepare_generation_for_stacking(gen_data, transmission_data, rooftop_data)
            
            # Create chart
            chart = create_24hour_generation_chart(pivot_df)
            
            return chart
            
        except Exception as e:
            logger.error(f"Error updating generation overview: {e}")
            return pn.pane.HTML(
                f"<div style='width:800px;height:400px;display:flex;align-items:center;justify-content:center;'>"
                f"<h3>Error loading generation overview: {e}</h3></div>",
                width=800, height=400
            )
    
    return pn.pane.panel(update_generation_overview)


if __name__ == "__main__":
    # Test the generation overview component
    pn.extension('bokeh')
    hv.extension('bokeh')
    
    overview = create_generation_overview_component()
    
    layout = pn.Column(
        pn.pane.Markdown("## 24-Hour Generation Overview Test"),
        overview
    )
    layout.show()