"""TrailBird Gradio UI. Run: python app.py  (binds to 127.0.0.1 only; no telemetry)."""
from __future__ import annotations

import os

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

import gradio as gr  # noqa: E402

from trailbird.errors import TrailbirdError  # noqa: E402
from trailbird.notes import load_notes  # noqa: E402
from trailbird.predictor import BirdNETPredictor  # noqa: E402
from trailbird.results import DISCLAIMER  # noqa: E402
from trailbird.service import Identifier  # noqa: E402

_identifier: Identifier | None = None


def identify(audio_path: str | None) -> str:
    """Lazy-load the model on first use so the page opens instantly."""
    global _identifier
    try:
        if _identifier is None:
            _identifier = Identifier(BirdNETPredictor(), load_notes())
    except TrailbirdError as exc:
        return f"❌ **{exc}**"
    return _identifier.identify_markdown(audio_path)


def build() -> gr.Blocks:
    with gr.Blocks(title="TrailBird") as demo:
        gr.Markdown(f"# 🐦 TrailBird: offline bird-call identifier\n_{DISCLAIMER}_")
        audio = gr.Audio(sources=["upload", "microphone"], type="filepath", label="Bird sound")
        btn = gr.Button("Identify", variant="primary")
        out = gr.Markdown()
        btn.click(identify, audio, out)
    return demo


if __name__ == "__main__":
    build().launch(server_name="127.0.0.1", share=False)
