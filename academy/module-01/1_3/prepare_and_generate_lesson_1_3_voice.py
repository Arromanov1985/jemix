#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import requests

TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"

MIN_DURATION_SECONDS = 30
MAX_DURATION_SECONDS = 40
WORDS_PER_MINUTE = 135

PAUSES = {
    "sentence": 350,
    "important": 600,
    "block": 800,
    "example": 900,
    "question": 700,
    "remember": 500,
}

ALLOWED_MODES = {"calm", "focus", "warning", "practice", "check", "summary"}
ALLOWED_SLIDE_TYPES = {
    "intro", "framework", "theory", "scheme",
    "case", "error", "check", "summary",
}

FORBIDDEN_PATTERNS = {
    r"м³/ч": "Единицу м³/ч нужно написать словами.",
    r"л/мин": "Единицу л/мин нужно написать словами.",
    r"кВт": "Единицу кВт нужно написать словами.",
    r"\b\d+\s*В\b": "Вольты нужно написать словами.",
    r"\b\d+\s*Гц\b": "Герцы нужно написать словами.",
    r"Ø": "Диаметр нужно написать словами.",
    r"\bIP\d+\b": "Степень защиты IP нужно подготовить для озвучки.",
    r"\bDN\d+\b": "Обозначение DN нужно подготовить для озвучки.",
    r"\bPN\d+\b": "Обозначение PN нужно подготовить для озвучки.",
}

PRONUNCIATION_TERMS = [
    "гидроаккумулятор",
    "производительность",
    "манометр",
    "кавитация",
    "колодезный",
    "скважинный",
    "циркуляционный",
    "водоотведение",
    "точка водоразбора",
    "канализационная установка",
    "динамический уровень",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Подготавливает сценарии урока JEMIX Academy 1.3, "
            "создаёт SSML, выполняет QA, генерирует MP3 "
            "и при необходимости пересобирает SCORM."
        )
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("lesson_1_3_voice_source.json"),
    )
    parser.add_argument(
        "--voice-dir",
        type=Path,
        default=Path("voice/module-01/lesson-1.3"),
    )
    parser.add_argument("--scorm", type=Path)
    parser.add_argument("--output-scorm", type=Path)
    parser.add_argument("--voice", default="ermil")
    parser.add_argument("--emotion", default="good")
    parser.add_argument("--speed", type=float, default=0.92)
    parser.add_argument(
        "--folder-id",
        default=os.getenv("YANDEX_FOLDER_ID", ""),
    )
    parser.add_argument("--only")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
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
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)

            if start > end:
                raise ValueError(f"Некорректный диапазон слайдов: {part}")

            result.update(range(start, end + 1))
        else:
            result.add(int(part))

    invalid = sorted(number for number in result if number < 1 or number > 21)
    if invalid:
        raise ValueError(f"Номера слайдов должны быть от 1 до 21: {invalid}")

    return result


def count_words(text: str) -> int:
    pattern = r"[A-Za-zА-Яа-яЁё0-9]+(?:[-–][A-Za-zА-Яа-яЁё0-9]+)?"
    return len(re.findall(pattern, text))


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def estimate_duration(text: str, speed: float) -> float:
    if speed <= 0:
        raise ValueError("Скорость должна быть больше нуля.")

    words = count_words(text)
    speech_seconds = words / (WORDS_PER_MINUTE * speed) * 60
    sentence_count = len(split_sentences(text))
    pause_seconds = max(0, sentence_count - 1) * 0.35 + 1.3
    return round(speech_seconds + pause_seconds, 1)


def escape_xml(text: str) -> str:
    return html.escape(text, quote=False)


def select_pause(sentence: str, index: int, total: int, mode: str) -> int:
    if index == total - 1:
        return 0

    lower = sentence.lower()

    if sentence.endswith("?"):
        return PAUSES["question"]
    if "запомните" in lower:
        return PAUSES["remember"]
    if "представьте" in lower:
        return PAUSES["example"]
    if mode in {"warning", "focus"} and index == 0:
        return PAUSES["important"]
    if index == total // 2:
        return PAUSES["block"]

    return PAUSES["sentence"]


