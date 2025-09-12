


import googlemaps


gmaps = googlemaps.Client(key="AIzaSyDZg6SMkglVT_VlJnPuRM1X55HlWoXQ8XI")

def cel_mai_apropiat_transport(lat, lon):
    
    results = gmaps.places_nearby(
        location=(lat, lon),
        radius=1000,
        type="transit_station"  
    )

    if results.get("results"):
        cea_mai_apropiata = results["results"][0]
        nume = cea_mai_apropiata["name"]
        coord = cea_mai_apropiata["geometry"]["location"]
        cd = (coord['lat'], coord['lng'])
        ch = (lat, lon)
        result = gmaps.distance_matrix(origins=[ch], destinations=[cd], mode="walking")
        distance = result["rows"][0]["elements"][0]["distance"]["text"]
        duration = result["rows"][0]["elements"][0]["duration"]["text"]
        print(f"🚏 Cea mai apropiată stație: {nume}")
        print(f"Distanta este {distance}. Timpul estimat este {duration}")
        #print(f"⭐ Rating: {cea_mai_apropiata.get('rating', 'N/A')}")
    else:
        print("Nu am găsit stații de transport în apropiere.")


#cel_mai_apropiat_transport(48.8566, 2.3522)  # coordonate pentru Paris
