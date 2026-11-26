"""Import bus timetables from PDF files into Supabase.

Usage:
  python main.py data/pdf             # preview, no DB write
  python main.py data/pdf --wyslij    # write to Supabase

Requires the DATABASE_URL environment variable.
"""

import csv
import os
import pathlib
import sys

from gmina_sync.db import connect, load_stops
from gmina_sync.transport.match import dopasuj, kierunek_slupka
from gmina_sync.transport.parse import parse_pdf
from gmina_sync.transport.upload import dedupe_departures, upload_departures

RESULT_CSV = "rozklady_wynik.csv"
CSV_FIELDS = ["bus_stop_id", "przystanek", "kierunek", "day_type", "godzina", "kod"]


def collect_rows(pdfs, stops):
    """Parse PDFs and match each to a stop. Returns (rows, unmatched).

    Without stops (no database) matching is skipped and bus_stop_id stays empty.
    """
    rows = []
    unmatched = []
    for pdf in pdfs:
        parsed = parse_pdf(pdf)
        if not parsed:
            unmatched.append((pdf.name, "brak odjazdów w PDF"))
            continue
        stop_id = ""
        if stops:
            header = parsed[0]["przystanek"]
            db_direction = kierunek_slupka(parsed[0]["kierunek"])
            matches = dopasuj(header, db_direction, stops)
            if len(matches) != 1:
                unmatched.append((pdf.name, f"{header} / {db_direction}: dopasowań {len(matches)}"))
                continue
            stop_id = matches[0]["id"]
        rows.extend({"bus_stop_id": stop_id, **r} for r in parsed)
    return rows, unmatched


def write_csv(rows, path):
    """Save rows to a semicolon-separated CSV (utf-8-sig so Excel reads Polish letters)."""
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def print_report(unmatched, stops, rows):
    """Print files that did not match and stops that have no timetable."""
    if unmatched:
        print("\nNIEDOPASOWANE (popraw ALIASY albo nazwy w bazie):")
        for name, reason in unmatched:
            print(" -", name, "|", reason)
    if stops:
        used = {r["bus_stop_id"] for r in rows}
        without = [s for s in stops if s["id"] not in used]
        print(f"\nSłupki bez rozkładu ({len(without)}):")
        for s in without:
            print(f" - {s['loc']} | {s['name']} | {s['dir']}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    folder = pathlib.Path(sys.argv[1])
    send = "--wyslij" in sys.argv
    pdfs = sorted(folder.glob("*.pdf"))
    print(f"Plików PDF: {len(pdfs)}")

    conn = None
    stops = []
    if send or os.environ.get("DATABASE_URL"):
        conn = connect()
        stops = load_stops(conn)
        print(f"Słupków w bazie: {len(stops)}")
    else:
        print("Brak DATABASE_URL - dopasowanie pominięte, tylko parsowanie.")

    rows, unmatched = collect_rows(pdfs, stops)
    write_csv(rows, RESULT_CSV)
    print(f"Zapisano {len(rows)} odjazdów do {RESULT_CSV}")
    print_report(unmatched, stops, rows)

    if send and conn is not None:
        if unmatched:
            sys.exit("Najpierw napraw niedopasowane pliki, potem uruchom z --wyslij.")
        unique, messages = dedupe_departures(rows)
        for m in messages:
            print(m)
        count = upload_departures(conn, unique)
        print(f"Wysłano {count} odjazdów do Supabase.")