def make_ssml(text: str, mode: str) -> str:
    sentences = split_sentences(text)
    if not sentences:
        raise ValueError("Нельзя создать SSML из пустого текста.")

    body: list[str] = []

    for index, sentence in enumerate(sentences):
        body.append(f"  <s>{escape_xml(sentence)}</s>")

        pause = select_pause(
            sentence=sentence,
            index=index,
            total=len(sentences),
            mode=mode,
        )

        if pause:
            body.append(f'  <break time="{pause}ms"/>')

    return "<speak>\n" + "\n".join(body) + "\n</speak>\n"


def load_source(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Файл сценариев не найден: {path.resolve()}")

    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, list):
        raise ValueError("Файл сценариев должен содержать JSON-массив.")

    if len(data) != 21:
        raise ValueError(f"Ожидается 21 слайд, получено: {len(data)}")

    expected_numbers = list(range(1, 22))
    actual_numbers: list[int] = []
    required_fields = {"number", "title", "type", "mode", "goal", "text"}

    for slide in data:
        if not isinstance(slide, dict):
            raise ValueError("Каждый слайд должен быть JSON-объектом.")

        missing = required_fields - set(slide)
        if missing:
            raise ValueError(f"В сценарии отсутствуют поля: {sorted(missing)}")

        actual_numbers.append(int(slide["number"]))

    if actual_numbers != expected_numbers:
        raise ValueError(
            "Нумерация слайдов должна идти последовательно от 1 до 21. "
            f"Получено: {actual_numbers}"
        )

    return data


def validate_ssml(ssml: str) -> list[str]:
    errors: list[str] = []

    try:
        root = ET.fromstring(ssml)
    except ET.ParseError as exc:
        return [f"Некорректный XML: {exc}"]

    if root.tag != "speak":
        errors.append("Корневой тег SSML должен быть <speak>.")

    allowed_tags = {"speak", "s", "break", "p", "sub", "phoneme"}

    for element in root.iter():
        if element.tag not in allowed_tags:
            errors.append(f"Неподдерживаемый тег: <{element.tag}>")

    return errors


