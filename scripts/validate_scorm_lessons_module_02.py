#!/usr/bin/env python3
"""Validate all six standalone SCORM lesson packages for JEMIX Module 2."""
from __future__ import annotations

from pathlib import Path
import sys
import zipfile
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "module-02"
LESSONS = [f"2_{i}" for i in range(1, 7)]
REQUIRED_FILES = {"imsmanifest.xml", "index.html", "style.css", "app.js", "scorm.js"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_manifest(data: bytes, package_names: set[str], lesson_id: str) -> None:
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as exc:
        fail(f"lesson {lesson_id}: invalid imsmanifest.xml: {exc}")

    ns = {"imscp": "http://www.imsproject.org/xsd/imscp_rootv1p1p2"}
    resources = root.findall(".//imscp:resource", ns)
    if not resources:
        fail(f"lesson {lesson_id}: manifest has no resource")

    launch_files = [resource.get("href") for resource in resources if resource.get("href")]
    if "index.html" not in launch_files:
        fail(f"lesson {lesson_id}: manifest does not launch index.html")

    declared = {
        node.get("href")
        for node in root.findall(".//imscp:file", ns)
        if node.get("href")
    }
    missing_declared = sorted(declared - package_names)
    if missing_declared:
        fail(
            f"lesson {lesson_id}: manifest references missing files: "
            + ", ".join(missing_declared)
        )


def validate_lesson(lesson_id: str) -> None:
    package = DIST / f"JEMIX_Lesson_{lesson_id}_SCORM.zip"
    if not package.is_file():
        fail(f"missing lesson package: {package.relative_to(ROOT)}")

    try:
        with zipfile.ZipFile(package) as archive:
            bad = archive.testzip()
            if bad:
                fail(f"lesson {lesson_id}: corrupt ZIP member: {bad}")

            names = set(archive.namelist())
            missing = sorted(REQUIRED_FILES - names)
            if missing:
                fail(f"lesson {lesson_id}: package is missing: " + ", ".join(missing))

            validate_manifest(archive.read("imsmanifest.xml"), names, lesson_id)
    except zipfile.BadZipFile as exc:
        fail(f"lesson {lesson_id}: invalid ZIP archive: {exc}")

    print(f"OK: {package.relative_to(ROOT)}")


def main() -> None:
    for lesson_id in LESSONS:
        validate_lesson(lesson_id)
    print("OK: all six Module 2 lesson packages are valid")


if __name__ == "__main__":
    main()
