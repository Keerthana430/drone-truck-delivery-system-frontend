import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QFrame, QPushButton, 
                           QTextEdit, QMessageBox, QSpinBox, QFormLayout)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QUrl, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon
from datetime import datetime

# Same dark theme from main application
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

QPushButton:disabled {
    background-color: #666666;
    color: #999999;
}

QLabel {
    color: #ffffff;
    font-size: 14px;
}

QSpinBox {
    background-color: #333333;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 8px;
    font-size: 14px;
    color: #ffffff;
}

QSpinBox:focus {
    border: 2px solid #ff6b35;
}

QTextEdit {
    background-color: #333333;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 8px;
    font-size: 12px;
}

QMessageBox {
    background-color: #2d2d2d;
    color: #ffffff;
}
"""

# HTML Template for depot selection map
DEPOT_SELECTION_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Select Depot Location - India Airspace Management</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body { 
    height: 100%; 
    margin: 0; 
    background: #0b1220; 
    font-family: 'Segoe UI', Arial, sans-serif;
  }
  #map { 
    height: 100%; 
    margin: 0; 
    background: #0b1220; 
    border-radius: 12px;
    overflow: hidden;
  }
  .info-panel {
    position: absolute;
    top: 20px;
    right: 20px;
    background: rgba(45, 45, 45, 0.95);
    color: white;
    padding: 20px;
    border-radius: 10px;
    width: 300px;
    backdrop-filter: blur(10px);
    border: 1px solid #404040;
  }
  .info-panel h3 {
    color: #ff6b35;
    margin-top: 0;
    font-size: 18px;
  }
  .info-panel p {
    margin: 8px 0;
    font-size: 14px;
    line-height: 1.4;
  }
  .selected-location {
    background: rgba(255, 107, 53, 0.1);
    border: 1px solid #ff6b35;
    padding: 10px;
    border-radius: 6px;
    margin: 10px 0;
  }
  .customer-info {
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid #8b5cf6;
    padding: 10px;
    border-radius: 6px;
    margin: 10px 0;
  }
  .legend {
    position: absolute; 
    bottom: 20px; 
    left: 20px;
    background: rgba(45, 45, 45, 0.95);
    color: white;
    padding: 15px;
    border-radius: 8px;
    font: 12px/1.4 system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    backdrop-filter: blur(10px);
    border: 1px solid #404040;
  }
  .legend .dot { 
    display: inline-block; 
    width: 12px; 
    height: 12px; 
    border-radius: 50%; 
    margin-right: 8px; 
  }
  .legend h4 {
    color: #ff6b35;
    margin: 0 0 10px 0;
    font-size: 14px;
  }
  .crosshair {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
    z-index: 1000;
  }
  .crosshair::before,
  .crosshair::after {
    content: '';
    position: absolute;
    background: #ff6b35;
  }
  .crosshair::before {
    width: 20px;
    height: 2px;
    top: -1px;
    left: -10px;
  }
  .crosshair::after {
    width: 2px;
    height: 20px;
    top: -10px;
    left: -1px;
  }
</style>
</head>
<body>
<div id="map"></div>

<div class="info-panel">
  <h3><i class="fa fa-map-marker-alt"></i> Select Depot Location</h3>
  <p><strong>Instructions:</strong></p>
  <p>• Click anywhere on the map to set your depot location</p>
  <p>• Avoid placing depot inside No-Fly Zones (red areas)</p>
  <p>• Consider proximity to delivery areas</p>
  <p>• Click "Confirm Location" when ready</p>
  
  <div class="customer-info">
    <strong>📦 Delivery Points:</strong><br>
    <span id="customerCount">0</span> delivery points will be generated around your depot
  </div>
  
  <div id="selectedLocation" class="selected-location" style="display: none;">
    <strong>Selected Depot:</strong><br>
    <span id="locationText">No location selected</span><br>
    <small id="coordsText"></small>
  </div>
</div>

<div class="legend">
  <h4>Map Legend</h4>
  <div><span class="dot" style="background:#ef4444"></span> No-Fly Zones</div>
  <div><span class="dot" style="background:#f59e0b"></span> Major Cities</div>
  <div><span class="dot" style="background:#22c55e"></span> Your Depot</div>
  <div><span class="dot" style="background:#8b5cf6"></span> Suggested Locations</div>
</div>

<script>
  let map;
  let depotMarker = null;
  let selectedCoords = null;
  let nfzLayers = [];
  let customerCount = 0;

  function initializeDepotMap(mapData) {
    map = L.map('map').setView([mapData.center[0], mapData.center[1]], mapData.zoom);
    
    // Use satellite view for better location selection
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 18,
      attribution: '&copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    }).addTo(map);

    // Add city labels overlay
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      opacity: 0.3,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Add major cities
    if (mapData.cities) {
      mapData.cities.forEach(city => {
        L.marker([city.coords[0], city.coords[1]], {
          icon: L.divIcon({
            className: 'custom-div-icon',
            html: '<div style="background-color: #f59e0b; color: white; border-radius: 50%; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; border: 2px solid white;"><i class="fa fa-city" style="font-size: 8px;"></i></div>',
            iconSize: [16, 16],
            iconAnchor: [8, 8]
          })
        }).addTo(map).bindTooltip(city.name, {permanent: false, direction: 'top'});
      });
    }

    // Add no-fly zones
    if (mapData.nfzones) {
      addNoFlyZones(mapData.nfzones);
    }

    // Add suggested depot locations
    if (mapData.suggested) {
      mapData.suggested.forEach((location, index) => {
        L.marker([location.coords[0], location.coords[1]], {
          icon: L.divIcon({
            className: 'custom-div-icon',
            html: '<div style="background-color: #8b5cf6; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; border: 2px solid white;"><i class="fa fa-warehouse" style="font-size: 10px;"></i></div>',
            iconSize: [20, 20],
            iconAnchor: [10, 10]
          })
        }).addTo(map)
        .bindPopup(`<strong>Suggested Location:</strong><br>${location.name}<br><small>${location.description}</small>`)
        .bindTooltip(location.name);
      });
    }

    // Map click handler
    map.on('click', function(e) {
      selectDepotLocation(e.latlng.lat, e.latlng.lng);
    });
  }

  function addNoFlyZones(nfzones) {
    const colors = {
      'military': '#ef4444',
      'airport': '#f97316', 
      'nuclear': '#dc2626',
      'government': '#a855f7',
      'border': '#374151',
      'space': '#3b82f6'
    };

    nfzones.forEach(nfz => {
      const color = colors[nfz.type] || '#6b7280';
      
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
          html: `<div style="background-color: ${color}; color: white; border-radius: 50%; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; border: 2px solid white;"><i class="fa fa-ban" style="font-size: 8px;"></i></div>`,
          iconSize: [16, 16],
          iconAnchor: [8, 8]
        })
      }).addTo(map);
      
      const popupContent = `
        <div style="width:200px;">
          <h4 style="color: ${color}; margin: 0 0 8px 0;">⚠️ NO-FLY ZONE</h4>
          <p style="margin: 4px 0;"><strong>Name:</strong> ${nfz.name}</p>
          <p style="margin: 4px 0;"><strong>Type:</strong> ${nfz.type}</p>
          <p style="margin: 4px 0;"><strong>Radius:</strong> ${(nfz.radius/1000).toFixed(1)} km</p>
        </div>
      `;
      
      circle.bindPopup(popupContent);
      marker.bindPopup(popupContent);
      
      nfzLayers.push(circle);
      nfzLayers.push(marker);
    });
  }

  function selectDepotLocation(lat, lng) {
    // Remove existing depot marker
    if (depotMarker) {
      map.removeLayer(depotMarker);
    }

    // Add new depot marker
    depotMarker = L.marker([lat, lng], {
      icon: L.divIcon({
        className: 'custom-div-icon',
        html: '<div style="background-color: #22c55e; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 2px 8px rgba(34,197,94,0.5);"><i class="fa fa-home"></i></div>',
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      })
    }).addTo(map);

    depotMarker.bindPopup(`<strong>Selected Depot Location</strong><br>Lat: ${lat.toFixed(6)}<br>Lng: ${lng.toFixed(6)}<br><br><strong>Delivery Points:</strong> ${customerCount}`);
    depotMarker.bindTooltip('Your Depot Location', {permanent: true, direction: 'top'});

    // Update UI
    selectedCoords = [lat, lng];
    document.getElementById('selectedLocation').style.display = 'block';
    document.getElementById('locationText').textContent = `Latitude: ${lat.toFixed(6)}, Longitude: ${lng.toFixed(6)}`;
    document.getElementById('coordsText').textContent = `${customerCount} delivery points will be generated`;

    // Notify Python
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.depot_selected(lat, lng);
    }
  }

  function updateCustomerCount(count) {
    customerCount = count;
    document.getElementById('customerCount').textContent = count;
    
    // Update selected location info if depot is selected
    if (selectedCoords) {
      document.getElementById('coordsText').textContent = `${count} delivery points will be generated`;
      if (depotMarker) {
        depotMarker.bindPopup(`<strong>Selected Depot Location</strong><br>Lat: ${selectedCoords[0].toFixed(6)}<br>Lng: ${selectedCoords[1].toFixed(6)}<br><br><strong>Delivery Points:</strong> ${count}`);
      }
    }
  }

  function getSelectedLocation() {
    return selectedCoords;
  }

  function getCustomerCount() {
    return customerCount;
  }

  // Expose functions
  window.initializeDepotMap = initializeDepotMap;
  window.selectDepotLocation = selectDepotLocation;
  window.updateCustomerCount = updateCustomerCount;
  window.getSelectedLocation = getSelectedLocation;
  window.getCustomerCount = getCustomerCount;
</script>
</body>
</html>
"""

