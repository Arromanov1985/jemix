$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path -LiteralPath ".env")) {
    Copy-Item -LiteralPath ".env.example" -Destination ".env"
    Write-Host "Created .env. Fill YANDEX_API_KEY and YANDEX_FOLDER_ID, then run again."
    notepad .env
    exit 0
}

python -m pip install requests python-dotenv
python .\generate_yandex_audio.py --voice ermil --emotion good --speed 1.0 --overwrite
