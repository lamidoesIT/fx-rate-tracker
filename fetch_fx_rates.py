"""
fetch_fx_rates.py

Pulls foreign-exchange rates from the free Frankfurter API (European
Central Bank data, no API key required) and stores them in a local
SQLite database.

Run it once to backfill several months of history. Re-run it any time
(e.g. daily) and it will only pull the days that are new since your
last run -- that incremental behaviour is the "automated pipeline"
part of the story for your resume/CV.

Setup (one-time):
    pip install requests

Usage:
    python fetch_fx_rates.py
"""

import sqlite3
import requests
from datetime import date, timedelta

# ---- Config: change these if you want different currencies ----
BASE_CURRENCY = "USD"
TARGET_CURRENCIES = ["EUR", "GBP", "JPY"]
BACKFILL_DAYS = 180          # how much history to pull on the first run
DB_PATH = "fx_rates.db"
API_ROOT = "https://api.frankfurter.dev/v1"


def create_table(conn):
    """Create the rates table if it doesn't already exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fx_rates (
            rate_date TEXT NOT NULL,
            base_currency TEXT NOT NULL,
            target_currency TEXT NOT NULL,
            rate REAL NOT NULL,
            PRIMARY KEY (rate_date, base_currency, target_currency)
        )
    """)
    conn.commit()


def get_latest_stored_date(conn):
    """Return the most recent date already in the database, or None if empty."""
    cur = conn.execute("SELECT MAX(rate_date) FROM fx_rates")
    return cur.fetchone()[0]   # a 'YYYY-MM-DD' string, or None


def fetch_time_series(start_date, end_date, base, symbols):
    """
    Call the Frankfurter time-series endpoint and return the raw JSON.
    start_date / end_date are date objects.
    Docs: https://frankfurter.dev/v1/
    """
    url = f"{API_ROOT}/{start_date.isoformat()}..{end_date.isoformat()}"
    params = {"base": base, "symbols": ",".join(symbols)}
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()   # raises an error if the request failed
    return response.json()


def upsert_rates(conn, payload, base):
    """
    Take the JSON payload from Frankfurter and insert each
    (date, base, target, rate) row into SQLite.
    Frankfurter's time-series shape is:
        { "rates": { "2024-01-01": {"EUR": 0.91, "GBP": 0.79}, ... } }
    """
    rows = []
    for rate_date, currency_rates in payload.get("rates", {}).items():
        for target_currency, rate in currency_rates.items():
            rows.append((rate_date, base, target_currency, rate))

    conn.executemany("""
        INSERT OR REPLACE INTO fx_rates (rate_date, base_currency, target_currency, rate)
        VALUES (?, ?, ?, ?)
    """, rows)
    conn.commit()
    return len(rows)


def main():
    conn = sqlite3.connect(DB_PATH)
    create_table(conn)

    latest_stored = get_latest_stored_date(conn)

    if latest_stored is None:
        start = date.today() - timedelta(days=BACKFILL_DAYS)
        print(f"No existing data found. Backfilling from {start} to today...")
    else:
        start = date.fromisoformat(latest_stored) + timedelta(days=1)
        print(f"Existing data found up to {latest_stored}. Fetching new rates from {start}...")

    end = date.today()

    if start > end:
        print("Already up to date -- nothing new to fetch.")
        conn.close()
        return

    payload = fetch_time_series(start, end, BASE_CURRENCY, TARGET_CURRENCIES)
    inserted = upsert_rates(conn, payload, BASE_CURRENCY)

    total = conn.execute("SELECT COUNT(*) FROM fx_rates").fetchone()[0]
    date_range = conn.execute("SELECT MIN(rate_date), MAX(rate_date) FROM fx_rates").fetchone()

    print(f"Inserted/updated {inserted} rows.")
    print(f"Database now has {total} rows covering {date_range[0]} to {date_range[1]}.")
    conn.close()


if __name__ == "__main__":
    main()
