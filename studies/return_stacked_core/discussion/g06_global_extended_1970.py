#!/usr/bin/env python3
"""g06 — global extended 1970+ window, LOW fidelity (secondary evidence only).

Adds the regimes the 1988/2000 windows hide: stagflation, the late-70s gold
bull, Volcker, 1987 — now with international equity sims (VT/VEA index
reconstructions that far back are themselves LOW fidelity). The HAIRCUT
variant (pre-1988 MF excess x0.5) is the honest headline
`[stocks_on_the_move, p.21-30]`, `[testing_tuning, p.327-335]`.

Outputs: ``tables/global_extended_metrics.csv``,
``series/global_portfolio_equity_extended.parquet`` (for fig g11).
Skips loudly if g01 could not build the extended matrix.
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

KMLM_INCEPTION = pd.Timestamp("1987-12-31")


def main() -> int:
    ext_path = dd.SERIES_DIR / "global_extended_returns.parquet"
    if not ext_path.exists():
        print("WARNING: global extended matrix missing — g06 SKIPPED.",
              file=sys.stderr)
        return 0

    ext = pd.read_parquet(ext_path)
    cash = ext["CASHX"]
    drag = dd.FINANCING_SPREAD_ANNUAL / dd.TRADING_DAYS

    # Haircut MF sleeves (pre-1988 excess over cash x0.5), mirroring s01.
    kmlm = ext["KMLM_SPLICED"]
    pre = ext.index < KMLM_INCEPTION
    kmlm_hc = kmlm.copy()
    kmlm_hc[pre] = cash[pre] + 0.5 * (kmlm[pre] - cash[pre])
    ext["RSST_HC"] = ext["SPYSIM"] + kmlm_hc - (cash + drag)
    ext["RSIT_HC"] = ext["VXUSSIM"] + kmlm_hc - (cash + drag)

    portfolios: list[tuple[str, dict[str, float] | str]] = [
        ("CORE-GLOBAL-EXT-HAIRCUT 20/15/20/20/25",
         {"GDESIM": .20, "NTSDSIM": .15, "RSST_HC": .20, "RSIT_HC": .20,
          "ZROZSIM": .25}),
        ("HALF-INTL-EXT-HAIRCUT 27.5/7.5/30/10/25",
         {"GDESIM": .275, "NTSDSIM": .075, "RSST_HC": .30, "RSIT_HC": .10,
          "ZROZSIM": .25}),
        ("US-CORE-EXT-HAIRCUT 35/40/25",
         {"GDESIM": .35, "RSST_HC": .40, "ZROZSIM": .25}),
        ("60/40 VT/IEF", {"VTSIM": .60, "IEFSIM": .40}),
        ("100% VT", "VTSIM"),
        ("100% SPY", "SPYSIM"),
    ]

    rows, curves = [], {}
    for label, spec in portfolios:
        equity = (engine.equity_from_returns(ext[spec]) if isinstance(spec, str)
                  else engine.rebalanced_equity(ext, spec))
        curves[label] = equity
        rows.append({"portfolio": label, "fidelity": "LOW",
                     **engine.compute_metrics(equity)})

    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(dd.TABLES_DIR / "global_extended_metrics.csv", index=False)
    pd.DataFrame(curves).to_parquet(
        dd.SERIES_DIR / "global_portfolio_equity_extended.parquet"
    )
    print(frame[["portfolio", "start", "cagr", "mdd", "sharpe"]].round(4)
          .to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
