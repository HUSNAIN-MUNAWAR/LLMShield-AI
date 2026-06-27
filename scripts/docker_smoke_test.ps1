$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
New-Item -ItemType Directory -Force -Path evidence | Out-Null
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  "NOT RUN: Docker CLI is not installed." | Tee-Object -FilePath evidence/docker_smoke_result.txt
  exit 2
}
docker compose config | Out-File -Encoding utf8 evidence/docker_compose_config.txt
docker compose up --build -d
try {
  for ($i=0; $i -lt 60; $i++) {
    try { Invoke-WebRequest http://localhost:8000/health -UseBasicParsing | Out-Null; break } catch { Start-Sleep -Seconds 2 }
  }
  Invoke-WebRequest http://localhost:8000/health -UseBasicParsing | Out-Null
  Invoke-WebRequest http://localhost:8000/api/attack-packs -UseBasicParsing | Out-Null
  Invoke-WebRequest http://localhost:3000 -UseBasicParsing | Out-Null
  "PASSED: docker compose config, backend health, attack packs, and frontend root responded." | Tee-Object -FilePath evidence/docker_smoke_result.txt
} finally { docker compose down }
