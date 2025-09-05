"""
HTML templates for map interfaces - FIXED VERSION
"""

# Main application map template with fixed legend
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
  
  /* FIXED LEGEND STYLES */
  .legend-container {
    position: fixed !important;
    bottom: 12px !important;
    left: 12px !important;
    background: rgba(40, 40, 40, 0.95) !important;
    border: 2px solid #ff6b35 !important;
    border-radius: 8px !important;
    padding: 12px !important;
    font-family: 'Arial', sans-serif !important;
    font-size: 12px !important;
    color: white !important;
    z-index: 9999 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
    max-width: 200px !important;
    pointer-events: auto !important;
    user-select: none !important;
    backdrop-filter: blur(10px) !important;
  }

  .legend-container h4 {
    margin: 0 0 8px 0 !important;
    color: #ff6b35 !important;
    font-size: 14px !important;
    font-weight: bold !important;
  }

  .legend-item {
    display: flex !important;
    align-items: center !important;
    margin: 4px 0 !important;
    white-space: nowrap !important;
  }

  .legend-dot {
    width: 12px !important;
    height: 12px !important;
    border-radius: 50% !important;
    margin-right: 8px !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    flex-shrink: 0 !important;
  }

  .legend-dot.drone { background-color: #3b82f6 !important; }
  .legend-dot.electric { background-color: #22c55e !important; }
  .legend-dot.fuel { background-color: #ef4444 !important; }
  .legend-dot.depot { background-color: #f59e0b !important; }
  .legend-dot.delivery { background-color: #8b5cf6 !important; }
</style>
</head>
<body>
<div id="map"></div>

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
  let legendContainer = null;

  function createPersistentLegend() {
    // Remove any existing legend
    if (legendContainer) {
      try {
        document.body.removeChild(legendContainer);
      } catch(e) {}
    }

    // Create new legend container
    legendContainer = document.createElement('div');
    legendContainer.className = 'legend-container';
    
    legendContainer.innerHTML = `
      <h4>Map Legend</h4>
      <div class="legend-item">
        <div class="legend-dot drone"></div>
        <span>Drones (route dotted)</span>
      </div>
      <div class="legend-item">
        <div class="legend-dot electric"></div>
        <span>Electric Truck</span>
      </div>
      <div class="legend-item">
        <div class="legend-dot fuel"></div>
        <span>Fuel Truck</span>
      </div>
      <div class="legend-item">
        <div class="legend-dot depot"></div>
        <span>Selected Depot</span>
      </div>
      <div class="legend-item">
        <div class="legend-dot delivery"></div>
        <span>Delivery Points</span>
      </div>
    `;
    
    // Append to document body
    document.body.appendChild(legendContainer);
    
    return legendContainer;
  }

  function ensureLegendVisibility() {
    if (legendContainer) {
      legendContainer.style.zIndex = '9999';
      legendContainer.style.visibility = 'visible';
      legendContainer.style.display = 'block';
      legendContainer.style.position = 'fixed';
    }
  }

  function initializeMap(mapData) {
    map = L.map('map').setView([mapData.center[0], mapData.center[1]], mapData.zoom);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, 
      attribution: '&copy; OpenStreetMap contributors',
      noWrap: true
    }).addTo(map);

    // Create persistent legend after map initialization
    setTimeout(() => {
      createPersistentLegend();
    }, 500);

    // Ensure legend stays visible during zoom/move events
    map.on('zoom', ensureLegendVisibility);
    map.on('move', ensureLegendVisibility);
    map.on('zoomend', ensureLegendVisibility);
    map.on('moveend', ensureLegendVisibility);

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
      iconColor = '#22c55e'; // green - FIXED: was red, now matches legend
    } else if (type === 'Fuel Truck') {
      iconHtml = '<i class="fa fa-truck"></i>';
      iconColor = '#ef4444'; // red - FIXED: was green, now matches legend
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

    // Ensure legend stays visible after adding vehicles
    setTimeout(ensureLegendVisibility, 100);
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

    // Ensure legend stays visible during updates
    ensureLegendVisibility();
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
    // Ensure legend stays visible
    setTimeout(ensureLegendVisibility, 100);
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
    // Ensure legend stays visible
    setTimeout(ensureLegendVisibility, 100);
  }

  // Periodic visibility check to ensure legend never disappears
  setInterval(ensureLegendVisibility, 2000);

  // Override Leaflet control positioning to maintain legend visibility
  if (window.L && L.Control) {
    const originalOnAdd = L.Control.prototype.onAdd;
    L.Control.prototype.onAdd = function(map) {
      const result = originalOnAdd.call(this, map);
      setTimeout(ensureLegendVisibility, 100);
      return result;
    };
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

# Keep the depot selection template unchanged
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
    position: fixed !important; 
    bottom: 20px !important; 
    left: 20px !important;
    background: rgba(45, 45, 45, 0.95) !important;
    color: white !important;
    padding: 15px !important;
    border-radius: 8px !important;
    font: 12px/1.4 system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid #404040 !important;
    z-index: 9999 !important;
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
</style>
</head>
<body>
<div id="map"></div>



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
    
    // Use same OpenStreetMap tiles as main window
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, 
      attribution: '&copy; OpenStreetMap contributors',
      noWrap: true
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