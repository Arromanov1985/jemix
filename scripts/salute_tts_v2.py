import os, sys, uuid, json, time, shutil, subprocess, tempfile
from pathlib import Path
import requests
from dotenv import load_dotenv

TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
TTS_URL = "https://smartspeech.sber.ru/rest/v1/text:synthesize"
CACHE = ".salute_token_cache.json"


def env_bool(name, default=True):
    v = os.getenv(name