from gmina_sync.transport.parse import parse_cell, parse_pdf


def test_parse_pdf_returns_departures():
    rows = parse_pdf("tests/samples/1.-Czestochowa-Pilsudskiego.pdf")
    assert len(rows) > 0
    assert set(rows[0]) == {"stop", "direction", "day_type", "time", "code"}


def test_parse_cell_with_codes():
    assert parse_cell("05 RL 32 45") == [("05", "RL"), ("32", ""), ("45", "")]


def test_parse_cell_multiline():
    assert parse_cell("05\n32") == [("05", ""), ("32", "")]


def test_parse_cell_empty():
    assert parse_cell("") == []


def test_parse_cell_star_variant():
    assert parse_cell("10 RL*") == [("10", "RL*")]