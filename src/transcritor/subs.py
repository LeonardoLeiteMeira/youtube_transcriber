"""Subtitle generation utilities."""

from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path
from typing import Dict, List

import srt

logger = logging.getLogger(__name__)


def write_srt(segments: List[Dict], out_path: Path) -> None:
    """Write segments to SRT file.

    Args:
        segments: List of dicts with start, end, text.
        out_path: Destination path.

    Example:
        >>> write_srt([], Path("out.srt"))
    """

    subs = []
    for i, seg in enumerate(segments, start=1):
        subs.append(
            srt.Subtitle(
                index=i,
                start=timedelta(seconds=seg["start"]),
                end=timedelta(seconds=seg["end"]),
                content=seg["text"].strip(),
            )
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(srt.compose(subs), encoding="utf-8")
    logger.info("SRT written to %s", out_path)
