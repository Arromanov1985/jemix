#!/usr/bin/env python3
"""Validate the combined JEMIX Academy Module 3 SCORM 1.2 package."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "dist" / "module-03" / "JEMIX_Module_03_SCORM.zip"
LESSONS = ["3.1", "3.2", "3.3", "3.4"]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not PACKAGE.is_file():
        fail(f"missing package: {PACKAGE.relative_to(ROOT)}")

    try:
        with zipfile.ZipFile(PACKAGE) as archive:
            bad = archive.testzip()
            if bad:
                fail(f"corrupt ZIP member: {bad}")
            names = set(archive.namelist())
            required = {"imsmanifest.xml"}
            required.update(f"lesson-{lesson}/index.html" for lesson in LESSONS)
            missing = sorted(required - names)
            if missing:
                fail("package is missing: " + ", ".join(missing))

            try:
                root = ElementTree.fromstring(archive.read("imsmanifest.xml"))
            except ElementTree.ParseError as exc:
                fail(f"invalid imsmanifest.xml: {exc}")

            ns = {"imscp": "http://www.imsproject.org/xsd/imscp_rootv1p1p2"}
            resources = root.findall(".//imscp:resource", ns)
            if len(resources) != len(LESSONS):
                fail(f"expected {len(LESSONS)} SCO resources, found {len(resources)}")

            hrefs = {resource.get("href") for resource in resources if resource.get("href")}
            expected_hrefs = {f"lesson-{lesson}/index.html" for lesson in LESSONS}
            if hrefs != expected_hrefs:
                fail("manifest launch files do not match lessons 3.1-3.4")
    except zipfile.BadZipFile as exc:
        fail(f"invalid ZIP archive: {exc}")

    print(f"OK: {PACKAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
