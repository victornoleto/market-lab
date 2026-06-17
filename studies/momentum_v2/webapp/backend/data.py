"""Read the portfolio_export.py artifacts off disk for the API.

The exported snapshot lives under ``studies/momentum_v2/universes/<u>/<window>/portfolio/``.
Set ``MOMENTUM_WEBAPP_UNIVERSES`` to point the API at a different universes root
(used by tests). Every loader raises ``FileNotFoundError`` for a missing artifact,
which the app maps to HTTP 404.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pandas as pd

_DEFAULT_UNIVERSES = Path(__file__).resolve().parents[2] / "universes"


def universes_root() -> Path:
    return Path(os.environ.get("MOMENTUM_WEBAPP_UNIVERSES", _DEFAULT_UNIVERSES))


# universe/window/strategy names are alphanumerics + _ . - (no slashes, no ``..``);
# anything else is rejected before it can touch the filesystem.
_SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.\-]*$")


def _safe(component: str) -> str:
    if not isinstance(component, str) or component in (".", "..") or not _SAFE_COMPONENT.match(component):
        raise ValueError(f"invalid path component: {component!r}")
    return component


def _within(*parts: str) -> Path:
    """Resolve universes_root()/parts after validating each part and confirming the
    result stays inside the root — defends the deployed API against path traversal
    via the universe/window/name parameters. Raises ValueError on any escape."""
    for part in parts:
        _safe(part)
    base = universes_root().resolve()
    full = base.joinpath(*parts).resolve()
    if not full.is_relative_to(base):
        raise ValueError("path escapes universes root")
    return full


def _portfolio_dir(universe: str, window: str) -> Path:
    return _within(universe, window, "portfolio")


def _read_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def available_windows(universe: str) -> list[str]:
    """Windows that have an exported portfolio index, newest-year first."""
    _safe(universe)
    root = universes_root() / universe
    if not root.exists():
        return []
    windows = [p.name for p in root.iterdir() if (p / "portfolio" / "index.json").exists()]
    return sorted(windows, reverse=True)


def load_index(universe: str, window: str) -> dict:
    return _read_json(_within(universe, window, "portfolio", "index.json"))


def load_artifact(universe: str, window: str, name: str, filename: str):
    return _read_json(_within(universe, window, "portfolio", name, filename))


def load_series(universe: str, window: str, name: str) -> list[dict]:
    path = _within(universe, window, "portfolio", name, "series.csv")
    if not path.exists():
        raise FileNotFoundError(str(path))
    df = pd.read_csv(path)
    return df.where(pd.notna(df), None).to_dict(orient="records")


# --- methodology / explanation content (the "explicação" feature) ----------

DISCLAIMER = (
    "Research-only, promotion_eligible=false. The Postgres+yfinance universe with "
    "survivorship filters mitigates but does not eliminate bias; fully delisted names "
    "are mostly missing, so historical screens stay inflated. Main metrics are after "
    "Brazil's 15% annual realized-gain tax, gross of transaction costs. Not investment advice."
)

SCORE_MODES = {
    "raw_13612": "Equal-weighted multi-window return momentum (1/3/6/12-month lookbacks) "
                 "[stocks_on_the_move, p.60].",
    "mom_12_1": "12-month momentum skipping the most recent month (reversal-robust).",
    "vol_adjusted_13612": "raw_13612 divided by realized volatility — risk-normalized momentum "
                          "[systematic_trading, p.137-148].",
    "clenow_trend": "Rolling exponential-regression slope × R² — rewards smooth trends over noisy "
                    "jumps [stocks_on_the_move, p.70-77, p.98].",
    "composite_mom_lowvol": "70/30 cross-sectional rank blend of momentum and low volatility "
                            "[systematic_trading, p.137-148].",
}

METHODOLOGIES = {
    "disclaimer": DISCLAIMER,
    "score_modes": SCORE_MODES,
    "scoring": (
        "Finalists are chosen by the rolling-dominance lens (rolling_rel_score): the weighted "
        "mean, across 3/5/10/15/20-year rolling windows, of the share of days the reset relative "
        "equity curve equity/equity_benchmark stays at or above 1.0 [testing_tuning, p.327-335]. "
        "This rewards durable, broad-based outperformance over a single lucky end-point."
    ),
    "weighting": "equal = 1/N per name; inverse_vol = weights ∝ 1/realized-vol of each holding.",
    "rebalance": "Calendar-month cadence; positions apply only to subsequent daily returns to avoid "
                 "look-ahead [advances_fin_ml, p.31-34].",
    "gates": {
        "summary": "Hard gates (zero bypass) applied to the small validate finalist set "
                   "[advances_fin_ml, p.208-211, p.273-275]. A FAIL is the honest, expected outcome "
                   "for a survivorship-biased screen.",
        "pbo": "Probability of Backtest Overfitting via CSCV < 0.5.",
        "dsr": "Deflated Sharpe Ratio p-value < 0.05 (corrects for multiple testing).",
        "wf": ">= 6 of 8 profitable walk-forward windows.",
        "bootstrap": "Stationary-block bootstrap CI-low on Sharpe > 0.",
        "xlib": "Vectorized vs holdings-loop CAGR agree within ±3pp (engine cross-check).",
    },
}
