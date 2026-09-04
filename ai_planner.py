"""
ai_planner.py
Generates AI-powered travel itineraries using Google Gemini.
Falls back to a deterministic rule-based generator if no API key
is configured or if the API call fails for any reason.
"""

import json
import re
import random
import requests

from config import GEMINI_API_KEY, AI_ENABLED

GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


# ------------------------------------------------------------------
# Public entry points
# ------------------------------------------------------------------

def generate_itinerary(trip_details):
    """
    Generate a full day-by-day itinerary for a trip.
    Tries Gemini first (if configured), falls back to rule-based generation.
    Returns a dict: {"source": "ai" | "rule_based", "days": [...]}
    """
    if AI_ENABLED:
        try:
            result = _generate_with_gemini(trip_details)
            if result:
                return {"source": "ai", "days": result}
        except Exception as e:
            print(f"Gemini generation failed, falling back to rule-based: {e}")

    return {"source": "rule_based", "days": _generate_rule_based(trip_details)}


def chat_with_ai(question, trip_context=None):
    """
    Answer a free-form travel question, using Gemini if available,
    otherwise a simple rule-based responder.
    """
    if AI_ENABLED:
        try:
            answer = _chat_with_gemini(question, trip_context)
            if answer:
                return answer
        except Exception as e:
            print(f"Gemini chat failed, falling back to rule-based: {e}")

    return _chat_rule_based(question, trip_context)


# ------------------------------------------------------------------
# Gemini-backed implementation
# ------------------------------------------------------------------

def _call_gemini(prompt, max_tokens=2048, temperature=0.7):
    """Low-level call to the Gemini generateContent endpoint."""
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    response = requests.post(
        GEMINI_URL, headers=headers, params=params, json=payload, timeout=30
    )
    response.raise_for_status()
    data = response.json()
    candidates = data.get("candidates", [])
    if not candidates:
        return None
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    return text.strip() if text else None


def _extract_json(text):
    """Extract a JSON object/array from a model response that may contain
    markdown fences or extra prose."""
    if not text:
        return None
    cleaned = re.sub(r"```json|```", "", text).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None


def _generate_with_gemini(trip_details):
    """Ask Gemini for a structured itinerary and parse the JSON response."""
    num_days = trip_details.get("num_days", 1)
    destination = trip_details.get("destination", "")
    source = trip_details.get("source", "")
    interests = ", ".join(trip_details.get("interests", [])) or "general sightseeing"
    style = trip_details.get("travel_style", "Comfort")
    budget = trip_details.get("budget", 0)
    currency = trip_details.get("currency", "USD")
    travelers = trip_details.get("num_travelers", 1)

    prompt = f"""You are an expert travel planner. Create a detailed {num_days}-day
itinerary for a trip from {source} to {destination}.
Travel style: {style}. Number of travelers: {travelers}.
Total budget: {budget} {currency}. Interests: {interests}.

Respond ONLY with valid JSON (no markdown, no explanation) in exactly this format:
[
  {{
    "day": 1,
    "morning": "activity description",
    "afternoon": "activity description",
    "evening": "activity description",
    "restaurant": "recommended restaurant name and cuisine",
    "travel_time": "estimated travel time between activities",
    "estimated_cost": 100,
    "photo_spots": "best photo spot for the day",
    "notes": "helpful note for the day"
  }}
]

Include exactly {num_days} day objects. estimated_cost must be a number in {currency}."""

    text = _call_gemini(prompt, max_tokens=4096, temperature=0.8)
    parsed = _extract_json(text)
    if not parsed or not isinstance(parsed, list):
        return None

    days = []
    for i, item in enumerate(parsed[:num_days], start=1):
        days.append({
            "day": item.get("day", i),
            "morning": item.get("morning", "Free time to explore"),
            "afternoon": item.get("afternoon", "Free time to explore"),
            "evening": item.get("evening", "Relax and enjoy local culture"),
            "restaurant": item.get("restaurant", "Local recommended restaurant"),
            "travel_time": item.get("travel_time", "30 mins"),
            "estimated_cost": item.get("estimated_cost", 0),
            "photo_spots": item.get("photo_spots", "City center"),
            "notes": item.get("notes", ""),
        })
    return days if days else None


def _chat_with_gemini(question, trip_context):
    """Ask Gemini a free-form question with optional trip context."""
    context_str = ""
    if trip_context:
        context_str = f"""
Trip context:
Destination: {trip_context.get('destination', 'N/A')}
Duration: {trip_context.get('num_days', 'N/A')} days
Budget: {trip_context.get('budget', 'N/A')} {trip_context.get('currency', '')}
Travel style: {trip_context.get('travel_style', 'N/A')}
"""
    prompt = f"""You are a helpful, friendly AI travel assistant.
{context_str}
Answer the user's question concisely and helpfully (max 150 words):
Question: {question}
"""
    return _call_gemini(prompt, max_tokens=512, temperature=0.7)


# ------------------------------------------------------------------
# Rule-based fallback implementation
# ------------------------------------------------------------------

