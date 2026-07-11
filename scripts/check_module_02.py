#!/usr/bin/env python3
"""Build and validate JEMIX Academy Module 2 in one command.

This command is intended for local use and CI. It:
1. checks Python syntax for all Module 2 builders and validators;
2. builds the combined six-lesson SCORM package;
3. validates the resulting ZIP and manifest;
4. reports optional audio coverage without failing when MP3 files are absent.
"""
from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
AUDIO_ROOT = ROOT / "voice" / "modules" / "module-02"

REQUIRED_SCRIPTS = [
    *(SCRIPTS / f"build_scorm_lesson_2_{i}.py" for i in range(1, 7)),
    SCRIPTS / "build_scorm_module_02.py",
    SCRIPTS / "validate_scorm_module_02.py",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_sources() -> None:
    missing = [path for path in REQUIRED_SCRIPTS if not path.is_file()]
    if missing:
        fail("missing scripts: " + ", ".join(str(p.relative_to(ROOT)) for p in missing))


def check_syntax() -> None:
    for path in REQUIRED_SCRIPTS:
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            fail(f"syntax error in {path.relative_to(ROOT)}: {exc.msg}")
    print(f"OK: syntax checked for {len(REQUIRED_SCRIPTS)} Module 2 scripts")


def run_script(path: Path) -> None:
    print(f"RUN: {path.relative_to(ROOT)}")
    completed = subprocess.run([sys.executable, str(path)], cwd=ROOT)
    if completed.returncode != 0:
        fail(f"command failed with exit code {completed.returncode}: {path.relative_to(ROOT)}")


def audio_report() -> None:
    total = 0
    present = 0
    for lesson in range(1, 7):
        lesson_dir = AUDIO_ROOT / f"lesson-2.{lesson}" / "audio"
        lesson_present = 0
        for slide in range(1, 13):
            total += 1
            if (lesson_dir / f"slide{slide:02d}.mp3").is_file():
                present += 1
                lesson_present += 1
        print(f"AUDIO: lesson 2.{lesson}: {lesson_present}/12 MP3")
    print(f"AUDIO TOTAL: {present}/{total} MP3 ({round(present / total * 100) if total else 0}%)")
    if present < total:
        print("INFO: audio is optional for the technical build and can be added later without changing lesson structure")


def main() -> None:
    check_sources()
    check_syntax()
    run_script(SCRIPTS / "build_scorm_module_02.py")
    run_script(SCRIPTS / "validate_scorm_module_02.py")
    audio_report()
    print("READY: Module 2 technical SCORM package built and validated")


if __name__ == "__main__":
    main()
