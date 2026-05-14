#!/usr/bin/env python3
"""Download a YouTube video, transcribe it, and extract visual frames."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class DownloadResult:
    video_path: Path
    run_dir: Path
    metadata: dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a YouTube video, transcribe it, and extract frames."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Base output directory. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--model",
        default="small",
        help="faster-whisper model size/name. Common values: tiny, base, small, medium, large-v3.",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Optional language code, e.g. pt, en, es. If omitted, Whisper auto-detects.",
    )
    parser.add_argument(
        "--frame-rate",
        type=float,
        default=1.0,
        help="Frames per second to extract. Default: 1.0",
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Device for faster-whisper. Default: auto",
    )
    parser.add_argument(
        "--compute-type",
        default="default",
        help="faster-whisper compute type, e.g. default, int8, float16. Default: default",
    )
    parser.add_argument(
        "--skip-frames",
        action="store_true",
        help="Skip frame extraction.",
    )
    return parser.parse_args()


def require_executable(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Missing required executable on PATH: {name}")


def slugify(value: str, max_length: int = 80) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return (value or "youtube-video")[:max_length].strip("-")


def safe_video_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-")
    return safe or "unknown"


def format_timestamp(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def download_video(url: str, output_dir: Path) -> DownloadResult:
    try:
        import yt_dlp
    except ImportError as exc:
        raise SystemExit("Missing dependency: install youtube-transcript/requirements.txt") from exc

    output_dir.mkdir(parents=True, exist_ok=True)

    probe_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(probe_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    video_id = str(info.get("id") or "unknown")
    run_dir = output_dir / safe_video_id(video_id)
    run_dir.mkdir(parents=True, exist_ok=True)

    download_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": str(run_dir / "source.%(ext)s"),
        "quiet": False,
        "no_warnings": False,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(download_opts) as ydl:
        downloaded_info = ydl.extract_info(url, download=True)

    video_path = find_downloaded_video(run_dir, downloaded_info)
    metadata = compact_metadata(downloaded_info, url, video_path)
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return DownloadResult(video_path=video_path, run_dir=run_dir, metadata=metadata)


def find_downloaded_video(run_dir: Path, info: dict[str, Any]) -> Path:
    requested = info.get("requested_downloads") or []
    for item in requested:
        filepath = item.get("filepath")
        if filepath and Path(filepath).exists():
            return Path(filepath)

    candidates = sorted(
        [path for path in run_dir.glob("source.*") if path.suffix.lower() in video_suffixes()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    raise SystemExit(f"Could not locate downloaded video in {run_dir}")


def video_suffixes() -> set[str]:
    return {".mp4", ".mkv", ".webm", ".mov", ".avi"}


def compact_metadata(info: dict[str, Any], url: str, video_path: Path) -> dict[str, Any]:
    return {
        "url": url,
        "id": info.get("id"),
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "channel": info.get("channel"),
        "duration_seconds": info.get("duration"),
        "webpage_url": info.get("webpage_url"),
        "downloaded_at": datetime.now(UTC).isoformat(),
        "video_path": str(video_path),
    }


def transcribe_video(
    video_path: Path,
    run_dir: Path,
    metadata: dict[str, Any],
    model_name: str,
    language: str | None,
    device: str,
    compute_type: str,
) -> None:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SystemExit("Missing dependency: install youtube-transcript/requirements.txt") from exc

    kwargs: dict[str, Any] = {}
    if device != "auto":
        kwargs["device"] = device
    if compute_type != "default":
        kwargs["compute_type"] = compute_type

    model = WhisperModel(model_name, **kwargs)
    segments, transcript_info = model.transcribe(
        str(video_path),
        language=language,
        vad_filter=True,
    )

    segment_rows = list(segments)
    transcript_txt = render_plain_transcript(segment_rows)
    transcript_md = render_markdown_transcript(metadata, segment_rows, transcript_info)

    (run_dir / "transcript.txt").write_text(transcript_txt, encoding="utf-8")
    (run_dir / "transcript.md").write_text(transcript_md, encoding="utf-8")
    (run_dir / "text.md").write_text(transcript_md, encoding="utf-8")


def render_plain_transcript(segments: list[Any]) -> str:
    lines = [f"[{format_timestamp(segment.start)}] {segment.text.strip()}" for segment in segments]
    return "\n".join(lines).strip() + "\n"


def render_markdown_transcript(metadata: dict[str, Any], segments: list[Any], info: Any) -> str:
    title = metadata.get("title") or "YouTube Video"
    url = metadata.get("webpage_url") or metadata.get("url")
    detected_language = getattr(info, "language", None)
    language_probability = getattr(info, "language_probability", None)

    lines = [
        f"# {title}",
        "",
        f"URL: {url}",
        f"Video file: `{metadata.get('video_path')}`",
        f"Duration: {metadata.get('duration_seconds')} seconds",
        f"Transcribed at: {datetime.now(UTC).isoformat()}",
    ]
    if detected_language:
        lines.append(f"Detected language: {detected_language} ({language_probability:.2%})")
    lines.extend(["", "## Transcript", ""])
    lines.extend(f"[{format_timestamp(segment.start)}] {segment.text.strip()}" for segment in segments)
    return "\n".join(lines).strip() + "\n"


def extract_frames(video_path: Path, run_dir: Path, frame_rate: float) -> None:
    if frame_rate <= 0:
        raise SystemExit("--frame-rate must be greater than zero")

    frames_dir = run_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vf",
        f"fps={frame_rate}",
        "-start_number",
        "1",
        str(frames_dir / "%d.png"),
    ]
    subprocess.run(command, check=True)


def main() -> int:
    args = parse_args()
    require_executable("ffmpeg")

    download = download_video(args.url, args.output_dir)
    transcribe_video(
        video_path=download.video_path,
        run_dir=download.run_dir,
        metadata=download.metadata,
        model_name=args.model,
        language=args.language,
        device=args.device,
        compute_type=args.compute_type,
    )
    if not args.skip_frames:
        extract_frames(download.video_path, download.run_dir, args.frame_rate)

    print(f"Output written to: {download.run_dir}")
    print(f"Transcript: {download.run_dir / 'text.md'}")
    if not args.skip_frames:
        print(f"Frames: {download.run_dir / 'frames'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}: {exc.cmd}", file=sys.stderr)
        raise SystemExit(exc.returncode) from exc
