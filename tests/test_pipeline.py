from pathlib import Path

from gmina_sync.transport.pipeline import collect_rows, write_csv

SAMPLE = Path("tests/samples/1.-Czestochowa-Pilsudskiego.pdf")
MATCHING_STOP = {"id": 7, "name": "Piłsudskiego", "loc": "Częstochowa", "dir": "Rędziny"}


def test_collect_rows_without_stops_leaves_stop_id_empty():
    rows, unmatched = collect_rows([SAMPLE], [])
    assert len(rows) > 0
    assert unmatched == []
    assert all(r["bus_stop_id"] == "" for r in rows)


def test_collect_rows_reports_unmatched_file():
    other_stop = [{"id": 99, "name": "Nieistniejący", "loc": "Nigdzie", "dir": "Rędziny"}]
    rows, unmatched = collect_rows([SAMPLE], other_stop)
    assert rows == []
    assert len(unmatched) == 1


def test_write_csv_writes_header_and_rows(tmp_path):
    path = tmp_path / "out.csv"
    rows = [{"bus_stop_id": 1, "stop": "A", "direction": "B",
             "day_type": "saturday", "time": "06:15", "code": "RL"}]
    write_csv(rows, path)
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    assert lines[0] == "bus_stop_id;stop;direction;day_type;time;code"
    assert lines[1] == "1;A;B;saturday;06:15;RL"