from __future__ import annotations
import argparse, os, sys, time
from pathlib import Path
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / 'voice_scripts'
AUDIO_DIR = BASE_DIR / 'audio'
TTS_URL = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
VOICE_SLIDES = list(range(1, 21)) + [26]

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--voice',default='ermil')
    p.add_argument('--emotion',default='good')
    p.add_argument('--speed',type=float,default=1.0)
    p.add_argument('--overwrite',action='store_true')
    return p.parse_args()

def main():
    load_dotenv(BASE_DIR / '.env')
    api_key=os.getenv('YANDEX_API_KEY','').strip()
    folder_id=os.getenv('YANDEX_FOLDER_ID','').strip()
    if not api_key or not folder_id or 'replace_with' in api_key or 'replace_with' in folder_id:
        print('ERROR: fill YANDEX_API_KEY and YANDEX_FOLDER_ID in .env', file=sys.stderr)
        return 2
    args=parse_args()
    AUDIO_DIR.mkdir(exist_ok=True)
    print(f'Voice: {args.voice}; emotion: {args.emotion}; speed: {args.speed}')
    headers={'Authorization':f'Api-Key {api_key}'}
    for n in VOICE_SLIDES:
        src=SCRIPTS_DIR / f'slide{n:02d}.txt'
        dst=AUDIO_DIR / f'slide{n:02d}.mp3'
        if dst.exists() and not args.overwrite:
            print(f'SKIP {dst.name}')
            continue
        text=src.read_text(encoding='utf-8').strip()
        data={'text':text,'lang':'ru-RU','voice':args.voice,'emotion':args.emotion,'speed':str(args.speed),'format':'mp3','folderId':folder_id}
        print(f'GENERATE {dst.name}')
        for attempt in range(3):
            r=requests.post(TTS_URL,headers=headers,data=data,timeout=120)
            if r.ok:
                dst.write_bytes(r.content)
                print(f'OK: {len(r.content):,} bytes')
                break
            wait=3*(attempt+1)
            print(f'ERROR HTTP {r.status_code}: {r.text}. Retry in {wait} sec.')
            if attempt==2:
                return 1
            time.sleep(wait)
    print(f'DONE: {AUDIO_DIR}')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
