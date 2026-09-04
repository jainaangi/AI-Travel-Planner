from packing import generate_packing_list

if __name__ == "__main__":
    sample_weather = {"current": {"temperature": 5, "rain_probability": 10}}
    interests = ["Adventure & Outdoors", "Photography"]
    packing = generate_packing_list("Reykjavik", 10, "Adventure & Outdoors", weather_data=sample_weather, interests=interests)

    for category, items in packing.items():
        print(f"{category}:")
        for it in items:
            print(f" - {it}")
        print()
