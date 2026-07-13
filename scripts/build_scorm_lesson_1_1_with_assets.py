#!/usr/bin/env python3
"""Prepare selected TerraWater imagery and build JEMIX lesson 1.1.

Usage:
  python scripts/build_scorm_lesson_1_1_with_assets.py

The script prefers images selected into:
  academy-assets/module-01/lesson-1.1/pump-main.*
  academy-assets/module-01/lesson-1.1/cover.*

It copies the best available product image to the canonical location expected
by the approved SCORM builder, then runs build_scorm_lesson_1_1_final.py.
"""
from __future__ import annotations

import runpy
import shutil
from pathlib import Path

ROOT = Path('.')
LESSON_ASSETS = ROOT / 'academy-assets' / 'module-01' / 'lesson-1.1'
CANONICAL_DIR = ROOT / 'academy-assets' / 'pumps'
CANONICAL_PUMP = CANONICAL_DIR / 'jemix-pump.png'
SUPPORTED = ('.png', '.webp', '.jpg', '.jpeg')


def find_asset(stem: str) -> Path | None:
    for ext in SUPPORTED:
        candidate = LESSON_ASSETS / f'{stem}{ext}'
        if candidate.exists():
            return candidate
    return None


def choose_source() -> Path:
    for stem in ('pump-main', 'cover'):
        source = find_asset(stem)
        if source:
            return source
    if CANONICAL_PUMP.exists():
        return CANONICAL_PUMP
    raise SystemExit(
        'No lesson 1.1 product image found. Run:\n'
        '  python scripts/fetch_terrawater_images.py --url https://www.terrawater.ru/catalog/3 --output academy-assets/catalog-3\n'
        '  python scripts/select_jemix_lesson_assets.py --catalog-dir academy-assets/catalog-3 --module-dir academy-assets/module-01'
    )


def prepare_canonical_image(source: Path) -> None:
    CANONICAL_DIR.mkdir(parents=True, exist_ok=True)
    if source.resolve() == CANONICAL_PUMP.resolve():
        print(f'IMAGE: using existing {source}')
        return
    shutil.copy2(source, CANONICAL_PUMP)
    print(f'IMAGE: {source} -> {CANONICAL_PUMP}')


def main() -> None:
    source = choose_source()
    prepare_canonical_image(source)
    runpy.run_path(
        str(ROOT / 'scripts' / 'build_scorm_lesson_1_1_final.py'),
        run_name='__main__',
    )


if __name__ == '__main__':
    main()
