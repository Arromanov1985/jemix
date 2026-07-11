#!/usr/bin/env python3
"""Validate source assets and the built SCORM package for JEMIX lesson 1.1."""

from pathlib import Path
import sys
import zipfile
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "dist" / "module-01" / "JEMIX_Lesson_1_1_SCORM_FINAL.zip"
LOGO = ROOT / "academy-assets" / "logo" / "jemix-logo.png"
PUMP = ROOT / "academy-assets" / "pumps" / "jemix-pump.png"
AUDIO_DIR = ROOT / "voice" / "modules" / "module-01" / "lesson-1.1" / "audio"

REQUIRED_PACKAGE_FILES = {
    "imsmanifest.xml",
    "index.html",
    "style.css",
    "app.js",
    "scorm.js",
    "img/jemix-logo.png",
    "img/jemix-pump.png",
    *(f"audio/slide{i:02d}.mp3" for i in range(1, 9)),
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_sources() -> None:
    missing = [path for path in (LOGO, PUMP) if not path.is_file()]
    missing.extend(
        AUDIO_DIR / f"slide{i:02d}.mp3"
        for i in range(1, 9)
        if not (AUDIO_DIR / f"slide{i:02d}.mp3").is_file()
    )
    if missing:
        fail("missing source assets: " + ", ".join(str(p.relative_to(ROOT)) for p in missing))


def validate_package() -> None:
    if not PACKAGE.is_file():
        fail(f"package not found: {PACKAGE.relative_to(ROOT)}")

    try:
        with zipfile.ZipFile(PACKAGE) as archive:
            bad_member = archive.testzip()
            if bad_member:
                fail(f"corrupt ZIP member: {bad_member}")

            names = set(archive.namelist())
            missing = sorted(REQUIRED_PACKAGE_FILES - names)
            if missing:
                fail("package is missing: " + ", ".join(missing))

            manifest_bytes = archive.read("imsmanifest.xml")
            try:
                ElementTree.fromstring(manifest_bytes)
            except ElementTree.ParseError as exc:
                fail(f"invalid imsmanifest.xml: {exc}")
    except zipfile.BadZipFile as exc:
        fail(f"invalid ZIP archive: {exc}")


def main() -> None:
    validate_sources()
    validate_package()
    print(f"OK: {PACKAGE.relative_to(ROOT)} contains all required lesson 1.1 assets")


if __name__ == "__main__":
    main()
