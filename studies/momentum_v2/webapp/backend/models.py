"""Pydantic response models for the portfolio API (shapes the frontend consumes)."""

from __future__ import annotations

from pydantic import BaseModel


class Holding(BaseModel):
    ticker: str
    weight: float


class IndexEntry(BaseModel):
    name: str
    mechanism: str
    top_n: int
    rebalance_months: int
    as_of: str | None = None
    cagr: float
    mdd: float
    sharpe: float
    gate_pass: bool
    kind: str | None = None


class StrategyIndex(BaseModel):
    universe: str
    window: str
    benchmark: str
    strategies: list[IndexEntry]
    disclaimer: str


class CurrentPortfolio(BaseModel):
    as_of: str | None = None
    holdings: list[Holding]


class HistoryEvent(BaseModel):
    date: str
    holdings: list[Holding]
    entered: list[str]
    exited: list[str]


class ContributionRow(BaseModel):
    ticker: str
    contribution: float
    last_weight: float
