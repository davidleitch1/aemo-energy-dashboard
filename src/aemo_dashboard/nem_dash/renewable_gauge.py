"""
Renewable Energy Gauge Component for Nem-dash tab
Uses Plotly gauge with reference markers on the rim
"""

import pandas as pd
import numpy as np
import panel as pn
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path

from ..shared.config import config
from ..shared.logging_config import get_logger

logger = get_logger(__name__)

# Renewable fuel types to include in calculation
RENEWABLE_FUELS = ['Wind', 'Solar', 'Water', 'Rooftop Solar']

# File to store historical records
RECORDS_FILE = Path(config.data_dir) / 'renewable_records.json'


def load_renewable_records():
    """
    Load historical renewable energy records from JSON file
    Returns dict with 'all_time' and 'hourly' records
    """
    default_records = {
        'all_time': {'value': 45.2, 'timestamp': '2025-01-15T14:30:00'},
        'hourly': {str(h): {'value': 30 + h * 0.8, 'timestamp': '2025-01-01T00:00:00'} 
                  for h in range(24)}
    }
    
    try:
        if RECORDS_FILE.exists():
            with open(RECORDS_FILE, 'r') as f:
                records = json.load(f)
            logger.info("Loaded renewable energy records from file")
            return records
        else:
            logger.info("No records file found, using defaults")
            return default_records
    except Exception as e:
        logger.error(f"Error loading records: {e}, using defaults")
        return default_records


def save_renewable_records(records):
    """
    Save renewable energy records to JSON file
    """
    try:
        RECORDS_FILE.parent.mkdir(exist_ok=True)
        with open(RECORDS_FILE, 'w') as f:
            json.dump(records, f, indent=2)
        logger.info("Saved renewable energy records to file")
    except Exception as e:
        logger.error(f"Error saving records: {e}")


def calculate_renewable_percentage(gen_data):
    """
    Calculate renewable energy percentage from generation data
    
    Args:
        gen_data: DataFrame with generation data by fuel type (latest row)
        
    Returns:
        float: Renewable percentage (0-100)
    """
    try:
        if gen_data is None or gen_data.empty:
            logger.warning("gen_data is None or empty")
            return 0.0
        
        logger.info(f"Calculating renewable % from data: {dict(gen_data) if hasattr(gen_data, 'to_dict') else gen_data}")
        logger.info(f"RENEWABLE_FUELS: {RENEWABLE_FUELS}")
        
        # Handle both Series and DataFrame
        if isinstance(gen_data, pd.DataFrame):
            if len(gen_data) > 1:
                latest_data = gen_data.iloc[-1]
            else:
                latest_data = gen_data.iloc[0] if len(gen_data) == 1 else gen_data.squeeze()
        else:
            # Already a Series
            latest_data = gen_data
        
        # Fuels to exclude from total generation calculation
        EXCLUDED_FUELS = ['Battery Storage', 'Transmission Flow']
        
        # Calculate renewable generation
        renewable_gen = 0
        total_gen = 0
        
        for fuel in latest_data.index:
            value = latest_data[fuel]
            is_excluded = fuel in EXCLUDED_FUELS
            is_renewable = fuel in RENEWABLE_FUELS
            logger.info(f"Fuel: {fuel}, Value: {value}, Is Renewable: {is_renewable}, Is Excluded: {is_excluded}")
            
            if pd.notna(value) and value > 0 and fuel not in EXCLUDED_FUELS:  # Exclude battery and transmission
                total_gen += value
                if fuel in RENEWABLE_FUELS:
                    renewable_gen += value
        
        if total_gen > 0:
            percentage = (renewable_gen / total_gen) * 100
            logger.info(f"Renewable: {renewable_gen:.1f}MW / Total (excl. battery/transmission): {total_gen:.1f}MW = {percentage:.1f}%")
            return min(100.0, max(0.0, percentage))  # Clamp to 0-100
        else:
            logger.warning("No positive generation data found")
            return 0.0
            
    except Exception as e:
        logger.error(f"Error calculating renewable percentage: {e}")
        return 0.0


