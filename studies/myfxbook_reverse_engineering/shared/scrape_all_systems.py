"""Standalone Playwright scraper for HappyForex systems.

Reads `data/catalog/all_systems.parquet`, iterates every system, and saves
raw trade JSON to `data/trades/<system_id>/raw/scrape.json`. Idempotent:
systems already scraped are skipped unless `--force`.

Setup (one-time):
    uv pip install -e '.[myfxbook_scrape]'
    uv run playwright install chromium

Run:
    uv run python studies/myfxbook_reverse_engineering/shared/scrape_all_systems.py
    # Options:
    --limit N         scrape only the first N (sorted by gain desc)
    --force           re-scrape systems that already have raw/scrape.json
    --headed          show the browser window (default: headless)
    --rate-limit-ms N inter-request sleep (default 400)
    --max-pages N     hard cap on pages per system (default 200; safety)

Notes:
- CSRF + cookies obtained automatically by warming the session at /members/HappyForex.
- All requests run inside the browser context (same-origin fetch) to bypass CF.
- Logs append to `logs/myfxbook_reverse_engineering.log` (project root).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from studies.myfxbook_reverse_engineering.shared import config  # noqa: E402

LOG_PATH = REPO_ROOT / "logs" / "myfxbook_reverse_engineering.log"

WARMUP_URL = "https://www.myfxbook.com/members/HappyForex"
HISTORY_FIRST_PAGE_URL = "/systemPageGetHistoryFirstPage.json"
PAGING_URL = "/paging.html"


def log(msg: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line)
    with LOG_PATH.open("a") as f:
        f.write(line + "\n")


# JS executed inside the browser context to scrape a single system.
SCRAPE_SYSTEM_JS = r"""
async ({accountOid, csrf, rateLimitMs, maxPages, fetchTimeoutMs}) => {
  const num = s => {
    if (s == null) return null;
    const cleaned = String(s).replace(/[^\d.+\-]/g, '');
    const n = parseFloat(cleaned);
    return Number.isFinite(n) ? n : null;
  };

  // fetch with hard timeout via AbortController; never hangs.
  async function fetchT(url, opts) {
    const ctrl = new AbortController();
    const tid = setTimeout(() => ctrl.abort(), fetchTimeoutMs);
    try {
      const r = await fetch(url, { ...opts, signal: ctrl.signal });
      clearTimeout(tid);
      return r;
    } catch (e) {
      clearTimeout(tid);
      const isAbort = e && (e.name === 'AbortError' || /aborted/i.test(e.message || ''));
      throw new Error(isAbort ? 'fetch_timeout' : ('fetch_error:' + (e.message || e.name)));
    }
  }

  function parseRows(doc) {
    const out = [];
    const rows = doc.querySelectorAll('#tradingHistoryTable tbody tr.commentRow, #tradingHistoryTable tbody tr[data-record]');
    rows.forEach(tr => {
      const symbolTd = tr.querySelector('td.symbol');
      if (!symbolTd) return;
      const brokerTimes = Array.from(tr.querySelectorAll('td.brokerTime')).map(t => t.textContent.trim());
      const userTimes = Array.from(tr.querySelectorAll('td.userTime')).map(t => t.textContent.trim());
      const opentime_ms = parseInt(symbolTd.getAttribute('opentime') || '0') || null;
      const closetime_ms = parseInt(symbolTd.getAttribute('closetime') || '0') || null;
      const symbol = symbolTd.querySelector('.symbolName')?.textContent.trim() || symbolTd.textContent.trim();
      const visibleCells = Array.from(tr.children).filter(c => !c.style.display || c.style.display !== 'none');
      const text = i => visibleCells[i]?.textContent.trim() || '';
      out.push({
        record: tr.getAttribute('data-record'),
        opentime_ms, closetime_ms,
        broker_open: brokerTimes[0] || null,
        broker_close: brokerTimes[1] || null,
        user_open: userTimes[0] || null,
        user_close: userTimes[1] || null,
        symbol, action: text(4),
        open_price: num(text(5)), close_price: num(text(6)),
        pips: num(text(7)), profit: num(text(8)),
        duration: text(9), pct: text(10),
        lots: null,
        sl_price: null, sl_pips: null, sl_profit: null,
        tp_price: null, tp_pips: null, tp_profit: null,
      });
    });
    return out;
  }

  // ---- First page via JSON endpoint
  let fpRes;
  try {
    fpRes = await fetchT('/systemPageGetHistoryFirstPage.json', {
      method: 'POST', credentials: 'include',
      headers: {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest',
        'origin': 'https://www.myfxbook.com',
        'referer': 'https://www.myfxbook.com/'
      },
      body: `invitation=&accountOid=${accountOid}&_csrf=${csrf}`
    });
  } catch (e) {
    return { error: `first_page_${e.message}`, n_collected: 0, total_advertised: 0, total_pages: 0, trades: [] };
  }
  if (fpRes.status !== 200) {
    return { error: `first_page_status_${fpRes.status}`, n_collected: 0, total_advertised: 0, total_pages: 0, trades: [] };
  }
  const fpJson = await fpRes.json();
  if (fpJson.error) {
    return { error: 'first_page_error_field_true', n_collected: 0, total_advertised: 0, total_pages: 0, trades: [] };
  }
  const fpHtml = fpJson.content?.history;
  if (!fpHtml) {
    return { error: 'no_history_content', n_collected: 0, total_advertised: 0, total_pages: 0, trades: [] };
  }
  const fpDoc = new DOMParser().parseFromString(fpHtml, 'text/html');

  const totalAdvertised = parseInt(fpDoc.querySelector('#historySize')?.value || '0');
  const lastBtn = Array.from(fpDoc.querySelectorAll('a.paging-btn[page]')).filter(a => a.getAttribute('lastPage') === 'true').pop();
  const totalPages = parseInt(lastBtn?.getAttribute('page') || '1');
  const baseParams = fpDoc.querySelector('.next a, a.paging-btn[page="2"]')?.getAttribute('params') || '';

  let allTrades = parseRows(fpDoc);
  let pagesFetched = 1;
  console.log(`[scrape ${accountOid}] first page OK, ${allTrades.length} rows, total_pages=${totalPages}, advertised=${totalAdvertised}`);

  const cap = Math.min(totalPages, maxPages);
  for (let p = 2; p <= cap; p++) {
    if (!baseParams) break;
    const url = '/paging.html' + baseParams.replace(/p=\d+/, 'p=' + p);
    let r;
    try {
      r = await fetchT(url, {
        credentials: 'include',
        headers: {
          'x-requested-with': 'XMLHttpRequest',
          'accept': '*/*',
          'referer': 'https://www.myfxbook.com/'
        }
      });
    } catch (e) {
      console.log(`[scrape ${accountOid}] page ${p} ${e.message}`);
      return { error: `page_${p}_${e.message}`, n_collected: allTrades.length, total_advertised: totalAdvertised, total_pages: totalPages, pages_fetched: pagesFetched, trades: allTrades };
    }
    if (r.status !== 200) {
      return { error: `page_${p}_status_${r.status}`, n_collected: allTrades.length, total_advertised: totalAdvertised, total_pages: totalPages, pages_fetched: pagesFetched, trades: allTrades };
    }
    const html = await r.text();
    const doc = new DOMParser().parseFromString(html, 'text/html');
    allTrades = allTrades.concat(parseRows(doc));
    pagesFetched++;
    if (p % 10 === 0) console.log(`[scrape ${accountOid}] page ${p}/${cap} done, total ${allTrades.length}`);
    await new Promise(res => setTimeout(res, rateLimitMs));
  }

  console.log(`[scrape ${accountOid}] DONE ${allTrades.length}/${totalAdvertised} in ${pagesFetched} pages`);
  return {
    error: null,
    n_collected: allTrades.length,
    total_advertised: totalAdvertised,
    total_pages: totalPages,
    pages_fetched: pagesFetched,
    capped: totalPages > maxPages,
    trades: allTrades,
  };
}
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--rate-limit-ms", type=int, default=1500,
                    help="Inter-page sleep (default 1500; CF throttles fast pagination).")
    ap.add_argument("--max-pages", type=int, default=100,
                    help="Hard cap on pages per system (default 100 = 2000 trades, ample for DSR).")
    ap.add_argument("--system-cooldown-s", type=int, default=5,
                    help="Seconds between systems + re-warmup of session.")
    ap.add_argument("--fetch-timeout-ms", type=int, default=30_000,
                    help="Per-fetch hard timeout via AbortController (default 30s).")
    args = ap.parse_args()

    catalog_path = config.CATALOG_ROOT / "all_systems.parquet"
    if not catalog_path.exists():
        print(f"ERROR: catalog parquet missing at {catalog_path}. Run Phase 1 first.", file=sys.stderr)
        return 2

    df = pd.read_parquet(catalog_path).sort_values("gain_pct", ascending=False).reset_index(drop=True)
    if args.limit:
        df = df.head(args.limit)

    queue: list[tuple[int, str]] = []
    for _, row in df.iterrows():
        sid = int(row["system_id"])
        out_path = config.trades_raw_dir(sid) / "scrape.json"
        if out_path.exists() and not args.force:
            try:
                prior = json.loads(out_path.read_text())
                # Skip only if previous run was clean OR collected >= advertised (capped is OK).
                if not prior.get("error") and prior.get("n_collected", 0) >= prior.get("total_advertised", 0):
                    log(f"SKIP {sid} ({row['name']}) — clean prior scrape ({prior['n_collected']} trades)")
                    continue
                log(f"REDO {sid} ({row['name']}) — prior had error={prior.get('error')!r} ({prior.get('n_collected',0)}/{prior.get('total_advertised',0)})")
            except Exception as e:
                log(f"REDO {sid} ({row['name']}) — could not parse prior scrape: {e}")
        queue.append((sid, row["name"]))

    if not queue:
        log("Nothing to scrape — all systems already have raw/scrape.json. Use --force to re-scrape.")
        return 0

    log(f"Queue: {len(queue)} systems to scrape (rate {args.rate_limit_ms}ms, max {args.max_pages} pages each)")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "ERROR: playwright not installed. Run:\n"
            "  uv pip install -e '.[myfxbook_scrape]'\n"
            "  uv run playwright install chromium",
            file=sys.stderr,
        )
        return 3

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headed)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
            locale="en-US",
        )
        page = ctx.new_page()
        # Mirror browser console messages into our logfile so we can see scrape progress
        # in real time even when running headless in background.
        page.on("console", lambda m: log(f"  [browser:{m.type}] {m.text}") if m.text.startswith("[scrape") else None)

        log(f"Warming session at {WARMUP_URL} (CF challenge here if any)…")
        page.goto(WARMUP_URL, wait_until="domcontentloaded", timeout=60_000)

        # Extract CSRF from cookies
        cookies = ctx.cookies("https://www.myfxbook.com")
        csrf = next((c["value"] for c in cookies if c["name"] == "XSRF-TOKEN"), None)
        if not csrf:
            log("ERROR: XSRF-TOKEN cookie not present after warmup. CF may have challenged the session.")
            browser.close()
            return 4
        log(f"CSRF acquired: {csrf}")

        successes = failures = 0
        for i, (sid, name) in enumerate(queue):
            # Re-warm session every system: navigate back to vendor page so the
            # browser's Referer / cookies remain "fresh" between paginated bursts.
            if i > 0:
                try:
                    page.goto(WARMUP_URL, wait_until="domcontentloaded", timeout=30_000)
                    new_csrf = next((c["value"] for c in ctx.cookies("https://www.myfxbook.com") if c["name"] == "XSRF-TOKEN"), None)
                    if new_csrf and new_csrf != csrf:
                        log(f"  CSRF rotated → {new_csrf}")
                        csrf = new_csrf
                    time.sleep(args.system_cooldown_s)
                except Exception as e:
                    log(f"  WARMUP_FAIL: {type(e).__name__}: {e} — continuing")

            try:
                result = page.evaluate(
                    SCRAPE_SYSTEM_JS,
                    {
                        "accountOid": str(sid),
                        "csrf": csrf,
                        "rateLimitMs": args.rate_limit_ms,
                        "maxPages": args.max_pages,
                        "fetchTimeoutMs": args.fetch_timeout_ms,
                    },
                )
            except Exception as e:
                log(f"FAIL {sid} ({name}): exception {type(e).__name__}: {e}")
                failures += 1
                continue

            out_dir = config.trades_raw_dir(sid)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "scrape.json"

            payload = {
                "accountOid": sid,
                "name": name,
                "scraped_at": datetime.now().isoformat(timespec="seconds"),
                **result,
            }
            out_path.write_text(json.dumps(payload, indent=2))

            err = result.get("error")
            n = result.get("n_collected", 0)
            adv = result.get("total_advertised", 0)
            pf = result.get("pages_fetched", 0)
            tp = result.get("total_pages", 0)
            cap = " [CAPPED]" if result.get("capped") else ""
            if err:
                log(f"WARN {sid} ({name}): {err} (collected {n}/{adv}){cap} → {out_path.relative_to(REPO_ROOT)}")
                failures += 1
            else:
                log(f"OK   {sid} ({name}): {n}/{adv} trades, {pf}/{tp} pages{cap} → {out_path.relative_to(REPO_ROOT)}")
                successes += 1

            time.sleep(args.rate_limit_ms / 1000.0)

        browser.close()

    log(f"Done. successes={successes}, failures={failures}, total_queued={len(queue)}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
