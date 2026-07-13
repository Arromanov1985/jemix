#!/usr/bin/env python3
"""Generate lesson 1.1 MP3 narration from narration.json using edge-tts."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import edge_tts


def valid_audio(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 1024:
        return False
    return path.read_bytes()[:3] == b"ID3" or path.read_bytes()[:2] in {b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"}


async def generate(config_path: Path, output_dir: Path, overwrite: bool) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    voice = config["voice"]
    rate = config.get("rate", "+0%")
    volume = config.get("volume", "+0%")
    slides = config["slides"]

    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, text in slides.items():
        target = output_dir / filename
        if valid_audio(target) and not overwrite:
            print(f"SKIP: {target} already contains valid MP3 audio")
            continue
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
        await communicate.save(str(target))
        if not valid_audio(target):
            raise SystemExit(f"Generated audio is invalid: {target}")
        print(f"OK: {target} ({target.stat().st_size} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="voice/modules/module-01/lesson-1.1/narration.json",
    )
    parser.add_argument(
        "--output",
        default="voice/modules/module-01/lesson-1.1/audio",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    asyncio.run(generate(Path(args.config), Path(args.output), args.overwrite))


if __name__ == "__main__":
    main()
