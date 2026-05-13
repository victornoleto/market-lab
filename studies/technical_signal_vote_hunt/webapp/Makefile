SHELL := /usr/bin/env bash

HOST ?= 127.0.0.1
API_PORT ?= 8765
WEB_PORT ?= 5173
FRONTEND_DIR := frontend
REPO_ROOT := ../../..

.PHONY: help install api frontend dev build clean

help:
	@printf "Available targets:\n"
	@printf "  make install   Install frontend dependencies\n"
	@printf "  make api       Run Python JSON API on $(HOST):$(API_PORT)\n"
	@printf "  make frontend  Run Vite dev server on $(HOST):$(WEB_PORT)\n"
	@printf "  make dev       Run API and frontend together\n"
	@printf "  make build     Build frontend production bundle\n"
	@printf "  make clean     Remove frontend build output\n"

install:
	cd $(FRONTEND_DIR) && npm install

api:
	cd $(REPO_ROOT) && uv run python -m studies.technical_signal_vote_hunt.webapp.api_server --host $(HOST) --port $(API_PORT)

frontend:
	cd $(FRONTEND_DIR) && npm run dev -- --host $(HOST) --port $(WEB_PORT)

dev:
	trap 'kill 0' INT TERM EXIT; \
	(cd $(REPO_ROOT) && uv run python -m studies.technical_signal_vote_hunt.webapp.api_server --host $(HOST) --port $(API_PORT)) & \
	for i in {1..60}; do \
		curl -fsS http://$(HOST):$(API_PORT)/api/health >/dev/null 2>&1 && break; \
		sleep 1; \
	done; \
	curl -fsS http://$(HOST):$(API_PORT)/api/health >/dev/null || { echo "API did not become ready on $(HOST):$(API_PORT)"; exit 1; }; \
	cd $(FRONTEND_DIR) && npm run dev -- --host $(HOST) --port $(WEB_PORT)

build:
	cd $(FRONTEND_DIR) && npm run build

clean:
	rm -rf $(FRONTEND_DIR)/dist
