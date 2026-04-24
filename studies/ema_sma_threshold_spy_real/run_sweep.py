"""Run the EMA/SMA threshold sweep on REAL SPY data (Tiingo).

Buy legs use real ETF returns:
  - buy_leverage = 1.0 -> SPY
  - buy_leverage = 2.0 -> SSO
  - buy_leverage = 3.0 -> UPRO

Sell legs: 0 = cash; -1/-2/-3 = synth inverse of real SPY returns
(inverse LETFs SH/SDS/SPXU are absent from Tiingo cache).

Effective data window: UPRO inception 2009-06-26 → today (~17 years).

Usage
-----

    .venv/bin/python studies/ema_sma_threshold_spy_real/run_sweep.py
    .venv/bin/python studies/ema_sma_threshold_spy_real/run_sweep.py --smoke
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from ai_trade.backtest.grid.ema_sma_threshold_grid import EMASMAThresholdAxes
from ai_trade.backtest.grid.real_etf_regime_runner import (
    SPY_MARKET,
    build_data_bundle,
)
from ai_trade.backtest.grid.real_etf_report_helpers import emit_all_artifacts

STUDY_DIR = Path(__file__).parent
LOG_PATH = Path("logs/ema_sma_threshold_spy_real.log")


def _setup_logging() -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("spy_real")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
    fh.setFormatter(fmt); logger.addHandler(fh)
    return logger


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--skip-gates", action="store_true")
    parser.add_argument("--top-k", type=int, default=20)
    args = parser.parse_args()

    log = _setup_logging()
    start = time.time()

    if args.smoke:
        axes = EMASMAThresholdAxes.smoke()
    elif args.full:
        axes = EMASMAThresholdAxes.full()
    else:
        axes = EMASMAThresholdAxes()
    top_k = min(args.top_k, axes.n_configs)

    log.info("Loading real SPY/SSO/UPRO from Tiingo...")
    bundle = build_data_bundle(
        SPY_MARKET, leverages_used=tuple(axes.buy_leverages),
    )
    meta = bundle["_meta"]
    log.info("Data window: %s -> %s (%d bars, ~%.1fy)",
             meta["start"].date(), meta["end"].date(),
             meta["n_bars"], meta["n_bars"] / 252)
    log.info("Running sweep: %d configs x 2 tax regimes (apply_gates=%s)...",
             axes.n_configs, not args.skip_gates)
    emit_all_artifacts(
        axes=axes, market=SPY_MARKET, bundle=bundle,
        study_dir=STUDY_DIR,
        apply_gates=not args.skip_gates,
        top_k=top_k,
    )

    readme = [
        "# EMA/SMA Threshold Crossover — REAL SPY data (Tiingo)\n",
        "> Real-ETF validation of the SPYSIM synth study. Buy leg uses "
        "actual UPRO/SSO/SPY returns from Tiingo. Sell leg with L<0 uses "
        "synth inverse of real SPY (inverse LETFs not cached).\n",
        "## Contents",
        "- `SPEC.md` — spec aligned with the synth study.",
        "- `FINAL.md` — top-20 ranked (pure + tax15) + narrative.",
        "- `configs.csv` — every config's metrics + gates.",
        "- `summary.json` — axes + top-K machine-readable.",
        "- `configs/NN_<cfg_id>/` — per-config: summary.md, equity.png, trades.csv.",
        "- `analyses/` — supplementary studies (equity-vs-benchmark, rolling windows).\n",
        "## Usage\n```bash",
        ".venv/bin/python studies/ema_sma_threshold_spy_real/run_sweep.py",
        ".venv/bin/python studies/ema_sma_threshold_spy_real/run_sweep.py --smoke",
        "```\n",
        f"Data source: `data/tiingo/daily/prices/` (SPY, SSO 2006+, UPRO 2009+). "
        f"Effective start: {meta['start'].date()} due to UPRO inception.\n",
    ]
    (STUDY_DIR / "README.md").write_text("\n".join(readme), encoding="utf-8")
    log.info("Done. Artifacts at %s", STUDY_DIR.resolve())
    log.info("Total wall time: %.1fs", time.time() - start)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
