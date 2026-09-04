"""
utils.py
Shared utility/helper functions used across the AI Travel Planner app.
"""

import datetime
import urllib.parse
import streamlit as st


def safe_str(value, default="N/A"):
    """Return a safe string representation of a value."""
    if value is None:
        return default
    if isinstance(value, str) and value.strip() == "":
        return default
    return str(value)


def days_between(start_date, end_date):
    """Return the number of days (inclusive) between two dates."""
    try:
        if isinstance(start_date, datetime.date) and isinstance(end_date, datetime.date):
            delta = (end_date - start_date).days
            return max(delta + 1, 1)
        return 1
    except Exception:
        return 1


def format_currency(amount, currency="USD"):
    """Format a numeric amount as a currency string."""
    symbols = {
        "USD": "$", "EUR": "€", "GBP": "£", "INR": "₹",
        "JPY": "¥", "AUD": "A$", "CAD": "C$", "SGD": "S$", "AED": "AED ",
    }
    symbol = symbols.get(currency, currency + " ")
    try:
        return f"{symbol}{amount:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol}0.00"


def google_maps_link(place_name, city=""):
    """Generate a Google Maps search link for a given place."""
    query = f"{place_name}, {city}" if city else place_name
    encoded = urllib.parse.quote_plus(query)
    return f"https://www.google.com/maps/search/?api=1&query={encoded}"

def google_hotel_booking_link(hotel_name, city=""):
    """Generate a generic Google search / booking link for a hotel."""
    query = f"{hotel_name} hotel {city} booking"
    encoded = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?q={encoded}"


def show_success(message):
    """Show a styled success message."""
    st.success(f"✅ {message}")


def show_error(message):
    """Show a styled error message."""
    st.error(f"⚠️ {message}")


def show_info(message):
    """Show a styled info message."""
    st.info(f"ℹ️ {message}")


def show_warning(message):
    """Show a styled warning message."""
    st.warning(f"🔔 {message}")


def load_css(css_path):
    """Load a local CSS file into the Streamlit app safely."""
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Fail silently - app should still work without custom CSS
        pass
    except Exception as e:
        st.warning(f"Could not load styles: {e}")


def init_session_state():
    """Initialize all required keys in Streamlit's session state."""
    defaults = {
        "theme": "dark",
        "trip_generated": False,
        "itinerary": None,
        "trip_details": {},
        "current_trip_id": None,
        "chat_history": [],
        "expenses": [],
        "weather_data": None,
        "packing_list": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def toggle_theme():
    """Toggle between dark and light theme."""
    st.session_state["theme"] = (
        "light" if st.session_state.get("theme") == "dark" else "dark"
    )


def validate_trip_inputs(source, destination, num_days, num_travelers, budget):
    """Validate core trip input fields. Returns (is_valid, error_message)."""
    if not source or not source.strip():
        return False, "Please enter a starting city."
    if not destination or not destination.strip():
        return False, "Please enter a destination."
    if source.strip().lower() == destination.strip().lower():
        return False, "Starting city and destination cannot be the same."
    if not num_days or num_days < 1:
        return False, "Trip duration must be at least 1 day."
    if num_days > 60:
        return False, "Trip duration seems unrealistic (max 60 days)."
    if not num_travelers or num_travelers < 1:
        return False, "Number of travelers must be at least 1."
    if budget is None or budget <= 0:
        return False, "Please enter a valid budget greater than 0."
    return True, ""


def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, avoiding division by zero."""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default
