from flask import Flask, request, render_template_string, jsonify, send_file
import sqlite3
import os
import io
import requests
from datetime import datetime

# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

# =========================================================
# DATABASE
# =========================================================

DATABASE = "travel.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            days INTEGER NOT NULL,
            budget REAL NOT NULL,
            interests TEXT,
            created_at TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER,
            category TEXT,
            amount REAL,
            description TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# Initialize database
try:
    init_db()
except Exception:
    pass


# =========================================================
# TRIP INPUT VALIDATION
# =========================================================

def validate_trip(destination, days, budget):

    if not destination or not destination.strip():
        return False, "Please enter a destination."

    try:
        days = int(days)
        if days <= 0:
            return False, "Number of days must be greater than 0."
    except (ValueError, TypeError):
        return False, "Please enter a valid number of days."

    try:
        budget = float(budget)
        if budget <= 0:
            return False, "Budget must be greater than 0."
    except (ValueError, TypeError):
        return False, "Please enter a valid budget."

    return True, "Valid"


# =========================================================
# WEATHER DATA
# =========================================================

def get_weather(city):

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return {
            "temperature": "N/A",
            "description": "Weather API key not configured"
        }

    try:
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={api_key}&units=metric"
        )

        response = requests.get(url, timeout=5)

        if response.status_code == 200:

            data = response.json()

            return {
                "temperature": f"{data['main']['temp']}°C",
                "description": data["weather"][0]["description"].title()
            }

    except Exception:
        pass

    return {
        "temperature": "N/A",
        "description": "Weather unavailable"
    }


# =========================================================
# ITINERARY GENERATION
# =========================================================

def generate_itinerary(destination, days, interests):

    destination = destination.strip().title()

    places = {
        "Goa": [
            "Baga Beach",
            "Calangute Beach",
            "Fort Aguada",
            "Dudhsagar Falls",
            "Anjuna Beach",
            "Basilica of Bom Jesus"
        ],

        "Manali": [
            "Solang Valley",
            "Rohtang Pass",
            "Hadimba Temple",
            "Mall Road",
            "Manu Temple",
            "Old Manali"
        ],

        "Mysore": [
            "Mysore Palace",
            "Chamundi Hills",
            "Brindavan Gardens",
            "Mysore Zoo",
            "St. Philomena's Church"
        ],

        "Ooty": [
            "Ooty Lake",
            "Botanical Garden",
            "Doddabetta Peak",
            "Rose Garden",
            "Tea Museum"
        ],

        "Delhi": [
            "India Gate",
            "Red Fort",
            "Qutub Minar",
            "Lotus Temple",
            "Humayun's Tomb"
        ],

        "Mumbai": [
            "Gateway of India",
            "Marine Drive",
            "Elephanta Caves",
            "Juhu Beach",
            "Colaba Causeway"
        ],

        "Bangalore": [
            "Lalbagh Botanical Garden",
            "Bangalore Palace",
            "Cubbon Park",
            "Vidhana Soudha",
            "ISKCON Temple"
        ],

        "Jaipur": [
            "Amber Fort",
            "Hawa Mahal",
            "City Palace",
            "Jantar Mantar",
            "Nahargarh Fort"
        ]
    }

    default_places = [
        f"Explore popular attractions in {destination}",
        "Visit local markets",
        "Try local cuisine",
        "Explore cultural landmarks",
        "Enjoy local activities"
    ]

    destination_places = places.get(destination, default_places)

    itinerary = []

    for day in range(1, days + 1):

        index1 = (day - 1) * 2
        index2 = index1 + 1

        place1 = destination_places[index1 % len(destination_places)]
        place2 = destination_places[index2 % len(destination_places)]

        itinerary.append({
            "day": day,
            "morning": place1,
            "afternoon": place2,
            "evening": "Explore local food and shopping"
        })

    return itinerary


# =========================================================
# PACKING LIST
# =========================================================

def generate_packing_list(weather_description, days):

    items = [
        "Mobile phone",
        "Phone charger",
        "Power bank",
        "Travel documents",
        "Wallet",
        "Basic medicines",
        "Toiletries",
        "Comfortable clothes",
        "Walking shoes"
    ]

    weather = weather_description.lower()

    if "rain" in weather:
        items.extend([
            "Umbrella",
            "Raincoat",
            "Waterproof bag"
        ])

    if any(word in weather for word in ["cold", "snow"]):
        items.extend([
            "Warm jacket",
            "Sweater",
            "Gloves"
        ])

    if any(word in weather for word in ["clear", "sun", "hot"]):
        items.extend([
            "Sunglasses",
            "Sunscreen",
            "Cap"
        ])

    if days >= 5:
        items.append("Extra clothes")

    return list(dict.fromkeys(items))


