#!/usr/bin/env python3
"""Build a branded JEMIX Academy Interactive Book prototype.

This script creates an H5P package that targets H5P.InteractiveBook.
It is intentionally focused on Module 1 and produces a test file for Brusnika LMS.

Usage:
  python scripts/build_interactive_book.py module-01

Output:
  dist/module-01/JEMIX_Module_01_Interactive_Book.h5p
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import zipfile
from pathlib import Path
from uuid import uuid4

MODULE = sys.argv[1] if len(sys.argv) > 1 else "module-01"
ROOT = Path(".")
DIST = ROOT / "dist" / MODULE
WORK = ROOT / "_interactive_book_build" / MODULE
OUT = DIST / "JEMIX_Module_01_Interactive_Book.h5p"

LESSONS = [
    ("lesson-1.1", "1.1 Что такое насос"),
    ("lesson-1.2", "1.2 Где применяются насосы"),
    ("lesson-1.3", "1.3 Как устроен насос"),
    ("lesson-1.4", "1.4 Как определить тип насоса"),
    ("lesson-1.5", "1.5 Ассортимент JEMIX"),
    ("lesson-1.6", "1.6 Практический экзамен"),
]


def strip_md(text: str) -> str:
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    text = text.replace("**", "")
    text = text.replace("---", "")
    return text.strip()


def read_slide(lesson: str, number: int) -> tuple[str, str]:
    p = ROOT / "voice" / "modules" / MODULE / lesson / f"slide{number:02d}.md"
    if not p.exists():
        return f"Слайд {number}", "Материал будет добавлен после финальной редакции."
    lines = p.read_text(encoding="utf-8").splitlines()
    title = strip_md(lines[0]) if lines else f"Слайд {number}"
    body = strip_md("\n".join(lines[1:])).strip() or "Материал слайда."
    return title, body


def compact_body(text: str) -> str:
    paragraphs = [x.strip() for x in text.split("\n") if x.strip()]
    text = " ".join(paragraphs)
    parts = re.split(r"(?<=[.!?])\s+", text)
    parts = [x for x in parts if x]
    if len(parts) > 3:
        parts = parts[:3]
    return " ".join(parts)


def page_html(title: str, body: str, lesson_title: str, audio_path: str | None = None) -> str:
    audio = ""
    if audio_path:
        audio = f"""
        <div style=\"margin-top:22px; padding:16px; background:#eef6ff; border-left:6px solid #0080ff; border-radius:14px;\">
          <div style=\"font-size:16px; font-weight:700; color:#1e3a8a; margin-bottom:8px;\">▶ Прослушать объяснение</div>
          <audio controls style=\"width:100%;\"><source src=\"{audio_path}\" type=\"audio/mpeg\"></audio>
        </div>
        """
    return f"""
<div style=\"font-family:Arial, sans-serif; background:#f4f8ff; border-radius:22px; border:1px solid #dbeafe; overflow:hidden;\">
  <div style=\"background:linear-gradient(90deg,#004a99,#0080ff); color:#fff; padding:20px 26px; display:flex; justify-content:space-between; align-items:center;\">
    <div style=\"font-size:30px; font-weight:800; letter-spacing:.2px;\">JEMIX Academy</div>
    <div style=\"font-size:16px; opacity:.95;\">{lesson_title}</div>
  </div>
  <div style=\"padding:30px;\">
    <div style=\"background:#fff; border-radius:20px; padding:30px; box-shadow:0 10px 26px rgba(15,23,42,.09); border:1px solid #e5e7eb;\">
      <div style=\"display:inline-block; background:#e30613; color:#fff; border-radius:999px; padding:7px 13px; font-size:14px; font-weight:700; margin-bottom:18px;\">Учебный экран</div>
      <h2 style=\"margin:0 0 18px; color:#111827; font-size:32px; line-height:1.15;\">{title}</h2>
      <div style=\"font-size:20px; line-height:1.55; color:#374151;\">
        <p>{body}</p>
      </div>
      <div style=\"margin-top:22px; padding:16px; background:#fff7ed; border-left:6px solid #e30613; border-radius:14px;\">
        <strong>Запомните:</strong> сначала задача клиента, затем группа оборудования и только потом модель JEMIX.
      </div>
      {audio}
    </div>
  </div>
