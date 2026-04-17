"""Run the Phase 3 Lead A3b Donchian-breakout grid per asset.

Per-asset protocol (each asset consumes its LONGEST available Tiingo
daily window per the manifest — CLAUDE.md Phase 3 hard rule):

1. Load OHLC (adjusted close for the return stream; raw H/L for the
   Donchian channel) from ``data/tiingo/daily/``.
2. Split into IS (first 60%) / OOS (next 25%) / Stress (last 15%). The
   splits are MUTUALLY EXCLUSIVE (guards PBO).
3. Run :func:`simulate_tsmom` for each grid cell on the full window.
4. Run :func:`evaluate_tsmom_gates` to produce PBO / DSR / WF / OOS /
   Stress / Bootstrap verdicts.
5. Persist ``reports/a3b_tsmom_<asset>.json`` per asset plus a summary
   JSON ``reports/a3b_tsmom_summary.json``.

Usage::

    .venv/bin/python scripts/run_grid_tsmom_a3b.py \\
        --assets QQQ,TLT,xrpusd --output-dir reports/

Assets default to ``QQQ,TLT,xrpusd`` (the three A3a dead-end assets —
rerun under a different strategy family per the A3b brief).
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from ai_trade.backtest.data.tiingo_storage import TiingoStorage
from ai_trade.backtest.grid.tsmom_a3b import (
    default_tsmom_grid,
    evaluate_tsmom_gates,
)
from ai_trade.backtest.strategies.tsmom import simulate_tsmom

log = logging.getLogger("a3b")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def _splits_for_window(
    start: pd.Timestamp, end: pd.Timestamp
) -> tuple[tuple[str, str], tuple[str, str], tuple[str, str]]:
    """IS 60% / OOS 25% / Stress 15% of the full window.

    Splits are mutually exclusive (end of IS + 1 day = start of OOS).
    """
    total = (end - start).days
    is_end = start + pd.Timedelta(days=int(total * 0.60))
    oos_end = start + pd.Timedelta(days=int(total * 0.85))
    return (
        (start.strftime("%Y-%m-%d"), is_end.strftime("%Y-%m-%d")),
        (
            (is_end + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            oos_end.strftime("%Y-%m-%d"),
        ),
        (
            (oos_end + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d"),
        ),
    )


def _run_one_asset(
    asset: str,
    storage: TiingoStorage,
    output_dir: Path,
    bootstrap_n_resamples: int,
) -> dict:
    df = storage.read(asset, frequency="daily")
    if df.empty:
        raise ValueError(f"{asset}: empty daily frame")

    # Tiingo daily layout is {open, high, low, close, adj_close, volume}.
    # close/high/low are raw (unadjusted); adj_close folds in dividends &
    # splits. For Donchian on long windows with dividends we reconstruct
    # adjusted H/L by scaling raw H/L by (adj_close / close) — preserves
    # the within-bar H/L/C ratio while using the TR price series for the
    # return stream. Same rationale as ai_trade.backtest.data.adjust.
    raw_close = df["close"].astype(float)
    adj_close = (
        df["adj_close"].astype(float)
        if "adj_close" in df.columns
        else raw_close
    )
    scale = (adj_close / raw_close).replace([pd.NA, pd.NaT], 1.0).fillna(1.0)
    close = adj_close.dropna()
    high = (df["high"].astype(float) * scale).loc[close.index].dropna()
    low = (df["low"].astype(float) * scale).loc[close.index].dropna()
    common = close.index.intersection(high.index).intersection(low.index)
    close = close.loc[common]
    high = high.loc[common]
    low = low.loc[common]

    start = close.index.min()
    end = close.index.max()
    is_range, oos_range, stress_range = _splits_for_window(start, end)
    log.info(
        "%s: %s → %s (%d bars); IS=%s OOS=%s STRESS=%s",
        asset, start, end, len(close), is_range, oos_range, stress_range,
    )

    grid = default_tsmom_grid()
    log.info("%s: running %d configs", asset, len(grid))
    t0 = time.perf_counter()
    results = [simulate_tsmom(high, low, close, cfg) for cfg in grid]
    t_sim = time.perf_counter() - t0
    log.info("%s: simulation done in %.2fs", asset, t_sim)

    t0 = time.perf_counter()
    verdict = evaluate_tsmom_gates(
        asset,
        grid,
        results,
        is_range=is_range,
        oos_range=oos_range,
        stress_range=stress_range,
        bootstrap_n_resamples=bootstrap_n_resamples,
    )
    t_gates = time.perf_counter() - t0
    log.info(
        "%s: gates done in %.2fs; PBO=%.3f winner=%s n_pass=%d/%d",
        asset,
        t_gates,
        verdict.pbo_value,
        verdict.winner_config_id,
        verdict.n_passing_configs,
        verdict.n_configs,
    )

    out_path = output_dir / f"a3b_tsmom_{asset}.json"
    out_path.write_text(json.dumps(verdict.to_dict(), indent=2))
    return {
        "asset": asset,
        "n_bars": int(len(close)),
        "window": {"start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")},
        "splits": {"is": is_range, "oos": oos_range, "stress": stress_range},
        "pbo": verdict.pbo_value,
        "n_configs": verdict.n_configs,
        "n_pass": verdict.n_passing_configs,
        "winner_config_id": verdict.winner_config_id,
        "report": str(out_path),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default="QQQ,TLT,xrpusd")
    ap.add_argument("--storage-root", default="data/tiingo")
    ap.add_argument("--output-dir", default="reports/")
    ap.add_argument("--bootstrap-n-resamples", type=int, default=2000)
    args = ap.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    storage = TiingoStorage(root=Path(args.storage_root))

    summaries = []
    for a in [s.strip() for s in args.assets.split(",") if s.strip()]:
        try:
            summaries.append(
                _run_one_asset(
                    a, storage, output, args.bootstrap_n_resamples
                )
            )
        except Exception as exc:  # keep per-asset failures non-fatal
            log.exception("asset %s failed: %s", a, exc)
            summaries.append({"asset": a, "error": str(exc)})

    summary_path = output / "a3b_tsmom_summary.json"
    summary_path.write_text(json.dumps(summaries, indent=2))
    log.info("summary: %s", summary_path)

    any_pass = any(s.get("n_pass", 0) > 0 for s in summaries)
    return 0 if any_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
