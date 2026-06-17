# momentum_v2 portfolio web-app

Compare/explain the momentum_v2 strategies, show each strategy's **current portfolio**,
and visualize the **holdings history** (entries/exits, per-name contribution, equity/drawdown).

**Research-only, `promotion_eligible=false`.** Every strategy view carries the
survivorship disclaimer; this is a dissemination + personal-tracking tool, not advice.

## Architecture
- **Backend** — FastAPI (`backend/app.py`) serving the JSON the SPA needs. It reads the
  snapshot written by `studies/momentum_v2/portfolio_export.py` (per-strategy
  `current/history/contribution/series/meta` under
  `universes/<universe>/<window>/portfolio/`). Optional `[webapp]` extra (fastapi, uvicorn);
  it is **not** a runtime dep of the funnel or the test baseline.
- **Frontend** — React + Vite + uplot SPA (`frontend/`). Dark, minimal. In production
  FastAPI serves the built `frontend/dist` same-origin via `StaticFiles`.

## Data flow
```
run.py (broad→evolution→validate)  ->  results CSV/JSON  ->  portfolio_export.py  ->  portfolio/*.json
                                                                                          ^ FastAPI reads these
```

## Quick start (local)
```bash
# 1. produce data (from repo root) — funnel then export
.venv/bin/python studies/momentum_v2/run.py --universe us_stocks --start 1990-01-01 --phase broad     --cache-panels --jobs 16
.venv/bin/python studies/momentum_v2/run.py --universe us_stocks --start 1990-01-01 --phase evolution --cache-panels --jobs 16
.venv/bin/python studies/momentum_v2/run.py --universe us_stocks --start 1990-01-01 --phase validate   --cache-panels
.venv/bin/python studies/momentum_v2/portfolio_export.py --universe us_stocks --start 1990-01-01

# 2. install + run (from this webapp/ dir)
make install
make backend      # terminal A -> http://127.0.0.1:8000/api/health
make frontend     # terminal B -> http://127.0.0.1:5173  (proxies /api)
# or single production process serving API + built SPA:
make serve        # http://0.0.0.0:8000
```

## Endpoints
`GET /api/health` · `/api/methodologies` · `/api/windows` · `/api/strategies` ·
`/api/strategies/{name}` · `/api/strategies/{name}/portfolio/current` · `/portfolio/history` ·
`/api/strategies/{name}/contribution` · `/api/strategies/{name}/series` · `/api/compare?names=a,b`

## Deploy (dynamic server)
`make serve` runs one uvicorn process serving the API and the SPA. Put it behind your
existing reverse proxy / supervisor (bind `127.0.0.1:8000`, proxy a domain to it).
A `Dockerfile` is provided for a containerized build (see its header). Re-run the funnel
+ export to refresh the snapshot the app serves.
