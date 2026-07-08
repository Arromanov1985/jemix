#!/usr/bin/env python3
"""Universal JEMIX Academy lesson generator.

Usage:
  python scripts/generate_lesson.py module-01 lesson-1.2
  python scripts/generate_lesson.py module-01 lesson-1.3 --force

Creates academy and voice source files for a lesson from built-in lesson presets.
Generated MP3 files are created separately with scripts/salute_tts_v2.py.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class Slide:
    number: int
    title: str
    body: str
    ssml: str
    h5p: str = ""


@dataclass
class LessonPreset:
    module: str
    lesson: str
    title: str
    goal: str
    main_idea: str
    slides: List[Slide]
    quiz_yml: str


def slug_to_number(lesson_slug: str) -> str:
    match = re.search(r"lesson-(\d+)\.(\d+)", lesson_slug)
    if not match:
        raise ValueError(f"Bad lesson slug: {lesson_slug}. Expected lesson-1.2")
    return f"{match.group(1)}.{match.group(2)}"


def module_to_number(module_slug: str) -> int:
    match = re.search(r"module-(\d+)", module_slug)
    if not match:
        raise ValueError(f"Bad module slug: {module_slug}. Expected module-01")
    return int(match.group(1))


def ssml(title: str, text: str) -> str:
    return f"""<speak>
<prosody rate="95%">

{title}.

<break time="700ms"/>

{text}

<break time="800ms"/>

</prosody>
</speak>
"""


def lesson_1_2() -> LessonPreset:
    slides = [
        Slide(1, "Клиент покупает не насос", "Большинство покупателей не знают модель насоса. Они знают только свою проблему. Главная задача продавца — понять, какую проблему нужно решить, и только после этого переходить к подбору оборудования.", """<speak>
<prosody rate="95%">
Добро пожаловать во второй урок.
<break time="700ms"/>
Большинство покупателей не знают, какой насос им нужен.
<break time="500ms"/>
Они знают только свою проблему.
<break time="700ms"/>
<emphasis level="moderate">Главная задача продавца — понять проблему клиента.</emphasis>
<break time="700ms"/>
И только после этого переходить к подбору оборудования.
</prosody>
</speak>
""", "Question Set: Что покупает клиент? Ответ: решение своей задачи."),
        Slide(2, "Голос клиента", "Клиенты редко называют модель насоса. Чаще всего они говорят: после дождя затопило подвал, из скважины пропала вода, нужно поливать огород, на втором этаже слабый напор, нужно подключить санузел, батареи плохо греют.", """<speak>
<prosody rate="95%">
Послушайте, как обычно обращаются покупатели.
<break time="700ms"/>
После дождя затопило подвал.
<break time="500ms"/>
Из скважины пропала вода.
<break time="500ms"/>
Нужно поливать огород.
<break time="500ms"/>
На втором этаже слабый напор.
<break time="500ms"/>
Нужно подключить санузел.
<break time="500ms"/>
Батареи плохо греют.
<break time="900ms"/>
<emphasis level="moderate">Все эти обращения — это разные задачи.</emphasis>
</prosody>
</speak>
""", "Drag & Drop: сопоставить фразу клиента и задачу."),
        Slide(3, "Алгоритм подбора", "Проблема клиента → определяем задачу → выбираем группу насосов → подбираем модель JEMIX. Именно такой порядок позволяет избежать ошибок при подборе.", """<speak>
<prosody rate="95%">
Запомните основной алгоритм.
<break time="700ms"/>
Сначала — <emphasis level="moderate">проблема клиента.</emphasis>
<break time="600ms"/>
Затем — определяем задачу.
<break time="600ms"/>
После этого — выбираем группу насосов.
<break time="600ms"/>
И только в самом конце — подбираем конкретную модель Джемикс.
<break time="900ms"/>
Именно этот порядок мы будем использовать на протяжении всего курса.
</prosody>
</speak>
""", "Fill in the blanks: Проблема клиента → ______ → группа насоса → модель JEMIX."),
        Slide(4, "Водоснабжение дома", "Голос клиента: из скважины перестала поступать вода. Нужно выяснить источник воды, глубину, расстояние до дома и количество пользователей. Не выбирайте насос до получения этих данных.", """<speak>
<prosody rate="95%">
Рассмотрим первую задачу.
<break time="700ms"/>
Клиент говорит: <emphasis level="moderate">из скважины перестала поступать вода.</emphasis>
<break time="900ms"/>
Не спешите предлагать насос.
<break time="500ms"/>
Сначала выясните источник воды, глубину, расстояние до дома и количество пользователей.
<break time="900ms"/>
Только после этого можно переходить к подбору оборудования.
</prosody>
</speak>
""", "Branching Question: что спросить первым? Ответ: глубина источника воды."),
        Slide(5, "Полив участка", "Голос клиента: нужно поливать огород и теплицу. Нужно уточнить площадь полива, источник воды, ручной или автоматический режим и количество одновременно работающих точек.", """<speak>
