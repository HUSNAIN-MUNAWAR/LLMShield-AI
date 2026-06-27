#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p evidence
if ! command -v docker >/dev/null 2>&1; then
  echo "NOT RUN: Docker CLI is not installed." | tee evidence/docker_smoke_result.txt
  exit 2
fi
docker compose config >/tmp/llmshield-compose-config.txt
docker compose up --build -d
cleanup(){ docker compose down; }
trap cleanup EXIT
for i in {1..60}; do
  if curl -fsS http://localhost:8000/health >/tmp/llmshield-health.json 2>/dev/null; then break; fi
  sleep 2
done
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:8000/api/attack-packs >/tmp/llmshield-attack-packs.json
curl -fsS http://localhost:3000 >/tmp/llmshield-frontend.html
echo "PASSED: docker compose config, backend health, attack packs, and frontend root responded." | tee evidence/docker_smoke_result.txt
