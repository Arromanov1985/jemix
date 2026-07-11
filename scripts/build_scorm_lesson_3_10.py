#!/usr/bin/env python3
"""Build JEMIX Academy lesson 3.10 as a standalone SCORM 1.2 package."""
from __future__ import annotations
import json, shutil, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'_scorm_lesson_3_10'; DIST=ROOT/'dist'/'module-03'; OUT=DIST/'JEMIX_Lesson_3_10_SCORM.zip'
AUDIO=ROOT/'voice'/'modules'/'module-03'/'lesson-3.10'/'audio'
SLIDES=[
('Циркуляционные насосы','Как подобрать насос для отопительного контура по расходу, нап