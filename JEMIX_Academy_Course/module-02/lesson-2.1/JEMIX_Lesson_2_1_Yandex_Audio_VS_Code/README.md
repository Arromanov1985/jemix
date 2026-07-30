# JEMIX Academy — урок 2.1 — Yandex SpeechKit

## Запуск в VS Code
1. Распакуйте архив.
2. Откройте папку в VS Code.
3. Откройте PowerShell-терминал.
4. Выполните:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_yandex_audio.ps1
```

Скрипт запросит новый `YANDEX_API_KEY` и `YANDEX_FOLDER_ID`.
Готовые файлы появятся в папке `audio` как `slide01.mp3`–`slide20.mp3`.

## Один слайд
```powershell
$env:YANDEX_API_KEY="НОВЫЙ_КЛЮЧ"
$env:YANDEX_FOLDER_ID="ID_КАТАЛОГА"
.\.venv\Scripts\python.exe generate_yandex_audio.py --slide 7 --overwrite
```
