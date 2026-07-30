#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import wave
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import requests

TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
MIN_DURATION = 30
MAX_DURATION = 40
WORDS_PER_MINUTE = 135

PAUSES = {
    "sentence": 350,
    "important": 600,
    "block": 800,
    "example": 900,
    "question": 700,
    "remember": 500,
}

MODES = {"calm", "focus", "warning", "practice", "check", "summary"}
SLIDE_TYPES = {"intro", "framework", "theory", "scheme", "case", "error", "check", "summary"}

FORBIDDEN_PATTERNS = [
    r"м³/ч", r"л/мин", r"кВт", r"\b\d+\s*В\b", r"\b\d+\s*Гц\b",
    r"Ø", r"\bIP\d+\b", r"\bDN\d+\b", r"\bPN\d+\b",
]

PRONUNCIATION_TERMS = [
    "гидроаккумулятор", "производительность", "манометр", "кавитация",
    "колодезный", "скважинный", "циркуляционный", "водоотведение",
    "точка водоразбора",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Подготовка сценариев, SSML, QA, MP3 и SCORM урока JEMIX 1.3."
    )
    parser.add_argument("--source", type=Path, default=Path("lesson_1_3_voice_source.json"))
    parser.add_argument("--voice-dir", type=Path, default=Path("voice/module-01/lesson-1.3"))
    parser.add_argument("--scorm", type=Path)
    parser.add_argument("--output-scorm", type=Path)
    parser.add_argument("--voice", default="ermil")
    parser.add_argument("--emotion", default="good")
    parser.add_argument("--speed", type=float, default=0.92)
    parser.add_argument("--folder-id", default=os.getenv("YANDEX_FOLDER_ID", ""))
    parser.add_argument("--only", help="Например: 1,3,7-10")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def parse_filter(value: str | None) -> set[int] | None:
    if not value:
        return None
    result: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            result.update(range(int(a), int(b) + 1))
        elif part:
            result.add(int(part))
    return result


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-zА-Яа-яЁё0-9]+(?:[-–][A-Za-zА-Яа-яЁё0-9]+)?", text))


def sentence_list(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def estimate_duration(text: str, speed: float) -> float:
    words = word_count(text)
    speech = words / (WORDS_PER_MINUTE * speed) * 60
    sentences = sentence_list(text)
    pause_seconds = max(0, len(sentences) - 1) * 0.35 + 1.3
    return round(speech + pause_seconds, 1)


def xml_escape(text: str) -> str:
    return html.escape(text, quote=False)


def choose_emphasis(sentences: list[str], mode: str) -> int | None:
    if not sentences or mode == "check":
        return None
    for i, sentence in enumerate(sentences):
        if "Запомните" in sentence or "главное правило" in sentence.lower():
            return i
    if mode in {"focus", "warning", "summary"}:
        return min(1, len(sentences) - 1)
    return None


def pause_after(sentence: str, index: int, total: int, mode: str) -> int:
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


def make_ssml(text: str, mode: str, rate_percent: int = 92) -> str:
    sentences = sentence_list(text)
    emphasis_idx = choose_emphasis(sentences, mode)
    body: list[str] = []
    for i, sentence in enumerate(sentences):
        safe = xml_escape(sentence)
        if emphasis_idx == i:
            safe = f'<emphasis level="strong">{safe}</emphasis>'
        body.append(safe)
        pause = pause_after(sentence, i, len(sentences), mode)
        if pause:
            body.append(f'<break time="{pause}ms"/>')
    joined = "\n    ".join(body)
    return (
        "<speak>\n"
        f'  <prosody rate="{rate_percent}%">\n'
        f"    {joined}\n"
        "  </prosody>\n"
        "</speak>\n"
    )


def qa_slide(slide: dict[str, Any], ssml: str, speed: float) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    text = slide["text"]
    number = slide["number"]

    try:
        ET.fromstring(ssml)
    except ET.ParseError as exc:
        errors.append(f"Некорректный XML/SSML: {exc}")

    if not ssml.strip().startswith("<speak>") or not ssml.strip().endswith("</speak>"):
        errors.append("SSML должен начинаться с <speak> и заканчиваться </speak>.")

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"Необработанная техническая запись: {pattern}")

    sentences = sentence_list(text)
    long_sentences = [s for s in sentences if word_count(s) > 16]
    if long_sentences:
        warnings.append(f"Предложений длиннее 16 слов: {len(long_sentences)}")

    emphasis_count = ssml.count("<emphasis")
    if emphasis_count > 1:
        errors.append("На слайде больше одного акцента.")
    if slide["mode"] == "check" and emphasis_count:
        errors.append("В тесте нельзя выделять ответ интонационным акцентом.")

    if re.search(r'<break time="(?:800|900|1100)ms"/>\s*<break', ssml):
        errors.append("Две длинные паузы подряд.")

    duration = estimate_duration(text, speed)
    if not MIN_DURATION <= duration <= MAX_DURATION:
        warnings.append(
            f"Оценка длительности {duration} сек.; целевой диапазон {MIN_DURATION}–{MAX_DURATION}."
        )

    if slide["mode"] not in MODES:
        errors.append(f"Неизвестный режим речи: {slide['mode']}")
    if slide["type"] not in SLIDE_TYPES:
        errors.append(f"Неизвестный тип слайда: {slide['type']}")

    return {
        "slide": number,
        "status": "ok" if not errors else "needs_fix",
        "duration_estimate_sec": duration,
        "word_count": word_count(text),
        "errors": errors,
        "warnings": warnings,
        "pronunciation_review": [
            term for term in PRONUNCIATION_TERMS if term.lower() in text.lower()
        ],
    }


