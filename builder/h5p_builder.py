"""Build JEMIX Academy H5P packages from YAML lesson sources.

This is the first scaffold. It creates the standard H5P package structure:
- h5p.json
- content/content.json

The output is a zip archive with .h5p extension. For production import into
H5P.com/Moodle/Lumi, the target platform must already have the required H5P
libraries installed.
"""
from __future__ import annotations

import json
import sys
import uuid
import zipfile
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = REPO_ROOT / "output" / "h5p"


def _uid() -> str:
    return str(uuid.uuid4())


def _advanced_text(title: str, body: str) -> dict[str, Any]:
    html = (
        "<div style='font-family:Arial,sans-serif;background:white;padding:14px;'>"
        "<div style='height:8px;background:#e30613;margin:-14px -14px 22px -14px;'></div>"
        f"<h2 style='color:#1f2937;margin-top:0'>{title}</h2>"
        f"{body}"
        "</div>"
    )
    return {
        "library": "H5P.AdvancedText 1.1",
        "params": {"text": html},
        "subContentId": _uid(),
        "metadata": {"contentType": "Text", "license": "U", "title": title},
    }


def _multi_choice(slide: dict[str, Any]) -> dict[str, Any]:
    correct = int(slide["correct"])
    answers = [
        {
            "text": answer,
            "correct": i == correct,
            "tipsAndFeedback": {
                "tip": "",
                "chosenFeedback": "Верно." if i == correct else "Неверно. Повторите предыдущий блок.",
                "notChosenFeedback": "",
            },
        }
        for i, answer in enumerate(slide["answers"])
    ]
    return {
        "library": "H5P.MultiChoice 1.16",
        "params": {
            "media": {"type": {"params": {}}},
            "question": f"<p>{slide['question']}</p>",
            "answers": answers,
            "overallFeedback": [
                {"from": 0, "to": 49, "feedback": "Повторите материал."},
                {"from": 50, "to": 79, "feedback": "Неплохо."},
                {"from": 80, "to": 100, "feedback": "Отлично!"},
            ],
            "behaviour": {
                "enableRetry": True,
                "enableSolutionsButton": True,
                "enableCheckButton": True,
                "type": "auto",
                "singlePoint": False,
                "randomAnswers": False,
                "showSolutionsRequiresInput": True,
                "confirmCheckDialog": False,
                "confirmRetryDialog": False,
                "autoCheck": False,
                "passPercentage": 80,
                "showScorePoints": True,
            },
            "UI": {
                "checkAnswerButton": "Проверить",
                "submitAnswerButton": "Отправить",
                "showSolutionButton": "Показать решение",
                "tryAgainButton": "Повторить",
                "tipsLabel": "Подсказка",
                "scoreBarLabel": "Вы набрали :num из :total баллов",
                "tipAvailable": "Подсказка доступна",
                "feedbackAvailable": "Доступен отзыв",
                "readFeedback": "Прочитать отзыв",
                "wrongAnswer": "Неверный ответ",
                "correctAnswer": "Правильный ответ",
                "shouldCheck": "Нужно ответить перед просмотром решения",
                "shouldNotScore": "Этот ответ не оценивается",
                "noInput": "Пожалуйста, выберите ответ",
                "a11yCheck": "Проверить ответы.",
                "a11yShowSolution": "Показать решение.",
                "a11yRetry": "Повторить задание.",
            },
            "confirmCheck": {
                "header": "Проверить?",
                "body": "Проверить ответ?",
                "cancelLabel": "Отмена",
                "confirmLabel": "Проверить",
            },
            "confirmRetry": {
                "header": "Повторить?",
                "body": "Ответ будет сброшен.",
                "cancelLabel": "Отмена",
                "confirmLabel": "Повторить",
            },
        },
        "subContentId": _uid(),
        "metadata": {"contentType": "Multiple Choice", "license": "U", "title": slide.get("title", "Квиз")},
    }


