"""
Depot selection dialog
"""
import os
import json
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QFrame, QPushButton, QSpinBox, QFormLayout,
                           QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QUrl, Qt, pyqtSignal
from config.app_config import DARK_STYLE
from utils.nfz_data import get_depot_selection_no_fly_zones
from resources.map_templates import DEPOT_SELECTION_HTML

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
        self.no_fly_zones = get_depot_selection_no_fly_zones()
        
        self.setup_ui()
        self.create_map_file()
        
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