</div>
"""


def advanced_text(text: str, title: str) -> dict:
    return {
        "content": {
            "library": "H5P.AdvancedText 1.1",
            "params": {"text": text},
            "subContentId": str(uuid4()),
            "metadata": {"contentType": "Text", "license": "U", "title": title},
        },
        "useSeparator": "auto",
    }


def multichoice(question: str, correct: str, wrong: list[str]) -> dict:
    answers = [{"text": correct, "correct": True, "tipsAndFeedback": {"tip": "", "chosenFeedback": "Верно.", "notChosenFeedback": ""}}]
    for w in wrong:
        answers.append({"text": w, "correct": False, "tipsAndFeedback": {"tip": "", "chosenFeedback": "Неверно. Вернитесь к материалу выше.", "notChosenFeedback": ""}})
    return {
        "content": {
            "library": "H5P.MultiChoice 1.16",
            "params": {
                "media": {"type": {"params": {}}},
                "question": f"<p>{question}</p>",
                "answers": answers,
                "behaviour": {"enableRetry": True, "enableSolutionsButton": True, "singlePoint": True, "randomAnswers": False},
                "overallFeedback": [{"from": 0, "to": 100}],
                "UI": {"checkAnswerButton": "Проверить", "submitAnswerButton": "Ответить", "showSolutionButton": "Показать ответ", "tryAgainButton": "Попробовать ещё"},
            },
            "subContentId": str(uuid4()),
            "metadata": {"contentType": "Multiple Choice", "license": "U", "title": question},
        },
        "useSeparator": "auto",
    }


def copy_audio(lesson: str, slide: int, target_content: Path) -> str | None:
    src = ROOT / "voice" / "modules" / MODULE / lesson / "audio" / f"slide{slide:02d}.mp3"
    if not src.exists():
        return None
    dst_dir = target_content / "audios" / lesson
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    shutil.copy2(src, dst)
    return f"audios/{lesson}/{src.name}"


def cover_html() -> str:
    return """
<div style="font-family:Arial, sans-serif; background:linear-gradient(135deg,#004a99,#0080ff); color:#fff; border-radius:24px; padding:42px; min-height:420px;">
  <div style="font-size:34px; font-weight:900; margin-bottom:28px;">JEMIX Academy</div>
  <div style="background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.28); border-radius:22px; padding:32px;">
    <div style="font-size:16px; text-transform:uppercase; letter-spacing:1px; opacity:.9;">Модуль 1</div>
    <h1 style="font-size:42px; line-height:1.1; margin:12px 0 16px;">Основы насосной техники</h1>
    <p style="font-size:21px; line-height:1.45; max-width:780px;">Один интерактивный модуль: короткие учебные экраны, озвучка, практические вопросы и итоговая проверка.</p>
    <div style="margin-top:26px; display:flex; gap:12px; flex-wrap:wrap;">
      <span style="background:#e30613; padding:10px 14px; border-radius:999px; font-weight:700;">6 уроков</span>
      <span style="background:rgba(255,255,255,.18); padding:10px 14px; border-radius:999px; font-weight:700;">озвучка</span>
      <span style="background:rgba(255,255,255,.18); padding:10px 14px; border-radius:999px; font-weight:700;">итоговый экзамен</span>
    </div>
  </div>
</div>
"""


def build_chapters(content_dir: Path) -> list[dict]:
    chapters = []
    chapters.append({
        "title": "Обложка",
        "content": [advanced_text(cover_html(), "JEMIX Academy — Модуль 1")],
    })
    for lesson, lesson_title in LESSONS:
        blocks = []
        for i in range(1, 4):
            title, body = read_slide(lesson, i)
            audio = copy_audio(lesson, i, content_dir)
            blocks.append(advanced_text(page_html(title, compact_body(body), lesson_title, audio), title))
        blocks.append(multichoice("С чего начинается правильный подбор насоса?", "С задачи клиента", ["С самой мощной модели", "С цены", "С цвета корпуса"]))
        chapters.append({"title": lesson_title, "content": blocks})
    chapters.append({
        "title": "Завершение",
        "content": [advanced_text(page_html("Модуль завершён", "Вы прошли основные темы первого модуля. Следующий шаг — проверка понимания и переход к модулю 2.", "Финал", None), "Модуль завершён")],
    })
    return chapters


def h5p_json() -> dict:
    return {
        "title": "JEMIX Academy — Module 1 Interactive Book",
        "language": "ru",
        "mainLibrary": "H5P.InteractiveBook",
        "embedTypes": ["div"],
        "license": "U",
        "preloadedDependencies": [
            {"machineName": "H5P.InteractiveBook", "majorVersion": 1, "minorVersion": 11},
            {"machineName": "H5P.AdvancedText", "majorVersion": 1, "minorVersion": 1},
            {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16}
        ]
    }


def zip_dir(src: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(src).as_posix())


def main() -> int:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True, exist_ok=True)
    content_dir = WORK / "content"
    content_dir.mkdir(parents=True, exist_ok=True)

    params = {
        "chapters": build_chapters(content_dir),
        "behaviour": {"defaultTableOfContents": True, "progressIndicators": True, "summary": True},
        "l10n": {"startLabel": "Начать", "resumeLabel": "Продолжить", "restartLabel": "Начать заново"}
    }

    (WORK / "h5p.json").write_text(json.dumps(h5p_json(), ensure_ascii=False, indent=2), encoding="utf-8")
    (content_dir / "content.json").write_text(json.dumps(params, ensure_ascii=False, indent=2), encoding="utf-8")
    zip_dir(WORK, OUT)
    print(f"OK: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
