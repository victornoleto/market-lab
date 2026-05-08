"""Parse MyFxBook system-page info into JSON-ready dictionaries.

The source page is full HTML; the useful parts are `#infoStats` tables and
`.portfolio-resolve-account-type`. Values are intentionally kept as raw strings
because MyFxBook mixes currencies, percentages and date annotations.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from . import config


def _key(label: str) -> str:
    label = re.sub(r"\s+", " ", label.replace(":", " ")).strip().lower()
    label = label.replace("abs. gain", "absolute_gain")
    label = re.sub(r"[^a-z0-9]+", "_", label).strip("_")
    return label


def parse_system_info_html(html: str, *, system_id: int | str | None = None, url: str = "") -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    stats: dict[str, str] = {}
    info = soup.select_one("#infoStats")
    if info:
        for tr in info.select("tr"):
            cells = tr.find_all("td", recursive=False)
            if len(cells) < 2:
                continue
            key = _key(cells[0].get_text(" ", strip=True))
            val = re.sub(r"\s+", " ", cells[1].get_text(" ", strip=True)).strip()
            if key:
                stats[key] = val

    account: dict[str, str] = {}
    account_box = soup.select_one(".portfolio-resolve-account-type")
    if account_box:
        text = re.sub(r"\s+", " ", account_box.get_text(" ", strip=True)).strip()
        parts = [p.strip() for p in text.split(",") if p.strip()]
        account["raw"] = text
        if parts:
            m = re.match(r"(Real|Demo)\s*\(([^)]+)\)", parts[0], flags=re.I)
            account["account_type"] = m.group(1) if m else parts[0]
            if m:
                account["currency"] = m.group(2)
        broker = account_box.select_one("a.underline")
        if broker:
            account["broker"] = broker.get_text(" ", strip=True)
            account["broker_url"] = broker.get("href", "")
        lev = re.search(r"\b\d+:\d+\b", text)
        if lev:
            account["leverage"] = lev.group(0)
        platform = re.search(r"MetaTrader\s+\d+", text, flags=re.I)
        if platform:
            account["platform"] = platform.group(0)

    title = soup.select_one("h1, .portfolio-name, title")
    return {
        "system_id": int(system_id) if system_id is not None and str(system_id).isdigit() else system_id,
        "url": url,
        "name": title.get_text(" ", strip=True) if title else "",
        "stats": stats,
        "account": account,
    }


def write_system_info_json(html: str, system_id: int | str, url: str = "", output_path: Path | None = None) -> tuple[dict[str, Any], Path]:
    data = parse_system_info_html(html, system_id=system_id, url=url)
    path = output_path or config.system_info_json_path(system_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return data, path
