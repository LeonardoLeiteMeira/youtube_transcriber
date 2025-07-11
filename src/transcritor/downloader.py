"""Download audio module."""

from __future__ import annotations

import logging
from pathlib import Path

import yt_dlp

logger = logging.getLogger(__name__)


def download_audio(url: str, out_dir: Path = Path("/tmp/audio")) -> Path:
    """Download audio from YouTube as WAV.

    Args:
        url: Public YouTube URL.
        out_dir: Directory to store audio.

    Returns:
        Path to WAV file.

    Example:
        >>> download_audio("https://youtu.be/abc123")
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            wav_path = out_dir / f"{info['id']}.wav"
    except Exception as err:  # noqa: BLE001
        raise RuntimeError("yt-dlp failed") from err
    return wav_path
