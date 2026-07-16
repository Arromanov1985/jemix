#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
TTS_URL = "https://smartspeech.sber