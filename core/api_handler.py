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

import math
import requests
import json
import time

class RouteManager:
    """Route planning using actual road networks with strict depot enforcement"""

    @staticmethod
    def get_osrm_route(start_lat, start_lon, end_lat, end_lon):
        """
        Get actual road route using OSRM (Open Source Routing Machine)
        This is a FREE service that provides real road routing
        """
        try:
            # OSRM API expects longitude,latitude format
            start_coord = f"{start_lon},{start_lat}"
            end_coord = f"{end_lon},{end_lat}"
            
            # Use the free OSRM demo server
            url = f"http://router.project-osrm.org/route/v1/driving/{start_coord};{end_coord}"
            
            params = {
                'overview': 'full',
                'geometries': 'geojson',
                'steps': 'false'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('routes') and len(data['routes']) > 0:
                    # Extract coordinates from the route
                    coordinates = data['routes'][0]['geometry']['coordinates']
                    
                    # Convert from [lon, lat] to [lat, lon] and filter points
                    route_points = []
                    for i, coord in enumerate(coordinates):
                        # Take every 3rd point to reduce density but keep detail
                        if i % 3 == 0 or i == len(coordinates) - 1:
                            route_points.append([coord[1], coord[0]])  # lat, lon
                    
                    # ENFORCE: Ensure route starts exactly at the requested start point
                    if route_points:
                        route_points[0] = [start_lat, start_lon]
                    
                    return route_points
            
            print(f"OSRM API failed with status: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            print(f"OSRM request failed: {e}")
        except Exception as e:
            print(f"OSRM routing error: {e}")
        
        # Fallback to straight line if API fails
        return RouteManager.create_fallback_route(start_lat, start_lon, end_lat, end_lon)

    @staticmethod
    def create_fallback_route(start_lat, start_lon, end_lat, end_lon):
        """
        Fallback route when API is unavailable - creates a more realistic interpolated path
        ALWAYS starts exactly at the given start coordinates
        """
        # ENFORCE: Always start exactly at the specified coordinates
        route = [[start_lat, start_lon]]
        
        # Calculate distance
        distance = RouteManager.haversine(start_lat, start_lon, end_lat, end_lon)
        
        # Create intermediate points based on distance
        num_points = max(5, min(20, int(distance / 2)))  # 1 point every 2km approximately
        
        for i in range(1, num_points):
            t = i / num_points
            
            # Linear interpolation
            lat = start_lat + (end_lat - start_lat) * t
            lon = start_lon + (end_lon - start_lon) * t
            
            # Add slight deviations to simulate road curves
            deviation = 0.001 * (1 - abs(t - 0.5) * 2)  # More deviation in middle
            lat += (hash(str(i)) % 1000 - 500) / 500000 * deviation  # Deterministic "random"
            lon += (hash(str(i + 100)) % 1000 - 500) / 500000 * deviation
            
            route.append([lat, lon])
        
        # ENFORCE: Always end exactly at the specified coordinates
        route.append([end_lat, end_lon])
        return route

    @staticmethod
    def create_drone_route(start_lat, start_lon, end_lat, end_lon):
        """
        Create a straight-line route for drones (air travel)
        ALWAYS starts exactly at the given start coordinates
        """
        # ENFORCE: Always start exactly at the specified coordinates
        route = [[start_lat, start_lon]]
        
        # Calculate distance to determine smoothness
        distance = RouteManager.haversine(start_lat, start_lon, end_lat, end_lon)
        
        # For drones, create fewer waypoints for straighter flight
        num_points = max(2, min(8, int(distance / 5)))  # 1 point every 5km for smooth movement
        
        for i in range(1, num_points):
            t = i / num_points
            
            # Simple linear interpolation for straight flight
            lat = start_lat + (end_lat - start_lat) * t
            lon = start_lon + (end_lon - start_lon) * t
            
            route.append([lat, lon])
        
        # ENFORCE: Always end exactly at the specified coordinates
        route.append([end_lat, end_lon])
        return route

    @staticmethod
    def build_delivery_route(depot, delivery, use_drone=True):
        """
        Build a route from depot to delivery and back using the same path
        Vehicle visits delivery point exactly once, then returns via same route
        ENFORCES that the route starts and ends exactly at the depot coordinates
        """
        # VALIDATE: Ensure depot coordinates are provided
        if not depot or len(depot) != 2:
            raise ValueError("Depot coordinates must be provided as [lat, lon]")
        
        # VALIDATE: Ensure delivery coordinates are provided
        if not delivery or len(delivery) != 2:
            raise ValueError("Delivery coordinates must be provided as [lat, lon]")
        
        depot_lat, depot_lon = depot[0], depot[1]
        delivery_lat, delivery_lon = delivery[0], delivery[1]
        
        print(f"Building route from depot {depot} to delivery {delivery} and back via same path (drone: {use_drone})")
        
        if use_drone:
            # DRONES: Use straight-line flight paths
            print("Creating drone delivery route with straight-line flight path...")
            outbound_route = RouteManager.create_drone_route(
                depot_lat, depot_lon, delivery_lat, delivery_lon
            )
            print(f"Drone outbound route completed with {len(outbound_route)} flight waypoints")
        else:
            # TRUCKS: Use actual road networks
            print("Creating truck delivery route using real road network...")
            outbound_route = RouteManager.get_osrm_route(
                depot_lat, depot_lon, delivery_lat, delivery_lon
            )
            print(f"Truck outbound route completed with {len(outbound_route)} road waypoints")
        
        # ENFORCE: Double-check that route starts at depot and ends at delivery
        if outbound_route and len(outbound_route) > 0:
            outbound_route[0] = [depot_lat, depot_lon]  # Force start at depot
            outbound_route[-1] = [delivery_lat, delivery_lon]  # Force end at delivery
        else:
            # Emergency fallback if API call failed
            print("WARNING: API call failed, using emergency fallback route")
            outbound_route = [[depot_lat, depot_lon], [delivery_lat, delivery_lon]]
        
        # CREATE RETURN ROUTE: Reverse the same path (excluding delivery point to avoid duplicate)
        # This creates the exact same path but in reverse direction
        return_route = outbound_route[:-1]  # Remove delivery point
        return_route.reverse()  # Reverse the order to go back to depot
        
        # COMBINE: Outbound route + return route (same path, reversed)
        complete_route = outbound_route + return_route
        
        print(f"Complete route: {len(outbound_route)} waypoints to delivery + {len(return_route)} waypoints back = {len(complete_route)} total")
        print(f"Route validation: Starts at {complete_route[0]}, visits delivery at waypoint {len(outbound_route)-1}, ends at {complete_route[-1]}")
        
        # Verify the route starts and ends at depot
        start_matches = (abs(complete_route[0][0] - depot_lat) < 0.0001 and 
                        abs(complete_route[0][1] - depot_lon) < 0.0001)
        end_matches = (abs(complete_route[-1][0] - depot_lat) < 0.0001 and 
                      abs(complete_route[-1][1] - depot_lon) < 0.0001)
        
        # Verify delivery point is visited exactly once
        delivery_visits = 0
        delivery_waypoint_index = -1
        for i, waypoint in enumerate(complete_route):
            if (abs(waypoint[0] - delivery_lat) < 0.0001 and 
                abs(waypoint[1] - delivery_lon) < 0.0001):
                delivery_visits += 1
                if delivery_waypoint_index == -1:
                    delivery_waypoint_index = i
        
        if not start_matches:
            print(f"WARNING: Route does not start exactly at depot!")
        if not end_matches:
            print(f"WARNING: Route does not end exactly at depot!")
        if delivery_visits != 1:
            print(f"WARNING: Delivery point visited {delivery_visits} times instead of exactly once!")
        else:
            print(f"✓ Delivery point visited exactly once at waypoint {delivery_waypoint_index}")
        
        return complete_route

    @staticmethod
    def build_roundtrip_route(depot, delivery, use_drone=True):
        """
        Alias for build_delivery_route() to maintain backward compatibility
        Build a route from depot to delivery and back using the same path
        Vehicle visits delivery point exactly once, then returns via same route
        """
        return RouteManager.build_delivery_route(depot, delivery, use_drone)

    @staticmethod
    def validate_delivery_compliance(route, depot_coords, delivery_coords):
        """
        Validate that a route starts and ends at depot, visits delivery exactly once
        """
        if not route or len(route) < 3:
            return False, "Route is too short for depot->delivery->depot"
        
        depot_lat, depot_lon = depot_coords[0], depot_coords[1]
        delivery_lat, delivery_lon = delivery_coords[0], delivery_coords[1]
        
        # Check start point (should be at depot)
        start_lat, start_lon = route[0][0], route[0][1]
        start_matches = (abs(start_lat - depot_lat) < 0.0001 and 
                        abs(start_lon - depot_lon) < 0.0001)
        
        # Check end point (should be back at depot)
        end_lat, end_lon = route[-1][0], route[-1][1]
        end_matches = (abs(end_lat - depot_lat) < 0.0001 and 
                      abs(end_lon - depot_lon) < 0.0001)
        
        # Count delivery point visits
        delivery_visits = 0
        for waypoint in route:
            if (abs(waypoint[0] - delivery_lat) < 0.0001 and 
                abs(waypoint[1] - delivery_lon) < 0.0001):
                delivery_visits += 1
        
        if start_matches and end_matches and delivery_visits == 1:
            return True, "Route complies: starts/ends at depot, visits delivery exactly once"
        elif not start_matches:
            return False, "Route does not start at depot"
        elif not end_matches:
            return False, "Route does not end at depot"
        elif delivery_visits != 1:
            return False, f"Route visits delivery {delivery_visits} times instead of exactly once"
        else:
            return False, "Route validation failed"

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance between two points on the Earth.
        Returns distance in kilometers.
        """
        R = 6371.0  # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c