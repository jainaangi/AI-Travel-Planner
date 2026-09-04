# ✈️ AI Travel Planner

A complete, production-quality AI-powered travel planning web app built with **Streamlit**.
Generate day-by-day itineraries, check live weather, plan and track your budget, build a
packing checklist, chat with an AI travel assistant, and export everything to PDF, CSV, or TXT —
all running locally, with no mandatory external services.

If no API keys are configured, the app automatically falls back to smart, deterministic
logic so **every feature still works out of the box.**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Installation](#installation)
- [API Setup](#api-setup)
- [How to Run](#how-to-run)
- [Screenshots](#screenshots)
- [Future Enhancements](#future-enhancements)

---

## Overview

AI Travel Planner is a multi-page Streamlit application with a glassmorphism-styled,
gradient UI. It lets a traveler enter a trip brief (cities, dates, budget, interests, travel
style) and generates a full itinerary, weather outlook, hotel/flight suggestions, tourist
attractions, restaurant picks, a budget breakdown with charts, an editable expense tracker,
a categorized packing list, travel tips, and an AI chatbot — then saves everything to a
local SQLite database and lets you export it.

## Features

- **🏠 Home Page** — Hero banner, feature highlights, responsive glassmorphism cards.
- **🗺️ AI Trip Planner** — Day-by-day itinerary (morning/afternoon/evening, restaurant,
  travel time, estimated cost, photo spots, notes) via Google Gemini, with an automatic
  rule-based fallback if no API key is set.
- **🌦️ Weather Forecast** — Live temperature, humidity, wind, rain probability, and
  condition via OpenWeatherMap, with a seasonal estimate fallback.
- **🏨 Hotel Recommendations** — Name, rating, price, location, amenities, booking link.
- **✈️ Flight Information** — Airline, departure/arrival, duration, estimated fare.
- **📍 Tourist Attractions** — Description, hours, ticket price, Google Maps link.
- **🍽️ Restaurants** — Breakfast, lunch, dinner, street food, vegetarian, vegan, local cuisine.
- **💰 Budget Planner** — Category breakdown (hotels, flights, food, transport, activities,
  shopping, emergency) with pie and bar charts (Plotly).
- **🧾 Expense Tracker** — Add / edit / delete expenses; remaining budget auto-calculated.
- **🧳 Packing Checklist** — Generated from weather, destination, duration, and travel style.
- **💬 AI Travel Chatbot** — Ask trip questions; Gemini-backed with rule-based fallback.
- **📁 Save & Manage Trips** — View, edit, delete, and search saved trips in SQLite.
- **📤 Export** — Download itineraries as PDF, CSV, or TXT.
- **🛡️ Travel Tips** — Local customs, safety tips, emergency numbers, currency, language,
  scam alerts, useful phrases.
- **🎨 Polished UI** — Gradient backgrounds, rounded glass cards, dark/light theme toggle,
  responsive layout, loading spinners, progress bars, and clear success/error messaging.
- **🛠️ Robust Error Handling** — Handles missing API keys, network failures, invalid inputs,
  and database errors gracefully; the app never crashes.

## Folder Structure

```
AI_Travel_Planner/
│
├── app.py                 # Main entry point / Home page
├── config.py               # Environment variables & app constants
├── database.py              # SQLite schema + CRUD operations
├── ai_planner.py             # Gemini AI itinerary/chat + rule-based fallback
├── weather.py               # OpenWeatherMap integration + fallback estimate
├── budget.py                # Budget breakdown & chart generation
├── packing.py                # Packing checklist generator
├── export.py                 # PDF / CSV / TXT export
├── utils.py                  # Shared helper functions
├── requirements.txt
├── README.md
├── .env.example
├── database/
│   └── travel.db            # Created automatically on first run
├── assets/
│   ├── logo.png
│   ├── hero.jpg
│   └── style.css
└── pages/
    ├── Home.py
    ├── Planner.py
    ├── Budget.py
    ├── Trips.py
    └── Chat.py
```

## Installation

1. **Clone or download** this project folder.
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## API Setup

The app works fully without any API keys (using built-in fallbacks), but for the best
experience, configure the following:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Fill in your keys in `.env`:
   ```
   GEMINI_API_KEY=your_gemini_key_here
   OPENWEATHER_API_KEY=your_openweather_key_here
   ```
   - **Gemini API key:** https://aistudio.google.com/app/apikey
   - **OpenWeatherMap API key:** https://openweathermap.org/api
3. Never commit your real `.env` file — it's excluded via typical `.gitignore` conventions.

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

## Screenshots

> Add screenshots of the Home page, Trip Planner, Budget dashboard, and Chat assistant here
> once you've run the app locally, e.g.:
>
> `![Home Page](assets/screenshots/home.png)`
>
> `![Trip Planner](assets/screenshots/planner.png)`

## Future Enhancements

- Real-time flight and hotel price integration via booking APIs (Skyscanner, Booking.com).
- Multi-user authentication and per-user trip history.
- Collaborative trip planning (shared itineraries).
- Offline map integration and downloadable GPS routes.
- Multi-language support for itineraries and the chatbot.
- Currency conversion using live exchange rates.
- Push/email notifications for upcoming trips and budget alerts.

---

Built with ❤️ using Streamlit, Google Gemini, and OpenWeatherMap.
