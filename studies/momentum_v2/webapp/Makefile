# momentum_v2 portfolio web-app. Run from this directory.
ROOT := $(shell git rev-parse --show-toplevel)
PY   := $(ROOT)/.venv/bin/python
APP  := studies.momentum_v2.webapp.backend.app:app

.PHONY: install build export backend frontend serve
install:                       ## install backend extra + frontend deps
	uv pip install --python $(PY) "fastapi>=0.110" "uvicorn[standard]>=0.29"
	npm --prefix frontend install

build:                         ## build the SPA into frontend/dist (served by FastAPI)
	npm --prefix frontend run build

export:                        ## (re)generate the portfolio snapshot for the default window
	cd $(ROOT) && $(PY) studies/momentum_v2/portfolio_export.py --universe us_stocks --start 1990-01-01

backend:                       ## dev backend with autoreload on :8000
	cd $(ROOT) && $(PY) -m uvicorn $(APP) --host 127.0.0.1 --port 8000 --reload

frontend:                      ## dev frontend with HMR on :5173 (proxies /api -> :8000)
	npm --prefix frontend run dev

serve: build                   ## production: one uvicorn process serving API + built SPA
	cd $(ROOT) && $(PY) -m uvicorn $(APP) --host 0.0.0.0 --port 8000
