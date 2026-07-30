from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

API_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / "audio"
SSML_DIR = ROOT / "ssml"
MANIFEST_PATH = ROOT / "audio_manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Yandex SpeechKit audio for JEMIX lesson 2.5")
    parser.add_argument("--voice", default="ermil")
    parser.add_argument("--emotion", default="good")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def synthesize(ssml: str, output_path: Path, api_key: str, folder_id: str, voice: str, emotion: str, speed: float) -> None:
    headers = {"Authorization": f"Api-Key {api_key}"}
    data = {
        "ssml": ssml,
        "lang": "ru-RU",
        "voice": voice,
        "emotion": emotion,
        "speed": str(speed),
        "folderId": folder_id,
        "format": "mp3",
    }
    delays = [3, 6, 12]
    last_error = None
    for attempt in range(len(delays) + 1):
        response = requests.post(API_URL, headers=headers, data=data, timeout=120)
        if response.status_code == 200:
            output_path.write_bytes(response.content)
            return
        last_error = f"Yandex SpeechKit HTTP {response.status_code}: {response.text}"
        if attempt < len(delays):
            delay = delays[attempt]
            print(f"Error: {last_error}. Retry in {delay} sec.")
            time.sleep(delay)
    raise RuntimeError(last_error or "Unknown Yandex SpeechKit error")


def main() -> int:
    args = parse_args()
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("YANDEX_API_KEY", "").strip()
    folder_id = os.getenv("YANDEX_FOLDER_ID", "").strip()
    if not api_key or not folder_id:
        print("ERROR: Fill YANDEX_API_KEY and YANDEX_FOLDER_ID in .env")
        return 2

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    slides = manifest["slides"]
    AUDIO_DIR.mkdir(exist_ok=True)

    print(f"Voice: {args.voice}; emotion: {args.emotion}; speed: {args.speed}")
    print("Lesson 2.5. Audio is generated for slides 01-20 and 26 only.")

    for item in slides:
        slide = int(item["slide"])
        filename = f"slide{slide:02d}.mp3"
        output_path = AUDIO_DIR / filename
        if output_path.exists() and not args.overwrite:
            print(f"SKIP {filename}")
            continue
        ssml_path = SSML_DIR / f"slide{slide:02d}.ssml"
        ssml = ssml_path.read_text(encoding="utf-8")
        print(f"GENERATE {filename}")
        synthesize(ssml, output_path, api_key, folder_id, args.voice, args.emotion, args.speed)
        print(f"OK: {output_path.stat().st_size:,} bytes")

    print(f"DONE: {AUDIO_DIR}")
    print("No audio files were created for slides 21-25 by design.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Cancelled.")
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)
