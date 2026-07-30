# JEMIX Academy — урок 3.1 — аудио через Yandex SpeechKit

Озвучиваются слайды 01–20 и 26.
Слайды 21–25 — квиз, поэтому намеренно оставлены без аудио.

## Запуск в VS Code / PowerShell

1. Откройте распакованную папку в VS Code.
2. Выполните:

```powershell
Copy-Item .\.env.example .\.env -Force
notepad .\.env
```

3. Вставьте корректные значения:

```text
YANDEX_API_KEY=...
YANDEX_FOLDER_ID=...
```

Важно: `YANDEX_FOLDER_ID` должен принадлежать тому же сервисному аккаунту, для которого выдан API-ключ.

4. Запустите:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_yandex_audio.ps1
```

Или напрямую:

```powershell
python -m pip install requests python-dotenv
python .\generate_yandex_audio.py --voice ermil --emotion good --speed 1.0 --overwrite
```

Готовые MP3 появятся в папке `audio`.
