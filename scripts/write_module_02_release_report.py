#!/usr/bin/env python3
"""Write a reproducible release report for JEMIX Academy Module 2 artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "module-02"
REPORT = DIST / "module-02-release-report.json"
AUDIO_ROOT = ROOT / "voice" / "modules" / "module-02"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_info(path: Path) -> dict[str, object]:
    with ZipFile(path) as archive:
        names = archive.namelist()
        bad_member = archive.testzip()
    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "zip_members": len(names),
        "zip_valid": bad_member is None,
        "bad_member": bad_member,
    }


def audio_info() -> dict[str, object]:
    lessons: dict[str, dict[str, object]] = {}
    total = 0
    present = 0
    for lesson in range(1, 7):
        lesson_id = f"2.{lesson}"
        audio_dir = AUDIO_ROOT / f"lesson-{lesson_id}" / "audio"
        files = []
        for slide in range(1, 13):
            total += 1
            name = f"slide{slide:02d}.mp3"
            path = audio_dir / name
            if path.is_file():
                present += 1
                files.append(name)
        lessons[lesson_id] = {
            "present": len(files),
            "expected": 12,
            "files": files,
        }
    return {
        "present": present,
        "expected": total,
        "percent": round((present / total) * 100) if total else 0,
        "lessons": lessons,
    }


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    expected = [
        DIST / "JEMIX_Module_02_SCORM.zip",
        *(DIST / f"JEMIX_Lesson_2_{lesson}_SCORM.zip" for lesson in range(1, 7)),
    ]
    missing = [str(path.relative_to(ROOT)) for path in expected if not path.is_file()]
    if missing:
        raise SystemExit("Missing release artifacts: " + ", ".join(missing))

    report = {
        "module": "2",
        "standard": "SCORM 1.2",
        "packages": [package_info(path) for path in expected],
        "audio": audio_info(),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
