# H5P sources

Этот каталог хранит исходники уроков JEMIX Academy для последующей сборки в отдельные `.h5p` файлы.

## Принцип

- один YAML-файл = один урок;
- один урок = один H5P Course Presentation;
- H5P-файлы не редактируются вручную, они собираются из исходников;
- картинки и схемы должны храниться как исходники в `assets/` или генерироваться сборщиком.

## Текущий формат урока

```yaml
title: "1.2 Где применяются насосы"
module: 1
lesson: 2
duration_min: 20
slides:
  - type: text
    title: "Цели обучения"
    body: "..."
  - type: quiz
    question: "Что делает насос?"
    answers:
      - "Передает жидкости энергию"
      - "Создает воду"
    correct: 0
```

## Сборка

Плановая команда:

```bash
python builder/h5p_builder.py h5p-src/module-01/lesson-01.yml
```

Результат должен попадать в:

```text
output/h5p/module-01/lesson-01.h5p
```
