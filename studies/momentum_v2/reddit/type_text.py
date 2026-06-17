#!/usr/bin/env python3
"""Type a text file into the currently-focused window, character-by-character,
after a short countdown — to enter text into a "paste-blocked" textarea (e.g. some
Reddit editors) by emitting REAL keystrokes instead of a paste event.

For your OWN content only (this is just automated typing, like an autotyper).

Backends (auto-detected):
  - xdotool  → X11 sessions (rock solid; flags certain).
  - ydotool  → Wayland (kernel uinput; needs the ydotoold daemon + uinput access).

Usage:
  python3 type_text.py --file body.txt --delay 25 --countdown 5
  # then click/focus the Reddit textarea before the countdown hits 0.

Tips:
  --delay   ms between keystrokes (25 is plenty; the blocker stops *paste* events,
            not fast typing — a small delay just avoids any rate-limit).
  --jitter  adds 0..N ms random pause per line for a more human cadence (optional).
"""

from __future__ import annotations

import argparse
import os
import random
import shutil
import subprocess
import sys
import time


def detect_backend() -> str | None:
    if os.environ.get("XDG_SESSION_TYPE") == "x11" and shutil.which("xdotool"):
        return "xdotool"
    if shutil.which("ydotool"):
        return "ydotool"
    if shutil.which("xdotool"):
        return "xdotool"  # may work if the target runs under XWayland
    return None


def type_chunk(backend: str, text: str, delay_ms: int) -> None:
    if backend == "xdotool":
        subprocess.run(["xdotool", "type", "--delay", str(delay_ms), "--clearmodifiers", "--", text], check=True)
    else:  # ydotool — flag is --key-delay on recent versions (older: --key-delay/-d)
        subprocess.run(["ydotool", "type", "--key-delay", str(delay_ms), "--", text], check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Autotype a file into the focused window.")
    ap.add_argument("--file", required=True, help="text file to type")
    ap.add_argument("--delay", type=int, default=25, help="ms between keystrokes")
    ap.add_argument("--jitter", type=int, default=0, help="ms of random extra pause per line (human-like)")
    ap.add_argument("--countdown", type=int, default=5, help="seconds to focus the textarea before typing")
    a = ap.parse_args()

    backend = detect_backend()
    if not backend:
        sys.exit(
            "No typing backend found.\n"
            "  X11 session : sudo apt install xdotool   (simplest — log in via 'Ubuntu on Xorg')\n"
            "  Wayland     : sudo apt install ydotool    (then start ydotoold + grant /dev/uinput; see README note)"
        )
    text = open(a.file, encoding="utf-8").read()
    secs = len(text) * a.delay / 1000.0
    print(f"backend={backend}  chars={len(text)}  ~{secs:.0f}s of typing at {a.delay}ms/key")
    print(f"FOCUS the textarea now — typing starts in {a.countdown}s (Ctrl+C to abort)...")
    for i in range(a.countdown, 0, -1):
        print(i, end=" ", flush=True)
        time.sleep(1)
    print("\ntyping…")
    if a.jitter > 0:
        for line in text.splitlines(keepends=True):
            type_chunk(backend, line, a.delay)
            time.sleep(random.uniform(0, a.jitter) / 1000.0)
    else:
        type_chunk(backend, text, a.delay)
    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
