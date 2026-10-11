# TrailBird: offline bird-call identifier

Identify a bird from a short recording on the trail, with no internet and no audio leaving your laptop.

> **Status (Hacktoberfest 2026, "Touch Grass"):** unit tests pass (39, model-free). The BirdNET call shape was checked against the `birdnet` 1.1.1 source. A real-audio end-to-end run needs the ~270 MB model download; see "Verification log" below for what has and has not been verified.

## How it works
1. `trailbird/audio.py` loads a file, converts to mono, resamples to 48 kHz and validates it.
2. `trailbird/predictor.py` runs [BirdNET+ V3.0 (developer preview)](https://zenodo.org/records/20703646) locally (ONNX FP16, ~11.5k species) and keeps the best score per species.
3. `trailbird/results.py` returns the top 3, flags low confidence (best < 50%, or within 10 points of second) and adds the disclaimer.
4. `app.py` is a local Gradio UI bound to 127.0.0.1 with analytics off.

## Install
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[ui,dev]"      # or: pip install -r requirements.txt
```
Download the model once (needs internet, ~270 MB), then everything runs offline:
```bash
trailbird fetch-model
```

## Run
```bash
python app.py                          # UI at http://127.0.0.1:7860, upload or record, press Identify
trailbird identify clip.wav            # CLI, add --json for machine-readable output
pytest                                 # tests (no model needed)
```

## Test audio (legal)
Download a CC-licensed recording from [xeno-canto.org](https://xeno-canto.org) or the Macaulay Library, and respect its license and attribution. Put it outside the repo or keep it out of git.

## Offline guarantee
The model is downloaded once (`trailbird fetch-model`). Every inference then runs inside `trailbird.offline.block_network()`, which raises if the TrailBird process tries to open a non-loopback connection (pass `--allow-network` to the CLI to disable). Tested in `tests/test_offline.py` and `tests/test_service.py`.

**Limit of the in-process guard:** it patches Python sockets in this process only. For an OS-level guarantee on macOS, run the CLI with the network denied at kernel level:
```bash
sandbox-exec -p '(version 1)(allow default)(deny network*)' trailbird identify clip.wav
```
See [ARCHITECTURE.md](ARCHITECTURE.md).

## Why open-source AI / privacy
Open weights run on your laptop: no signal needed, no API key, and your recordings and location never leave the device.

## Attribution and licenses
- Project code: MIT.
- `birdnet` Python package: MIT.
- **BirdNET+ V3.0 developer preview** model (K. Lisa Yang Center for Conservation Bioacoustics at Cornell, Chemnitz University of Technology, Museum für Naturkunde Berlin): **CC BY-SA 4.0** per its [Zenodo record](https://zenodo.org/records/20703646), plus Terms of Use that **prohibit poaching and military use** and require attribution ("Powered by BirdNET"). Commercial use is allowed, but because of those extra restrictions the weights are open-access rather than OSI-open. The model is downloaded at runtime and is not redistributed in this repo.
- The older BirdNET v2.4 weights are CC BY-NC-SA 4.0 (non-commercial); this project does not use them.
- Powered by BirdNET.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).

## Limitations
Not a definitive identification. Accuracy drops with noise, overlapping birds, and short clips. BirdNET coverage varies by region.

## Future improvements
Location filter, live microphone streaming, per-region notes, an Apache-licensed fallback model, moving to the stable BirdNET v3.0 release when published.

## Verification log
- [x] 39 unit tests pass (audio, results, service, offline guard, CLI, notes).
- [x] `birdnet` 1.1.1 API (`load`, `predict`, result columns `species_name`/`confidence`) and label format checked against installed source.
- [x] v2.4 has no ONNX backend; v3.0 does, so the project uses v3.0 ONNX.
- [ ] End-to-end run on real bird audio (pending model download).
- [ ] Run under `sandbox-exec` with network denied (pending model download).