def _true_false(slide: dict[str, Any]) -> dict[str, Any]:
    return {
        "library": "H5P.TrueFalse 1.8",
        "params": {
            "question": f"<p>{slide['question']}</p>",
            "correct": "true" if bool(slide["correct"]) else "false",
            "behaviour": {
                "enableRetry": True,
                "enableSolutionsButton": True,
                "confirmCheckDialog": False,
                "confirmRetryDialog": False,
                "autoCheck": False,
            },
            "l10n": {
                "trueText": "Верно",
                "falseText": "Неверно",
                "score": "Вы набрали @score из @total",
                "checkAnswer": "Проверить",
                "submitAnswer": "Отправить",
                "showSolutionButton": "Показать решение",
                "tryAgain": "Повторить",
                "wrongAnswerMessage": "Неверно",
                "correctAnswerMessage": "Верно",
                "scoreBarLabel": "Вы набрали :num из :total баллов",
                "a11yCheck": "Проверить ответ",
                "a11yShowSolution": "Показать решение",
                "a11yRetry": "Повторить",
            },
        },
        "subContentId": _uid(),
        "metadata": {"contentType": "True/False Question", "license": "U", "title": slide.get("title", "Верно/неверно")},
    }


def _element(action: dict[str, Any]) -> dict[str, Any]:
    return {
        "x": 5,
        "y": 5,
        "width": 90,
        "height": 85,
        "action": action,
        "alwaysDisplayComments": False,
        "backgroundOpacity": 0,
        "displayAsButton": False,
        "buttonSize": "big",
        "goToSlideType": "specified",
        "invisible": False,
        "solution": "",
    }


def _slide(item: dict[str, Any]) -> dict[str, Any]:
    slide_type = item.get("type", "text")
    if slide_type == "quiz":
        action = _multi_choice(item)
    elif slide_type == "true_false":
        action = _true_false(item)
    else:
        action = _advanced_text(item["title"], item.get("body", ""))
    return {
        "elements": [_element(action)],
        "keywords": [{"main": item.get("title", item.get("question", "Слайд"))}],
        "slideBackgroundSelector": {},
    }


def build_package(source_file: Path) -> Path:
    lesson = yaml.safe_load(source_file.read_text(encoding="utf-8"))
    module = int(lesson["module"])
    lesson_no = int(lesson["lesson"])

    slides = [_slide(item) for item in lesson["slides"]]

    content = {
        "presentation": {
            "slides": slides,
            "keywordListEnabled": True,
            "globalBackgroundSelector": {"fillGlobalBackground": "#ffffff"},
            "keywordListAlwaysShow": False,
            "keywordListAutoHide": False,
            "keywordListOpacity": 90,
        },
        "override": {
            "activeSurface": False,
            "hideSummarySlide": False,
            "summarySlideSolutionButton": True,
            "summarySlideRetryButton": True,
            "enablePrintButton": False,
            "social": {
                "showFacebookShare": False,
                "facebookShare": {},
                "showTwitterShare": False,
                "twitterShare": {},
                "showGoogleShare": False,
                "googleShareUrl": "",
            },
        },
        "l10n": {
            "slide": "Слайд",
            "score": "Результат",
            "yourScore": "Ваш результат",
            "maxScore": "Максимальный результат",
            "total": "Всего",
            "totalScore": "Общий результат",
            "showSolutions": "Показать решение",
            "retry": "Повторить",
            "exportAnswers": "Экспортировать ответы",
            "hideKeywords": "Скрыть навигацию",
            "showKeywords": "Показать навигацию",
            "fullscreen": "Во весь экран",
            "exitFullscreen": "Выйти из полноэкранного режима",
            "prevSlide": "Предыдущий слайд",
            "nextSlide": "Следующий слайд",
            "currentSlide": "Текущий слайд",
            "lastSlide": "Последний слайд",
        },
    }

    h5p = {
        "title": lesson["title"],
        "language": "ru",
        "mainLibrary": "H5P.CoursePresentation",
        "embedTypes": ["div"],
        "license": "U",
        "defaultLanguage": "ru",
        "preloadedDependencies": [
            {"machineName": "H5P.CoursePresentation", "majorVersion": 1, "minorVersion": 25},
            {"machineName": "H5P.AdvancedText", "majorVersion": 1, "minorVersion": 1},
            {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
            {"machineName": "H5P.TrueFalse", "majorVersion": 1, "minorVersion": 8},
            {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
            {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
            {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
        ],
    }

    output_dir = OUTPUT_ROOT / f"module-{module:02d}"
    output_dir.mkdir(parents=True, exist_ok=True)
    package_path = output_dir / f"lesson-{lesson_no:02d}.h5p"

    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("h5p.json", json.dumps(h5p, ensure_ascii=False, indent=2))
        archive.writestr("content/content.json", json.dumps(content, ensure_ascii=False, indent=2))

    return package_path


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python builder/h5p_builder.py <lesson.yml>")
        raise SystemExit(2)
    source_file = Path(sys.argv[1])
    package_path = build_package(source_file)
    print(f"Built: {package_path}")


if __name__ == "__main__":
    main()
