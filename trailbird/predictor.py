"""Local BirdNET inference. UNVERIFIED against the installed birdnet version: debug first."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Protocol

from .results import Prediction, top_k


class ModelError(RuntimeError):
    """Raised when the model is missing or fails to load/run."""


class Predictor(Protocol):
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


class BirdNETPredictor:
    """Wraps the `birdnet` package. Needs a one-time model download, then runs offline."""

    def __init__(self) -> None:
        try:
            import birdnet  # noqa: PLC0415
        except ImportError as exc:
            raise ModelError("Missing dependency. Run: pip install -r requirements.txt") from exc
        try:
            self._model = birdnet.load("acoustic", "2.4", "onnx")
        except Exception as exc:
            raise ModelError(
                f"Could not load the BirdNET model ({exc}). "
                "The first run needs internet to download it once; after that it works offline."
            ) from exc

    def predict(self, audio_path: str | Path, k: int = 3) -> list[Prediction]:
        try:
            result = self._model.predict(str(audio_path), top_k=10)
            df = result.to_dataframe()
        except Exception as exc:
            raise ModelError(f"Inference failed: {exc}") from exc
        label_col = next((c for c in ("species_name", "species", "label") if c in df.columns), None)
        conf_col = next((c for c in ("confidence", "score") if c in df.columns), None)
        if label_col is None or conf_col is None:
            raise ModelError(f"Unexpected result columns from birdnet: {list(df.columns)}")
        rows = list(zip(df[label_col].astype(str), df[conf_col].astype(float)))
        return aggregate(rows, k)
