import numpy as np
import pytest
import soundfile as sf

from trailbird.audio import CHUNK_SECONDS, SAMPLE_RATE, AudioError, load_audio, to_chunks


def _wav(tmp_path, sr=22050, seconds=4.0, channels=1):
    t = np.linspace(0, seconds, int(sr * seconds), endpoint=False)
    x = 0.3 * np.sin(2 * np.pi * 3000 * t).astype("float32")
    if channels == 2:
        x = np.stack([x, x], axis=1)
    p = tmp_path / "tone.wav"
    sf.write(p, x, sr)
    return p


def test_load_resamples_to_48k_mono(tmp_path):
    a = load_audio(_wav(tmp_path, channels=2))
    assert a.ndim == 1 and a.dtype == np.float32
    assert abs(a.size - 4 * SAMPLE_RATE) <= 2


def test_chunk_shape_and_padding():
    chunks = to_chunks(np.ones(int(SAMPLE_RATE * 4), dtype=np.float32))
    assert chunks.shape == (2, int(SAMPLE_RATE * CHUNK_SECONDS))
    assert chunks[1, -1] == 0.0


def test_missing_file():
    with pytest.raises(AudioError, match="not found"):
        load_audio("/nope/x.wav")


def test_none_input():
    with pytest.raises(AudioError, match="No audio"):
        load_audio(None)


def test_unsupported_extension(tmp_path):
    p = tmp_path / "x.txt"
    p.write_text("hi")
    with pytest.raises(AudioError, match="Unsupported"):
        load_audio(p)


def test_corrupt_audio(tmp_path):
    p = tmp_path / "bad.wav"
    p.write_bytes(b"not audio at all")
    with pytest.raises(AudioError, match="decode"):
        load_audio(p)
