#!/usr/bin/env python3
"""
Logging configuration for AEMO Data Service
Provides consistent logging across all collectors.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from .config import config


def setup_logging(
    log_file: Optional[Path] = None,
    log_level: str = None,
    console_output: bool = True
) -> None:
    """
    Set up logging for the data service.
    
    Args:
        log_file: Path to log file (defaults to config.log_file)
        log_level: Logging level (defaults to config.log_level)
        console_output: Whether to also log to console
    """
    if log_file is None:
        log_file = config.log_file
    
    if log_level is None:
        log_level = config.log_level
    
    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Clear any existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler (optional)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Log configuration
    root_logger.info(f"Logging configured: level={log_level}, file={log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the logger (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Convenience function to set up service-wide logging
def configure_service_logging():
    """Configure logging for the entire data service."""
    setup_logging(
        log_file=config.log_file,
        log_level=config.log_level,
        console_output=True
    )
    
    logger = get_logger(__name__)
    logger.info("AEMO Data Service logging initialized")
    logger.info(config.get_summary())