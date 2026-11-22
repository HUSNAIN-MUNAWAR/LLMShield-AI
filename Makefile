.PHONY: setup install migrate migration reset-db seed backend worker frontend dev docker-up docker-down scan-demo scan-demo-async animation ci-scan reports screenshots test test-backend test-frontend validate secret-scan run-all-checks clean
setup: install
install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
migrate:
	cd backend && alembic upgrade head
migration:
	cd backend && alembic revision --autogenerate -m "schema update"
reset-db:
	rm -f backend/llmshield.db llmshield.db
seed:
	python scripts/seed_demo.py
backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
worker:
	cd backend && python -m app.workers.worker
frontend:
	cd frontend && npm run dev
dev:
	@echo "Run make backend and make frontend in separate terminals."
docker-up:
	docker compose up --build
docker-down:
	docker compose down
scan-demo:
	python scripts/run_demo_scan.py
scan-demo-async:
	SCAN_EXECUTION_MODE=async python scripts/run_demo_scan.py
animation:
	python scripts/generate_security_animation.py
ci-scan:
	cd backend && python -m app.cli ci-scan --target mock-safe --attack-packs prompt_injection,jailbreak,rag_poisoning --fail-on high --output ../sample_outputs/reports/ci_report.json
reports:
	python scripts/generate_sample_reports.py
screenshots:
	python scripts/capture_real_screenshots.py --real
test: test-backend test-frontend
test-backend:
	cd backend && pytest -q
test-frontend:
	cd frontend && npm run typecheck && npm run build
validate:
	python scripts/validate_project.py
secret-scan:
	python scripts/secret_scan.py
run-all-checks:
	python scripts/run_all_checks.py
clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf frontend/.next frontend/node_modules .pytest_cache backend/.pytest_cache
	rm -f .env backend/llmshield.db llmshield.db
