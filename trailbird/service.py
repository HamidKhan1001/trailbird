"""Orchestration: validate -> predict (network blocked) -> assess -> report.

Depends only on the `Predictor` protocol, so it is fully testable with a fake model
and the UI/CLI stay thin.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .audio import load_audio
from .errors import TrailbirdError
from .notes import GENERIC
from .offline import block_network
from .predictor import Predictor
from .results import DISCLAIMER, Prediction, format_markdown, is_uncertain, top_k


@dataclass(frozen=True)
class Identification:
    predictions: list[Prediction]
    uncertain: bool
    note: str | None
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict[str, Any]:
        return {
            "predictions": [
                {
                    "common_name": p.common_name,
                    "scientific_name": p.scientific_name,
                    "confidence": round(p.confidence, 4),
                }
                for p in self.predictions
            ],
            "uncertain": self.uncertain,
            "note": self.note,
            "disclaimer": self.disclaimer,
        }


class Identifier:
    def __init__(
        self,
        predictor: Predictor,
        notes: Mapping[str, str] | None = None,
        k: int = 3,
        enforce_offline: bool = True,
    ) -> None:
        self._predictor = predictor
        self._notes = dict(notes or {})
        self._k = k
        self._enforce_offline = enforce_offline

    def identify(self, audio_path: str | Path | None) -> Identification:
        load_audio(audio_path)  # fail fast with a friendly AudioError before touching the model
        assert audio_path is not None
        if self._enforce_offline:
            with block_network():
                raw = self._predictor.predict(audio_path, k=self._k)
        else:
            raw = self._predictor.predict(audio_path, k=self._k)
        preds = top_k(raw, self._k)
        note = None
        if preds:
            best = preds[0]
            note = self._notes.get(best.scientific_name) or GENERIC
        return Identification(preds, is_uncertain(preds), note)

    def identify_markdown(self, audio_path: str | Path | None) -> str:
        """UI helper: never raises for expected failures; returns a readable message instead."""
        try:
            result = self.identify(audio_path)
        except TrailbirdError as exc:
            return f"❌ **{exc}**"
        notes = {result.predictions[0].scientific_name: result.note} if result.predictions else {}
        return format_markdown(result.predictions, {k: v for k, v in notes.items() if v})
