# JEMIX Academy — урок 3.3 — Yandex SpeechKit

Пакет построен на рабочем скрипте озвучки урока 3.2.

## Параметры

- голос: `ermil`
- эмоциональная окраска: `good`
- скорость: `1.0`
- формат: `mp3`
- API: Yandex SpeechKit v1 REST

## Запуск в PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
code .env
```

Проверка первого слайда обычным текстом:

```powershell
py .\yandex_tts.py --slide 1 --plain-text --overwrite
```

Если тест звучит правильно, генерация всех 28 файлов:

```powershell
py .\yandex_tts.py --plain-text --overwrite
```

SSML-режим оставлен как в уроке 3.2:

```powershell
py .\yandex_tts.py --slide 1 --overwrite
```

MP3 сохраняются в папке `audio`.
