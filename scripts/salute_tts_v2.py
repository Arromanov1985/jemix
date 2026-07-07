import os, sys, uuid, json, time, hashlib
from pathlib import Path
import requests
from dotenv import load_dotenv

TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
TTS_URL = "https://smartspeech.sber.ru/rest/v1/text:synthesize"
CACHE = ".salute_token_cache.json"

def env_bool(name, default=True):
    v = os.getenv(name, "").lower().strip()
    return default if not v else v not in ("0", "false", "no", "off")

def get_token():
    cached = Path(CACHE)
    if cached.exists():
        data = json.loads(cached.read_text(encoding="utf-8"))
        if data.get("access_token") and data.get("expires_at", 0) - int(time.time()*1000) > 120000:
            return data["access_token"]

    auth_key = os.getenv("SBER_AUTH_KEY", "").strip()
    if not auth_key:
        raise SystemExit("Нет SBER_AUTH_KEY в .env")

    headers = {
        "Authorization": f"Basic {auth_key}",
        "RqUID": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    r = requests.post(
        TOKEN_URL,
        headers=headers,
        data={"scope": os.getenv("SBER_SCOPE", "SALUTE_SPEECH_PERS")},
        verify=env_bool("SBER_SSL_VERIFY", True),
        timeout=60,
    )
    if r.status_code >= 400:
        raise SystemExit(f"OAuth error {r.status_code}: {r.text}")

    data = r.json()
    token = data["access_token"]
    cached.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return token

def main():
    load_dotenv()
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "voice/modules/module-01/lesson-1.1")
    verify = env_bool("SBER_SSL_VERIFY", True)
    token = get_token()

    files = sorted(folder.glob("slide*.ssml"))
    print(f"SSML files: {len(files)}")

    audio_dir = folder / "audio"
    audio_dir.mkdir(exist_ok=True)

    for f in files:
        ssml = f.read_text(encoding="utf-8").strip()
        out = audio_dir / f"{f.stem}.mp3"
        print(f"generate: {f.name} -> {out.name}")

        r = requests.post(
            TTS_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/ssml",
                "Accept": "audio/mpeg",
            },
            data=ssml.encode("utf-8"),
            verify=verify,
            timeout=120,
        )

        if r.status_code >= 400:
            raise SystemExit(f"TTS error {r.status_code}: {r.text}")

        out.write_bytes(r.content)

    print("Done.")

if __name__ == "__main__":
    main()
