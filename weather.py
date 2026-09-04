"""
weather.py
Fetches weather forecast data from OpenWeatherMap.
Falls back to a seasonal estimate if no API key is configured or the
API call fails, so the app always has data to display.
"""

import datetime
import requests

from config import OPENWEATHER_API_KEY, WEATHER_API_ENABLED

GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(destination):
    """
    Return current weather + short forecast for a destination.
    Returns a dict with keys: source, current, forecast (list), error
    """
    if WEATHER_API_ENABLED:
        try:
            result = _get_weather_from_api(destination)
            if result:
                return result
        except requests.exceptions.RequestException as e:
            print(f"Weather API network error, using fallback: {e}")
        except Exception as e:
            print(f"Weather API error, using fallback: {e}")

    return _get_fallback_weather(destination)


def _geocode(destination):
    """Convert a city name to latitude/longitude using OpenWeatherMap geocoding."""
    params = {"q": destination, "limit": 1, "appid": OPENWEATHER_API_KEY}
    resp = requests.get(GEOCODE_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return None, None
    return data[0].get("lat"), data[0].get("lon")


def _get_weather_from_api(destination):
    """Fetch live current weather and 5-day forecast."""
    lat, lon = _geocode(destination)
    if lat is None or lon is None:
        return None

    current_params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    current_resp = requests.get(CURRENT_URL, params=current_params, timeout=15)
    current_resp.raise_for_status()
    current_data = current_resp.json()

    forecast_params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    forecast_resp = requests.get(FORECAST_URL, params=forecast_params, timeout=15)
    forecast_resp.raise_for_status()
    forecast_data = forecast_resp.json()

    current = {
        "temperature": current_data.get("main", {}).get("temp"),
        "feels_like": current_data.get("main", {}).get("feels_like"),
        "humidity": current_data.get("main", {}).get("humidity"),
        "wind_speed": current_data.get("wind", {}).get("speed"),
        "condition": current_data.get("weather", [{}])[0].get("main", "Clear"),
        "description": current_data.get("weather", [{}])[0].get("description", ""),
        "rain_probability": 0,
    }

    daily_forecast = {}
    for entry in forecast_data.get("list", []):
        date_str = entry.get("dt_txt", "").split(" ")[0]
        if not date_str:
            continue
        if date_str not in daily_forecast:
            daily_forecast[date_str] = {
                "date": date_str,
                "temp_min": entry["main"]["temp_min"],
                "temp_max": entry["main"]["temp_max"],
                "humidity": entry["main"]["humidity"],
                "condition": entry["weather"][0]["main"],
                "rain_probability": round(entry.get("pop", 0) * 100),
            }
        else:
            daily_forecast[date_str]["temp_min"] = min(
                daily_forecast[date_str]["temp_min"], entry["main"]["temp_min"]
            )
            daily_forecast[date_str]["temp_max"] = max(
                daily_forecast[date_str]["temp_max"], entry["main"]["temp_max"]
            )

    forecast_list = list(daily_forecast.values())[:5]

    return {
        "source": "api",
        "current": current,
        "forecast": forecast_list,
        "packing_suggestions": _packing_suggestions_from_weather(current),
        "error": None,
    }


def _get_fallback_weather(destination):
    """Generate a reasonable seasonal weather estimate when the API is unavailable."""
    month = datetime.date.today().month
    if month in (12, 1, 2):
        season, base_temp = "Winter", 10
    elif month in (3, 4, 5):
        season, base_temp = "Spring", 20
    elif month in (6, 7, 8):
        season, base_temp = "Summer", 30
    else:
        season, base_temp = "Autumn", 18

    current = {
        "temperature": base_temp,
        "feels_like": base_temp - 1,
        "humidity": 60,
        "wind_speed": 3.5,
        "condition": "Partly Cloudy",
        "description": f"typical {season.lower()} weather (estimated)",
        "rain_probability": 20,
    }

    forecast_list = []
    today = datetime.date.today()
    for i in range(5):
        d = today + datetime.timedelta(days=i)
        forecast_list.append({
            "date": d.isoformat(),
            "temp_min": base_temp - 4,
            "temp_max": base_temp + 4,
            "humidity": 55 + (i % 3) * 5,
            "condition": "Partly Cloudy",
            "rain_probability": 15 + (i % 4) * 10,
        })

    return {
        "source": "estimated",
        "current": current,
        "forecast": forecast_list,
        "packing_suggestions": _packing_suggestions_from_weather(current),
        "error": (
            "Live weather data unavailable (no API key or network issue). "
            f"Showing a seasonal estimate for {season}."
        ),
    }


def _packing_suggestions_from_weather(current):
    """Return packing suggestions based on temperature and conditions."""
    suggestions = []
    temp = current.get("temperature", 20) or 20
    condition = (current.get("condition", "") or "").lower()
    rain_prob = current.get("rain_probability", 0) or 0

    if temp <= 10:
        suggestions += ["Heavy jacket", "Thermal wear", "Gloves and scarf", "Warm boots"]
    elif temp <= 20:
        suggestions += ["Light jacket or sweater", "Long sleeve shirts", "Comfortable layers"]
    else:
        suggestions += ["Light breathable clothing", "Sunscreen", "Sunglasses", "Hat/cap"]

    if rain_prob > 40 or "rain" in condition:
        suggestions += ["Umbrella", "Waterproof jacket", "Waterproof shoe covers"]

    if "snow" in condition:
        suggestions += ["Snow boots", "Insulated gloves"]

    suggestions.append("Reusable water bottle")
    return suggestions
