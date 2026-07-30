from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import requests

API_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
BASE_DIR = Path(__file__).resolve().parent
SSML_DIR = BASE_DIR / "ssml"
AUDIO_DIR = BASE_DIR / "audio"


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Не задана переменная окружения {name}")
    return value


def synthesize(ssml: str, output: Path, *, api_key: str, folder_id: str,
               voice: str, emotion: str, speed: float, retries: int = 3) -> None:
    headers = {"Authorization": f"Api-Key {api_key}"}
    data = {
        "ssml": ssml,
        "lang": "ru-RU",
        "voice": voice,
        "emotion": emotion,
        "speed": str(speed),
        "format": "mp3",
        "folderId": folder_id,
    }
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(API_URL, headers=headers, data=data, timeout=120)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Yandex SpeechKit: HTTP {response.status_code}: {response.text[:500]}"
                )
            content_type = response.headers.get("Content-Type", "")
            if "audio" not in content_type and not response.content.startswith(
                (b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")
            ):
                raise RuntimeError(f"Вместо MP3 получен неожиданный ответ: {content_type}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(response.content)
            return
        except (requests.RequestException, RuntimeError) as exc:
            if attempt == retries:
                raise
            wait = attempt * 3
            print(f"  Ошибка: {exc}. Повтор через {wait} сек.")
            time.sleep(wait)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Генерация аудио урока JEMIX Academy 2.1 в Yandex SpeechKit"
    )
    parser.add_argument("--voice", default="ermil")
    parser.add_argument("--emotion", default="good")
    parser.add_argument("--speed", type=float, default=0.95)
    parser.add_argument("--slide", type=int, help="Сгенерировать один слайд, например 7")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    api_key = required_env("YANDEX_API_KEY")
    folder_id = required_env("YANDEX_FOLDER_ID")

    files = sorted(SSML_DIR.glob("slide*.ssml"))
    if args.slide:
        target = SSML_DIR / f"slide{args.slide:02d}.ssml"
        files = [target] if target.exists() else []
    if not files:
        raise RuntimeError("SSML-файлы не найдены")

    print(f"Голос: {args.voice}; эмоция: {args.emotion}; скорость: {args.speed}")
    for ssml_file in files:
        output = AUDIO_DIR / f"{ssml_file.stem}.mp3"
        if output.exists() and not args.overwrite:
            print(f"SKIP {output.name} — файл уже существует")
            continue
        print(f"GENERATE {output.name}")
        synthesize(
            ssml_file.read_text(encoding="utf-8"), output,
            api_key=api_key,
            folder_id=folder_id,
            voice=args.voice,
            emotion=args.emotion,
            speed=args.speed,
        )
        print(f"  OK: {output.stat().st_size:,} bytes")

    print(f"Готово. MP3 находятся в папке: {AUDIO_DIR}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
