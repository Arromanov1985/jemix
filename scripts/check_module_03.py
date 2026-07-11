#!/usr/bin/env python3
"""Build and validate the confirmed JEMIX Academy Module 3 SCORM packages."""
from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DIST = ROOT / "dist" / "module-03"
AUDIO_ROOT = ROOT / "voice" / "modules" / "module-03"

LESSONS = ["3_1", "3_2", "3_3", "3_4"]
BUILDERS = [SCRIPTS / f"build_scorm_lesson_{lesson}.py" for lesson in LESSONS