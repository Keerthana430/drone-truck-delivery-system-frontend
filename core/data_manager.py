"""
Data structures and data management for vehicle tracking and delivery system
"""
import sys
import time
import random
import math
import numpy as np
from collections import deque
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal

class VehicleData:
    """Data structure for vehicle information"""
    def __init__(self, vehicle_id, vehicle_type, lat, lon, status="Idle", speed=0):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.lat = lat
        self.lon = lon
        self.status = status
        self.speed = speed
        self.last_update = datetime.now()

class DeliveryPoint:
    """Data structure for delivery points"""
    def __init__(self, name, address, lat, lon, weight, distance=0):
        self.name = name
        self.address = address
        self.lat = lat
        self.lon = lon
        self.weight = weight
        self.distance = distance

class DataSimulator(QThread):
    """Simulates real-time vehicle and sensor data"""
    vehicle_updated = pyqtSignal(VehicleData)
    sound_data_updated = pyqtSignal(float, list)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        while self.running:
            # Simulate drone sound data
            sound_level = random.uniform(30, 60)  # dB levels
            time_series = [random.uniform(-1, 1) for _ in range(50)]  # Audio waveform
            self.sound_data_updated.emit(sound_level, time_series)
            
            time.sleep(1)  # Update every second
    
    def stop(self):
        self.running = False