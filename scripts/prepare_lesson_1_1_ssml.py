#!/usr/bin/env python3
"""Build SaluteSpeech SSML files for JEMIX Academy lesson 1.1."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned) if part.strip()]


def make_ssml(text: str, pause_ms: int) -> str:
    parts: list[str] = ["<speak>"]
    sentences = split_sentences(text)
    for index, sentence in enumerate(sentences):
        parts.append(html.escape(sentence))
        if index < len(sentences) - 1:
            parts.append(f'<break time="{pause_ms}ms"/>')
    parts.append("</speak>")
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="voice/modules/module-01/lesson-1.1/narration.json",
        help="Path to narration.json",
    )
    parser.add_argument(
        "--output",
        default="voice/modules/module-01/lesson-1.1",
        help="Folder where slideNN.ssml files will be written",
    )
    parser.add_argument("--pause-ms", type=int, default=450)
    args = parser.parse_args()

    config_path = Path(args.config)
    output_dir = Path(args.output)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    slides = config.get("slides", {})

    if len(slides) != 20:
        raise SystemExit(f"Expected 20 narration entries, found {len(slides)}")

    output_dir.mkdir(parents=True, exist_ok=True)

    for index in range(1, 21):
        mp3_name = f"slide{index:02d}.mp3"
        text = slides.get(mp3_name)
        if not text:
            raise SystemExit(f"Missing narration text for {mp3_name}")

        target = output_dir / f"slide{index:02d}.ssml"
        target.write_text(make_ssml(text, args.pause_ms), encoding="utf-8")
        print(f"OK: {target}")

    print("Prepared 20 SSML files for SaluteSpeech.")


if __name__ == "__main__":
    main()