# =========================================================
# BUDGET ALLOCATION
# =========================================================

def allocate_budget(total_budget):

    return {
        "Hotel": round(total_budget * 0.40, 2),
        "Food": round(total_budget * 0.25, 2),
        "Transport": round(total_budget * 0.20, 2),
        "Activities": round(total_budget * 0.10, 2),
        "Shopping": round(total_budget * 0.05, 2)
    }


# =========================================================
# HOTEL RECOMMENDATION
# =========================================================

def recommend_hotel(budget, days):

    daily_budget = budget / days

    if daily_budget < 1500:
        return {
            "name": "Budget Comfort Hotel",
            "type": "Budget",
            "price": "₹800 - ₹1,500/night"
        }

    elif daily_budget < 3000:
        return {
            "name": "City View Hotel",
            "type": "3-Star",
            "price": "₹1,500 - ₹3,000/night"
        }

    elif daily_budget < 6000:
        return {
            "name": "Premium Stay Resort",
            "type": "4-Star",
            "price": "₹3,000 - ₹6,000/night"
        }

    else:
        return {
            "name": "Luxury Grand Resort",
            "type": "Luxury",
            "price": "₹6,000+/night"
        }


# =========================================================
# CHATBOT
# =========================================================

def chatbot_response(message):

    message = message.lower().strip()

    if "hello" in message or "hi" in message:
        return "Hello! 👋 I am your AI Travel Assistant. How can I help you?"

    if "budget" in message:
        return "I can help divide your budget between hotels, food, transport, activities and shopping."

    if "packing" in message:
        return "I can generate a personalized packing list based on your destination and weather."

    if "hotel" in message:
        return "I recommend hotels according to your total budget and number of travel days."

    if "weather" in message:
        return "Enter your destination in the trip planner to check available weather information."

    if "itinerary" in message or "plan" in message:
        return "Enter your destination, number of days, budget and interests to generate a personalized itinerary."

    if "goa" in message:
        return "Goa is great for beaches, nightlife, water sports and Portuguese heritage."

    if "manali" in message:
        return "Manali is ideal for mountains, adventure activities, nature and scenic views."

    return "I can help with itineraries, hotels, budgets, packing lists and travel suggestions. 😊"


# =========================================================
# SAVE TRIP
# =========================================================

