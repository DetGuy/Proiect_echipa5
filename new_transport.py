# functia asta ar trebui sa inlocuiasca functia de transport simplu creata la inceput ca sa functioneze cu noul api de tip json de la google maps!!!!
# NEW TRANSPORT FINDER USING PLACES API (NEW)

import requests
import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()

# Still use googlemaps for distance matrix (it works)
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

def cel_mai_apropiat_transport_new_api(lat, lon, radius=1000):
    """Find nearest transport using the new Places API"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        print("❌ Google Maps API key not found")
        return None
    
    # Use the NEW Places API endpoint
    url = "https://places.googleapis.com/v1/places:searchNearby"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'places.displayName,places.location,places.primaryType,places.types'
    }
    
    # Request body for the new API
    data = {
        "includedTypes": ["transit_station", "bus_station", "subway_station", "train_station"],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lon
                },
                "radius": radius
            }
        }
    }
    
    try:
        print(f"🔍 Searching for transport near {lat}, {lon}...")
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            places = result.get('places', [])
            
            if places:
                # Get the nearest station
                nearest_station = places[0]
                station_name = nearest_station['displayName']['text']
                station_location = nearest_station['location']
                station_lat = station_location['latitude']
                station_lng = station_location['longitude']
                
                print(f"🚇 Found station: {station_name}")
                
                # Calculate distance using Distance Matrix API (this still works)
                distance_result = gmaps.distance_matrix(
                    origins=[(lat, lon)],
                    destinations=[(station_lat, station_lng)],
                    mode="walking"
                )
                
                if distance_result["rows"][0]["elements"][0]["status"] == "OK":
                    element = distance_result["rows"][0]["elements"][0]
                    distance = element["distance"]["text"]
                    duration = element["duration"]["text"]
                    
                    print(f"🚇 Cea mai apropiată stație: {station_name}")
                    print(f"Distanța este {distance}. Timpul estimat este {duration}")
                    
                    return {
                        "station_name": station_name,
                        "distance": distance,
                        "duration": duration,
                        "latitude": station_lat,
                        "longitude": station_lng
                    }
                else:
                    print(f"⚠️  Found station but couldn't calculate distance")
                    return {
                        "station_name": station_name,
                        "distance": "Unknown",
                        "duration": "Unknown"
                    }
            else:
                print("❌ No transit stations found nearby")
                return None
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error in new Places API: {e}")
        return try_fallback_method(lat, lon)

# alta metoda in caz ca nu merge apiul nou incearca cu geocoding

def try_fallback_method(lat, lon):
    """Fallback to a simpler approach using Geocoding API"""
    try:
        print("🔄 Trying fallback method...")
        
        # Use reverse geocoding to get nearby places
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        
        # Try nearby search with a simple HTTP request to a working endpoint
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        
        # Search for nearby transit keywords
        params = {
            'latlng': f'{lat},{lon}',
            'key': api_key,
            'result_type': 'transit_station|bus_station|subway_station'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                station = data['results'][0]
                station_name = station['formatted_address']
                station_location = station['geometry']['location']
                
                print(f"🚇 Fallback found: {station_name}")
                
                # Calculate distance
                distance_result = gmaps.distance_matrix(
                    origins=[(lat, lon)],
                    destinations=[(station_location['lat'], station_location['lng'])],
                    mode="walking"
                )
                
                if distance_result["rows"][0]["elements"][0]["status"] == "OK":
                    element = distance_result["rows"][0]["elements"][0]
                    distance = element["distance"]["text"]
                    duration = element["duration"]["text"]
                    
                    return {
                        "station_name": station_name,
                        "distance": distance,
                        "duration": duration
                    }
        
        print("❌ Fallback method also failed")
        return None
        
    except Exception as e:
        print(f"❌ Fallback method error: {e}")
        return None

def cel_mai_apropiat_transport(lat, lon):
    """Main function - replaces your original function"""
    result = cel_mai_apropiat_transport_new_api(lat, lon)
    
    if not result:
        # If new API fails, return a default response
        print("⚠️  Could not find transport info, using default response")
        return {
            "station_name": "Transport information unavailable",
            "distance": "Unknown",
            "duration": "Unknown"
        }
    
    return result

# Test function
if __name__ == "__main__":
    print("Testing new Places API transport finder...")
    
    # Test with Bucharest coordinates
    result = cel_mai_apropiat_transport(44.4389, 26.1170)
    print(f"\nResult: {result}")
    
    # Test with Paris coordinates  
    print("\n" + "="*50)
    result2 = cel_mai_apropiat_transport(48.8566, 2.3522)
    print(f"\nResult: {result2}")