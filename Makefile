SHELL := /bin/bash

BUN ?= /home/oladapo/.bun/bin/bun
UV ?= uv
PYTHON ?= python3

.PHONY: help install dev dev-backend dev-frontend test test-backend build build-backend build-frontend check clean

help:
	@printf "\nKiniVideo commands\n\n"
	@printf "  make install        Install backend and frontend dependencies\n"
	@printf "  make dev            Run backend and frontend together with colored logs\n"
	@printf "  make dev-backend    Run only the FastAPI backend\n"
	@printf "  make dev-frontend   Run only the frontend dev server\n"
	@printf "  make test           Run backend tests\n"
	@printf "  make build          Build backend bytecode and frontend assets\n"
	@printf "  make check          Run tests and build\n"
	@printf "  make clean          Remove generated runtime and build artifacts\n\n"

install:
	$(UV) sync --dev
	$(BUN) install --cwd web

dev:
	@set -m; \
	( $(UV) run uvicorn main:app --reload --host 0.0.0.0 --port 8000 2>&1 | awk '{print "\033[1;34m[api]\033[0m " $$0; fflush()}' ) & api_pid=$$!; \
	( $(BUN) run --cwd web dev --host 0.0.0.0 2>&1 | awk '{print "\033[1;33m[web]\033[0m " $$0; fflush()}' ) & web_pid=$$!; \
	trap 'kill $$api_pid $$web_pid 2>/dev/null; wait $$api_pid $$web_pid 2>/dev/null' EXIT INT TERM; \
	wait $$api_pid $$web_pid

dev-backend:
	$(UV) run uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	$(BUN) run --cwd web dev --host 0.0.0.0

test: test-backend

test-backend:
	$(UV) run pytest

build: build-backend build-frontend

build-backend:
	$(UV) run $(PYTHON) -m compileall main.py api.py jobs.py pipeline.py models.py recipes.py repository.py source_adapters.py storage.py config.py

build-frontend:
	$(BUN) run --cwd web build

check: test build

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache var web/dist web/tsconfig.tsbuildinfo
