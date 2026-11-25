"""Import bus timetables from PDF files into Supabase.

Usage:
  python -m gmina_sync.transport.pdf_to_csv_upload data/pdf             # preview, no DB write
  python -m gmina_sync.transport.pdf_to_csv_upload data/pdf --wyslij    # write to Supabase

Requires the SUPABASE_DB_URL environment variable.
"""

import csv
import os
import pathlib
import sys

from gmina_sync.db import load_stops, connect
from gmina_sync.transport.match import kierunek_slupka, dopasuj
from gmina_sync.transport.parse import parse_pdf

OPERATOR = "GZK Rędziny"
WYNIK_CSV = "rozklady_wynik.csv"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    folder = pathlib.Path(sys.argv[1])
    wyslij = "--wyslij" in sys.argv
    pdfs = sorted(folder.glob("*.pdf"))
    print(f"Plików PDF: {len(pdfs)}")

    conn = None
    stops = []
    if wyslij or os.environ.get("SUPABASE_DB_URL"):
        conn = connect()
        stops = load_stops(conn)
        print(f"Słupków w bazie: {len(stops)}")
    else:
        print("Brak SUPABASE_DB_URL - dopasowanie pominięte, tylko parsowanie.")

    wynik = []
    niedopasowane = []
    zrodla = {}
    for pdf in pdfs:
        rows = parse_pdf(pdf)
        if not rows:
            niedopasowane.append((pdf.name, "brak odjazdów w PDF"))
            continue
        naglowek = rows[0]["przystanek"]
        kierunek = rows[0]["kierunek"]
        if stops:
            kier_bazy = kierunek_slupka(kierunek)
            pasujace = dopasuj(naglowek, kier_bazy, stops)
            if len(pasujace) != 1:
                niedopasowane.append((pdf.name, f"{naglowek} / {kier_bazy}: dopasowań {len(pasujace)}"))
                continue
            stop_id = pasujace[0]["id"]
        else:
            stop_id = ""
        for r in rows:
            wynik.append({"bus_stop_id": stop_id, **r})
        if stop_id != "":
            zrodla.setdefault(stop_id, []).append(pdf.name)

    # utf-8-sig: BOM, żeby Excel na Windowsie nie czytał polskich liter jako cp1250
    with open(WYNIK_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["bus_stop_id", "przystanek", "kierunek", "day_type", "godzina", "kod"], delimiter=";")
        w.writeheader()
        w.writerows(wynik)
    print(f"Zapisano {len(wynik)} odjazdów do {WYNIK_CSV}")

    if niedopasowane:
        print("\nNIEDOPASOWANE (popraw ALIASY albo nazwy w bazie):")
        for name, why in niedopasowane:
            print(" -", name, "|", why)

    if stops:
        uzyte = {r["bus_stop_id"] for r in wynik}
        bez_rozkladu = [s for s in stops if s["id"] not in uzyte]
        print(f"\nSłupki bez rozkładu ({len(bez_rozkladu)}):")
        for s in bez_rozkladu:
            print(f" - {s['loc']} | {s['name']} | {s['dir']}")

    if wyslij and conn is not None:
        if niedopasowane:
            sys.exit("Najpierw napraw niedopasowane pliki, potem uruchom z --wyslij.")
        # Baza nie przyjmuje dwóch identycznych odjazdów. Gdy ten sam kod pojawia się
        # dwa razy o tej samej minucie, drugi dostaje gwiazdkę (wariant trasy, np. RL*),
        # jeśli taki kod jeszcze nie istnieje dla tego odjazdu. Inaczej pomijamy.
        widziane = set()
        unikalne = []
        for r in wynik:
            klucz = (r["bus_stop_id"], r["kod"], r["day_type"], r["godzina"])
            if klucz in widziane:
                kod_gw = r["kod"] + "*"
                klucz_gw = (r["bus_stop_id"], kod_gw, r["day_type"], r["godzina"])
                if klucz_gw in widziane:
                    print(f"Powtórzony odjazd (pominięto): słupek {r['bus_stop_id']} | {r['kod']} | {r['day_type']} | {r['godzina']}")
                    continue
                print(f"Powtórzony odjazd oznaczony gwiazdką: {r['kod']} -> {kod_gw} | słupek {r['bus_stop_id']} | {r['day_type']} | {r['godzina']}")
                r = {**r, "kod": kod_gw}
                klucz = klucz_gw
            widziane.add(klucz)
            unikalne.append(r)
        wynik = unikalne
        kody = sorted({r["kod"] for r in wynik if r["kod"]})
        stop_ids = sorted({r["bus_stop_id"] for r in wynik})
        with conn:
            with conn.cursor() as cur:
                for kod in kody:
                    cur.execute(
                        "INSERT INTO bus_line (name, operator) SELECT %s, %s "
                        "WHERE NOT EXISTS (SELECT 1 FROM bus_line WHERE name = %s)",
                        (kod, OPERATOR, kod))
                cur.execute("SELECT name, id FROM bus_line WHERE name = ANY(%s)", (kody,))
                line_ids = dict(cur.fetchall())

                cur.execute("DELETE FROM departure WHERE bus_stop_id = ANY(%s)", (stop_ids,))
                data = [(r["bus_stop_id"], line_ids[r["kod"]], r["day_type"], r["godzina"]) for r in wynik]
                from psycopg2.extras import execute_batch
                execute_batch(cur,
                    "INSERT INTO departure (bus_stop_id, bus_line_id, day_type, departure_time) "
                    "VALUES (%s, %s, %s, %s::time)", data, page_size=500)

                cur.execute("UPDATE data_version SET version = version + 1, updated_at = now() WHERE dataset = 'bus'")
        print(f"Wysłano {len(data)} odjazdów do Supabase.")


if __name__ == "__main__":
    main()