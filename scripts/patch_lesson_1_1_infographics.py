#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:
    raise SystemExit("Install Pillow first: python -m pip install pillow") from exc

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "dist" / "module-01" / "JEMIX_Academy_1_1_SCORM_20_SLIDES_LMS_READY.zip"
DEFAULT_OUTPUT = ROOT / "dist" / "module-01