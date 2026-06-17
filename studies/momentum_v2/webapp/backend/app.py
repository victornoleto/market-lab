"""FastAPI app for the momentum_v2 portfolio web-app.

Serves the portfolio_export.py snapshot (per-strategy holdings/history/contribution/
series + headline metrics) and the methodology/explanation content. Research-only;
every strategy view carries the survivorship disclaimer.

Run (after `uv pip install -e '.[webapp]'` and exporting a window):
    uv run uvicorn studies.momentum_v2.webapp.backend.app:app --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from studies.momentum_v2.webapp.backend import data
from studies.momentum_v2.webapp.backend.models import (
    ContributionRow,
    CurrentPortfolio,
    HistoryEvent,
    IndexEntry,
    StrategyIndex,
)

app = FastAPI(title="momentum_v2 portfolio", version="0.1.0",
              description="Research-only momentum portfolio comparison & tracking (promotion_eligible=false).")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"],
)

DEFAULT_UNIVERSE = "us_stocks"


def _resolve_window(universe: str, window: str | None) -> str:
    if window:
        return window
    try:
        windows = data.available_windows(universe)
    except ValueError as exc:
        raise HTTPException(400, "invalid universe") from exc
    if not windows:
        raise HTTPException(404, f"no exported portfolio for universe '{universe}'")
    return windows[0]


def _guard(fn, *args):
    try:
        return fn(*args)
    except FileNotFoundError as exc:
        raise HTTPException(404, f"not found: {Path(str(exc)).name}") from exc
    except ValueError as exc:  # rejected path component (traversal attempt)
        raise HTTPException(400, "invalid parameter") from exc


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/methodologies")
def methodologies() -> dict:
    return data.METHODOLOGIES


@app.get("/api/windows")
def windows(universe: str = DEFAULT_UNIVERSE) -> dict:
    return {"universe": universe, "windows": data.available_windows(universe)}


@app.get("/api/strategies", response_model=StrategyIndex)
def strategies(universe: str = DEFAULT_UNIVERSE, window: str | None = None) -> dict:
    return _guard(data.load_index, universe, _resolve_window(universe, window))


@app.get("/api/strategies/{name}")
def strategy_detail(name: str, universe: str = DEFAULT_UNIVERSE, window: str | None = None) -> dict:
    return _guard(data.load_artifact, universe, _resolve_window(universe, window), name, "meta.json")


@app.get("/api/strategies/{name}/portfolio/current", response_model=CurrentPortfolio)
def current(name: str, universe: str = DEFAULT_UNIVERSE, window: str | None = None) -> dict:
    return _guard(data.load_artifact, universe, _resolve_window(universe, window), name, "current.json")


@app.get("/api/strategies/{name}/portfolio/history", response_model=list[HistoryEvent])
def history(name: str, universe: str = DEFAULT_UNIVERSE, window: str | None = None) -> list:
    return _guard(data.load_artifact, universe, _resolve_window(universe, window), name, "history.json")


@app.get("/api/strategies/{name}/contribution", response_model=list[ContributionRow])
def contribution(name: str, universe: str = DEFAULT_UNIVERSE, window: str | None = None) -> list:
    return _guard(data.load_artifact, universe, _resolve_window(universe, window), name, "contribution.json")


@app.get("/api/strategies/{name}/series")
def series(name: str, universe: str = DEFAULT_UNIVERSE, window: str | None = None) -> list:
    return _guard(data.load_series, universe, _resolve_window(universe, window), name)


@app.get("/api/compare")
def compare(names: str = Query(..., description="comma-separated strategy names"),
            universe: str = DEFAULT_UNIVERSE, window: str | None = None) -> dict:
    win = _resolve_window(universe, window)
    wanted = [n for n in (s.strip() for s in names.split(",")) if n]
    out = {"universe": universe, "window": win, "strategies": [], "series": {}}
    for name in wanted:
        try:
            out["strategies"].append(data.load_artifact(universe, win, name, "meta.json"))
            out["series"][name] = data.load_series(universe, win, name)
        except (FileNotFoundError, ValueError):  # missing or unsafe name -> skip
            continue
    if not out["strategies"]:
        raise HTTPException(404, "none of the requested strategies were found")
    return out


# Serve the built SPA (frontend/dist) when present; API routes above take precedence.
_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if _DIST.exists():
    app.mount("/", StaticFiles(directory=str(_DIST), html=True), name="spa")
