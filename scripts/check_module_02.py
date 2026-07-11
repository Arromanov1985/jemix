#!/usr/bin/env python3
"""Build and validate JEMIX Academy Module 2 in one command.

This command is intended for local use and CI. It:
1. checks Python syntax for all Module 2 builders, validators, and report tools;
2. builds all six standalone lesson packages and the combined SCORM package;
3. validates every standalone lesson ZIP;
4. validates the combined ZIP and manifest;
5. writes a reproducible release report with checksums and audio coverage.
"""
from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DIST = ROOT / "dist" / "module-02"
REPORT = DIST / "module-02-release-report.json"

LESSON_BUILDERS = [SCRIPTS / f"build_scorm_lesson_2_{i}.py" for i in range(1, 7)]
MODULE_BUILDER = SCRIPTS / "build_scorm_module_02.py"
LESSON_VALIDATOR = SCRIPTS / "validate_scorm_lessons_module_02.py"
MODULE_VALIDATOR = SCRIPTS / "validate_scorm_module_02.py"
REPORT_WRITER = SCRIPTS / "write_module_02_release_report.py"
REQUIRED_SCRIPTS = [
    *LESSON_BUILDERS,
    MODULE_BUILDER,
    LESSON_VALIDATOR,
    MODULE_VALIDATOR,
    REPORT_WRITER,
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


def check_report() -> None:
    if not REPORT.is_file():
        fail(f"release report was not created: {REPORT.relative_to(ROOT)}")
    if REPORT.stat().st_size == 0:
        fail(f"release report is empty: {REPORT.relative_to(ROOT)}")
    print(f"OK: release report created: {REPORT.relative_to(ROOT)}")


def main() -> None:
    check_sources()
    check_syntax()
    run_script(MODULE_BUILDER)
    run_script(LESSON_VALIDATOR)
    run_script(MODULE_VALIDATOR)
    run_script(REPORT_WRITER)
    check_report()
    print(
        "READY: all Module 2 standalone lessons, the combined SCORM package, "
        "and the release report are valid"
    )


if __name__ == "__main__":
    main()
