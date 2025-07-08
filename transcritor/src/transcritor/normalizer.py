"""Audio normalization utilities."""

from __future__ import annotations

import logging
from pathlib import Path

import ffmpeg

logger = logging.getLogger(__name__)


def normalize(wav_in: Path) -> Path:
    """Normalize sample rate, channels and loudness using FFmpeg.

    Args:
        wav_in: Input WAV file.

    Returns:
        Path to normalized WAV file.

    Example:
        >>> normalize(Path("in.wav"))
    """

    out_path = wav_in.with_name(f"{wav_in.stem}_norm.wav")
    (
        ffmpeg.input(str(wav_in))
        .output(
            str(out_path),
            ac=1,
            ar=16000,
            af="loudnorm",
            format="wav",
        )
        .overwrite_output()
        .run(quiet=True)
    )
    return out_path
