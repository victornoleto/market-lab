"""Scrape MyFxBook general systems ranking to CSV/JSON.

This script targets the general `/systems` listing (`pt=84`), not a vendor page.
It uses Playwright so requests run inside a real browser session and does not
store cookies in code or logs.

Default filters are intentionally stricter than the raw browser capture:

- real accounts only (`accountType=2`);
- recently active (`lastTraded=90` days instead of 1095);
- at least 90 days old (`ageValue=90` instead of 30);
- drawdown up to 50% (kept from the captured URL; ranking still records DD);
- positive pips threshold (`pipsType=1`, `pipsValue=30`);
- sorted by gain descending (`sb=19`, `st=2`, inferred from captured request).

Research-only. This is a triage list for later decoder runs; gain ranking is not
evidence of a tradeable edge because public track records are affected by
survivorship and selection bias `[fooled_by_randomness]` and require proper
bootstrap/DSR validation `[advances_fin_ml, p.196-211]`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.myfxbook_reverse_engineering.shared import config  # noqa: E402
from studies.myfxbook_reverse_engineering.shared.download_data import (  # noqa: E402
    _csrf,
    _fetch_text,
    _load_playwright,
)


DEFAULT_OUT_DIR = config.CATALOG_ROOT / "systems_rank"
WARMUP_URL = "https://www.myfxbook.com/systems"


@dataclass(frozen=True)
class RankedSystem:
    system_id: int
    name: str
    url: str
    owner: str | None
    account_type: str | None
    leverage: str | None
    platform: str | None
    gain_pct: float | None
    drawdown_pct: float | None
    performance_img_id: int | None
    raw_text: str


def _to_pct(text: str | None) -> float | None:
    if not text:
        return None
    cleaned = text.replace("%", "").replace(",", "").replace("+", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def _system_id_from_href(href: str) -> int | None:
    m = re.search(r"/members/[^/]+/[^/]+/(\d+)", href or "")
    return int(m.group(1)) if m else None


def _owner_from_href(href: str) -> str | None:
    m = re.search(r"/members/([^/]+)/", href or "")
    return m.group(1) if m else None


def _spark_id(row) -> int | None:
    img = row.select_one("img[src*='system-spark.png?id=']")
    if not img:
        return None
    m = re.search(r"id=(\d+)", img.get("src", ""))
    return int(m.group(1)) if m else None


def parse_systems_html(html: str) -> list[RankedSystem]:
    """Parse one `pt=84` systems page into ranked rows."""
    soup = BeautifulSoup(html, "html.parser")
    out: list[RankedSystem] = []

    # General `/systems` listing (`pt=84`) is a table, not the vendor-card layout.
    for row in soup.select("#systemsContTable tbody tr"):
        checkbox = row.select_one("input[data-oid]")
        sid = int(checkbox.get("data-oid")) if checkbox and str(checkbox.get("data-oid", "")).isdigit() else None
        link = row.select_one("a[id^='system-name-'][href*='/members/']") or row.select_one("a[href*='/members/'][href*='/%s']" % sid) if sid else None
        if link is None:
            link = row.select_one("a[href*='/members/'][href$='/%s']" % sid) if sid else row.select_one("a[href*='/members/']")
        href = link.get("href", "") if link else ""
        sid = sid or _system_id_from_href(href)
        if sid is None or not link:
            continue
        owner_link = None
        for candidate in row.select("a[href*='/members/']"):
            chref = candidate.get("href", "")
            if _system_id_from_href(chref) is None and candidate.get_text(" ", strip=True):
                owner_link = candidate
                break
        cells = row.find_all("td", recursive=False)
        gain = cells[3].get_text(" ", strip=True) if len(cells) > 3 else ""
        drawdown = cells[4].get_text(" ", strip=True) if len(cells) > 4 else ""
        out.append(
            RankedSystem(
                system_id=sid,
                name=link.get_text(" ", strip=True),
                url=href if href.startswith("http") else f"https://www.myfxbook.com{href}",
                owner=owner_link.get_text(" ", strip=True) if owner_link else _owner_from_href(href),
                account_type=None,
                leverage=None,
                platform=None,
                gain_pct=_to_pct(gain),
                drawdown_pct=_to_pct(drawdown),
                performance_img_id=_spark_id(row),
                raw_text=re.sub(r"\s+", " ", row.get_text(" ", strip=True)).strip(),
            )
        )
    if out:
        return out

    for row in soup.select("div.content-row.has-actions"):
        link = row.select_one("a.bold[href*='/members/'], a[href*='/members/']")
        if not link:
            continue
        href = link.get("href", "")
        sid = _system_id_from_href(href)
        if sid is None:
            continue
        cells = row.find_all("div", class_="grid-table-cell", recursive=False)
        mini = [x.get_text(" ", strip=True) for x in row.select(".system-info-mini-boxes")]
        account_type = next((x for x in mini if x.lower() in {"real", "demo"}), None)
        leverage = next((x for x in mini if re.match(r"^\d+:\d+$", x)), None)
        platform = next((x for x in mini if "metatrader" in x.lower()), None)
        gain = cells[1].get_text(" ", strip=True) if len(cells) > 1 else ""
        drawdown = cells[2].get_text(" ", strip=True) if len(cells) > 2 else ""
        out.append(
            RankedSystem(
                system_id=sid,
                name=link.get_text(" ", strip=True),
                url=href if href.startswith("http") else f"https://www.myfxbook.com{href}",
                owner=_owner_from_href(href),
                account_type=account_type,
                leverage=leverage,
                platform=platform,
                gain_pct=_to_pct(gain),
                drawdown_pct=_to_pct(drawdown),
                performance_img_id=_spark_id(row),
                raw_text=re.sub(r"\s+", " ", row.get_text(" ", strip=True)).strip(),
            )
        )
    return out


def last_page(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    pages = []
    for a in soup.select("a.paging-btn[page]"):
        try:
            pages.append(int(a.get("page", "")))
        except ValueError:
            continue
    return max(pages) if pages else 1


def build_params(args: argparse.Namespace, page: int, csrf: str) -> dict[str, str]:
    return {
        "pt": "84",
        "p": str(page),
        "ts": str(args.ts),
        "profitType": "0",
        "profitValue": str(args.min_profit),
        "drawType": "1",
        "drawValue": str(args.max_drawdown),
        "profitabilityType": "0",
        "profitabilityValue": str(args.min_profitability),
        "ageType": "0",
        "ageValue": str(args.min_age_days),
        "tradingType": str(args.trading_type),
        "systemType": str(args.system_type),
        "symbols": args.symbols,
        "accountType": str(args.account_type),
        "size": str(args.page_size),
        "sb": str(args.sort_by),
        "st": str(args.sort_type),
        "lastTraded": str(args.last_traded_days),
        "tradesType": "0",
        "pipsType": "1",
        "pipsValue": str(args.min_pips),
        "equityType": "1",
        "equityValue": str(args.min_equity),
        "serverOid": str(args.server_oid),
        "platformOid": str(args.platform_oid),
        "regulationType": str(args.regulation_type),
        "_csrf": csrf,
        "z": str(time.time()),
    }


def scrape_rank(args: argparse.Namespace) -> pd.DataFrame:
    out_dir = Path(args.output_dir)
    raw_dir = out_dir / "raw_pages"
    raw_dir.mkdir(parents=True, exist_ok=True)

    sync_playwright = _load_playwright()
    rows: list[RankedSystem] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headed)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
            locale="en-US",
        )
        page = ctx.new_page()
        page.goto(WARMUP_URL, wait_until="domcontentloaded", timeout=args.timeout_ms)
        csrf = _csrf(ctx)

        advertised_last = args.max_pages
        for p in range(1, args.max_pages + 1):
            params = build_params(args, p, csrf)
            url = "/paging.html?" + urlencode(params)
            html = _fetch_text(page, url, timeout_ms=args.timeout_ms)
            (raw_dir / f"page_{p:03d}.html").write_text(html)
            parsed = parse_systems_html(html)
            if not parsed:
                print(f"page {p}: 0 systems, stopping", flush=True)
                break
            rows.extend(parsed)
            advertised_last = min(args.max_pages, last_page(html))
            print(f"page {p}: {len(parsed)} systems", flush=True)
            if p >= advertised_last:
                break
            time.sleep(args.rate_limit_ms / 1000.0)
        browser.close()

    df = pd.DataFrame([asdict(r) for r in rows]).drop_duplicates(subset=["system_id"], keep="first")
    if df.empty:
        return df
    if args.account_type == 2:
        df["account_type"] = df["account_type"].fillna("Real (filter)")
    df = df.sort_values(["gain_pct", "drawdown_pct"], ascending=[False, True], na_position="last")
    df.insert(0, "rank_gain_desc", range(1, len(df) + 1))
    return df


def write_outputs(df: pd.DataFrame, args: argparse.Namespace) -> None:
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = args.output_stem
    csv_path = out_dir / f"{stem}.csv"
    json_path = out_dir / f"{stem}.json"
    parquet_path = out_dir / f"{stem}.parquet"
    manifest_path = out_dir / f"{stem}_manifest.md"

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2, force_ascii=False)
    df.to_parquet(parquet_path, compression="snappy")

    lines = [
        "# MyFxBook Systems Ranking Manifest",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Filters",
        "",
        f"- accountType: `{args.account_type}` (default 2 = real accounts)",
        f"- max_drawdown: `{args.max_drawdown}`",
        f"- min_age_days: `{args.min_age_days}`",
        f"- last_traded_days: `{args.last_traded_days}`",
        f"- min_pips: `{args.min_pips}`",
        f"- min_equity: `{args.min_equity}`",
        f"- sort: `sb={args.sort_by}, st={args.sort_type}` (gain desc inferred from browser capture)",
        "",
        "## Outputs",
        "",
        f"- CSV: `{csv_path}`",
        f"- JSON: `{json_path}`",
        f"- Parquet: `{parquet_path}`",
        "",
        "## Caveat",
        "",
        "Ranking by gain is only triage. Public track records are subject to survivorship/vendor selection bias `[fooled_by_randomness]`; any candidate still needs decoder fidelity and economic validation `[advances_fin_ml, p.196-211]`.",
        "",
    ]
    manifest_path.write_text("\n".join(lines))

    print("\n=== MyFxBook systems rank ===")
    print(f"rows: {len(df)}")
    print(f"csv: {csv_path}")
    print(f"json: {json_path}")
    print(f"parquet: {parquet_path}")
    if not df.empty:
        cols = ["rank_gain_desc", "system_id", "gain_pct", "drawdown_pct", "account_type", "name", "url"]
        print("\nTop systems by gain:")
        print(df[cols].head(args.print_top).to_string(index=False))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Scrape MyFxBook systems ranking sorted by gain desc")
    ap.add_argument("--output-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--output-stem", default="systems_gain_desc")
    ap.add_argument("--max-pages", type=int, default=10)
    ap.add_argument("--page-size", type=int, default=50)
    ap.add_argument("--timeout-ms", type=int, default=60_000)
    ap.add_argument("--rate-limit-ms", type=int, default=1500)
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--print-top", type=int, default=20)

    # MyFxBook filters. Defaults are chosen for decoder triage, not investment approval.
    ap.add_argument("--ts", type=int, default=374)
    ap.add_argument("--account-type", type=int, default=2, help="2=real accounts in captured URL")
    ap.add_argument("--max-drawdown", type=float, default=50.0)
    ap.add_argument("--min-age-days", type=int, default=90)
    ap.add_argument("--last-traded-days", type=int, default=90)
    ap.add_argument("--min-pips", type=float, default=30.0)
    ap.add_argument("--min-equity", type=float, default=30.0)
    ap.add_argument("--min-profit", type=float, default=0.0)
    ap.add_argument("--min-profitability", type=float, default=0.0)
    ap.add_argument("--trading-type", type=int, default=2)
    ap.add_argument("--system-type", type=int, default=0)
    ap.add_argument("--symbols", default="")
    ap.add_argument("--server-oid", type=int, default=0)
    ap.add_argument("--platform-oid", type=int, default=0)
    ap.add_argument("--regulation-type", type=int, default=1)
    ap.add_argument("--sort-by", type=int, default=19)
    ap.add_argument("--sort-type", type=int, default=2)
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    df = scrape_rank(args)
    write_outputs(df, args)
    return 0 if not df.empty else 1


if __name__ == "__main__":
    raise SystemExit(main())
