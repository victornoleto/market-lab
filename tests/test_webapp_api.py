"""API tests for the momentum_v2 portfolio web-app.

Skips entirely when the optional ``[webapp]`` extra (fastapi/httpx) is absent, so
the core 975-test baseline is unaffected. Uses a synthetic exported snapshot via
the ``MOMENTUM_WEBAPP_UNIVERSES`` override.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

REPO_ROOT = Path(__file__).resolve().parents[1]
for _c in (REPO_ROOT, REPO_ROOT / "src"):
    if str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

UNIVERSE, WINDOW, STRAT = "us_stocks", "from_1990", "momv2_demo_raw_lb6_top5_reb3_off0"


@pytest.fixture()
def client(tmp_path, monkeypatch):
    pdir = tmp_path / UNIVERSE / WINDOW / "portfolio" / STRAT
    pdir.mkdir(parents=True)
    (pdir.parent / "index.json").write_text(json.dumps({
        "universe": UNIVERSE, "window": WINDOW, "benchmark": "SPY", "disclaimer": "research-only",
        "strategies": [{"name": STRAT, "mechanism": "raw_13612", "top_n": 5, "rebalance_months": 3,
                        "as_of": "2026-05-31", "cagr": 0.12, "mdd": -0.3, "sharpe": 0.8,
                        "gate_pass": False, "kind": "broad"}],
    }))
    (pdir / "meta.json").write_text(json.dumps({"name": STRAT, "mechanism": "raw_13612", "top_n": 5,
        "rebalance_months": 3, "weight_mode": "equal", "metrics": {"cagr": 0.12}, "gate_verdict": None,
        "promotion_eligible": False, "disclaimer": "research-only", "as_of": "2026-05-31"}))
    (pdir / "current.json").write_text(json.dumps({"as_of": "2026-05-31",
        "holdings": [{"ticker": "AAA", "weight": 0.5}, {"ticker": "BBB", "weight": 0.5}]}))
    (pdir / "history.json").write_text(json.dumps([
        {"date": "2026-04-30", "holdings": [{"ticker": "AAA", "weight": 1.0}], "entered": ["AAA"], "exited": []},
        {"date": "2026-05-31", "holdings": [{"ticker": "AAA", "weight": 0.5}, {"ticker": "BBB", "weight": 0.5}],
         "entered": ["BBB"], "exited": []}]))
    (pdir / "contribution.json").write_text(json.dumps([
        {"ticker": "AAA", "contribution": 0.08, "last_weight": 0.5},
        {"ticker": "BBB", "contribution": 0.04, "last_weight": 0.5}]))
    (pdir / "series.csv").write_text(
        "date,ret_after_tax,equity_after_tax,ret_gross,equity_gross,spy_ret,spy_equity\n"
        "2026-05-29,0.0,1.0,0.0,1.0,0.0,1.0\n2026-05-30,0.01,1.01,0.012,1.012,0.005,1.005\n")

    monkeypatch.setenv("MOMENTUM_WEBAPP_UNIVERSES", str(tmp_path))
    from fastapi.testclient import TestClient

    from studies.momentum_v2.webapp.backend.app import app
    return TestClient(app)


def test_health_and_methodologies(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    meth = client.get("/api/methodologies").json()
    assert "rolling_rel_score" in meth["scoring"] and "score_modes" in meth and "gates" in meth


def test_windows_and_index(client):
    assert client.get(f"/api/windows?universe={UNIVERSE}").json()["windows"] == [WINDOW]
    idx = client.get("/api/strategies").json()
    assert idx["benchmark"] == "SPY" and idx["strategies"][0]["name"] == STRAT


def test_strategy_detail_and_portfolio(client):
    assert client.get(f"/api/strategies/{STRAT}").json()["mechanism"] == "raw_13612"
    cur = client.get(f"/api/strategies/{STRAT}/portfolio/current").json()
    assert cur["as_of"] == "2026-05-31" and len(cur["holdings"]) == 2
    hist = client.get(f"/api/strategies/{STRAT}/portfolio/history").json()
    assert hist[1]["entered"] == ["BBB"]
    contrib = client.get(f"/api/strategies/{STRAT}/contribution").json()
    assert contrib[0]["ticker"] == "AAA"
    ser = client.get(f"/api/strategies/{STRAT}/series").json()
    assert ser[-1]["spy_equity"] == 1.005


def test_compare_and_404(client):
    cmp = client.get(f"/api/compare?names={STRAT},nope").json()
    assert len(cmp["strategies"]) == 1 and STRAT in cmp["series"]
    assert client.get("/api/strategies/does_not_exist").status_code == 404
    assert client.get("/api/compare?names=nope1,nope2").status_code == 404


def test_path_traversal_rejected(client):
    # unsafe window/universe query params are rejected with 400 (no file read)
    assert client.get(f"/api/strategies/{STRAT}?window=../../etc").status_code == 400
    assert client.get("/api/strategies?universe=..%2f..").status_code == 400
    assert client.get(f"/api/strategies/{STRAT}/series?window=..%2f..%2f..").status_code == 400
    # data layer rejects an unsafe strategy name before touching the filesystem
    from studies.momentum_v2.webapp.backend import data as d
    with pytest.raises(ValueError):
        d.load_artifact("us_stocks", "from_1990", "../../../../etc/passwd", "meta.json")
