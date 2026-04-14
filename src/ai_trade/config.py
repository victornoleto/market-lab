"""Typed configuration loaded from .env (or the process environment).

Usage:
    from ai_trade.config import get_settings
    settings = get_settings()
    host = settings.ctrader_host  # picks demo/live based on CTRADER_MODE

All fields default to safe/empty values so that `Settings()` loads even when
.env is absent (useful in tests and CI). Callers that require a value must
validate it at the boundary (e.g., raise if `ctrader_client_id` is empty
before attempting OAuth).
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class CTraderMode(StrEnum):
    DEMO = "demo"
    LIVE = "live"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # cTrader OAuth app credentials (from openapi.ctrader.com).
    ctrader_client_id: str = ""
    ctrader_client_secret: str = ""
    ctrader_redirect_uri: str = "http://localhost:8080/callback"
    ctrader_scope: str = "trading"

    # Tokens — written by scripts/ctrader_oauth_bootstrap.py and rotated by the
    # runtime on every refresh. Refresh tokens are single-use (rotating).
    ctrader_refresh_token: str = ""
    ctrader_access_token: str = ""

    # Account IDs resolved via ProtoOAGetAccountsByAccessTokenReq after OAuth.
    # These are `ctidTraderAccountId`, not the login number shown in the portal.
    ctrader_demo_account_id: int | None = None
    ctrader_live_account_id: int | None = None

    # Protobuf transport. Same port on demo/live; host differs.
    ctrader_host_demo: str = "demo.ctraderapi.com"
    ctrader_host_live: str = "live.ctraderapi.com"
    ctrader_port: int = 5035
    ctrader_mode: CTraderMode = CTraderMode.DEMO

    # Postgres.
    database_url: str = "postgresql://ai_trade:ai_trade@localhost:5435/ai_trade"

    @property
    def ctrader_host(self) -> str:
        return (
            self.ctrader_host_live
            if self.ctrader_mode == CTraderMode.LIVE
            else self.ctrader_host_demo
        )

    @property
    def ctrader_account_id(self) -> int | None:
        return (
            self.ctrader_live_account_id
            if self.ctrader_mode == CTraderMode.LIVE
            else self.ctrader_demo_account_id
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
