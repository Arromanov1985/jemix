#!/usr/bin/env python3
"""Compatibility wrapper for the current JEMIX Academy SCORM builder.

The old test-only builder produced JEMIX_Module_01_SCORM_TEST.zip.
The current production builder is scripts/build_scorm_module.py and produces
JEMIX_Module_01_SCORM.zip.

Usage:
  python scripts/build_scorm.py module-01
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


if __name__ == "__main__":
    target = Path(__file__).with_name("build_scorm_module.py")
    if not target.exists():
        raise SystemExit("Нет scripts/build_scorm_module.py. Выполните git pull.")
    runpy.run_path(str(target), run_name="__main__")
