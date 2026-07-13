#!/usr/bin/env python3
"""Validate source assets and the built SCORM package for JEMIX lesson 1.1."""

from pathlib import Path
import sys
import zipfile
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "dist" / "module-01" / "JEMIX_Lesson_1_1_SCORM_FINAL.zip"
LOGO = ROOT / "academy-assets" / "logo" / "jemix-logo.png"
PUMP = ROOT / "academy-assets" / "pumps" / "jemix-pump.png"
AUDIO_DIR = ROOT / "voice