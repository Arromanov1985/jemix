#!/usr/bin/env python3
"""Build SCORM package lesson by lesson.

Usage:
  python scripts/build_scorm_lesson.py module-01 lesson-1.1
  python scripts/build_scorm_lesson.py module-01 lesson-1.2

For now this wrapper uses the approved Lesson 1.1 player/template as the base.
Next steps: replace per-lesson titles, goals, quiz questions and product images.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


MODULE = sys.argv[1] if len(sys.argv) > 1 else "module-01"
LESSON = sys.argv[2] if len(sys.argv) > 2 else "lesson-1.1"

if MODULE != "module-01":
    raise SystemExit("Пока готовим модуль 1. Используй: module-01")

if LESSON != "lesson-1.1":
    print(f"Сборка по урокам включена. Следующий шаблон будет адаптирован под {LESSON}.")
    print("Сейчас соберу базовый проверенный шаблон 1.1, чтобы не ломать рабочую версию.")

runpy.run_path(str(Path(__file__).with_name("build_scorm_lesson_1_1.py")), run_name="__main__")
