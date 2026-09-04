"""
export.py
Export a generated itinerary as PDF, CSV, or TXT for download.
"""

import io
import csv
from fpdf import FPDF


def _sanitize(text):
    """Remove characters that fpdf2's default fonts can't render."""
    if text is None:
        return ""
    text = str(text)
    return text.encode("latin-1", "replace").decode("latin-1")


def export_to_pdf(trip_details, itinerary_days):
    """Generate a PDF itinerary and return raw PDF bytes."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, _sanitize("AI Travel Planner - Itinerary"), ln=True, align="C")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 12)
    source = trip_details.get("source", "N/A")
    destination = trip_details.get("destination", "N/A")
    num_days = trip_details.get("num_days", "N/A")
    budget = trip_details.get("budget", "N/A")
    currency = trip_details.get("currency", "")
    travelers = trip_details.get("num_travelers", "N/A")
    style = trip_details.get("travel_style", "N/A")

    summary_lines = [
        f"From: {source}   To: {destination}",
        f"Duration: {num_days} days   Travelers: {travelers}",
        f"Budget: {budget} {currency}   Style: {style}",
    ]
    for line in summary_lines:
        pdf.cell(0, 8, _sanitize(line), ln=True)
    pdf.ln(4)

    for day in itinerary_days:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(230, 230, 250)
        pdf.cell(0, 10, _sanitize(f"Day {day.get('day', '')}"), ln=True, fill=True)

        pdf.set_font("Helvetica", "", 11)
        fields = [
            ("Morning", day.get("morning", "")),
            ("Afternoon", day.get("afternoon", "")),
            ("Evening", day.get("evening", "")),
            ("Restaurant", day.get("restaurant", "")),
            ("Travel Time", day.get("travel_time", "")),
            ("Estimated Cost", day.get("estimated_cost", "")),
            ("Photo Spots", day.get("photo_spots", "")),
            ("Notes", day.get("notes", "")),
        ]
        for label, value in fields:
            pdf.set_font("Helvetica", "B", 11)
            pdf.write(6, _sanitize(f"{label}: "))
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, _sanitize(value))
        pdf.ln(3)

    output = pdf.output(dest="S")
    if isinstance(output, str):
        return output.encode("latin-1", "replace")
    return bytes(output)


def export_to_csv(trip_details, itinerary_days):
    """Generate a CSV itinerary and return it as a string."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Day", "Morning", "Afternoon", "Evening", "Restaurant",
                      "Travel Time", "Estimated Cost", "Photo Spots", "Notes"])
    for day in itinerary_days:
        writer.writerow([
            day.get("day", ""), day.get("morning", ""), day.get("afternoon", ""),
            day.get("evening", ""), day.get("restaurant", ""), day.get("travel_time", ""),
            day.get("estimated_cost", ""), day.get("photo_spots", ""), day.get("notes", ""),
        ])
    return buffer.getvalue()


def export_to_txt(trip_details, itinerary_days):
    """Generate a plain text itinerary and return it as a string."""
    lines = []
    lines.append("=" * 50)
    lines.append("AI TRAVEL PLANNER - ITINERARY")
    lines.append("=" * 50)
    lines.append(f"From: {trip_details.get('source', 'N/A')}")
    lines.append(f"To: {trip_details.get('destination', 'N/A')}")
    lines.append(f"Duration: {trip_details.get('num_days', 'N/A')} days")
    lines.append(f"Travelers: {trip_details.get('num_travelers', 'N/A')}")
    lines.append(f"Budget: {trip_details.get('budget', 'N/A')} {trip_details.get('currency', '')}")
    lines.append(f"Travel Style: {trip_details.get('travel_style', 'N/A')}")
    lines.append("")

    for day in itinerary_days:
        lines.append("-" * 50)
        lines.append(f"DAY {day.get('day', '')}")
        lines.append("-" * 50)
        lines.append(f"Morning: {day.get('morning', '')}")
        lines.append(f"Afternoon: {day.get('afternoon', '')}")
        lines.append(f"Evening: {day.get('evening', '')}")
        lines.append(f"Restaurant: {day.get('restaurant', '')}")
        lines.append(f"Travel Time: {day.get('travel_time', '')}")
        lines.append(f"Estimated Cost: {day.get('estimated_cost', '')}")
        lines.append(f"Photo Spots: {day.get('photo_spots', '')}")
        lines.append(f"Notes: {day.get('notes', '')}")
        lines.append("")

    return "\n".join(lines)
