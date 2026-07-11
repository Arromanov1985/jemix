#!/usr/bin/env python3
"""Build SCORM 1.2 package for JEMIX lesson 2.6 final exam.

Output:
  dist/module-02/JEMIX_Lesson_2_6_SCORM.zip
"""
from __future__ import annotations
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path('.')
WORK = ROOT / '_scorm_lesson_2_6'
DIST = ROOT / 'dist' / 'module-02'
OUT = DIST / 'JEMIX_Lesson_2_6_SCORM.zip'
LOGO_SRC = ROOT / 'academy-assets' / 'logo' / 'jemix-logo