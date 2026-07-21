#!/usr/bin/env python3
"""
Генерация озвучки урока JEMIX Academy 1.3 через Yandex SpeechKit API v1.

Пример:
python yandex_tts_lesson_1_3.py ^
  --scorm "JEMIX_Academy_Lesson_1_3_SCORM_UXv2_FINAL_EXACT.zip" ^
  --texts voice_texts_1_3.json ^
  --voice ermil ^
  --emotion good ^
  --speed 1.0 ^
  --overwrite
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any

import requests

TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Создаёт MP3-файлы slide01.mp3...slide21.mp3 и пересобирает SCORM."
    )
    parser.add_argument("--scorm", type=Path, required=True, help="Исходный SCORM ZIP.")
    parser.add_argument(
        "--texts",
        type=Path,
        default=Path("voice_texts_1_3.json"),
        help="JSON с текстами slide01...slide21.",
    )
    parser.add_argument("--output", type=Path, help="Имя итогового ZIP.")
    parser.add_argument("--voice", default="ermil", help="Голос SpeechKit.")
    parser.add_argument("--emotion", default="good", help="Амплуа голоса.")
    parser.add_argument("--speed", type=float, default=1.0, help="Скорость 0.1–3.0.")
    parser.add_argument("--format", choices=("mp3", "oggopus"), default="mp3")
    parser.add_argument("--folder-id", default=os.getenv("YANDEX_FOLDER_ID", ""))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--only",
        help="Только отдельные слайды, например: 1,3,7-10",
    )
    parser.add_argument("--pause", type=float, default=0.3, help="Пауза между запросами.")
    return parser.parse_args()


def parse_slide_filter(value: str | None) -> set[int] | None:
    if not value:
        return None
    result: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            result.update(range(int(start), int(end) + 1))
        else:
            result.add(int(part))
    return result


def load_texts(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Файл текстов не найден: {path}")
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON должен быть объектом: slide01 -> текст.")
    result: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(value, str) and value.strip():
            result[str(key)] = value.strip()
    return result


def get_auth_headers() -> dict[str, str]:
    api_key = os.getenv("YANDEX_API_KEY", "").strip()
    iam_token = os.getenv("YANDEX_IAM_TOKEN", "").strip()

    if api_key:
        return {"Authorization": f"Api-Key {api_key}"}
    if iam_token:
        return {"Authorization": f"Bearer {iam_token}"}

    raise RuntimeError(
        "Не найден ключ. Установите YANDEX_API_KEY или YANDEX_IAM_TOKEN."
    )


def synthesize(
    text: str,
    destination: Path,
    *,
    headers: dict[str, str],
    voice: str,
    emotion: str,
    speed: float,
    audio_format: str,
    folder_id: str,
) -> None:
    if not 0.1 <= speed <= 3.0:
        raise ValueError("Скорость должна быть в диапазоне 0.1–3.0.")

    data = {
        "text": text,
        "lang": "ru-RU",
        "voice": voice,
        "emotion": emotion,
        "speed": str(speed),
        "format": audio_format,
    }
    if folder_id:
        data["folderId"] = folder_id

    response = requests.post(
        TTS_URL,
        headers=headers,
        data=data,
        timeout=(20, 180),
    )

    content_type = response.headers.get("Content-Type", "")
    if response.status_code != 200:
        message = response.text[:1000]
        raise RuntimeError(
            f"SpeechKit вернул HTTP {response.status_code}: {message}"
        )
    if "audio" not in content_type and "octet-stream" not in content_type:
        raise RuntimeError(
            f"Вместо аудио получен Content-Type: {content_type}. "
            f"Ответ: {response.text[:500]}"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.content)

    if destination.stat().st_size < 500:
        raise RuntimeError(f"Слишком маленький аудиофайл: {destination}")


def repack_folder(folder: Path, output_zip: Path) -> None:
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    temp_zip = output_zip.with_suffix(output_zip.suffix + ".tmp")
    if temp_zip.exists():
        temp_zip.unlink()

    # Порядок близок к эталону 1.2 FINAL.
    preferred = [
        "img",
        "audio",
        "style-v2.css",
    ]
    ordered_files: list[Path] = []

    for name in preferred:
        path = folder / name
        if path.is_dir():
            ordered_files.extend(sorted(p for p in path.rglob("*") if p.is_file()))
        elif path.is_file():
            ordered_files.append(path)

    ordered_files.extend(sorted(folder.glob("slide*.html"), reverse=True))

    for name in (
        "progress-v2.js",
        "lesson-v2.js",
        "lesson.yml",
        "index.html",
        "imsmanifest.xml",
        "complete.html",
        "audio-v2.js",
        "scorm.js",
    ):
        path = folder / name
        if path.is_file() and path not in ordered_files:
            ordered_files.append(path)

    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        if path not in ordered_files:
            ordered_files.append(path)

    with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in ordered_files:
            archive.write(path, path.relative_to(folder).as_posix())

    temp_zip.replace(output_zip)


def main() -> int:
    args = parse_args()
    args.scorm = args.scorm.resolve()
    args.texts = args.texts.resolve()

    if not args.scorm.exists():
        print(f"SCORM не найден: {args.scorm}", file=sys.stderr)
        return 2

    texts = load_texts(args.texts)
    selected = parse_slide_filter(args.only)
    headers = get_auth_headers()

    default_output = args.scorm.with_name(
        args.scorm.stem + "_WITH_YANDEX_VOICE.zip"
    )
    output_zip = (args.output or default_output).resolve()

    with tempfile.TemporaryDirectory(prefix="jemix_tts_") as tmp:
        workdir = Path(tmp) / "scorm"
        workdir.mkdir()

        with zipfile.ZipFile(args.scorm, "r") as archive:
            archive.extractall(workdir)

        audio_dir = workdir / "audio"
        audio_dir.mkdir(exist_ok=True)

        generated = 0
        skipped = 0

        for number in range(1, 22):
            if selected is not None and number not in selected:
                continue

            key = f"slide{number:02d}"
            text = texts.get(key, "").strip()
            if not text:
                print(f"[ПРОПУСК] Нет текста: {key}")
                skipped += 1
                continue

            extension = "mp3" if args.format == "mp3" else "ogg"
            destination = audio_dir / f"{key}.{extension}"

            if destination.exists() and destination.stat().st_size > 500 and not args.overwrite:
                print(f"[ГОТОВО] Уже существует: {destination.name}")
                skipped += 1
                continue

            print(f"[{number:02d}/21] Генерация {destination.name}...")
            synthesize(
                text,
                destination,
                headers=headers,
                voice=args.voice,
                emotion=args.emotion,
                speed=args.speed,
                audio_format=args.format,
                folder_id=args.folder_id,
            )
            print(f"          {destination.stat().st_size / 1024:.1f} КБ")
            generated += 1
            time.sleep(max(0.0, args.pause))

        if args.format != "mp3":
            print(
                "Внимание: исходный SCORM обычно ожидает файлы .mp3. "
                "Для урока используйте --format mp3.",
                file=sys.stderr,
            )

        repack_folder(workdir, output_zip)

    print()
    print(f"Создано аудиофайлов: {generated}")
    print(f"Пропущено: {skipped}")
    print(f"Итоговый SCORM: {output_zip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
