#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

RED = "#D71920"
DARK = "#1F2937"
MID = "#6B7280"
LIGHT = "#E5E7EB"
BG = "#FAFAFA"

SLIDES = [
    ("Что такое насос", ["Источник воды", "Насос", "Потребитель"]),
    ("Где применяются насосы", ["Дом", "Полив", "Отопление", "Дрен