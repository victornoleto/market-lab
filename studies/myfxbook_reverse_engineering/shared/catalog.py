"""Scrape vendor catalog (HappyForex / others) and classify systems into tiers.

Endpoint: https://www.myfxbook.com/paging.html?pt=90&p=<N>&name=<vendor>
Returns paginated HTML — each page lists ~20 systems with id, name, account
type, broker, leverage, gain%, drawdown%, age, n_trades.

Tier classification (per ROADMAP Phase 1):
  TIER 1: Real account, DD < 30%, NOT "OLD" prefix, age > 365d
  TIER 2: Real, DD < 30%, "OLD" prefix but n_trades > 500
  TIER 3: Demo OR DD > 50% OR n_trades < 200
  FOLCLORE_OBVIOUS: name matches MartiGrid/Frequency/Grid regex

Citations:
- [fooled_by_randomness, Taleb] — vendor track-record bias / survivorship
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from . import config

CATALOG_URL = "https://www.myfxbook.com/strategies/paging.html"
FOLCLORE_NAME_RE = re.compile(r"\b(MartiGrid|Frequency|Grid|Martin|Recovery)\b", re.IGNORECASE)
OLD_PREFIX_RE = re.compile(r"^OLD\b", re.IGNORECASE)


@dataclass(frozen=True)
class CatalogEntry:
    system_id: int
    name: str
    account_type: str  # "Real" | "Demo"
    broker: str
    leverage: str
    gain_pct: float | None
    drawdown_pct: float | None
    age_days: int | None
    n_trades_visible: int | None
    url: str = ""
    platform: str = ""

    @property
    def has_old_prefix(self) -> bool:
        return bool(OLD_PREFIX_RE.match(self.name))

    @property
    def is_folclore_by_name(self) -> bool:
        return bool(FOLCLORE_NAME_RE.search(self.name))


def _to_int(s: str | None) -> int | None:
    if not s:
        return None
    digits = re.sub(r"[^\d-]", "", s)
    return int(digits) if digits and digits != "-" else None


def _to_pct(s: str | None) -> float | None:
    if not s:
        return None
    cleaned = s.replace("%", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_catalog_html(html: str) -> list[CatalogEntry]:
    """Pure: HTML page → CatalogEntry list. Tolerant of structure drift."""
    soup = BeautifulSoup(html, "html.parser")
    entries: list[CatalogEntry] = []

    # Current MyFxBook user systems HTML: one `div.content-row.has-actions`
    # per system, with the account id at the tail of the member URL.
    for row in soup.select("div.content-row.has-actions"):
        link = row.select_one("a.bold[href*='/members/'], a[href*='/members/']")
        if not link:
            continue
        href = link.get("href", "")
        m = re.search(r"/members/[^/]+/[^/]+/(\d+)", href)
        if not m:
            continue
        sid = int(m.group(1))
        cells = row.find_all("div", class_="grid-table-cell", recursive=False)
        mini = [x.get_text(" ", strip=True) for x in row.select(".system-info-mini-boxes")]
        account_type = next((x for x in mini if x.lower() in {"real", "demo"}), "")
        leverage = next((x for x in mini if re.match(r"^\d+:\d+$", x)), "")
        platform = next((x for x in mini if "metatrader" in x.lower()), "")
        gain = cells[1].get_text(" ", strip=True) if len(cells) > 1 else ""
        drawdown = cells[2].get_text(" ", strip=True) if len(cells) > 2 else ""
        entries.append(
            CatalogEntry(
                system_id=sid,
                name=link.get_text(" ", strip=True),
                account_type=account_type,
                broker="",
                leverage=leverage,
                gain_pct=_to_pct(gain),
                drawdown_pct=_to_pct(drawdown),
                age_days=None,
                n_trades_visible=None,
                url=href,
                platform=platform,
            )
        )
    if entries:
        return entries

    for row in soup.select("table tr[data-system-id], div.system-row"):
        sid_attr = row.get("data-system-id") or row.get("data-id")
        sid = _to_int(sid_attr) if sid_attr else None
        if sid is None:
            link = row.select_one("a[href*='/members/']")
            if link and (m := re.search(r"/members/[^/]+/[^/]+/(\d+)", link.get("href", ""))):
                sid = int(m.group(1))
        if sid is None:
            continue
        cells = [c.get_text(strip=True) for c in row.select("td")]
        name = cells[0] if cells else row.select_one(".system-name").get_text(strip=True) if row.select_one(".system-name") else ""
        cell = lambda i: cells[i] if i < len(cells) else ""  # noqa: E731
        entries.append(
            CatalogEntry(
                system_id=sid,
                name=name,
                account_type=cell(1),
                broker=cell(2),
                leverage=cell(3),
                gain_pct=_to_pct(cell(4)),
                drawdown_pct=_to_pct(cell(5)),
                age_days=_to_int(cell(6)),
                n_trades_visible=_to_int(cell(7)),
                url=link.get("href", "") if 'link' in locals() and link else "",
            )
        )
    return entries


def last_catalog_page(html: str) -> int:
    """Return the highest catalog pagination page advertised in an HTML page."""
    soup = BeautifulSoup(html, "html.parser")
    pages = []
    for a in soup.select("a.paging-btn[page]"):
        try:
            pages.append(int(a.get("page", "")))
        except ValueError:
            continue
    return max(pages) if pages else 1


def fetch_catalog(
    vendor_name: str = config.VENDOR_NAME,
    pt: int = 90,
    max_pages: int = 50,
    rate_limit_ms: int = config.SCRAPE_RATE_LIMIT_MS,
) -> list[CatalogEntry]:
    """Iterate ?p=1..max_pages until a page returns 0 entries; concat results."""
    session = config.load_session()
    headers = {"Cookie": session.cookie, "User-Agent": session.user_agent}
    all_entries: list[CatalogEntry] = []
    for page in range(1, max_pages + 1):
        params = {"pt": str(pt), "p": str(page), "name": vendor_name}
        r = requests.get(CATALOG_URL, params=params, headers=headers, timeout=30)
        if r.status_code in (401, 403):
            raise RuntimeError(f"Catalog page {page} → {r.status_code}; refresh cookies")
        r.raise_for_status()
        page_entries = parse_catalog_html(r.text)
        if not page_entries:
            break
        all_entries.extend(page_entries)
        time.sleep(rate_limit_ms / 1000.0)
    return all_entries


def classify_tier(entry: CatalogEntry, min_age_days: int = 365) -> str:
    """ROADMAP Phase 1 tiering. Returns one of: TIER_1 | TIER_2 | TIER_3 | FOLCLORE_OBVIOUS."""
    if entry.is_folclore_by_name:
        return "FOLCLORE_OBVIOUS"
    real = entry.account_type.lower().startswith("real")
    dd = entry.drawdown_pct or 100.0
    n = entry.n_trades_visible or 0
    if not real or dd > 50 or n < 200:
        return "TIER_3"
    if dd >= 30:
        return "TIER_3"
    if entry.has_old_prefix:
        return "TIER_2" if n > 500 else "TIER_3"
    if (entry.age_days or 0) <= min_age_days:
        return "TIER_3"
    return "TIER_1"


def to_dataframe(entries: list[CatalogEntry]) -> pd.DataFrame:
    if not entries:
        return pd.DataFrame(columns=[
            "system_id", "name", "account_type", "broker", "leverage", "platform", "url",
            "gain_pct", "drawdown_pct", "age_days", "n_trades_visible",
            "has_old_prefix", "is_folclore_by_name", "tier",
        ])
    rows = [
        {
            "system_id": e.system_id,
            "name": e.name,
            "account_type": e.account_type,
            "broker": e.broker,
            "leverage": e.leverage,
            "platform": e.platform,
            "url": e.url,
            "gain_pct": e.gain_pct,
            "drawdown_pct": e.drawdown_pct,
            "age_days": e.age_days,
            "n_trades_visible": e.n_trades_visible,
            "has_old_prefix": e.has_old_prefix,
            "is_folclore_by_name": e.is_folclore_by_name,
            "tier": classify_tier(e),
        }
        for e in entries
    ]
    return pd.DataFrame(rows)


def save_catalog(df: pd.DataFrame, output_path: Path | None = None) -> Path:
    path = output_path or (config.CATALOG_ROOT / "all_systems.parquet")
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, compression="snappy")
    return path
