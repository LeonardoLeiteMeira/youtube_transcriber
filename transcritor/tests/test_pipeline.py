from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))


def test_small_clip(tmp_path: Path):
    """Faz download/transcrição de um vídeo curto CC-0 (<10 s)."""
    from transcritor.downloader import download_audio
    from transcritor.normalizer import normalize
    from transcritor.asr import transcribe
    from transcritor.subs import write_srt

    url = "https://youtu.be/J---aiyznGQ"
    wav = normalize(download_audio(url, tmp_path))
    segments = transcribe(wav, model_name="tiny")
    srt_file = tmp_path / "out.srt"
    write_srt(segments, srt_file)
    assert srt_file.exists() and srt_file.stat().st_size > 50