def save_trip(destination, days, budget, interests):

    try:

        conn = get_db()

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO trips
            (destination, days, budget, interests, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            destination,
            days,
            budget,
            interests,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        trip_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return trip_id

    except Exception:
        return None


# =========================================================
# ADD EXPENSE
# =========================================================

def add_expense(trip_id, category, amount, description):

    try:

        conn = get_db()

        conn.execute("""
            INSERT INTO expenses
            (trip_id, category, amount, description, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            trip_id,
            category,
            amount,
            description,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        return True

    except Exception:
        return False


# =========================================================
# MAIN PAGE
# =========================================================

HTML = """

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>AI Travel Planner</title>

<style>

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {

    font-family: Arial, sans-serif;

    background:
    linear-gradient(
        135deg,
        #dbeafe,
        #f0f9ff,
        #ffffff
    );

    color: #1e293b;

}

.navbar {

    background: #0f172a;

    color: white;

    padding: 18px 8%;

    display: flex;

    justify-content: space-between;

    align-items: center;

}

.logo {

    font-size: 24px;

    font-weight: bold;

}

.container {

    width: 90%;

    max-width: 1100px;

    margin: 40px auto;

}

.hero {

    text-align: center;

    margin-bottom: 35px;

}

.hero h1 {

    font-size: 42px;

    margin-bottom: 10px;

}

.hero p {

    font-size: 18px;

    color: #64748b;

}

.card {

    background: white;

    border-radius: 18px;

    padding: 30px;

    margin-bottom: 25px;

    box-shadow:
    0 10px 30px rgba(0,0,0,0.08);

}

.form-grid {

    display: grid;

    grid-template-columns:
    repeat(auto-fit, minmax(220px, 1fr));

    gap: 20px;

}

label {

    display: block;

    font-weight: bold;

    margin-bottom: 7px;

}

input, textarea, select {

    width: 100%;

    padding: 13px;

    border: 1px solid #cbd5e1;

    border-radius: 10px;

    font-size: 15px;

}

textarea {

    resize: vertical;

}

button {

    border: none;

    padding: 14px 25px;

    border-radius: 10px;

    background: #2563eb;

    color: white;

    font-size: 16px;

    cursor: pointer;

}

button:hover {

    background: #1d4ed8;

}

.generate {

    margin-top: 20px;

    width: 100%;

}

.results {

    display: grid;

    grid-template-columns:
    repeat(auto-fit, minmax(250px, 1fr));

    gap: 20px;

}

.result-card {

    background: #f8fafc;

    padding: 20px;

    border-radius: 14px;

    border: 1px solid #e2e8f0;

}

.result-card h3 {

    margin-bottom: 12px;

}

ul {

    padding-left: 20px;

}

li {

    margin: 7px 0;

}

.day {

    border-left: 5px solid #2563eb;

    padding: 18px;

    margin: 15px 0;

    background: #f8fafc;

    border-radius: 10px;

}

.chatbox {

    display: flex;

    gap: 10px;

    margin-top: 15px;

}

.chatbox input {

    flex: 1;

}

#chatResponse {

    margin-top: 15px;

    padding: 15px;

    background: #eff6ff;

    border-radius: 10px;

}

.error {

    background: #fee2e2;

    color: #991b1b;

    padding: 15px;

    border-radius: 10px;

    margin-bottom: 20px;

}

footer {

    text-align: center;

    padding: 30px;

    color: #64748b;

}

</style>

</head>


<body>


<nav class="navbar">

<div class="logo">

✈️ AI Travel Planner

</div>

<div>

Smart • Personalized • Easy

</div>

</nav>


<div class="container">


<div class="hero">

<h1>Plan Your Perfect Trip</h1>

<p>
Create personalized travel plans using AI-powered recommendations.
</p>

</div>


{% if error %}

<div class="error">

{{ error }}

</div>

{% endif %}


<div class="card">

<h2>🌍 Trip Details</h2>

<br>


<form method="POST" action="/plan">


<div class="form-grid">


<div>

<label>Destination</label>

<input
type="text"
name="destination"
placeholder="Example: Goa"
required>

</div>


<div>

<label>Number of Days</label>

<input
type="number"
name="days"
min="1"
placeholder="3"
required>

</div>


<div>

<label>Total Budget (₹)</label>

<input
type="number"
name="budget"
min="1"
placeholder="15000"
required>

</div>


<div>

<label>Interests</label>

<input
type="text"
name="interests"
placeholder="Beaches, Food, Adventure">

</div>


</div>


<button class="generate">

✨ Generate My Travel Plan

</button>


</form>

</div>


{% if plan %}


<div class="card">

<h2>📍 {{ destination }}</h2>

<br>

<div class="results">


<div class="result-card">

<h3>🌤 Weather</h3>

<p>
{{ weather.description }}
</p>

<p>
{{ weather.temperature }}
</p>

</div>


<div class="result-card">

<h3>🏨 Hotel</h3>

<p>
<strong>{{ hotel.name }}</strong>
</p>

<p>
{{ hotel.type }}
</p>

<p>
{{ hotel.price }}
</p>

</div>


<div class="result-card">

<h3>💰 Budget</h3>

<ul>

{% for category, amount in budget_plan.items() %}

<li>
{{ category }}:
₹{{ "%.2f"|format(amount) }}
</li>

{% endfor %}

</ul>

</div>


</div>

</div>


<div class="card">

<h2>🗓 Your Itinerary</h2>


{% for day in plan %}

<div class="day">

<h3>Day {{ day.day }}</h3>

<p>
🌅 <strong>Morning:</strong>
{{ day.morning }}
</p>

<p>
☀️ <strong>Afternoon:</strong>
{{ day.afternoon }}
</p>

<p>
🌆 <strong>Evening:</strong>
{{ day.evening }}
</p>

</div>

{% endfor %}

</div>


<div class="card">

<h2>🎒 Packing List</h2>

<br>

<ul>

{% for item in packing %}

<li>✅ {{ item }}</li>

{% endfor %}

</ul>

</div>


<div class="card">

<h2>💾 Trip Saved</h2>

<p>
Your trip has been successfully saved.
</p>

</div>


{% endif %}


<div class="card">

<h2>🤖 AI Travel Assistant</h2>

<p>
Ask me anything about your trip.
</p>


<div class="chatbox">

<input
id="chatInput"
placeholder="Example: Suggest a budget plan">

<button onclick="sendMessage()">
Ask
</button>

</div>


<div id="chatResponse">

AI Assistant is ready! 👋

</div>

</div>


</div>


<footer>

AI Travel Planner © 2026

</footer>


<script>

async function sendMessage() {

    const input =
        document.getElementById("chatInput");

    const response =
        document.getElementById("chatResponse");

    const message = input.value.trim();

    if (!message) {
        return;
    }

    response.innerHTML = "Thinking... 🤔";

    const result = await fetch("/chat", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            message: message
        })

    });

    const data = await result.json();

    response.innerHTML = data.response;

}

