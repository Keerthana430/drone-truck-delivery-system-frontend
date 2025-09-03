"""
Enhanced application configuration settings with full fleet support
"""

# Dark theme stylesheet - enhanced for better fleet display
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

# Enhanced fleet configuration with more granular control
DEFAULT_FLEET_CONFIG = {
    "electric_trucks": 2,
    "fuel_trucks": 1, 
    "drones": 3
}

# Fleet constraints and validation
FLEET_CONSTRAINTS = {
    "min_electric_trucks": 0,
    "max_electric_trucks": 50,
    "min_fuel_trucks": 0,
    "max_fuel_trucks": 50,
    "min_drones": 0,
    "max_drones": 100,
    "min_total_vehicles": 1,
    "max_total_vehicles": 200
}

# Legacy waves configuration (kept for backward compatibility)
DEFAULT_WAVES = [
    {"num_drones": 3, "num_electric_trucks": 10, "num_fuel_trucks": 2},
    {"num_drones": 2, "num_electric_trucks": 4, "num_fuel_trucks": 1},
]

PAUSE_BETWEEN_WAVES = 3.0

# Vehicle speeds (km/h) - optimized for delivery operations
VEHICLE_SPEEDS = {
    "Drone": 60,           # Fast air delivery
    "Electric Truck": 40,  # Urban delivery speed
    "Fuel Truck": 35       # Heavier, slower trucks
}

# Vehicle weight ranges (kg) - realistic payload capacities
VEHICLE_WEIGHTS = {
    "Drone": (1, 5),              # Light packages only
    "Electric Truck": (200, 500),  # Medium cargo capacity
    "Fuel Truck": (300, 700)      # Heavy cargo capacity
}

# Vehicle operational characteristics
VEHICLE_CHARACTERISTICS = {
    "Drone": {
        "max_range_km": 100,        # Flight range before return
        "battery_life_hours": 2,    # Operating time
        "weather_dependent": True,   # Affected by weather
        "color": "#2196F3",         # Blue for drones
        "icon": "🚁"
    },
    "Electric Truck": {
        "max_range_km": 300,        # Range on full charge
        "battery_life_hours": 8,    # Work shift duration
        "weather_dependent": False,  # All-weather operation
        "color": "#4CAF50",         # Green for electric
        "icon": "🔋"
    },
    "Fuel Truck": {
        "max_range_km": 800,        # Long range capability
        "battery_life_hours": 12,   # Extended operation
        "weather_dependent": False,  # All-weather operation
        "color": "#FF9800",         # Orange for fuel
        "icon": "⛽"
    }
}

# Map settings
MAP_UPDATE_INTERVAL = 500  # milliseconds
SOUND_UPDATE_INTERVAL = 1000  # milliseconds

# Delivery point generation settings
DELIVERY_DISTANCE_MIN = 15  # km
DELIVERY_DISTANCE_MAX = 45  # km
MAX_CUSTOMERS = 50          # Increased for scalability
MIN_CUSTOMERS = 1

# Customer and delivery constraints
CUSTOMER_CONSTRAINTS = {
    "min_customers": 1,
    "max_customers": 999,       # Support large operations
    "default_customers": 5
}

# Performance and optimization settings
PERFORMANCE_CONFIG = {
    "max_route_points": 100,    # Limit route complexity for performance
    "update_frequency_ms": 500, # UI update interval
    "max_concurrent_vehicles": 200  # System limit
}

# Validation functions
def validate_fleet_config(electric_trucks, fuel_trucks, drones):
    """Validate fleet configuration against constraints"""
    total_vehicles = electric_trucks + fuel_trucks + drones
    
    errors = []
    
    # Check individual vehicle type limits
    if electric_trucks < FLEET_CONSTRAINTS["min_electric_trucks"] or electric_trucks > FLEET_CONSTRAINTS["max_electric_trucks"]:
        errors.append(f"Electric trucks must be between {FLEET_CONSTRAINTS['min_electric_trucks']} and {FLEET_CONSTRAINTS['max_electric_trucks']}")
    
    if fuel_trucks < FLEET_CONSTRAINTS["min_fuel_trucks"] or fuel_trucks > FLEET_CONSTRAINTS["max_fuel_trucks"]:
        errors.append(f"Fuel trucks must be between {FLEET_CONSTRAINTS['min_fuel_trucks']} and {FLEET_CONSTRAINTS['max_fuel_trucks']}")
    
    if drones < FLEET_CONSTRAINTS["min_drones"] or drones > FLEET_CONSTRAINTS["max_drones"]:
        errors.append(f"Drones must be between {FLEET_CONSTRAINTS['min_drones']} and {FLEET_CONSTRAINTS['max_drones']}")
    
    # Check total vehicle limits
    if total_vehicles < FLEET_CONSTRAINTS["min_total_vehicles"]:
        errors.append(f"Total vehicles must be at least {FLEET_CONSTRAINTS['min_total_vehicles']}")
    
    if total_vehicles > FLEET_CONSTRAINTS["max_total_vehicles"]:
        errors.append(f"Total vehicles cannot exceed {FLEET_CONSTRAINTS['max_total_vehicles']}")
    
    return len(errors) == 0, errors

def validate_customer_count(customer_count):
    """Validate customer count against constraints"""
    if customer_count < CUSTOMER_CONSTRAINTS["min_customers"] or customer_count > CUSTOMER_CONSTRAINTS["max_customers"]:
        return False, f"Customer count must be between {CUSTOMER_CONSTRAINTS['min_customers']} and {CUSTOMER_CONSTRAINTS['max_customers']}"
    return True, ""

def get_fleet_summary(electric_trucks, fuel_trucks, drones):
    """Generate a human-readable fleet summary"""
    total_vehicles = electric_trucks + fuel_trucks + drones
    
    summary = f"Fleet Configuration: {total_vehicles} Total Vehicles\n"
    summary += f"  • Electric Trucks: {electric_trucks} ({VEHICLE_CHARACTERISTICS['Electric Truck']['icon']})\n"
    summary += f"  • Fuel Trucks: {fuel_trucks} ({VEHICLE_CHARACTERISTICS['Fuel Truck']['icon']})\n" 
    summary += f"  • Drones: {drones} ({VEHICLE_CHARACTERISTICS['Drone']['icon']})\n"
    
    # Calculate capacity estimates
    daily_deliveries = total_vehicles * 8  # Rough estimate: 8 deliveries per vehicle per day
    coverage_radius = total_vehicles * 5   # Rough estimate: 5km radius per vehicle
    
    summary += f"\nEstimated Capacity:\n"
    summary += f"  • Daily Deliveries: ~{daily_deliveries} packages\n"
    summary += f"  • Coverage Area: ~{coverage_radius}km radius\n"
    
    return summary

# Export key configuration for easy import
__all__ = [
    'DARK_STYLE',
    'DEFAULT_DEPOT_COORDS',
    'DEFAULT_CUSTOMER_COUNT',
    'MAP_CENTER',
    'MAP_ZOOM',
    'DEFAULT_FLEET_CONFIG',
    'FLEET_CONSTRAINTS',
    'VEHICLE_SPEEDS',
    'VEHICLE_WEIGHTS',
    'VEHICLE_CHARACTERISTICS',
    'validate_fleet_config',
    'validate_customer_count',
    'get_fleet_summary'
]