#!/usr/bin/env python3
"""
Generate JEMIX lesson audio with Yandex SpeechKit.

Run from VS Code terminal in the lesson-1.5 folder:

  python generate_yandex_audio.py

Required environment variables:

  YANDEX_FOLDER_ID
  YANDEX_API_KEY       or       YANDEX_IAM_TOKEN

Optional:

  YANDEX_VOICE=ermil
  YANDEX_EMOTION=good
  YANDEX_SPEED=1.0
"""

from __future__ import annotations

import os
import re
import sys
import time
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


LESSON_DIR = Path(__file__).resolve().parent

# Supports both structures:
# 1) generated SCORM source: lesson-1.5/scorm/audio_scripts -> lesson-1.5/scorm/audio
# 2) local repository source: lesson-1.5/audio only, with scripts embedded below
SCORM_DIR = LESSON_DIR / "scorm"
if SCORM_DIR.exists():
    AUDIO_SCRIPTS_DIR = SCORM_DIR / "audio_scripts"
    AUDIO_DIR = SCORM_DIR / "audio"
else:
    AUDIO_SCRIPTS_DIR = LESSON_DIR / "audio_scripts"
    AUDIO_DIR = LESSON_DIR / "audio"
PACKAGE_NAME = "JEMIX_Academy_1_5_SCORM_UX_v2_yandex_audio.zip"
REPO_PACK_NAME = "JEMIX_Academy_1_5_Repo_Pack_yandex_audio.zip"
TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"

FALLBACK_SCRIPTS = {
    "slide01": "В этом уроке собираем базовый алгоритм подбора насоса. Продавец начинает не с модели и не с цены, а с задачи клиента. Затем уточняет среду, источник, параметры системы и комплект для монтажа. Так консультация становится управляемой, а риск ошибки заметно снижается.",
    "slide02": "После урока продавец должен уверенно объяснять, почему подбор начинается с задачи клиента. Важно видеть связь между средой, источником, расходом, напором и комплектом. Отдельная модель насоса без этих условий ещё не является правильным решением.",
    "slide03": "Базовый алгоритм можно держать как короткую цепочку. Сначала задача клиента, затем среда, источник, параметры, риски и комплект. Если продавец пропускает один из шагов, он подбирает не систему, а догадку.",
    "slide04": "Первый шаг — определить задачу. Клиенту может быть нужно подать воду, откачать её, повысить давление, обеспечить циркуляцию или перекачать стоки. Эти задачи ведут к разным группам насосов.",
    "slide05": "Продавец не обязан сразу знать модель. Его задача — правильно задать вопросы. Для какой задачи нужен насос, какую жидкость перекачиваем, откуда берём воду, куда подаём, какая высота и нужна ли защита.",
    "slide06": "Проверьте базовый принцип. Правильный подбор начинается с задачи клиента и условий работы. Цена, мощность и внешний вид не могут заменить понимание задачи.",
    "slide07": "Второй шаг — уточнить среду. Чистая вода, загрязнённая вода, стоки и теплоноситель требуют разных решений. Ошибка на этом шаге часто приводит к поломке, возврату или недовольству клиента.",
    "slide08": "Когда задача и среда понятны, появляется карта выбора. Для скважины нужны одни решения, для дренажа другие, для отопления третьи. Продавец сначала выбирает группу, а уже потом уточняет модель.",
    "slide09": "Это вопрос на различие групп. Если клиент говорит про грязную воду из приямка, ближе дренажный насос. Циркуляционный, повысительный и скважинный решают другие задачи.",
    "slide10": "После выбора группы проверяют параметры. Важны расход, напор, давление, глубина, длина трассы и потери. Максимальные цифры из паспорта нельзя читать отдельно от условий системы.",
    "slide11": "Отдельно продавец проверяет риски. Сухой ход, песок, потери напора, несовместимые фитинги и нестабильное питание могут испортить даже правильно выбранную модель.",
    "slide12": "Насос редко работает один. Часто нужны обратный клапан, фильтр, автоматика, защита, труба, шланг и фитинги. Комплект — это часть правильного решения, а не дополнительная продажа ради суммы.",
    "slide13": "В кейсе со скважиной продавец уточняет глубину, уровень воды, требуемый расход, напор, потери и защиту от сухого хода. Ответ строится не вокруг самой мощной модели, а вокруг устойчивой схемы.",
    "slide14": "Если в квартире вода есть, но напор слабый, задача не в добыче воды из источника. Сначала проверяют условия существующей системы и рассматривают повысительное решение.",
    "slide15": "Типичная ошибка начинающего продавца — начать с мощности и цены, не задав вопросы. Правильная логика другая: задача, среда, источник, параметры и риски. Только после этого выбирают модель.",
    "slide16": "Это утверждение верное. Подбор начинается с вопроса, что должен сделать насос. Такой вопрос переводит разговор с отдельных характеристик на реальную задачу клиента.",
    "slide17": "Клиент спрашивает: нужен насос для дома. Продавец думает: нужно понять задачу, источник, расход, напор и защиту. Отвечает просто: сначала уточню условия, чтобы подобрать не просто насос, а рабочую схему.",
    "slide18": "Насос нельзя подбирать только по мощности, потому что мощность не показывает рабочую точку. Для решения нужны расход, напор, среда, источник и условия системы.",
    "slide19": "Утверждение верное. Если источник воды нестабильный, защита от сухого хода становится обязательной темой консультации. Она помогает предотвратить перегрев и повреждение насоса.",
    "slide20": "Итог урока простой. Алгоритм подбора начинается с задачи клиента. Затем уточняют среду, источник, параметры и комплект. Главная ошибка — выбирать насос без вопросов. Следующий шаг — финальный тест модуля один.",
}


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def auth_header() -> dict[str, str]:
    api_key = os.environ.get("YANDEX_API_KEY", "").strip()
    iam_token = os.environ.get("YANDEX_IAM_TOKEN", "").strip()
    if api_key:
        return {"Authorization": f"Api-Key {api_key}"}
    if iam_token:
        return {"Authorization": f"Bearer {iam_token}"}
    raise RuntimeError("Set YANDEX_API_KEY or YANDEX_IAM_TOKEN")


