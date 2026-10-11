"""Local BirdNET+ V3.0 inference via the `birdnet` package (ONNX, FP16).

API shape (load/predict/to_dataframe columns) verified against birdnet 1.1.1 source;
end-to-end inference on real audio is verified separately (see README status).
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Protocol

from .errors import ModelError
from .results import Prediction, top_k


class Predictor(Protocol):
    def load(self) -> None: ...

    def predict(self, audio_path: str | Path, k: int = 3) -> list[Prediction]: ...


def split_species(label: str) -> tuple[str, str]:
    """BirdNET labels look like 'Genus species_Common Name'."""
    if "_" in label:
        sci, common = label.split("_", 1)
        return common, sci
    return label, label


def aggregate(rows: list[tuple[str, float]], k: int = 3) -> list[Prediction]:
    """Collapse per-chunk (label, confidence) rows into one score per species (max over chunks)."""
    best: dict[str, float] = defaultdict(float)
    for label, conf in rows:
        best[label] = max(best[label], float(conf))
    preds = []
    for label, conf in best.items():
        common, sci = split_species(label)
        preds.append(Prediction(common, sci, min(max(conf, 0.0), 1.0)))
    return top_k(preds, k)


MODEL_TYPE, MODEL_VERSION, MODEL_BACKEND, MODEL_PRECISION = "acoustic", "3.0", "onnx", "fp16"
# Keep low-scoring species so we can always show a top-3 and let the uncertainty rule judge them.
MIN_CONFIDENCE = 0.01


class BirdNETPredictor:
    """Wraps the `birdnet` package. Needs a one-time model download, then runs offline."""

    def __init__(self) -> None:
        self._model = None  # loaded lazily so bad input fails fast and downloads are explicit

    def load(self) -> None:
        """Load the model, downloading it on first use (the only step that needs internet)."""
        if self._model is not None:
            return
        try:
            import birdnet  # noqa: PLC0415
        except ImportError as exc:
            raise ModelError("Missing dependency. Run: pip install -r requirements.txt") from exc
        try:
            self._model = birdnet.load(
                MODEL_TYPE, MODEL_VERSION, MODEL_BACKEND, precision=MODEL_PRECISION
            )
        except Exception as exc:
            raise ModelError(
                f"Could not load the BirdNET model ({exc}). "
                "The first run needs internet to download the ~270 MB model once "
                "(`trailbird fetch-model`); after that it works offline."
            ) from exc

    def predict(self, audio_path: str | Path, k: int = 3) -> list[Prediction]:
        self.load()
        try:
            result = self._model.predict(
                str(audio_path),
                top_k=10,
                n_producers=1,
                n_workers=1,
                default_confidence_threshold=MIN_CONFIDENCE,
            )
            df = result.to_dataframe()
        except Exception as exc:
            raise ModelError(f"Inference failed: {exc}") from exc
        label_col = next((c for c in ("species_name", "species", "label") if c in df.columns), None)
        conf_col = next((c for c in ("confidence", "score") if c in df.columns), None)
        if label_col is None or conf_col is None:
            raise ModelError(f"Unexpected result columns from birdnet: {list(df.columns)}")
        rows = list(zip(df[label_col].astype(str), df[conf_col].astype(float)))
        return aggregate(rows, k)
