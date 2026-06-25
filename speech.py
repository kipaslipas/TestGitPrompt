"""Local (offline) speech-to-text using faster-whisper.

The Whisper model is loaded lazily and cached so it is only built once per
process. The first run downloads the chosen model (~140 MB for "base").
"""

from __future__ import annotations

import io
import tempfile

_MODEL_CACHE: dict = {}


def _get_model(model_size: str = "tiny"):
    if model_size not in _MODEL_CACHE:
        # Imported lazily so importing this module is cheap and the unit
        # tests for matcher/attendance don't require faster-whisper.
        from faster_whisper import WhisperModel

        _MODEL_CACHE[model_size] = WhisperModel(
            model_size, device="cpu", compute_type="int8"
        )
    return _MODEL_CACHE[model_size]


def transcribe_bytes(audio_bytes: bytes, model_size: str = "tiny") -> str:
    """Transcribe raw audio file bytes (e.g. a WAV from st.audio_input)."""
    model = _get_model(model_size)

    # faster-whisper accepts a file path or file-like object. We persist to a
    # temp file for maximum compatibility across audio container formats.
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        segments, _info = model.transcribe(tmp_path, language="en", beam_size=5)
        return " ".join(seg.text for seg in segments).strip()
    finally:
        import os

        try:
            os.remove(tmp_path)
        except OSError:
            pass
