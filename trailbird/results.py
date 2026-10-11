"""Prediction data types, confidence handling, and formatting."""
from __future__ import annotations

from dataclasses import dataclass

UNCERTAIN_BELOW = 0.50  # top-1 below this => flagged uncertain
MARGIN = 0.10  # top-1 within this of top-2 => flagged ambiguous

DISCLAIMER = (
    "Assistive prediction only, not a definitive identification. "
    "Confirm with sight, a field guide, or an expert."
)


@dataclass(frozen=True)
class Prediction:
    common_name: str
    scientific_name: str
    confidence: float


def top_k(preds: list[Prediction], k: int = 3) -> list[Prediction]:
    return sorted(preds, key=lambda p: p.confidence, reverse=True)[:k]


def is_uncertain(preds: list[Prediction]) -> bool:
    if not preds:
        return True
    if preds[0].confidence < UNCERTAIN_BELOW:
        return True
    return len(preds) > 1 and preds[0].confidence - preds[1].confidence < MARGIN


def format_markdown(preds: list[Prediction], notes: dict[str, str] | None = None) -> str:
    if not preds:
        return "**No bird detected.** Try a longer or clearer recording.\n\n_" + DISCLAIMER + "_"
    notes = notes or {}
    lines = []
    best = preds[0]
    if is_uncertain(preds):
        lines.append(f"⚠️ **UNCERTAIN** — best guess: **{best.common_name}** ({best.confidence:.0%})")
    else:
        lines.append(f"✅ **{best.common_name}** ({best.confidence:.0%})")
    lines.append("")
    lines.append("| # | Species | Scientific name | Confidence |")
    lines.append("|---|---------|-----------------|-----------|")
    for i, p in enumerate(preds, 1):
        lines.append(f"| {i} | {p.common_name} | *{p.scientific_name}* | {p.confidence:.1%} |")
    note = notes.get(best.scientific_name) or notes.get(best.common_name)
    if note:
        lines += ["", f"**Listening notes:** {note}"]
    lines += ["", f"_{DISCLAIMER}_"]
    return "\n".join(lines)
