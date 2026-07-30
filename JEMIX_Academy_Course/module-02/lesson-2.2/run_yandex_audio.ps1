$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (!(Test-Path ".env")) { Copy-Item ".env.example" ".env"; Write-Host "Fill .env and run again."; exit 1 }
Get-Content ".env" | ForEach-Object {
  $line = $_.Trim()
  if ($line -and !$line.StartsWith("#") -and $line.Contains("=")) {
    $parts = $line.Split("=", 2)
    [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
  }
}
python .\generate_yandex_audio.py --voice ermil --emotion good --speed 1.0 --overwrite
