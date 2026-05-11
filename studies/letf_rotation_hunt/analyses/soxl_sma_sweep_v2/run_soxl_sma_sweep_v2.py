"""SOXL SMA sweep v2 — SMH signals + SOXL positions, real Tiingo data 2010-04+.

Corrects the methodological error in v1 (which used QQQSIM proxy for SOXL signals)
by using real SMH (1x SOX) for the signal computation and real SOXL (3x SOX) for
position returns. Analogous to: TQQQ signals from QQQ, UPRO signals from SPY.

Citations:
  - [trading_systems_methods, Kaufman ch.21] SMA scaling for vol regimes
  - [advances_fin_ml, p.275] Sortino in metric family
  - Sister: sortino_reanalysis (Sortino > Sharpe for LETF rotation)
  - Methodology: signals on 1x underlying matches parent study LETF_TESTFOLIO
    convention for QLD (signals from QQQSIM=NDX 1x) and UPRO (signals from
    SPYSIM=SPX 1x). SOXL signals from QQQSIM was a proxy mistake; corrected here.
"""
from __future__ import annotations

import argparse
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import (
    load_testfolio_series,
    load_tiingo_real_etf,
)
from studies.letf_rotation_hunt.core.signals import (
    ar1_coefficient,
    realized_vol_gate,
)
from studies.letf_rotation_hunt.analyses.sortino_reanalysis.recompute import _annualised_sharpe
from studies.letf_rotation_hunt.analyses.sortino_reanalysis.sortino_metric import (
    _annualised_sortino,
)
from studies.letf_rotation_hunt.analyses.threshold_sweep.threshold_signals import (
    sma_gate_with_buffer,
)

SMA_LONG_GRID = [100, 125, 150, 175, 200, 250]
SMA_SHORT_GRID = [25, 50, 75, 100]
VOL_WINDOW = 21
VOL_THRESHOLD = 0.30  # SMH 1x SOX class — scaled from canonical 0.40 (QLD 2x NDX)
AR1_WINDOW = 30
SMABUF = 0.05  # 5%, per Sortino-winner threshold_sweep finding


def _compute_signal(
    smh_prices: pd.Series,
    sma_long: int,
    sma_short: int,
) -> pd.Series:
    """Compute T3d K=2 Vote-of-K signal on SMH (1x SOX).

    4 sub-signals:
      s1: price > SMA(long) with smabuf=5% hysteresis
      s2: price > SMA(short) with smabuf=5% hysteresis
      s3: realized_vol(21d) < 0.30 (annualized)
      s4: AR(1)(30d) > 0

    ON when K >= 2 of the 4 are TRUE. [trading_systems_methods, Kaufman ch.21]
    """
    smh_returns = smh_prices.pct_change().dropna()

    # Signal 1: price > SMA(long) with smabuf [threshold_sweep; systematic_trading, Carver p.174]
    s1_raw = sma_gate_with_buffer(
        smh_prices, period=sma_long,
        on_threshold=SMABUF, off_threshold=SMABUF,
    )
    # Signal 2: price > SMA(short) with smabuf
    s2_raw = sma_gate_with_buffer(
        smh_prices, period=sma_short,
        on_threshold=SMABUF, off_threshold=SMABUF,
    )
    # Signal 3: realized vol < threshold [leverage_for_the_long_run, p.5-6]
    s3_raw = realized_vol_gate(smh_returns, window=VOL_WINDOW, threshold=VOL_THRESHOLD)
    # Signal 4: AR(1) > 0 [paper.hsieh_2025_letf_compounding]
    ar1 = ar1_coefficient(smh_returns, window=AR1_WINDOW)
    s4_raw = (ar1 > 0).astype(float)
    s4_raw[ar1.isna()] = np.nan

    # Align all 4 signals on the same index
    df = pd.DataFrame({
        "s1": s1_raw,
        "s2": s2_raw,
        "s3": s3_raw,
        "s4": s4_raw,
    }).dropna()
    k_count = df.sum(axis=1)
    signal = (k_count >= 2).astype(float)
    signal.name = "signal_on"
    return signal


