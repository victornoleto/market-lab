#!/usr/bin/env python3
"""s06 — extended 1970+ window, LOW fidelity (secondary evidence only).

Uses the matrix built by s01 (KMLM spliced with Ken French UMD+RF pre-1988;
gold administered price pre-1971-08). Every output row carries
``fidelity: LOW``. The HAIRCUT variant (pre-1988 MF excess x0.5) is the
honest headline for any chart that reaches the stagflation years — the raw
UMD splice overstates MF-like Sharpe ~3x `[stocks_on_the_move, p.21-30]`,
`[testing_tuning, p.327-335]`.

Outputs:
- ``tables/extended_metrics.csv`` — full-window metrics per portfolio.
- ``series/portfolio_equity_extended.parquet`` — daily equity for fig 11.
Extended-episode rows (stagflation, gold bull, Volcker, 1987) already live in
``tables/episodes_components.csv`` / ``episodes_products.csv`` (window =
extended), produced by s02.

Skips LOUDLY (exit 0, warning) if s01 could not build the extended matrix.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.return_stacked_core.discussion import discussion_data as dd  # noqa: E402
from studies.return_stacked_core.discussion import engine  # noqa: E402

PORTFOLIOS: list[tuple[str, dict[str, float] | str]] = [
    ("CORE-EXT 35/40/25", {"GDESIM": 0.35, "RSST_EXT": 0.40, "ZROZSIM": 0.25}),
    ("CORE-EXT-HAIRCUT 35/40/25", {"GDESIM": 0.35, "RSST_EXT_HAIRCUT": 0.40, "ZROZSIM": 0.25}),
    ("NTSX-swap-EXT", {"NTSXSIM": 0.35, "RSST_EXT_HAIRCUT": 0.40, "ZROZSIM": 0.25}),
    ("HFEA 55/45", {"UPROSIM": 0.55, "TMFSIM_D": 0.45}),
    ("60/40 SPY/IEF", {"SPYSIM": 0.60, "IEFSIM": 0.40}),
    ("100% SPY", "SPYSIM"),
]


def main() -> int:
    ext_path = dd.SERIES_DIR / "extended_returns.parquet"
    if not ext_path.exists():
        print(
            "WARNING: extended matrix missing (Ken French CSVs absent at s01 "
            "time) — s06 SKIPPED. Post must degrade to 2000+ evidence only.",
            file=sys.stderr,
        )
        return 0

    ext = pd.read_parquet(ext_path)
    rows = []
    curves: dict[str, pd.Series] = {}
    for label, spec in PORTFOLIOS:
        if isinstance(spec, str):
            equity = engine.equity_from_returns(ext[spec])
        else:
            equity = engine.rebalanced_equity(ext, spec)
        curves[label] = equity
        rows.append({"portfolio": label, "fidelity": "LOW", **engine.compute_metrics(equity)})

    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(dd.TABLES_DIR / "extended_metrics.csv", index=False)
    pd.DataFrame(curves).to_parquet(dd.SERIES_DIR / "portfolio_equity_extended.parquet")

    print(frame[["portfolio", "start", "cagr", "mdd", "sharpe"]].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
