#!/usr/bin/env python3
"""Replace slide01.mp3 ... slide20.mp3 in an approved lesson 1.1 SCORM ZIP.

The script preserves every existing file from the template and replaces only the
20 narration files. It validates the resulting ZIP before reporting success.
"""
from __future__ import annotations

import argparse
import re
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO = ROOT / "voice" / "modules" / "module-01" / "lesson-1.1" / "audio"
DEFAULT_OUTPUT = ROOT / "dist" / "module-01" / "JEMIX_Lesson_1_1_SCORM_20_AUDIO_FINAL.zip"
AUDIO_RE = re.compile(r"(?:^|/)audio/slide(\d{2})\.mp3$", re.IGNORECASE)
SLIDE_RE = re.compile(r"(?:^|/)slide(\d{2})\.html$", re.IGNORECASE)


def valid_mp3(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 1024:
        return False
    header = path.read_bytes()[:3]
    return header == b"ID3" or header[:2] in {b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"}


def collect_audio(audio_dir: Path) -> dict[int, Path]:
    files: dict[int, Path] = {}
    bad: list[str] = []
    for index in range(1, 21):
        path = audio_dir / f"slide{index:02d}.mp3"
        if not valid_mp3(path):
            bad.append(str(path))
        else:
            files[index] = path
    if bad:
        raise SystemExit("Missing or invalid MP3 files:\n" + "\n".join(bad))
    return files


def inspect_template(template: Path) -> tuple[list[str], str]:
    if not template.is_file():
        raise SystemExit(f"Template ZIP not found: {template}")
    try:
        with zipfile.ZipFile(template) as archive:
            bad_member = archive.testzip()
            if bad_member:
                raise SystemExit(f"Template ZIP is corrupt: {bad_member}")
            names = archive.namelist()
    except zipfile.BadZipFile as exc:
        raise SystemExit(f"Invalid template ZIP: {exc}") from exc

    slide_numbers = {int(match.group(1)) for name in names if (match := SLIDE_RE.search(name))}
    if len(slide_numbers) < 20 or not set(range(1, 21)).issubset(slide_numbers):
        raise SystemExit(
            f"Template must contain slide01.html ... slide20.html; found {len(slide_numbers)} slide files"
        )

    existing_audio = [name for name in names if AUDIO_RE.search(name)]
    if existing_audio:
        sample = PurePosixPath(existing_audio[0])
        audio_prefix = str(sample.parent)
    else:
        manifest_candidates = [name for name in names if name.endswith("imsmanifest.xml")]
        if not manifest_candidates:
            raise SystemExit("Template does not contain imsmanifest.xml")
        manifest_parent = PurePosixPath(manifest_candidates[0]).parent
        audio_prefix = str(manifest_parent / "audio") if str(manifest_parent) != "." else "audio"

    return names, audio_prefix


def repack(template: Path, output: Path, audio_dir: Path) -> None:
    audio_files = collect_audio(audio_dir)
    _, audio_prefix = inspect_template(template)
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(prefix="jemix_scorm_", suffix=".zip", delete=False) as handle:
        temp_output = Path(handle.name)

    try:
        with zipfile.ZipFile(template, "r") as source, zipfile.ZipFile(
            temp_output, "w", compression=zipfile.ZIP_DEFLATED
        ) as target:
            for item in source.infolist():
                if AUDIO_RE.search(item.filename):
                    continue
                target.writestr(item, source.read(item.filename))

            for index, source_path in audio_files.items():
                member = f"{audio_prefix}/slide{index:02d}.mp3"
                target.write(source_path, member)

        validate_output(temp_output)
        temp_output.replace(output)
    finally:
        if temp_output.exists():
            temp_output.unlink()

    print(f"OK: {output}")
    print("Audio replaced: slide01.mp3 ... slide20.mp3")


def validate_output(output: Path) -> None:
    try:
        with zipfile.ZipFile(output) as archive:
            bad_member = archive.testzip()
            if bad_member:
                raise SystemExit(f"Output ZIP is corrupt: {bad_member}")

            names = archive.namelist()
            slide_numbers = {int(match.group(1)) for name in names if (match := SLIDE_RE.search(name))}
            audio_entries = {
                int(match.group(1)): name
                for name in names
                if (match := AUDIO_RE.search(name))
            }

            if not set(range(1, 21)).issubset(slide_numbers):
                raise SystemExit("Output ZIP does not contain all 20 slide HTML files")
            if set(audio_entries) != set(range(1, 21)):
                raise SystemExit(
                    "Output ZIP does not contain exactly slide01.mp3 ... slide20.mp3"
                )
            for index, member in audio_entries.items():
                if archive.getinfo(member).file_size < 1024:
                    raise SystemExit(f"Audio file is empty or too small: {member}")

            if not any(name.endswith("imsmanifest.xml") for name in names):
                raise SystemExit("Output ZIP does not contain imsmanifest.xml")
    except zipfile.BadZipFile as exc:
        raise SystemExit(f"Invalid output ZIP: {exc}") from exc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--audio", default=DEFAULT_AUDIO, type=Path)
    parser.add_argument("--output", default=DEFAULT_OUTPUT, type=Path)
    args = parser.parse_args()
    repack(args.template, args.output, args.audio)


if __name__ == "__main__":
    main()