<prosody rate="95%">
Следующая задача — полив участка.
<break time="700ms"/>
Клиент говорит: <emphasis level="moderate">нужно поливать огород и теплицу.</emphasis>
<break time="900ms"/>
Уточните площадь полива, источник воды, ручной или автоматический режим и сколько точек полива будут работать одновременно.
<break time="900ms"/>
Эти данные необходимы для правильного подбора насоса.
</prosody>
</speak>
""", "Drag & Drop: вопрос и цель вопроса."),
        Slide(6, "Откачка воды", "Голос клиента: после дождя затопило подвал. Это задача дренажного насоса. Нужно уточнить, вода чистая или грязная, есть ли песок, мусор и куда нужно откачивать воду.", """<speak>
<prosody rate="95%">
Одна из самых частых сезонных задач — откачка воды.
<break time="700ms"/>
Клиент говорит: <emphasis level="strong">после дождя затопило подвал.</emphasis>
<break time="1200ms"/>
Подумайте, <break time="2000ms"/> какой насос потребуется в этой ситуации.
<break time="900ms"/>
Правильный ответ — дренажный насос.
<break time="800ms"/>
Но перед подбором обязательно уточните, чистая вода или грязная, есть ли песок, есть ли мусор и куда нужно откачивать воду.
</prosody>
</speak>
""", "Single Choice: затопило подвал. Ответ: дренажный насос."),
        Slide(7, "Канализация", "Голос клиента: нужно подключить санузел в подвальном помещении. Нужно понять, есть ли твёрдые включения, нужен ли измельчитель и на какую высоту необходимо поднять стоки.", """<speak>
<prosody rate="95%">
Следующая задача — канализация.
<break time="700ms"/>
Клиент говорит: <emphasis level="moderate">нужно подключить санузел в подвальном помещении.</emphasis>
<break time="900ms"/>
Уточните, есть ли твёрдые включения, нужен ли измельчитель и на какую высоту необходимо поднять стоки.
<break time="800ms"/>
Только после этого можно выбирать канализационный насос.
</prosody>
</speak>
""", "True/False: санузел ниже канализации может требовать канализационный насос."),
        Slide(8, "Отопление", "Голос клиента: на втором этаже батареи плохо прогреваются. Не торопитесь менять насос. Сначала выясните тип системы, площадь дома и работает ли существующий циркуляционный насос.", """<speak>
<prosody rate="95%">
Теперь рассмотрим систему отопления.
<break time="700ms"/>
Клиент говорит: <emphasis level="moderate">на втором этаже батареи плохо прогреваются.</emphasis>
<break time="900ms"/>
Не торопитесь менять насос.
<break time="600ms"/>
Сначала выясните, какая система отопления установлена, какова площадь дома и работает ли существующий циркуляционный насос.
<break time="900ms"/>
Иногда причина находится совсем в другом месте.
</prosody>
</speak>
""", "Single Choice: что проверить первым? Ответ: систему и работу существующего насоса."),
        Slide(9, "Повышение давления", "Голос клиента: из душа течёт очень слабая струя. Нужно выяснить, проблема постоянная или периодическая, квартира это или частный дом и какое давление на вводе.", """<speak>
<prosody rate="95%">
Ещё одна распространённая задача — повышение давления.
<break time="700ms"/>
Клиент говорит: <emphasis level="moderate">из душа течёт очень слабая струя.</emphasis>
<break time="1000ms"/>
Не спешите рекомендовать насос.
<break time="600ms"/>
Выясните, постоянная это проблема или нет, квартира это или частный дом и какое давление на вводе.
<break time="900ms"/>
Только после этого принимайте решение.
</prosody>
</speak>
""", "Drag & Drop: проблема и группа оборудования."),
        Slide(10, "Пять вопросов продавца", "Перед подбором любого насоса задайте пять вопросов: что необходимо сделать, откуда берётся вода, куда её нужно подать, какая это вода и как будет работать система.", """<speak>
<prosody rate="95%">
Перед подбором любого насоса задайте клиенту пять вопросов.
<break time="700ms"/>
Первый. Что необходимо сделать?
<break time="500ms"/>
Второй. Откуда берётся вода?
<break time="500ms"/>
Третий. Куда необходимо её подать?
<break time="500ms"/>
Четвёртый. Какая это вода?
<break time="500ms"/>
Пятый. Как будет работать система?
<break time="900ms"/>
Если вы получили ответы на эти вопросы, подбор оборудования станет значительно точнее.
</prosody>
</speak>
""", "Drag the Words: задача, источник, назначение."),
        Slide(11, "Практический кейс", "Клиент говорит: после сильного дождя затопило подвал. Вода чистая. Нужно быстро её удалить. Правильное направление — дренажный насос.", """<speak>
