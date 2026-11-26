from gmina_sync.transport.upload import dedupe_departures


def make_row(code="RL", time="06:15"):
    return {"bus_stop_id": 1, "code": code, "day_type": "saturday", "time": time}


def test_dedupe_departures_keeps_unique_rows():
    rows = [make_row(time="06:15"), make_row(time="07:15")]
    unique, messages = dedupe_departures(rows)
    assert unique == rows
    assert messages == []


def test_dedupe_departures_marks_duplicate_with_star():
    unique, messages = dedupe_departures([make_row(), make_row()])
    assert [r["code"] for r in unique] == ["RL", "RL*"]
    assert len(messages) == 1


def test_dedupe_departures_skips_third_duplicate():
    unique, messages = dedupe_departures([make_row(), make_row(), make_row()])
    assert [r["code"] for r in unique] == ["RL", "RL*"]
    assert len(messages) == 2