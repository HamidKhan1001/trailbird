# TrailBird: offline bird-call identifier

Identify a bird from a short recording on the trail, with no internet and no audio leaving your laptop.

> **Status: work in progress (Hacktoberfest 2026, "Touch Grass" challenge).**
> Done so far: audio loading/resampling/chunking (`trailbird/audio.py`) and top-3 / uncertainty / disclaimer formatting (`trailbird/results.py`).
> Still to do: BirdNET inference wiring, Gradio UI, tests, demo audio.

## Planned model
[BirdNET](https://github.com/birdnet-team/BirdNET-Analyzer) via the `birdnet` Python package (~6,000 species), run locally with ONNX.
- Code: MIT. **Model weights: CC BY-NC-SA 4.0** (non-commercial, share-alike, attribution required). Fine for this non-commercial project; not OSI-open weights.

## Disclaimer
Results are an assistive prediction, not a definitive identification.

## License
Project code: MIT. BirdNET model weights: CC BY-NC-SA 4.0.
