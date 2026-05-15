"""Audit static portfolio universes and common data windows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.static_spy_beater_portfolio.scripts.universe import UNIVERSES, common_window, load_universe_returns


def audit() -> tuple[pd.DataFrame, pd.DataFrame]:
    asset_rows = []
    universe_rows = []
    for universe, tickers in UNIVERSES.items():
        frame = load_universe_returns(universe)
        for ticker in tickers:
            series = frame[ticker].dropna() if ticker in frame.columns else pd.Series(dtype=float)
            asset_rows.append(
                {
                    "universe": universe,
                    "ticker": ticker,
                    "available": bool(len(series)),
                    "start": str(series.index[0].date()) if len(series) else "",
                    "end": str(series.index[-1].date()) if len(series) else "",
                    "rows": int(len(series)),
                }
            )
        start, end, rows = common_window(frame, tickers)
        universe_rows.append(
            {
                "universe": universe,
                "n_assets": len(tickers),
                "common_start": str(start.date()),
                "common_end": str(end.date()),
                "common_rows": rows,
                "common_years": round((end - start).days / 365.25, 2),
            }
        )
    return pd.DataFrame(asset_rows), pd.DataFrame(universe_rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("studies/static_spy_beater_portfolio/results/audit"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    assets, universes = audit()
    assets.to_csv(args.output_dir / "asset_coverage.csv", index=False)
    universes.to_csv(args.output_dir / "universe_windows.csv", index=False)
    (args.output_dir / "universe_windows.json").write_text(
        json.dumps(universes.to_dict(orient="records"), indent=2) + "\n", encoding="utf-8"
    )
    print(universes.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
