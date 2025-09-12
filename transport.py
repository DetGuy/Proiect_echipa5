
#PROGRAM PENTRU A AFLA CEL MAI APROPIAT MIJLOC DE TRANSPORT

import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()

gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

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
        cd = (coord['lat'], coord['lng']) #coordonate destinatie
        ch = (lat, lon) #coordonate hotel
        result = gmaps.distance_matrix(origins=[ch], destinations=[cd], mode="walking")
        distance = result["rows"][0]["elements"][0]["distance"]["text"]
        duration = result["rows"][0]["elements"][0]["duration"]["text"]
        print(f"🚏 Cea mai apropiată stație: {nume}")
        print(f"Distanta este {distance}. Timpul estimat este {duration}")
        
    else:
        print("Nu am găsit stații de transport în apropiere.")


#cel_mai_apropiat_transport(48.8566, 2.3522)  # coordonate pentru Paris
