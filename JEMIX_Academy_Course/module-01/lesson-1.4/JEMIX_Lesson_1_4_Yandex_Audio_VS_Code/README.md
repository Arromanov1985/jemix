# JEMIX Academy — урок 1.4: Yandex SpeechKit

Пакет содержит 20 дикторских сценариев, SSML и Python-код для генерации MP3 в Yandex SpeechKit.

## Быстрый запуск в VS Code / PowerShell

1. Распакуйте архив и откройте папку в VS Code.
2. Откройте Terminal → New Terminal.
3. Выполните:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_yandex_audio.ps1
```

Скрипт запросит API-ключ и Folder ID, создаст `.venv`, установит `requests` и сгенерирует `audio\slide01.mp3` … `audio\slide20.mp3`.

## Ручной запуск

```powershell
$env:YANDEX_API_KEY="НОВЫЙ_API_КЛЮЧ"
$env:YANDEX_FOLDER_ID="ВАШ_FOLDER_ID"
python -m pip install -r requirements.txt
python generate_yandex_audio.py --overwrite
```

Один слайд:

```powershell
python generate_yandex_audio.py --slide 7 --overwrite
```

## Настройки

- голос: `ermil`
- амплуа: `good`
- скорость: `0.95`
- формат: MP3
- целевая длительность: около 30–40 секунд на учебный экран

## Важно

Не храните настоящий API-ключ в коде, GitHub или архиве. Используйте переменную окружения `YANDEX_API_KEY`.
