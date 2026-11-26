import os

import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)


def connect():
    """Open a connection to Supabase using DATABASE_URL."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise SystemExit("Set the DATABASE_URL environment variable.")
    return psycopg2.connect(DATABASE_URL)


def load_stops(conn):
    """Return all bus stops as dicts with id, name, locality and direction."""
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT b.id, b.name, l.name, d.name
                    FROM bus_stop b
                             JOIN locality l ON l.id = b.locality_id
                             JOIN direction d ON d.id = b.direction_id
                    """)
        return [
            {"id": stop_id, "name": name, "loc": locality, "dir": direction}
            for stop_id, name, locality, direction in cur.fetchall()
        ]