def synthesize(text: str, out_path: Path) -> None:
    folder_id = require_env("YANDEX_FOLDER_ID")
    voice = os.environ.get("YANDEX_VOICE", "ermil")
    emotion = os.environ.get("YANDEX_EMOTION", "good")
    speed = os.environ.get("YANDEX_SPEED", "1.0")

    payload = urlencode(
        {
            "text": text,
            "lang": "ru-RU",
            "voice": voice,
            "emotion": emotion,
            "speed": speed,
            "format": "mp3",
            "folderId": folder_id,
        }
    ).encode("utf-8")

    request = Request(
        TTS_URL,
        data=payload,
        headers={
            **auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            audio = response.read()
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Yandex SpeechKit HTTP {exc.code}: {details}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error while calling Yandex SpeechKit: {exc}") from exc

    if len(audio) < 1024:
        raise RuntimeError(f"Suspiciously small audio response for {out_path.name}")

    out_path.write_bytes(audio)


def generate_audio() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    scripts = sorted(AUDIO_SCRIPTS_DIR.glob("slide*.txt"))

    if scripts:
        items = [
            (script_path.stem, script_path.read_text(encoding="utf-8").strip())
            for script_path in scripts
        ]
    else:
        print("No audio_scripts folder found. Using built-in Lesson 1.5 scripts.")
        items = sorted(FALLBACK_SCRIPTS.items())

    if len(items) != 20:
        raise RuntimeError(f"Expected 20 audio scripts, found {len(items)}")

    for slide_id, text in items:
        number = slide_id.replace("slide", "")
        out_path = AUDIO_DIR / f"slide{number}.mp3"
        if not text:
            raise RuntimeError(f"Empty audio script: {slide_id}")
        print(f"Generating {out_path.relative_to(LESSON_DIR)}")
        synthesize(text, out_path)
        time.sleep(0.2)


def ensure_audio_css() -> None:
    if not SCORM_DIR.exists():
        return
    css_path = SCORM_DIR / "style-v2.css"
    css = css_path.read_text(encoding="utf-8")
    marker = "/* Yandex audio player */"
    if marker in css:
        return
    css += """

/* Yandex audio player */
.audio-player{margin-top:auto;margin-bottom:12px;background:#f6f7f8;border:1px solid #e1e5eb;border-radius:13px;padding:12px 14px}
.audio-player b{display:block;margin-bottom:8px;color:#1f2937;font-size:14px}
.audio-player audio{width:100%;height:36px}
"""
    css_path.write_text(css, encoding="utf-8")


def update_slide_html() -> None:
    if not SCORM_DIR.exists():
        return
    for number in range(1, 21):
        slide_path = SCORM_DIR / f"slide{number:02d}.html"
        html = slide_path.read_text(encoding="utf-8")
        audio_html = (
            f'<div class="audio-player">'
            f"<b>Прослушать объяснение</b>"
            f'<audio controls preload="metadata" src="audio/slide{number:02d}.mp3"></audio>'
            f"</div>"
        )

        html = re.sub(r'<div class="audio-player">.*?</div>', "", html, flags=re.S)
        html = html.replace('<div class="audio-note">', audio_html + '<div class="audio-note">')
        slide_path.write_text(html, encoding="utf-8")


def update_manifest() -> None:
    if not SCORM_DIR.exists():
        return
    manifest_path = SCORM_DIR / "imsmanifest.xml"
    xml = manifest_path.read_text(encoding="utf-8")
    if 'href="audio/slide01.mp3"' in xml:
        return

    audio_files = "\n".join(
        f'    <file href="audio/slide{number:02d}.mp3"/>'
        for number in range(1, 21)
    )
    xml = xml.replace("  </resource></resources>", f"{audio_files}\n  </resource></resources>")
    manifest_path.write_text(xml, encoding="utf-8")


def update_lesson_yml() -> None:
    if not (LESSON_DIR / "lesson.yml").exists():
        return
    yml_path = LESSON_DIR / "lesson.yml"
    yml = yml_path.read_text(encoding="utf-8")
    yml = yml.replace(
        'status: "prepared_not_scorm_ready_missing_real_audio"',
        'status: "scorm_ready_yandex_audio_generated"',
    )
    yml = yml.replace(
        'package: "JEMIX_Academy_1_5_SCORM_UX_v2_no_images.zip"',
        f'package: "{PACKAGE_NAME}"',
    )
    yml = yml.replace(
        'status: "scripts_prepared_mp3_not_generated"',
        'status: "generated"',
    )
    yml = yml.replace(
        '  engine_target: "Yandex SpeechKit"',
        '  engine: "Yandex SpeechKit"',
    )
    yml_path.write_text(yml, encoding="utf-8")


def zip_dir(source_dir: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(source_dir).as_posix())


def rebuild_packages() -> None:
    if not SCORM_DIR.exists():
        print("No scorm folder found. Audio files generated only.")
        return
    scorm_zip = LESSON_DIR / PACKAGE_NAME
    repo_pack = LESSON_DIR / REPO_PACK_NAME
    zip_dir(SCORM_DIR, scorm_zip)

    if repo_pack.exists():
        repo_pack.unlink()
    with zipfile.ZipFile(repo_pack, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for folder in ("scorm",):
            for file_path in sorted((LESSON_DIR / folder).rglob("*")):
                if file_path.is_file():
                    zf.write(file_path, file_path.relative_to(LESSON_DIR).as_posix())
        for name in ("lesson.yml", "MANIFEST.txt", PACKAGE_NAME):
            file_path = LESSON_DIR / name
            if file_path.exists():
                zf.write(file_path, file_path.name)


def validate() -> None:
    missing = [
        f"audio/slide{number:02d}.mp3"
        for number in range(1, 21)
        if not (AUDIO_DIR / f"slide{number:02d}.mp3").exists()
    ]
    if missing:
        raise RuntimeError("Missing generated audio files: " + ", ".join(missing))

    zip_path = LESSON_DIR / PACKAGE_NAME
    if not zip_path.exists():
        print("No SCORM ZIP rebuilt because this folder has no scorm source.")
        return
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    required = {"imsmanifest.xml", "index.html"} | {
        f"slide{number:02d}.html" for number in range(1, 21)
    } | {
        f"audio/slide{number:02d}.mp3" for number in range(1, 21)
    }
    missing_in_zip = sorted(required - names)
    if missing_in_zip:
        raise RuntimeError("Missing files in SCORM ZIP: " + ", ".join(missing_in_zip))


def main() -> int:
    try:
        generate_audio()
        ensure_audio_css()
        update_slide_html()
        update_manifest()
        update_lesson_yml()
        rebuild_packages()
        validate()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("OK: Yandex audio generated and SCORM package rebuilt")
    print(f"SCORM: {LESSON_DIR / PACKAGE_NAME}")
    print(f"Repo-pack: {LESSON_DIR / REPO_PACK_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
