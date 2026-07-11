#!/usr/bin/env python3
"""Build Module 2 as one SCORM 1.2 package from lessons 2.1-2.6.

The script runs each lesson builder, extracts the resulting lesson package into
its own directory, writes a multi-SCO manifest, and creates:
  dist/module-02/JEMIX_Module_02_SCORM.zip

Audio is optional at build time. When slide01.mp3-slide12.mp3 are present in
voice/modules/module-02/lesson-2.x/audio, the lesson builders include them.
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

LESS