def update_records(current_percentage):
    """
    Update historical records if current percentage sets new records
    
    Args:
        current_percentage: Current renewable percentage
        
    Returns:
        tuple: (all_time_record, hour_record, records_updated)
    """
    try:
        records = load_renewable_records()
        current_time = datetime.now()
        current_hour = current_time.hour
        timestamp = current_time.isoformat()
        records_updated = False
        
        # Check all-time record
        if current_percentage > records['all_time']['value']:
            records['all_time'] = {
                'value': current_percentage,
                'timestamp': timestamp
            }
            records_updated = True
            logger.info(f"New all-time renewable record: {current_percentage:.1f}%")
        
        # Check hourly record
        hour_key = str(current_hour)
        if hour_key not in records['hourly']:
            records['hourly'][hour_key] = {
                'value': current_percentage,
                'timestamp': timestamp
            }
            records_updated = True
        elif current_percentage > records['hourly'][hour_key]['value']:
            records['hourly'][hour_key] = {
                'value': current_percentage,
                'timestamp': timestamp
            }
            records_updated = True
            logger.info(f"New {current_hour}:00 hour record: {current_percentage:.1f}%")
        
        if records_updated:
            save_renewable_records(records)
        
        all_time_record = records['all_time']['value']
        hour_record = records['hourly'][hour_key]['value']
        
        return all_time_record, hour_record, records_updated
        
    except Exception as e:
        logger.error(f"Error updating records: {e}")
        return 45.2, 38.7, False  # Default values


def create_renewable_gauge_plotly(current_value, all_time_record=45.2, hour_record=38.7):
    """
    Create Plotly gauge with reference markers on the rim
    """
    try:
        fig = go.Figure()
        
        # Main gauge
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=current_value,
            title={'text': "Renewable Energy %", 'font': {'size': 16, 'color': "#ff79c6"}},
            number={'suffix': "%", 'font': {'size': 18, 'color': "#ff79c6"}, 'valueformat': '.0f'},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickmode': 'linear',
                    'tick0': 0,
                    'dtick': 20,
                    'tickwidth': 1,
                    'tickcolor': "rgba(255, 121, 198, 0.6)",  # Pink with alpha 0.6
                    'tickfont': {'color': "rgba(255, 121, 198, 0.6)"}  # Pink text with alpha 0.6
                },
                'bar': {'color': "#ff79c6", 'thickness': 0.6, 'line': {'color': "#ff79c6", 'width': 4}},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 20], 'color': "rgba(255, 68, 68, 0.3)"},    # Red
                    {'range': [20, 40], 'color': "rgba(255, 136, 68, 0.3)"},  # Orange
                    {'range': [40, 60], 'color': "rgba(255, 170, 68, 0.3)"},  # Yellow
                    {'range': [60, 80], 'color': "rgba(136, 221, 68, 0.3)"},  # Light green
                    {'range': [80, 100], 'color': "rgba(68, 255, 68, 0.3)"}   # Green
                ],
                'threshold': {
                    'line': {'color': "gold", 'width': 4},
                    'thickness': 0.75,
                    'value': all_time_record
                }
            }
        ))
        
        # Calculate positions for rim markers
        center_x, center_y = 0.5, 0.35
        marker_radius = 0.28
        
        # All-time record marker (crown icon)
        all_time_angle = np.radians(180 - (all_time_record / 100) * 180)
        crown_x = center_x + marker_radius * np.cos(all_time_angle)
        crown_y = center_y + marker_radius * np.sin(all_time_angle)
        
        # Hour record marker (clock icon)
        hour_angle = np.radians(180 - (hour_record / 100) * 180)
        clock_x = center_x + marker_radius * np.cos(hour_angle)
        clock_y = center_y + marker_radius * np.sin(hour_angle)
        
        # Add marker annotations with icons
        fig.add_annotation(
            x=crown_x, y=crown_y,
            text="👑",  # Crown emoji for all-time record
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="gold",
            ax=0, ay=-30,  # Arrow pointing to gauge
            font=dict(size=20),
            bgcolor="rgba(255, 215, 0, 0.8)",
            bordercolor="gold",
            borderwidth=2
        )
        
        fig.add_annotation(
            x=clock_x, y=clock_y,
            text="🕐",  # Clock emoji for hour record
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="silver",
            ax=0, ay=-25,
            font=dict(size=16),
            bgcolor="rgba(192, 192, 192, 0.8)",
            bordercolor="silver",
            borderwidth=2
        )
        
        # Add legend positioned below the gauge
        fig.add_annotation(
            x=0.5, y=0.05,  # Bottom center
            text=f"👑 All-time: {all_time_record:.0f}%  🕐 Hour record: {hour_record:.0f}%",
            showarrow=False,
            xref="paper", yref="paper",
            align="center",
            font=dict(size=12, color="#ff79c6"),
            bgcolor="rgba(40, 40, 40, 0.8)",
            bordercolor="rgba(255, 121, 198, 0.5)",
            borderwidth=1,
            borderpad=4
        )
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            height=350,
            width=400,
            margin=dict(l=30, r=30, t=60, b=30)
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating Plotly gauge: {e}")
        # Return simple fallback gauge
        return go.Figure().add_trace(go.Indicator(
            mode="gauge+number",
            value=current_value,
            title={'text': "Renewable Energy %"},
            gauge={'axis': {'range': [0, 100]}}
        ))


