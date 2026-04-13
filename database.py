import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "appointments.db")

DB_NAME = "appointments.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_booking(name, phone, date, time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO bookings (name, phone, date, time)
        VALUES (?, ?, ?, ?)
    """, (name, phone, date, time))

    conn.commit()
    conn.close()
def get_all_bookings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, phone, date, time FROM bookings")
    rows = cursor.fetchall()

    conn.close()
    return rows
def delete_booking(booking_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    
    conn.commit()
    conn.close()
def delete_booking(booking_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    
    conn.commit()
    conn.close()
def add_demo_data(): #remove later
    demo_entries = [
        ("Hemanth", "+919999999999", "2026-03-01", "4 pm"),
        ("Rahul", "+919888888888", "2026-03-02", "11 am"),
        ("Sneha", "+919777777777", "2026-03-03", "2 pm"),
    ]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO bookings (name, phone, date, time)
        VALUES (?, ?, ?, ?)
    """, demo_entries)

    conn.commit()
    conn.close()

def search_bookings(query):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    like_query = f"%{query}%"

    cursor.execute("""
        SELECT id, name, phone, date, time
        FROM bookings
        WHERE name LIKE ?
           OR phone LIKE ?
           OR date LIKE ?
    """, (like_query, like_query, like_query))

    rows = cursor.fetchall()
    conn.close()

    return rows

def get_sorted_by_time_of_day():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT id, name, phone, date, time
        FROM bookings
    """).fetchall()

    conn.close()

    def convert_to_24h(t):
        t = t.lower().strip()
        parts = t.replace(":", " ").split()

        try:
            hour = int(parts[0])
            period = parts[-1]

            if period == "pm" and hour != 12:
                hour += 12
            if period == "am" and hour == 12:
                hour = 0

            return hour
        except:
            return 99  # push invalid times to bottom

    def time_group(hour):
        if 6 <= hour <= 11:
            return 1  # Morning
        elif 12 <= hour <= 16:
            return 2  # Afternoon
        elif 17 <= hour <= 20:
            return 3  # Evening
        else:
            return 4  # Night

    sorted_rows = sorted(
        rows,
        key=lambda row: (time_group(convert_to_24h(row[4])), convert_to_24h(row[4]))
    )

    return sorted_rows