#!/usr/bin/env python3
"""
Real-time Energy Generation Dashboard with HvPlot
Shows interactive generation by fuel type with scrollable time window.
Supports both server and Pyodide (serverless) deployment.
"""

import pandas as pd
import numpy as np
import panel as pn
import param
import holoviews as hv
import hvplot.pandas
import asyncio
import os
from datetime import datetime, timedelta
import pickle
from pathlib import Path
import json
import sys
from bokeh.models import DatetimeTickFormatter
from dotenv import load_dotenv

from ..shared.config import config
from ..shared.logging_config import setup_logging, get_logger
from ..shared.email_alerts import EmailAlertManager
from ..analysis.price_analysis_ui import create_price_analysis_tab
from ..station.station_analysis_ui import create_station_analysis_tab

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Configure Panel and HoloViews BEFORE extension loading
pn.config.theme = 'dark'
pn.extension('tabulator', template='material')
hv.extension('bokeh')

# Logging is set up in imports

# Configure dark theme with grid enabled
hv.opts.defaults(
    hv.opts.Area(
        width=900,
        height=500,
        alpha=0.8,
        show_grid=True,
        toolbar='above'
    ),
    hv.opts.Overlay(
        show_grid=True,
        toolbar='above'
    )
)

# File paths from shared config
GEN_INFO_FILE = config.gen_info_file
GEN_OUTPUT_FILE = config.gen_output_file

# Add this function anywhere in your gen_dash.py file
def create_sample_env_file():
    """Create a sample .env file with all available options"""
    
    sample_content = """# Energy Dashboard Configuration
# Copy this file to .env and fill in your values
# DO NOT COMMIT .env TO GIT - ADD TO .gitignore

# ===== EMAIL ALERT CONFIGURATION =====
# iCloud Mail settings
ALERT_EMAIL=your-email@icloud.com
ALERT_PASSWORD=your-app-specific-password
RECIPIENT_EMAIL=your-email@icloud.com

# Email server settings (iCloud defaults)
SMTP_SERVER=smtp.mail.me.com
SMTP_PORT=587

# Gmail alternative (uncomment if using Gmail)
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587

# ===== ALERT BEHAVIOR =====
ENABLE_EMAIL_ALERTS=true
ALERT_COOLDOWN_HOURS=24
AUTO_ADD_TO_EXCEPTIONS=true

# ===== DASHBOARD SETTINGS =====
DEFAULT_REGION=NEM
UPDATE_INTERVAL_MINUTES=4.5

# ===== FILE PATHS (optional overrides) =====
# BASE_PATH=/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot
# GEN_INFO_FILE=/custom/path/to/gen_info.pkl
# GEN_OUTPUT_FILE=/custom/path/to/gen_output.parquet

# ===== LOGGING =====
LOG_LEVEL=INFO
LOG_FILE=dashboard.log
"""
    
    env_sample_file = Path('.env.sample')
    with open(env_sample_file, 'w') as f:
        f.write(sample_content)
    
    print(f"✅ Created sample configuration file: {env_sample_file}")
    print("📝 Next steps:")
    print("   1. Copy .env.sample to .env")
    print("   2. Edit .env with your iCloud email settings")
    print("   3. Get an iCloud App-Specific Password from appleid.apple.com")

    from bokeh.models import DatetimeTickFormatter

def apply_datetime_formatter(plot, element):
    """
    A Bokeh hook that forces the X axis to stay as real datetimes.
    """
    plot.handles['xaxis'].formatter = DatetimeTickFormatter(
        hours="%H:%M", days="%H:%M", months="%b %d", years="%Y"
    )

from bokeh.models import PrintfTickFormatter

def apply_numeric_yaxis_formatter(plot, element):
    """
    Forces the LEFT (generation) axis to use integer formatting.
    """
    plot.handles['yaxis'].formatter = PrintfTickFormatter(format="%.0f")

