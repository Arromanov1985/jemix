#!/usr/bin/env python3
"""Generate SaluteSpeech audio for all lessons in one voice module.

Examples:
  python scripts/generate_module.py module-03
  python scripts/generate_module.py voice/modules/module-03
  python scripts/generate_module.py module-03 --force
  python scripts/generate_module.py module-03 --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, Optional

from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from salute_auth import get_salute_token, ssl_verify_setting  # noqa: E402
from salute_tts import generate_lesson  # noqa: E402

ROOT_DIR = SCRIPT_DIR.parent
VOICE_DIR = ROOT_DIR / "voice" / "modules"


def natural_key(path: Path) -> list[object]:
    parts = re.split(r"(\d+)", path.name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def resolve_module_dir(module: str) -> Path:
    raw = Path(module)
    if raw.exists():
        return raw.resolve()

    name = module.strip().rstrip("/\\")
    if re.fullmatch(r"\d+", name):
        name = f"module-{int(name):02d}"
    elif re.fullmatch(r"module-\d+", name):
        number = int(name.split("-", 1)[1])
        name = f"module-{number:02d}"

    return (VOICE_DIR / name).resolve()


def iter_lesson_dirs(module_dir: Path) -> Iterable[Path]:
    return sorted(
        (
            p
            for p in module_dir.iterdir()
            if p.is_dir() and list(p.glob("slide*.ssml"))
        ),
        key=natural_key,
    )


def generate_module(module: str, *, force: bool = False, dry_run: bool = False) -> int:
    load_dotenv(override=True)

    module_dir = resolve_module_dir(module)
    if not module_dir.exists():
        print(f"Module folder not found: {module_dir}", file=sys.stderr)
        return 2

    lessons = list(iter_lesson_dirs(module_dir))
    if not lessons:
        print(f"No lesson folders with slide*.ssml found in {module_dir}", file=sys.stderr)
        return 2

    print(f"Module: {module_dir}")
    print(f"Lessons: {len(lessons)}")

    token: Optional[str] = None
    if not dry_run:
        token = get_salute_token(verify=ssl_verify_setting())
        print("Token: OK")

    failures = 0
    for index, lesson_dir in enumerate(lessons, start=1):
        print(f"\n[{index}/{len(lessons)}] {lesson_dir.name}")
        try:
            code = generate_lesson(
                lesson_dir,
                token=token,
                force=force,
                dry_run=dry_run,
                verbose=True,
            )
            if code != 0:
                failures += 1
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"ERROR: {lesson_dir}: {exc}", file=sys.stderr)

    if failures:
        print(f"\nDone with errors: {failures}")
        return 1

    print("\nDone.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("module", help="Module name/path, for example module-03 or voice/modules/module-03")
    parser.add_argument("--force", action="store_true", help="Regenerate existing mp3 files")
    parser.add_argument("--dry-run", action="store_true", help="Show files without API calls")
    args = parser.parse_args()

    return generate_module(args.module, force=args.force, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
