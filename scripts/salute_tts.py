#!/usr/bin/env python3
"""Generate audio files from JEMIX Voice SSML scripts via SaluteSpeech.

Usage:
  python scripts/salute_tts.py voice/modules/module-01/lesson-1.1
  python scripts/salute_tts.py voice/modules/module-01/lesson-1.1 --force
  python scripts/salute_tts.py voice/modules/module-01/lesson-1.1 --dry-run

Secrets are read from .env or environment variables.
Do not commit real tokens or credentials.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path
from typing import Dict, Iterable, Optional, Union

import requests
from dotenv import load_dotenv

# Allow running both as a script and as an imported module.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from salute_auth import get_salute_token, ssl_verify_setting  # noqa: E402


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


def synthesize_ssml(
    ssml: str,
    token: str,
    tts_url: str,
    voice: Optional[str] = None,
    verify: Union[bool, str] = True,
) -> bytes:
    headers = {
        "Authorization": f"Bearer {token}",
        # Sber currently accepts application/ssml, not application/ssml+xml.
        "Content-Type": "application/ssml",
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
        verify=verify,
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"SaluteSpeech error {response.status_code}: {response.text[:1000]}"
        )

    return response.content


def generate_lesson(
    lesson_dir: Path,
    *,
    token: Optional[str] = None,
    force: bool = False,
    dry_run: bool = False,
    verbose: bool = True,
) -> int:
    lesson_dir = Path(lesson_dir).resolve()
    if not lesson_dir.exists():
        print(f"Folder not found: {lesson_dir}", file=sys.stderr)
        return 2

    tts_url = os.getenv("SBER_TTS_URL", DEFAULT_TTS_URL).strip() or DEFAULT_TTS_URL
    voice = os.getenv("SBER_TTS_VOICE", "").strip() or None
    verify = ssl_verify_setting()

    ssml_files = list(iter_ssml_files(lesson_dir))
    if not ssml_files:
        print(f"No slide*.ssml files found in {lesson_dir}", file=sys.stderr)
        return 2

    if token is None and not dry_run:
        token = get_salute_token(verify=verify)

    if verbose:
        print(f"Lesson: {lesson_dir}")
        print(f"SSML files: {len(ssml_files)}")
        if verify is False:
            print("Warning: SSL verification is disabled. Use only for local troubleshooting.")
        elif isinstance(verify, str):
            print(f"SSL CA bundle: {verify}")

    for ssml_path in ssml_files:
        ssml = read_text(ssml_path)
        mp3_path = output_path_for(ssml_path)
        hash_path = mp3_path.with_suffix(".sha256")
        current_hash = sha256_text(ssml)

        if mp3_path.exists() and hash_path.exists() and not force:
            if hash_path.read_text(encoding="utf-8").strip() == current_hash:
                if verbose:
                    print(f"skip: {mp3_path.name}")
                continue

        if dry_run:
            if verbose:
                print(f"dry-run: {ssml_path.name} -> {mp3_path}")
            continue

        if verbose:
            print(f"generate: {ssml_path.name} -> {mp3_path.name}")
        audio = synthesize_ssml(
            ssml,
            token=token or "",
            tts_url=tts_url,
            voice=voice,
            verify=verify,
        )
        mp3_path.write_bytes(audio)
        hash_path.write_text(current_hash, encoding="utf-8")

    if verbose:
        print("Done.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson_dir", help="Folder with slideXX.ssml files")
    parser.add_argument("--force", action="store_true", help="Regenerate existing mp3 files")
    parser.add_argument("--dry-run", action="store_true", help="Show files without API calls")
    args = parser.parse_args()

    load_dotenv(override=True)
    return generate_lesson(
        Path(args.lesson_dir),
        force=args.force,
        dry_run=args.dry_run,
        verbose=True,
    )


if __name__ == "__main__":
    raise SystemExit(main())
