import numpy as np
import pytest
import soundfile as sf

from trailbird.results import Prediction


class FakePredictor:
    """Test double implementing the Predictor protocol. Used only in tests."""

    def __init__(self, preds=None, raises=None):
        self.preds = preds if preds is not None else []
        self.raises = raises
        self.calls = []

    def predict(self, audio_path, k=3):
        self.calls.append((str(audio_path), k))
        if self.raises:
            raise self.raises
        return self.preds


@pytest.fixture
def wav_path(tmp_path):
    sr = 22050
    t = np.linspace(0, 4, sr * 4, endpoint=False)
    p = tmp_path / "tone.wav"
    sf.write(p, (0.3 * np.sin(2 * np.pi * 3000 * t)).astype("float32"), sr)
    return p


@pytest.fixture
def confident_preds():
    return [
        Prediction("Common Blackbird", "Turdus merula", 0.93),
        Prediction("European Robin", "Erithacus rubecula", 0.31),
        Prediction("Great Tit", "Parus major", 0.12),
        Prediction("Song Thrush", "Turdus philomelos", 0.05),
    ]
