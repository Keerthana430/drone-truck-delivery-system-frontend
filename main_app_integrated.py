import sys
import requests
import json
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QFrame, QPushButton, QComboBox,
                           QSlider, QTextEdit, QTabWidget, QGroupBox, QCheckBox,
                           QSpinBox, QLineEdit, QFormLayout, QSplitter, QToolBar, QAction,
                           QListWidget, QProgressBar, QGridLayout, QMessageBox, QDialog)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QUrl, Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon
import folium
import os
import math
import random
from datetime import datetime, timedelta
import pyqtgraph as pg
import numpy as np
from collections import deque

# Import depot selection window
try:
    from depot_selector import DepotSelectionWindow
except ImportError:
    print("Error: depot_selector.py not found! Please ensure it's in the same directory.")
    sys.exit(1)

# Dark theme stylesheet from original code
DARK_STYLE = """
QMainWindow {
    background-color: #1a1a1a;
    color: #ffffff;
}

QWidget {
    background-color: #1a1a1a;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QFrame {
    background-color: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 8px;
}

QPushButton {
    background-color: #ff6b35;
    border: none;
    padding: 12px 20px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 14px;
    color: white;
}

QPushButton:hover {
    background-color: #e55a2e;
}

QPushButton:pressed {
    background-color: #cc4e26;
}

QPushButton:checked {
    background-color: #ff8c42;
}

QLabel {
    color: #ffffff;
    font-size: 14px;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #404040;
    border-radius: 8px;
    margin-top: 1ex;
    padding-top: 10px;
    background-color: #2d2d2d;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    color: #ff6b35;
}

QScrollArea {
    border: none;
    background-color: #2d2d2d;
}

QListWidget {
    background-color: #333333;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 5px;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #404040;
}

QListWidget::item:selected {
    background-color: #ff6b35;
}

QProgressBar {
    border: 2px solid #404040;
    border-radius: 5px;
    text-align: center;
    background-color: #333333;
}

QProgressBar::chunk {
    background-color: #ff6b35;
    border-radius: 3px;
}

QToolBar {
    background-color: #2d2d2d;
    border: none;
    color: #ffffff;
}

QAction {
    color: #ffffff;
    padding: 8px;
}
"""

# Data structures from original code
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

# Sidebar components from original code
class SoundGraphWidget(QWidget):
    """Real-time drone sound visualization"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Waveform graph
        self.waveform_widget = pg.PlotWidget(title="Drone Sound Waveform")
        self.waveform_widget.setBackground('#2d2d2d')
        self.waveform_widget.setLabel('left', 'Amplitude')
        self.waveform_widget.setLabel('bottom', 'Time (ms)')
        self.waveform_curve = self.waveform_widget.plot(pen=pg.mkPen('#ff6b35', width=2))
        
        # Sound level graph
        self.level_widget = pg.PlotWidget(title="Sound Level (dB)")
        self.level_widget.setBackground('#2d2d2d')
        self.level_widget.setLabel('left', 'dB')
        self.level_widget.setLabel('bottom', 'Time')
        self.level_curve = self.level_widget.plot(pen=pg.mkPen('#00ff88', width=2))
        
        layout.addWidget(self.waveform_widget)
        layout.addWidget(self.level_widget)
        
        # Data buffers
        self.waveform_data = np.zeros(50)
        self.level_data = deque(maxlen=60)
        self.time_data = deque(maxlen=60)
        
    def update_sound_data(self, level, waveform):
        """Update both sound graphs"""
        # Update waveform
        self.waveform_data = np.array(waveform)
        self.waveform_curve.setData(self.waveform_data)
        
        # Update level graph
        current_time = time.time()
        self.level_data.append(level)
        self.time_data.append(current_time)
        
        if len(self.level_data) > 1:
            times = np.array(self.time_data) - self.time_data[0]
            levels = np.array(self.level_data)
            self.level_curve.setData(times, levels)

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

class NoiseStatisticsWidget(QWidget):
    """Display noise statistics and metrics"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.reset_stats()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Current readings
        current_group = QGroupBox("Current Readings")
        current_layout = QGridLayout(current_group)
        
        self.current_level = QLabel("-- dB")
        self.current_level.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff6b35;")
        
        current_layout.addWidget(QLabel("Current Level:"), 0, 0)
        current_layout.addWidget(self.current_level, 0, 1)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QGridLayout(stats_group)
        
        self.avg_level = QLabel("-- dB")
        self.peak_level = QLabel("-- dB")
        self.min_level = QLabel("-- dB")
        
        self.avg_level.setStyleSheet("font-size: 18px; color: #00ff88;")
        self.peak_level.setStyleSheet("font-size: 18px; color: #ff4757;")
        self.min_level.setStyleSheet("font-size: 18px; color: #3742fa;")
        
        stats_layout.addWidget(QLabel("Average:"), 0, 0)
        stats_layout.addWidget(self.avg_level, 0, 1)
        stats_layout.addWidget(QLabel("Peak:"), 1, 0)
        stats_layout.addWidget(self.peak_level, 1, 1)
        stats_layout.addWidget(QLabel("Minimum:"), 2, 0)
        stats_layout.addWidget(self.min_level, 2, 1)
        
        # Progress bars for levels
        levels_group = QGroupBox("Noise Levels")
        levels_layout = QVBoxLayout(levels_group)
        
        self.current_bar = QProgressBar()
        self.current_bar.setRange(0, 100)
        self.avg_bar = QProgressBar()
        self.avg_bar.setRange(0, 100)
        
        levels_layout.addWidget(QLabel("Current Level"))
        levels_layout.addWidget(self.current_bar)
        levels_layout.addWidget(QLabel("Average Level"))
        levels_layout.addWidget(self.avg_bar)
        
        layout.addWidget(current_group)
        layout.addWidget(stats_group)
        layout.addWidget(levels_group)
        layout.addStretch()
        
    def reset_stats(self):
        self.levels_history = []
        
    def update_statistics(self, current_level):
        """Update noise statistics"""
        self.levels_history.append(current_level)
        
        # Keep only last 100 readings
        if len(self.levels_history) > 100:
            self.levels_history.pop(0)
            
        avg = np.mean(self.levels_history)
        peak = np.max(self.levels_history)
        minimum = np.min(self.levels_history)
        
        self.current_level.setText(f"{current_level:.1f} dB")
        self.avg_level.setText(f"{avg:.1f} dB")
        self.peak_level.setText(f"{peak:.1f} dB")
        self.min_level.setText(f"{minimum:.1f} dB")
        
        # Update progress bars
        self.current_bar.setValue(int(current_level))
        self.avg_bar.setValue(int(avg))

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
        
        layout.addWidget(depot_group)
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