def qa_slide(
    slide: dict[str, Any],
    ssml: str,
    speed: float,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    text = str(slide["text"]).strip()
    number = int(slide["number"])
    slide_type = str(slide["type"])
    mode = str(slide["mode"])

    errors.extend(validate_ssml(ssml))

    if mode not in ALLOWED_MODES:
        errors.append(f"Неизвестный режим речи: {mode}")

    if slide_type not in ALLOWED_SLIDE_TYPES:
        errors.append(f"Неизвестный тип слайда: {slide_type}")

    for pattern, message in FORBIDDEN_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(message)

    long_sentences = [
        sentence
        for sentence in split_sentences(text)
        if count_words(sentence) > 16
    ]

    if long_sentences:
        warnings.append(
            f"Предложений длиннее шестнадцати слов: {len(long_sentences)}."
        )

    if "<prosody" in ssml:
        errors.append("Тег <prosody> не поддерживается используемым API.")

    if "<emphasis" in ssml:
        errors.append("Тег <emphasis> не поддерживается используемым API.")

    duration = estimate_duration(text=text, speed=speed)

    if not MIN_DURATION_SECONDS <= duration <= MAX_DURATION_SECONDS:
        warnings.append(
            f"Оценка длительности: {duration} секунды. "
            f"Цель: {MIN_DURATION_SECONDS}–{MAX_DURATION_SECONDS} секунд."
        )

    pronunciation_review = [
        term
        for term in PRONUNCIATION_TERMS
        if term.lower() in text.lower()
    ]

    return {
        "slide": number,
        "status": "ok" if not errors else "needs_fix",
        "duration_estimate_sec": duration,
        "word_count": count_words(text),
        "errors": errors,
        "warnings": warnings,
        "pronunciation_review": pronunciation_review,
    }


def create_slide_markdown(
    slide: dict[str, Any],
    ssml: str,
    qa: dict[str, Any],
) -> str:
    warning_lines = (
        "\n".join(f"- {warning}" for warning in qa["warnings"])
        if qa["warnings"]
        else "- none"
    )

    error_lines = (
        "\n".join(f"- {error}" for error in qa["errors"])
        if qa["errors"]
        else "- none"
    )

    pronunciation_lines = (
        "\n".join(f"- {term}" for term in qa["pronunciation_review"])
        if qa["pronunciation_review"]
        else "- none"
    )

    return (
        f"# Slide {int(slide['number']):02d} — {slide['title']}\n\n"
        f"## Type\n\n{slide['type']}\n\n"
        f"## Emotion mode\n\n{slide['mode']}\n\n"
        f"## Goal\n\n{slide['goal']}\n\n"
        f"## Plain text\n\n{slide['text']}\n\n"
        f"## SSML\n\n```xml\n{ssml.strip()}\n```\n\n"
        f"## Estimated duration\n\n{qa['duration_estimate_sec']} sec\n\n"
        f"## Word count\n\n{qa['word_count']}\n\n"
        f"## QA status\n\n{qa['status']}\n\n"
        f"### Warnings\n\n{warning_lines}\n\n"
        f"### Errors\n\n{error_lines}\n\n"
        f"### Pronunciation review\n\n{pronunciation_lines}\n"
    )


def write_voice_assets(
    slides: list[dict[str, Any]],
    voice_dir: Path,
    speed: float,
) -> list[dict[str, Any]]:
    voice_dir.mkdir(parents=True, exist_ok=True)
    (voice_dir / "audio").mkdir(parents=True, exist_ok=True)

    qa_results: list[dict[str, Any]] = []

    for slide in slides:
        number = int(slide["number"])
        key = f"slide{number:02d}"
        text = str(slide["text"]).strip()
        mode = str(slide["mode"])

        ssml = make_ssml(text=text, mode=mode)
        qa = qa_slide(slide=slide, ssml=ssml, speed=speed)
        qa_results.append(qa)

        (voice_dir / f"{key}.txt").write_text(text + "\n", encoding="utf-8")
        (voice_dir / f"{key}.ssml").write_text(ssml, encoding="utf-8")
        (voice_dir / f"{key}.md").write_text(
            create_slide_markdown(slide=slide, ssml=ssml, qa=qa),
            encoding="utf-8",
        )

    write_voice_qa(qa_results=qa_results, voice_dir=voice_dir)
    write_audio_manifest(
        slides=slides,
        qa_results=qa_results,
        voice_dir=voice_dir,
        speed=speed,
    )

    return qa_results


def write_voice_qa(
    qa_results: list[dict[str, Any]],
    voice_dir: Path,
) -> None:
    lines = ["# Voice QA — lesson-1.3", "", "## Automatic checks", ""]

    for qa in qa_results:
        slide_number = int(qa["slide"])

        lines.append(
            f"- slide{slide_number:02d}: "
            f"{qa['status']}; "
            f"{qa['duration_estimate_sec']} sec; "
            f"{qa['word_count']} words"
        )

        for warning in qa["warnings"]:
            lines.append(f"  - warning: {warning}")

        for error in qa["errors"]:
            lines.append(f"  - error: {error}")

        if qa["pronunciation_review"]:
            lines.append(
                "  - listen carefully: "
                + ", ".join(qa["pronunciation_review"])
            )

    lines.extend(
        [
            "",
            "## Final listening",
            "",
            "- naturalness: pending",
            "- pronunciation: pending",
            "- pauses: pending",
            "- test neutrality: pending",
            "- duration: pending",
            "- publication: pending",
            "",
        ]
    )

    (voice_dir / "voice_qa.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def write_audio_manifest(
    slides: list[dict[str, Any]],
    qa_results: list[dict[str, Any]],
    voice_dir: Path,
    speed: float,
) -> None:
    lines = [
        "lesson: '1.3'",
        "voice_provider: yandex_speechkit_v1",
        "voice_profile:",
        "  role: technical_mentor",
        "  voice: ermil",
        "  emotion: good",
        f"  speed: {speed}",
        "slides:",
    ]

    for slide, qa in zip(slides, qa_results):
        number = int(slide["number"])

        lines.extend(
            [
                f"  - slide: {number:02d}",
                f"    title: '{slide['title']}'",
                f"    type: {slide['type']}",
                f"    mode: {slide['mode']}",
                f"    text: slide{number:02d}.txt",
                f"    ssml: slide{number:02d}.ssml",
                f"    audio: audio/slide{number:02d}.mp3",
                f"    estimated_duration_sec: {qa['duration_estimate_sec']}",
                f"    qa: {qa['status']}",
            ]
        )

    (voice_dir / "audio_manifest.yml").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def get_auth_headers() -> dict[str, str]:
    api_key = os.getenv("YANDEX_API_KEY", "").strip()
    iam_token = os.getenv("YANDEX_IAM_TOKEN", "").strip()

    if api_key:
        return {"Authorization": f"Api-Key {api_key}"}

    if iam_token:
        return {"Authorization": f"Bearer {iam_token}"}

    raise RuntimeError(
        "Не найден ключ. Установите YANDEX_API_KEY "
        "или YANDEX_IAM_TOKEN."
    )


def synthesize_ssml(
    ssml: str,
    destination: Path,
    *,
    voice: str,
    emotion: str,
    speed: float,
    folder_id: str,
    headers: dict[str, str],
) -> None:
    if not 0.1 <= speed <= 3.0:
        raise ValueError("Скорость должна быть в диапазоне от 0.1 до 3.0.")

    data = {
        "ssml": ssml,
        "lang": "ru-RU",
        "voice": voice,
        "emotion": emotion,
        "speed": str(speed),
        "format": "mp3",
    }

    if folder_id:
        data["folderId"] = folder_id

    response = requests.post(
        TTS_URL,
        headers=headers,
        data=data,
        timeout=(20, 180),
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"SpeechKit HTTP {response.status_code}: "
            f"{response.text[:1000]}"
        )

    content_type = response.headers.get("Content-Type", "")

    if "audio" not in content_type and "octet-stream" not in content_type:
        raise RuntimeError(
            f"Вместо аудио получен Content-Type: {content_type}. "
            f"Ответ: {response.text[:500]}"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.content)

    if destination.stat().st_size < 500:
        raise RuntimeError(f"Слишком маленький аудиофайл: {destination}")


def repack_scorm(
    source_scorm: Path,
    voice_dir: Path,
    output_scorm: Path,
) -> None:
    if not source_scorm.exists():
        raise FileNotFoundError(f"Исходный SCORM не найден: {source_scorm}")

    audio_source = voice_dir / "audio"
    mp3_files = sorted(audio_source.glob("slide*.mp3"))

    if not mp3_files:
        raise RuntimeError("В папке audio нет файлов slideXX.mp3.")

    with tempfile.TemporaryDirectory(prefix="jemix_scorm_") as temp_dir:
        workdir = Path(temp_dir) / "package"
        workdir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(source_scorm, "r") as archive:
            archive.extractall(workdir)

        target_audio_dir = workdir / "audio"
        target_audio_dir.mkdir(parents=True, exist_ok=True)

        for mp3_file in mp3_files:
            shutil.copy2(mp3_file, target_audio_dir / mp3_file.name)

        output_scorm.parent.mkdir(parents=True, exist_ok=True)
        temp_zip = output_scorm.with_suffix(output_scorm.suffix + ".tmp")

        if temp_zip.exists():
            temp_zip.unlink()

        with zipfile.ZipFile(
            temp_zip,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            for path in sorted(workdir.rglob("*")):
                if path.is_file():
                    archive.write(
                        path,
                        path.relative_to(workdir).as_posix(),
                    )

        temp_zip.replace(output_scorm)


def print_qa_results(
    qa_results: list[dict[str, Any]],
) -> None:
    for qa in qa_results:
        number = int(qa["slide"])

        print(
            f"slide{number:02d}: "
            f"{qa['duration_estimate_sec']:>4} сек., "
            f"{qa['word_count']:>3} слов, "
            f"{qa['status']}"
        )

        for warning in qa["warnings"]:
            print(f"         предупреждение: {warning}")

        for error in qa["errors"]:
            print(f"         ошибка: {error}")


def main() -> int:
    args = parse_args()

    try:
        args.source = args.source.resolve()
        args.voice_dir = args.voice_dir.resolve()

        if args.scorm:
            args.scorm = args.scorm.resolve()

        if args.output_scorm:
            args.output_scorm = args.output_scorm.resolve()

        selected_slides = parse_slide_filter(args.only)
        slides = load_source(args.source)

        qa_results = write_voice_assets(
            slides=slides,
            voice_dir=args.voice_dir,
            speed=args.speed,
        )

        print(f"Сценарии подготовлены: {args.voice_dir}")
        print_qa_results(qa_results)

        critical_errors = [
            qa for qa in qa_results if qa["status"] != "ok"
        ]

        if critical_errors:
            print(
                "\nОбнаружены критические ошибки QA. Синтез остановлен.",
                file=sys.stderr,
            )
            return 2

        if args.prepare_only:
            print("\nПодготовка завершена без генерации MP3.")
            return 0

        headers = get_auth_headers()
        audio_dir = args.voice_dir / "audio"

        generated = 0
        skipped = 0

        for slide in slides:
            number = int(slide["number"])

            if selected_slides is not None and number not in selected_slides:
                continue

            key = f"slide{number:02d}"
            ssml_path = args.voice_dir / f"{key}.ssml"
            destination = audio_dir / f"{key}.mp3"

            if (
                destination.exists()
                and destination.stat().st_size > 500
                and not args.overwrite
            ):
                print(f"[ПРОПУСК] Уже существует: {destination.name}")
                skipped += 1
                continue

            ssml = ssml_path.read_text(encoding="utf-8")

            print(f"[{number:02d}/21] Генерация {destination.name}")

            synthesize_ssml(
                ssml=ssml,
                destination=destination,
                voice=args.voice,
                emotion=args.emotion,
                speed=args.speed,
                folder_id=args.folder_id,
                headers=headers,
            )

            print(f"          {destination.stat().st_size / 1024:.1f} КБ")
            generated += 1
            time.sleep(0.3)

        print()
        print(f"Создано аудиофайлов: {generated}")
        print(f"Пропущено аудиофайлов: {skipped}")
        print(f"Папка аудио: {audio_dir}")

        if args.scorm:
            output_scorm = (
                args.output_scorm
                if args.output_scorm
                else args.scorm.with_name(
                    args.scorm.stem
                    + "_WITH_YANDEX_VOICE_STANDARD.zip"
                )
            )

            repack_scorm(
                source_scorm=args.scorm,
                voice_dir=args.voice_dir,
                output_scorm=output_scorm,
            )

            print(f"Итоговый SCORM: {output_scorm}")

        print()
        print("Автоматическая генерация завершена.")
        print(
            "Прослушайте MP3 и заполните финальный "
            "раздел файла voice_qa.md."
        )

        return 0

    except KeyboardInterrupt:
        print("\nОперация остановлена пользователем.", file=sys.stderr)
        return 130

    except Exception as exc:
        print(f"\nОШИБКА: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
