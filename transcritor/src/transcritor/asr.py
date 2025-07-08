"""ASR using Whisper."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import whisper

logger = logging.getLogger(__name__)


def transcribe(wav_fp: Path, model_name: str = "large-v3") -> List[Dict]:
    """Transcribe audio with Whisper.

    Args:
        wav_fp: Path to WAV file.
        model_name: Whisper model to use.

    Returns:
        List of segments dicts with start, end and text.

    Example:
        >>> transcribe(Path("audio.wav"), model_name="tiny")
    """
    model = whisper.load_model(model_name)
    result = model.transcribe(str(wav_fp), fp16=False)
    segments = [
        {"start": seg["start"], "end": seg["end"], "text": seg["text"]}
        for seg in result["segments"]
    ]
    return segments