<prosody rate="95%">
Проверим, как вы усвоили материал.
<break time="700ms"/>
Клиент говорит. После сильного дождя затопило подвал.
<break time="500ms"/>
Вода чистая.
<break time="500ms"/>
Её необходимо быстро удалить.
<break time="1500ms"/>
Подумайте, <break time="2500ms"/> какой тип насоса потребуется.
<break time="1500ms"/>
Правильный ответ — дренажный насос.
</prosody>
</speak>
""", "Single Choice Set: какой насос нужен? Ответ: дренажный."),
        Slide(12, "Итоги урока", "Сначала определите задачу клиента. Затем выберите группу насосов. И только после этого подберите конкретную модель JEMIX.", """<speak>
<prosody rate="95%">
Подведём итог урока.
<break time="700ms"/>
Теперь вы знаете, где применяются насосы Джемикс.
<break time="700ms"/>
Запомните главное правило.
<break time="600ms"/>
Сначала — задача клиента.
<break time="500ms"/>
Затем — группа насосов.
<break time="500ms"/>
И только после этого — конкретная модель.
<break time="1000ms"/>
Именно этот алгоритм мы будем использовать во всех следующих уроках.
</prosody>
</speak>
""", "Summary slide."),
    ]
    quiz = """lesson: 1.2
title: Где применяются насосы JEMIX
questions:
  - type: single_choice
    title: Что покупает клиент?
    options:
      - text: Самую мощную модель
        correct: false
      - text: Решение своей задачи
        correct: true
      - text: Самый дорогой насос
        correct: false
    feedback: Клиент чаще всего покупает решение проблемы, а не конкретную модель.
  - type: matching
    title: Соотнесите фразу клиента и задачу
    pairs:
      - left: Затопило подвал
        right: Откачка воды
      - left: Слабый напор
        right: Повышение давления
      - left: Нужно поливать участок
        right: Полив
      - left: Санузел в подвале
        right: Канализация
"""
    return LessonPreset("module-01", "lesson-1.2", "Где применяются насосы JEMIX", "Научиться определять задачу клиента по его фразе.", "Сначала задача клиента, затем группа насосов, и только потом модель JEMIX.", slides, quiz)


def lesson_1_3() -> LessonPreset:
    raw = [
        ("Что происходит внутри насоса?", "Насос передаёт воде энергию. За счёт этой энергии вода начинает двигаться по трубопроводу."),
        ("Три главные детали", "Двигатель создаёт вращение. Вал передаёт вращение рабочему колесу. Рабочее колесо передаёт энергию воде."),
        ("Рабочее колесо", "Рабочее колесо захватывает воду лопатками и направляет её к выходу из насоса."),
        ("Корпус насоса", "Корпус направляет поток воды и помогает снизить потери энергии."),
        ("Откуда появляется давление", "Насос передаёт воде энергию. Благодаря этому вода проходит по трубам и поступает к потребителю."),
        ("Почему нельзя включать насос без воды", "Работа без воды называется сухим ходом. Она может привести к перегреву и поломке."),
        ("Что такое расход", "Расход показывает, сколько воды насос способен подать за определённое время."),
        ("Что такое напор", "Напор показывает, как насос преодолевает высоту, расстояние и сопротивление системы."),
        ("Почему насос шумит", "Причиной может быть воздух, сухой ход, износ, загрязнение рабочего колеса или неправильная установка."),
        ("Частые ошибки", "Насос нельзя выбирать только по мощности. Его подбирают под задачу и условия работы."),
        ("Практический тренажёр", "На разрезе насоса нужно найти двигатель, вал, рабочее колесо и корпус."),
        ("Итоги", "Насос передаёт воде энергию, создаёт поток и помогает получить нужный расход и напор."),
    ]
    slides = [Slide(i + 1, title, body, ssml(title, body), "") for i, (title, body) in enumerate(raw)]
    quiz = """lesson: 1.3
title: Как устроен насос и почему он качает воду
questions:
  - type: single_choice
    title: Что делает рабочее колесо?
    options:
      - text: Передаёт энергию воде
        correct: true
      - text: Измеряет давление
        correct: false
      - text: Отключает насос
        correct: false
    feedback: Рабочее колесо вращается и передаёт воде энергию.
  - type: true_false
    title: Насос можно долго включать без воды.
    correct: false
    feedback: Работа без воды называется сухим ходом и может привести к поломке.
