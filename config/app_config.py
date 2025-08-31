"""
Application configuration settings
"""

# Dark theme stylesheet
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

QPushButton:disabled {
    background-color: #666666;
    color: #999999;
}
"""

# Default configuration values
DEFAULT_DEPOT_COORDS = [12.8500, 74.9200]  # Default Mangaluru
DEFAULT_CUSTOMER_COUNT = 5
MAP_CENTER = [20.5937, 78.9629]  # Center of India
MAP_ZOOM = 5  # Zoom level to show entire India

# Vehicle configuration
DEFAULT_WAVES = [
    {"num_drones": 3, "num_electric_trucks": 10, "num_fuel_trucks": 2},
    {"num_drones": 2, "num_electric_trucks": 4, "num_fuel_trucks": 1},
]

PAUSE_BETWEEN_WAVES = 3.0

# Vehicle speeds (km/h)
VEHICLE_SPEEDS = {
    "Drone": 60,
    "Electric Truck": 40,
    "Fuel Truck": 35
}

# Vehicle weight ranges (kg)
VEHICLE_WEIGHTS = {
    "Drone": (1, 5),
    "Electric Truck": (200, 500),
    "Fuel Truck": (300, 700)
}

# Map settings
MAP_UPDATE_INTERVAL = 500  # milliseconds
SOUND_UPDATE_INTERVAL = 1000  # milliseconds

# Delivery point generation settings
DELIVERY_DISTANCE_MIN = 15  # km
DELIVERY_DISTANCE_MAX = 45  # km
MAX_CUSTOMERS = 20
MIN_CUSTOMERS = 1