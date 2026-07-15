#!/usr/bin/env python3
"""Replace slide01.mp3 ... slide20.mp3 in an approved lesson 1.1 SCORM ZIP.

The script preserves every HTML/CSS/JS/image/test file from the template and only
replaces audio/slideXX.mp3. It then validates that the result contains 20 slide
HTML files and 20 non-empty MP3 files.
"""
from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO = ROOT / "voice" / "modules" / "module-01" / "lesson-1.1" / "audio"
DEFAULT_TEMPLATE = ROOT / "templates" / "JEMIX_Lesson_1_1_SCORM_