"""
    return LessonPreset("module-01", "lesson-1.3", "Как устроен насос и почему он качает воду", "Понять принцип работы насоса простыми словами.", "Насос передаёт воде энергию с помощью рабочего колеса.", slides, quiz)


PRESETS: Dict[str, LessonPreset] = {
    "module-01/lesson-1.2": lesson_1_2(),
    "module-01/lesson-1.3": lesson_1_3(),
}


def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        print(f"skip existing: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"write: {path}")


def render_lesson_md(preset: LessonPreset) -> str:
    parts = [
        f"# {preset.title}",
        "",
        "## Цель урока",
        preset.goal,
        "",
        "## Основная мысль",
        preset.main_idea,
        "",
        "## Слайды",
    ]
    for slide in preset.slides:
        parts += ["", f"### Слайд {slide.number:02d}. {slide.title}", slide.body]
        if slide.h5p:
            parts += ["", f"**H5P:** {slide.h5p}"]
    return "\n".join(parts)


def render_lesson_yml(module_slug: str, lesson_slug: str, preset: LessonPreset) -> str:
    return f"""module: {module_to_number(module_slug)}
lesson: {slug_to_number(lesson_slug)}
title: {preset.title}
status: draft
slides: {len(preset.slides)}
source: scripts/generate_lesson.py
"""


def render_notes_md(preset: LessonPreset) -> str:
    return f"""# Notes — {preset.title}

## Методика

Урок объясняет тему через реальные задачи клиента и простые технические образы.

## Главная мысль

{preset.main_idea}

## Что проверить после прохождения

- слушатель понимает, зачем нужен урок;
- слушатель может объяснить тему простыми словами;
- слушатель применяет материал к реальной ситуации клиента.
"""


def render_images_md(preset: LessonPreset) -> str:
    lines = [f"# Image prompts — {preset.title}", ""]
    for slide in preset.slides:
        lines += [f"## Slide {slide.number:02d} — {slide.title}", "", f"Иллюстрация в едином стиле JEMIX Academy: {slide.title.lower()}. Чистый технический стиль, белый фон, синие акценты JEMIX, понятные стрелки и минимальный текст.", ""]
    return "\n".join(lines)


def render_voice_qa(preset: LessonPreset) -> str:
    rows = "\n".join([f"| {s.number:02d} | tts-test-needed |" for s in preset.slides])
    return f"""# Voice QA — {preset.title}

## Проверить

- [ ] Темп речи одинаковый.
- [ ] Паузы естественные.
- [ ] Нет сложных длинных фраз.
- [ ] Все MP3 прослушаны полностью.
- [ ] Ударения проверены.

## Статус по слайдам

| Слайд | Статус |
|---:|---|
{rows}
"""


def render_pronunciation() -> str:
    return """# Pronunciation dictionary

JEMIX — Джемикс
SaluteSpeech — Салют Спич
H5P — эйч-пять-пи
SSML — эс-эс-эм-эл
MP3 — эм-пэ-три
сухой ход — сухой ход
рабочее колесо — рабочее колесо
расход — расход
напор — напор
"""


def generate(module_slug: str, lesson_slug: str, force: bool) -> None:
    key = f"{module_slug}/{lesson_slug}"
    if key not in PRESETS:
        known = ", ".join(sorted(PRESETS.keys()))
        raise SystemExit(f"No preset for {key}. Known presets: {known}")

    preset = PRESETS[key]
    academy_dir = Path("academy") / module_slug / lesson_slug
    voice_dir = Path("voice/modules") / module_slug / lesson_slug

    write_file(academy_dir / "lesson.md", render_lesson_md(preset), force)
    write_file(academy_dir / "lesson.yml", render_lesson_yml(module_slug, lesson_slug, preset), force)
    write_file(academy_dir / "quiz.yml", preset.quiz_yml, force)
    write_file(academy_dir / "notes.md", render_notes_md(preset), force)
    write_file(academy_dir / "images.md", render_images_md(preset), force)
    write_file(academy_dir / "README.md", f"# {preset.title}\n\nСтатус: draft.\n", force)
    (academy_dir / "assets").mkdir(parents=True, exist_ok=True)

    for slide in preset.slides:
        write_file(voice_dir / f"slide{slide.number:02d}.md", f"# Slide {slide.number:02d} — {slide.title}\n\n{slide.body}\n", force)
        write_file(voice_dir / f"slide{slide.number:02d}.ssml", slide.ssml, force)

    write_file(voice_dir / "voice_qa.md", render_voice_qa(preset), force)
    write_file(voice_dir / "pronunciation_dictionary.md", render_pronunciation(), force)

    print("Done.")
    print(f"Next: python scripts/salute_tts_v2.py {voice_dir}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("module_slug", help="module-01")
    parser.add_argument("lesson_slug", help="lesson-1.2")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    args = parser.parse_args()
    generate(args.module_slug, args.lesson_slug, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
