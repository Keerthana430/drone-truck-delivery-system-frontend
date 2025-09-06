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

"""
Optimized Route Manager with performance improvements for large fleets
FIXES: Slow loading, unallocated delivery points, excessive API calls
"""
import math
import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

class RouteManager:
    """Optimized route planning with caching and batch processing"""
    
    # Class-level cache for routes to avoid duplicate API calls
    _route_cache = {}
    _cache_lock = threading.Lock()
    
    @staticmethod
    @lru_cache(maxsize=1000)  # Cache for haversine calculations
    def haversine(lat1, lon1, lat2, lon2):
        """Calculate distance with caching for repeated calculations"""
        R = 6371.0  # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    @staticmethod
    def get_cached_route_key(start_lat, start_lon, end_lat, end_lon, use_drone):
        """Generate cache key for routes"""
        # Round to 4 decimal places to increase cache hits for nearby points
        return f"{round(start_lat,4)}_{round(start_lon,4)}_{round(end_lat,4)}_{round(end_lon,4)}_{use_drone}"
    
    @staticmethod
    def get_osrm_route_cached(start_lat, start_lon, end_lat, end_lon):
        """Get route with caching to avoid duplicate API calls"""
        cache_key = RouteManager.get_cached_route_key(start_lat, start_lon, end_lat, end_lon, False)
        
        with RouteManager._cache_lock:
            if cache_key in RouteManager._route_cache:
                print(f"Using cached route for key: {cache_key}")
                return RouteManager._route_cache[cache_key]
        
        try:
            # OSRM API call with timeout and error handling
            start_coord = f"{start_lon},{start_lat}"
            end_coord = f"{end_lon},{end_lat}"
            url = f"http://router.project-osrm.org/route/v1/driving/{start_coord};{end_coord}"
            
            params = {
                'overview': 'simplified',  # Use simplified instead of full for better performance
                'geometries': 'geojson',
                'steps': 'false'
            }
            
            response = requests.get(url, params=params, timeout=5)  # Reduced timeout
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('routes') and len(data['routes']) > 0:
                    coordinates = data['routes'][0]['geometry']['coordinates']
                    
                    # Optimize point density - take fewer points for performance
                    route_points = []
                    step_size = max(1, len(coordinates) // 10)  # Limit to ~10 points max
                    
                    for i in range(0, len(coordinates), step_size):
                        coord = coordinates[i]
                        route_points.append([coord[1], coord[0]])  # lat, lon
                    
                    # Ensure we have the end point
                    if coordinates:
                        final_coord = coordinates[-1]
                        route_points.append([final_coord[1], final_coord[0]])
                    
                    # Enforce start/end points
                    if route_points:
                        route_points[0] = [start_lat, start_lon]
                        route_points[-1] = [end_lat, end_lon]
                    
                    # Cache the result
                    with RouteManager._cache_lock:
                        RouteManager._route_cache[cache_key] = route_points
                    
                    return route_points
            
            print(f"OSRM API failed with status: {response.status_code}")
            
        except requests.exceptions.Timeout:
            print("OSRM request timeout - using fallback")
        except requests.exceptions.RequestException as e:
            print(f"OSRM request failed: {e}")
        except Exception as e:
            print(f"OSRM routing error: {e}")
        
        # Fallback route
        fallback = RouteManager.create_fast_fallback_route(start_lat, start_lon, end_lat, end_lon)
        
        # Cache the fallback too
        with RouteManager._cache_lock:
            RouteManager._route_cache[cache_key] = fallback
        
        return fallback

    @staticmethod
    def create_fast_fallback_route(start_lat, start_lon, end_lat, end_lon):
        """Fast fallback route with minimal points"""
        # Always start exactly at specified coordinates
        route = [[start_lat, start_lon]]
        
        # Calculate distance to determine intermediate points
        distance = RouteManager.haversine(start_lat, start_lon, end_lat, end_lon)
        
        # Limit intermediate points based on distance for performance
        if distance < 10:
            num_points = 2  # Very short route
        elif distance < 50:
            num_points = 3  # Medium route
        else:
            num_points = 5  # Long route
        
        for i in range(1, num_points):
            t = i / num_points
            lat = start_lat + (end_lat - start_lat) * t
            lon = start_lon + (end_lon - start_lon) * t
            route.append([lat, lon])
        
        # Always end exactly at specified coordinates
        route.append([end_lat, end_lon])
        return route

    @staticmethod
    def create_drone_route_fast(start_lat, start_lon, end_lat, end_lon):
        """Fast drone route with minimal waypoints"""
        cache_key = RouteManager.get_cached_route_key(start_lat, start_lon, end_lat, end_lon, True)
        
        with RouteManager._cache_lock:
            if cache_key in RouteManager._route_cache:
                return RouteManager._route_cache[cache_key]
        
        # Simple 3-point route for drones (start -> end)
        route = [
            [start_lat, start_lon],
            [end_lat, end_lon]
        ]
        
        # Cache it
        with RouteManager._cache_lock:
            RouteManager._route_cache[cache_key] = route
        
        return route

    @staticmethod
    def build_routes_batch(route_requests):
        """Build multiple routes in parallel for better performance"""
        routes = {}
        
        # Separate drone and truck requests
        drone_requests = [(depot, delivery, name) for depot, delivery, name, is_drone in route_requests if is_drone]
        truck_requests = [(depot, delivery, name) for depot, delivery, name, is_drone in route_requests if not is_drone]
        
        print(f"Building routes: {len(drone_requests)} drone routes, {len(truck_requests)} truck routes")
        
        # Process drone routes (fast, no API calls needed)
        for depot, delivery, name in drone_requests:
            try:
                outbound = RouteManager.create_drone_route_fast(
                    depot[0], depot[1], delivery[0], delivery[1]
                )
                # Create return route (reverse path)
                return_route = [[depot[0], depot[1]]]  # Just go straight back
                complete_route = outbound + return_route
                routes[name] = complete_route
            except Exception as e:
                print(f"Error creating drone route for {name}: {e}")
                routes[name] = [[depot[0], depot[1]], [delivery[0], delivery[1]], [depot[0], depot[1]]]
        
        # Process truck routes with limited parallelism to avoid API rate limits
        def build_truck_route(request):
            depot, delivery, name = request
            try:
                outbound = RouteManager.get_osrm_route_cached(
                    depot[0], depot[1], delivery[0], delivery[1]
                )
                if outbound and len(outbound) > 1:
                    # Create return route (reverse the outbound route, excluding delivery point)
                    return_route = outbound[:-1]  # Remove delivery point
                    return_route.reverse()  # Reverse to go back to depot
                    complete_route = outbound + return_route
                else:
                    # Fallback route
                    complete_route = [[depot[0], depot[1]], [delivery[0], delivery[1]], [depot[0], depot[1]]]
                return name, complete_route
            except Exception as e:
                print(f"Error creating truck route for {name}: {e}")
                return name, [[depot[0], depot[1]], [delivery[0], delivery[1]], [depot[0], depot[1]]]
        
        # Use ThreadPoolExecutor with limited workers to avoid overwhelming the API
        if truck_requests:
            max_workers = min(3, len(truck_requests))  # Limit concurrent API calls
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_name = {executor.submit(build_truck_route, req): req[2] for req in truck_requests}
                
                for future in as_completed(future_to_name, timeout=30):  # 30 second timeout total
                    try:
                        name, route = future.result(timeout=10)  # 10 second timeout per route
                        routes[name] = route
                    except Exception as e:
                        name = future_to_name[future]
                        print(f"Route building failed for {name}: {e}")
                        # Use emergency fallback
                        depot, delivery = None, None
                        for dep, del_, n, _ in route_requests:
                            if n == name:
                                depot, delivery = dep, del_
                                break
                        if depot and delivery:
                            routes[name] = [[depot[0], depot[1]], [delivery[0], delivery[1]], [depot[0], depot[1]]]
        
        print(f"Successfully built {len(routes)} routes out of {len(route_requests)} requested")
        return routes

    @staticmethod
    def build_delivery_route(depot, delivery, use_drone=True):
        """Single route building - now uses batch processing internally for consistency"""
        route_requests = [(depot, delivery, "single", use_drone)]
        routes = RouteManager.build_routes_batch(route_requests)
        return routes.get("single", [[depot[0], depot[1]], [delivery[0], delivery[1]], [depot[0], depot[1]]])

    @staticmethod
    def build_roundtrip_route(depot, delivery, use_drone=True):
        """Alias for build_delivery_route() to maintain backward compatibility"""
        return RouteManager.build_delivery_route(depot, delivery, use_drone)


# IMPROVED FLEET ALLOCATION FUNCTION
def create_optimized_fleet(depot_coords, delivery_points, electric_trucks, fuel_trucks, drones):
    """
    Create fleet with improved allocation algorithm and parallel route building
    FIXES: Unallocated delivery points and slow route generation
    """
    print(f"\n=== OPTIMIZED FLEET ALLOCATION ===")
    print(f"Depot: {depot_coords}")
    print(f"Delivery points: {len(delivery_points)}")
    print(f"Fleet config: {electric_trucks}E + {fuel_trucks}F + {drones}D")
    
    vehicles = {}
    total_vehicles = electric_trucks + fuel_trucks + drones
    
    if total_vehicles == 0:
        print("ERROR: No vehicles configured!")
        return vehicles
    
    if len(delivery_points) == 0:
        print("ERROR: No delivery points!")
        return vehicles
    
    # STEP 1: Smart delivery point allocation
    # If we have more vehicles than delivery points, some vehicles will share routes
    # If we have more delivery points than vehicles, prioritize closest points
    
    allocated_deliveries = []
    
    if total_vehicles >= len(delivery_points):
        # More vehicles than delivery points - distribute vehicles among points
        print(f"More vehicles ({total_vehicles}) than delivery points ({len(delivery_points)})")
        print("Some vehicles will be assigned to the same delivery points")
        
        # Assign each delivery point at least once
        for delivery in delivery_points:
            allocated_deliveries.append(delivery)
        
        # Distribute remaining vehicles among delivery points
        remaining_vehicles = total_vehicles - len(delivery_points)
        for i in range(remaining_vehicles):
            allocated_deliveries.append(delivery_points[i % len(delivery_points)])
        
    else:
        # More delivery points than vehicles - select closest points
        print(f"More delivery points ({len(delivery_points)}) than vehicles ({total_vehicles})")
        print("Selecting closest delivery points for assignment")
        
        # Calculate distances and sort by proximity to depot
        deliveries_with_distance = []
        depot_lat, depot_lon = depot_coords
        
        for delivery in delivery_points:
            dist = RouteManager.haversine(depot_lat, depot_lon, delivery[0], delivery[1])
            deliveries_with_distance.append((delivery, dist))
        
        # Sort by distance and take closest points
        deliveries_with_distance.sort(key=lambda x: x[1])
        allocated_deliveries = [d[0] for d in deliveries_with_distance[:total_vehicles]]
        
        unassigned_count = len(delivery_points) - total_vehicles
        print(f"WARNING: {unassigned_count} delivery points will remain unassigned")
    
    print(f"Total delivery assignments: {len(allocated_deliveries)}")
    
    # STEP 2: Create route requests for batch processing
    route_requests = []
    vehicle_assignments = []
    
    # Assign drones first (fastest routes)
    assignment_index = 0
    for i in range(drones):
        if assignment_index >= len(allocated_deliveries):
            break
        name = f"Drone {i+1}"
        delivery = allocated_deliveries[assignment_index]
        route_requests.append((depot_coords, delivery, name, True))  # True = drone
        vehicle_assignments.append((name, "Drone", delivery))
        assignment_index += 1
    
    # Assign electric trucks
    for i in range(electric_trucks):
        if assignment_index >= len(allocated_deliveries):
            break
        name = f"Electric Truck {i+1}"
        delivery = allocated_deliveries[assignment_index]
        route_requests.append((depot_coords, delivery, name, False))  # False = truck
        vehicle_assignments.append((name, "Electric Truck", delivery))
        assignment_index += 1
    
    # Assign fuel trucks
    for i in range(fuel_trucks):
        if assignment_index >= len(allocated_deliveries):
            break
        name = f"Fuel Truck {i+1}"
        delivery = allocated_deliveries[assignment_index]
        route_requests.append((depot_coords, delivery, name, False))  # False = truck
        vehicle_assignments.append((name, "Fuel Truck", delivery))
        assignment_index += 1
    
    print(f"Created {len(route_requests)} route requests")
    
    # STEP 3: Build all routes in parallel (MAJOR PERFORMANCE IMPROVEMENT)
    start_time = time.time()
    routes = RouteManager.build_routes_batch(route_requests)
    route_time = time.time() - start_time
    
    print(f"Route building completed in {route_time:.2f} seconds")
    
    # STEP 4: Create vehicle objects with the built routes
    VEHICLE_SPEEDS = {
        "Drone": 60,
        "Electric Truck": 40,
        "Fuel Truck": 35
    }
    
    VEHICLE_WEIGHTS = {
        "Drone": (1, 5),
        "Electric Truck": (200, 500),
        "Fuel Truck": (300, 700)
    }
    
    for name, vehicle_type, delivery in vehicle_assignments:
        route = routes.get(name)
        if route and len(route) >= 3:  # Valid route: depot -> delivery -> depot
            vehicles[name] = {
                "type": vehicle_type,
                "pos": route[0][:],  # Start at depot
                "route": route,
                "route_index": 0,
                "speed": VEHICLE_SPEEDS[vehicle_type],
                "progress": 0.0,
                "weight": random.randint(*VEHICLE_WEIGHTS[vehicle_type]),
                "assigned_delivery": delivery
            }
            print(f"✓ {name} assigned to {delivery} with {len(route)} waypoints")
        else:
            print(f"✗ Failed to create route for {name}")
    
    # STEP 5: Final allocation summary
    unique_deliveries = set()
    for vehicle in vehicles.values():
        delivery_coords = tuple(vehicle["assigned_delivery"])
        unique_deliveries.add(delivery_coords)
    
    print(f"\n=== FINAL ALLOCATION SUMMARY ===")
    print(f"Successfully created vehicles: {len(vehicles)}")
    print(f"Unique delivery points with vehicles: {len(unique_deliveries)}")
    print(f"Total delivery points available: {len(delivery_points)}")
    print(f"Route building time: {route_time:.2f} seconds")
    
    if len(vehicles) == total_vehicles:
        print("✓ SUCCESS: All configured vehicles created successfully!")
    else:
        print(f"⚠ WARNING: Only {len(vehicles)} out of {total_vehicles} vehicles created")
    
    if len(unique_deliveries) == len(delivery_points):
        print("✓ SUCCESS: All delivery points have vehicles assigned!")
    elif len(delivery_points) > total_vehicles:
        coverage_percent = (len(unique_deliveries) / len(delivery_points)) * 100
        print(f"ℹ INFO: {coverage_percent:.1f}% of delivery points covered (limited by fleet size)")
    
    print("=====================================\n")
    
    return vehicles


# USAGE: Replace the original RouteManager with OptimizedRouteManager in your imports
# Example of how to integrate this into your main application:
"""
# In main_window.py, replace the create_configured_fleet method with:

def create_configured_fleet(self):
    '''Create vehicles based on the configured fleet numbers with optimized performance'''
    self.vehicles.clear()
    
    # Use the optimized fleet creation
    self.vehicles = create_optimized_fleet(
        self.depot_coords,
        self.delivery_points,
        self.electric_trucks,
        self.fuel_trucks,
        self.drones
    )
    
    if self.vehicles:
        self.wave_running = True
        self.wave_start_time = time.time()
        self.send_vehicles_to_js()
        print(f"Optimized fleet created with {len(self.vehicles)} vehicles in seconds, not minutes!")
    else:
        print("Failed to create any vehicles")
"""