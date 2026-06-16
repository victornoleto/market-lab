"""Config loading helpers for the Postgres-backed momentum study."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.yaml"


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


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict[str, Any]:
    """Load YAML config and return a plain dict."""
    config_path = Path(path)
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"config must be a YAML mapping: {config_path}")
    return raw


def database_url(config: dict[str, Any]) -> str:
    """Resolve database URL from configured env var names."""
    db = config.get("database", {})
    url_env = str(db.get("url_env", "YFINANCE_DATABASE_URL"))
    fallback_env = str(db.get("fallback_url_env", "DATABASE_URL"))
    value = os.getenv(url_env) or os.getenv(fallback_env)
    if value:
        return value
    return "postgresql://postgres:postgres@localhost:5432/stocks"


def schema_name(config: dict[str, Any]) -> str:
    return str(config.get("database", {}).get("schema", "public"))


def price_column(config: dict[str, Any]) -> str:
    return str(config.get("database", {}).get("price_column", "adj_close"))


def filter_key(country: str, asset_class: str) -> str:
    if asset_class == "crypto":
        return "crypto"
    return f"{country}_{asset_class}"


def merged_filter_config(config: dict[str, Any], country: str, asset_class: str) -> dict[str, Any]:
    """Merge `filters.default` with `filters.<country>_<asset_class>` overrides."""
    filters = config.get("filters", {})
    default = dict(filters.get("default", {}))
    override = dict(filters.get(filter_key(country, asset_class), {}))
    default.update(override)
    return default


def as_int_list(value: Any) -> list[int]:
    if isinstance(value, str):
        return [int(part.strip()) for part in value.split(",") if part.strip()]
    return [int(item) for item in value]


def as_str_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(item) for item in value]


def as_bool_list(value: Any) -> list[bool]:
    if isinstance(value, bool):
        return [value]
    if isinstance(value, str):
        return [part.strip().lower() in {"1", "true", "yes", "y"} for part in value.split(",")]
    return [bool(item) for item in value]


def masked_database_url(url: str) -> str:
    if "@" not in url:
        return url
    scheme, rest = url.split("://", 1) if "://" in url else ("", url)
    host = rest.split("@", 1)[1]
    return f"{scheme}://***:***@{host}" if scheme else f"***:***@{host}"