def load_source(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) != 21:
        raise ValueError("Ожидается список из 21 слайда.")
    expected = list(range(1, 22))
    actual = [int(item["number"]) for item in data]
    if actual != expected:
        raise ValueError(f"Нумерация должна быть 1–21, получено: {actual}")
    return data


def write_assets(slides: list[dict[str, Any]], voice_dir: Path, speed: float) -> list[dict[str, Any]]:
    voice_dir.mkdir(parents=True, exist_ok=True)
    (voice_dir / "audio").mkdir(exist_ok=True)
    results: list[dict[str, Any]] = []

    for slide in slides:
        n = int(slide["number"])
        key = f"slide{n:02d}"
        ssml = make_ssml(slide["text"], slide["mode"])
        qa = qa_slide(slide, ssml, speed)
        results.append(qa)

        (voice_dir / f"{key}.txt").write_text(slide["text"].strip() + "\n", encoding="utf-8")
        (voice_dir / f"{key}.ssml").write_text(ssml, encoding="utf-8")

        md = f"""# Slide {n:02d} — {slide['title']}

## Type
{slide['type']}

## Emotion mode
{slide['mode']}

## Goal
{slide['goal']}

## Plain text
{slide['text']}

## SSML
```xml
{ssml.strip()}
```

## Estimated duration
{qa['duration_estimate_sec']} sec

## QA
{qa['status']}

### Warnings
{chr(10).join('- ' + x for x in qa['warnings']) if qa['warnings'] else '- none'}

### Errors
{chr(10).join('- ' + x for x in qa['errors']) if qa['errors'] else '- none'}
"""
        (voice_dir / f"{key}.md").write_text(md, encoding="utf-8")

    qa_lines = ["# Voice QA — lesson-1.3", ""]
    for qa in results:
        qa_lines.append(
            f"- slide{qa['slide']:02d}: {qa['status']}; "
            f"{qa['duration_estimate_sec']} sec; {qa['word_count']} words"
        )
        for warning in qa["warnings"]:
            qa_lines.append(f"  - warning: {warning}")
        for error in qa["errors"]:
            qa_lines.append(f"  - error: {error}")
        if qa["pronunciation_review"]:
            qa_lines.append(
                "  - listen carefully: " + ", ".join(qa["pronunciation_review"])
            )
    qa_lines.extend([
        "",
        "## Final listening",
        "- naturalness: pending",
        "- pronunciation: pending",
        "- pauses: pending",
        "- test neutrality: pending",
        "- publication: pending",
    ])
    (voice_dir / "voice_qa.md").write_text("\n".join(qa_lines) + "\n", encoding="utf-8")

    manifest_lines = [
        "lesson: '1.3'",
        "voice_provider: yandex_speechkit_v1",
        "voice_profile:",
        "  role: technical_mentor",
        "  voice: ermil",
        "  emotion: good",
        f"  speed: {speed}",
        "slides:",
    ]
    for slide, qa in zip(slides, results):
        n = slide["number"]
        manifest_lines.extend([
            f"  - slide: {n:02d}",
            f"    type: {slide['type']}",
            f"    mode: {slide['mode']}",
            f"    text: slide{n:02d}.txt",
            f"    ssml: slide{n:02d}.ssml",
            f"    audio: audio/slide{n:02d}.mp3",
            f"    estimated_duration_sec: {qa['duration_estimate_sec']}",
            f"    qa: {qa['status']}",
        ])
    (voice_dir / "audio_manifest.yml").write_text(
        "\n".join(manifest_lines) + "\n", encoding="utf-8"
    )
    return results


