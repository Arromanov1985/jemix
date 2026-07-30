# JEMIX Academy — урок 3.2 — Yandex SpeechKit

Проект предназначен для запуска в VS Code на Windows.

## Параметры

- голос: `ermil`
- эмоциональная окраска: `good`
- скорость: `1.0`
- формат: `mp3`
- API: Yandex SpeechKit v1 REST

## Запуск в PowerShell

```powershell
cd JEMIX_VOICE_3_2_YANDEX_VS
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Откройте `.env` и вставьте `YANDEX_API_KEY` или `YANDEX_IAM_TOKEN`.

Тест одного слайда:

```powershell
py .\yandex_tts.py --slide 1 --overwrite
```

Генерация всех 28 файлов:

```powershell
py .\yandex_tts.py --overwrite
```

Если Яндекс отклонит SSML, временно проверьте обычный текст:

```powershell
py .\yandex_tts.py --slide 1 --plain-text --overwrite
```

## Результат

MP3 сохраняются в папке `audio`.


## Версия 30–40 секунд

Все 28 сценариев расширены до ориентировочной длительности 30–40 секунд при голосе `ermil`, скорости `1.0`. Для повторной генерации используйте `--overwrite`.
