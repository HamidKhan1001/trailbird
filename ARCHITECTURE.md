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
- **BirdNET** for coverage (~6k species). Trade-off: weights are CC BY-NC-SA 4.0, so non-commercial. The `Predictor` protocol makes swapping in a permissive model (e.g. an Apache-2.0 HF classifier) a one-file change.
- **Uncertainty rule:** top score < 0.50, or lead over runner-up < 0.10. Tunable in `results.py`.
- **Model download is the only network step**, done once before inference; inference runs with sockets blocked.
- **Dependency injection** keeps tests fast and model-free.
