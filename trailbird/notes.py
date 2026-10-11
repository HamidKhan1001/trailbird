"""Small hand-written species notes (keyed by scientific name). Falls back to generic tips."""
from __future__ import annotations

import json
from pathlib import Path

NOTES_PATH = Path(__file__).parent / "data" / "species_notes.json"
GENERIC = "Note where you heard it (canopy, shrub, water edge) and whether the call repeats. That helps confirm."


def load_notes(path: Path = NOTES_PATH) -> dict[str, str]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid species notes file {path}: {exc}") from exc
