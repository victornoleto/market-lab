#!/usr/bin/env python3
"""Phase 3 Lead A2 — multi-asset universe screener.

Reads each candidate's longest-available history from the local
TiingoStorage and computes:

* Hurst exponent (Chan structure-function ``[algo_trading_chan, p.44-46]``)
* ATR(20) / mean-close (``[stocks_on_the_move, p.88]``)
* Annualized realized vol (``[volatility_trading]`` baseline)
* Mean dollar volume (``[stocks_on_the_move, p.81]``)

Outputs:

* ``reports/screener_a2_universe.json`` — full table + Top-N selection
* stdout — markdown table sorted by composite rank

Usage::

    .venv/bin/python scripts/run_screener_a2.py \
        --storage-root data/tiingo \
        --output reports/screener_a2_universe.json \
        --top-n 5
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

from ai_trade.backtest.data.tiingo_storage import TiingoStorage
from ai_trade.backtest.screener import screen_universe
from ai_trade.backtest.screener.universe import Candidate

log = logging.getLogger("ai_trade.screener.a2")


# Universe per investment mandate §3 (Strategy A multi-asset). FX majors
# don't have daily Tiingo cache yet — documented in jornada.
DEFAULT_CANDIDATES: list[Candidate] = [
    # Equity / ETF — long history (~22y daily)
    Candidate("SPY", "etf"),
    Candidate("QQQ", "etf"),
    Candidate("IWM", "etf"),
    Candidate("GLD", "etf"),
    Candidate("TLT", "etf"),
    # Crypto majors — Tiingo daily 2014+
    Candidate("btcusd", "crypto"),
    Candidate("ethusd", "crypto"),
    Candidate("solusd", "crypto"),
    Candidate("xrpusd", "crypto"),
    Candidate("adausd", "crypto"),
    Candidate("dogeusd", "crypto"),
    Candidate("dotusd", "crypto"),
    Candidate("avaxusd", "crypto"),
    Candidate("bnbusd", "crypto"),
]


def _df_to_markdown(df: pd.DataFrame) -> str:
    """Tiny tabulate-free markdown table renderer (we don't pull deps)."""
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, r in df.iterrows():
        rows.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join([header, sep, *rows])


def _format_markdown(df: pd.DataFrame, *, top_n: int) -> str:
    cols = [
        "ticker",
        "asset_class",
        "n_bars",
        "first_dt",
        "last_dt",
        "hurst",
        "hurst_ci_low",
        "hurst_ci_high",
        "atr_pct",
        "realized_vol",
        "dollar_volume",
        "composite_rank",
        "notes",
    ]
    fmt = df[cols].copy()
    for col in ("hurst", "hurst_ci_low", "hurst_ci_high"):
        fmt[col] = fmt[col].map(lambda v: "N/A" if pd.isna(v) else f"{v:.3f}")
    for col in ("atr_pct", "realized_vol"):
        fmt[col] = fmt[col].map(lambda v: "N/A" if pd.isna(v) else f"{v*100:.2f}%")
    fmt["dollar_volume"] = fmt["dollar_volume"].map(
        lambda v: "N/A" if pd.isna(v) else f"${v / 1e6:,.1f}M"
    )
    fmt["first_dt"] = fmt["first_dt"].map(
        lambda v: "N/A" if pd.isna(v) else str(v)[:10]
    )
    fmt["last_dt"] = fmt["last_dt"].map(
        lambda v: "N/A" if pd.isna(v) else str(v)[:10]
    )
    fmt["composite_rank"] = fmt["composite_rank"].map(
        lambda v: "N/A" if pd.isna(v) else f"{v:.1f}"
    )
    md = _df_to_markdown(fmt)
    top = df.head(top_n)[["ticker", "asset_class", "hurst", "atr_pct", "dollar_volume"]].copy()
    top["hurst"] = top["hurst"].map(lambda v: "N/A" if pd.isna(v) else f"{v:.3f}")
    top["atr_pct"] = top["atr_pct"].map(lambda v: "N/A" if pd.isna(v) else f"{v*100:.2f}%")
    top["dollar_volume"] = top["dollar_volume"].map(
        lambda v: "N/A" if pd.isna(v) else f"${v / 1e6:,.1f}M"
    )
    top_block = (
        f"\n\n## Top-{top_n} (composite rank, lower = better)\n\n"
        + _df_to_markdown(top)
    )
    return md + top_block


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--storage-root", default="data/tiingo")
    p.add_argument("--output", default="reports/screener_a2_universe.json")
    p.add_argument("--frequency", default="daily")
    p.add_argument("--top-n", type=int, default=5)
    p.add_argument("--bootstrap", type=int, default=200,
                   help="Hurst bootstrap resamples for 95% CI (default 200).")
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )

    storage = TiingoStorage(root=args.storage_root)
    log.info(
        "screener: %d candidates, freq=%s, bootstrap=%d",
        len(DEFAULT_CANDIDATES),
        args.frequency,
        args.bootstrap,
    )

    df = screen_universe(
        DEFAULT_CANDIDATES,
        storage,
        frequency=args.frequency,
        bootstrap=args.bootstrap,
        random_state=args.seed,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "frequency": args.frequency,
        "n_candidates": len(DEFAULT_CANDIDATES),
        "rows": json.loads(
            df.assign(
                first_dt=df["first_dt"].astype(str),
                last_dt=df["last_dt"].astype(str),
            ).to_json(orient="records", date_format="iso")
        ),
        "top_n": int(args.top_n),
        "top_tickers": df.head(args.top_n)["ticker"].tolist(),
        "citations": [
            "[algo_trading_chan, p.44-46]",
            "[stocks_on_the_move, p.81, p.88]",
            "[volatility_trading]",
            "[algo_trading_chan, p.6-7]",
        ],
    }
    output_path.write_text(json.dumps(payload, indent=2, default=str))

    print(_format_markdown(df, top_n=args.top_n))
    log.info("screener: wrote %s", output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