# Data simulator
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

# HTML Template (same as original)
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>India Airspace Management</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body { height: 100%; margin: 0; background: #0b1220; }
  #map { 
    height: 100%; 
    margin: 0; 
    background: #0b1220; 
    border-radius: 12px;
    overflow: hidden;
  }
  .legend {
    position: absolute; bottom: 12px; left: 12px;
    background: rgba(255,255,255,0.9); padding: 8px 10px; border-radius: 8px;
    font: 12px/1.2 system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  }
  .legend .dot { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; }
</style>
</head>
<body>
<div id="map"></div>
<div class="legend">
  <div><span class="dot" style="background:#3b82f6"></span> Drones (route dotted)</div>
  <div><span class="dot" style="background:#22c55e"></span> Electric Truck</div>
  <div><span class="dot" style="background:#ef4444"></span> Fuel Truck</div>
  <div><span class="dot" style="background:#f59e0b"></span> Selected Depot</div>
  <div><span class="dot" style="background:#8b5cf6"></span> Delivery Points</div>
</div>

<script>
  let map;
  let vehicleMarkers = {};
  let routeLines = {};
  let trailLines = {};
  let depotMarker;
  let deliveryMarkers = [];
  let showVehicles = true;
  let showNFZ = true;
  let nfzLayers = [];

  function initializeMap(mapData) {
    map = L.map('map').setView([mapData.center[0], mapData.center[1]], mapData.zoom);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, 
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Add depot marker
    if (mapData.depot) {
      depotMarker = L.marker([mapData.depot[0], mapData.depot[1]], {
        icon: L.divIcon({
          className: 'custom-div-icon',
          html: '<div style="background-color: #f59e0b; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; border: 2px solid white;"><i class="fa fa-home"></i></div>',
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        })
      }).addTo(map).bindTooltip('Your Selected Depot');
    }

    // Add delivery points
    if (mapData.deliveries) {
      mapData.deliveries.forEach((d, i) => {
        const marker = L.marker([d[0], d[1]], {
          icon: L.divIcon({
            className: 'custom-div-icon',
            html: '<div style="background-color: #8b5cf6; color: white; border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; border: 2px solid white;"><i class="fa fa-flag"></i></div>',
            iconSize: [18, 18],
            iconAnchor: [9, 9]
          })
        }).addTo(map).bindTooltip('Customer ' + (i+1));
        deliveryMarkers.push(marker);
      });
    }

    // Add major cities
    if (mapData.cities) {
      mapData.cities.forEach(city => {
        L.marker([city.coords[0], city.coords[1]], {
          icon: L.icon({
            iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
          })
        }).addTo(map).bindPopup('📍 ' + city.name).bindTooltip(city.name);
      });
    }

    // Add no-fly zones
    if (mapData.nfzones && showNFZ) {
      addNoFlyZones(mapData.nfzones);
    }
  }

  function addNoFlyZones(nfzones) {
    const colors = {
      'military': 'red',
      'airport': 'orange', 
      'nuclear': 'darkred',
      'government': 'purple',
      'border': 'black',
      'space': 'blue'
    };

    nfzones.forEach(nfz => {
      const color = colors[nfz.type] || 'gray';
      
      // Create circle
      const circle = L.circle([nfz.center[0], nfz.center[1]], {
        color: color,
        weight: 2,
        fillColor: color,
        fillOpacity: 0.3,
        radius: nfz.radius
      }).addTo(map);
      
      // Create marker
      const marker = L.marker([nfz.center[0], nfz.center[1]], {
        icon: L.divIcon({
          className: 'nfz-marker',
          html: `<div style="background-color: ${color}; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; border: 2px solid white;"><i class="fa fa-ban"></i></div>`,
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        })
      }).addTo(map);
      
      const popupContent = `
        <div style="width:250px;">
          <h4 style="color: red;">⚠️ NO-FLY ZONE</h4>
          <p><strong>Name:</strong> ${nfz.name}</p>
          <p><strong>Type:</strong> ${nfz.type}</p>
          <p><strong>Radius:</strong> ${(nfz.radius/1000).toFixed(1)} km</p>
          <p><strong>Description:</strong> ${nfz.description}</p>
        </div>
      `;
      
      circle.bindPopup(popupContent);
      marker.bindPopup(popupContent).bindTooltip('NFZ: ' + nfz.name);
      
      nfzLayers.push(circle);
      nfzLayers.push(marker);
    });
  }

  function getVehicleIcon(name, type) {
    let iconHtml = '';
    let iconColor = '';
    
    if (type === 'Drone') {
      iconHtml = '<i class="fa fa-plane"></i>';
      iconColor = '#3b82f6'; // blue
    } else if (type === 'Electric Truck') {
      iconHtml = '<i class="fa fa-truck"></i>';
      iconColor = '#ef4444'; // red
    } else if (type === 'Fuel Truck') {
      iconHtml = '<i class="fa fa-truck"></i>';
      iconColor = '#22c55e'; // green
    }
    
    return L.divIcon({
      className: 'custom-div-icon',
      html: `<div style="background-color: ${iconColor}; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">${iconHtml}</div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });
  }

  function setVehicles(vehicleData) {
    // Clear existing vehicles
    clearVehicles();
    
    if (!showVehicles) return;

    vehicleData.vehicles.forEach(v => {
      const icon = getVehicleIcon(v.name, v.type);
      const color = v.type === 'Drone' ? '#3b82f6' : v.type === 'Electric Truck' ? '#22c55e' : '#ef4444';
      
      // Create vehicle marker
      const marker = L.marker([v.pos[0], v.pos[1]], { icon: icon }).addTo(map);
      
      const tooltipText = `${v.name}\\nType: ${v.type}\\nWeight: ${v.weight} kg\\nSpeed: ${v.speed} km/h`;
      marker.bindTooltip(tooltipText).bindPopup(tooltipText);
      
      vehicleMarkers[v.name] = marker;

      // Create route line
      let routeStyle = {color: color, weight: 2, opacity: 0.7};
      if(v.type === 'Drone'){ 
        routeStyle.dashArray = '4,8';
      }
      routeLines[v.name] = L.polyline(v.route, routeStyle).addTo(map);

      // Create trail line
      const trail = L.polyline([v.pos], {color: color, weight: 3, opacity: 1});
      if(v.type === 'Drone'){ 
        trail.setStyle({dashArray: '6,6'}); 
      }
      trailLines[v.name] = trail.addTo(map);
    });
  }

  function updateVehiclePositions(vehicleData) {
    if (!showVehicles) return;
    
    vehicleData.vehicles.forEach(v => {
      const marker = vehicleMarkers[v.name];
      const trail = trailLines[v.name];
      
      if(marker){ 
        marker.setLatLng([v.pos[0], v.pos[1]]);
        const tooltipText = `${v.name}\\nType: ${v.type}\\nWeight: ${v.weight} kg\\nSpeed: ${v.speed} km/h`;
        marker.bindTooltip(tooltipText).bindPopup(tooltipText);
      }
      
      if(trail){
        const latlngs = trail.getLatLngs();
        const last = latlngs[latlngs.length - 1];
        const newpt = [v.pos[0], v.pos[1]];
        if(!last || last.lat !== newpt[0] || last.lng !== newpt[1]){
          latlngs.push(newpt);
          if(latlngs.length > 200) { 
            latlngs.splice(0, latlngs.length - 200); 
          }
          trail.setLatLngs(latlngs);
        }
      }
    });
  }

  function clearVehicles(){
    Object.values(vehicleMarkers).forEach(m => { 
      try { map.removeLayer(m); } catch(e){} 
    });
    Object.values(routeLines).forEach(l => { 
      try { map.removeLayer(l); } catch(e){} 
    });
    Object.values(trailLines).forEach(l => { 
      try { map.removeLayer(l); } catch(e){} 
    });
    vehicleMarkers = {};
    routeLines = {};
    trailLines = {};
  }

  function toggleVehicles(show) {
    showVehicles = show;
    if (!show) {
      clearVehicles();
    }
  }

  function toggleNoFlyZones(show) {
    showNFZ = show;
    nfzLayers.forEach(layer => {
      if (show) {
        map.addLayer(layer);
      } else {
        map.removeLayer(layer);
      }
    });
  }

  // Expose functions to Python
  window.initializeMap = initializeMap;
  window.setVehicles = setVehicles;
  window.updateVehiclePositions = updateVehiclePositions;
  window.toggleVehicles = toggleVehicles;
  window.toggleNoFlyZones = toggleNoFlyZones;
</script>
</body>
</html>
"""

class IndiaAirspaceMap(QMainWindow):
    def __init__(self, depot_coords=None, customer_count=5):
        super().__init__()
        self.setWindowTitle("India Airspace Management - No-Fly Zones Map")
        self.setGeometry(50, 50, 1800, 1000)
        self.setMinimumSize(1600, 900)
        
        # Apply dark theme
        self.setStyleSheet(DARK_STYLE)
        
        # Store depot coordinates and customer count
        self.depot_coords = depot_coords or [12.8500, 74.9200]  # Default Mangaluru
        self.customer_count = customer_count
        
        # India center coordinates for full country view
        self.map_center = [20.5937, 78.9629]  # Center of India
        self.map_zoom = 5  # Zoom level to show entire India
        
        # Major No-fly zones across India
        self.no_fly_zones = self.get_india_no_fly_zones()
        
        # Vehicle system
        self.vehicles = {}
        self.waves = [
            {"num_drones": 3, "num_electric_trucks": 10, "num_fuel_trucks": 2},
            {"num_drones": 2, "num_electric_trucks": 4, "num_fuel_trucks": 1},
        ]
        self.pause_between_waves = 3.0
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
        
    def get_india_no_fly_zones(self):
        """Comprehensive no-fly zones across India"""
        return [
            # Delhi NCR
            {
                'name': 'Indira Gandhi International Airport',
                'center': [28.5562, 77.1000],
                'radius': 8000,
                'type': 'airport',
                'description': 'Major international airport'
            },
            {
                'name': 'Red Fort & India Gate Area',
                'center': [28.6562, 77.2410],
                'radius': 3000,
                'type': 'government',
                'description': 'High security government area'
            },
            {
                'name': 'Palam Air Force Station',
                'center': [28.5599, 77.1026],
                'radius': 6000,
                'type': 'military',
                'description': 'IAF base adjacent to IGIA'
            },
            
            # Mumbai
            {
                'name': 'Chhatrapati Shivaji International Airport',
                'center': [19.0896, 72.8656],
                'radius': 8000,
                'type': 'airport',
                'description': 'Busiest airport in India'
            },
            {
                'name': 'Bhabha Atomic Research Centre',
                'center': [19.0176, 72.9201],
                'radius': 5000,
                'type': 'nuclear',
                'description': 'Nuclear facility restricted zone'
            },
            {
                'name': 'Mumbai Port',
                'center': [18.9667, 72.8333],
                'radius': 3000,
                'type': 'port',
                'description': 'Major commercial port'
            },
            {
                'name': 'INS Shikra - Naval Air Station',
                'center': [19.0896, 72.8656],
                'radius': 4000,
                'type': 'military',
                'description': 'Naval aviation facility'
            },
            
            # Bangalore
            {
                'name': 'Kempegowda International Airport',
                'center': [13.1986, 77.7066],
                'radius': 8000,
                'type': 'airport',
                'description': 'Major international airport'
            },
            {
                'name': 'HAL Airport & Aerospace Complex',
                'center': [12.9500, 77.6682],
                'radius': 4000,
                'type': 'military',
                'description': 'Military aerospace facility'
            },
            {
                'name': 'Yelahanka Air Force Station',
                'center': [13.1350, 77.6081],
                'radius': 5000,
                'type': 'military',
                'description': 'IAF training base'
            },
            
            # Chennai
            {
                'name': 'Chennai International Airport',
                'center': [12.9941, 80.1709],
                'radius': 8000,
                'type': 'airport',
                'description': 'Major South Indian airport'
            },
            {
                'name': 'INS Adyar - Naval Base',
                'center': [13.0067, 80.2206],
                'radius': 3000,
                'type': 'military',
                'description': 'Naval facility'
            },
            {
                'name': 'Chennai Port',
                'center': [13.0827, 80.3007],
                'radius': 2500,
                'type': 'port',
                'description': 'Major port facility'
            },
            
            # Hyderabad
            {
                'name': 'Rajiv Gandhi International Airport',
                'center': [17.2403, 78.4294],
                'radius': 8000,
                'type': 'airport',
                'description': 'Major international airport'
            },
            {
                'name': 'Begumpet Airport',
                'center': [17.4532, 78.4676],
                'radius': 3000,
                'type': 'airport',
                'description': 'Domestic and general aviation'
            },
            {
                'name': 'Dundigal Air Force Academy',
                'center': [17.6170, 78.4040],
                'radius': 5000,
                'type': 'military',
                'description': 'IAF training academy'
            },
            
            # Kolkata
            {
                'name': 'Netaji Subhas Chandra Bose Airport',
                'center': [22.6540, 88.4477],
                'radius': 8000,
                'type': 'airport',
                'description': 'Eastern India major airport'
            },
            {
                'name': 'Kolkata Port',
                'center': [22.5726, 88.3639],
                'radius': 4000,
                'type': 'port',
                'description': 'Major river port'
            },
            {
                'name': 'Barrackpore Air Force Station',
                'center': [22.7606, 88.3784],
                'radius': 4000,
                'type': 'military',
                'description': 'IAF transport base'
            },
            
            # MANGALURU REGION - NOW INCLUDED!
            {
                'name': 'Mangaluru International Airport',
                'center': [12.9612, 74.8900],
                'radius': 6000,
                'type': 'airport',
                'description': 'International airport serving coastal Karnataka'
            },
            {
                'name': 'New Mangalore Port',
                'center': [12.9141, 74.7994],
                'radius': 3500,
                'type': 'port',
                'description': 'Major port on west coast'
            },
            {
                'name': 'NITK Surathkal Campus',
                'center': [13.0067, 74.7939],
                'radius': 1500,
                'type': 'government',
                'description': 'Educational institution restricted area'
            },
            
            # Gujarat
            {
                'name': 'Sardar Vallabhbhai Patel Airport',
                'center': [23.0726, 72.6177],
                'radius': 8000,
                'type': 'airport',
                'description': 'Gujarat major airport'
            },
            {
                'name': 'Kandla Port',
                'center': [23.0000, 70.2167],
                'radius': 4000,
                'type': 'port',
                'description': 'Major port in Gujarat'
            },
            {
                'name': 'Jamnagar Air Force Station',
                'center': [22.4707, 70.0527],
                'radius': 5000,
                'type': 'military',
                'description': 'IAF fighter base'
            },
            {
                'name': 'Reliance Jamnagar Refinery',
                'center': [22.3000, 70.0500],
                'radius': 3000,
                'type': 'refinery',
                'description': 'World\'s largest oil refinery complex'
            },
            
            # Maharashtra (Additional)
            {
                'name': 'Pune Airport & Air Force Station',
                'center': [18.5822, 73.9197],
                'radius': 6000,
                'type': 'military',
                'description': 'Dual use military-civilian airport'
            },
            {
                'name': 'Nashik Air Force Station',
                'center': [19.9975, 73.7898],
                'radius': 4000,
                'type': 'military',
                'description': 'IAF transport base'
            },
            
            # Tamil Nadu (Additional)
            {
                'name': 'Coimbatore Airport',
                'center': [11.0297, 77.0434],
                'radius': 5000,
                'type': 'airport',
                'description': 'Domestic airport'
            },
            {
                'name': 'Kudankulam Nuclear Power Plant',
                'center': [8.1644, 77.7069],
                'radius': 10000,
                'type': 'nuclear',
                'description': 'Major nuclear power facility'
            },
            {
                'name': 'Kalpakkam Nuclear Facility',
                'center': [12.5504, 80.1755],
                'radius': 8000,
                'type': 'nuclear',
                'description': 'Nuclear research facility'
            },
            {
                'name': 'Satish Dhawan Space Centre SHAR',
                'center': [13.7199, 80.2304],
                'radius': 10000,
                'type': 'space',
                'description': 'ISRO launch facility'
            },
            {
                'name': 'Tuticorin Port',
                'center': [8.7642, 78.1348],
                'radius': 3000,
                'type': 'port',
                'description': 'Major port in Tamil Nadu'
            },
            
            # Kerala
            {
                'name': 'Cochin International Airport',
                'center': [10.1520, 76.4019],
                'radius': 7000,
                'type': 'airport',
                'description': 'Major international airport in Kerala'
            },
            {
                'name': 'Kochi Port',
                'center': [9.9312, 76.2673],
                'radius': 3000,
                'type': 'port',
                'description': 'Major port in Kerala'
            },
            {
                'name': 'INS Dronacharya - Naval Academy',
                'center': [10.0889, 76.3394],
                'radius': 4000,
                'type': 'military',
                'description': 'Naval training facility'
            },
            {
                'name': 'Trivandrum International Airport',
                'center': [8.4821, 76.9200],
                'radius': 6000,
                'type': 'airport',
                'description': 'International airport'
            },
            
            # Goa
            {
                'name': 'Dabolim Airport & Naval Air Station',
                'center': [15.3808, 73.8314],
                'radius': 5000,
                'type': 'military',
                'description': 'Naval air station and civilian airport'
            },
            {
                'name': 'Mormugao Port',
                'center': [15.4000, 73.8000],
                'radius': 2500,
                'type': 'port',
                'description': 'Iron ore export port'
            },
            
            # Andhra Pradesh
            {
                'name': 'Visakhapatnam Airport',
                'center': [17.7211, 83.2245],
                'radius': 6000,
                'type': 'airport',
                'description': 'Major airport in AP'
            },
            {
                'name': 'Visakhapatnam Port',
                'center': [17.6868, 83.2185],
                'radius': 4000,
                'type': 'port',
                'description': 'Major port on east coast'
            },
            {
                'name': 'INS Karna - Naval Base',
                'center': [17.6833, 83.2167],
                'radius': 3000,
                'type': 'military',
                'description': 'Naval facility'
            },
            
            # Odisha
            {
                'name': 'Bhubaneswar Airport',
                'center': [20.2538, 85.8179],
                'radius': 5000,
                'type': 'airport',
                'description': 'Capital airport'
            },
            {
                'name': 'Paradip Port',
                'center': [20.3167, 86.6167],
                'radius': 3500,
                'type': 'port',
                'description': 'Major port in Odisha'
            },
            
            # West Bengal (Additional)
            {
                'name': 'Bagdogra Airport',
                'center': [26.6812, 88.3286],
                'radius': 5000,
                'type': 'airport',
                'description': 'Airport serving North Bengal and Sikkim'
            },
            {
                'name': 'Haldia Port',
                'center': [22.0333, 88.1167],
                'radius': 3000,
                'type': 'port',
                'description': 'Major industrial port'
            },
            
            # Rajasthan
            {
                'name': 'Jaipur International Airport',
                'center': [26.8242, 75.8122],
                'radius': 6000,
                'type': 'airport',
                'description': 'Major airport in Rajasthan'
            },
            {
                'name': 'Jodhpur Air Force Station',
                'center': [26.2389, 73.0486],
                'radius': 4000,
                'type': 'military',
                'description': 'IAF fighter base'
            },
            {
                'name': 'Pokhran Test Range',
                'center': [27.0950, 71.7517],
                'radius': 15000,
                'type': 'military',
                'description': 'Nuclear test site - highly restricted'
            },
            
            # Punjab
            {
                'name': 'Sri Guru Ram Dass Jee International Airport',
                'center': [31.7098, 74.7979],
                'radius': 6000,
                'type': 'airport',
                'description': 'Amritsar international airport'
            },
            {
                'name': 'Pathankot Air Force Station',
                'center': [32.2338, 75.6346],
                'radius': 4000,
                'type': 'military',
                'description': 'IAF base near Pakistan border'
            },
            {
                'name': 'Halwara Air Force Station',
                'center': [30.7467, 75.6133],
                'radius': 4000,
                'type': 'military',
                'description': 'IAF transport base'
            },
            
            # Haryana
            {
                'name': 'Ambala Air Force Station',
                'center': [30.3816, 76.8047],
                'radius': 5000,
                'type': 'military',
                'description': 'Major IAF fighter base'
            },
            {
                'name': 'Sirsa Air Force Station',
                'center': [29.5604, 75.0454],
                'radius': 4000,
                'type': 'military',
                'description': 'IAF base'
            },
            
            # Uttar Pradesh
            {
                'name': 'Lucknow Airport',
                'center': [26.7606, 80.8893],
                'radius': 5000,
                'type': 'airport',
                'description': 'Capital airport'
            },
            {
                'name': 'Agra Air Force Station',
                'center': [27.1579, 77.9610],
                'radius': 4000,
                'type': 'military',
                'description': 'IAF base near Taj Mahal'
            },
            {
                'name': 'Varanasi Airport',
                'center': [25.4522, 82.8592],
                'radius': 4000,
                'type': 'airport',
                'description': 'Holy city airport'
            },
            
            # Madhya Pradesh
            {
                'name': 'Bhopal Airport',
                'center': [23.2876, 77.3376],
                'radius': 5000,
                'type': 'airport',
                'description': 'Capital airport'
            },
            {
                'name': 'Gwalior Air Force Station',
                'center': [26.2932, 78.2275],
                'radius': 4000,
                'type': 'military',
                'description': 'IAF fighter base'
            },
            
            # Chhattisgarh
            {
                'name': 'Raipur Airport',
                'center': [21.1804, 81.7385],
                'radius': 4000,
                'type': 'airport',
                'description': 'Capital airport'
            },
            
            # Jharkhand
            {
                'name': 'Ranchi Airport',
                'center': [23.3142, 85.3219],
                'radius': 4000,
                'type': 'airport',
                'description': 'Capital airport'
            },
            
            # Bihar
            {
                'name': 'Jay Prakash Narayan Airport',
                'center': [25.5913, 85.0879],
                'radius': 4000,
                'type': 'airport',
                'description': 'Patna airport'
            },
            
            # Assam & Northeast
            {
                'name': 'Lokpriya Gopinath Bordoloi Airport',
                'center': [26.1056, 91.5856],
                'radius': 5000,
                'type': 'airport',
                'description': 'Guwahati international airport'
            },
            {
                'name': 'Jorhat Air Force Station',
                'center': [26.7318, 94.1753],
                'radius': 4000,
                'type': 'military',
                'description': 'IAF base in Assam'
            },
            {
                'name': 'Tezpur Air Force Station',
                'center': [26.7089, 92.7845],
                'radius': 4000,
                'type': 'military',
                'description': 'IAF base near China border'
            },
            
            # Jammu & Kashmir / Ladakh
            {
                'name': 'Srinagar Airport',
                'center': [33.9871, 74.7742],
                'radius': 6000,
                'type': 'airport',
                'description': 'High-altitude airport'
            },
            {
                'name': 'Leh Airport',
                'center': [34.1358, 77.5464],
                'radius': 5000,
                'type': 'airport',
                'description': 'High-altitude military-civilian airport'
            },
            {
                'name': 'Jammu Airport',
                'center': [32.6890, 74.8375],
                'radius': 4000,
                'type': 'airport',
                'description': 'Winter capital airport'
            },
            
            # Himachal Pradesh
            {
                'name': 'Kullu Airport',
                'center': [31.8769, 77.1544],
                'radius': 3000,
                'type': 'airport',
                'description': 'High-altitude domestic airport'
            },
            
            # Uttarakhand
            {
                'name': 'Dehradun Airport',
                'center': [30.1897, 78.1802],
                'radius': 4000,
                'type': 'airport',
                'description': 'Capital airport'
            },
            
            # Additional Strategic Locations
            {
                'name': 'Kargil Military Area',
                'center': [34.5539, 76.1313],
                'radius': 20000,
                'type': 'military',
                'description': 'High-altitude military zone'
            },
            {
                'name': 'Siachen Base Camp Area',
                'center': [35.4219, 77.0615],
                'radius': 25000,
                'type': 'military',
                'description': 'World\'s highest battlefield'
            },
            {
                'name': 'Arunachal Pradesh Border Areas',
                'center': [28.2180, 94.7278],
                'radius': 30000,
                'type': 'border',
                'description': 'Sensitive border region with China'
            },
            
            # More Ports
            {
                'name': 'JNPT (Jawaharlal Nehru Port)',
                'center': [18.9647, 72.9505],
                'radius': 4000,
                'type': 'port',
                'description': 'Major container port near Mumbai'
            },
            {
                'name': 'Ennore Port',
                'center': [13.2333, 80.3333],
                'radius': 3000,
                'type': 'port',
                'description': 'Major port near Chennai'
            },
            
            # More Nuclear Facilities
            {
                'name': 'Tarapore Atomic Power Station',
                'center': [19.8500, 72.6667],
                'radius': 6000,
                'type': 'nuclear',
                'description': 'Nuclear power plant in Maharashtra'
            },
            {
                'name': 'Kakrapar Atomic Power Station',
                'center': [21.2333, 73.3500],
                'radius': 6000,
                'type': 'nuclear',
                'description': 'Nuclear power plant in Gujarat'
            },
            
            # Dams and Hydroelectric Projects
            {
                'name': 'Tehri Dam',
                'center': [30.3783, 78.4803],
                'radius': 5000,
                'type': 'dam',
                'description': 'Major hydroelectric dam'
            },
            {
                'name': 'Sardar Sarovar Dam',
                'center': [21.8386, 73.7593],
                'radius': 4000,
                'type': 'dam',
                'description': 'Major dam on Narmada river'
            },
            {
                'name': 'Hirakud Dam',
                'center': [21.5364, 83.8640],
                'radius': 4000,
                'type': 'dam',
                'description': 'Major dam in Odisha'
            },
            
            # More Defense Research Organizations
            {
                'name': 'DRDO Chandipur',
                'center': [20.9133, 87.0267],
                'radius': 8000,
                'type': 'defense',
                'description': 'Missile testing range'
            },
            {
                'name': 'DRDO Chitradurga',
                'center': [14.2251, 76.3980],
                'radius': 5000,
                'type': 'defense',
                'description': 'Aeronautical test range'
            }
        ]
        
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
        self.change_depot_action = QAction("📍 Change Depot & Customer Count", self)
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
        depot_dialog.exec_()
    
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
            f"📍 Depot Location:\n   Latitude: {lat:.6f}\n   Longitude: {lng:.6f}\n\n"
            f"📦 Customer Count: {customer_count}\n\n"
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
    
    # Vehicle movement methods (same as original with depot coordination)
    def create_straight_route(self, start, end, steps=50):
        """Create straight route between two points"""
        lat1, lon1 = start
        lat2, lon2 = end
        return [[lat1 + (lat2 - lat1) * t / steps, lon1 + (lon2 - lon1) * t / steps] 
                for t in range(steps + 1)]
    
    def get_route(self, start, end):
        """Get route - fallback to straight line"""
        try:
            url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
            r = requests.get(url, timeout=2)
            r.raise_for_status()
            coords = r.json()["routes"][0]["geometry"]["coordinates"]
            return [[lat, lon] for lon, lat in coords]
        except:
            return self.create_straight_route(start, end, steps=30)
    
    def build_roundtrip_route(self, start, delivery, use_drone=False):
        """Build roundtrip route"""
        if use_drone:
            to = self.create_straight_route(start, delivery, steps=20)
            back = self.create_straight_route(delivery, start, steps=20)
        else:
            to = self.get_route(start, delivery)
            back = self.get_route(delivery, start)
        return to + back[1:]
    
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
            route = self.build_roundtrip_route(self.depot_coords, delivery, use_drone=True)
            self.vehicles[name] = {
                "type": "Drone",
                "pos": route[0][:],
                "route": route,
                "route_index": 0,
                "speed": 60,
                "progress": 0.0,
                "weight": random.randint(1, 5)
            }
        
        offset += cfg.get("num_drones", 0)
        
        # Create electric trucks  
        for i in range(cfg.get("num_electric_trucks", 0)):
            name = f"Electric Truck {i+1}"
            delivery = pick_delivery(i + offset)
            route = self.build_roundtrip_route(self.depot_coords, delivery, use_drone=False)
            self.vehicles[name] = {
                "type": "Electric Truck",
                "pos": route[0][:],
                "route": route,
                "route_index": 0,
                "speed": 40,
                "progress": 0.0,
                "weight": random.randint(200, 500)
            }
        
        offset += cfg.get("num_electric_trucks", 0)
        
        # Create fuel trucks
        for i in range(cfg.get("num_fuel_trucks", 0)):
            name = f"Fuel Truck {i+1}"
            delivery = pick_delivery(i + offset)
            route = self.build_roundtrip_route(self.depot_coords, delivery, use_drone=False)
            self.vehicles[name] = {
                "type": "Fuel Truck",
                "pos": route[0][:],
                "route": route,
                "route_index": 0,
                "speed": 35,
                "progress": 0.0,
                "weight": random.randint(300, 700)
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
    
    def haversine(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points"""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
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
            dist = self.haversine(lat1, lon1, lat2, lon2)
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


def main():
    """Main application entry point with depot and customer selection"""
    app = QApplication(sys.argv)
    app.setApplicationName("India Airspace Management - Custom Depot & Customer Selection")
    app.setStyle('Fusion')
    
    # Step 1: Show depot selection window
    print("Starting Depot & Customer Selection...")
    depot_dialog = DepotSelectionWindow()
    
    selected_depot = None
    selected_customer_count = None
    main_window = None
    
    def on_depot_selected(lat, lng, customer_count):
        nonlocal selected_depot, selected_customer_count, main_window
        selected_depot = [lat, lng]
        selected_customer_count = customer_count
        print(f"Depot selected: {lat:.6f}, {lng:.6f} with {customer_count} customers")
        
        # Close the depot dialog
        depot_dialog.close()
        
        # Step 2: Launch main application with selected depot and customer count
        print(f"\nLaunching main application with:")
        print(f"  Depot: {selected_depot[0]:.6f}, {selected_depot[1]:.6f}")
        print(f"  Customers: {selected_customer_count}")
        
        # Create main window with selected depot and customer count
        main_window = IndiaAirspaceMap(depot_coords=selected_depot, customer_count=selected_customer_count)
        main_window.show()
        
        print("\n" + "="*70)
        print("INDIA AIRSPACE MANAGEMENT SYSTEM LAUNCHED!")
        print("="*70)
        print("Features:")
        print("✅ Custom Depot Location & Customer Count Selected")
        print(f"   📍 Depot: {selected_depot[0]:.6f}, {selected_depot[1]:.6f}")
        print(f"   👥 Customers: {selected_customer_count}")
        print(f"   📦 Delivery Points: {selected_customer_count} points generated")
        print("✅ Comprehensive No-Fly Zones across India")
        print("✅ Real-time Vehicle Movement (NO map reloading)")
        print("✅ Left Sidebar: Vehicle Controls & Delivery Info")
        print("✅ Right Sidebar: Drone Sound Monitoring & Statistics")
        print("✅ Interactive Controls:")
        print("   • Change Depot Location & Customer Count (anytime)")
        print("   • Toggle No-Fly Zones")
        print("   • Toggle Vehicles") 
        print("   • Start/Stop Vehicle Movement")
        print("\n🚀 Moving Vehicles:")
        print("• Drones: Blue icons with dotted routes (60 km/h)")
        print("• Electric Trucks: Green icons (40 km/h)")  
        print("• Fuel Trucks: Red icons (35 km/h)")
        print(f"\n📦 Delivery System ({selected_customer_count} customers):")
        print("• Vehicles move from YOUR selected depot")
        print(f"• {selected_customer_count} delivery points generated around your depot")
        print("• Real-time vehicle trails and status monitoring")
        print("• Dynamic delivery point generation based on customer count")
        print("\n🎯 Advanced Features:")
        print("• Depot & customer count reconfiguration without restarting app")
        print("• Automatic delivery point regeneration")
        print("• Real-time sound monitoring simulation")
        print("• Comprehensive vehicle status tracking")
        print("• Scalable customer-based delivery system (1-20 customers)")
        print("="*70)
    
    def on_dialog_closed():
        """Handle when depot dialog is closed without selection"""
        if not selected_depot:
            print("No depot selected. Exiting application.")
            app.quit()
    
    # Connect signals
    depot_dialog.depot_selected.connect(on_depot_selected)
    
    # Show the depot selection window
    depot_dialog.show()
    
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()