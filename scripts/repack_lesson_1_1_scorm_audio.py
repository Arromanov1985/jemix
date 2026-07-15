#!/usr/bin/env python3
"""Replace slide01.mp3 ... slide20.mp3 in the approved lesson 1.1 SCORM template."""
from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO = ROOT / "voice" / "modules" / "module-01" / "lesson-1.1" / "audio"
DEFAULT_OUTPUT = ROOT / "dist