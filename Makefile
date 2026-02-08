.PHONY: install dev sync lock lint type-check test test-cov fmt generate serve clean docker-up docker-down \
       frontend-install frontend-dev frontend-build frontend-lint start stop restart

# ---- Package Management (uv) ----
install:  ## Install production dependencies
	uv sync --no-dev

dev:  ## Install all dependencies including dev tools
	uv sync

sync:  ## Sync dependencies from lock file
	uv sync --frozen

lock:  ## Update lock file from pyproject.toml
	uv lock

upgrade:  ## Upgrade all dependencies
	uv lock --upgrade
	uv sync

add:  ## Add a dependency: make add pkg=httpx
	uv add $(pkg)

add-dev:  ## Add a dev dependency: make add-dev pkg=pytest
	uv add --dev $(pkg)

remove:  ## Remove a dependency: make remove pkg=httpx
	uv remove $(pkg)

# ---- Code Quality ----
lint:  ## Run linter
	uv run ruff check src/ tests/

lint-fix:  ## Run linter with auto-fix
	uv run ruff check --fix src/ tests/

fmt:  ## Format code
	uv run ruff format src/ tests/

type-check:  ## Run type checker
	uv run mypy src/worldmaker/

check: lint type-check  ## Run all checks

# ---- Testing ----
test:  ## Run tests
	uv run pytest

test-cov:  ## Run tests with coverage
	uv run pytest --cov=src/worldmaker --cov-report=html --cov-report=term-missing

test-fast:  ## Run tests without coverage
	uv run pytest --no-cov -x -q

# ---- Application ----
serve:  ## Start the API server
	uv run worldmaker serve --reload

generate:  ## Generate a sample ecosystem (small)
	uv run worldmaker generate --size small --format summary

generate-medium:  ## Generate a medium ecosystem and write to file
	uv run worldmaker generate --size medium -o ecosystem_medium.json

generate-large:  ## Generate a large ecosystem and write to file
	uv run worldmaker generate --size large -o ecosystem_large.json

info:  ## Show system info and backend availability
	uv run worldmaker info

# ---- Database ----
db-migrate:  ## Run database migrations
	uv run alembic upgrade head

db-revision:  ## Create a new migration: make db-revision msg="add users"
	uv run alembic revision --autogenerate -m "$(msg)"

db-downgrade:  ## Rollback last migration
	uv run alembic downgrade -1

# ---- Docker ----
docker-up:  ## Start all services
	docker compose up -d

docker-down:  ## Stop all services
	docker compose down

docker-rebuild:  ## Rebuild and restart
	docker compose up -d --build

docker-logs:  ## Tail logs for all services
	docker compose logs -f

docker-infra:  ## Start only infrastructure (no app)
	docker compose up -d postgres mongodb neo4j redis kafka zookeeper

# ---- Frontend ----
frontend-install:  ## Install frontend dependencies
	cd frontend && npm install

frontend-dev:  ## Start frontend dev server (port 3000)
	cd frontend && npm run dev

frontend-build:  ## Build frontend for production
	cd frontend && npm run build

frontend-lint:  ## Lint frontend code
	cd frontend && npm run lint

# ---- Full Stack ----
start:  ## Start everything (infra + worker + API + frontend)
	./start.sh

start-local:  ## Start API + frontend only (no Docker infra)
	./start.sh --no-infra

stop:  ## Stop everything
	./shutdown.sh

restart:  ## Restart everything
	./restart.sh

# ---- Cleanup ----
clean:  ## Remove build artifacts and caches
	rm -rf .venv __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
