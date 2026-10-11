import pytest

from trailbird.errors import AudioError, ModelError
from trailbird.results import Prediction
from trailbird.service import Identifier

from .conftest import FakePredictor


def test_identify_returns_top3_sorted_not_uncertain(wav_path, confident_preds):
    fake = FakePredictor(confident_preds)
    out = Identifier(fake, {"Turdus merula": "Rich flute-like phrases."}).identify(wav_path)
    assert [p.common_name for p in out.predictions] == [
        "Common Blackbird", "European Robin", "Great Tit"
    ]
    assert not out.uncertain
    assert out.note == "Rich flute-like phrases."
    assert fake.calls == [(str(wav_path), 3)]


def test_low_confidence_marked_uncertain(wav_path):
    out = Identifier(FakePredictor([Prediction("A", "A a", 0.2)])).identify(wav_path)
    assert out.uncertain


def test_no_detections(wav_path):
    out = Identifier(FakePredictor([])).identify(wav_path)
    assert out.predictions == [] and out.uncertain and out.note is None


def test_generic_note_fallback(wav_path):
    out = Identifier(FakePredictor([Prediction("A", "A a", 0.9)]), {}).identify(wav_path)
    assert out.note


def test_invalid_file_never_reaches_model(tmp_path):
    bad = tmp_path / "bad.wav"
    bad.write_bytes(b"junk")
    fake = FakePredictor()
    with pytest.raises(AudioError):
        Identifier(fake).identify(bad)
    assert fake.calls == []


def test_markdown_wraps_expected_errors(tmp_path):
    msg = Identifier(FakePredictor()).identify_markdown(tmp_path / "missing.wav")
    assert msg.startswith("❌") and "not found" in msg


def test_markdown_model_error_is_readable(wav_path):
    ident = Identifier(FakePredictor(raises=ModelError("boom")))
    assert "boom" in ident.identify_markdown(wav_path)


def test_markdown_happy_path_has_disclaimer_and_note(wav_path, confident_preds):
    md = Identifier(FakePredictor(confident_preds), {"Turdus merula": "Dusk singer."}).identify_markdown(wav_path)
    assert "Common Blackbird" in md and "Dusk singer." in md and "not a definitive" in md


def test_to_dict_is_json_serialisable(wav_path, confident_preds):
    import json

    d = Identifier(FakePredictor(confident_preds)).identify(wav_path).to_dict()
    assert json.loads(json.dumps(d))["predictions"][0]["confidence"] == 0.93


def test_inference_runs_with_network_blocked(wav_path):
    import socket

    class Sneaky(FakePredictor):
        def predict(self, audio_path, k=3):
            socket.socket().connect(("93.184.216.34", 80))  # example.com, must be blocked

    with pytest.raises(Exception, match="Offline mode"):
        Identifier(Sneaky()).identify(wav_path)


def test_allow_network_flag_disables_guard(wav_path):
    out = Identifier(FakePredictor([Prediction("A", "A a", 0.9)]), enforce_offline=False)
    assert out.identify(wav_path).predictions
