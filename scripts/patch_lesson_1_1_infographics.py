#!/usr/bin/env python3
from pathlib import Path
import argparse,re,tempfile,zipfile
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'dist/module-01/JEMIX_Academy_1_1_SCORM_UX_v2_FINAL_WITH_JEMIX_PUMPS.zip'
ATLAS=ROOT/'dist/module-01/JEMIX_Academy_1_1_INFOGRAPHICS_ATLAS.png'
OUT=ROOT/'dist/module-01/JEMIX_Academy_1_1_SCORM_INFOGRAPHICS_FINAL.zip'
INTERACTIVE={6,9,16,18,19}

def crop_atlas(at