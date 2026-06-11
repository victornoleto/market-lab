#!/usr/bin/env python3
"""g01 — build the three global daily-return matrices into ``series/``.

- ``series/global_primary_returns.parquet`` — 2000+ (MFBLEND sleeves; same
  fidelity standard as the US primary window). Benchmark: VTSIM.
- ``series/global_1988_returns.parquet`` — 1988+ canonical global window
  (KMLM-only MF; MEDIUM fidelity).
- ``series/global_extended_returns.parquet`` — 1970+ (KMLM_SPLICED; LOW
  fidelity; skipped loudly without Ken French CSVs).

Sleeve formulas: see ``discussion_data._compose_global_sleeves`` and
METHODS.md §3-G. Provenance sidecar: ``series/global_series_meta.json``.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.return_stacked_core.discussion import discussion_data as dd  # noqa: E402


def main() -> int:
    dd.SERIES_DIR.mkdir(parents=True, exist_ok=True)
    meta: dict = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "financing_standard": (
            "2%/yr spread on 100%-stack legs (RSST tracking convention), "
            "plain CASHX on 90/60 legs; g00 documents -0.60pp/yr CAGR vs the "
            "old saved testfol payload"
        ),
        "series": {},
    }

    primary = dd.load_global_primary_returns()
    primary.to_parquet(dd.SERIES_DIR / "global_primary_returns.parquet")
    meta["series"]["global_primary_returns"] = {
        "window": f"{primary.index[0].date()}..{primary.index[-1].date()}",
        "mf_sleeve": "MFBLEND (0.7 DBMF + 0.3 KMLM)",
        "fidelity": "primary standard",
        "columns": sorted(primary.columns),
    }

    g88 = dd.load_global_1988_returns()
    g88.to_parquet(dd.SERIES_DIR / "global_1988_returns.parquet")
    meta["series"]["global_1988_returns"] = {
        "window": f"{g88.index[0].date()}..{g88.index[-1].date()}",
        "mf_sleeve": "KMLM only (DBMF starts 2000)",
        "fidelity": "MEDIUM — canonical global window",
    }

    try:
        ext = dd.load_global_extended_returns()
        ext.to_parquet(dd.SERIES_DIR / "global_extended_returns.parquet")
        meta["series"]["global_extended_returns"] = {
            "window": f"{ext.index[0].date()}..{ext.index[-1].date()}",
            "mf_sleeve": "KMLM_SPLICED (UMD+RF pre-1988)",
            "fidelity": "LOW — academic splice + index reconstructions",
        }
    except FileNotFoundError as exc:
        print(f"WARNING: {exc} — global extended matrix SKIPPED.", file=sys.stderr)
        meta["series"]["global_extended_returns"] = {"status": "SKIPPED"}

    (dd.SERIES_DIR / "global_series_meta.json").write_text(json.dumps(meta, indent=2))
    for name, info in meta["series"].items():
        print(f"{name}: {info.get('status', 'BUILT')} {info.get('window', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
