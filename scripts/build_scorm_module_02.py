#!/usr/bin/env python3
"""Build Module 2 as one multi-SCO SCORM 1.2 package.

Runs lesson builders 2.1-2.6, extracts each lesson ZIP into its own folder,
creates a multi-SCO imsmanifest.xml, and writes:
  dist/module-02/JEMIX_Module_02_SCORM.zip

Audio remains optional at build time. Lesson builders include MP3 files when
present under voice/modules/module-02/lesson-2.x/audio/.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "module-02"
WORK = ROOT / "_scorm_module_02"
OUT = DIST / "JEMIX_Module_02_SCORM.zip"

LESSONS = [
    ("2.1", "Водоснабжение как система"),
    ("2.2", "Источник и забор воды"),
    ("2.3", "Расход дома"),
    ("2.4", "Напор и потери"),
    ("2.5", "Автоматика и защита"),
    ("2.6", "Итоговый экзамен"),
]


def builder_path(lesson_id: str) -> Path:
    return ROOT / "scripts" / f"build_scorm_lesson_{lesson_id.replace('.', '_')}.py"


def lesson_zip(lesson_id: str) -> Path:
    suffix = lesson_id.replace('.', '_')
    return DIST / f"JEMIX_Lesson_{suffix}_SCORM.zip"


def run_lesson_builders() -> None:
    for lesson_id, _ in LESSONS:
        script = builder_path(lesson_id)
        if not script.is_file():
            raise SystemExit(f"Missing lesson builder: {script.relative_to(ROOT)}")
        subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
        package = lesson_zip(lesson_id)
        if not package.is_file():
            raise SystemExit(f"Lesson builder did not create: {package.relative_to(ROOT)}")


def extract_lessons() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    for lesson_id, _ in LESSONS:
        target = WORK / f"lesson-{lesson_id}"
        target.mkdir(parents=True)
        with zipfile.ZipFile(lesson_zip(lesson_id)) as archive:
            bad = archive.testzip()
            if bad:
                raise SystemExit(f"Corrupt lesson package {lesson_id}: {bad}")
            archive.extractall(target)
        manifest = target / "imsmanifest.xml"
        if manifest.exists():
            manifest.unlink()


def write_manifest() -> None:
    items = []
    resources = []
    for index, (lesson_id, title) in enumerate(LESSONS, start=1):
        folder = f"lesson-{lesson_id}"
        resource_id = f"RES{index}"
        item_id = f"ITEM{index}"
        files = []
        for path in sorted((WORK / folder).rglob("*")):
            if path.is_file():
                rel = path.relative_to(WORK).as_posix()
                files.append(f'      <file href="{escape(rel)}"/>')
        items.append(
            f'      <item identifier="{item_id}" identifierref="{resource_id}">\n'
            f'        <title>{escape(lesson_id + " — " + title)}</title>\n'
            f'      </item>'
        )
        resources.append(
            f'    <resource identifier="{resource_id}" type="webcontent" '
            f'adlcp:scormtype="sco" href="{folder}/index.html">\n'
            + "\n".join(files)
            + "\n    </resource>"
        )

    manifest = f'''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_MODULE_02" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="ORG1">
    <organization identifier="ORG1">
      <title>JEMIX Academy — Модуль 2</title>
{chr(10).join(items)}
    </organization>
  </organizations>
  <resources>
{chr(10).join(resources)}
  </resources>
</manifest>
'''
    (WORK / "imsmanifest.xml").write_text(manifest, encoding="utf-8")


def create_zip() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(WORK.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(WORK).as_posix())


def validate_output() -> None:
    with zipfile.ZipFile(OUT) as archive:
        bad = archive.testzip()
        if bad:
            raise SystemExit(f"Corrupt module archive member: {bad}")
        names = set(archive.namelist())
        required = {"imsmanifest.xml"}
        required.update(f"lesson-{lesson_id}/index.html" for lesson_id, _ in LESSONS)
        missing = sorted(required - names)
        if missing:
            raise SystemExit("Module package is missing: " + ", ".join(missing))


def main() -> None:
    run_lesson_builders()
    extract_lessons()
    write_manifest()
    create_zip()
    validate_output()
    print(f"OK: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
