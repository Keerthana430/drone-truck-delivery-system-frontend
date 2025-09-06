"""
Main application window for India Airspace Management System - ENHANCED with fleet configuration
FIXED: Depot location update issue resolved
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
    def __init__(self, depot_coords=None, customer_count=5, electric_trucks=2, fuel_trucks=1, drones=3):
        super().__init__()
        self.setWindowTitle("India Airspace Management - No-Fly Zones Map")
        self.setGeometry(50, 50, 1800, 1000)
        self.setMinimumSize(1600, 900)
        
        # Apply dark theme
        self.setStyleSheet(DARK_STYLE)
        
        # Store depot coordinates and fleet configuration
        self.depot_coords = depot_coords or DEFAULT_DEPOT_COORDS
        self.customer_count = customer_count
        self.electric_trucks = electric_trucks
        self.fuel_trucks = fuel_trucks
        self.drones = drones
        
        # India center coordinates for full country view
        self.map_center = MAP_CENTER
        self.map_zoom = MAP_ZOOM
        
        # Major No-fly zones across India
        self.no_fly_zones = get_india_no_fly_zones()
        
        # Vehicle system
        self.vehicles = {}
        self.current_wave = 0
        self.wave_running = False
        self.wave_start_time = 0.0
        self.vehicles_started = False  # Track if vehicles are started
        self.vehicles_paused = False   # Track if vehicles are paused/stopped
        
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
        
        # Open in full screen
        self.showMaximized()
        
    def generate_delivery_points_around_depot(self):
        """Generate delivery points around the selected depot based on customer count"""
        points = []
        depot_lat, depot_lon = self.depot_coords
        
        for i in range(self.customer_count):
            # Generate points in a rough circle around depot
            angle = (i * (360 / self.customer_count)) + random.uniform(-20, 20)
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
        title_label = QLabel("Delivery System")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff6b35; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Depot and fleet configuration info
        depot_info = QLabel(f"Depot: {self.depot_coords[0]:.4f}, {self.depot_coords[1]:.4f}")
        depot_info.setStyleSheet("font-size: 12px; color: #cccccc; padding: 5px; text-align: center;")
        depot_info.setAlignment(Qt.AlignCenter)
        
        customer_info = QLabel(f"Customers: {self.customer_count}")
        customer_info.setStyleSheet("font-size: 12px; color: #8b5cf6; font-weight: bold; padding: 5px; text-align: center;")
        customer_info.setAlignment(Qt.AlignCenter)
        
        # Fleet configuration display
        fleet_info = QLabel(f"Fleet: {self.electric_trucks}E + {self.fuel_trucks}F + {self.drones}D")
        fleet_info.setStyleSheet("font-size: 12px; color: #4CAF50; font-weight: bold; padding: 5px; text-align: center;")
        fleet_info.setAlignment(Qt.AlignCenter)
        
        total_vehicles = self.electric_trucks + self.fuel_trucks + self.drones
        fleet_summary = QLabel(f"Total Vehicles: {total_vehicles}")
        fleet_summary.setStyleSheet("font-size: 11px; color: #FF9800; padding: 2px; text-align: center;")
        fleet_summary.setAlignment(Qt.AlignCenter)
        
        # Store references for updates
        self.depot_info_label = depot_info
        self.customer_info_label = customer_info
        self.fleet_info_label = fleet_info
        self.fleet_summary_label = fleet_summary
        
        # Control panels
        self.vehicle_control = VehicleControlPanel()
        self.delivery_info = DeliveryInfoWidget(self.depot_coords, self.customer_count)
        
        left_layout.addWidget(title_label)
        left_layout.addWidget(depot_info)
        left_layout.addWidget(customer_info)
        left_layout.addWidget(fleet_info)
        left_layout.addWidget(fleet_summary)
        left_layout.addWidget(self.vehicle_control)
        left_layout.addWidget(self.delivery_info)
        
        # Middle panel - Map
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        
        # Toolbar with depot info
        toolbar = QToolBar()
        
        # Depot change action
        self.change_depot_action = QAction("🚩 Change Depot & Fleet Configuration", self)
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
        
        # Start/Stop vehicles toggle button
        self.start_stop_action = QAction("▶ Start Vehicles", self)
        self.start_stop_action.setCheckable(True)
        self.start_stop_action.triggered.connect(self.toggle_start_stop_vehicles)
        toolbar.addAction(self.start_stop_action)
        
        # Restart vehicles button
        self.restart_action = QAction("🔄 Restart from Beginning", self)
        self.restart_action.triggered.connect(self.restart_vehicles)
        self.restart_action.setVisible(False)
        toolbar.addAction(self.restart_action)
        
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
        self.update_status_bar()
        self.statusBar().setStyleSheet("background-color: #2d2d2d; color: #ffffff; padding: 5px;")
    
    def update_status_bar(self):
        """Update status bar with current configuration"""
        total_vehicles = self.electric_trucks + self.fuel_trucks + self.drones
        self.statusBar().showMessage(
            f"India Airspace Management System Ready - "
            f"Depot: {self.depot_coords[0]:.4f}, {self.depot_coords[1]:.4f} | "
            f"Customers: {self.customer_count} | "
            f"Fleet: {total_vehicles} vehicles ({self.electric_trucks}E, {self.fuel_trucks}F, {self.drones}D)"
        )
    
    def toggle_start_stop_vehicles(self):
        """Toggle between starting and stopping vehicles with a single button"""
        if self.start_stop_action.isChecked():
            self.start_vehicles()
            self.start_stop_action.setText("⏸ Pause Vehicles")
            self.start_stop_action.setToolTip("Click to pause all vehicles")
            self.restart_action.setVisible(True)
        else:
            self.pause_vehicles()
            self.start_stop_action.setText("▶ Resume Vehicles")
            self.start_stop_action.setToolTip("Click to resume vehicle simulation")
    
    def start_vehicles(self):
        """Start vehicle movement with configured fleet"""
        if not self.map_ready:
            print("Map not ready, cannot start vehicles")
            return False
            
        if not self.vehicles_started:
            # First time starting - create vehicles based on configuration
            self.vehicles_started = True
            self.vehicles_paused = False
            self.create_configured_fleet()
        else:
            # Resume paused vehicles
            self.vehicles_paused = False
        
        # Update vehicle statuses to "Moving"
        for name, v in self.vehicles.items():
            vehicle_data = VehicleData(name, v["type"], v["pos"][0], v["pos"][1], "Moving", v["speed"])
            self.vehicle_control.update_vehicle_status(vehicle_data)
        
        print(f"Vehicle movement started with configured fleet: {self.electric_trucks}E + {self.fuel_trucks}F + {self.drones}D")
        return True

    def create_configured_fleet(self):
        """Create vehicles based on the configured fleet numbers with proper delivery allocation"""
        self.vehicles.clear()
        
        # Get delivery points
        deliveries = self.delivery_points[:]
        total_vehicles = self.electric_trucks + self.fuel_trucks + self.drones
        
        print(f"\n=== FLEET ALLOCATION DEBUG ===")
        print(f"Total delivery points generated: {len(deliveries)}")
        print(f"Total vehicles configured: {total_vehicles}")
        print(f"  - Electric Trucks: {self.electric_trucks}")
        print(f"  - Fuel Trucks: {self.fuel_trucks}")
        print(f"  - Drones: {self.drones}")
        
        # If we have more delivery points than vehicles, we need to select which ones to serve
        if total_vehicles < len(deliveries):
            print(f"WARNING: You have {len(deliveries)} delivery points but only {total_vehicles} vehicles!")
            print(f"Only {total_vehicles} delivery points will be assigned vehicles.")
            print(f"{len(deliveries) - total_vehicles} delivery points will remain unassigned.")
            
            # Select the closest delivery points to the depot for assignment
            deliveries_with_distance = []
            depot_lat, depot_lon = self.depot_coords
            
            for delivery in deliveries:
                dist = RouteManager.haversine(depot_lat, depot_lon, delivery[0], delivery[1])
                deliveries_with_distance.append((delivery, dist))
            
            # Sort by distance and take only what we can handle
            deliveries_with_distance.sort(key=lambda x: x[1])
            allocated_deliveries = [d[0] for d in deliveries_with_distance[:total_vehicles]]
            
            print(f"Selected {len(allocated_deliveries)} closest delivery points for vehicle assignment.")
            
        else:
            # We have enough or more vehicles than delivery points
            allocated_deliveries = []
            
            # First, assign one vehicle to each delivery point
            for delivery in deliveries:
                allocated_deliveries.append(delivery)
            
            # If we have extra vehicles, distribute them among delivery points
            remaining_vehicles = total_vehicles - len(deliveries)
            if remaining_vehicles > 0:
                print(f"Distributing {remaining_vehicles} extra vehicles among {len(deliveries)} delivery points.")
                for i in range(remaining_vehicles):
                    allocated_deliveries.append(deliveries[i % len(deliveries)])
            
            # Shuffle to distribute vehicle types evenly
            random.shuffle(allocated_deliveries)
        
        print(f"Final allocation list: {len(allocated_deliveries)} assignments")
        
        # Create vehicles and assign them to delivery points
        vehicle_count = 0
        
        # Create drones based on configuration
        for i in range(self.drones):
            if vehicle_count >= len(allocated_deliveries):
                break
                
            name = f"Drone {i+1}"
            delivery = allocated_deliveries[vehicle_count]
            route = RouteManager.build_roundtrip_route(self.depot_coords, delivery, use_drone=True)
            self.vehicles[name] = {
                "type": "Drone",
                "pos": route[0][:],
                "route": route,
                "route_index": 0,
                "speed": VEHICLE_SPEEDS["Drone"],
                "progress": 0.0,
                "weight": random.randint(*VEHICLE_WEIGHTS["Drone"]),
                "assigned_delivery": delivery
            }
            print(f"  {name} assigned to delivery point: ({delivery[0]:.4f}, {delivery[1]:.4f})")
            vehicle_count += 1
        
        # Create electric trucks based on configuration
        for i in range(self.electric_trucks):
            if vehicle_count >= len(allocated_deliveries):
                break
                
            name = f"Electric Truck {i+1}"
            delivery = allocated_deliveries[vehicle_count]
            route = RouteManager.build_roundtrip_route(self.depot_coords, delivery, use_drone=False)
            self.vehicles[name] = {
                "type": "Electric Truck",
                "pos": route[0][:],
                "route": route,
                "route_index": 0,
                "speed": VEHICLE_SPEEDS["Electric Truck"],
                "progress": 0.0,
                "weight": random.randint(*VEHICLE_WEIGHTS["Electric Truck"]),
                "assigned_delivery": delivery
            }
            print(f"  {name} assigned to delivery point: ({delivery[0]:.4f}, {delivery[1]:.4f})")
            vehicle_count += 1
        
        # Create fuel trucks based on configuration
        for i in range(self.fuel_trucks):
            if vehicle_count >= len(allocated_deliveries):
                break
                
            name = f"Fuel Truck {i+1}"
            delivery = allocated_deliveries[vehicle_count]
            route = RouteManager.build_roundtrip_route(self.depot_coords, delivery, use_drone=False)
            self.vehicles[name] = {
                "type": "Fuel Truck",
                "pos": route[0][:],
                "route": route,
                "route_index": 0,
                "speed": VEHICLE_SPEEDS["Fuel Truck"],
                "progress": 0.0,
                "weight": random.randint(*VEHICLE_WEIGHTS["Fuel Truck"]),
                "assigned_delivery": delivery
            }
            print(f"  {name} assigned to delivery point: ({delivery[0]:.4f}, {delivery[1]:.4f})")
            vehicle_count += 1
        
        self.wave_running = True
        self.wave_start_time = time.time()
        
        # Send vehicles to JavaScript
        self.send_vehicles_to_js()
        
        # Final allocation summary
        unique_deliveries = set()
        for vehicle in self.vehicles.values():
            delivery_coords = tuple(vehicle["assigned_delivery"])
            unique_deliveries.add(delivery_coords)
        
        print(f"\n=== FINAL ALLOCATION SUMMARY ===")
        print(f"Created vehicles: {len(self.vehicles)}")
        print(f"Unique delivery points with vehicles: {len(unique_deliveries)}")
        print(f"Total delivery points generated: {len(self.delivery_points)}")
        print(f"Unassigned delivery points: {len(self.delivery_points) - len(unique_deliveries)}")
        
        if len(unique_deliveries) < len(self.delivery_points):
            coverage_percent = (len(unique_deliveries) / len(self.delivery_points)) * 100
            print(f"Coverage: {coverage_percent:.1f}% of delivery points have vehicles assigned")
            print(f"\nRECOMMENDATION: To cover all delivery points, increase your fleet size to at least {len(self.delivery_points)} vehicles")
            print(f"OR reduce the number of customers/delivery points to {total_vehicles} or fewer")
        else:
            print(f"SUCCESS: All delivery points have vehicles assigned!")
        
        print(f"================================\n")

    def restart_vehicles(self):
        """Restart vehicles from the beginning of their routes"""
        if not self.vehicles_started:
            return
        
        # Reset all vehicles to start of their routes
        for name, v in self.vehicles.items():
            v["route_index"] = 0
            v["progress"] = 0.0
            v["pos"] = v["route"][0][:]  # Reset to depot position
        
        # Resume movement if paused
        self.vehicles_paused = False
        self.wave_running = True
        self.wave_start_time = time.time()
        
        # Update button states
        self.start_stop_action.setChecked(True)
        self.start_stop_action.setText("⏸ Pause Vehicles")
        
        # Update vehicle statuses to "Moving"
        for name, v in self.vehicles.items():
            vehicle_data = VehicleData(name, v["type"], v["pos"][0], v["pos"][1], "Moving", v["speed"])
            self.vehicle_control.update_vehicle_status(vehicle_data)
        
        # Update positions on map
        self.send_vehicles_to_js()
        
        print("All vehicles restarted from the beginning of their routes!")
        
        QMessageBox.information(
            self, 
            "Vehicles Restarted", 
            "All vehicles have been reset to the depot and will restart their delivery routes from the beginning."
        )

    def pause_vehicles(self):
        """Pause vehicle movement but keep them visible on map"""
        self.vehicles_paused = True
        
        # Update vehicle statuses to "Stopped"
        for name, v in self.vehicles.items():
            vehicle_data = VehicleData(name, v["type"], v["pos"][0], v["pos"][1], "Stopped", 0)
            self.vehicle_control.update_vehicle_status(vehicle_data)
            
        print("Vehicle movement paused! Vehicles remain visible at current positions.")
        return True

    def stop_vehicles(self):
        """Completely stop and clear all vehicles"""
        self.vehicles_started = False
        self.vehicles_paused = False
        self.wave_running = False
        self.vehicles.clear()
        
        if hasattr(self, 'vehicle_control') and hasattr(self.vehicle_control, 'status_list'):
            self.vehicle_control.status_list.clear()
        
        if self.map_ready:
            self.map_view.page().runJavaScript("clearVehicles();")
        
        if hasattr(self, 'start_stop_action'):
            self.start_stop_action.setChecked(False)
            self.start_stop_action.setText("▶ Start Vehicles")
            
        if hasattr(self, 'restart_action'):
            self.restart_action.setVisible(False)
            
        print("All vehicles cleared from map!")
        return True

    def change_depot_location(self):
        """Open depot selection dialog to change location, customer count, and fleet configuration"""
        depot_dialog = DepotSelectionWindow()
        depot_dialog.depot_selected.connect(self.on_new_depot_selected)
        depot_dialog.exec()
    
    def on_new_depot_selected(self, lat, lng, customer_count, electric_trucks, fuel_trucks, drones):
        """Handle new depot and fleet configuration selection"""
        # Store old coordinates for comparison
        old_depot = self.depot_coords[:]
        
        # Update configuration
        self.depot_coords = [lat, lng]
        self.customer_count = customer_count
        self.electric_trucks = electric_trucks
        self.fuel_trucks = fuel_trucks
        self.drones = drones
        
        # Regenerate delivery points around new depot
        self.delivery_points = self.generate_delivery_points_around_depot()
        
        # Update delivery info widget
        self.delivery_info.update_depot(self.depot_coords, self.customer_count)
        
        # Stop current vehicles completely when changing configuration
        self.stop_vehicles()
        
        # Update UI
        self.update_depot_and_fleet_ui()
        
        # FIXED: Force map reinitialization with new depot
        if self.map_ready:
            print(f"Updating depot from {old_depot} to {self.depot_coords}")
            self.force_map_update()
        
        total_vehicles = electric_trucks + fuel_trucks + drones
        QMessageBox.information(
            self, 
            "Configuration Updated", 
            f"Depot and fleet configuration updated:\n\n"
            f"🚩 Depot Location:\n   Latitude: {lat:.6f}\n   Longitude: {lng:.6f}\n\n"
            f" Customer Count: {customer_count}\n\n"
            f" Fleet Configuration:\n"
            f"   • Electric Trucks: {electric_trucks}\n"
            f"   • Fuel Trucks: {fuel_trucks}\n"
            f"   • Drones: {drones}\n"
            f"   • Total Vehicles: {total_vehicles}\n\n"
            f"{customer_count} delivery points have been generated around your new depot."
        )
    
    def update_depot_and_fleet_ui(self):
        """Update UI elements with new depot and fleet configuration"""
        # Update status bar
        self.update_status_bar()
        
        # Update toolbar tooltip
        total_vehicles = self.electric_trucks + self.fuel_trucks + self.drones
        self.change_depot_action.setToolTip(
            f"Current depot: {self.depot_coords[0]:.4f}, {self.depot_coords[1]:.4f} | "
            f"Customers: {self.customer_count} | "
            f"Fleet: {total_vehicles} vehicles"
        )
        
        # Update left panel labels
        if hasattr(self, 'depot_info_label'):
            self.depot_info_label.setText(f"Depot: {self.depot_coords[0]:.4f}, {self.depot_coords[1]:.4f}")
        if hasattr(self, 'customer_info_label'):
            self.customer_info_label.setText(f"Customers: {self.customer_count}")
        if hasattr(self, 'fleet_info_label'):
            self.fleet_info_label.setText(f"Fleet: {self.electric_trucks}E + {self.fuel_trucks}F + {self.drones}D")
        if hasattr(self, 'fleet_summary_label'):
            self.fleet_summary_label.setText(f"Total Vehicles: {total_vehicles}")
    
    def force_map_update(self):
        """FIXED: Force a complete map reload with new depot location"""
        if not self.map_ready:
            return
        
        print(f"Force updating map with new depot: {self.depot_coords}")
        
        # Method 1: Try to completely reload the map HTML file
        self.map_ready = False
        self.create_new_map_file()
        self.map_view.setUrl(QUrl.fromLocalFile(self.map_path))
    
    def create_new_map_file(self):
        """Create a new HTML map file to force complete reload"""
        # Create unique filename to force reload
        timestamp = str(int(time.time() * 1000))
        self.map_path = os.path.abspath(f"india_airspace_map_{timestamp}.html")
        
        # Write HTML template to new file
        with open(self.map_path, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE)
        
        print(f"Created new map file: {self.map_path}")
    
    def reinitialize_map(self):
        """FIXED: Reinitialize map with new depot location and delivery points"""
        if not self.map_ready:
            return
        
        print(f"Reinitializing map with depot: {self.depot_coords}")
        
        # Prepare complete map data including new depot
        map_data = {
            "center": self.map_center,
            "zoom": self.map_zoom,
            "depot": self.depot_coords,  # FIXED: Explicitly include depot coordinates
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
        
        # Try multiple approaches to ensure depot updates
        js_code = f"""
        console.log('Attempting to update depot to: {json.dumps(self.depot_coords)}');
        
        // Method 1: Direct depot update if function exists
        if (typeof window.updateDepotLocation === 'function') {{
            console.log('Using updateDepotLocation function');
            window.updateDepotLocation({json.dumps(self.depot_coords)}, {json.dumps(self.delivery_points)});
        }}
        // Method 2: Full map reinitialization
        else if (typeof window.initializeMap === 'function') {{
            console.log('Using initializeMap function');
            window.initializeMap({json.dumps(map_data)});
        }}
        // Method 3: Manual depot marker update
        else if (typeof map !== 'undefined') {{
            console.log('Manual depot marker update');
            
            // Remove existing depot marker if it exists
            if (typeof depotMarker !== 'undefined' && depotMarker) {{
                map.removeLayer(depotMarker);
            }}
            
            // Create new depot marker
            var newDepotCoords = {json.dumps(self.depot_coords)};
            var newDeliveries = {json.dumps(self.delivery_points)};
            
            // Add new depot marker
            depotMarker = L.marker(newDepotCoords, {{
                icon: L.divIcon({{
                    className: 'depot-marker',
                    html: '<div style="background: #ff6b35; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white;">🏢</div>',
                    iconSize: [20, 20],
                    iconAnchor: [10, 10]
                }})
            }}).addTo(map);
            
            depotMarker.bindPopup('<b>Depot</b><br/>Coordinates: ' + newDepotCoords[0].toFixed(4) + ', ' + newDepotCoords[1].toFixed(4));
            
            // Remove existing delivery markers
            if (typeof deliveryMarkers !== 'undefined' && deliveryMarkers) {{
                deliveryMarkers.forEach(function(marker) {{ map.removeLayer(marker); }});
            }}
            
            // Add new delivery markers
            deliveryMarkers = [];
            newDeliveries.forEach(function(coords, index) {{
                var marker = L.marker(coords, {{
                    icon: L.divIcon({{
                        className: 'delivery-marker',
                        html: '<div style="background: #8b5cf6; color: white; border-radius: 50%; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; border: 1px solid white;">' + (index + 1) + '</div>',
                        iconSize: [16, 16],
                        iconAnchor: [8, 8]
                    }})
                }}).addTo(map);
                
                marker.bindPopup('<b>Delivery Point ' + (index + 1) + '</b><br/>Coordinates: ' + coords[0].toFixed(4) + ', ' + coords[1].toFixed(4));
                deliveryMarkers.push(marker);
            }});
            
            // Center map on new depot
            map.setView(newDepotCoords, 8);
            
            console.log('Manual depot update completed');
        }}
        else {{
            console.error('No method available to update depot location');
        }}
        """
        
        self.map_view.page().runJavaScript(js_code)
        print(f"Map reinitialization attempted for depot at {self.depot_coords}")
    
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
        total_vehicles = self.electric_trucks + self.fuel_trucks + self.drones
        print(f"Map initialized successfully with depot at {self.depot_coords}")
        print(f"Configuration: {self.customer_count} customers, {total_vehicles} vehicles")
    
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
        
        if show and self.vehicles:
            self.send_vehicles_to_js()
    
    def send_vehicles_to_js(self):
        """Send vehicle data to JavaScript without reloading map"""
        if not self.map_ready:
            return
        
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
        
        if not self.toggle_vehicles_action.isChecked():
            return
        
        vehicle_data = {
            "vehicles": [
                {
                    "name": name,
                    "type": v["type"],
                    "pos": v["pos"],
                    "speed": v["speed"] if not self.vehicles_paused else 0,
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
        if not self.map_ready or not self.vehicles_started or self.vehicles_paused:
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
            status = "Stopped" if self.vehicles_paused else "Moving"
            speed = 0 if self.vehicles_paused else v["speed"]
            vehicle_data = VehicleData(name, v["type"], v["pos"][0], v["pos"][1], status, speed)
            self.vehicle_control.update_vehicle_status(vehicle_data)
        
        # Update positions in JavaScript
        if vehicles_moved:
            self.update_vehicle_positions_js()
        
        # Check if all vehicles completed
        if self.wave_running and self.all_vehicles_returned():
            self.wave_running = False
            print(f"All vehicles completed their delivery routes!")
            
            # Update status bar
            active_vehicles = len([v for v in self.vehicles.values() if v["route_index"] < len(v["route"]) - 1])
            status_text = "paused" if self.vehicles_paused else "completed"
            total_vehicles = self.electric_trucks + self.fuel_trucks + self.drones
            self.statusBar().showMessage(
                f"Delivery cycle {status_text} - "
                f"Fleet: {total_vehicles} vehicles ({self.electric_trucks}E, {self.fuel_trucks}F, {self.drones}D) - "
                f"Depot: {self.depot_coords[0]:.4f}, {self.depot_coords[1]:.4f} | Customers: {self.customer_count}"
            )
    
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