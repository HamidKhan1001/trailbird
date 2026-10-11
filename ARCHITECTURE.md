# Architecture

```
 file/mic ──► audio.py ──► service.Identifier ──► results.py ──► CLI / Gradio
              validate       │  Predictor protocol     top-3, uncertainty,
              mono, 48 kHz   │  (BirdNET adapter)      disclaimer
                             └─ offline.block_network() around inference
```

| Module | Responsibility |
|---|---|
| `audio.py` | Decode, validate (format, empty, max length), mono, resample, chunk |
| `predictor.py` | `Predictor` protocol + `BirdNETPredictor` adapter + per-species aggregation |
| `service.py` | `Identifier`: validate → predict (network blocked) → assess → `Identification` |
| `results.py` | `Prediction`, ranking, uncertainty rule, markdown, disclaimer |
| `offline.py` | `block_network()` raises on any non-loopback socket connect during inference |
| `notes.py` | Loads hand-written species notes, generic fallback |
| `cli.py`, `app.py` | Thin front-ends; no business logic |
| `errors.py` | `TrailbirdError` hierarchy; messages are user-safe |

## Decisions
- **BirdNET+ V3.0 preview (ONNX)** for coverage (~11.5k species). v2.4 has no ONNX backend in the `birdnet` package and its weights are non-commercial (CC BY-NC-SA); V3.0 preview is CC BY-SA 4.0 with a no-poaching/no-military use clause. Trade-off: it is a developer preview, and the FP16 ONNX file is ~270 MB. The `Predictor` protocol makes swapping in a permissive model (e.g. an Apache-2.0 HF classifier) a one-file change.
- **Uncertainty rule:** top score < 0.50, or lead over runner-up < 0.10. Tunable in `results.py`.
- **Model download is the only network step**, done once before inference; inference runs with sockets blocked.
- **Offline guard scope:** `block_network()` is in-process; BirdNET's workers are separate processes, so we pin `n_workers=1` and recommend an OS-level sandbox for a hard guarantee.
- **Dependency injection** keeps tests fast and model-free.
