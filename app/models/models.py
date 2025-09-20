from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Float, Text, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://andrei:2004@localhost/vacation_booking_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    preferences = relationship("UserPreferences", back_populates="user")
    searches = relationship("SearchHistory", back_populates="user")
    saved_bookings = relationship("SavedBooking", back_populates="user")

# User preferences model
class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    preferred_cities = Column(JSON, default=["Bucharest", "Copenhagen", "Budapest"])
    budget_range = Column(JSON, default={"min": 50, "max": 300})
    preferred_amenities = Column(JSON, default=["wifi", "breakfast"])
    distance_preference = Column(Integer, default=1000)  # meters
    minimum_rating = Column(Float, default=3.0)
    adults_default = Column(Integer, default=2)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="preferences")

# Search history model
class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    city = Column(String, nullable=False)
    budget = Column(Float, nullable=False)
    check_in_date = Column(String, nullable=False)
    check_out_date = Column(String, nullable=False)
    adults = Column(Integer, default=2)
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="searches")

# Saved bookings model
class SavedBooking(Base):
    __tablename__ = "saved_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    hotel_id = Column(String, nullable=False)  # From Amadeus
    hotel_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    price_eur = Column(Float, nullable=False)
    rating = Column(Float)
    website = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    nearest_transport = Column(String)
    transport_distance = Column(String)
    transport_duration = Column(String)
    search_dates = Column(JSON)  # {"check_in": "2024-12-12", "check_out": "2024-12-13"}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="saved_bookings")

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)