# youtube-transcript

Utility to turn a YouTube video into local context for LLM analysis:

1. download the video;
2. transcribe the audio with timestamps;
3. extract one frame per second as visual context.

Generated outputs are intentionally ignored by git because videos, frames and
transcripts can be large or copyrighted.

## Requirements

- Python 3.11+
- `ffmpeg` available on `PATH`
- Python dependencies from `requirements.txt`

Install locally:

```bash
python -m venv .venv-youtube-transcript
. .venv-youtube-transcript/bin/activate
pip install -r youtube-transcript/requirements.txt
```

Install `ffmpeg` if needed:

```bash
sudo apt-get install ffmpeg
```

## Usage

```bash
python youtube-transcript/youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Optional flags:

```bash
python youtube-transcript/youtube_transcript.py \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --output-dir youtube-transcript \
  --model small \
  --language pt \
  --frame-rate 1
```

## Output Layout

Each run creates a folder by YouTube video id:

```text
youtube-transcript/VIDEO_ID/
├── frames/
│   ├── 1.png
│   ├── 2.png
│   └── ...
├── metadata.json
├── source.mp4
├── text.md
├── transcript.md
└── transcript.txt
```

`text.md` and `transcript.md` follow the LLM-friendly format:

```text
# Video Title

URL: https://www.youtube.com/watch?v=VIDEO_ID

## Transcript

[00:00] ...
[01:23] ...
```
