"""Audio loading and preprocessing."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

from .errors import AudioError

SAMPLE_RATE = 48_000  # BirdNET input rate
CHUNK_SECONDS = 3.0
SUPPORTED = {".wav", ".flac", ".ogg", ".mp3"}
MAX_SECONDS = 600  # reject clips over 10 minutes to keep memory bounded


def load_audio(path: str | Path, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Load a file as mono float32 at `sr`. Raises AudioError with a helpful message."""
    if path is None or str(path) == "":
        raise AudioError("No audio provided. Upload or record a bird sound first.")
    p = Path(path)
    if not p.exists():
        raise AudioError(f"File not found: {p}")
    if p.suffix.lower() not in SUPPORTED:
        raise AudioError(
            f"Unsupported format '{p.suffix}'. Use one of: {', '.join(sorted(SUPPORTED))}."
        )
    try:
        data, orig_sr = sf.read(str(p), dtype="float32", always_2d=True)
    except Exception as exc:  # soundfile raises various errors on corrupt files
        raise AudioError(f"Could not decode '{p.name}': {exc}") from exc
    if data.size == 0:
        raise AudioError(f"'{p.name}' contains no audio.")
    if data.shape[0] / orig_sr > MAX_SECONDS:
        raise AudioError(f"'{p.name}' is longer than {MAX_SECONDS // 60} minutes. Trim it first.")
    mono = data.mean(axis=1)
    if orig_sr != sr:
        g = np.gcd(int(orig_sr), int(sr))
        mono = resample_poly(mono, sr // g, orig_sr // g).astype(np.float32)
    return mono


def to_chunks(
    audio: np.ndarray, sr: int = SAMPLE_RATE, seconds: float = CHUNK_SECONDS
) -> np.ndarray:
    """Split into fixed-length chunks, zero-padding the tail. Shape: (n, sr*seconds)."""
    size = int(sr * seconds)
    if audio.ndim != 1 or audio.size == 0:
        raise AudioError("Expected non-empty mono audio.")
    n = max(1, int(np.ceil(audio.size / size)))
    padded = np.zeros(n * size, dtype=np.float32)
    padded[: audio.size] = audio
    return padded.reshape(n, size)
