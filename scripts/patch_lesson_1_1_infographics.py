#!/usr/bin/env python3
from pathlib import Path
import tempfile, zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'dist/module-01/JEMIX_Academy_1_1_SCORM_UX_v2_FINAL_WITH_JEMIX_PUMPS.zip'
ATLAS = ROOT / 'dist/module-01/JEMIX_Academy_1_1_INFOGRAPHICS_ATLAS.png'
OUT = ROOT / 'dist/module-01/JEMIX_Academy_1_1_SCORM_INFOGRAPHICS_FINAL.zip'
INTERACTIVE = {6, 9, 16, 18, 19}


def split_atlas(atlas_path, out_dir):
    im = Image.open(atlas_path).convert('RGB')
    w, h = im.size
    for n in range(20):
        row, col = divmod(n, 5)
        x0, x1 = round(col * w / 5), round((col + 1) * w / 5)