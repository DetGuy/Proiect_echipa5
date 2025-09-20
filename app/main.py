from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta, date
from typing import Optional
import sys
import os

# Add the parent directory to the path so we can import our existing files
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.models import get_db, create_tables, User, UserPreferences, SavedBooking, SearchHistory
from app.services.auth import (
    authenticate_user, create_user, create_access_token, 
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

# Import your existing functionality
from baza import cauta_oferte_hoteluri, obtine_hoteluri_oras, obtine_city_code_hotel
from new_transport import cel_mai_apropiat_transport #functia veche in caz ca nu merge!!!!
from schimb_euro import convert_to_euro

app = FastAPI(
    title="Vacation Booking API",
    description="AI-powered vacation booking system with authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

class SearchRequest(BaseModel):
    city: str
    budget_eur: float
    check_in: date
    check_out: date
    adults: int = 2

class SaveBookingRequest(BaseModel):
    hotel_id: str
    hotel_name: str
    city: str
    price_eur: float
    rating: Optional[float] = None
    website: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    search_dates: dict

# Dependency to get current user
def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    user = get_current_user(db, token)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

# Optional user dependency (for endpoints that work with or without auth)
def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not credentials:
        return None
    try:
        return get_current_user(db, credentials.credentials)
    except HTTPException:
        return None

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    create_tables()

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    user = create_user(db, user_data.username, user_data.email, user_data.password)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active
    )

@app.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active
    )

# Hotel search endpoints
@app.post("/search")
async def search_hotels(
    search_data: SearchRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Search hotels - works for both guest and authenticated users"""
    try:
        # Get city code
        city_code = obtine_city_code_hotel(search_data.city)
        if not city_code:
            raise HTTPException(status_code=404, detail="City not found")
        
        # Get hotel IDs
        hotel_ids = obtine_hoteluri_oras(city_code)
        if not hotel_ids:
            raise HTTPException(status_code=404, detail="No hotels found")
        
        # Search hotels using your existing function
        check_in_str = search_data.check_in.isoformat()
        check_out_str = search_data.check_out.isoformat()
        
        # Modified version of your hotel search to return data instead of printing
        hotels = []
        count = 0
        
        for hotel_id in hotel_ids:
            if count >= 5:  # Limit results
                break
                
            try:
                from amadeus import Client
                amadeus = Client(
                    client_id=os.getenv("AMADEUS_CLIENT_ID"),
                    client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
                )
                
                response = amadeus.shopping.hotel_offers_search.get(
                    hotelIds=hotel_id,
                    checkInDate=check_in_str,
                    checkOutDate=check_out_str,
                    adults=search_data.adults
                )
                
                if response.data:
                    for oferta in response.data:
                        hotel = oferta["hotel"]
                        name = hotel["name"]
                        
                        if "offers" in oferta and oferta["offers"]:
                            price = oferta["offers"][0]["price"]["total"]
                            rating = hotel.get("rating", "N/A")
                            website = hotel.get("website", "N/A")
                            currency = oferta["offers"][0]["price"]["currency"]
                            price_eur = round(convert_to_euro(float(price), currency), 2)
                            
                            if price_eur <= search_data.budget_eur:
                                hotel_data = {
                                    "hotel_id": hotel_id,
                                    "name": name,
                                    "city": search_data.city,
                                    "price_eur": price_eur,
                                    "rating": rating,
                                    "website": website,
                                    "latitude": None,
                                    "longitude": None,
                                    "transport_info": None
                                }
                                
                                # Get coordinates and transport info
                                geo = hotel.get("geoCode")
                                if geo:
                                    lat = geo["latitude"]
                                    lon = geo["longitude"]
                                    hotel_data["latitude"] = lat
                                    hotel_data["longitude"] = lon
                                    
                                    # Get transport info using your existing function
                                    transport_info = cel_mai_apropiat_transport(lat, lon)
                                    hotel_data["transport_info"] = transport_info
                                
                                hotels.append(hotel_data)
                                count += 1
                                
                                if count >= 5:
                                    break
            except Exception as e:
                continue
        
        # Save search history for logged-in users
        if current_user:
            search_record = SearchHistory(
                user_id=current_user.id,
                city=search_data.city,
                budget=search_data.budget_eur,
                check_in_date=check_in_str,
                check_out_date=check_out_str,
                adults=search_data.adults,
                results_count=len(hotels)
            )
            db.add(search_record)
            db.commit()
        
        return {
            "hotels": hotels,
            "search_id": search_record.id if current_user else None,
            "user_authenticated": current_user is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/bookings/save")
async def save_booking(
    booking_data: SaveBookingRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Save a hotel booking - requires authentication"""
    try:
        saved_booking = SavedBooking(
            user_id=current_user.id,
            hotel_id=booking_data.hotel_id,
            hotel_name=booking_data.hotel_name,
            city=booking_data.city,
            price_eur=booking_data.price_eur,
            rating=booking_data.rating,
            website=booking_data.website,
            latitude=booking_data.latitude,
            longitude=booking_data.longitude,
            search_dates=booking_data.search_dates
        )
        
        db.add(saved_booking)
        db.commit()
        db.refresh(saved_booking)
        
        return {"message": "Booking saved successfully", "booking_id": saved_booking.id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving booking: {str(e)}")

@app.get("/bookings/saved")
async def get_saved_bookings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's saved bookings - requires authentication"""
    try:
        bookings = db.query(SavedBooking).filter(
            SavedBooking.user_id == current_user.id
        ).order_by(SavedBooking.created_at.desc()).all()
        
        return {
            "saved_bookings": [
                {
                    "id": booking.id,
                    "hotel_name": booking.hotel_name,
                    "city": booking.city,
                    "price_eur": booking.price_eur,
                    "rating": booking.rating,
                    "website": booking.website,
                    "saved_at": booking.created_at,
                    "search_dates": booking.search_dates
                }
                for booking in bookings
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bookings: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Vacation Booking API with Authentication!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}