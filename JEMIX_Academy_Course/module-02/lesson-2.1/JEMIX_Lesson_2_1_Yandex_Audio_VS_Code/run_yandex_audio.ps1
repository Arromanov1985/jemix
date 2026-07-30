$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not $env:YANDEX_API_KEY) {
    $env:YANDEX_API_KEY = Read-Host "Введите новый YANDEX_API_KEY"
}
if (-not $env:YANDEX_FOLDER_ID) {
    $env:YANDEX_FOLDER_ID = Read-Host "Введите YANDEX_FOLDER_ID"
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" generate_yandex_audio.py --voice ermil --emotion good --speed 0.95 --overwrite

Write-Host "Готово: $PSScriptRoot\audio" -ForegroundColor Green
