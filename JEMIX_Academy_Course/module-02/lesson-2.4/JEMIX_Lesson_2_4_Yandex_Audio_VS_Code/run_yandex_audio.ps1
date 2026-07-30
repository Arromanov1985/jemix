$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Open .env, add YANDEX_API_KEY and YANDEX_FOLDER_ID, then run this file again."
    exit 1
}

python -m pip install -r .equirements.txt
python .\generate_yandex_audio.py --voice ermil --emotion good --speed 1.0 --overwrite