class DepotSelectionWindow(QMainWindow):
    depot_selected = pyqtSignal(float, float, int)  # Signal to emit selected coordinates and customer count
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Depot Location & Customer Count - India Airspace Management")
        self.setGeometry(100, 100, 1600, 1000)  # Increased width for customer selector
        self.setMinimumSize(1400, 800)
        
        # Apply dark theme
        self.setStyleSheet(DARK_STYLE)
        
        # Selected depot coordinates and customer count
        self.selected_depot = None
        self.customer_count = 5  # Default customer count
        self.map_ready = False
        
        # India center coordinates
        self.map_center = [20.5937, 78.9629]
        self.map_zoom = 5
        
        # No-fly zones data (subset for depot selection)
        self.no_fly_zones = self.get_complete_india_no_fly_zones()
        
        self.setup_ui()
        self.create_map_file()
        
    def get_complete_india_no_fly_zones(self):
        """Get major no-fly zones for depot selection"""
        return [
            # Major airports
            {
                'name': 'Indira Gandhi International Airport',
                'center': [28.5562, 77.1000],
                'radius': 8000,
                'type': 'airport',
                'description': 'Major international airport'
            },
            {
                'name': 'Chhatrapati Shivaji International Airport',
                'center': [19.0896, 72.8656],
                'radius': 8000,
                'type': 'airport',
                'description': 'Busiest airport in India'
            },
            {
                'name': 'Kempegowda International Airport',
                'center': [13.1986, 77.7066],
                'radius': 8000,
                'type': 'airport',
                'description': 'Major international airport'
            },
            {
                'name': 'Chennai International Airport',
                'center': [12.9941, 80.1709],
                'radius': 8000,
                'type': 'airport',
                'description': 'Major South Indian airport'
            },
            # Nuclear facilities
            {
                'name': 'Bhabha Atomic Research Centre',
                'center': [19.0176, 72.9201],
                'radius': 5000,
                'type': 'nuclear',
                'description': 'Nuclear facility restricted zone'
            },
            {
                'name': 'Kudankulam Nuclear Power Plant',
                'center': [8.1644, 77.7069],
                'radius': 10000,
                'type': 'nuclear',
                'description': 'Major nuclear power facility'
            },
            # Military bases
            {
                'name': 'HAL Airport & Aerospace Complex',
                'center': [12.9500, 77.6682],
                'radius': 4000,
                'type': 'military',
                'description': 'Military aerospace facility'
            },
            # Government areas
            {
                'name': 'Red Fort & India Gate Area',
                'center': [28.6562, 77.2410],
                'radius': 3000,
                'type': 'government',
                'description': 'High security government area'
            },
            # Space center
            {
                'name': 'Satish Dhawan Space Centre SHAR',
                'center': [13.7199, 80.2304],
                'radius': 10000,
                'type': 'space',
                'description': 'ISRO launch facility'
            }
        ]
    
    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout - horizontal split for customer selector
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Customer configuration
        left_panel = QFrame()
        left_panel.setMaximumWidth(350)
        left_panel.setMinimumWidth(300)
        left_panel.setStyleSheet("QFrame { background-color: #2d2d2d; padding: 15px; }")
        left_layout = QVBoxLayout(left_panel)
        
        # Configuration title
        config_title = QLabel("📦 Delivery Configuration")
        config_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff6b35; margin-bottom: 20px;")
        
        # Customer count selector
        customer_group = QFrame()
        customer_group.setStyleSheet("QFrame { background-color: #333333; padding: 15px; border-radius: 8px; }")
        customer_layout = QFormLayout(customer_group)
        
        customer_label = QLabel("Number of Customers:")
        customer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        
        self.customer_spinbox = QSpinBox()
        self.customer_spinbox.setRange(1, 20)  # Allow 1-20 customers
        self.customer_spinbox.setValue(5)  # Default 5 customers
        self.customer_spinbox.setSuffix(" customers")
        self.customer_spinbox.setStyleSheet("font-size: 16px; padding: 10px;")
        self.customer_spinbox.valueChanged.connect(self.on_customer_count_changed)
        
        customer_info = QLabel("This determines how many delivery points will be generated around your selected depot location.")
        customer_info.setStyleSheet("font-size: 12px; color: #cccccc; margin-top: 10px;")
        customer_info.setWordWrap(True)
        
        customer_layout.addRow(customer_label, self.customer_spinbox)
        customer_layout.addWidget(customer_info)
        
        # Depot instructions
        depot_instructions = QLabel("""
🏭 <b>Depot Selection Instructions:</b>

1️⃣ Select number of customers above
2️⃣ Click on the map to choose depot location
3️⃣ Avoid red No-Fly Zones
4️⃣ Consider proximity to major cities
5️⃣ Click "Confirm" to proceed

💡 <b>Tips:</b>
• Higher customer count = more delivery points
• Depot location affects delivery efficiency
• Delivery points are generated within 15-45km radius
        """)
        depot_instructions.setStyleSheet("font-size: 12px; color: #ffffff; padding: 15px; background-color: #404040; border-radius: 8px; line-height: 1.4;")
        depot_instructions.setWordWrap(True)
        
        # Current selection display
        self.selection_display = QLabel("No depot selected")
        self.selection_display.setStyleSheet("font-size: 14px; color: #ff6b35; font-weight: bold; padding: 10px; background-color: #404040; border-radius: 4px; text-align: center;")
        self.selection_display.setAlignment(Qt.AlignCenter)
        
        left_layout.addWidget(config_title)
        left_layout.addWidget(customer_group)
        left_layout.addWidget(depot_instructions)
        left_layout.addWidget(self.selection_display)
        left_layout.addStretch()
        
        # Right panel - Map and controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("QFrame { background-color: #2d2d2d; padding: 15px; }")
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("🗺️ Select Your Depot Location")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #ff6b35;")
        
        # Subtitle
        subtitle_label = QLabel("Choose the starting point for your delivery operations")
        subtitle_label.setStyleSheet("font-size: 16px; color: #cccccc; margin-left: 10px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()
        
        # Map container
        map_container = QFrame()
        map_container.setStyleSheet("QFrame { border: 2px solid #404040; border-radius: 8px; }")
        map_layout = QVBoxLayout(map_container)
        map_layout.setContentsMargins(5, 5, 5, 5)
        
        # Map view
        self.map_view = QWebEngineView()
        self.map_view.loadFinished.connect(self.on_map_ready)
        map_layout.addWidget(self.map_view)
        
        # Bottom controls
        controls_frame = QFrame()
        controls_frame.setStyleSheet("QFrame { background-color: #2d2d2d; padding: 15px; }")
        controls_layout = QHBoxLayout(controls_frame)
        
        # Instructions
        instructions_label = QLabel(
            "📍 Click anywhere on the map to select your depot location. "
            f"This will generate {self.customer_count} delivery points around your depot."
        )
        instructions_label.setStyleSheet("font-size: 14px; color: #cccccc;")
        instructions_label.setWordWrap(True)
        self.instructions_label = instructions_label  # Keep reference for updates
        
        # Status display
        self.status_label = QLabel("No location selected")
        self.status_label.setStyleSheet("font-size: 14px; color: #ff6b35; font-weight: bold;")
        
        # Buttons
        self.confirm_btn = QPushButton("✅ Confirm Location & Continue")
        self.confirm_btn.clicked.connect(self.confirm_depot_selection)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setStyleSheet("QPushButton { padding: 15px 30px; font-size: 16px; }")
        
        self.reset_btn = QPushButton("🔄 Reset Selection")
        self.reset_btn.clicked.connect(self.reset_selection)
        self.reset_btn.setEnabled(False)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.close)
        
        # Layout controls
        controls_layout.addWidget(instructions_label)
        controls_layout.addStretch()
        controls_layout.addWidget(self.status_label)
        controls_layout.addWidget(self.reset_btn)
        controls_layout.addWidget(self.cancel_btn)
        controls_layout.addWidget(self.confirm_btn)
        
        # Add to right layout
        right_layout.addWidget(header_frame)
        right_layout.addWidget(map_container, 1)
        right_layout.addWidget(controls_frame)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)
        
        # Status bar
        self.statusBar().showMessage(f"Ready to select depot location for {self.customer_count} customers - Click on the map")
        self.statusBar().setStyleSheet("background-color: #2d2d2d; color: #ffffff; padding: 8px;")
    
    def on_customer_count_changed(self, value):
        """Handle customer count change"""
        self.customer_count = value
        
        # Update instructions
        self.instructions_label.setText(
            f"📍 Click anywhere on the map to select your depot location. "
            f"This will generate {value} delivery points around your depot."
        )
        
        # Update status bar
        self.statusBar().showMessage(f"Ready to select depot location for {value} customers - Click on the map")
        
        # Update selection display if depot is selected
        if self.selected_depot:
            lat, lng = self.selected_depot
            self.selection_display.setText(f"Depot: {lat:.4f}, {lng:.4f}\nCustomers: {value}")
        
        # Update map info panel
        if self.map_ready:
            js_code = f"window.updateCustomerCount({value});"
            self.map_view.page().runJavaScript(js_code)
    
    def create_map_file(self):
        """Create the HTML map file"""
        self.map_path = os.path.abspath("depot_selection_map.html")
        with open(self.map_path, "w", encoding="utf-8") as f:
            f.write(DEPOT_SELECTION_HTML)
        self.map_view.setUrl(QUrl.fromLocalFile(self.map_path))
    
    def on_map_ready(self, success):
        """Initialize map when ready"""
        if not success:
            QMessageBox.critical(self, "Error", "Failed to load the map!")
            return
            
        self.map_ready = True
        
        # Suggested depot locations
        suggested_locations = [
            {
                'name': 'Outskirts of Bangalore',
                'coords': [13.0500, 77.7500],
                'description': 'Good connectivity, away from airport NFZ'
            },
            {
                'name': 'Chennai Surroundings',
                'coords': [12.8500, 80.0500],
                'description': 'Industrial area, good for logistics'
            },
            {
                'name': 'Mumbai Suburbs',
                'coords': [19.2000, 72.9500],
                'description': 'Outside nuclear facility zone'
            },
            {
                'name': 'Delhi NCR Edge',
                'coords': [28.4000, 77.3000],
                'description': 'Away from airport and government areas'
            },
            {
                'name': 'Hyderabad Outskirts',
                'coords': [17.1000, 78.6000],
                'description': 'Developing logistics hub'
            },
            {
                'name': 'Pune Industrial Area',
                'coords': [18.4000, 73.7000],
                'description': 'Away from air force station'
            }
        ]
        
        # Initialize map with data
        map_data = {
            "center": self.map_center,
            "zoom": self.map_zoom,
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
            "nfzones": self.no_fly_zones,
            "suggested": suggested_locations
        }
        
        js_code = f"window.initializeDepotMap({json.dumps(map_data)});"
        self.map_view.page().runJavaScript(js_code)
        
        # Update customer count in map
        js_code = f"window.updateCustomerCount({self.customer_count});"
        self.map_view.page().runJavaScript(js_code)
        
        # Setup JavaScript callback for depot selection
        self.setup_js_callback()
        
        print("Depot selection map initialized successfully!")
    
    def setup_js_callback(self):
        """Setup JavaScript callback for depot selection"""
        # We'll use a timer to periodically check for selection
        self.selection_timer = QTimer()
        self.selection_timer.timeout.connect(self.check_selection)
        self.selection_timer.start(1000)  # Check every second
    
    def check_selection(self):
        """Check if user has selected a location"""
        if not self.map_ready:
            return
        
        js_code = "window.getSelectedLocation();"
        self.map_view.page().runJavaScript(js_code, self.handle_selection_result)
    
    def handle_selection_result(self, result):
        """Handle the result from JavaScript"""
        if result and isinstance(result, list) and len(result) == 2:
            lat, lng = result
            if self.selected_depot != [lat, lng]:
                self.selected_depot = [lat, lng]
                self.update_selection_ui(lat, lng)
    
    def update_selection_ui(self, lat, lng):
        """Update UI when depot is selected"""
        self.status_label.setText(f"Selected: {lat:.6f}, {lng:.6f}")
        self.selection_display.setText(f"Depot: {lat:.4f}, {lng:.4f}\nCustomers: {self.customer_count}")
        self.confirm_btn.setEnabled(True)
        self.reset_btn.setEnabled(True)
        
        # Update status bar
        self.statusBar().showMessage(f"Depot selected at coordinates: {lat:.6f}, {lng:.6f} for {self.customer_count} customers - Ready to confirm")
        
        print(f"Depot selected: Latitude {lat:.6f}, Longitude {lng:.6f} for {self.customer_count} customers")
    
    def reset_selection(self):
        """Reset the depot selection"""
        self.selected_depot = None
        self.status_label.setText("No location selected")
        self.selection_display.setText("No depot selected")
        self.confirm_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        
        # Clear selection in JavaScript
        if self.map_ready:
            js_code = """
            if (depotMarker) {
                map.removeLayer(depotMarker);
                depotMarker = null;
            }
            selectedCoords = null;
            document.getElementById('selectedLocation').style.display = 'none';
            """
            self.map_view.page().runJavaScript(js_code)
        
        self.statusBar().showMessage(f"Selection reset - Click on the map to select depot location for {self.customer_count} customers")
    
    def confirm_depot_selection(self):
        """Confirm the depot selection and emit signal"""
        if not self.selected_depot:
            QMessageBox.warning(self, "Warning", "Please select a depot location first!")
            return
        
        lat, lng = self.selected_depot
        
        # Confirm with user
        reply = QMessageBox.question(
            self, 
            "Confirm Depot Configuration",
            f"Confirm depot configuration:\n\n"
            f"📍 Depot Location:\n   Latitude: {lat:.6f}\n   Longitude: {lng:.6f}\n\n"
            f"📦 Customer Count: {self.customer_count}\n\n"
            f"This will generate {self.customer_count} delivery points around your depot.\n\n"
            f"Proceed to main application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # Emit signal with selected coordinates and customer count
            self.depot_selected.emit(lat, lng, self.customer_count)
            print(f"Depot confirmed at: {lat:.6f}, {lng:.6f} with {self.customer_count} customers")
            self.accept()
    
    def accept(self):
        """Override accept to clean up"""
        if hasattr(self, 'selection_timer'):
            self.selection_timer.stop()
        super().close()
    
    def closeEvent(self, event):
        """Clean up on close"""
        if hasattr(self, 'selection_timer'):
            self.selection_timer.stop()
        
        # Clean up map file
        try:
            if os.path.exists(self.map_path):
                os.remove(self.map_path)
        except:
            pass
        
        event.accept()


def main():
    """Test the depot selection window"""
    app = QApplication(sys.argv)
    app.setApplicationName("Depot Location & Customer Selector")
    app.setStyle('Fusion')
    
    def on_depot_selected(lat, lng, customer_count):
        print(f"\n{'='*60}")
        print(f"DEPOT CONFIGURATION SELECTED:")
        print(f"Latitude: {lat:.6f}")
        print(f"Longitude: {lng:.6f}")
        print(f"Customer Count: {customer_count}")
        print(f"Delivery points to be generated: {customer_count}")
        print(f"{'='*60}")
        app.quit()
    
    window = DepotSelectionWindow()
    window.depot_selected.connect(on_depot_selected)
    window.show()
    
    print("Depot Selection System with Customer Configuration Started!")
    print("="*60)
    print("Features:")
    print("- Interactive map with satellite imagery")
    print("- Customer count selector (1-20 customers)")
    print("- No-Fly Zone visualization")
    print("- Suggested depot locations")
    print("- Click anywhere to select depot")
    print("- Real-time coordinate display")
    print("- Dynamic delivery point count preview")
    print("="*60)
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()