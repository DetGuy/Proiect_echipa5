#!/usr/bin/env python3
"""
Test Google Maps APIs to make sure they're working
"""

import os
import googlemaps
import requests
from dotenv import load_dotenv

load_dotenv()

def test_google_maps():
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_MAPS_API_KEY not found in .env")
        return
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print("=" * 50)
    
    # Test 1: Basic connection
    print("\n1. Testing Google Maps Client...")
    try:
        gmaps = googlemaps.Client(key=api_key)
        print("✅ Google Maps client created successfully")
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return
    
    # Test 2: Geocoding API (most basic)
    print("\n2. Testing Geocoding API...")
    try:
        result = gmaps.geocode("Bucharest, Romania")
        if result:
            location = result[0]['geometry']['location']
            print(f"✅ Geocoding works! Bucharest: {location['lat']}, {location['lng']}")
        else:
            print("❌ Geocoding returned no results")
    except Exception as e:
        print(f"❌ Geocoding failed: {e}")
    
    # Test 3: Distance Matrix API
    print("\n3. Testing Distance Matrix API...")
    try:
        result = gmaps.distance_matrix(
            origins=[(44.4268, 26.1025)],  # Bucharest center
            destinations=[(44.4479, 26.0979)],  # Nearby point
            mode="walking"
        )
        
        if result['rows'][0]['elements'][0]['status'] == 'OK':
            distance = result['rows'][0]['elements'][0]['distance']['text']
            duration = result['rows'][0]['elements'][0]['duration']['text']
            print(f"✅ Distance Matrix works! Distance: {distance}, Duration: {duration}")
        else:
            print("❌ Distance Matrix returned error status")
    except Exception as e:
        print(f"❌ Distance Matrix failed: {e}")
    
    # Test 4: Places API (Text Search)
    print("\n4. Testing Places API (New) - Text Search...")
    try:
        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.id"
        }
        body = {"textQuery": "metro station in Bucharest"}
        resp = requests.post(url, headers=headers, json=body)
        data = resp.json()
        if resp.status_code == 200 and data.get("places"):
            print(f"✅ Places API (New) works! Found: {data['places'][0]['displayName']['text']}")
        else:
            print(f"❌ Places API (New) failed: {resp.text}")
    except Exception as e:
        print(f"❌ Places API (New) call failed: {e}")
    
    # Test 5: Direct HTTP request
    print("\n5. Testing Places API (New) - Nearby Search...")
    try:
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.id"
        }
        body = {
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": 44.4268, "longitude": 26.1025},
                    "radius": 1000.0
                }
            },
            "includedTypes": ["transit_station"]
        }
        resp = requests.post(url, headers=headers, json=body)
        data = resp.json()
        if resp.status_code == 200 and data.get("places"):
            print(f"✅ Nearby Search works! Found: {data['places'][0]['displayName']['text']}")
        else:
            print(f"❌ Nearby Search failed: {resp.text}")
    except Exception as e:
        print(f"❌ Nearby Search call failed: {e}")

    print("\n" + "=" * 50)
    print("🏁 Google Maps API (New) testing complete!")

if __name__ == "__main__":
    test_google_maps()