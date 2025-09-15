# Proiect_echipa5

This project is a Python-based application designed to assist users in identifying available hotel accommodations within a selected city, based on their budget and travel dates. By integrating the Amadeus API for lodging offers and the Google Maps API for locating nearby transit stations, the application provides an intelligent solution for urban travel planning. The output includes hotel prices converted to EURO, user ratings, and walking distances to the nearest public transportation options.

## Tech stack
- **Frontend**:
- **APIs**: Amadeus, Google Maps
- **Database**:
- **Programming language used for backend**: Python 3.13.0

## Features
- Sign up/in/out
- Simple UI
- "My Account" page:
- Add to favourites

# Requirements & Setup
## Requirements
- Python 3.10+
- pip (Python package manager)
- Git (for cloning the repository)
- A valid Amadeus API key and Google Maps API key

## Setup
pip install -r requirements.txt





# BACKLOG

MUST:
- Integrarea API-uirlor Amadeus si Google Maps
- conversie valutara(pentru aceasta aplicatie orice moneda este schimbata in euro)
- Validare date utilizator
      
SHOULD: 
- Afisare rating hotel
- Afisare cea mai apropiata statie
- Un fisiera (de preferat .txt) in care sa fie salvat istoricul de cazari
- Tratarea erorilor intr-un mod elegant

COULD:
- Notificari reduceri
- Sugestii turistice pentru orasul pe care dorim sa il vizitam


# Implementation roadmap for requirements
## Milestone 1
      - Create a code using Amadeus API that will have the name of a city as an input and return 5 hotels(any) from that city
## Milestone 2
      - Add the feature to input the check in and out dates and check availability during that period
## Milestone 3
      - Make the code return the rating and price of each accomodation
## Milestone 4
      - Write a function that will find the nearest transit station to each hotel
## Milestone 5
      - Convert all currency to euro, regardless of region
## Milestone 5
      - "Create a User Account" option and add each account to a database
## Milestone 6
      - Create a user-friendly interface that will make it easier to use the app(frontend)
## Milestone 7
      - link everything together

# Relevant Architecture Documents

## Foldere BACKEND
- baza.py: punctul de intrare, interacțiune cu utilizatorul
- transport.py: caută stații de transport și calculează distanțe
- schimb_euro.py: conversie valutară
- .env: stochează cheile API





# **!!VA LAS AICI CE MI-A ZIS CHATUL SA SCRIETI PENTRU DUPA CE VA FI GATA PROIECTUL!!**
📐 Ce ar trebui să conțină
1. Diagramă de arhitectură
Un desen simplu (poate fi PNG sau făcut în draw.io) care arată:

Utilizatorul → Interfața CLI

Modulele Python (baza.py, transport.py, schimb_euro.py)

API-urile externe (Amadeus, Google Maps)

Fișierul .env pentru chei

Fluxul de date între componente

2. Descrierea modulelor
Ce face fiecare fișier:

baza.py: punctul de intrare, interacțiune cu utilizatorul

transport.py: caută stații de transport și calculează distanțe

schimb_euro.py: conversie valutară

.env: stochează cheile API

3. Fluxul aplicației
Pașii logici:

Utilizatorul introduce orașul, datele și bugetul

Se interoghează Amadeus pentru hoteluri

Se calculează distanța până la stația de transport

Se convertesc prețurile în euro

Se afișează rezultatele










# Risks and Blockers

## API Limitations
The biggest blocker for this app is by far Amadeus API: an outdated and slow API. It does not offer the information required for the completion of this project.

## Data availability
- Incomplete or missing hotel data from Amadeus in certain regions.
- Google Maps may not return nearby transit stations in low-density areas.

## Lack of knowledge in webscripting
- Tried webscraping Booking.com to get more information about hotels from different regions and failed.
