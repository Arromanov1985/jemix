from __future__ import annotations

import html
import json
import re
import zipfile
from pathlib import Path


SOURCE_JSON = Path("lesson_1_3_voice_source.json")
SCORM_DIR = Path("scorm_work")
OUTPUT_ZIP = Path.home() / "Downloads" / (
    "JEMIX_Academy_Lesson_1_3_SCORM_"
    "UXv2_FINAL_EXACT_WITH_YANDEX_VOICE_STANDARD_READ_TEXTS.zip"
)


def load_slides() -> list[dict]:
    if not SOURCE_JSON.exists():
        raise FileNotFoundError(f"Не найден файл: {SOURCE_JSON}")

    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))

    if not isinstance(data, list) or len(data) != 21:
        raise ValueError("В JSON должно быть ровно 21 слайд.")

    return data


def replace_read_text(html_text: str, new_text: str) -> str:
    escaped = html.escape(new_text, quote=True)

    pattern = r'(data-read-text=")[^"]*(")'

    updated, count = re.subn(
        pattern,
        lambda match: f'{match.group(1)}{escaped}{match.group(2)}',
        html_text,
        count=1,
        flags=re.DOTALL,
    )

    if count != 1:
        raise RuntimeError(
            "Не удалось найти или заменить data-read-text."
        )

    return updated


def update_html_files(slides: list[dict]) -> None:
    for slide in slides:
        number = int(slide["number"])
        text = str(slide["text"]).strip()

        html_path = SCORM_DIR / f"slide{number:02d}.html"

        if not html_path.exists():
            raise FileNotFoundError(f"Не найден файл: {html_path}")

        original = html_path.read_text(encoding="utf-8")
        updated = replace_read_text(original, text)

        html_path.write_text(updated, encoding="utf-8")

        print(
            f"slide{number:02d}.html: "
            f"обновлён data-read-text"
        )


def validate(slides: list[dict]) -> None:
    errors: list[str] = []

    for slide in slides:
        number = int(slide["number"])
        text = str(slide["text"]).strip()

        html_path = SCORM_DIR / f"slide{number:02d}.html"
        content = html_path.read_text(encoding="utf-8")

        escaped = html.escape(text, quote=True)

        if f'data-read-text="{escaped}"' not in content:
            errors.append(
                f"slide{number:02d}: полный текст не найден"
            )

    if errors:
        raise RuntimeError("\n".join(errors))


def build_zip() -> None:
    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()

    with zipfile.ZipFile(
        OUTPUT_ZIP,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for path in sorted(SCORM_DIR.rglob("*")):
            if path.is_file():
                archive.write(
                    path,
                    path.relative_to(SCORM_DIR).as_posix(),
                )

    print()
    print(f"Итоговый SCORM: {OUTPUT_ZIP}")


def main() -> None:
    slides = load_slides()
    update_html_files(slides)
    validate(slides)
    build_zip()

    print()
    print("Готово.")
    print(
        "Кнопка «Прочитать» теперь показывает "
        "полный текст озвучки на всех 21 экранах."
    )


if __name__ == "__main__":
    main()
