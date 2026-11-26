"""Write departures to Supabase."""

from psycopg2.extras import execute_batch

OPERATOR = "GZK Rędziny"


def dedupe_departures(rows):
    """Return (unique_rows, messages).

    The database rejects identical departures. A repeated (stop, code, day_type, time)
    gets a '*' appended to the code (route variant); if that also exists, it is skipped.
    """
    seen = set()
    unique = []
    messages = []
    for r in rows:
        key = (r["bus_stop_id"], r["kod"], r["day_type"], r["godzina"])
        if key in seen:
            starred = r["kod"] + "*"
            starred_key = (r["bus_stop_id"], starred, r["day_type"], r["godzina"])
            if starred_key in seen:
                messages.append(f"Skipped duplicate: {key}")
                continue
            messages.append(f"Marked duplicate with star: {key} -> {starred}")
            r = {**r, "kod": starred}
            key = starred_key
        seen.add(key)
        unique.append(r)
    return unique, messages


def upload_departures(conn, rows):
    """Replace departures of the affected stops in one transaction. Returns the count."""
    rows = [r for r in rows if r["kod"]]
    codes = sorted({r["kod"] for r in rows})
    stop_ids = sorted({r["bus_stop_id"] for r in rows})
    with conn:
        with conn.cursor() as cur:
            for code in codes:
                cur.execute(
                    "INSERT INTO bus_line (name, operator) SELECT %s, %s "
                    "WHERE NOT EXISTS (SELECT 1 FROM bus_line WHERE name = %s)",
                    (code, OPERATOR, code))
            cur.execute("SELECT name, id FROM bus_line WHERE name = ANY(%s)", (codes,))
            line_ids = dict(cur.fetchall())

            cur.execute("DELETE FROM departure WHERE bus_stop_id = ANY(%s)", (stop_ids,))
            data = [(r["bus_stop_id"], line_ids[r["kod"]], r["day_type"], r["godzina"]) for r in rows]
            execute_batch(
                cur,
                "INSERT INTO departure (bus_stop_id, bus_line_id, day_type, departure_time) "
                "VALUES (%s, %s, %s, %s::time)", data, page_size=500)
            cur.execute("UPDATE data_version SET version = version + 1, updated_at = now() WHERE dataset = 'bus'")
    return len(data)