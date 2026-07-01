from pathlib import Path

LESSONS = {
    "academy/module-01": ["1_1", "1_2", "1_3", "1_4", "1_5", "final_test"],
    "academy/module-02": ["2_1", "2_2", "2_3", "2_4", "2_5"],
    "academy/module-03": ["3_1", "3_2", "3_3", "3_4", "3_5_1", "3_5_2", "3_6_1", "3_6_2", "3_7", "3_8", "3_9", "3_10", "3_11", "3_12"],
}

README_TEMPLATE = """# {lesson_id}\n\nСтатус: каркас добавлен.\n\n## Файлы урока\n\n- `lesson.yml` — структура урока и метаданные.\n- `notes.md` — текст лектора.\n- `quiz.yml` — вопросы и ответы.\n- `assets/` — схемы, изображения и таблицы.\n"""

NOTES_TEMPLATE = """# {lesson_id}\n\n## Текст лектора\n\nЧерновик. Здесь будет полный текст объяснения для преподавателя/диктора.\n\n## Что нужно доработать\n\n- Проверить факты по каталогу JEMIX.\n- Добавить примеры.\n- Добавить схемы и изображения в `assets/`.\n"""

QUIZ_TEMPLATE = """questions:\n  - type: single_choice\n    question: \"Черновой вопрос для урока {lesson_id}.\"\n    answers:\n      - \"Правильный ответ\"\n      - \"Неверный ответ 1\"\n      - \"Неверный ответ 2\"\n      - \"Неверный ответ 3\"\n    correct: 0\n"""

LESSON_TEMPLATE = """id: \"{lesson_id}\"\ntitle: \"{lesson_id}\"\nstatus: \"scaffold\"\nformat: \"H5P Course Presentation\"\n\nobjectives: []\n\nslides:\n  - type: title\n    title: \"{lesson_id}\"\n  - type: summary\n    title: \"Итоги\"\n    body: \"Черновик урока.\"\n"""


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"created: {path}")
    else:
        print(f"exists:  {path}")


def main() -> None:
    for module_path, lesson_ids in LESSONS.items():
        module = Path(module_path)
        module.mkdir(parents=True, exist_ok=True)
        for lesson_id in lesson_ids:
            lesson_dir = module / lesson_id
            write_if_missing(lesson_dir / "lesson.yml", LESSON_TEMPLATE.format(lesson_id=lesson_id))
            write_if_missing(lesson_dir / "notes.md", NOTES_TEMPLATE.format(lesson_id=lesson_id))
            write_if_missing(lesson_dir / "quiz.yml", QUIZ_TEMPLATE.format(lesson_id=lesson_id))
            write_if_missing(lesson_dir / "README.md", README_TEMPLATE.format(lesson_id=lesson_id))
            write_if_missing(lesson_dir / "assets" / ".gitkeep", "")


if __name__ == "__main__":
    main()
