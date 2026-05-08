"""Single source of truth for paths, cost models, and env-backed secrets.

All other shared/* modules import paths and constants from here. Per-system
state lives under STUDY_ROOT/data/{trades,catalog,ohlc}/<system_id>/ and
STUDY_ROOT/systems/<system_id>/<report>.md.

Citations:
- [carver_systematic_trading, p.185-188] — fixed commission dominates retail FX cost model
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

STUDY_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = STUDY_ROOT / "data"
TRADES_ROOT = DATA_ROOT / "trades"
CATALOG_ROOT = DATA_ROOT / "catalog"
OHLC_ROOT = DATA_ROOT / "ohlc"
SYSTEMS_ROOT = STUDY_ROOT / "systems"
ARCHIVE_ROOT = STUDY_ROOT / "_archive"
LOGS_PATH = STUDY_ROOT.parent.parent / "logs" / "myfxbook_reverse_engineering.log"

VENDOR_NAME = "HappyForex"
SCRAPE_RATE_LIMIT_MS = 400

# Pepperstone Razor 2025 cost model (pips, RT). Forward-looking — used as
# conservative cost overlay on observed gross pips. Source: pepperstone.com
# spreads page accessed 2025. Commission ≈ $7/lot RT ≈ 0.7 pips on majors.
PEPPERSTONE_SPREAD_PIPS: dict[str, float] = {
    "EURUSD": 0.13,
    "GBPUSD": 0.50,
    "USDCAD": 0.74,
    "USDCHF": 0.75,
    "EURGBP": 0.75,
    "EURCHF": 1.20,
}
PEPPERSTONE_COMMISSION_PIPS = 0.7


@dataclass(frozen=True)
class CostModel:
    """Per-pair RT pip cost = spread + commission. Override per system if needed."""

    spread_pips: dict[str, float]
    commission_pips: float

    def cost_for(self, symbol: str) -> float:
        return float(self.spread_pips.get(symbol, max(self.spread_pips.values()))) + self.commission_pips


def pepperstone_razor_2025() -> CostModel:
    return CostModel(spread_pips=dict(PEPPERSTONE_SPREAD_PIPS), commission_pips=PEPPERSTONE_COMMISSION_PIPS)


def trades_dir(system_id: int | str) -> Path:
    return TRADES_ROOT / str(system_id)


def trades_raw_dir(system_id: int | str) -> Path:
    return trades_dir(system_id) / "raw"


def trades_parquet_path(system_id: int | str) -> Path:
    return trades_dir(system_id) / "trades.parquet"


def trades_csv_path(system_id: int | str) -> Path:
    return trades_dir(system_id) / "trades.csv"


def system_report_dir(system_id: int | str) -> Path:
    return SYSTEMS_ROOT / str(system_id)


def system_info_json_path(system_id: int | str) -> Path:
    return system_report_dir(system_id) / "system_info.json"


def system_info_html_path(system_id: int | str) -> Path:
    return trades_dir(system_id) / "raw" / "system_info.html"


def sanity_report_path(system_id: int | str) -> Path:
    return system_report_dir(system_id) / "sanity.md"


def eda_report_path(system_id: int | str) -> Path:
    return system_report_dir(system_id) / "eda.md"


def gates_report_path(system_id: int | str) -> Path:
    return system_report_dir(system_id) / "gates.md"


@dataclass(frozen=True)
class MyFxBookSession:
    cookie: str
    csrf: str
    user_agent: str


def load_session(env_path: Path | None = None) -> MyFxBookSession:
    """Load MyFxBook browser-session cookies from .env (study-root level).

    .env keys: MYFXBOOK_COOKIE, MYFXBOOK_CSRF, MYFXBOOK_USER_AGENT.
    .env is gitignored at repo root (.env / .env.local patterns).
    """
    path = env_path or (STUDY_ROOT / ".env")
    if not path.exists():
        raise FileNotFoundError(f".env not found at {path} — re-export cookies from browser DevTools")
    pairs: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs[key.strip()] = value.strip().strip("'").strip('"')
    cookie = pairs.get("MYFXBOOK_COOKIE") or os.environ.get("MYFXBOOK_COOKIE", "")
    csrf = pairs.get("MYFXBOOK_CSRF") or os.environ.get("MYFXBOOK_CSRF", "")
    user_agent = pairs.get("MYFXBOOK_USER_AGENT") or os.environ.get("MYFXBOOK_USER_AGENT", "")
    if not cookie or not csrf:
        raise RuntimeError(f"MYFXBOOK_COOKIE/CSRF empty in {path}")
    return MyFxBookSession(cookie=cookie, csrf=csrf, user_agent=user_agent)


def ensure_dirs(*paths: Path) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)
