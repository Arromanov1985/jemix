#!/usr/bin/env python3
"""Audit source readiness for JEMIX Academy Module 3 without inventing content.

The audit looks for six lesson source files and optional audio slots. It is safe to
run before Module 3 content is uploaded and gives an exact blocker list.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MODULE_ROOT = ROOT / "academy" / "module-03"
VOICE_ROOT = ROOT / "voice" / "modules" / "module-03"
LESSONS = [f"3_{i}" for i in range(1, 7)]


def lesson_source(lesson: str) -> Path:
    return MODULE_ROOT / lesson / "lesson.yml"


def audio_dir(lesson: str) -> Path:
    dotted = lesson.replace("_", ".")
    return VOICE_ROOT / f"lesson-{dotted}" / "audio"


def main() -> None:
    missing_sources: list[Path] = []
    total_audio = 0
    present_audio = 0

    print("MODULE 3 SOURCE AUDIT")
    for lesson in LESSONS:
        source = lesson_source(lesson)
        source_ok = source.is_file()
        if not source_ok:
            missing_sources.append(source)

        lesson_audio = 0
        directory = audio_dir(lesson)
        for slide in range(1, 13):
            total_audio += 1
            if (directory / f"slide{slide:02d}.mp3").is_file():
                present_audio += 1
                lesson_audio += 1

        print(
            f"{lesson.replace('_', '.')}: "
            f"lesson.yml={'OK' if source_ok else 'MISSING'}, "
            f"audio={lesson_audio}/12"
        )

    percent = round(present_audio / total_audio * 100) if total_audio else 0
    print(f"AUDIO TOTAL: {present_audio}/{total_audio} ({percent}%)")

    if missing_sources:
        print("BLOCKER: Module 3 lesson sources are missing:", file=sys.stderr)
        for path in missing_sources:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        raise SystemExit(2)

    print("READY: all six Module 3 lesson.yml files are present")


if __name__ == "__main__":
    main()
