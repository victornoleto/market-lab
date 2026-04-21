"""BCB SGS série 1 PTAX venda client + persistent cache + feriado fallback."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import holidays
import requests

from ops.core import storage
from ops.core.models import FxRate

BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"
BCB_TIMEOUT_SEC = 10.0
_BR_HOLIDAYS = holidays.country_holidays("BR")


class PtaxUnavailable(Exception):
    pass


def _is_business_day(d: date) -> bool:
    return d.weekday() < 5 and d not in _BR_HOLIDAYS


def _previous_business_day(d: date) -> date:
    cur = d - timedelta(days=1)
    while not _is_business_day(cur):
        cur -= timedelta(days=1)
    return cur


def _lookup_cache(d: date) -> Decimal | None:
    # Linear scan; acceptable for MVP volume (~2500 rows lifetime). Upgrade
    # to module-level dict if cache grows beyond ~100k rows.
    for rate in storage.read_fx_rates():
        if rate.date == d:
            return rate.ptax_venda
    return None


def _fetch_bcb(d: date) -> Decimal:
    params = {
        "formato": "json",
        "dataInicial": d.strftime("%d/%m/%Y"),
        "dataFinal": d.strftime("%d/%m/%Y"),
    }
    resp = requests.get(BCB_URL, params=params, timeout=BCB_TIMEOUT_SEC)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list) or not data:
        raise PtaxUnavailable(
            f"BCB returned unexpected payload for {d.isoformat()}: {data!r}"
        )
    return Decimal(str(data[0]["valor"]))


def get_ptax(d: date) -> Decimal:
    """Resolve PTAX venda for d.

    Order: cache → BCB fetch → fallback to last business day if d is weekend/holiday.
    """
    target = d if _is_business_day(d) else _previous_business_day(d)

    cached = _lookup_cache(target)
    if cached is not None:
        return cached

    value = _fetch_bcb(target)
    storage.append_fx_rate(
        FxRate(
            date=target,
            ptax_venda=value,
            source="bcb_sgs_1",
            fetched_at=datetime.now(timezone.utc),
        )
    )
    return value


def set_ptax_manual(d: date, value: Decimal) -> None:
    """Override cache with a manual PTAX value. Source tagged 'manual'."""
    storage.append_fx_rate(
        FxRate(
            date=d,
            ptax_venda=value,
            source="manual",
            fetched_at=datetime.now(timezone.utc),
        )
    )
