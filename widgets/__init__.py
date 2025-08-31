"""
Widgets module for India Airspace Management System

This module contains all custom UI widgets including vehicle controls,
delivery information displays, and sound monitoring components.
"""

from .vehicle_control import VehicleControlPanel
from .delivery_info import DeliveryInfoWidget
from .sound_monitoring import SoundGraphWidget, NoiseStatisticsWidget

__all__ = [
    'VehicleControlPanel',
    'DeliveryInfoWidget',
    'SoundGraphWidget',
    'NoiseStatisticsWidget'
]

__version__ = '1.0.0'