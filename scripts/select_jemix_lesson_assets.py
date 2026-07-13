#!/usr/bin/env python3
"""Select downloaded TerraWater images for JEMIX Academy lessons.

Usage:
  python scripts/select_jemix_lesson_assets.py \
      --catalog-dir academy-assets/catalog-3 \
      --module-dir academy-assets/module-01

The selector reads manifest.json created by fetch_terrawater_images.py,
filters likely JEMIX product images, ranks them by size and relevance,
and copies deterministic assets into lesson folders.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

JEMIX_WORDS = ('jemix', 'джемикс')
PUMP_WORDS = ('насос', 'pump', 'jsw', 'sg', 'stp', 'wp', 'cp', 'qb', 'jgp')
NEGATIVE_WORDS = ('logo', 'логотип', 'banner', 'баннер', 'icon', 'икон', 'scheme', 'схем')

LESSON_TARGETS = {
    'lesson-1.1': {
        'pump-main': ('jemix', 'насос'),
        'cover': ('jemix', 'насос'),
    },
    'lesson-1.2': {
        'pump-main': ('jemix', 'насос'),
        'characteristics': ('jemix', 'насос'),
    },
    'lesson-1.3': {
        'pump-main': ('jemix', 'насос'),
        'construction': ('jemix', 'насос'),
    },
    'lesson-1.4': {
        'surface-pump': ('jemix', 'поверхност'),
        'submersible-pump': ('jemix', 'погруж'),
    },
}


def text_for(item: dict) -> str:
    return ' '.join(str(item.get(k, '')) for k in ('file', 'alt', 'page', 'source')).lower()


def score(item: dict, keywords: tuple[str, ...]) -> int:
    text = text_for(item)
    value = 0
    if any(w in text for w in JEMIX_WORDS):
        value += 100
    if any(w in text for w in PUMP_WORDS):
        value += 35
    for word in keywords:
        if word.lower() in text:
            value += 30
    if any(w in text for w in NEGATIVE_WORDS):
        value -= 100
    width = int(item.get('width') or 0)
    height = int(item.get('height') or 0)
    if width >= 1200 or height >= 1200:
        value += 30
    elif width >= 800 or height >= 800:
        value += 20
    elif width >= 500 or height >= 500:
        value += 10
    if width and height:
        ratio = max(width, height) / max(1, min(width, height))
        if ratio <= 2.2:
            value += 10
    return value


def safe_ext(path: Path) -> str:
    ext = path.suffix.lower()
    return ext if ext in {'.png', '.jpg', '.jpeg', '.webp'} else '.jpg'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--catalog-dir', default='academy-assets/catalog-3')
    parser.add_argument('--module-dir', default='academy-assets/module-01')
    args = parser.parse_args()

    catalog_dir = Path(args.catalog_dir)
    module_dir = Path(args.module_dir)
    manifest_path = catalog_dir / 'manifest.json'
    if not manifest_path.exists():
        raise SystemExit(f'Missing manifest: {manifest_path}')

    items = json.loads(manifest_path.read_text(encoding='utf-8'))
    valid = [x for x in items if (catalog_dir / x.get('file', '')).exists()]
    if not valid:
        raise SystemExit('No downloaded images found in manifest')

    selected_report = []
    used_files: set[str] = set()

    for lesson, targets in LESSON_TARGETS.items():
        lesson_dir = module_dir / lesson
        lesson_dir.mkdir(parents=True, exist_ok=True)
        for target, keywords in targets.items():
            ranked = sorted(valid, key=lambda x: score(x, keywords), reverse=True)
            chosen = next((x for x in ranked if x['file'] not in used_files and score(x, keywords) > 0), None)
            if chosen is None:
                chosen = ranked[0]
            src = catalog_dir / chosen['file']
            dst = lesson_dir / f'{target}{safe_ext(src)}'
            shutil.copy2(src, dst)
            used_files.add(chosen['file'])
            selected_report.append({
                'lesson': lesson,
                'target': target,
                'file': dst.as_posix(),
                'source_file': chosen['file'],
                'source_url': chosen.get('source'),
                'score': score(chosen, keywords),
                'width': chosen.get('width'),
                'height': chosen.get('height'),
            })
            print(f'{lesson}: {target} <- {chosen["file"]}')

    report_path = module_dir / 'selected-assets.json'
    report_path.write_text(json.dumps(selected_report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'OK: {len(selected_report)} assets selected -> {module_dir}')


if __name__ == '__main__':
    main()
