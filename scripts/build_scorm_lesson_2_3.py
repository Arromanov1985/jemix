#!/usr/bin/env python3
"""Build SCORM 1.2 package for JEMIX lesson 2.3: Расход дома."""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path('.')
WORK = ROOT / '_scorm_lesson_2_3'
DIST = ROOT / 'dist' / 'module-02'
OUT = DIST / 'JEMIX_Lesson_2_3_SCORM.zip'
LOGO_SRC = ROOT / 'academy-assets' / 'logo' / 'jemix-logo.png'
PUMP_SRC = ROOT / 'academy-assets' / 'pumps' / 'jemix-pump.png'
AUDIO_SRC = ROOT / 'voice' / 'modules' / 'module-02' / 'lesson-2.3' / 'audio'

SCREENS = [
    {'kind':'title','title':'Расход дома','body':'Расход отвечает на вопрос