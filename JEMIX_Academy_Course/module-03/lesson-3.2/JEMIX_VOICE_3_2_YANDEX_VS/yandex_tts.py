from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ENDPOINT = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"


def auth_headers() -> dict[str, str]:
    api_key = os.getenv("YANDEX_API_KEY", "").strip()
    iam_token = os.getenv("YANDEX_IAM_TOKEN", "").strip()
    if api_key:
        return {"Authorization": f"Api-Key {api_key}"}
    if iam_token:
        return {"Authorization": f"Bearer {iam_token}"}
    raise RuntimeError("Укажите YANDEX_API_KEY или YANDEX_IAM_TOKEN в файле .env")


def synthesize(source: Path, output: Path, use_ssml: bool, overwrite: bool) -> None:
    if output.exists() and not overwrite:
        print(f"SKIP {output.name}: файл уже существует")
        return

    content = source.read_text(encoding="utf-8").strip()
    payload = {
        "lang": "ru-RU",
        "voice": os.getenv("YANDEX_VOICE", "ermil"),
        "emotion": os.getenv("YANDEX_EMOTION", "good"),
        "speed": os.getenv("YANDEX_SPEED", "1.0"),
        "format": os.getenv("YANDEX_FORMAT", "mp3"),
        "ssml" if use_ssml else "text": content,
    }
    folder_id = os.getenv("YANDEX_FOLDER_ID", "").strip()
    if folder_id:
        payload["folderId"] = folder_id

    response = requests.post(
        ENDPOINT,
        headers=auth_headers(),
        data=payload,
        timeout=120,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Yandex SpeechKit: HTTP {response.status_code}: {response.text[:1000]}"
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(response.content)
    print(f"OK   {output.name} ({len(response.content):,} bytes)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Пакетная озвучка JEMIX lesson 3.2 через Yandex SpeechKit API v1")
    parser.add_argument("--slide", type=int, help="Сгенерировать только один слайд, например 1")
    parser.add_argument("--plain-text", action="store_true", help="Использовать .txt вместо .ssml")
    parser.add_argument("--overwrite", action="store_true", help="Перезаписывать существующие MP3")
    parser.add_argument("--delay", type=float, default=0.4, help="Пауза между запросами, секунд")
    args = parser.parse_args()

    load_dotenv()
    base = Path(__file__).resolve().parent
    scripts = base / "scripts"
    audio = base / "audio"
    ext = ".txt" if args.plain_text else ".ssml"

    if args.slide:
        if not 1 <= args.slide <= 28:
            parser.error("Номер слайда должен быть от 1 до 28")
        sources = [scripts / f"slide{args.slide:02d}{ext}"]
    else:
        sources = sorted(scripts.glob(f"slide??{ext}"))

    if not sources:
        raise RuntimeError(f"Не найдены файлы {ext} в {scripts}")

    failures: list[str] = []
    for source in sources:
        try:
            output = audio / f"{source.stem}.mp3"
            synthesize(source, output, use_ssml=not args.plain_text, overwrite=args.overwrite)
        except Exception as exc:
            failures.append(f"{source.name}: {exc}")
            print(f"ERROR {source.name}: {exc}", file=sys.stderr)
        time.sleep(max(args.delay, 0))

    if failures:
        print("\nОшибки:", file=sys.stderr)
        for item in failures:
            print(f"- {item}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
