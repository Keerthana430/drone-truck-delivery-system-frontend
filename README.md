# India Airspace Management System

A comprehensive drone delivery and airspace management system for India with real-time vehicle tracking, no-fly zone visualization, and sound monitoring capabilities.

## Features

### ✅ Core Functionality
- **Custom Depot Location Selection** - Interactive map-based depot selection
- **Scalable Customer Configuration** - 1-20 customers with automatic delivery point generation
- **Real-time Vehicle Movement** - Smooth animation without map reloading
- **Comprehensive No-Fly Zones** - Complete coverage across India
- **Multi-Vehicle Support** - Drones, Electric Trucks, and Fuel Trucks

### ✅ User Interface
- **Left Sidebar**: Vehicle Controls & Delivery Information
- **Center Panel**: Interactive map with India airspace
- **Right Sidebar**: Drone Sound Monitoring & Statistics
- **Dark Theme**: Professional dark UI throughout

### ✅ Advanced Features
- **Dynamic Reconfiguration** - Change depot and customer count anytime
- **Sound Visualization** - Real-time drone noise monitoring
- **Vehicle Status Tracking** - Live updates for all vehicles
- **Route Planning** - Automatic route generation and optimization
- **Interactive Controls** - Toggle vehicles, NFZ visibility, start/stop operations

## Project Structure

```
drone-truck-delivery-system/
├── main.py                          # Application entry point
├── README.md                        # This documentation
├── config/
│   ├── __init__.py
│   └── app_config.py               # Configuration settings and themes
├── core/
│   ├── __init__.py
│   ├── data_manager.py             # Data structures and simulation
│   └── api_handler.py              # Route planning and API management
├── gui/
│   ├── __init__.py
│   └── main_window.py              # Main application window
├── ui/
│   ├── __init__.py
│   └── dialog.py                   # Depot selection dialog
├── utils/
│   ├── __init__.py
│   └── nfz_data.py                 # No-fly zone database
├── widgets/
│   ├── __init__.py
│   ├── delivery_info.py            # Delivery information widget
│   ├── sound_monitoring.py         # Sound analysis widgets
│   └── vehicle_control.py          # Vehicle control panel
└── resources/
    ├── __init__.py
    ├── map_templates.py            # HTML/JavaScript map templates
    └── styles.qss                  # Qt stylesheet
```

## Installation & Setup

### Requirements
```bash
pip install PyQt5
pip install pyqtgraph
pip install requests
pip install numpy
pip install folium
```

### Running the Application
```bash
python main.py
```

## Usage

### 1. Depot Selection
- Launch the application to open the depot selection window
- Configure the number of customers (1-20)
- Click on the map to select your depot location
- Avoid red no-fly zones when selecting depot
- Confirm your selection to proceed

### 2. Main Application
- **Start Vehicles**: Click the play button to begin vehicle movement
- **Change Configuration**: Use toolbar to change depot location and customer count
- **Toggle Features**: Show/hide no-fly zones and vehicles
- **Monitor Status**: View real-time vehicle status in left sidebar
- **Sound Analysis**: Monitor drone noise in right sidebar

### 3. Vehicle Operations
- **Drones**: Blue icons with dotted routes (60 km/h)
- **Electric Trucks**: Green icons (40 km/h)
- **Fuel Trucks**: Red icons (35 km/h)
- All vehicles operate in waves with automatic cycling

## Technical Details

### Architecture
- **Modular Design**: Separated into logical modules for maintainability
- **PyQt5 Framework**: Modern Qt-based user interface
- **WebEngine Integration**: Leaflet.js maps with JavaScript bridge
- **Multi-threading**: Separate threads for data simulation and UI

### Data Management
- **Real-time Simulation**: Vehicle movement and sound data
- **Route Planning**: OSRM API with fallback to direct routes
- **No-Fly Zone Database**: Comprehensive Indian airspace restrictions
- **Dynamic Configuration**: Runtime reconfiguration without restart

### Performance
- **Optimized Updates**: Position updates without map reloading
- **Efficient Rendering**: Smooth 60fps vehicle movement
- **Memory Management**: Automatic cleanup and resource management

## Configuration

### Vehicle Waves
```python
DEFAULT_WAVES = [
    {"num_drones": 3, "num_electric_trucks": 10, "num_fuel_trucks": 2},
    {"num_drones": 2, "num_electric_trucks": 4, "num_fuel_trucks": 1},
]
```

### Vehicle Specifications
- **Drone**: 60 km/h, 1-5 kg payload
- **Electric Truck**: 40 km/h, 200-500 kg payload  
- **Fuel Truck**: 35 km/h, 300-700 kg payload

### Delivery Configuration
- **Distance Range**: 15-45 km from depot
- **Customer Range**: 1-20 customers configurable
- **Auto-generation**: Points distributed around depot

## Key Components

### Core Modules
- `data_manager.py`: Vehicle data structures and simulation thread
- `api_handler.py`: Route planning and distance calculations
- `nfz_data.py`: Complete no-fly zone database for India

### UI Components  
- `main_window.py`: Primary application interface
- `dialog.py`: Depot and customer selection interface
- `vehicle_control.py`: Vehicle tracking panel
- `delivery_info.py`: Delivery management widget
- `sound_monitoring.py`: Real-time audio analysis

### Resources
- `map_templates.py`: HTML/JavaScript map interfaces
- `styles.qss`: Qt stylesheet definitions
- `app_config.py`: Application configuration and constants

## Features in Detail

### No-Fly Zones Coverage
- **Airports**: All major international and domestic airports
- **Military Bases**: IAF stations, naval facilities, army installations  
- **Nuclear Facilities**: Power plants and research centers
- **Government Areas**: High security zones and administrative areas
- **Ports**: Major commercial and naval ports
- **Space Centers**: ISRO facilities and launch sites

### Real-time Monitoring
- **Vehicle Tracking**: Live position updates with trails
- **Sound Analysis**: Drone noise level monitoring and waveform display
- **Status Dashboard**: Comprehensive vehicle status information
- **Performance Metrics**: Speed, payload, and route progress

## Development Notes

This modular structure maintains the exact same functionality as the original monolithic code while providing:
- **Better Maintainability**: Logical separation of concerns
- **Code Reusability**: Modular components can be reused
- **Easier Testing**: Individual modules can be tested independently
- **Scalability**: Easy to add new features without affecting existing code

The restructuring preserves all original functionality including the depot selection workflow, vehicle movement simulation, sound monitoring, and interactive map features.