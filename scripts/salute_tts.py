#!/usr/bin/env python3
"""Generate audio files from JEMIX Voice SSML scripts via SaluteSpeech.

Usage:
  python scripts/salute_tts.py voice/modules/module-01/lesson-1.1
  python scripts/salute_tts.py voice/modules/module-01/lesson-1.1 --force

Secrets are read from .env or environment variables.
Do not commit real tokens or credentials.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path
from typing import Dict, Iterable, Optional

import requests
from dotenv import load_dotenv


DEFAULT_TTS_URL = "https://smartspeech.sber.ru/rest/v1/text:synthesize"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def iter_ssml_files(lesson_dir: Path) -> Iterable[Path]:
    return sorted(p for p in lesson_dir.glob("slide*.ssml") if p.is_file())


def output_path_for(ssml_path: Path) -> Path:
    audio_dir = ssml_path.parent / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    return audio_dir / f"{ssml_path.stem}.mp3"


def synthesize_ssml(ssml: str, token: str, tts_url: str, voice: Optional[str] = None) -> bytes:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/ssml+xml; charset=utf-8",
        "Accept": "audio/mpeg",
    }

    params: Dict[str, str] = {}
    if voice:
        params["voice"] = voice

    response = requests.post(
        tts_url,
        params=params,
        headers=headers,
        data=ssml.encode("utf-8"),
        timeout=120,
        verify=True,
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"SaluteSpeech error {response.status_code}: {response.text[:1000]}"
        )

    return response.content


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson_dir", help="Folder with slideXX.ssml files")
    parser.add_argument("--force", action="store_true", help="Regenerate existing mp3 files")
    parser.add_argument("--dry-run", action="store_true", help="Show files without API calls")
    args = parser.parse_args()

    load_dotenv()

    lesson_dir = Path(args.lesson_dir).resolve()
    if not lesson_dir.exists():
        print(f"Folder not found: {lesson_dir}", file=sys.stderr)
        return 2

    token = os.getenv("SBER_SALUTE_TOKEN", "").strip()
    tts_url = os.getenv("SBER_TTS_URL", DEFAULT_TTS_URL).strip() or DEFAULT_TTS_URL
    voice = os.getenv("SBER_TTS_VOICE", "").strip() or None

    ssml_files = list(iter_ssml_files(lesson_dir))
    if not ssml_files:
        print(f"No slide*.ssml files found in {lesson_dir}", file=sys.stderr)
        return 2

    if not token and not args.dry_run:
        print("SBER_SALUTE_TOKEN is empty. Put it into .env first.", file=sys.stderr)
        return 2

    print(f"Lesson: {lesson_dir}")
    print(f"SSML files: {len(ssml_files)}")

    for ssml_path in ssml_files:
        ssml = read_text(ssml_path)
        mp3_path = output_path_for(ssml_path)
        hash_path = mp3_path.with_suffix(".sha256")
        current_hash = sha256_text(ssml)

        if mp3_path.exists() and hash_path.exists() and not args.force:
            if hash_path.read_text(encoding="utf-8").strip() == current_hash:
                print(f"skip: {mp3_path.name}")
                continue

        if args.dry_run:
            print(f"dry-run: {ssml_path.name} -> {mp3_path}")
            continue

        print(f"generate: {ssml_path.name} -> {mp3_path.name}")
        audio = synthesize_ssml(ssml, token=token, tts_url=tts_url, voice=voice)
        mp3_path.write_bytes(audio)
        hash_path.write_text(current_hash, encoding="utf-8")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
