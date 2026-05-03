"""End-to-end MyFxBook downloader: catalog + system info + trade history.

Uses Playwright as transport and Python parsers as source of truth. Playwright
keeps requests inside a real browser session (cookies, CSRF, same-origin), while
raw HTML is persisted so parsing is reproducible and auditable.

Run:
    uv run python studies/myfxbook_reverse_engineering/shared/download_data.py

Outputs:
    data/catalog/all_systems.parquet
    data/catalog/pages/page_NNN.html
    data/trades/<system_id>/raw/system_info.html
    data/trades/<system_id>/raw/history_page_NNN.html
    data/trades/<system_id>/trades.parquet
    systems/<system_id>/system_info.json
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from studies.myfxbook_reverse_engineering.shared import catalog, config, parser, system_info  # noqa: E402

LOG_PATH = REPO_ROOT / "logs" / "myfxbook_reverse_engineering.log"
WARMUP_URL = "https://www.myfxbook.com/members/HappyForex"


@dataclass(frozen=True)
class HistoryFirstPage:
    html: str
    total_advertised: int
    total_pages: int
    base_params: str


def log(msg: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with LOG_PATH.open("a") as f:
        f.write(line + "\n")


def _load_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise RuntimeError(
            "playwright not installed. Run: uv pip install -e '.[myfxbook_scrape]' && "
            "uv run playwright install chromium"
        ) from e
    return sync_playwright


def _csrf(context) -> str:
    token = next((c["value"] for c in context.cookies("https://www.myfxbook.com") if c["name"] == "XSRF-TOKEN"), "")
    if not token:
        raise RuntimeError("XSRF-TOKEN cookie not present after warmup")
    return token


def _fetch_text(page, url: str, *, timeout_ms: int) -> str:
    return page.evaluate(
        """async ({url, timeoutMs}) => {
          const ctrl = new AbortController();
          const tid = setTimeout(() => ctrl.abort(), timeoutMs);
          try {
            const r = await fetch(url, {
              credentials: 'include',
              headers: {'x-requested-with': 'XMLHttpRequest', 'accept': '*/*', 'referer': 'https://www.myfxbook.com/'} ,
              signal: ctrl.signal
            });
            clearTimeout(tid);
            if (!r.ok) throw new Error('status_' + r.status);
            return await r.text();
          } catch (e) {
            clearTimeout(tid);
            throw e;
          }
        }""",
        {"url": url, "timeoutMs": timeout_ms},
    )


def scrape_catalog(page, csrf: str, *, vendor: str, max_pages: int, timeout_ms: int, rate_limit_ms: int) -> pd.DataFrame:
    raw_dir = config.CATALOG_ROOT / "pages"
    raw_dir.mkdir(parents=True, exist_ok=True)
    entries: list[catalog.CatalogEntry] = []
    last_page = max_pages
    for p in range(1, max_pages + 1):
        url = f"/paging.html?pt=90&p={p}&ts=52&name={vendor}&_csrf={csrf}&z={time.time()}"
        html = _fetch_text(page, url, timeout_ms=timeout_ms)
        (raw_dir / f"page_{p:03d}.html").write_text(html)
        page_entries = catalog.parse_catalog_html(html)
        if not page_entries:
            log(f"Catalog page {p}: empty, stopping")
            break
        entries.extend(page_entries)
        last_page = min(max_pages, catalog.last_catalog_page(html))
        log(f"Catalog page {p}: {len(page_entries)} systems")
        if p >= last_page:
            break
        time.sleep(rate_limit_ms / 1000.0)
    df = catalog.to_dataframe(entries).drop_duplicates(subset=["system_id"], keep="first")
    catalog.save_catalog(df)
    log(f"Catalog saved: {len(df)} systems → {config.CATALOG_ROOT / 'all_systems.parquet'}")
    return df


def load_or_scrape_catalog(
    page,
    csrf: str,
    *,
    vendor: str,
    max_pages: int,
    timeout_ms: int,
    rate_limit_ms: int,
    force_catalog: bool,
) -> pd.DataFrame:
    catalog_path = config.CATALOG_ROOT / "all_systems.parquet"
    if catalog_path.exists() and not force_catalog:
        df = pd.read_parquet(catalog_path)
        log(f"SKIP catalog: found {len(df)} systems at {catalog_path}. Use --force-catalog to re-download.")
        return df
    return scrape_catalog(
        page,
        csrf,
        vendor=vendor,
        max_pages=max_pages,
        timeout_ms=timeout_ms,
        rate_limit_ms=rate_limit_ms,
    )


def fetch_history_first_page(page, account_oid: int, csrf: str, *, timeout_ms: int) -> HistoryFirstPage:
    data = page.evaluate(
        """async ({accountOid, csrf, timeoutMs}) => {
          const ctrl = new AbortController();
          const tid = setTimeout(() => ctrl.abort(), timeoutMs);
          try {
            const r = await fetch('/systemPageGetHistoryFirstPage.json', {
              method: 'POST', credentials: 'include', signal: ctrl.signal,
              headers: {
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'x-requested-with': 'XMLHttpRequest',
                'origin': 'https://www.myfxbook.com',
                'referer': 'https://www.myfxbook.com/'
              },
              body: `invitation=&accountOid=${accountOid}&_csrf=${csrf}`
            });
            clearTimeout(tid);
            if (!r.ok) return {error: 'status_' + r.status};
            const j = await r.json();
            const html = j.content && j.content.history;
            if (!html) return {error: 'no_history_content'};
            const doc = new DOMParser().parseFromString(html, 'text/html');
            const totalAdvertised = parseInt(doc.querySelector('#historySize')?.value || '0');
            const lastBtn = Array.from(doc.querySelectorAll('a.paging-btn[page]')).filter(a => a.getAttribute('lastPage') === 'true').pop();
            const totalPages = parseInt(lastBtn?.getAttribute('page') || '1');
            const baseParams = doc.querySelector('.next a, a.paging-btn[page="2"]')?.getAttribute('params') || '';
            return {html, totalAdvertised, totalPages, baseParams, error: null};
          } catch (e) {
            clearTimeout(tid);
            return {error: e.name === 'AbortError' ? 'fetch_timeout' : (e.message || e.name)};
          }
        }""",
        {"accountOid": str(account_oid), "csrf": csrf, "timeoutMs": timeout_ms},
    )
    if data.get("error"):
        raise RuntimeError(data["error"])
    return HistoryFirstPage(
        html=data["html"],
        total_advertised=int(data.get("totalAdvertised") or 0),
        total_pages=int(data.get("totalPages") or 1),
        base_params=data.get("baseParams") or "",
    )


def scrape_one_system(
    page,
    row: pd.Series,
    csrf: str,
    *,
    max_history_pages: int,
    timeout_ms: int,
    rate_limit_ms: int,
    force: bool,
) -> dict[str, object]:
    sid = int(row["system_id"])
    name = str(row["name"])
    url = str(row.get("url") or f"https://www.myfxbook.com/members/{config.VENDOR_NAME}/{sid}")
    raw_dir = config.trades_raw_dir(sid)
    raw_dir.mkdir(parents=True, exist_ok=True)

    info_path = config.system_info_json_path(sid)
    parquet_path = config.trades_parquet_path(sid)
    if info_path.exists() and parquet_path.exists() and not force:
        df = pd.read_parquet(parquet_path)
        n_trades = int(df["is_trade"].sum()) if "is_trade" in df.columns else 0
        n_cash = int((~df["is_trade"]).sum()) if "is_trade" in df.columns else 0
        log(f"SKIP {sid} ({name}): already downloaded → {parquet_path.relative_to(REPO_ROOT)} ({n_trades} trades, {n_cash} non-trades). Use --force to re-download.")
        return {
            "system_id": sid,
            "name": name,
            "status": "SKIP",
            "rows": len(df),
            "trades": n_trades,
            "non_trades": n_cash,
            "history_pages": "cached",
            "history_pages_advertised": "cached",
        }

    log(f"INFO {sid} ({name})")
    page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
    html = page.content()
    config.system_info_html_path(sid).write_text(html)
    system_info.write_system_info_json(html, sid, url=url)

    first = fetch_history_first_page(page, sid, csrf, timeout_ms=timeout_ms)
    history_files: list[Path] = []
    first_path = raw_dir / "history_page_001.html"
    first_path.write_text(first.html)
    history_files.append(first_path)

    cap = min(first.total_pages, max_history_pages)
    for p in range(2, cap + 1):
        if not first.base_params:
            break
        params = first.base_params
        if "p=1" in params:
            params = params.replace("p=1", f"p={p}", 1)
        elif "p=2" in params:
            params = params.replace("p=2", f"p={p}", 1)
        html = _fetch_text(page, "/paging.html" + params, timeout_ms=timeout_ms)
        path = raw_dir / f"history_page_{p:03d}.html"
        path.write_text(html)
        history_files.append(path)
        log(f"  history {sid}: page {p}/{cap} saved")
        time.sleep(rate_limit_ms / 1000.0)

    df = parser.parse_history_html_files_to_parquet(history_files, config.trades_parquet_path(sid))
    n_trades = int(df["is_trade"].sum())
    n_cash = int((~df["is_trade"]).sum())
    log(f"OK {sid}: rows={len(df)}, trades={n_trades}, non_trades={n_cash}, pages={len(history_files)}/{first.total_pages}")
    return {
        "system_id": sid,
        "name": name,
        "status": "OK",
        "rows": len(df),
        "trades": n_trades,
        "non_trades": n_cash,
        "history_pages": len(history_files),
        "history_pages_advertised": first.total_pages,
        "history_total_advertised": first.total_advertised,
        "capped": first.total_pages > max_history_pages,
    }


def write_run_manifest(results: list[dict[str, object]]) -> Path:
    path = config.CATALOG_ROOT / "download_data_manifest.md"
    ok = [r for r in results if r.get("status") == "OK"]
    skipped = [r for r in results if r.get("status") == "SKIP"]
    bad = [r for r in results if r.get("status") not in {"OK", "SKIP"}]
    lines = ["# Download data manifest", f"\nGenerated: {pd.Timestamp.now('UTC').isoformat(timespec='seconds')}"]
    lines.append(f"\nTotal: {len(results)} | OK: {len(ok)} | Skipped: {len(skipped)} | Issues: {len(bad)}\n")
    lines.append("| system_id | name | status | trades | non_trades | pages | detail |")
    lines.append("|---:|---|---|---:|---:|---:|---|")
    for r in results:
        pages = f"{r.get('history_pages', '-')}/{r.get('history_pages_advertised', '-')}"
        detail = str(r.get("error") or ("capped" if r.get("capped") else ""))
        lines.append(
            f"| {r.get('system_id')} | {r.get('name')} | {r.get('status')} | "
            f"{r.get('trades', '-')} | {r.get('non_trades', '-')} | {pages} | {detail} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vendor", default=config.VENDOR_NAME)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-catalog-pages", type=int, default=20)
    ap.add_argument("--max-history-pages", type=int, default=200)
    ap.add_argument("--rate-limit-ms", type=int, default=1500)
    ap.add_argument("--timeout-ms", type=int, default=60_000)
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--catalog-only", action="store_true")
    ap.add_argument("--force", action="store_true", help="Re-download system info and trade history even if parquet/json already exist.")
    ap.add_argument("--force-catalog", action="store_true", help="Re-download catalog even if all_systems.parquet already exists.")
    args = ap.parse_args()

    sync_playwright = _load_playwright()
    results: list[dict[str, object]] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headed)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
            locale="en-US",
        )
        page = ctx.new_page()
        log(f"Warming session at {WARMUP_URL}")
        page.goto(WARMUP_URL, wait_until="domcontentloaded", timeout=args.timeout_ms)
        csrf = _csrf(ctx)
        log(f"CSRF acquired: {csrf}")

        df = load_or_scrape_catalog(
            page,
            csrf,
            vendor=args.vendor,
            max_pages=args.max_catalog_pages,
            timeout_ms=args.timeout_ms,
            rate_limit_ms=args.rate_limit_ms,
            force_catalog=args.force_catalog,
        )
        if args.catalog_only:
            browser.close()
            return 0
        if args.limit:
            df = df.head(args.limit)

        for _, row in df.iterrows():
            try:
                idx = len(results) + 1
                total = len(df)
                log(f"SYSTEM {idx}/{total}: {int(row['system_id'])} — {row['name']}")
                results.append(scrape_one_system(
                    page,
                    row,
                    csrf,
                    max_history_pages=args.max_history_pages,
                    timeout_ms=args.timeout_ms,
                    rate_limit_ms=args.rate_limit_ms,
                    force=args.force,
                ))
            except Exception as e:  # keep the batch moving; manifest records failures.
                sid = int(row["system_id"])
                name = str(row["name"])
                log(f"FAIL {sid} ({name}): {type(e).__name__}: {e}")
                results.append({"system_id": sid, "name": name, "status": "FAIL", "error": f"{type(e).__name__}: {e}"})
            time.sleep(args.rate_limit_ms / 1000.0)

        browser.close()

    manifest = write_run_manifest(results)
    log(f"Manifest written: {manifest}")
    return 0 if all(r.get("status") in {"OK", "SKIP"} for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
