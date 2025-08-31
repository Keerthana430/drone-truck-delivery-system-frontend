"""
Configuration module for India Airspace Management System

This module contains application settings, themes, and configuration constants.
"""

from .app_config import (
    DARK_STYLE,
    DEFAULT_DEPOT_COORDS,
    DEFAULT_CUSTOMER_COUNT,
    MAP_CENTER,
    MAP_ZOOM,
    DEFAULT_WAVES,
    PAUSE_BETWEEN_WAVES,
    VEHICLE_SPEEDS,
    VEHICLE_WEIGHTS,
    MAP_UPDATE_INTERVAL,
    SOUND_UPDATE_INTERVAL,
    DELIVERY_DISTANCE_MIN,
    DELIVERY_DISTANCE_MAX,
    MAX_CUSTOMERS,
    MIN_CUSTOMERS
)

__all__ = [
    'DARK_STYLE',
    'DEFAULT_DEPOT_COORDS', 
    'DEFAULT_CUSTOMER_COUNT',
    'MAP_CENTER',
    'MAP_ZOOM',
    'DEFAULT_WAVES',
    'PAUSE_BETWEEN_WAVES',
    'VEHICLE_SPEEDS',
    'VEHICLE_WEIGHTS',
    'MAP_UPDATE_INTERVAL',
    'SOUND_UPDATE_INTERVAL',
    'DELIVERY_DISTANCE_MIN',
    'DELIVERY_DISTANCE_MAX',
    'MAX_CUSTOMERS',
    'MIN_CUSTOMERS'
]

__version__ = '1.0.0'