class EnergyDashboard(param.Parameterized):
    """
    Real-time energy generation dashboard with HvPlot
    """
    
    # Parameters for user controls
    region = param.Selector(
        default='NEM',
        objects=['NEM', 'NSW1', 'QLD1', 'SA1', 'TAS1', 'VIC1'],
        doc="Select region to display"
    )
    
    
    def __init__(self, **params):
        super().__init__(**params)
        self.gen_info_df = None
        self.gen_output_df = None
        self.duid_to_fuel = {}
        self.duid_to_region = {}
        self.last_update = None
        self.update_task = None
        self.hours = 24  # Fixed 24 hours
        self._plot_objects = {}  # Cache for plot objects
        
        # Initialize email alert manager
        self.email_manager = EmailAlertManager()
        
        # Load initial data
        self.load_reference_data()
        
        # Create the initial plot panes with proper initialization
        self.plot_pane = None
        self.utilization_pane = None
        self.main_content = None
        self.update_time_display = None
        # Track unknown DUIDs for session reporting
        self.session_unknown_duids = set()
        # Initialize panes
        self._initialize_panes()
        
    def _initialize_panes(self):
        """Initialize plot panes with proper document handling"""
        try:
            # Create fresh plots for initialization
            gen_plot = self.create_plot()
            util_plot = self.create_utilization_plot()
            
            # Create panes with explicit sizing
            self.plot_pane = pn.pane.HoloViews(
                gen_plot,
                sizing_mode='stretch_width',
                height=600,
                margin=(5, 5)
            )
            
            self.utilization_pane = pn.pane.HoloViews(
                util_plot,
                sizing_mode='stretch_width',
                height=500,
                margin=(5, 5)
            )
            
            # Set initial visibility
            self.plot_pane.visible = True
            self.utilization_pane.visible = True
            
        except Exception as e:
            logger.error(f"Error initializing panes: {e}")
            # Create fallback empty panes
            self.plot_pane = pn.pane.HTML("Loading generation chart...", height=600)
            self.utilization_pane = pn.pane.HTML("Loading utilization chart...", height=500)
        
    def load_reference_data(self):
        """Load DUID to fuel/region mapping from gen_info.pkl"""
        try:
            if os.path.exists(GEN_INFO_FILE):
                with open(GEN_INFO_FILE, 'rb') as f:
                    self.gen_info_df = pickle.load(f)
                
                # Create mapping dictionaries
                self.duid_to_fuel = dict(zip(self.gen_info_df['DUID'], self.gen_info_df['Fuel']))
                self.duid_to_region = dict(zip(self.gen_info_df['DUID'], self.gen_info_df['Region']))
                
                logger.info(f"Loaded {len(self.gen_info_df)} DUID mappings")
                logger.info(f"Fuel types: {self.gen_info_df['Fuel'].unique()}")
                
            else:
                logger.error(f"gen_info.pkl not found at {GEN_INFO_FILE}")
                
        except Exception as e:
            logger.error(f"Error loading gen_info.pkl: {e}")
    
    def load_duid_exception_list(self):
        """Load the list of DUIDs to ignore for email alerts"""
        exception_file = config.data_dir / "duid_exceptions.json"
        try:
            if exception_file.exists():
                with open(exception_file, 'r') as f:
                    data = json.load(f)
                    # Return as a set for fast lookup
                    return set(data.get('exception_duids', []))
            else:
                return set()
        except Exception as e:
            logger.error(f"Error loading DUID exception list: {e}")
            return set()
    
    def save_duid_exception_list(self, exception_duids):
        """Save the list of DUIDs to ignore for email alerts"""
        exception_file = config.data_dir / "duid_exceptions.json"
        try:
            # Convert set to list for JSON serialization
            data = {
                'exception_duids': sorted(list(exception_duids)),
                'last_updated': datetime.now().isoformat(),
                'note': 'DUIDs in this list will not trigger email alerts'
            }
            with open(exception_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(exception_duids)} DUIDs to exception list")
        except Exception as e:
            logger.error(f"Error saving DUID exception list: {e}")
    
    def add_duids_to_exception_list(self, duids_to_add):
        """Add DUIDs to the exception list"""
        current_exceptions = self.load_duid_exception_list()
        current_exceptions.update(duids_to_add)
        self.save_duid_exception_list(current_exceptions)
        logger.info(f"Added {len(duids_to_add)} DUIDs to exception list")
    
    def handle_unknown_duids(self, unknown_duids, df):
        """Handle unknown DUIDs - log and potentially send alerts"""
        
        # Load exception list
        exception_duids = self.load_duid_exception_list()
        
        # Filter out DUIDs that are in the exception list
        new_unknown_duids = unknown_duids - exception_duids
        known_exception_duids = unknown_duids & exception_duids
        
        # Always log the issue
        logger.warning(f"🚨 Found {len(unknown_duids)} unknown DUIDs not in gen_info.pkl:")
        logger.warning(f"   - {len(new_unknown_duids)} are NEW (will trigger email if enabled)")
        logger.warning(f"   - {len(known_exception_duids)} are in exception list (no email)")
        
        for duid in sorted(unknown_duids):
            # Get some sample data for this DUID
            duid_data = df[df['duid'] == duid]
            if not duid_data.empty:
                sample = duid_data.iloc[-1]  # Most recent record
                exception_flag = " [EXCEPTION LIST]" if duid in exception_duids else " [NEW]"
                logger.warning(f"  - {duid}: {sample['scadavalue']:.1f} MW at {sample['settlementdate']}{exception_flag}")
            else:
                logger.warning(f"  - {duid}: No data found")
        
        # Only send email for new unknown DUIDs not in exception list
        if new_unknown_duids:
            # Check if email alerts are enabled
            if os.getenv('ENABLE_EMAIL_ALERTS', 'true').lower() == 'true':
                if self.should_send_email_alert(new_unknown_duids):
                    self.send_unknown_duid_email(new_unknown_duids, df)
                    
                    # After sending email, optionally add these to exception list
                    # to prevent repeated emails about the same DUIDs
                    if os.getenv('AUTO_ADD_TO_EXCEPTIONS', 'true').lower() == 'true':
                        self.add_duids_to_exception_list(new_unknown_duids)
                        logger.info("Auto-added alerted DUIDs to exception list")
            else:
                logger.info(f"Email alerts disabled - would have alerted about {len(new_unknown_duids)} new DUIDs")

    def should_send_email_alert(self, unknown_duids):
        """Check if we should send an email alert (rate limiting)"""
        # Load cache of previously alerted DUIDs
        cache_file = BASE_PATH / "unknown_duids_alerts.json"
        alert_cache = {}
        
        try:
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    alert_cache = json.load(f)
        except Exception as e:
            logger.error(f"Error loading alert cache: {e}")
        
        # Check if any DUID needs alerting (hasn't been alerted in last 24 hours)
        now = datetime.now()
        duids_needing_alert = []
        
        for duid in unknown_duids:
            if duid not in alert_cache:
                duids_needing_alert.append(duid)
            else:
                last_alert = datetime.fromisoformat(alert_cache[duid])
                if (now - last_alert).total_seconds() > 24 * 3600:  # 24 hours
                    duids_needing_alert.append(duid)
        
        if duids_needing_alert:
            # Update cache for DUIDs we're about to alert
            for duid in duids_needing_alert:
                alert_cache[duid] = now.isoformat()
            
            # Save updated cache
            try:
                with open(cache_file, 'w') as f:
                    json.dump(alert_cache, f, indent=2, default=str)
            except Exception as e:
                logger.error(f"Error saving alert cache: {e}")
            
            return True
        
        return False

    def send_unknown_duid_email(self, unknown_duids, df):
        """Send email alert about unknown DUIDs"""
        try:
            # Email configuration - use environment variables
            sender_email = os.getenv('ALERT_EMAIL')
            sender_password = os.getenv('ALERT_PASSWORD') 
            recipient_email = os.getenv('RECIPIENT_EMAIL', sender_email)
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.mail.me.com')  # Default to iCloud
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            
            if not all([sender_email, sender_password]):
                logger.error("Email credentials not configured. Set ALERT_EMAIL and ALERT_PASSWORD environment variables.")
                return
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"⚠️ Unknown DUIDs in Energy Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Create email body
            body = self.create_alert_email_body(unknown_duids, df)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email using configured SMTP server
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email alert sent for {len(unknown_duids)} unknown DUIDs via {smtp_server}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send email alert: {e}")

    def create_alert_email_body(self, unknown_duids, df):
        """Create HTML email body"""
        # Get sample data for each unknown DUID
        duid_samples = []
        for duid in sorted(unknown_duids)[:10]:  # Limit to 10 for email size
            duid_data = df[df['duid'] == duid]
            if not duid_data.empty:
                sample = duid_data.iloc[-1]
                duid_samples.append({
                    'duid': duid,
                    'power': sample['scadavalue'],
                    'time': sample['settlementdate'],
                    'records': len(duid_data)
                })
        
        # Build HTML
        samples_html = ""
        for sample in duid_samples:
            samples_html += f"""
            <tr>
                <td>{sample['duid']}</td>
                <td>{sample['power']:.1f} MW</td>
                <td>{sample['time']}</td>
                <td>{sample['records']}</td>
            </tr>
            """
        
        body = f"""
        <html>
        <body>
            <h2>🚨 Unknown DUIDs Detected</h2>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Found <strong>{len(unknown_duids)} unknown DUID(s)</strong> not in gen_info.pkl</p>
            
            <h3>Sample Data:</h3>
            <table border="1" style="border-collapse: collapse;">
            <tr>
                <th>DUID</th>
                <th>Latest Power</th>
                <th>Latest Time</th>
                <th>Records (24h)</th>
            </tr>
            {samples_html}
            </table>
            
            <h3>Action Required:</h3>
            <ul>
                <li>Update gen_info.pkl with new DUID information</li>
                <li>Check AEMO data sources for DUID details</li>
                <li>Verify these are legitimate new generation units</li>
            </ul>
            
            <p><em>All unknown DUIDs: {', '.join(sorted(unknown_duids))}</em></p>
        </body>
        </html>
        """
        return body
    
    def load_generation_data(self):
        """Enhanced version that checks for unknown DUIDs and sends alerts"""
        try:
            if os.path.exists(GEN_OUTPUT_FILE):
                # Calculate time window - fixed 24 hours
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=self.hours)
                
                # Load parquet file
                df = pd.read_parquet(GEN_OUTPUT_FILE)
                
                # Filter to time window
                df = df[df['settlementdate'] >= start_time]
                
                # *** NEW: CHECK FOR UNKNOWN DUIDs BEFORE MAPPING ***
                all_duids_in_data = set(df['duid'].unique())
                known_duids = set(self.duid_to_fuel.keys())
                unknown_duids = all_duids_in_data - known_duids
                
                # Log and potentially alert about unknown DUIDs
                if unknown_duids:
                    self.handle_unknown_duids(unknown_duids, df)
                
                # Add fuel and region information
                df['fuel'] = df['duid'].map(self.duid_to_fuel)
                df['region'] = df['duid'].map(self.duid_to_region)
                
                # Log how much data is being dropped
                original_count = len(df)
                df = df.dropna(subset=['fuel', 'region'])
                dropped_count = original_count - len(df)
                
                if dropped_count > 0:
                    logger.warning(f"Dropped {dropped_count} records ({dropped_count/original_count*100:.1f}%) due to unknown DUIDs")
                
                self.gen_output_df = df
                logger.info(f"Loaded {len(df)} generation records for last {self.hours} hours")
                
            else:
                logger.error(f"gen_output.parquet not found at {GEN_OUTPUT_FILE}")
                self.gen_output_df = pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error loading generation data: {e}")
            self.gen_output_df = pd.DataFrame()

    def load_price_data(self):
        """Load and process price data from parquet file"""
        try:
            price_file = config.spot_hist_file
            
            if not os.path.exists(price_file):
                logger.error(f"Price data file not found at {price_file}")
                return pd.DataFrame()
            
            # Calculate time window - same as generation data (24 hours)
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=self.hours)
            
            # Load parquet file
            df = pd.read_parquet(price_file)
            
            # Debug: Check the structure
            logger.info(f"Price data columns: {df.columns.tolist()}")
            logger.info(f"Price data index: {df.index.name}")
            logger.info(f"Price data shape: {df.shape}")
            logger.info(f"Price data dtypes:\n{df.dtypes}")
            
            # Check if SETTLEMENTDATE is the index
            if df.index.name == 'SETTLEMENTDATE':
                # Reset index to make SETTLEMENTDATE a regular column
                df = df.reset_index()
                logger.info("Reset index - SETTLEMENTDATE is now a column")
            
            # Now check columns again
            logger.info(f"Columns after reset_index: {df.columns.tolist()}")
            
            # Verify we have the required columns
            required_cols = ['SETTLEMENTDATE', 'RRP', 'REGIONID']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                logger.error(f"Missing required columns: {missing_cols}")
                return pd.DataFrame()
            
            # Convert settlement date if it's not already datetime
            if not pd.api.types.is_datetime64_any_dtype(df['SETTLEMENTDATE']):
                df['SETTLEMENTDATE'] = pd.to_datetime(df['SETTLEMENTDATE'])
            
            # Filter to time window
            df = df[df['SETTLEMENTDATE'] >= start_time]
            logger.info(f"Price data shape after time filtering: {df.shape}")
            
            # Filter by region
            if self.region != 'NEM':
                df = df[df['REGIONID'] == self.region]
            else:
                # For NEM, use NSW1 as representative (or you could average all regions)
                df = df[df['REGIONID'] == 'NSW1']
            
            logger.info(f"Price data shape after region filtering: {df.shape}")
            logger.info(f"Available regions in data: {df['REGIONID'].unique()}")
            
            # Ensure data is sorted by time
            df = df.sort_values('SETTLEMENTDATE')
            
            # Handle missing data by interpolating
            if not df.empty:
                # Create a clean dataframe with standardized column names
                clean_df = pd.DataFrame({
                    'settlementdate': df['SETTLEMENTDATE'],
                    'RRP': df['RRP']
                })
                
                # Set time as index for easier resampling/interpolation
                clean_df.set_index('settlementdate', inplace=True)
                
                # Resample to 5-minute intervals and interpolate missing values
                clean_df = clean_df.resample('5min').mean()
                clean_df['RRP'] = clean_df['RRP'].interpolate(method='linear')
                
                # Reset index to get settlementdate back as column
                clean_df = clean_df.reset_index()
                
                logger.info(f"Loaded {len(clean_df)} price records for last {self.hours} hours")
                if not clean_df.empty:
                    logger.info(f"Price range: ${clean_df['RRP'].min():.2f} to ${clean_df['RRP'].max():.2f}")
                    logger.info(f"Time range: {clean_df['settlementdate'].min()} to {clean_df['settlementdate'].max()}")
                
                return clean_df
                
            else:
                logger.warning("No price data found for the specified time window and region")
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error loading price data: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    
    def process_data_for_region(self):
        """Process generation data for selected region"""
        if self.gen_output_df is None or self.gen_output_df.empty:
            return pd.DataFrame()
        
        df = self.gen_output_df.copy()
        
        # Filter by region
        if self.region != 'NEM':
            df = df[df['region'] == self.region]
        
        # Group by time and fuel type
        df['settlementdate'] = pd.to_datetime(df['settlementdate'])
        
        # Aggregate by 5-minute intervals and fuel type
        result = df.groupby([
            pd.Grouper(key='settlementdate', freq='5min'),
            'fuel'
        ])['scadavalue'].sum().reset_index()
        
        # Pivot to get fuel types as columns
        pivot_df = result.pivot(index='settlementdate', columns='fuel', values='scadavalue')
        pivot_df = pivot_df.fillna(0)
        
        # Define preferred fuel order (Battery Storage first as it can be negative)
        preferred_order = [
            'Battery Storage',  # First - can be negative
            'Solar', 
            'Wind', 
            'Other', 
            'Coal', 
            'CCGT', 
            'Gas other', 
            'OCGT', 
            'Water'
        ]
        
        # Reorder columns based on preferred order, only including columns that exist
        available_fuels = [fuel for fuel in preferred_order if fuel in pivot_df.columns]
        
        # Add any remaining fuels not in the preferred order
        remaining_fuels = [col for col in pivot_df.columns if col not in available_fuels]
        final_order = available_fuels + remaining_fuels
        
        # Reorder the dataframe
        pivot_df = pivot_df[final_order]
        
        return pivot_df
    
    def calculate_capacity_utilization(self):
        """Calculate capacity utilization by fuel type for selected region"""
        if self.gen_output_df is None or self.gen_output_df.empty:
            return pd.DataFrame()
        
        df = self.gen_output_df.copy()
        
        # Filter by region
        if self.region != 'NEM':
            df = df[df['region'] == self.region]
        
        # Group generation by time and fuel type
        df['settlementdate'] = pd.to_datetime(df['settlementdate'])
        
        # Aggregate generation by 5-minute intervals and fuel type
        generation = df.groupby([
            pd.Grouper(key='settlementdate', freq='5min'),
            'fuel'
        ])['scadavalue'].sum().reset_index()
        
        # Get capacity data by fuel type for the region
        capacity_df = self.gen_info_df.copy()
        if self.region != 'NEM':
            capacity_df = capacity_df[capacity_df['Region'] == self.region]
        
        # Clean and convert capacity data - handle string ranges and non-numeric values
        def clean_capacity(capacity):
            if pd.isna(capacity):
                return 0
            if isinstance(capacity, str):
                # Handle range strings like "23.44 - 27.60"
                if ' - ' in capacity:
                    try:
                        # Take the average of the range
                        parts = capacity.split(' - ')
                        return (float(parts[0]) + float(parts[1])) / 2
                    except ValueError:
                        return 0
                else:
                    try:
                        return float(capacity)
                    except ValueError:
                        return 0
            try:
                return float(capacity)
            except (ValueError, TypeError):
                return 0
        
        capacity_df['Clean_Capacity'] = capacity_df['Capacity(MW)'].apply(clean_capacity)
        
        # Sum capacity by fuel type using the cleaned capacity
        fuel_capacity = capacity_df.groupby('Fuel')['Clean_Capacity'].sum()
        
        # Debug: Log capacity data for troubleshooting
        logger.info(f"Fuel capacities for {self.region}: {fuel_capacity.to_dict()}")
        
        # Calculate utilization for each time period and fuel
        utilization_data = []
        for _, row in generation.iterrows():
            fuel = row['fuel']
            if fuel in fuel_capacity.index and fuel_capacity[fuel] > 0:
                generation_mw = row['scadavalue']
                capacity_mw = fuel_capacity[fuel]
                utilization = (generation_mw / capacity_mw) * 100
                
                # Debug logging for first few calculations
                if len(utilization_data) < 5:
                    logger.info(f"Fuel: {fuel}, Generation: {generation_mw:.2f} MW, Capacity: {capacity_mw:.2f} MW, Utilization: {utilization:.2f}%")
                
                # Cap at 100% to handle any data anomalies and negative values
                utilization = max(0, min(utilization, 100))
                utilization_data.append({
                    'settlementdate': row['settlementdate'],
                    'fuel': fuel,
                    'utilization': utilization
                })
        
        if not utilization_data:
            logger.warning("No utilization data calculated")
            return pd.DataFrame()
        
        utilization_df = pd.DataFrame(utilization_data)
        
        # Debug: Check the raw utilization values
        logger.info(f"Sample utilization values: {utilization_df['utilization'].head().tolist()}")
        
        # Pivot to get fuel types as columns
        pivot_df = utilization_df.pivot(index='settlementdate', columns='fuel', values='utilization')
        pivot_df = pivot_df.fillna(0)
        
        # Additional safety: ensure all values are between 0 and 100
        pivot_df = pivot_df.clip(lower=0, upper=100)
        
        # Debug: Check final pivot values
        logger.info(f"Final pivot data shape: {pivot_df.shape}")
        logger.info(f"Final pivot max values: {pivot_df.max().to_dict()}")
        
        return pivot_df
    
    def get_fuel_colors(self):
        """Define colors for different fuel types - all distinct and visually clear"""
        fuel_colors = {
            'Coal': '#4a4a4a',        # Dark gray - distinctive for coal
            'CCGT': '#ff5555',        # Bright red - gas turbine
            'OCGT': '#ff8c42',        # Orange-red - different gas turbine type
            'Gas other': '#ff9500',   # Pure orange - clearly different from yellow
            'Solar': '#ffd700',       # Gold/bright yellow - sunny color
            'Wind': '#00bfff',        # Sky blue - wind/air
            'Water': '#00ff7f',       # Spring green - water/hydro
            'Battery Storage': '#9370db',  # Medium purple - technology
            'Biomass': '#8b4513',     # Saddle brown - organic/wood
            'Other': '#ff69b4'        # Hot pink - catch-all category
        }
        return fuel_colors
    
    

    def create_plot(self):
        """Create the HvPlot visualization with generation and price charts stacked vertically"""
        try:
            # Load fresh data
            self.load_generation_data()
            data = self.process_data_for_region()
            
            if data.empty:
                # Create empty plot with message
                empty_plot = hv.Text(0.5, 0.5, 'No data available').opts(
                    xlim=(0, 1),
                    ylim=(0, 1),
                    bgcolor='black',
                    width=900,
                    height=400,
                    color='white',
                    fontsize=16
                )
                return empty_plot
            
            # Get colors
            fuel_colors = self.get_fuel_colors()
            
            # Use all available fuel types in the order they appear (already sorted)
            fuel_types = list(data.columns)
            
            if not fuel_types:
                # Fallback empty plot
                return hv.Text(0.5, 0.5, 'No generation data for selected region').opts(
                    bgcolor='black',
                    color='white',
                    fontsize=14
                )
            
            # Create stacked area plot with special handling for negative battery values
            plot_data = data[fuel_types].copy().reset_index()
            
            # Check if Battery Storage exists and has negative values
            battery_col = 'Battery Storage'
            has_battery = battery_col in plot_data.columns
            
            if has_battery and (plot_data[battery_col] < 0).any():
                # Split battery data for proper color handling
                battery_data = plot_data[battery_col].copy()
                
                # Create separate datasets for positive and negative battery values
                plot_data_positive = plot_data.copy()
                plot_data_positive[battery_col] = battery_data.where(battery_data >= 0, 0)  # Only positive values
                
                plot_data_negative = plot_data[['settlementdate', battery_col]].copy()
                plot_data_negative[battery_col] = battery_data.where(battery_data < 0, 0)   # Only negative values
                
                # Create the main stacked area plot (without negative battery values)
                main_plot = plot_data_positive.hvplot.area(
                    x='settlementdate',
                    y=fuel_types,
                    stacked=True,
                    width=900,
                    height=300,  # Reduced height to make room for price chart
                    ylabel='Generation (MW)',
                    xlabel='',  # Remove x-label since it will be on the price chart
                    grid=True,
                    legend='right',
                    bgcolor='black',
                    color=[fuel_colors.get(fuel, '#6272a4') for fuel in fuel_types],
                    alpha=0.8,
                    hover=True,
                    hover_tooltips=[('Fuel Type', '$name')]
                )
                
                # Create the negative battery area plot
                battery_color = fuel_colors.get('Battery Storage', '#9370db')
                negative_plot = plot_data_negative.hvplot.area(
                    x='settlementdate',
                    y=[battery_col],
                    width=900,
                    height=300,  # Match main plot height
                    color=battery_color,
                    alpha=0.8,
                    hover=True,
                    hover_tooltips=[('Fuel Type', battery_col)],
                    legend=False  # Don't show legend for negative part
                )
                
                # Combine both plots
                area_plot = (main_plot * negative_plot).opts(
                    title=f'Generation by Fuel Type - {self.region} (Updated: {datetime.now().strftime("%H:%M:%S")}) | data:AEMO, design ITK',
                    show_grid=True,
                    bgcolor='black',
                    xaxis=None  # Hide x-axis since price chart will show it
                )
                
            else:
                # No negative battery values, use simple stacked area with attribution in title
                area_plot = plot_data.hvplot.area(
                    x='settlementdate',
                    y=fuel_types,
                    stacked=True,
                    width=900,
                    height=300,  # Reduced height to make room for price chart
                    title=f'Generation by Fuel Type - {self.region} (Updated: {datetime.now().strftime("%H:%M:%S")}) | data:AEMO, design ITK',
                    ylabel='Generation (MW)',
                    xlabel='',  # Remove x-label since it will be on the price chart
                    grid=True,
                    legend='right',
                    bgcolor='black',
                    color=[fuel_colors.get(fuel, '#6272a4') for fuel in fuel_types],
                    alpha=0.8,
                    hover=True,
                    hover_tooltips=[('Fuel Type', '$name')]
                ).opts(
                    show_grid=True,
                    bgcolor='black',
                    xaxis=None  # Hide x-axis since price chart will show it
                )
            
            # Load and create price chart
            price_df = self.load_price_data()
            
            if price_df.empty:
                # If no price data, return just the generation plot with x-axis restored
                return area_plot.opts(xaxis='bottom', xlabel='Time')
            
            # Create price line chart
            price_plot = price_df.hvplot.line(
                x='settlementdate',
                y='RRP',
                width=900,
                height=250,  # Smaller height - about half of generation chart
                ylabel='Price ($/MWh)',
                xlabel='Time',
                grid=True,
                bgcolor='black',
                color='white',
                line_width=2,
                alpha=0.8,
                hover=True,
                hover_tooltips=[('Price', '@RRP{$0.2f}')]
            ).opts(
                show_grid=True,
                bgcolor='black'
            )
            
            # Stack the plots vertically using Layout
            # The plots will share the same x-axis range automatically
            combined_layout = (area_plot + price_plot).cols(1).opts(
                shared_axes=True,  # This ensures x-axes are linked
                merge_tools=True   # Merge toolbars into a single toolbar
            )
            
            self.last_update = datetime.now()
            logger.info(f"Plot updated for {self.region}, {self.hours} hours")
            
            return combined_layout
            
        except Exception as e:
            logger.error(f"Error creating plot: {e}")
            # Return fallback plot
            return hv.Text(0.5, 0.5, f'Error creating plot: {str(e)}').opts(
                bgcolor='black',
                color='red',
                fontsize=12
            )
    
    

    
    
    def create_utilization_plot(self):
        """Create capacity utilization line chart with proper document handling"""
        try:
            utilization_data = self.calculate_capacity_utilization()
            
            if utilization_data.empty:
                # Create empty plot with message
                empty_plot = hv.Text(0.5, 0.5, 'No utilization data available').opts(
                    xlim=(0, 1),
                    ylim=(0, 1),
                    bgcolor='black',
                    width=900,
                    height=400,
                    color='white',
                    fontsize=14
                )
                return empty_plot
            
            # Get colors (same as generation chart for consistency)
            fuel_colors = self.get_fuel_colors()
            
            # Reset index to make time a column
            plot_data = utilization_data.reset_index()
            
            # Get available fuel types
            fuel_types = [col for col in utilization_data.columns if col in fuel_colors]
            
            if not fuel_types:
                return hv.Text(0.5, 0.5, 'No fuel data for utilization chart').opts(
                    bgcolor='black',
                    color='white',
                    fontsize=14
                )
            
            # Create line plot for capacity utilization with different Y dimension name
            line_plot = plot_data.hvplot.line(
                x='settlementdate',
                y=fuel_types,
                width=900,
                height=400,
                title=f'Capacity Utilization by Fuel Type - {self.region} (Updated: {datetime.now().strftime("%H:%M:%S")}) | data:AEMO, design ITK',
                ylabel='Capacity Utilization (%)',
                xlabel='Time',
                grid=False,
                legend='right',
                bgcolor='black',
                color=[fuel_colors.get(fuel, '#6272a4') for fuel in fuel_types],
                alpha=0.8,
                hover=True,
                hover_tooltips=[('Fuel Type', '$name'), ('Utilization', '@$name{0.1f}%')],
                ylim=(0, 100)  # Force Y-axis to 0-100%
            ).opts(
                show_grid=False,
                toolbar='above',
                bgcolor='black',
                ylim=(0, 100),  # Double ensure Y-axis range
                yformatter='%.0f%%'  # Format Y-axis as percentage
            )
            
            # Rename the Y dimension to make it independent from generation MW axis
            line_plot = line_plot.redim(**{fuel: f'{fuel}_utilization' for fuel in fuel_types})
            
            return line_plot
            
        except Exception as e:
            logger.error(f"Error creating utilization plot: {e}")
            # Return fallback plot
            return hv.Text(0.5, 0.5, f'Error creating utilization plot: {str(e)}').opts(
                bgcolor='black',
                color='red',
                fontsize=12
            )
    
    def update_plot(self):
        """Update both plots with fresh data and proper error handling"""
        try:
            logger.info("Starting plot update...")
            
            # Create new plots
            new_generation_plot = self.create_plot()
            new_utilization_plot = self.create_utilization_plot()
            
            # Safely update the panes
            if self.plot_pane is not None:
                self.plot_pane.object = new_generation_plot
            
            if self.utilization_pane is not None:
                self.utilization_pane.object = new_utilization_plot
            
            # Update the time display
            if self.update_time_display is not None:
                self.update_time_display.object = f"<div style='text-align: center; color: white; font-size: 16px; margin: 10px 0;'>Last Updated: {datetime.now().strftime('%H:%M:%S')} | data:AEMO, design ITK</div>"
            
            logger.info("Plot update completed successfully")
            
        except Exception as e:
            logger.error(f"Error updating plots: {e}")
            # Don't crash the application, just log and continue
    
    async def auto_update_loop(self):
        """Automatic update loop every 4.5 minutes with better error handling"""
        while True:
            try:
                await asyncio.sleep(270)  # 4.5 minutes
                # Update plots in both tabs
                self.update_plot()
                logger.info("Auto-update completed")
            except asyncio.CancelledError:
                logger.info("Auto-update loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in auto-update loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def start_auto_update(self):
        """Start the auto-update task - only when event loop is running"""
        try:
            # Cancel existing task if running
            if self.update_task is not None and not self.update_task.done():
                self.update_task.cancel()
            
            # Start new task
            self.update_task = asyncio.create_task(self.auto_update_loop())
            logger.info("Auto-update started")
        except RuntimeError as e:
            # No event loop running yet - will start later
            logger.info(f"Event loop not ready - auto-update will start when served: {e}")
            pass
    
    @param.depends('region', watch=True)
    def on_region_change(self):
        """Called when region parameter changes"""
        logger.info(f"Region changed to: {self.region}")
        self.update_plot()
    
    
    def test_vol_price(self):
        """Test method to verify vol_price functionality"""
        try:
            print("Testing vol_price method...")
            
            # Test loading price data
            price_data = self.load_price_data()
            print(f"Price data loaded: {len(price_data)} records")
            if not price_data.empty:
                print(f"Price range: ${price_data['RRP'].min():.2f} to ${price_data['RRP'].max():.2f}")
                print(f"Time range: {price_data['settlementdate'].min()} to {price_data['settlementdate'].max()}")
            
            # Test loading generation data
            self.load_generation_data()
            gen_data = self.process_data_for_region()
            print(f"Generation data loaded: {len(gen_data)} records")
            if not gen_data.empty:
                print(f"Fuel types: {list(gen_data.columns)}")
                print(f"Generation range: {gen_data.sum(axis=1).min():.1f} to {gen_data.sum(axis=1).max():.1f} MW")
            
            # Test creating the combined plot
            plot = self.vol_price()
            print("Combined plot created successfully!")
            return plot
            
        except Exception as e:
            print(f"Error in test_vol_price: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_generation_tab(self):
        """Create the Generation by Fuel tab with left-side controls and right-side chart subtabs"""
        try:
            # Region selector for left side
            region_selector = pn.Param(
                self,
                parameters=['region'],
                widgets={'region': pn.widgets.Select},
                name="Region Selection",
                width=280,
                margin=(10, 0)
            )
            
            # Create left-side control panel
            control_panel = pn.Column(
                "### Generation by Fuel Controls",
                region_selector,
                pn.pane.Markdown("""
                **Region Options:**
                - **NEM:** All regions combined
                - **NSW1:** New South Wales  
                - **QLD1:** Queensland
                - **SA1:** South Australia
                - **TAS1:** Tasmania
                - **VIC1:** Victoria
                """),
                width=300,
                sizing_mode='fixed'
            )
            
            # Create subtabs for charts
            chart_subtabs = pn.Tabs(
                ("Generation Stack", pn.Column(
                    "#### Generation by Fuel Type",
                    self.plot_pane,
                    sizing_mode='stretch_width'
                )),
                ("Capacity Utilization", pn.Column(
                    "#### Capacity Utilization by Fuel",
                    self.utilization_pane,
                    sizing_mode='stretch_width'
                )),
                dynamic=True,
                sizing_mode='stretch_width'
            )
            
            # Create main layout with controls on left, charts on right
            generation_tab_layout = pn.Row(
                control_panel,
                chart_subtabs,
                sizing_mode='stretch_width'
            )
            
            return generation_tab_layout
            
        except Exception as e:
            logger.error(f"Error creating generation tab: {e}")
            return pn.pane.Markdown(f"**Error creating Generation tab:** {e}")

    def create_dashboard(self):
        """Create the complete dashboard with tabbed interface"""
        try:
            # Dashboard title with update time
            title = pn.pane.HTML(
                "<h1 style='color: white; margin: 10px 0 5px 0; text-align: center;'>Nem Analysis</h1>",
                sizing_mode='stretch_width'
            )
            
            # Update time display
            self.update_time_display = pn.pane.HTML(
                f"<div style='text-align: center; color: white; font-size: 16px; margin: 0 0 10px 0;'>Last Updated: {datetime.now().strftime('%H:%M:%S')} | data:AEMO, design ITK</div>",
                sizing_mode='stretch_width'
            )
            
            # Create tabs for different views
            # Generation tab with embedded region selector and subtabs
            generation_tab = self._create_generation_tab()
            
            # Price analysis tab
            try:
                logger.info("Creating price analysis tab...")
                price_analysis_tab = create_price_analysis_tab()
                logger.info("Price analysis tab created successfully")
            except Exception as e:
                logger.error(f"Error creating price analysis tab: {e}")
                price_analysis_tab = pn.pane.Markdown(f"**Error loading Price Analysis:** {e}")
            
            # Station analysis tab
            try:
                logger.info("Creating station analysis tab...")
                station_analysis_tab = create_station_analysis_tab()
                logger.info("Station analysis tab created successfully")
            except Exception as e:
                logger.error(f"Error creating station analysis tab: {e}")
                station_analysis_tab = pn.pane.Markdown(f"**Error loading Station Analysis:** {e}")
            
            # Create tabbed interface
            tabs = pn.Tabs(
                ("Generation by Fuel", generation_tab),
                ("Average Price Analysis", price_analysis_tab),
                ("Station Analysis", station_analysis_tab),
                dynamic=True,
                closable=False,
                sizing_mode='stretch_width'
            )
            
            # Complete dashboard layout
            dashboard = pn.Column(
                title,
                self.update_time_display,
                pn.pane.HTML("<div style='height: 10px;'></div>"),
                tabs,
                sizing_mode='stretch_width'
            )
            
            # Initialize plots for both tabs
            self.update_plot()
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            # Return error message dashboard
            return pn.pane.HTML(f"<h1>Error creating dashboard: {str(e)}</h1>", 
                              sizing_mode='stretch_width')

def create_app():
    """Create the Panel application with proper session handling"""
    def _create_dashboard():
        """Factory function to create a new dashboard instance per session"""
        try:
            # Create dashboard instance
            dashboard = EnergyDashboard()
            
            # Create the app
            app = dashboard.create_dashboard()
            
            # Start auto-update for this session
            def start_dashboard_updates():
                try:
                    dashboard.start_auto_update()
                except Exception as e:
                    logger.error(f"Error starting dashboard updates: {e}")
            
            # Hook into Panel's server startup
            pn.state.onload(start_dashboard_updates)
            
            return app
            
        except Exception as e:
            logger.error(f"Error creating app: {e}")
            return pn.pane.HTML(f"<h1>Application Error: {str(e)}</h1>")
    
    return _create_dashboard

def main():
    """Enhanced main function with configuration management"""
    
    # Check for command line arguments FIRST
    if len(sys.argv) > 1:
        if sys.argv[1] == '--create-config':
            create_sample_env_file()
            return  # Exit after creating config
        elif sys.argv[1] == '--help':
            print("Energy Dashboard Utilities:")
            print("  --create-config   Create sample .env file")
            print("  --help           Show this help")
            print("  (no args)        Start dashboard server")
            return
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for available options")
            return
    
    # Load environment variables if .env file exists
    env_file = Path('.env')
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded configuration from {env_file}")
    else:
        print("⚠️  No .env file found - using default settings")
        print("💡 Run 'python gen_dash.py --create-config' to create one")
    
    # Set Panel to dark theme globally
    pn.config.theme = 'dark'
    
    # Check if required files exist (your existing code)
    if not os.path.exists(GEN_INFO_FILE):
        print(f"Error: {GEN_INFO_FILE} not found")
        print("Please ensure gen_info.pkl exists in the specified location")
        return
    
    if not os.path.exists(GEN_OUTPUT_FILE):
        print(f"Error: {GEN_OUTPUT_FILE} not found")
        print("Please ensure gen_output.parquet exists in the specified location")
        return
    
    # Create the app factory (your existing code)
    app_factory = create_app()
    
    print("Starting Interactive Energy Generation Dashboard...")
    print("Navigate to: http://localhost:5010")
    print("Press Ctrl+C to stop the server")
    
    # Serve the app with dark theme and proper session handling
    pn.serve(
        app_factory, 
        port=5010, 
        allow_websocket_origin=["localhost:5010", "nemgen.itkservices2.com"],
        show=True,
        autoreload=False,  # Disable autoreload in production
        threaded=True     # Enable threading for better concurrent handling
    )

if __name__ == "__main__":
    main()