import pytest

from trailbird.notes import load_notes


def test_bundled_notes_load_and_nonempty():
    notes = load_notes()
    assert notes and all(isinstance(v, str) and v for v in notes.values())


def test_missing_file_returns_empty(tmp_path):
    assert load_notes(tmp_path / "nope.json") == {}


def test_invalid_json_gives_clear_error(tmp_path):
    p = tmp_path / "n.json"
    p.write_text("{oops")
    with pytest.raises(ValueError, match="Invalid species notes"):
        load_notes(p)
