# ── Stadium Sync — Makefile ──
# Common commands for development, testing, and deployment.

.PHONY: dev test test-all test-phase1 test-phase2 test-phase3 test-phase4 test-phase5 test-phase6 seed docker-up docker-down lint clean

# ── Development ──
dev:
	uvicorn app.main:app --reload --port 8000

# ── Testing ──
test:
	pytest tests/ -v --tb=short

test-all:
	pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

test-phase1:
	pytest tests/phase1_test_foundation.py -v --tb=short

test-phase2:
	pytest tests/phase2_test_auth.py -v --tb=short

test-phase3:
	pytest tests/phase3_test_navigation.py -v --tb=short

test-phase4:
	pytest tests/phase4_test_features.py -v --tb=short

test-phase5:
	pytest tests/phase5_test_realtime.py -v --tb=short

test-phase6:
	pytest tests/phase6_test_e2e.py -v --tb=short

# ── Database ──
seed:
	python scripts/seed_stadium_data.py && python scripts/generate_test_tickets.py

# ── Docker ──
docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-build:
	docker build -t stadium-sync-api ./backend

# ── Code Quality ──
lint:
	ruff check app/

# ── Cleanup ──
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