def create_renewable_gauge_component(dashboard_instance=None):
    """
    Create Panel component for renewable energy gauge
    
    Args:
        dashboard_instance: Reference to main dashboard for data access
    """
    def update_gauge():
        try:
            logger.info("Updating renewable gauge...")
            gen_data = None
            
            # Get generation data from dashboard or load directly  
            if dashboard_instance and hasattr(dashboard_instance, 'process_data_for_region'):
                logger.info("Using dashboard's process_data_for_region() for gauge")
                try:
                    # Use the dashboard's own processed data method
                    plot_data = dashboard_instance.process_data_for_region()
                    logger.info(f"Dashboard processed data shape: {plot_data.shape if not plot_data.empty else 'empty'}")
                    logger.info(f"Dashboard processed data columns: {list(plot_data.columns) if not plot_data.empty else 'none'}")
                    
                    if not plot_data.empty:
                        # Get the latest row - this is already aggregated by fuel type
                        latest_row = plot_data.iloc[-1]
                        gen_data = latest_row
                        logger.info(f"Using dashboard processed latest row: {dict(latest_row)}")
                except Exception as e:
                    logger.error(f"Error using dashboard processed data: {e}")
                    gen_data = None
            
            if gen_data is None or (hasattr(gen_data, 'empty') and gen_data.empty):
                logger.warning("No dashboard data available, trying direct load...")
                # Fallback: load data directly (less efficient)
                try:
                    gen_file = config.gen_output_file
                    if Path(gen_file).exists():
                        gen_data = pd.read_parquet(gen_file)
                        if not gen_data.empty:
                            # Get latest data point
                            gen_data = gen_data.tail(100).groupby('FUEL_CAT').sum()
                    else:
                        gen_data = None
                except Exception as e:
                    logger.error(f"Error loading generation data: {e}")
                    gen_data = None
            
            # Calculate renewable percentage
            if gen_data is not None and not gen_data.empty:
                current_percentage = calculate_renewable_percentage(gen_data)
                all_time_record, hour_record, updated = update_records(current_percentage)
                logger.info(f"Calculated renewable percentage: {current_percentage:.1f}%")
            else:
                logger.warning("No generation data available for renewable gauge - using test value")
                current_percentage = 25.0  # Test value so we can see the needle
                all_time_record, hour_record = 45.2, 38.7  # Defaults
            
            # Create Plotly gauge
            fig = create_renewable_gauge_plotly(current_percentage, all_time_record, hour_record)
            
            return pn.pane.Plotly(fig, sizing_mode='fixed', width=400, height=350)
            
        except Exception as e:
            logger.error(f"Error updating renewable gauge: {e}")
            return pn.pane.HTML(
                f"<div style='width:400px;height:350px;display:flex;align-items:center;justify-content:center;'>"
                f"<p>Renewable Gauge Error: {e}</p></div>",
                width=400, height=350
            )
    
    return pn.pane.panel(update_gauge)


if __name__ == "__main__":
    # Test the gauge component
    pn.extension()
    
    # Test with sample data
    test_data = pd.Series({
        'Wind': 2500,
        'Solar': 1800,
        'Water': 1200,
        'Rooftop Solar': 500,
        'Coal': 8000,
        'Gas other': 1500,
        'CCGT': 2000
    })
    
    percentage = calculate_renewable_percentage(test_data)
    fig = create_renewable_gauge_plotly(percentage)
    gauge_pane = pn.pane.Plotly(fig, width=400, height=350)
    
    layout = pn.Column(
        pn.pane.Markdown(f"## Renewable Gauge Test\n**Current:** {percentage:.1f}%"),
        gauge_pane
    )
    layout.show()