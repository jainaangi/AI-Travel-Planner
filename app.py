"""
app.py
Main entry point for the AI Travel Planner Streamlit application.
Run with: streamlit run app.py
"""

import streamlit as st

from config import APP_NAME, APP_ICON, CSS_PATH, LOGO_PATH, AI_ENABLED, WEATHER_API_ENABLED
from utils import init_session_state, load_css, toggle_theme
from database import init_db

# ------------------------------------------------------------------
# Page configuration (must be first Streamlit call)
# ------------------------------------------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Initialize app state & database
# ------------------------------------------------------------------
init_session_state()

try:
    db_ready = init_db()
except Exception as e:
    db_ready = False
    st.error(f"⚠️ Could not initialize the database: {e}")

load_css(CSS_PATH)

# ------------------------------------------------------------------
# Sidebar navigation
# ------------------------------------------------------------------
with st.sidebar:
    try:
        st.image(LOGO_PATH, width=80)
    except Exception:
        st.markdown("### ✈️")

    st.markdown(f"## {APP_NAME}")
    st.caption("Plan smarter. Travel better.")
    st.divider()

    st.page_link("app.py", label="🏠 Home", icon=None)
    st.page_link("pages/Planner.py", label="🗺️ Trip Planner")
    st.page_link("pages/Budget.py", label="💰 Budget & Expenses")
    st.page_link("pages/Trips.py", label="📁 My Trips")
    st.page_link("pages/Chat.py", label="💬 AI Chat Assistant")

    st.divider()

    theme_label = "🌙 Switch to Dark" if st.session_state["theme"] == "light" else "☀️ Switch to Light"
    if st.button(theme_label, use_container_width=True):
        toggle_theme()
        st.rerun()

    st.divider()
    st.caption("**System Status**")
    st.caption(f"{'🟢' if AI_ENABLED else '🟡'} AI Itinerary Engine: {'Gemini' if AI_ENABLED else 'Rule-based (no API key)'}")
    st.caption(f"{'🟢' if WEATHER_API_ENABLED else '🟡'} Weather: {'Live API' if WEATHER_API_ENABLED else 'Estimated (no API key)'}")
    st.caption(f"{'🟢' if db_ready else '🔴'} Database: {'Connected' if db_ready else 'Unavailable'}")

# ------------------------------------------------------------------
# Home page content
# ------------------------------------------------------------------
try:
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-title">{APP_ICON} {APP_NAME}</div>
            <div class="hero-subtitle">Your AI-powered co-pilot for planning unforgettable trips —
            itineraries, budgets, weather, packing lists, and more, all in one place.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
except Exception:
    st.title(f"{APP_ICON} {APP_NAME}")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🗺️ Start Planning a Trip", use_container_width=True):
        st.switch_page("pages/Planner.py")
with col2:
    if st.button("📁 View Saved Trips", use_container_width=True):
        st.switch_page("pages/Trips.py")
with col3:
    if st.button("💬 Ask the AI Assistant", use_container_width=True):
        st.switch_page("pages/Chat.py")

st.markdown("### ✨ What you can do")

features = [
    ("🤖", "AI Itinerary Generator", "Day-by-day plans with activities, food, and photo spots."),
    ("🌦️", "Live Weather Forecasts", "Know what to expect and what to pack before you go."),
    ("🏨", "Hotel & Flight Info", "Curated suggestions with prices and booking links."),
    ("💰", "Smart Budget Planner", "Visual breakdowns across hotels, food, transport & more."),
    ("🧳", "Packing Checklists", "Auto-generated based on weather, duration, and style."),
    ("📤", "Export Anywhere", "Download your itinerary as PDF, CSV, or TXT."),
]

cols = st.columns(3)
for i, (icon, title, desc) in enumerate(features):
    with cols[i % 3]:
        st.markdown(
            f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <h4>{title}</h4>
                <p style="color:#d0d0e0; font-size:0.9rem;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")
st.caption(
    "💡 Tip: Add your GEMINI_API_KEY and OPENWEATHER_API_KEY to a .env file for AI-generated "
    "itineraries and live weather. Without them, the app still works using smart built-in fallbacks."
)
