"""
Main application window for India Airspace Management System
"""
import sys
import os
import json
import time
import math
import random
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QFrame, QToolBar, QAction, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QUrl, Qt
from PyQt5.QtGui import QFont, QIcon

# Import from other modules
from config.app_config import (DARK_STYLE, DEFAULT_DEPOT_COORDS, MAP_CENTER, MAP_ZOOM, 
                              DEFAULT_WAVES, PAUSE_BETWEEN_WAVES, VEHICLE_SPEEDS, VEHICLE_WEIGHTS)
from core.data_manager import VehicleData, DataSimulator
from core.api_handler import RouteManager
from widgets.vehicle_control import VehicleControlPanel
from widgets.delivery_info import DeliveryInfoWidget  
from widgets.sound_monitoring import SoundGraphWidget, NoiseStatisticsWidget
from utils.nfz_data import get_india_no_fly_zones
from resources.map_templates import HTML_TEMPLATE
from ui.dialog import DepotSelectionWindow

class IndiaAirspaceMap(QMainWindow):
    def __init__(self, depot_coords=None, customer_count=5):
        super().__init__()
        self.setWindowTitle("India Airspace Management - No-Fly Zones Map")
        self.setGeometry(50, 50, 1800, 1000)
        self.setMinimumSize(1600, 900)
        
        # Apply dark theme
        self.setStyleSheet(DARK_STYLE)
        
        # Store depot coordinates and customer count
        self.depot_coords = depot_coords or DEFAULT_DEPOT_COORDS
        self.customer_count = customer_count
        
        # India center coordinates for full country view
        self.map_center = MAP_CENTER
        self.map_zoom = MAP_ZOOM
        
        # Major No-fly zones across India
        self.no_fly_zones = get_india_no_fly_zones()
        
        # Vehicle system
        self.vehicles = {}
        self.waves = DEFAULT_WAVES
        self.pause_between_waves = PAUSE_BETWEEN_WAVES
        self.current_wave = 0
        self.wave_running = False
        self.wave_start_time = 0.0
        self.vehicles_started = False  # Track if vehicles are started
        
        # Generate delivery points around selected depot based on customer count
        self.delivery_points = self.generate_delivery_points_around_depot()
        
        self.map_ready = False
        self.setup_ui()
        self.setup_data_simulator()  # Add data simulator for sidebars
        self.create_map_file()
        
        # Movement timer - no map reload needed
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick_vehicle_movement)
        self.timer.start(500)  # Update every 500ms
        # ADD THIS LINE TO OPEN IN FULL SCREEN
        self.showMaximized()  # Opens maximized (recommended)
        
    def generate_delivery_points_around_depot(self):
        """Generate delivery points around the selected depot based on customer count"""
        points = []
        depot_lat, depot_lon = self.depot_coords
        
        for i in range(self.customer_count):  # Use customer_count instead of fixed number
            # Generate points in a rough circle around depot
            angle = (i * (360 / self.customer_count)) + random.uniform(-20, 20)  # Distribute evenly with some randomness
            distance_km = random.uniform(15, 45)  # 15-45 km from depot
            
            # Convert to lat/lon offset
            lat_offset = (distance_km / 111.32) * math.cos(math.radians(angle))
            lon_offset = (distance_km / (111.32 * math.cos(math.radians(depot_lat)))) * math.sin(math.radians(angle))
            
            point_lat = depot_lat + lat_offset
            point_lon = depot_lon + lon_offset
            
            points.append([point_lat, point_lon])
            
        return points
        
    def setup_ui(self):
        """Setup UI with sidebar layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with sidebars
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Left sidebar (300px width)
        left_panel = QFrame()
        left_panel.setMaximumWidth(300)
        left_panel.setMinimumWidth(250)
        left_layout = QVBoxLayout(left_panel)
        
        # Logo/Title
        title_label = QLabel("India Airspace")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff6b35; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Depot and customer info
        depot_info = QLabel(f"Depot: {self.depot_coords[0]:.4f}, {self.depot_coords[1]:.4f}")
        depot_info.setStyleSheet("font-size: 12px; color: #cccccc; padding: 5px; text-align: center;")
        depot_info.setAlignment(Qt.AlignCenter)
        
        customer_info = QLabel(f"Customers: {self.customer_count}")
        customer_info.setStyleSheet("font-size: 12px; color: #8b5cf6; font-weight: bold; padding: 5px; text-align: center;")
        customer_info.setAlignment(Qt.AlignCenter)
        
        # Control panels
        self.vehicle_control = VehicleControlPanel()
        self.delivery_info = DeliveryInfoWidget(self.depot_coords, self.customer_count)
        
        left_layout.addWidget(title_label)
        left_layout.addWidget(depot_info)
        left_layout.addWidget(customer_info)
        left_layout.addWidget(self.vehicle_control)
        left_layout.addWidget(self.delivery_info)
        
        # Middle panel - Map
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        
        # Toolbar with depot info
        toolbar = QToolBar()
        
        # Depot change action
        self.change_depot_action = QAction("🚩 Change Depot & Customer Count", self)
        self.change_depot_action.triggered.connect(self.change_depot_location)
        toolbar.addAction(self.change_depot_action)
        
        toolbar.addSeparator()
        
        # Toggle controls
        self.toggle_nfz_action = QAction("Toggle No-Fly Zones", self)
        self.toggle_nfz_action.setCheckable(True)
        self.toggle_nfz_action.setChecked(True)
        self.toggle_nfz_action.triggered.connect(self.toggle_no_fly_zones)
        toolbar.addAction(self.toggle_nfz_action)
        
        self.toggle_vehicles_action = QAction("Toggle Vehicles", self)
        self.toggle_vehicles_action.setCheckable(True)
        self.toggle_vehicles_action.setChecked(True)
        self.toggle_vehicles_action.triggered.connect(self.toggle_vehicles)
        toolbar.addAction(self.toggle_vehicles_action)
        
        toolbar.addSeparator()
        
        # Start/Stop vehicles
        self.start_action = QAction("▶ Start Vehicles", self)
        self.start_action.triggered.connect(self.start_vehicles)
        toolbar.addAction(self.start_action)
        
        self.stop_action = QAction("⏹ Stop Vehicles", self)
        self.stop_action.triggered.connect(self.stop_vehicles)
        toolbar.addAction(self.stop_action)
        
        # Map view
        self.map_view = QWebEngineView()
        self.map_view.loadFinished.connect(self.on_map_ready)
        
        middle_layout.addWidget(toolbar)
        middle_layout.addWidget(self.map_view)
        
        # Right panel - Sound monitoring
        right_panel = QFrame()
        right_panel.setMaximumWidth(400)
        right_panel.setMinimumWidth(350)
        right_layout = QVBoxLayout(right_panel)
        
        # Sound monitoring title
        sound_title = QLabel("Drone Sound Monitoring")
        sound_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff6b35; padding: 5px;")
        
        self.sound_graphs = SoundGraphWidget()
        self.noise_stats = NoiseStatisticsWidget()
        
        right_layout.addWidget(sound_title)
        right_layout.addWidget(self.sound_graphs, 2)
        right_layout.addWidget(self.noise_stats, 1)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(middle_widget, 1)
        main_layout.addWidget(right_panel)
        
        # Status bar
        self.statusBar().showMessage(f"India Airspace Management System Ready - Depot: {self.depot_coords[0]:.4f}, {self.depot_coords[1]:.4f} | Customers: {self.customer_count}")
        self.statusBar().setStyleSheet("background-color: #2d2d2d; color: #ffffff; padding: 5px;")
    
    def change_depot_location(self):
        """Open depot selection dialog to change location and customer count"""
        depot_dialog = DepotSelectionWindow()
        depot_dialog.depot_selected.connect(self.on_new_depot_selected)
        depot_dialog.exec()
    
    def on_new_depot_selected(self, lat, lng, customer_count):
        """Handle new depot selection with customer count"""
        self.depot_coords = [lat, lng]
        self.customer_count = customer_count
        
        # Regenerate delivery points around new depot with new customer count
        self.delivery_points = self.generate_delivery_points_around_depot()
        
        # Update delivery info widget
        self.delivery_info.update_depot(self.depot_coords, self.customer_count)
        
        # Stop current vehicles
        self.stop_vehicles()
        
        # Update UI
        self.update_depot_ui()
        
        # Reinitialize map if ready
        if self.map_ready:
            self.reinitialize_map()
        
        QMessageBox.information(
            self, 
            "Configuration Updated", 
            f"Depot and configuration updated:\n\n"
            f"🚩 Depot Location:\n   Latitude: {lat:.6f}\n   Longitude: {lng:.6f}\n\n"
            f" Customer Count: {customer_count}\n\n"
            f"{customer_count} delivery points have been generated around your new depot."
        )
    
    def update_depot_ui(self):
        """Update UI elements with new depot and customer info"""
        # Update status bar
        self.statusBar().showMessage(f"India Airspace Management System Ready - Depot: {self.depot_coords[0]:.4f}, {self.depot_coords[1]:.4f} | Customers: {self.customer_count}")
        
        # Update toolbar tooltip
        self.change_depot_action.setToolTip(f"Current depot: {self.depot_coords[0]:.4f}, {self.depot_coords[1]:.4f} | Customers: {self.customer_count}")
        
        # Update left panel labels
        for i in range(self.centralWidget().layout().itemAt(0).widget().layout().count()):
            item = self.centralWidget().layout().itemAt(0).widget().layout().itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QLabel):
                    text = widget.text()
                    if text.startswith("Depot:"):
                        widget.setText(f"Depot: {self.depot_coords[0]:.4f}, {self.depot_coords[1]:.4f}")
                    elif text.startswith("Customers:"):
                        widget.setText(f"Customers: {self.customer_count}")
    
    def reinitialize_map(self):
        """Reinitialize map with new depot location and delivery points"""
        if not self.map_ready:
            return
        
        # Initialize map with new data
        map_data = {
            "center": self.map_center,
            "zoom": self.map_zoom,
            "depot": self.depot_coords,
            "deliveries": self.delivery_points,
            "cities": [
                {'name': 'New Delhi', 'coords': [28.6139, 77.2090]},
                {'name': 'Mumbai', 'coords': [19.0760, 72.8777]},
                {'name': 'Bangalore', 'coords': [12.9716, 77.5946]},
                {'name': 'Chennai', 'coords': [13.0827, 80.2707]},
                {'name': 'Kolkata', 'coords': [22.5726, 88.3639]},
                {'name': 'Hyderabad', 'coords': [17.3850, 78.4867]},
                {'name': 'Pune', 'coords': [18.5204, 73.8567]},
                {'name': 'Ahmedabad', 'coords': [23.0225, 72.5714]}
            ],
            "nfzones": self.no_fly_zones
        }
        
        js_code = f"window.initializeMap({json.dumps(map_data)});"
        self.map_view.page().runJavaScript(js_code)
    
    def setup_data_simulator(self):
        """Setup data simulation thread for sidebars"""
        self.data_simulator = DataSimulator()
        self.data_simulator.sound_data_updated.connect(self.on_sound_data_updated)
        self.data_simulator.start()
    
    def on_sound_data_updated(self, level, waveform):
        """Handle sound data updates for right sidebar"""
        self.sound_graphs.update_sound_data(level, waveform)
        self.noise_stats.update_statistics(level)
        
    def create_map_file(self):
        """Create the HTML map file with JavaScript"""
        self.map_path = os.path.abspath("india_airspace_map.html")
        with open(self.map_path, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE)
        self.map_view.setUrl(QUrl.fromLocalFile(self.map_path))
        
    def on_map_ready(self, success):
        """Initialize map when ready"""
        if not success:
            print("Map failed to load!")
            return
            
        self.map_ready = True
        self.reinitialize_map()
        print(f"Map initialized successfully with depot at {self.depot_coords} and {self.customer_count} delivery points!")
    
    def toggle_no_fly_zones(self):
        """Toggle no-fly zones visibility"""
        if self.map_ready:
            show = self.toggle_nfz_action.isChecked()
            self.map_view.page().runJavaScript(f"window.toggleNoFlyZones({str(show).lower()});")
    
    def toggle_vehicles(self):
        """Toggle vehicles visibility"""
        if self.map_ready:
            show = self.toggle_vehicles_action.isChecked()
            self.map_view.page().runJavaScript(f"window.toggleVehicles({str(show).lower()});")
    
        # If showing vehicles and we have vehicles data, resend them
        if show and self.vehicles:
            self.send_vehicles_to_js()
    
    def start_vehicles(self):
        """Start vehicle movement"""
        if not self.map_ready:
            return
        if self.vehicles_started:
            return  # Already started
            
        self.vehicles_started = True
        self.start_wave(0)
        self.start_action.setText("🟢 Vehicles Running")
        self.start_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        print(f"Vehicle movement started from depot with {self.customer_count} delivery points!")
    
    def stop_vehicles(self):
        """Stop vehicle movement"""
        self.vehicles_started = False
        self.wave_running = False
        self.vehicles.clear()
        self.vehicle_control.status_list.clear()  # Clear status list
        
        if self.map_ready:
            self.map_view.page().runJavaScript("clearVehicles();")
            
        self.start_action.setText("▶ Start Vehicles")
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        print("Vehicle movement stopped!")
    
    def start_wave(self, wave_index):
        """Start wave of vehicles from custom depot to customer delivery points"""
        if wave_index >= len(self.waves):
            return
            
        cfg = self.waves[wave_index]
        self.vehicles.clear()
        
        deliveries = self.delivery_points[:]
        random.shuffle(deliveries)
        
        def pick_delivery(i):
            return deliveries[i % len(deliveries)]
        
        offset = 0
        
        # Create drones
        for i in range(cfg.get("num_drones", 0)):
            name = f"Drone {i+1}"
            delivery = pick_delivery(i + offset)
            route = RouteManager.build_roundtrip_route(self.depot_coords, delivery, use_drone=True)
            self.vehicles[name] = {
                "type": "Drone",
                "pos": route[0][:],
                "route": route,
                "route_index": 0,
                "speed": VEHICLE_SPEEDS["Drone"],
                "progress": 0.0,
                "weight": random.randint(*VEHICLE_WEIGHTS["Drone"])
            }
        
        offset += cfg.get("num_drones", 0)
        
        # Create electric trucks  
        for i in range(cfg.get("num_electric_trucks", 0)):
            name = f"Electric Truck {i+1}"
            delivery = pick_delivery(i + offset)
            route = RouteManager.build_roundtrip_route(self.depot_coords, delivery, use_drone=False)
            self.vehicles[name] = {
                "type": "Electric Truck",
                "pos": route[0][:],
                "route": route,
                "route_index": 0,
                "speed": VEHICLE_SPEEDS["Electric Truck"],
                "progress": 0.0,
                "weight": random.randint(*VEHICLE_WEIGHTS["Electric Truck"])
            }
        
        offset += cfg.get("num_electric_trucks", 0)
        
        # Create fuel trucks
        for i in range(cfg.get("num_fuel_trucks", 0)):
            name = f"Fuel Truck {i+1}"
            delivery = pick_delivery(i + offset)
            route = RouteManager.build_roundtrip_route(self.depot_coords, delivery, use_drone=False)
            self.vehicles[name] = {
                "type": "Fuel Truck",
                "pos": route[0][:],
                "route": route,
                "route_index": 0,
                "speed": VEHICLE_SPEEDS["Fuel Truck"],
                "progress": 0.0,
                "weight": random.randint(*VEHICLE_WEIGHTS["Fuel Truck"])
            }
        
        self.wave_running = True
        self.wave_start_time = time.time()
        
        # Send vehicles to JavaScript
        self.send_vehicles_to_js()
        
        # Update left sidebar with vehicle info
        for name, v in self.vehicles.items():
            vehicle_data = VehicleData(name, v["type"], v["pos"][0], v["pos"][1], "Moving", v["speed"])
            self.vehicle_control.update_vehicle_status(vehicle_data)
    
    def send_vehicles_to_js(self):
        """Send vehicle data to JavaScript without reloading map"""
        if not self.map_ready:
            return
        
        # Only send if vehicles should be visible
        if not self.toggle_vehicles_action.isChecked():
            return
        
        vehicle_data = {
            "vehicles": [
                {
                    "name": name,
                    "type": v["type"],
                    "pos": v["pos"],
                    "route": v["route"],
                    "speed": v["speed"],
                    "weight": v["weight"]
                }
                for name, v in self.vehicles.items()
            ]
        }
    
        js_code = f"window.setVehicles({json.dumps(vehicle_data)});"
        self.map_view.page().runJavaScript(js_code)
    
    def update_vehicle_positions_js(self):
        """Update vehicle positions in JavaScript without reloading map"""
        if not self.map_ready or not self.vehicles:
            return
        
        # Only update if vehicles should be visible
        if not self.toggle_vehicles_action.isChecked():
            return
        
        vehicle_data = {
            "vehicles": [
                {
                    "name": name,
                    "type": v["type"],
                    "pos": v["pos"],
                    "speed": v["speed"],
                    "weight": v["weight"]
                }
                for name, v in self.vehicles.items()
            ]
        }
    
        js_code = f"window.updateVehiclePositions({json.dumps(vehicle_data)});"
        self.map_view.page().runJavaScript(js_code)

    def all_vehicles_returned(self):
        """Check if all vehicles completed their routes"""
        for v in self.vehicles.values():
            if v["route_index"] < len(v["route"]) - 1:
                return False
        return True
    
    def tick_vehicle_movement(self):
        """Main vehicle movement tick"""
        if not self.map_ready or not self.vehicles_started:
            return
            
        # Check if we need to start next wave
        if not self.wave_running:
            if time.time() - self.wave_start_time >= self.pause_between_waves:
                self.current_wave = (self.current_wave + 1) % len(self.waves)
                self.start_wave(self.current_wave)
            return
        
        if not self.vehicles:
            return
            
        # Move vehicles
        dt = 0.5 / 3600.0  # 500ms in hours
        vehicles_moved = False
        
        for name, v in self.vehicles.items():
            if v["route_index"] >= len(v["route"]) - 1:
                continue
                
            # Current segment
            lat1, lon1 = v["route"][v["route_index"]]
            lat2, lon2 = v["route"][v["route_index"] + 1]
            
            # Calculate distance
            dist = RouteManager.haversine(lat1, lon1, lat2, lon2)
            if dist == 0:
                v["route_index"] += 1
                v["progress"] = 0.0
                if v["route_index"] < len(v["route"]):
                    v["pos"] = v["route"][v["route_index"]]
                vehicles_moved = True
                continue
            
            # Calculate movement
            step_km = v["speed"] * dt
            frac = step_km / dist
            v["progress"] += frac
            
            if v["progress"] >= 1.0:
                v["route_index"] += 1
                v["progress"] = 0.0
                if v["route_index"] < len(v["route"]):
                    v["pos"] = v["route"][v["route_index"]]
            else:
                # Interpolate position
                v["pos"] = [
                    lat1 + (lat2 - lat1) * v["progress"],
                    lon1 + (lon2 - lon1) * v["progress"]
                ]
            vehicles_moved = True
            
            # Update sidebar vehicle status
            vehicle_data = VehicleData(name, v["type"], v["pos"][0], v["pos"][1], "Moving", v["speed"])
            self.vehicle_control.update_vehicle_status(vehicle_data)
        
        # Update positions in JavaScript
        if vehicles_moved:
            self.update_vehicle_positions_js()
        
        # Check if wave completed
        if self.wave_running and self.all_vehicles_returned():
            self.wave_running = False
            self.wave_start_time = time.time()
            print(f"Wave {self.current_wave + 1} completed!")
            
            # Update status bar
            active_vehicles = len([v for v in self.vehicles.values() if v["route_index"] < len(v["route"]) - 1])
            self.statusBar().showMessage(f"Wave {self.current_wave + 1} completed - {active_vehicles} vehicles active - Depot: {self.depot_coords[0]:.4f}, {self.depot_coords[1]:.4f} | Customers: {self.customer_count}")
    
    def closeEvent(self, event):
        """Clean up on close"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'data_simulator'):
            self.data_simulator.stop()
            self.data_simulator.wait()
        
        # Clean up map file
        try:
            if os.path.exists(self.map_path):
                os.remove(self.map_path)
        except:
            pass
            
        event.accept()