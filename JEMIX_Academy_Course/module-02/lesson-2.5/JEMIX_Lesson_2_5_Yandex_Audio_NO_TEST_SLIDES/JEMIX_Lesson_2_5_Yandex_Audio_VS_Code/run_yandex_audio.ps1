$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "JEMIX Academy - Lesson 2.5 audio generation"
Write-Host "Slides with audio: 01-20 and 26. Slides 21-25 are intentionally skipped."

python -m pip install requests python-dotenv

if (Test-Path "$PSScriptRoot\audio") {
    Get-ChildItem "$PSScriptRoot\audio\slide*.mp3" -ErrorAction SilentlyContinue | Remove-Item -Force
}

python "$PSScriptRoot\generate_yandex_audio.py" --voice ermil --emotion good --speed 1.0 --overwrite
