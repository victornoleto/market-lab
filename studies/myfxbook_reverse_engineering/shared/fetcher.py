"""Scrape MyFxBook trade-history into batched JSON files under data/trades/<id>/raw/.

The actual P1 scrape in the prototype was executed via Playwright's
browser_evaluate (inline JS in a logged-in session) because Cloudflare
fingerprints non-browser HTTP. This module exposes the parameterized
shape (system_id, page range, output dir, cookies-from-env) so that the
P1 worker — whether that's `requests`, Playwright headless, or a
copy-pasted browser_evaluate snippet — is a swappable backend.

If 401/403 is observed, cookies have expired: re-export from a logged-in
browser DevTools and rewrite STUDY_ROOT/.env. See `config.load_session`.

Citations: N/A — vendor-API plumbing, no academic basis.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests

from . import config

TRADE_HISTORY_URL = "https://www.myfxbook.com/widgets/system-trades-detailed"


@dataclass(frozen=True)
class FetchSpec:
    system_id: int | str
    start_iso: str  # "YYYY-MM-DD HH:MM"
    end_iso: str
    ts: str  # MYFXBOOK_TS query param (account opaque token, from .env)


def _build_params(spec: FetchSpec, page: int) -> dict[str, str]:
    return {
        "id": str(spec.system_id),
        "type": "fullDetails",
        "ts": spec.ts,
        "page": str(page),
        "start": spec.start_iso,
        "end": spec.end_iso,
    }


def fetch_page(spec: FetchSpec, page: int, session: config.MyFxBookSession) -> dict:
    """One paged GET. Returns parsed JSON. Raises on 401/403/non-200."""
    headers = {
        "Cookie": session.cookie,
        "X-CSRF-Token": session.csrf,
        "User-Agent": session.user_agent,
        "Accept": "application/json, text/html, */*",
        "Referer": f"https://www.myfxbook.com/members/x/{spec.system_id}",
    }
    r = requests.get(TRADE_HISTORY_URL, params=_build_params(spec, page), headers=headers, timeout=30)
    if r.status_code in (401, 403):
        raise RuntimeError(
            f"MyFxBook returned {r.status_code} on page {page}. Cookies expired — "
            f"re-export from browser DevTools and rewrite {config.STUDY_ROOT/'.env'}"
        )
    r.raise_for_status()
    return r.json() if "json" in r.headers.get("content-type", "") else {"trades": [], "raw_html": r.text}


def fetch_trades(
    system_id: int | str,
    start_iso: str,
    end_iso: str,
    ts: str,
    pages: Iterable[int] | None = None,
    raw_dir: Path | None = None,
    rate_limit_ms: int = config.SCRAPE_RATE_LIMIT_MS,
) -> list[Path]:
    """Iterate pages, persist each as raw_dir/batch_<NNN>.json, return paths.

    `pages` defaults to 1..400 stopping when a response has no trades.
    """
    out_dir = raw_dir or config.trades_raw_dir(system_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    spec = FetchSpec(system_id=system_id, start_iso=start_iso, end_iso=end_iso, ts=ts)
    session = config.load_session()
    page_iter = pages if pages is not None else range(1, 401)
    saved: list[Path] = []
    for page in page_iter:
        data = fetch_page(spec, page, session)
        if not data.get("trades"):
            break
        path = out_dir / f"batch_{page:03d}.json"
        path.write_text(json.dumps(data))
        saved.append(path)
        time.sleep(rate_limit_ms / 1000.0)
    return saved
