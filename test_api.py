#!/usr/bin/env python3
"""
Test your new authentication system
Make sure FastAPI server is running first: uvicorn app.main:app --reload
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_and_search():
    print("🧪 Testing Your Vacation Booking API with Auth")
    print("=" * 60)
    
    # Test 1: Register a user
    print("\n1. Testing User Registration...")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Registration successful: {user['username']} ({user['email']})")
        else:
            print(f"❌ Registration failed: {response.text}")
            if "already registered" in response.text:
                print("   User might already exist, continuing with login test...")
    except requests.exceptions.ConnectionError:
        print("❌ Can't connect to server. Make sure it's running on http://localhost:8000")
        return
    
    # Test 2: Login
    print("\n2. Testing Login...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"✅ Login successful! Token: {access_token[:30]}...")
        else:
            print(f"❌ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 3: Get user profile
    print("\n3. Testing User Profile...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Profile retrieved: {user_info}")
        else:
            print(f"❌ Profile retrieval failed: {response.text}")
    except Exception as e:
        print(f"❌ Profile error: {e}")
    
    # Test 4: Search hotels (guest - no auth)
    print("\n4. Testing Hotel Search (Guest User)...")
    search_data = {
        "city": "Bucharest",
        "budget_eur": 200,
        "check_in": "2024-12-20",
        "check_out": "2024-12-22",
        "adults": 2
    }
    
    try:
        response = requests.post(f"{BASE_URL}/search", json=search_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Guest search successful! Found {len(result.get('hotels', []))} hotels")
            print(f"   User authenticated: {result.get('user_authenticated', False)}")
        else:
            print(f"❌ Guest search failed: {response.text}")
    except Exception as e:
        print(f"❌ Guest search error: {e}")
    
    # Test 5: Search hotels (authenticated user)
    print("\n5. Testing Hotel Search (Authenticated User)...")
    
    try:
        response = requests.post(f"{BASE_URL}/search", json=search_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Authenticated search successful! Found {len(result.get('hotels', []))} hotels")
            print(f"   User authenticated: {result.get('user_authenticated', False)}")
            print(f"   Search saved with ID: {result.get('search_id', 'None')}")
            
            # Save first hotel if available
            hotels = result.get('hotels', [])
            if hotels:
                first_hotel = hotels[0]
                print(f"   First hotel: {first_hotel['name']} - €{first_hotel['price_eur']}")
        else:
            print(f"❌ Authenticated search failed: {response.text}")
    except Exception as e:
        print(f"❌ Authenticated search error: {e}")
    
    # Test 6: Save a booking
    print("\n6. Testing Save Booking...")
    if 'first_hotel' in locals() and first_hotel:
        save_data = {
            "hotel_id": first_hotel["hotel_id"],
            "hotel_name": first_hotel["name"],
            "city": first_hotel["city"],
            "price_eur": first_hotel["price_eur"],
            "rating": first_hotel.get("rating"),
            "website": first_hotel.get("website"),
            "latitude": first_hotel.get("latitude"),
            "longitude": first_hotel.get("longitude"),
            "search_dates": {
                "check_in": search_data["check_in"],
                "check_out": search_data["check_out"],
                "adults": search_data["adults"]
            }
        }
        
        try:
            response = requests.post(f"{BASE_URL}/bookings/save", json=save_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Booking saved! ID: {result.get('booking_id')}")
            else:
                print(f"❌ Save booking failed: {response.text}")
        except Exception as e:
            print(f"❌ Save booking error: {e}")
    else:
        print("⏭️  Skipping save booking test (no hotels found)")
    
    # Test 7: Get saved bookings
    print("\n7. Testing Get Saved Bookings...")
    try:
        response = requests.get(f"{BASE_URL}/bookings/saved", headers=headers)
        if response.status_code == 200:
            result = response.json()
            bookings = result.get('saved_bookings', [])
            print(f"✅ Retrieved {len(bookings)} saved bookings")
            for booking in bookings:
                print(f"   - {booking['hotel_name']} in {booking['city']} (€{booking['price_eur']})")
        else:
            print(f"❌ Get saved bookings failed: {response.text}")
    except Exception as e:
        print(f"❌ Get saved bookings error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 API Testing Complete!")
    print(f"📖 View API docs at: {BASE_URL}/docs")

if __name__ == "__main__":
    print("Make sure your server is running:")
    print("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    input("\nPress Enter to start testing...")
    test_auth_and_search()