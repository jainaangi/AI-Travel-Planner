"""
budget.py
Budget breakdown, allocation, and expense analysis logic.
"""

import pandas as pd
import plotly.express as px

from config import BUDGET_CATEGORIES, DEFAULT_BUDGET_SPLIT
from utils import safe_divide


def calculate_budget_breakdown(total_budget, custom_split=None):
    """
    Split a total budget across categories.
    Returns a dict: {category: allocated_amount}
    """
    split = custom_split or DEFAULT_BUDGET_SPLIT
    try:
        total_budget = float(total_budget)
    except (TypeError, ValueError):
        total_budget = 0.0

    breakdown = {}
    for category in BUDGET_CATEGORIES:
        pct = split.get(category, 0)
        breakdown[category] = round(total_budget * pct, 2)
    return breakdown


def breakdown_to_dataframe(breakdown, currency="USD"):
    """Convert a budget breakdown dict into a pandas DataFrame for display."""
    rows = [{"Category": cat, "Allocated Amount": amt, "Currency": currency}
            for cat, amt in breakdown.items()]
    return pd.DataFrame(rows)


def make_pie_chart(breakdown, title="Budget Allocation"):
    """Return a Plotly pie chart figure for the budget breakdown."""
    df = pd.DataFrame({"Category": list(breakdown.keys()), "Amount": list(breakdown.values())})
    fig = px.pie(
        df, names="Category", values="Amount", title=title, hole=0.4,
        color_discrete_sequence=px.colors.sequential.Sunsetdark,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
    )
    return fig


def make_bar_chart(breakdown, title="Budget by Category"):
    """Return a Plotly bar chart figure for the budget breakdown."""
    df = pd.DataFrame({"Category": list(breakdown.keys()), "Amount": list(breakdown.values())})
    fig = px.bar(
        df, x="Category", y="Amount", title=title, color="Category",
        color_discrete_sequence=px.colors.sequential.Sunsetdark, text_auto=".2s",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        showlegend=False,
    )
    return fig


def make_expense_vs_budget_chart(breakdown, spent_by_category, title="Budget vs Actual Spend"):
    """Return a grouped bar chart comparing allocated budget vs actual spend."""
    categories = list(breakdown.keys())
    allocated = [breakdown.get(c, 0) for c in categories]
    spent = [spent_by_category.get(c, 0) for c in categories]

    df = pd.DataFrame({
        "Category": categories * 2,
        "Amount": allocated + spent,
        "Type": ["Allocated"] * len(categories) + ["Spent"] * len(categories),
    })
    fig = px.bar(
        df, x="Category", y="Amount", color="Type", barmode="group", title=title,
        color_discrete_map={"Allocated": "#4facfe", "Spent": "#f5576c"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
    )
    return fig


def calculate_spent_by_category(expenses):
    """Sum expense amounts grouped by category. expenses: list of dicts with 'category', 'amount'."""
    result = {cat: 0.0 for cat in BUDGET_CATEGORIES}
    for exp in expenses:
        cat = exp.get("category", "Other")
        amt = exp.get("amount", 0) or 0
        result[cat] = result.get(cat, 0.0) + float(amt)
    return result


def calculate_remaining_budget(total_budget, expenses):
    """Return (total_spent, remaining_budget, percent_used)."""
    try:
        total_budget = float(total_budget)
    except (TypeError, ValueError):
        total_budget = 0.0

    total_spent = sum(float(e.get("amount", 0) or 0) for e in expenses)
    remaining = round(total_budget - total_spent, 2)
    percent_used = round(safe_divide(total_spent, total_budget, 0) * 100, 1)
    return round(total_spent, 2), remaining, percent_used