def auth_headers() -> dict[str, str]:
    api_key = os.getenv("YANDEX_API_KEY", "").strip()
    iam_token = os.getenv("YANDEX_IAM_TOKEN", "").strip()
    if api_key:
        return {"Authorization": f"Api-Key {api_key}"}
    if iam_token:
        return {"Authorization": f"Bearer {iam_token}"}
    raise RuntimeError("Установите YANDEX_API_KEY или YANDEX_IAM_TOKEN.")


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
        TTS_URL, headers=headers, data=data, timeout=(20, 180)
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"SpeechKit HTTP {response.status_code}: {response.text[:1000]}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.content)
    if destination.stat().st_size < 500:
        raise RuntimeError(f"Подозрительно маленький файл: {destination}")


def add_audio_to_scorm(scorm: Path, voice_dir: Path, output: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="jemix_scorm_") as temp:
        work = Path(temp) / "package"
        work.mkdir()
        with zipfile.ZipFile(scorm, "r") as archive:
            archive.extractall(work)
        audio_dir = work / "audio"
        audio_dir.mkdir(exist_ok=True)
        for mp3 in sorted((voice_dir / "audio").glob("slide*.mp3")):
            shutil.copy2(mp3, audio_dir / mp3.name)
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(work.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(work).as_posix())


def main() -> int:
    args = parse_args()
    slides = load_source(args.source)
    selected = parse_filter(args.only)
    results = write_assets(slides, args.voice_dir, args.speed)

    bad = [r for r in results if r["status"] != "ok"]
    if bad:
        print("Есть критические ошибки QA. Синтез остановлен.", file=sys.stderr)
        return 2

    print(f"Сценарии подготовлены: {args.voice_dir.resolve()}")
    for qa in results:
        print(
            f"slide{qa['slide']:02d}: {qa['duration_estimate_sec']:>4} сек., "
            f"{qa['word_count']:>3} слов, {qa['status']}"
        )

    if args.prepare_only:
        return 0

    headers = auth_headers()
    for slide in slides:
        n = int(slide["number"])
        if selected is not None and n not in selected:
            continue
        key = f"slide{n:02d}"
        destination = args.voice_dir / "audio" / f"{key}.mp3"
        if destination.exists() and destination.stat().st_size > 500 and not args.overwrite:
            print(f"[SKIP] {destination.name}")
            continue
        ssml = (args.voice_dir / f"{key}.ssml").read_text(encoding="utf-8")
        print(f"[{n:02d}/21] Генерация {destination.name}")
        synthesize_ssml(
            ssml,
            destination,
            voice=args.voice,
            emotion=args.emotion,
            speed=args.speed,
            folder_id=args.folder_id,
            headers=headers,
        )
        time.sleep(0.3)

    if args.scorm:
        output = args.output_scorm or args.scorm.with_name(
            args.scorm.stem + "_WITH_YANDEX_VOICE_STANDARD.zip"
        )
        add_audio_to_scorm(args.scorm, args.voice_dir, output)
        print(f"SCORM собран: {output.resolve()}")

    print("MP3 созданы. Теперь обязательно выполните финальное прослушивание и обновите voice_qa.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
