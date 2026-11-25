import os

import psycopg2


def connect():
    """Open a connection to Supabase using SUPABASE_DB_URL."""
    url = os.environ.get("SUPABASE_DB_URL")
    if not url:
        raise SystemExit("Set the SUPABASE_DB_URL environment variable.")
    return psycopg2.connect(url)


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
