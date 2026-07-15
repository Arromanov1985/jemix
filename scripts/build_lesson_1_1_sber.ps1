$ErrorActionPreference = "Stop"

Write-Host "JEMIX Academy: preparing SSML for lesson 1.1..." -ForegroundColor Cyan
python scripts/prepare_lesson_1_1_ssml.py

Write-Host "Generating MP3 with SaluteSpeech..." -ForegroundColor Cyan
python scripts/salute_tts_v2.py voice/modules/module-01/lesson-1.1

$audioDir = "voice/modules/module-01/lesson-1.1/audio"
$missing = @()
1..20 | ForEach-Object {
    $name = "slide{0:D2}.mp3" -f $_
    $path = Join-Path $audioDir $name
    if (-not (Test-Path $path) -or (Get-Item $path).Length -lt 1024) {
        $missing += $name
    }
}

if ($missing.Count -gt 0) {
    throw "Missing or invalid MP3 files: $($missing -join ', ')"
}

Write-Host "Done: 20 MP3 files generated in $audioDir" -ForegroundColor Green
