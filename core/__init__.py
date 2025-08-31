"""
Core module for India Airspace Management System

This module contains the core business logic, data structures, 
and API handling functionality.
"""

from .data_manager import VehicleData, DeliveryPoint, DataSimulator
from .api_handler import RouteManager

__all__ = [
    'VehicleData',
    'DeliveryPoint', 
    'DataSimulator',
    'RouteManager'
]

__version__ = '1.0.0'