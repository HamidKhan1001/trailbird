# Contributing to TrailBird

Thanks for helping! Good first issues: species notes, regional filters, docs, UI polish.

## Setup
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[ui,dev]"
pytest && ruff check .
```

## Ground rules
- **Privacy first:** no telemetry, no cloud APIs, no sending audio anywhere. Inference must keep working under `block_network()` (see `trailbird/offline.py`).
- **No fake predictions** outside `tests/`. Test doubles live in `tests/conftest.py` only.
- Add or update tests with every change. Keep the model behind the `Predictor` protocol.
- **Species notes** (`trailbird/data/species_notes.json`): keyed by scientific name; write original text, do not copy from copyrighted guides.
- **Audio samples:** only commit recordings with a compatible licence (e.g. CC0/CC-BY from xeno-canto) and list attribution in `ATTRIBUTION.md`.

## Pull requests
Small, focused PRs. Describe what you tested. CI must pass.
