# TrailBird: offline bird-call identifier

Identify a bird from a short recording on the trail, with no internet and no audio leaving your laptop.

> **Status (Hacktoberfest 2026, "Touch Grass"): code complete but NOT yet run end to end.**
> The BirdNET call in `trailbird/predictor.py` was written from the package docs and is unverified. Expect to debug it on first run.

## How it works
1. `trailbird/audio.py` loads a file, converts to mono, resamples to 48 kHz and validates it.
2. `trailbird/predictor.py` runs [BirdNET](https://github.com/birdnet-team/BirdNET-Analyzer) locally (ONNX) and keeps the best score per species.
3. `trailbird/results.py` returns the top 3, flags low confidence (best < 50%, or within 10 points of second) and adds the disclaimer.
4. `app.py` is a local Gradio UI bound to 127.0.0.1 with analytics off.

## Install
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[ui,dev]"      # or: pip install -r requirements.txt
```
The first run downloads the BirdNET model once (needs internet). After that it runs offline.

## Run
```bash
python app.py                          # UI at http://127.0.0.1:7860, upload or record, press Identify
trailbird identify clip.wav            # CLI, add --json for machine-readable output
pytest                                 # tests (no model needed)
```

## Test audio (legal)
Download a CC-licensed recording from [xeno-canto.org](https://xeno-canto.org) or the Macaulay Library, and respect its license and attribution. Put it outside the repo or keep it out of git.

## Offline guarantee
The model is downloaded once. Every inference then runs inside `trailbird.offline.block_network()`, which raises if anything tries to open a non-loopback connection (pass `--allow-network` to the CLI to disable). This is tested in `tests/test_offline.py` and `tests/test_service.py`. See [ARCHITECTURE.md](ARCHITECTURE.md).

## Why open-source AI / privacy
Open weights run on your laptop: no signal needed, no API key, and your recordings and location never leave the device.

## Attribution and licenses
- Project code: MIT.
- BirdNET (Cornell Lab of Ornithology and Chemnitz University of Technology): code MIT, **model weights CC BY-NC-SA 4.0** (non-commercial, share-alike, attribution).

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).

## Limitations
Not a definitive identification. Accuracy drops with noise, overlapping birds, and short clips. BirdNET coverage varies by region.

## Future improvements
Location filter, live microphone streaming, per-region notes, an Apache-licensed fallback model.
