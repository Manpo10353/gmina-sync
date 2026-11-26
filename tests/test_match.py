from gmina_sync.transport.match import match_stops, stop_direction

STOPS = [
    {"id": 1, "name": "Spacerowa", "loc": "Częstochowa", "dir": "Rędziny"},
    {"id": 2, "name": "Spacerowa", "loc": "Częstochowa", "dir": "Częstochowa"},
    {"id": 3, "name": "Nowe 1", "loc": "Rudniki", "dir": "Rędziny"},
]


def test_kierunek_slupka_city_direction():
    assert stop_direction("CZĘSTOCHOWA") == "Częstochowa"


def test_kierunek_slupka_defaults_to_local_direction():
    assert stop_direction("KAROLINA, KONIN, MARIANKA RĘDZIŃSKA") == "Rędziny"


def test_dopasuj_by_name_and_direction():
    result = match_stops("SPACEROWA", "Częstochowa", STOPS)
    assert [s["id"] for s in result] == [2]


def test_dopasuj_by_alias():
    result = match_stops("RUDNIKI NOWE I", "Rędziny", STOPS)
    assert [s["id"] for s in result] == [3]


def test_dopasuj_no_match():
    assert match_stops("NIEISTNIEJĄCY", "Rędziny", STOPS) == []


def test_dopasuj_case_insensitive():
    result = match_stops("spacerowa", "Częstochowa", STOPS)
    assert [s["id"] for s in result] == [2]