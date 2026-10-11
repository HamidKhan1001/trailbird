"""TrailBird Gradio UI. Run: python app.py  (binds to 127.0.0.1 only; no telemetry)."""
from __future__ import annotations

import os

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

import gradio as gr  # noqa: E402

from trailbird.audio import AudioError, load_audio  # noqa: E402
from trailbird.notes import GENERIC, load_notes  # noqa: E402
from trailbird.predictor import BirdNETPredictor, ModelError, Predictor  # noqa: E402
from trailbird.results import DISCLAIMER, format_markdown  # noqa: E402

_predictor: Predictor | None = None
_notes = load_notes()


def identify(audio_path: str | None) -> str:
    global _predictor
    try:
        load_audio(audio_path)  # validate format and content before touching the model
        if _predictor is None:
            _predictor = BirdNETPredictor()
        preds = _predictor.predict(audio_path, k=3)
    except (AudioError, ModelError) as exc:
        return f"❌ **{exc}**"
    notes = dict(_notes)
    if preds:
        notes.setdefault(preds[0].scientific_name, GENERIC)
    return format_markdown(preds, notes)


def build() -> gr.Blocks:
    with gr.Blocks(title="TrailBird") as demo:
        gr.Markdown("# 🐦 TrailBird: offline bird-call identifier\n" f"_{DISCLAIMER}_")
        audio = gr.Audio(sources=["upload", "microphone"], type="filepath", label="Bird sound")
        btn = gr.Button("Identify", variant="primary")
        out = gr.Markdown()
        btn.click(identify, audio, out)
    return demo


if __name__ == "__main__":
    build().launch(server_name="127.0.0.1", share=False)