</script>


</body>

</html>

"""


# =========================================================
# HOME ROUTE
# =========================================================

@app.route("/")
def home():

    return render_template_string(
        HTML,
        plan=None,
        error=None
    )


# =========================================================
# PLAN ROUTE
# =========================================================

@app.route("/plan", methods=["POST"])
def plan_trip():

    destination = request.form.get("destination", "")
    days = request.form.get("days", "")
    budget = request.form.get("budget", "")
    interests = request.form.get("interests", "")

    valid, message = validate_trip(
        destination,
        days,
        budget
    )

    if not valid:

        return render_template_string(
            HTML,
            plan=None,
            error=message
        )

    days = int(days)
    budget = float(budget)

    # Weather
    weather = get_weather(destination)

    # Itinerary
    itinerary = generate_itinerary(
        destination,
        days,
        interests
    )

    # Packing
    packing = generate_packing_list(
        weather["description"],
        days
    )

    # Budget
    budget_plan = allocate_budget(budget)

    # Hotel
    hotel = recommend_hotel(
        budget,
        days
    )

    # Save trip
    save_trip(
        destination,
        days,
        budget,
        interests
    )

    return render_template_string(

        HTML,

        plan=itinerary,

        destination=destination,

        weather=weather,

        packing=packing,

        budget_plan=budget_plan,

        hotel=hotel,

        error=None

    )


# =========================================================
# CHATBOT ROUTE
# =========================================================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    message = data.get("message", "")

    response = chatbot_response(message)

    return jsonify({
        "response": response
    })


# =========================================================
# EXPENSE TRACKING
# =========================================================

@app.route("/expense", methods=["POST"])
def expense():

    data = request.get_json()

    trip_id = data.get("trip_id")
    category = data.get("category")
    amount = data.get("amount")
    description = data.get("description", "")

    try:

        amount = float(amount)

    except:

        return jsonify({
            "success": False,
            "message": "Invalid amount"
        })


    success = add_expense(
        trip_id,
        category,
        amount,
        description
    )

    return jsonify({
        "success": success
    })


# =========================================================
# EXPORT ITINERARY
# =========================================================

@app.route("/export")
def export_itinerary():

    destination = request.args.get(
        "destination",
        "Travel Destination"
    )

    days = int(
        request.args.get(
            "days",
            3
        )
    )

    itinerary = generate_itinerary(
        destination,
        days,
        ""
    )

    text = f"AI TRAVEL PLANNER\n"
    text += f"Destination: {destination}\n"
    text += f"Days: {days}\n\n"

    for day in itinerary:

        text += f"DAY {day['day']}\n"
        text += f"Morning: {day['morning']}\n"
        text += f"Afternoon: {day['afternoon']}\n"
        text += f"Evening: {day['evening']}\n\n"

    file = io.BytesIO(
        text.encode("utf-8")
    )

    file.seek(0)

    return send_file(
        file,
        as_attachment=True,
        download_name="travel_itinerary.txt",
        mimetype="text/plain"
    )


# =========================================================
# VERCEL ENTRY POINT
# =========================================================

# IMPORTANT:
# Vercel looks for a top-level variable named "app".
# This line already exists at the top:
#
# app = Flask(__name__)
#
# DO NOT put app inside a function.


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
