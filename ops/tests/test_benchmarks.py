"""Tests for ops/core/benchmarks.py — fetchers + equity curve normalizer."""
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from ops.core import benchmarks, storage
from ops.core.models import BenchmarkPoint


def test_ipca_fetch_from_bcb(tmp_data_dir, requests_mock):
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados",
        json=[
            {"data": "01/03/2026", "valor": "0.35"},
            {"data": "01/04/2026", "valor": "0.40"},
        ],
    )
    benchmarks.fetch_ipca()
    points = storage.read_benchmark_points()
    ipca = [p for p in points if p.series_id == "ipca_pct_monthly"]
    assert len(ipca) == 2
    assert ipca[0].value == Decimal("0.35")


def test_selic_daily_fetch(tmp_data_dir, requests_mock):
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados",
        json=[
            {"data": "20/04/2026", "valor": "0.0456"},
        ],
    )
    benchmarks.fetch_selic_daily()
    points = storage.read_benchmark_points()
    assert any(p.series_id == "selic_daily_pct" for p in points)


def test_equity_curve_selic_accumulates(tmp_data_dir):
    # Seed 3 daily SELIC bars @ 0.05% each
    storage.append_benchmark_points([
        BenchmarkPoint(
            date=date(2026, 4, 20 + i), series_id="selic_daily_pct",
            value=Decimal("0.05"), source="bcb_sgs_11",
            fetched_at=datetime.now(timezone.utc),
        )
        for i in range(3)
    ])
    curve = benchmarks.equity_curve_brl(
        series_id="selic_daily_pct",
        inception_date=date(2026, 4, 20),
        end_date=date(2026, 4, 22),
        base_value_brl=Decimal("100000"),
    )
    # Convention: each bar's return accrues on its own date.
    # After 3 days at 0.05%: 100_000 × 1.0005³ ≈ 100_150.08
    assert curve.iloc[-1]["value"] == pytest.approx(100150.08, rel=1e-4)


def test_equity_curve_single_bar_applies_return(tmp_data_dir):
    """Single bar on inception day applies its return — convention: each bar's
    return accrues on its own date."""
    storage.append_benchmark_points([
        BenchmarkPoint(
            date=date(2026, 4, 20), series_id="selic_daily_pct",
            value=Decimal("0.05"), source="bcb_sgs_11",
            fetched_at=datetime.now(timezone.utc),
        ),
    ])
    curve = benchmarks.equity_curve_brl(
        series_id="selic_daily_pct",
        inception_date=date(2026, 4, 20),
        end_date=date(2026, 4, 20),
        base_value_brl=Decimal("100000"),
    )
    # 100000 × 1.0005 = 100050
    assert curve.iloc[0]["value"] == pytest.approx(100050.0, rel=1e-6)
