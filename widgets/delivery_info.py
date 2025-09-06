"""
Delivery information widget
"""
import math
import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QLabel, 
                           QListWidget, QGridLayout)
from PyQt5.QtCore import Qt
from core.data_manager import DeliveryPoint

class DeliveryInfoWidget(QWidget):
    """Display delivery points information - now with custom customer count"""
    def __init__(self, depot_coords=None, customer_count=5):
        super().__init__()
        self.depot_coords = depot_coords
        self.customer_count = customer_count
        self.init_ui()
        if depot_coords:
            self.setup_delivery_points()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Depot info
        depot_group = QGroupBox("Depot Information")
        depot_layout = QVBoxLayout(depot_group)
        
        self.depot_info = QLabel("No depot selected")
        self.depot_info.setStyleSheet("font-size: 12px; color: #ff6b35;")
        depot_layout.addWidget(self.depot_info)
        
        # Customer count info
        self.customer_info = QLabel(f"Customers: {self.customer_count}")
        self.customer_info.setStyleSheet("font-size: 12px; color: #8b5cf6; font-weight: bold;")
        depot_layout.addWidget(self.customer_info)
        
        info_group = QGroupBox("Delivery Information")
        info_layout = QVBoxLayout(info_group)
        
        self.delivery_list = QListWidget()
        info_layout.addWidget(self.delivery_list)
        
        # Summary
        summary_group = QGroupBox("Summary")
        summary_layout = QGridLayout(summary_group)
        
        self.total_points = QLabel("0")
        self.total_weight = QLabel("0.0 kg")
        self.total_distance = QLabel("0.0 km")
        
        summary_layout.addWidget(QLabel("Total Points:"), 0, 0)
        summary_layout.addWidget(self.total_points, 0, 1)
        summary_layout.addWidget(QLabel("Total Weight:"), 1, 0)
        summary_layout.addWidget(self.total_weight, 1, 1)
        summary_layout.addWidget(QLabel("Total Distance:"), 2, 0)
        summary_layout.addWidget(self.total_distance, 2, 1)
        
        
        layout.addWidget(info_group)
        layout.addWidget(summary_group)
    
    def update_depot(self, depot_coords, customer_count=None):
        """Update depot coordinates and customer count, regenerate delivery points"""
        self.depot_coords = depot_coords
        if customer_count is not None:
            self.customer_count = customer_count
            
        self.depot_info.setText(f"Depot: {depot_coords[0]:.4f}, {depot_coords[1]:.4f}")
        self.customer_info.setText(f"Customers: {self.customer_count}")
        self.setup_delivery_points()
        
    def setup_delivery_points(self):
        """Setup delivery points around the selected depot based on customer count"""
        if not self.depot_coords:
            return
            
        self.delivery_list.clear()
        
        # Generate delivery points around the depot (within 10-50km radius)
        delivery_points = []
        depot_lat, depot_lon = self.depot_coords
        
        for i in range(self.customer_count):  # Use customer_count instead of fixed number
            # Generate random points around depot
            angle = random.uniform(0, 360)
            distance_km = random.uniform(10, 50)  # 10-50 km from depot
            
            # Convert to lat/lon offset
            lat_offset = (distance_km / 111.32) * math.cos(math.radians(angle))
            lon_offset = (distance_km / (111.32 * math.cos(math.radians(depot_lat)))) * math.sin(math.radians(angle))
            
            point_lat = depot_lat + lat_offset
            point_lon = depot_lon + lon_offset
            
            point = DeliveryPoint(
                name=f"Customer {i+1}",
                address=f"Delivery Location {i+1} - {distance_km:.1f}km from depot",
                lat=point_lat,
                lon=point_lon,
                weight=random.uniform(1.0, 5.0),
                distance=distance_km
            )
            delivery_points.append(point)
        
        # Sort by distance
        delivery_points.sort(key=lambda p: p.distance)
        
        total_weight = 0
        total_distance = 0
        
        for point in delivery_points:
            item_text = f"{point.name}\n{point.address}\nWeight: {point.weight:.1f} kg\nDistance: {point.distance:.1f} km"
            self.delivery_list.addItem(item_text)
            total_weight += point.weight
            total_distance += point.distance
            
        self.total_points.setText(str(len(delivery_points)))
        self.total_weight.setText(f"{total_weight:.1f} kg")
        self.total_distance.setText(f"{total_distance:.1f} km")