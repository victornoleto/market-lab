"""Tests for ops/core/fx.py — BCB SGS série 1 PTAX client."""
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from ops.core import fx, storage
from ops.core.models import FxRate


def test_get_ptax_cache_hit(tmp_data_dir):
    storage.append_fx_rate(
        FxRate(
            date=date(2026, 4, 20),
            ptax_venda=Decimal("5.1234"),
            source="bcb_sgs_1",
            fetched_at=datetime.now(timezone.utc),
        )
    )
    result = fx.get_ptax(date(2026, 4, 20))
    assert result == Decimal("5.1234")


def test_get_ptax_cache_miss_fetches_bcb(tmp_data_dir, requests_mock):
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados",
        json=[{"data": "20/04/2026", "valor": "5.1234"}],
    )
    result = fx.get_ptax(date(2026, 4, 20))
    assert result == Decimal("5.1234")

    # Second call: cache hit, no new HTTP
    requests_mock.reset_mock()
    result2 = fx.get_ptax(date(2026, 4, 20))
    assert result2 == Decimal("5.1234")
    assert requests_mock.call_count == 0


def test_weekend_falls_back_to_previous_business_day(tmp_data_dir, requests_mock):
    # 2026-04-18 is a Saturday → fallback to Friday 2026-04-17
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados",
        json=[{"data": "17/04/2026", "valor": "5.1000"}],
    )
    result = fx.get_ptax(date(2026, 4, 18))
    assert result == Decimal("5.1000")


def test_bcb_empty_response_raises(tmp_data_dir, requests_mock):
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados",
        json=[],
    )
    with pytest.raises(fx.PtaxUnavailable):
        fx.get_ptax(date(2026, 4, 20))


def test_set_ptax_manual_bypasses_api(tmp_data_dir, requests_mock):
    fx.set_ptax_manual(date(2026, 4, 20), Decimal("5.5000"))
    # API never called
    assert requests_mock.call_count == 0
    assert fx.get_ptax(date(2026, 4, 20)) == Decimal("5.5000")