_MORNING_ACTIVITIES = [
    "Explore the historic city center and main landmarks",
    "Visit the top-rated local museum",
    "Take a guided walking tour of the old town",
    "Relax at a scenic viewpoint with morning coffee",
    "Explore local markets and street vendors",
    "Visit a famous temple, cathedral, or monument",
]

_AFTERNOON_ACTIVITIES = [
    "Visit a popular tourist attraction and nearby shops",
    "Enjoy a boat ride or scenic nature trail",
    "Explore art galleries and cultural centers",
    "Try local adventure activities (hiking, biking, watersports)",
    "Shop at the main commercial district",
    "Visit a botanical garden or city park",
]

_EVENING_ACTIVITIES = [
    "Enjoy a sunset view from a rooftop or viewpoint",
    "Experience the local nightlife and entertainment district",
    "Attend a cultural show or live music performance",
    "Relax with a leisurely walk along the waterfront",
    "Enjoy a traditional dinner with local performances",
    "Visit a night market for food and souvenirs",
]

_RESTAURANTS = [
    "The Local Kitchen (Regional Cuisine)",
    "Sunset Bistro (International Fusion)",
    "Heritage Dining House (Traditional Cuisine)",
    "Spice Route Café (Local Street Food)",
    "Garden Terrace Restaurant (Continental)",
    "Old Town Eatery (Authentic Local Dishes)",
]

_PHOTO_SPOTS = [
    "City skyline viewpoint",
    "Historic old town square",
    "Waterfront promenade",
    "Iconic landmark entrance",
    "Local market street",
    "Scenic hilltop lookout",
]

_NOTES = [
    "Carry a water bottle and comfortable walking shoes.",
    "Book tickets online in advance to skip queues.",
    "Local currency is preferred for small vendors.",
    "Check opening hours before visiting, some sites close on Mondays.",
    "Great day for photography, aim for golden hour light.",
    "Consider hiring a local guide for deeper cultural insight.",
]


def _generate_rule_based(trip_details):
    """Deterministic itinerary generator used when no AI key is present."""
    num_days = max(int(trip_details.get("num_days", 1) or 1), 1)
    budget = float(trip_details.get("budget", 0) or 0)
    per_day_budget = round(budget / num_days, 2) if num_days > 0 else 0

    days = []
    for day_num in range(1, num_days + 1):
        idx = (day_num - 1) % len(_MORNING_ACTIVITIES)
        days.append({
            "day": day_num,
            "morning": _MORNING_ACTIVITIES[idx],
            "afternoon": _AFTERNOON_ACTIVITIES[idx],
            "evening": _EVENING_ACTIVITIES[idx],
            "restaurant": _RESTAURANTS[idx],
            "travel_time": f"{random.choice([15, 20, 30, 45])} mins between stops",
            "estimated_cost": round(per_day_budget * 0.8, 2) if per_day_budget else 50.0,
            "photo_spots": _PHOTO_SPOTS[idx],
            "notes": _NOTES[idx],
        })
    return days


def _chat_rule_based(question, trip_context):
    """Simple keyword-matching responder used when no AI key is present."""
    q = question.lower().strip()
    destination = trip_context.get("destination", "your destination") if trip_context else "your destination"
    num_days = trip_context.get("num_days") if trip_context else None

    if "pack" in q:
        return (
            f"For {destination}, pack weather-appropriate clothing, comfortable walking shoes, "
            "a universal adapter, any required medicines, copies of your documents, and a "
            "reusable water bottle. Check the Packing tab for a full checklist tailored to your trip."
        )
    if "money" in q or "budget" in q or "cost" in q or "cash" in q:
        return (
            "A good rule of thumb is to carry small local currency for daily expenses and street food, "
            "keep a card for larger purchases, and set aside an emergency fund of about 10-15% of your "
            "total budget. Check the Budget tab for a full breakdown."
        )
    if "food" in q or "eat" in q or "restaurant" in q:
        return (
            f"In {destination}, try the local specialties at highly-rated neighborhood restaurants, "
            "explore street food markets for authentic flavors, and ask locals for hidden-gem "
            "recommendations away from tourist zones."
        )
    day_match = re.search(r"day\s*(\d+)", q)
    if day_match and num_days:
        day_num = int(day_match.group(1))
        if 1 <= day_num <= int(num_days):
            return (
                f"On Day {day_num}, check your itinerary in the Planner tab for the full "
                "morning, afternoon, and evening schedule with restaurant picks and photo spots."
            )
        return f"Your trip is only {num_days} day(s) long, so Day {day_num} isn't part of this itinerary."
    if "weather" in q:
        return "Check the Weather tab for a live forecast including temperature, humidity, and rain probability."
    if "safe" in q or "safety" in q:
        return (
            "Stay aware of your surroundings, keep valuables secure, avoid poorly lit areas at night, "
            "keep copies of important documents, and save local emergency numbers before you travel."
        )
    return (
        "I can help with itinerary questions, packing tips, budget guidance, food recommendations, "
        "and safety advice. Try asking something like 'What should I do on Day 2?' or 'Best local food?'"
    )
