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
- Transport Integration: Find nearest public transport stations with walking directions
- Multi-API Integration: Seamless integration of Amadeus and Google Maps APIs
- Hotel Search: Find accommodations by city, budget, dates, and number of guests
- Secure Registration: Email validation and password hashing
- JWT Authentication: Token-based secure login system
- Booking Management: Save favorite hotels with AI explanations
- Search History: Track previous searches automatically

# Requirements & Setup
## Requirements
- Python 3.10+
- pip (Python package manager)
- Git (for cloning the repository)
- A valid Amadeus API key and Google Maps API key

## Setup
pip install -r requirements.txt

It is recommended to use a virtual environment such as conda or venv to work or see this project. We used venv especially for the backend part to keep things organized between multiple projects. To create a Python virtual environment do the following:
- clone the project from github to a specified folder 
- cd backend (navigate to the backend part)
- python3 -m venv venv
- source venv/bin/activate (you also have to have venv installed for this to work)

Create a .env file in the root of the cloned project with all the necessary keys that are used in the project.

- PostgreSQL (for user data and bookings)
- Git (for cloning the repository)
- Valid API Keys:

   - Amadeus Travel API (Client ID & Secret)
   - Google Maps API Key (with Places API New, Distance Matrix, Geocoding)

# BACKLOG

MUST:
- Integration of the Amadeus and Google Maps APIs
- currency conversion(change everything to euro)
- Data user validation
      
SHOULD: 
- Display hotel rating
- Show the nearest public transport station
- Save booking history to a file (preferably .txt)
- Handle errors gracefully and informatively

COULD:
- Offer notifications and alerts
- Tourist suggestions for the selected city


# Implementation roadmap for requirements
## Milestone 1
      - Create a code using Amadeus API that will have the name of a city as an input and return 5 hotels(any) from that city
## Milestone 2
      - Add the feature to input the check in and out dates and check availability during that period (done)
      Using amadeus api for checking and input text from baza.py
## Milestone 3
      - Make the code return the rating and price of each accomodation (done)
      Using amadeus api and baza.py as well as  main.py functions.
## Milestone 4
      - Write a function that will find the nearest transit station to each hotel (done)
      new_transport.py finds all location based pois.
## Milestone 5
      - Convert all currency to euro, regardless of region (done)
      Using the function in schimb_euro.py.
## Milestone 5
      - "Create a User Account" option and add each account to a database (done)
      Users can now create an account to see past bookings and keep their filters from other bookings.
      A user can search for an accomodation wheter it is logged in or not.
      The passwords and sensitive informartion are hashed in the database using a JWT key.
      The ways of transport can also be saved in the user account for selected accomodations/locations.

## Milestone 6
      - Create a user-friendly interface that will make it easier to use the app(frontend)
## Milestone 7
      - Created server that acts as the bridge between frontend and backend: it exposes clean REST API endpoints for auth, hotel search, favorites, and history, while also normalizing data (currency, ratings) before sending it to the UI. It loads environment keys, handles CORS and token-based authentication, and can serve the frontend static files. This ensures the frontend only talks to one consistent API layer, without touching the backend internals.




# Relevant Architecture Documents

Original CLI System
baza.py: Main entry point and hotel search orchestrator
- Interactive CLI interface for user input (city, dates, budget, guests)
- Amadeus API client initialization and hotel search logic
- Currency conversion integration and budget filtering
- Hardcoded city mappings for major destinations (Bucharest, Copenhagen, Budapest)
- Main execution flow with input validation and error handling

transport.py: Google Maps integration for transit discovery
- Places API integration for finding nearby transit stations
- Distance Matrix API for walking time/distance calculations
- Support for multiple transport types (metro, bus, train, subway)
- Error handling with graceful fallbacks for areas with limited transit data

schimb_euro.py: Real-time currency conversion service
- Exchange rate API integration (open.er-api.com)
- Multi-currency support with EUR normalization
- Rate caching mechanism for performance optimization
- Fallback conversion rates for API failures

Modern Web API Architecture
app/main.py: FastAPI application server
- RESTful API endpoints for hotel search and user management
- JWT authentication middleware and protected routes
- CORS configuration for frontend integration
- Request/response validation using Pydantic models
- Integration layer connecting CLI functions to web endpoints

app/models/models.py: Database schema and ORM models
- SQLAlchemy models for users, preferences, search history, saved bookings
- Relational database design with foreign key relationships
- JSON fields for flexible preference and search data storage
- Database connection management and session handling

app/services/auth.py: Authentication and user management service
- Password hashing using bcrypt with salt
- JWT token generation and validation
- User registration with email validation
- Session management and permission control

Enhanced Service Modules
- new_transport.py: Updated Google Places API implementation
- setup_db.py: Database initialization and management

Configuration and Environment
- .env: Environment configuration and API key management
- Database connection strings and credentials


(am mai pus ce mi a dat si claude mai sus daca e sa luati din ele pe la backend sau frontend)
## Foldere BACKEND
- app/main.py: the heart of the backend that compprises classes for the database and all apis
- baza.py: entry point: the main program that gives the info for the hotels in each city
- transport.py and new_transport.py(the new google maps places api): search for the nearest transit station and return the walking duration from hotel to nearest station
- schimb_euro.py: currency conversion
- .env: keeps the API keys private
- server.py: links the frontend with the existing backend logic, exposes REST endpoints for all the main functionalities

  ## Frontend
  - static/index.html: user-friendly frontend interface, allows users to search for hotels, manage favorites, and handle account actions












# Risks and Blockers

## API Limitations
- The biggest blocker for this app is by far Amadeus API: an outdated and slow API. It does not offer the information required for the completion of this project.
- Amamdeus API is very slow.
- Google Maps API Considerations: Legacy API Issues: New Places API migration required. Quota Limits: Daily request limits may impact heavy usage.

## Data availability
- Incomplete or missing hotel data from Amadeus in certain regions.
- Rate Limits: Limited requests per minute on free tier.
- Response Speed: Google Maps api can be slow during peak usage.
- Google Maps may not return nearby transit stations in low-density areas.
- Coverage: Transit data limited in rural/small urban areas.
- API keys and user data require enhanced protection.

## Lack of knowledge in webscripting
- Tried webscraping Booking.com to get more information about hotels from different regions and failed.
- using tools like Selenium can be difficult in webscaping depending on the site visited and its policy. Also in some regions webscraping is prohibited by law.
