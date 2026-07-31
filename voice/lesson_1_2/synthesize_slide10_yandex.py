#!/usr/bin/env python3
import argparse
import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path


TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"


def auth_header() -> str:
    api_key = os.getenv("YANDEX_API_KEY")
    iam_token = os.getenv("YANDEX_IAM_TOKEN")

    if api_key:
        return f"Api-Key {api_key}"
    if iam_token:
        return f"Bearer {iam_token}"

    raise SystemExit(
        "Нет ключа для Yandex SpeechKit. "
        "Перед запуском задайте YANDEX_API_KEY или YANDEX_IAM_TOKEN."
    )


def synthesize(text: str, output_path: Path, folder_id: str | None) -> None:
    data = {
        "text": text,
        "lang": "ru-RU",
        "voice": "ermil",
        "emotion": "good",
        "speed": "1.0",
        "format": "mp3",
    }

    if folder_id:
        data["folderId"] = folder_id

    request = urllib.request.Request(
        TTS_URL,
        data=urllib.parse.urlencode(data).encode("utf-8"),
        headers={
            "Authorization": auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            audio = response.read()
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"SpeechKit вернул ошибку {error.code}: {details}") from error
    except urllib.error.URLError as error:
        raise SystemExit(f"Не удалось подключиться к SpeechKit: {error}") from error

    if not audio:
        raise SystemExit("SpeechKit вернул пустой аудиофайл.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(audio)
    print(f"Готово: {output_path}")


def replace_slide10_in_zip(source_zip: Path, slide10_mp3: Path, output_zip: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        with zipfile.ZipFile(source_zip, "r") as archive:
            archive.extractall(tmp_path)

        target = tmp_path / "slide10.mp3"
        if not target.exists():
            raise SystemExit("В исходном аудио-ZIP не найден slide10.mp3.")

        shutil.copy2(slide10_mp3, target)

        output_zip.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path in sorted(tmp_path.rglob("*")):
                if file_path.is_file():
                    archive.write(file_path, file_path.relative_to(tmp_path))

    print(f"Новый аудио-ZIP: {output_zip}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Синтез slide10.mp3 для JEMIX через Yandex SpeechKit."
    )
    parser.add_argument(
        "--text",
        default="voice/lesson_1_2/slide10_tts_text.txt",
        help="Путь к plain-text сценарию озвучки.",
    )
    parser.add_argument(
        "--out",
        default="voice/lesson_1_2/slide10.mp3",
        help="Куда сохранить новый slide10.mp3.",
    )
    parser.add_argument(
        "--folder-id",
        default=os.getenv("YANDEX_FOLDER_ID"),
        help="Yandex Cloud folderId. Можно передать через YANDEX_FOLDER_ID.",
    )
    parser.add_argument(
        "--audio-zip",
        default="",
        help="Исходный аудио-ZIP, где нужно заменить slide10.mp3.",
    )
    parser.add_argument(
        "--zip-out",
        default="voice/lesson_1_2/lesson-1.2-audio-corrected-slide10.zip",
        help="Куда сохранить новый аудио-ZIP.",
    )
    args = parser.parse_args()

    text_path = Path(args.text)
    output_mp3 = Path(args.out)
    text = text_path.read_text(encoding="utf-8").strip()

    if not text:
        raise SystemExit(f"Файл с текстом пустой: {text_path}")

    synthesize(text, output_mp3, args.folder_id)

    if args.audio_zip:
        replace_slide10_in_zip(Path(args.audio_zip), output_mp3, Path(args.zip_out))

    return 0


if __name__ == "__main__":
    sys.exit(main())
