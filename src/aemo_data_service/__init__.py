#!/usr/bin/env python3
"""
AEMO Data Service
Continuous data collection service for Australian Energy Market data.
"""

from .service import AEMODataService
from .shared.config import config
from .shared.logging_config import configure_service_logging, get_logger

__version__ = "1.0.0"
__author__ = "David Leitch"

# Convenience imports
from .collectors.generation_collector import GenerationCollector
from .collectors.price_collector import PriceCollector

__all__ = [
    'AEMODataService',
    'GenerationCollector', 
    'PriceCollector',
    'config',
    'configure_service_logging',
    'get_logger'
]