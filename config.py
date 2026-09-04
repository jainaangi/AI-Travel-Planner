"""
config.py
Central configuration for the AI Travel Planner application.
Loads environment variables and exposes constants used across the app.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# ------------------------------------------------------------------
# API Keys
# ------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()

# ------------------------------------------------------------------
# Feature flags (auto-computed based on key availability)
# ------------------------------------------------------------------
AI_ENABLED = bool(GEMINI_API_KEY)
WEATHER_API_ENABLED = bool(OPENWEATHER_API_KEY)

# ------------------------------------------------------------------
# App metadata
# ------------------------------------------------------------------
APP_NAME = "AI Travel Planner"
APP_ICON = "✈️"
APP_VERSION = "1.0.0"

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "travel.db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CSS_PATH = os.path.join(ASSETS_DIR, "style.css")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
HERO_PATH = os.path.join(ASSETS_DIR, "hero.jpg")

# Ensure database directory exists
os.makedirs(DATABASE_DIR, exist_ok=True)

# ------------------------------------------------------------------
# Budget categories (used by budget.py and packing.py)
# ------------------------------------------------------------------
BUDGET_CATEGORIES = [
    "Hotels",
    "Flights",
    "Food",
    "Transport",
    "Activities",
    "Shopping",
    "Emergency",
]

DEFAULT_BUDGET_SPLIT = {
    "Hotels": 0.30,
    "Flights": 0.25,
    "Food": 0.15,
    "Transport": 0.10,
    "Activities": 0.12,
    "Shopping": 0.05,
    "Emergency": 0.03,
}

CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "SGD", "AED"]

TRAVEL_STYLES = ["Budget", "Comfort", "Luxury", "Backpacking", "Family", "Business"]

INTERESTS = [
    "History & Culture",
    "Adventure & Outdoors",
    "Food & Cuisine",
    "Nightlife",
    "Shopping",
    "Relaxation & Wellness",
    "Nature & Wildlife",
    "Art & Museums",
    "Photography",
    "Religious & Spiritual",
]

TRANSPORT_MODES = ["Flight", "Train", "Bus", "Car Rental", "Mixed"]

PACKING_CATEGORIES = [
    "Clothes",
    "Electronics",
    "Medicines",
    "Documents",
    "Accessories",
    "Toiletries",
]
