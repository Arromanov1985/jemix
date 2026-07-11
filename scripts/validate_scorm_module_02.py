#!/usr/bin/env python3
"""Validate the combined JEMIX Module 2 SCORM 1.2 package."""
from __future__ import annotations

from pathlib import Path
import sys
import zipfile
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "dist" / "module-02" / "JEMIX_Module_02_SCORM.zip"
LESSONS = [f"lesson-2.{i}" for i in range(1, 7)]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_manifest(data: bytes, names: set[str]) -> None:
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as exc:
        fail(f"invalid imsmanifest.xml: {exc}")

    ns = {"imscp": "http://www.imsproject.org/xsd/imscp_rootv1p1p2"}
    resources = root.findall(".//imscp:resource", ns)
    if len(resources) != 6:
        fail(f"expected 6 SCO resources, found {len(resources)}")

    hrefs = [r.get("href") for r in resources if r.get("href")]
    expected_hrefs = {f"{lesson}/index.html" for lesson in LESSONS}
    if set(hrefs) != expected_hrefs:
        fail("unexpected launch files: " + ", ".join(sorted(set(hrefs))))

    items = root.findall(".//imscp:item", ns)
    if len(items) < 6:
        fail(f"expected at least 6 organization items, found {len(items)}")

    declared = {
        node.get("href")
        for node in root.findall(".//imscp:file", ns)
        if node.get("href")
    }
    missing_declared = sorted(declared - names)
    if missing_declared:
        fail("manifest references missing files: " + ", ".join(missing_declared))


def validate_package() -> None:
    if not PACKAGE.is_file():
        fail(f"package not found: {PACKAGE.relative_to(ROOT)}")

    try:
        with zipfile.ZipFile(PACKAGE) as archive:
            bad = archive.testzip()
            if bad:
                fail(f"corrupt ZIP member: {bad}")

            names = set(archive.namelist())
            required = {"imsmanifest.xml"}
            for lesson in LESSONS:
                required.update({
                    f"{lesson}/index.html",
                    f"{lesson}/style.css",
                    f"{lesson}/app.js",
                    f"{lesson}/scorm.js",
                })
            missing = sorted(required - names)
            if missing:
                fail("package is missing: " + ", ".join(missing))

            validate_manifest(archive.read("imsmanifest.xml"), names)
    except zipfile.BadZipFile as exc:
        fail(f"invalid ZIP archive: {exc}")


def main() -> None:
    validate_package()
    print(f"OK: {PACKAGE.relative_to(ROOT)} is a valid six-lesson Module 2 SCORM package")


if __name__ == "__main__":
    main()
