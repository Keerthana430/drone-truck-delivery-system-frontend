"""
Utilities module for India Airspace Management System

This module contains utility functions, data providers, and helper classes
for no-fly zone management and other system utilities.
"""

from .nfz_data import get_india_no_fly_zones, get_depot_selection_no_fly_zones

__all__ = [
    'get_india_no_fly_zones',
    'get_depot_selection_no_fly_zones'  
]

__version__ = '1.0.0'