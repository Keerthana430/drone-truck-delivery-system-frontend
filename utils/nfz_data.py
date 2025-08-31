"""
No-fly zone data for India airspace
"""

def get_india_no_fly_zones():
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
        
        # Additional zones
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
        
        # More strategic locations
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
        }
    ]

def get_depot_selection_no_fly_zones():
    """Get major no-fly zones for depot selection"""
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
        
        # Additional zones
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
        
        # More strategic locations
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
        }
    ]