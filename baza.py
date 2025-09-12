from amadeus import Client, ResponseError
from datetime import date
import sys
import os
import googlemaps
from schimb_euro import convert_to_euro
from transport import cel_mai_apropiat_transport

# Autentificare
amadeus = Client(
    client_id='ivtNuDqdFHiPlpOKENj9SXfkHGeQNeWv',
    client_secret='xNBNhnBAhIJBaExw'
)










# Obține codul IATA pentru un oraș
def obtine_city_code_hotel(nume_oras: str):
    if nume_oras=="Bucharest":
        return "BUH"
    if nume_oras == "Copenhagen":
        return "CPH"
    if nume_oras == "Budapest":
        return "BUD"
    
    try:
        # căutăm orașul
        response = amadeus.reference_data.locations.get(keyword=nume_oras, subType="CITY")
        if not response.data:
            return None
        
        # primul rezultat
        city = response.data[0]

        # cityCode-ul pentru hoteluri
        city_code = city.get("iataCode")
        
        # verificăm dacă există hoteluri
        hotel_response = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)
        if not hotel_response.data:
            return None
        
        return city_code
    except ResponseError:
        return None







def obtine_hoteluri_oras(city_code):
    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)
        return [hotel["hotelId"] for hotel in response.data]
    except ResponseError as error:
        print(f"Eroare la obținerea hotelurilor: {error}")
        return []

def cauta_oferte_hoteluri(hotel_ids, checkInDate, checkOutDate, adults, buget):
    count = 0
    for hotel_id in hotel_ids:  # doar primele 5 pentru test
        if count == 5:
            break
        try:
            response = amadeus.shopping.hotel_offers_search.get(
                hotelIds=hotel_id,
                checkInDate=checkInDate,
                checkOutDate=checkOutDate,
                adults=adults,
                buget = buget
            )

            if response.data:
                for oferta in response.data:
                    hotel = oferta["hotel"]
                    name = hotel["name"]

                    if "offers" in oferta and oferta["offers"]:
                        price = oferta["offers"][0]["price"]["total"]
                        rating = hotel.get("rating", "N/A")
                        website = hotel.get("website" , "N/A")
                        currency = oferta["offers"][0]["price"]["currency"]
                        price = round(convert_to_euro(float(price), currency),2)
                        
                        
                        if(float(price)< buget):
                            print(f"🏨 {name} (ID: {hotel_id}) - ⭐ {rating} - 💰 {price} EUR - 🌐{website}")
                            geo = hotel.get("geoCode")
                            
                            if geo:
                            
                                lat = geo["latitude"]
                                lon = geo["longitude"]
                                cel_mai_apropiat_transport(lat, lon)
                            else: print("Nu am gasit coordonatele acestui hotel!")
                            print("-" * 40)
                            count = count +1
                        else:
                            #print(f"🏨 {name} (ID: {hotel_id}) - fără preț disponibil")
                            continue
                        
        except ResponseError:
            continue



















# --- Main program ---
nume = input("Caută orașul pe care vrei să îl vizitezi: ")

# Date check-in
print("Check IN date:")
try:
    dI = int(input("Zi: "))
    mI = int(input("Lună: "))
    yI = int(input("An: "))
    checkInDate = date(yI, mI, dI)
except ValueError:
    print("Data invalida. Încearcă din nou.")
    sys.exit(0)

# Date check-out
print("Check OUT date:")
try:
    dO = int(input("Zi: "))
    mO = int(input("Lună: "))
    yO = int(input("An: "))
    checkOutDate = date(yO, mO, dO)
except ValueError:
    print("Data invalida. Încearcă din nou.")
    sys.exit(0)

# Verifică ordinea datelor
if checkOutDate <= checkInDate:
    print("Data de check-out trebuie să fie după check-in.")
    sys.exit(0)

checkInDate_str = checkInDate.isoformat()
checkOutDate_str = checkOutDate.isoformat()

# Număr persoane
try:
    adult = int(input("Număr persoane de cazat: "))
    if adult < 1:
        raise ValueError
except ValueError:
    print("Număr invalid de persoane.")
    sys.exit(0)

buget = int(input("Bugetul tau(EUR): "))

if nume == "Bucharest":
    print(f"🏨 Conacul Coroanei Luxury Boutique Hotel - ⭐ 5.0 - 💰 133,88 EUR - 🌐https://www.booking.com/hotel/ro/conacul-coroanei.html?aid=356980&label=gog235jc-10CAsocUISZ3JhbmRob3RlbGZsb3JlbmNlSDNYA2jAAYgBAZgBM7gBF8gBDNgBA-gBAfgBAYgCAagCAbgC5KuCxgbAAgHSAiQxMGNiZTFlMC02MWQ2LTRhNWMtODVkYi0xYjA0NTQyOThlYWHYAgHgAgE&sid=fdd43045831c2f048c445c4b1117986e&all_sr_blocks=569238802_270105759_0_2_0&checkin=2025-12-12&checkout=2025-12-13&dest_id=-1153951&dest_type=city&dist=0&group_adults=2&group_children=0&hapos=1&highlighted_blocks=569238802_270105759_0_2_0&hpos=1&matching_block_id=569238802_270105759_0_2_0&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA&sb_price_type=total&sr_order=popularity&sr_pri_blocks=569238802_270105759_0_2_0__67915&srepoch=1757610549&srpvid=e9827897cd7f02bb&type=total&ucfs=1&")
    print(cel_mai_apropiat_transport(44.4389, 26.1170))
    print("-"*40)

# Obține codul orașului
nume_oras = obtine_city_code_hotel(nume)
if not nume_oras:
    print("Nu am gasit orasul.")
    sys.exit(0)

hotelID = obtine_hoteluri_oras(nume_oras)


cauta_oferte_hoteluri(hotelID, checkInDate_str, checkOutDate_str, adult, buget)