def _backtest_combo(
    soxl_prices: pd.Series,
    zroz_prices: pd.Series,
    smh_prices: pd.Series,
    sma_long: int,
    sma_short: int,
) -> dict | None:
    """Run one (sma_long, sma_short) combo. Returns metrics dict or None."""
    signal = _compute_signal(smh_prices, sma_long, sma_short)
    soxl_ret = soxl_prices.pct_change().dropna()
    zroz_ret = zroz_prices.pct_change().dropna()

    # Align on common dates: signal index & soxl & zroz
    common = signal.index.intersection(soxl_ret.index).intersection(zroz_ret.index)
    if len(common) < 252:
        return None
    sig = signal.loc[common]
    sret = soxl_ret.loc[common]
    zret = zroz_ret.loc[common]

    # Strategy returns: signal[t-1] (lagged 1 day to avoid lookahead) drives returns[t]
    sig_lag = sig.shift(1).fillna(0.0)
    strat_ret = sig_lag * sret + (1 - sig_lag) * zret
    strat_ret = strat_ret.dropna()
    if len(strat_ret) < 252:
        return None

    equity = (1.0 + strat_ret).cumprod() * 10_000.0

    # Trade count: number of signal flips (ON<->OFF transitions)
    flips = int((sig_lag != sig_lag.shift(1)).fillna(False).sum())

    n_years = (equity.index[-1] - equity.index[0]).days / 365.25
    cagr = (
        (equity.iloc[-1] / equity.iloc[0]) ** (1 / n_years) - 1
        if n_years > 0
        else float("nan")
    )
    rolling_max = equity.cummax()
    mdd = float(((equity - rolling_max) / rolling_max).min())

    return {
        "sma_long": sma_long,
        "sma_short": sma_short,
        "sortino": float(_annualised_sortino(strat_ret, target=0.0)),
        "sharpe": float(_annualised_sharpe(strat_ret)),
        "cagr": float(cagr),
        "mdd": mdd,
        "trade_count": flips,
        "final_equity": float(equity.iloc[-1]),
        "n_obs": len(strat_ret),
        "start_date": str(equity.index[0].date()),
        "end_date": str(equity.index[-1].date()),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="SOXL SMA sweep v2 -- SMH signals + SOXL positions"
    )
    parser.add_argument(
        "--out-data-dir",
        type=Path,
        default=Path("data/soxl_sma_sweep_v2"),
    )
    parser.add_argument(
        "--out-report-dir",
        type=Path,
        default=Path("studies/letf_rotation_hunt/reports/soxl_sma_sweep_v2"),
    )
    args = parser.parse_args(argv)
    args.out_data_dir.mkdir(parents=True, exist_ok=True)
    args.out_report_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print("[soxl_sma_sweep_v2] loading SMH (signals — 1x SOX, real Tiingo)")
    smh = load_tiingo_real_etf("SMH")
    print(
        f"[soxl_sma_sweep_v2]   SMH: {len(smh)} rows, "
        f"{smh.index[0].date()} to {smh.index[-1].date()}"
    )

    print("[soxl_sma_sweep_v2] loading SOXL (positions — 3x SOX, real Tiingo)")
    soxl = load_tiingo_real_etf("SOXL")
    print(
        f"[soxl_sma_sweep_v2]   SOXL: {len(soxl)} rows, "
        f"{soxl.index[0].date()} to {soxl.index[-1].date()}"
    )

    print("[soxl_sma_sweep_v2] loading ZROZ (off-state, testfolio sim)")
    zroz = load_testfolio_series("ZROZSIM")
    print(
        f"[soxl_sma_sweep_v2]   ZROZ: {len(zroz)} rows, "
        f"{zroz.index[0].date()} to {zroz.index[-1].date()}"
    )

    # Run sweep
    valid_combos = [
        (L, S) for L, S in product(SMA_LONG_GRID, SMA_SHORT_GRID) if S < L
    ]
    print(f"[soxl_sma_sweep_v2] running {len(valid_combos)} combos")
    print(
        f"[soxl_sma_sweep_v2] params: vol_threshold={VOL_THRESHOLD}, "
        f"smabuf={SMABUF}, ar1_window={AR1_WINDOW}, vol_window={VOL_WINDOW}"
    )

    rows: list[dict] = []
    for i, (sma_long, sma_short) in enumerate(valid_combos, start=1):
        print(
            f"[soxl_sma_sweep_v2] [{i}/{len(valid_combos)}] "
            f"sma{sma_long}/{sma_short}"
        )
        m = _backtest_combo(soxl, zroz, smh, sma_long, sma_short)
        if m is None:
            print("[soxl_sma_sweep_v2]   skip: insufficient data")
            continue
        rows.append(m)
        print(
            f"[soxl_sma_sweep_v2]   sortino={m['sortino']:.3f} "
            f"sharpe={m['sharpe']:.3f} cagr={m['cagr']:.1%} "
            f"mdd={m['mdd']:.1%} trades={m['trade_count']} "
            f"window={m['start_date']}..{m['end_date']}"
        )

    if not rows:
        print("[soxl_sma_sweep_v2] ERROR: no valid combos")
        return 1

    df = pd.DataFrame(rows)
    csv_path = args.out_data_dir / "sweep_metrics.csv"
    df.to_csv(csv_path, index=False)
    print(f"[soxl_sma_sweep_v2] CSV: {csv_path} ({len(df)} rows)")

    # Heatmap
    import matplotlib.pyplot as plt

    pivot = df.pivot(index="sma_long", columns="sma_short", values="sortino")
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(pivot.values, cmap="RdYlGn", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_xlabel("SMA short")
    ax.set_ylabel("SMA long")
    start = df["start_date"].min()
    end = df["end_date"].max()
    ax.set_title(
        f"SOXL/ZROZ rotation - Sortino by SMA(long, short)\n"
        f"Signal: SMH (1x SOX), Position: SOXL (3x SOX), "
        f"vol_thresh={VOL_THRESHOLD}, smabuf={SMABUF}\n"
        f"Window: {start} to {end}"
    )
    plt.colorbar(im, ax=ax, label="Sortino")
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            v = pivot.values[i, j]
            if not np.isnan(v):
                ax.text(
                    j, i, f"{v:.2f}", ha="center", va="center",
                    color="black", fontsize=8,
                )
    fig.tight_layout()
    heatmap_path = args.out_report_dir / "sortino_heatmap.png"
    fig.savefig(heatmap_path, dpi=120)
    plt.close(fig)
    print(f"[soxl_sma_sweep_v2] heatmap: {heatmap_path}")

    # Top 5
    top = df.sort_values("sortino", ascending=False).head(5)
    print(f"\n[soxl_sma_sweep_v2] === Top 5 by Sortino ===")
    print(
        top[
            [
                "sma_long", "sma_short", "sortino", "sharpe",
                "cagr", "mdd", "trade_count", "start_date", "end_date",
            ]
        ].to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
