# JEMIX Academy — урок 2.5

Пакет создаёт аудио через Yandex SpeechKit в VS Code.

Озвучиваются слайды:

- `slide01.mp3` — `slide20.mp3`
- `slide26.mp3`

Слайды `21–25` — итоговый тест, поэтому намеренно не озвучиваются.

## Запуск в PowerShell

```powershell
Copy-Item .\.env.example .\.env -Force
notepad .\.env
```

Заполните:

```text
YANDEX_API_KEY=...
YANDEX_FOLDER_ID=...
```

Запуск:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_yandex_audio.ps1
```

Или напрямую:

```powershell
python -m pip install requests python-dotenv
python .\generate_yandex_audio.py --voice ermil --emotion good --speed 1.0 --overwrite
```
