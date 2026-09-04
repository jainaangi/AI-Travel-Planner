"""
packing.py
Generates a packing checklist based on weather, destination, trip
duration, and travel style.
"""

from config import PACKING_CATEGORIES

_BASE_ITEMS = {
    "Clothes": ["Comfortable walking shoes", "Underwear (enough for each day)", "Sleepwear", "Casual outfits"],
    "Electronics": ["Phone charger", "Power bank", "Universal travel adapter", "Headphones/earphones"],
    "Medicines": ["Personal prescription medicines", "Basic first-aid kit", "Pain relievers", "Motion sickness tablets"],
    "Documents": ["Passport/ID", "Travel insurance papers", "Printed hotel & flight bookings", "Emergency contact list"],
    "Accessories": ["Sunglasses", "Travel pillow", "Daypack/small backpack", "Reusable water bottle"],
    "Toiletries": ["Toothbrush & toothpaste", "Shampoo & soap (travel size)", "Deodorant", "Skincare essentials"],
}

_STYLE_EXTRAS = {
    "Luxury": {"Clothes": ["Formal evening wear", "Dress shoes"], "Accessories": ["Jewelry/watch", "Premium camera"]},
    "Adventure & Outdoors": {"Clothes": ["Quick-dry hiking clothes", "Rain jacket"], "Accessories": ["Hiking boots", "Trekking poles"]},
    "Backpacking": {"Clothes": ["Quick-dry travel clothes", "Compression packing cubes"], "Accessories": ["Padlock", "Money belt"]},
    "Business": {"Clothes": ["Formal business attire", "Ironed shirts"], "Electronics": ["Laptop & charger", "Business cards"]},
    "Family": {"Accessories": ["Kids' entertainment/games", "Snacks for travel"], "Medicines": ["Child-safe medicines"]},
}

_CLIMATE_EXTRAS = {
    "cold": {"Clothes": ["Heavy jacket", "Thermal wear", "Gloves and scarf", "Warm boots"]},
    "hot": {"Clothes": ["Light breathable clothing", "Hat/cap", "Swimwear"], "Toiletries": ["Sunscreen SPF 50+"]},
    "rainy": {"Accessories": ["Compact umbrella", "Waterproof jacket", "Waterproof bag cover"]},
    "mild": {"Clothes": ["Light layers", "A versatile jacket"]},
}


def generate_packing_list(destination, num_days, travel_style, weather_data=None, interests=None):
    """
    Build a categorized packing checklist as a dict:
    {category: [list of items]}
    """
    checklist = {cat: list(items) for cat, items in _BASE_ITEMS.items()}

    if travel_style in _STYLE_EXTRAS:
        for cat, items in _STYLE_EXTRAS[travel_style].items():
            checklist.setdefault(cat, [])
            for item in items:
                if item not in checklist[cat]:
                    checklist[cat].append(item)

    climate_key = "mild"
    if weather_data:
        current = weather_data.get("current", {})
        temp = current.get("temperature", 20) or 20
        rain_prob = current.get("rain_probability", 0) or 0
        if temp <= 10:
            climate_key = "cold"
        elif temp >= 28:
            climate_key = "hot"
        elif rain_prob > 40:
            climate_key = "rainy"

    for cat, items in _CLIMATE_EXTRAS.get(climate_key, {}).items():
        checklist.setdefault(cat, [])
        for item in items:
            if item not in checklist[cat]:
                checklist[cat].append(item)

    if weather_data and (weather_data.get("current", {}).get("rain_probability", 0) or 0) > 40:
        for item in _CLIMATE_EXTRAS["rainy"]["Accessories"]:
            checklist.setdefault("Accessories", [])
            if item not in checklist["Accessories"]:
                checklist["Accessories"].append(item)

    if interests:
        if "Adventure & Outdoors" in interests or "Nature & Wildlife" in interests:
            checklist.setdefault("Accessories", []).append("Insect repellent")
        if "Photography" in interests:
            checklist.setdefault("Electronics", []).append("Camera + extra memory cards")
        if "Nightlife" in interests:
            checklist.setdefault("Clothes", []).append("Smart-casual evening outfit")

    if num_days and num_days >= 7:
        checklist.setdefault("Toiletries", []).append("Laundry bag / travel detergent sheets")

    # Deduplicate while preserving order
    for cat in checklist:
        seen = set()
        deduped = []
        for item in checklist[cat]:
            if item not in seen:
                seen.add(item)
                deduped.append(item)
        checklist[cat] = deduped

    ordered = {cat: checklist.get(cat, []) for cat in PACKING_CATEGORIES}
    return ordered
