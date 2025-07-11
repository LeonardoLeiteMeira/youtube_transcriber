import argparse
import logging
from pathlib import Path

from transcritor.downloader import download_audio
from transcritor.normalizer import normalize
from transcritor.asr import transcribe
from transcritor.subs import write_srt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YouTube audio transcriber")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--cpu", action="store_true", help="reserved flag")
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("/tmp/subs"),
        help="output directory for SRT",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="ISO 639-1 language code (default auto)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    audio = download_audio(args.url)
    norm_audio = normalize(audio)
    segments = transcribe(norm_audio)
    video_id = audio.stem
    srt_path = args.outdir / f"{video_id}.srt"
    write_srt(segments, srt_path)
    logger.info("SRT written to %s", srt_path)
    print(srt_path)


if __name__ == "__main__":
    main()
