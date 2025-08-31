"""
Vehicle control panel widget
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QPushButton, 
                           QListWidget)
from PyQt5.QtCore import Qt

class VehicleControlPanel(QWidget):
    """Control panel for vehicle tracking"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Vehicle toggles
        vehicle_group = QGroupBox("Vehicle Tracking")
        vehicle_layout = QVBoxLayout(vehicle_group)
        
        self.drone_toggle = QPushButton("🚁 Track Drone")
        self.drone_toggle.setCheckable(True)
        self.drone_toggle.setChecked(True)
        
        self.etruck_toggle = QPushButton("🔋 Track E-Truck")
        self.etruck_toggle.setCheckable(True)
        self.etruck_toggle.setChecked(True)
        
        self.ftruck_toggle = QPushButton("🚚 Track Fuel Truck")
        self.ftruck_toggle.setCheckable(True)
        self.ftruck_toggle.setChecked(True)
        
        vehicle_layout.addWidget(self.drone_toggle)
        vehicle_layout.addWidget(self.etruck_toggle)
        vehicle_layout.addWidget(self.ftruck_toggle)
        
        # Status display
        status_group = QGroupBox("Vehicle Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_list = QListWidget()
        self.status_list.setMaximumHeight(200)
        status_layout.addWidget(self.status_list)
        
        # Map controls
        map_group = QGroupBox("Map Controls")
        map_layout = QVBoxLayout(map_group)
        
        self.show_noflyzone = QPushButton("🚫 Toggle No-Fly Zones")
        self.show_noflyzone.setCheckable(True)
        
        self.refresh_map = QPushButton("🔄 Refresh Map")
        
        map_layout.addWidget(self.show_noflyzone)
        map_layout.addWidget(self.refresh_map)
        
        layout.addWidget(vehicle_group)
        layout.addWidget(status_group)
        layout.addWidget(map_group)
        layout.addStretch()
    
    def update_vehicle_status(self, vehicle_data):
        """Update vehicle status in the list"""
        status_text = f"{vehicle_data.vehicle_type} ({vehicle_data.vehicle_id})\n"
        status_text += f"Status: {vehicle_data.status}\n"
        status_text += f"Speed: {vehicle_data.speed:.1f} km/h\n"
        status_text += f"Position: {vehicle_data.lat:.4f}, {vehicle_data.lon:.4f}"
        
        # Find existing item or create new
        for i in range(self.status_list.count()):
            item = self.status_list.item(i)
            if vehicle_data.vehicle_id in item.text():
                item.setText(status_text)
                return
        
        # Add new item
        self.status_list.addItem(status_text)