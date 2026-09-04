"""
database.py
SQLite database layer for the AI Travel Planner.
Handles trip storage and expense tracking using parameterized queries.
"""

import sqlite3
import json
import datetime
from contextlib import contextmanager

from config import DATABASE_PATH


@contextmanager
def get_connection():
    """Context manager that yields a SQLite connection and ensures it closes."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=10, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    finally:
        if conn:
            conn.close()


def init_db():
    """Create the required tables if they do not already exist."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS trips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    num_days INTEGER,
                    num_travelers INTEGER,
                    budget REAL,
                    currency TEXT,
                    travel_style TEXT,
                    interests TEXT,
                    transport_mode TEXT,
                    itinerary_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trip_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    amount REAL NOT NULL,
                    expense_date TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_expenses_trip_id ON expenses (trip_id)")
        return True
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return False


def save_trip(trip_data, itinerary):
    """Insert a new trip record. Returns the new trip id, or None on failure."""
    try:
        now = datetime.datetime.now().isoformat()
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO trips (
                    source, destination, start_date, end_date, num_days,
                    num_travelers, budget, currency, travel_style, interests,
                    transport_mode, itinerary_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trip_data.get("source", ""),
                trip_data.get("destination", ""),
                str(trip_data.get("start_date", "")),
                str(trip_data.get("end_date", "")),
                trip_data.get("num_days", 0),
                trip_data.get("num_travelers", 1),
                trip_data.get("budget", 0.0),
                trip_data.get("currency", "USD"),
                trip_data.get("travel_style", ""),
                json.dumps(trip_data.get("interests", [])),
                trip_data.get("transport_mode", ""),
                json.dumps(itinerary or {}),
                now, now,
            ))
            return cur.lastrowid
    except Exception as e:
        print(f"Failed to save trip: {e}")
        return None


def update_trip(trip_id, trip_data, itinerary=None):
    """Update an existing trip record."""
    try:
        now = datetime.datetime.now().isoformat()
        with get_connection() as conn:
            cur = conn.cursor()
            if itinerary is not None:
                cur.execute("""
                    UPDATE trips SET source=?, destination=?, start_date=?, end_date=?,
                        num_days=?, num_travelers=?, budget=?, currency=?, travel_style=?,
                        interests=?, transport_mode=?, itinerary_json=?, updated_at=?
                    WHERE id=?
                """, (
                    trip_data.get("source", ""), trip_data.get("destination", ""),
                    str(trip_data.get("start_date", "")), str(trip_data.get("end_date", "")),
                    trip_data.get("num_days", 0), trip_data.get("num_travelers", 1),
                    trip_data.get("budget", 0.0), trip_data.get("currency", "USD"),
                    trip_data.get("travel_style", ""), json.dumps(trip_data.get("interests", [])),
                    trip_data.get("transport_mode", ""), json.dumps(itinerary),
                    now, trip_id,
                ))
            else:
                cur.execute("""
                    UPDATE trips SET source=?, destination=?, start_date=?, end_date=?,
                        num_days=?, num_travelers=?, budget=?, currency=?, travel_style=?,
                        interests=?, transport_mode=?, updated_at=?
                    WHERE id=?
                """, (
                    trip_data.get("source", ""), trip_data.get("destination", ""),
                    str(trip_data.get("start_date", "")), str(trip_data.get("end_date", "")),
                    trip_data.get("num_days", 0), trip_data.get("num_travelers", 1),
                    trip_data.get("budget", 0.0), trip_data.get("currency", "USD"),
                    trip_data.get("travel_style", ""), json.dumps(trip_data.get("interests", [])),
                    trip_data.get("transport_mode", ""), now, trip_id,
                ))
            return True
    except Exception as e:
        print(f"Failed to update trip: {e}")
        return False


def get_all_trips():
    """Return a list of all saved trips (most recent first)."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM trips ORDER BY created_at DESC")
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Failed to fetch trips: {e}")
        return []


def get_trip_by_id(trip_id):
    """Return a single trip by id, or None if not found."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    except Exception as e:
        print(f"Failed to fetch trip: {e}")
        return None


def search_trips(keyword):
    """Search trips by destination or source city."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            like_term = f"%{keyword}%"
            cur.execute("""
                SELECT * FROM trips
                WHERE destination LIKE ? OR source LIKE ?
                ORDER BY created_at DESC
            """, (like_term, like_term))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Failed to search trips: {e}")
        return []


def delete_trip(trip_id):
    """Delete a trip and its associated expenses."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM expenses WHERE trip_id = ?", (trip_id,))
            cur.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
            return True
    except Exception as e:
        print(f"Failed to delete trip: {e}")
        return False


# ------------------------------------------------------------------
# Expense operations
# ------------------------------------------------------------------

def add_expense(trip_id, category, description, amount, expense_date=None):
    """Add a new expense record for a trip."""
    try:
        now = datetime.datetime.now().isoformat()
        expense_date = expense_date or datetime.date.today().isoformat()
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO expenses (trip_id, category, description, amount, expense_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (trip_id, category, description, float(amount), str(expense_date), now))
            return cur.lastrowid
    except Exception as e:
        print(f"Failed to add expense: {e}")
        return None


def get_expenses(trip_id):
    """Return all expenses for a given trip."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM expenses WHERE trip_id = ? ORDER BY expense_date DESC", (trip_id,))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Failed to fetch expenses: {e}")
        return []


def update_expense(expense_id, category, description, amount, expense_date):
    """Update an existing expense."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE expenses SET category=?, description=?, amount=?, expense_date=?
                WHERE id=?
            """, (category, description, float(amount), str(expense_date), expense_id))
            return True
    except Exception as e:
        print(f"Failed to update expense: {e}")
        return False


def delete_expense(expense_id):
    """Delete an expense record."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            return True
    except Exception as e:
        print(f"Failed to delete expense: {e}")
        return False


def get_total_expenses(trip_id):
    """Return the sum of all expenses for a trip."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE trip_id = ?", (trip_id,))
            row = cur.fetchone()
            return row["total"] if row else 0.0
    except Exception as e:
        print(f"Failed to compute total expenses: {e}")
        return 0.0
