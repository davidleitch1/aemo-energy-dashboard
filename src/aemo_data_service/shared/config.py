#!/usr/bin/env python3
"""
Configuration for AEMO Data Service
Shared configuration that can be imported by all collectors.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DataServiceConfig:
    """
    Configuration class for the AEMO Data Service.
    Centralizes all file paths, URLs, and settings.
    """
    
    # Base paths
    BASE_PATH = Path(os.getenv('BASE_PATH', 
        '/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/aemo-energy-dashboard/data'))
    
    # Ensure data directory exists
    BASE_PATH.mkdir(parents=True, exist_ok=True)
    
    # Data files
    gen_output_file = BASE_PATH / 'gen_output.parquet'
    gen_info_file = BASE_PATH / 'gen_info.pkl'  # Station info from AEMO
    spot_hist_file = BASE_PATH / 'spot_hist.parquet'
    rooftop_file = BASE_PATH / 'rooftop_actual.parquet'
    transmission_file = BASE_PATH / 'transmission_flows.parquet'
    
    # Update intervals (minutes)
    update_interval_minutes = float(os.getenv('UPDATE_INTERVAL_MINUTES', '4.5'))
    
    # AEMO URLs
    aemo_dispatch_url = "http://nemweb.com.au/Reports/CURRENT/Dispatch_IS/"
    aemo_scada_url = "http://nemweb.com.au/Reports/CURRENT/Dispatch_SCADA/"
    aemo_rooftop_url = "https://www.nemweb.com.au/Reports/Current/ROOFTOP_PV/ACTUAL/"
    aemo_transmission_url = "http://nemweb.com.au/Reports/CURRENT/Dispatch_IS/"
    
    # Logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = BASE_PATH.parent / 'logs' / 'data_service.log'
    
    # Email alerts (optional)
    enable_email_alerts = os.getenv('ENABLE_EMAIL_ALERTS', 'false').lower() == 'true'
    alert_email = os.getenv('ALERT_EMAIL', '')
    alert_password = os.getenv('ALERT_PASSWORD', '')
    recipient_email = os.getenv('RECIPIENT_EMAIL', '')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.mail.me.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    alert_cooldown_hours = int(os.getenv('ALERT_COOLDOWN_HOURS', '24'))
    
    # Service settings
    max_retries = int(os.getenv('MAX_RETRIES', '3'))
    timeout_seconds = int(os.getenv('TIMEOUT_SECONDS', '60'))
    
    # Performance settings
    concurrent_collectors = int(os.getenv('CONCURRENT_COLLECTORS', '4'))
    memory_limit_gb = float(os.getenv('MEMORY_LIMIT_GB', '8.0'))
    
    @classmethod
    def get_summary(cls) -> str:
        """Get a summary of the current configuration."""
        summary = "AEMO Data Service Configuration:\n"
        summary += f"  Base path: {cls.BASE_PATH}\n"
        summary += f"  Update interval: {cls.update_interval_minutes} minutes\n"
        summary += f"  Log file: {cls.log_file}\n"
        summary += f"  Email alerts: {cls.enable_email_alerts}\n"
        summary += f"  Max retries: {cls.max_retries}\n"
        summary += f"  Concurrent collectors: {cls.concurrent_collectors}\n"
        
        # Data files
        summary += "  Data files:\n"
        summary += f"    Generation: {cls.gen_output_file}\n"
        summary += f"    Prices: {cls.spot_hist_file}\n"
        summary += f"    Rooftop: {cls.rooftop_file}\n"
        summary += f"    Transmission: {cls.transmission_file}\n"
        
        return summary
    
    @classmethod
    def create_directories(cls):
        """Ensure all required directories exist."""
        cls.BASE_PATH.mkdir(parents=True, exist_ok=True)
        cls.log_file.parent.mkdir(parents=True, exist_ok=True)


# Create global config instance
config = DataServiceConfig()

# Ensure directories exist when module is imported
config.create_directories()