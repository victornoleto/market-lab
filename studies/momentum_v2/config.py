"""Config loading: a shared ``base.yaml`` deep-merged with a per-universe file.

The per-universe file (e.g. ``config/us_stocks.yaml``) only carries the
overrides that differ from ``base.yaml`` (universe name, benchmark, filter
tightening), so every universe produces the same result schema.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = Path(__file__).resolve().parent / "config"
BASE_CONFIG = CONFIG_DIR / "base.yaml"


def load_env_file(path: Path = REPO_ROOT / ".env") -> None:
    """Load simple KEY=VALUE entries from `.env` without overriding env vars."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(universe: str, *, base_path: str | Path = BASE_CONFIG) -> dict[str, Any]:
    """Load ``base.yaml`` and deep-merge ``config/<universe>.yaml`` if present."""
    base = yaml.safe_load(Path(base_path).read_text(encoding="utf-8"))
    if not isinstance(base, dict):
        raise ValueError(f"base config must be a YAML mapping: {base_path}")
    universe_path = CONFIG_DIR / f"{universe}.yaml"
    if universe_path.exists():
        override = yaml.safe_load(universe_path.read_text(encoding="utf-8")) or {}
        base = _deep_merge(base, override)
    base.setdefault("run", {})["universe"] = universe
    return base


def database_url(config: dict[str, Any]) -> str:
    db = config.get("database", {})
    url_env = str(db.get("url_env", "YFINANCE_DATABASE_URL"))
    fallback_env = str(db.get("fallback_url_env", "DATABASE_URL"))
    return os.getenv(url_env) or os.getenv(fallback_env) or "postgresql://postgres:postgres@localhost:5432/stocks"


def schema_name(config: dict[str, Any]) -> str:
    return str(config.get("database", {}).get("schema", "public"))


def price_column(config: dict[str, Any]) -> str:
    return str(config.get("database", {}).get("price_column", "adj_close"))


def universe_name(config: dict[str, Any]) -> str:
    return str(config.get("run", {}).get("universe", "us_stocks"))


def benchmark_symbol(config: dict[str, Any]) -> str:
    run = config.get("run", {})
    universe = universe_name(config)
    by_universe = run.get("benchmark_by_universe", {})
    return str(by_universe.get(universe, "SPY"))


def _country_asset(universe: str) -> tuple[str, str]:
    if universe == "crypto":
        return "global", "crypto"
    country, _, asset = universe.partition("_")
    return country, asset.rstrip("s") if asset else "stock"


def filter_key(universe: str) -> str:
    country, asset = _country_asset(universe)
    if asset == "crypto":
        return "crypto"
    return f"{country}_{asset}"


def merged_filter_config(config: dict[str, Any], universe: str) -> dict[str, Any]:
    """Merge ``filters.default`` with the ``filters.<universe-key>`` override."""
    filters = config.get("filters", {})
    default = dict(filters.get("default", {}))
    default.update(dict(filters.get(filter_key(universe), {})))
    return default


def masked_database_url(url: str) -> str:
    if "@" not in url:
        return url
    scheme, rest = url.split("://", 1) if "://" in url else ("", url)
    host = rest.split("@", 1)[1]
    return f"{scheme}://***:***@{host}" if scheme else f"***:***@{host}"
