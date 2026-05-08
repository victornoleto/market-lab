"""SMA long x short sweep on SOXL + SMH (spec: Q2 from session 2026-05-07).

Goal: find best SMA combo for "faster assets" (high-vol LETFs).

Data availability:
  - SOXL: supported natively in run_iter_t3.LETF_TESTFOLIO (QQQSIM re-synth 3x)
  - SMH: NOT in testfolio cache (no SMHSIM). Proxy: QQQSIM with leverage=1.0
    (SMH = 1x VanEck Semiconductor ETF; closest proxy is QQQ/NDX).
    Note: QQQSIM@1x is a very rough proxy for SMH; it serves only as a
    sanity check that 1x semiconductors pick different SMA optima than 3x.

Citations:
  - [trading_systems_methods, Kaufman ch.21] SMA period scaling for vol regime
  - [advances_fin_ml, p.275] Sortino in metric family
  - Parent: sortino_reanalysis identified sma250/100 as winner for canonical
    (2x NDX vol class). This sweep finds the analogous winner for SOXL/SMH.
"""
from __future__ import annotations

import argparse
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

import studies.letf_rotation_hunt.run_iter_t3 as _t3_module
from studies.letf_rotation_hunt.data_loader import (
    load_ffr_daily,
    load_testfolio_series,
)
from studies.letf_rotation_hunt.run_iter_t1 import DATASET_WINDOWS
from studies.letf_rotation_hunt.run_iter_t3 import _run_single_composite_config
from studies.letf_rotation_hunt.sortino_reanalysis.recompute import (
    _annualised_sharpe,
    _slice_by_dataset,
)
from studies.letf_rotation_hunt.sortino_reanalysis.sortino_metric import (
    _annualised_sortino,
)
from studies.letf_rotation_hunt.synths import (
    LETF_EXPENSE_RATIOS,
    LETF_LEVERAGE,
)

SMA_LONG_GRID = [100, 125, 150, 175, 200, 250]
SMA_SHORT_GRID = [25, 50, 75, 100]

# SMH proxy: 1x QQQSIM (nearest available proxy for 1x semiconductor ETF)
# SMH ER: VanEck Semiconductor ETF, ER = 0.35% (prospectus 2024)
_SMH_ER = 0.0035
_SMH_LEVERAGE = 1.0


def _patch_smh_support() -> None:
    """Add SMH to run_iter_t3 module-level dicts so _resolve_asset_returns works.

    SMH is proxied by QQQSIM with leverage=1.0 and ER=0.35%.
    This is a rough proxy (QQQ vs. SOX index) but suitable for a sanity check.
    """
    # Patch LETF_TESTFOLIO in run_iter_t3 so _resolve_asset_returns("SMH") works
    if "SMH" not in _t3_module.LETF_TESTFOLIO:
        _t3_module.LETF_TESTFOLIO["SMH"] = ("QQQSIM", False)
    # Patch synths module-level dicts so letf_synth_by_ticker("SMH") works
    if "SMH" not in LETF_EXPENSE_RATIOS:
        LETF_EXPENSE_RATIOS["SMH"] = _SMH_ER
    if "SMH" not in LETF_LEVERAGE:
        LETF_LEVERAGE["SMH"] = _SMH_LEVERAGE


def _make_cfg(asset: str, sma_long: int, sma_short: int) -> dict:
    return {
        "name": f"{asset.lower()}_voteK2_sma{sma_long}_{sma_short}_vol21_40_ar30_off_zroz",
        "on_asset": asset,
        "off_asset": "ZROZ",
        "signal_type": "vote_of_k",
        "k": 2,
        "sma_long_period": sma_long,
        "sma_short_period": sma_short,
        "vol_window": 21,
        "vol_threshold": 0.40,
        "ar1_window": 30,
        "sma_long_buffer_on": 0.05,
        "sma_long_buffer_off": 0.05,
        "sma_short_buffer_on": 0.05,
        "sma_short_buffer_off": 0.05,
        "ar1_buffer": 0.0,
    }


def _trade_count(positions: pd.DataFrame, on_asset: str) -> int:
    """Count ON<->OFF flips by tracking when on_asset weight goes from 0 to >0 or vice versa."""
    if on_asset not in positions.columns:
        return 0
    on_w = positions[on_asset]
    is_on = on_w > 0.5
    flips = (is_on != is_on.shift(1)).fillna(False).sum()
    return int(flips)


def run_sweep(asset: str, ffr_daily: pd.Series) -> list[dict]:
    """Run all valid SMA combos for one asset on lh_56y."""
    rows: list[dict] = []
    valid_combos = [(L, S) for L, S in product(SMA_LONG_GRID, SMA_SHORT_GRID) if S < L]
    for i, (sma_long, sma_short) in enumerate(valid_combos, start=1):
        cfg = _make_cfg(asset, sma_long, sma_short)
        print(
            f"[soxl_sma_sweep] [{asset}] [{i}/{len(valid_combos)}] "
            f"sma{sma_long}/{sma_short}"
        )
        try:
            result = _run_single_composite_config(
                cfg,
                datasets=["lh_56y"],
                ffr_daily=ffr_daily,
                n_trials_local=len(valid_combos),
            )
        except Exception as e:
            print(f"[soxl_sma_sweep]   skip: {e}")
            continue

        full_eq = result["_equity"]
        full_ret = result["_strategy_returns"]
        positions = result["_positions"]
        ds_eq, ds_ret = _slice_by_dataset(full_eq, full_ret, "lh_56y")

        if len(ds_ret) < 252:
            print(
                f"[soxl_sma_sweep]   skip: insufficient lh_56y data ({len(ds_ret)} rows)"
            )
            continue

        n_years = (ds_eq.index[-1] - ds_eq.index[0]).days / 365.25
        cagr = (
            (ds_eq.iloc[-1] / ds_eq.iloc[0]) ** (1 / n_years) - 1
            if n_years > 0
            else float("nan")
        )
        rolling_max = ds_eq.cummax()
        mdd = float(((ds_eq - rolling_max) / rolling_max).min())
        rows.append(
            {
                "asset": asset,
                "sma_long": sma_long,
                "sma_short": sma_short,
                "sortino": _annualised_sortino(ds_ret, target=0.0),
                "sharpe": _annualised_sharpe(ds_ret),
                "cagr": float(cagr),
                "mdd": mdd,
                "trade_count": _trade_count(positions, asset),
                "final_equity": float(ds_eq.iloc[-1]),
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SOXL/SMH SMA sweep")
    parser.add_argument(
        "--out-data-dir",
        type=Path,
        default=Path("data/soxl_sma_sweep"),
    )
    parser.add_argument(
        "--out-report-dir",
        type=Path,
        default=Path("studies/letf_rotation_hunt/reports/soxl_sma_sweep"),
    )
    args = parser.parse_args(argv)
    args.out_data_dir.mkdir(parents=True, exist_ok=True)
    args.out_report_dir.mkdir(parents=True, exist_ok=True)

    # Patch SMH into module-level dicts before any dispatching
    _patch_smh_support()

    ffr_daily = load_ffr_daily()

    print("[soxl_sma_sweep] === SOXL ===")
    rows = run_sweep("SOXL", ffr_daily)
    print(f"[soxl_sma_sweep] SOXL: {len(rows)} valid rows")

    print("[soxl_sma_sweep] === SMH ===")
    rows += run_sweep("SMH", ffr_daily)
    n_smh = sum(1 for r in rows if r["asset"] == "SMH")
    print(f"[soxl_sma_sweep] SMH: {n_smh} valid rows (total {len(rows)})")

    df = pd.DataFrame(rows)
    csv_path = args.out_data_dir / "sweep_metrics.csv"
    df.to_csv(csv_path, index=False)
    print(f"[soxl_sma_sweep] CSV: {csv_path}")

    # Heatmap (one per asset)
    import matplotlib.pyplot as plt

    for asset in ["SOXL", "SMH"]:
        sub = df[df["asset"] == asset]
        if sub.empty:
            continue
        pivot = sub.pivot(index="sma_long", columns="sma_short", values="sortino")
        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(pivot.values, cmap="RdYlGn", aspect="auto")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        ax.set_xlabel("SMA short")
        ax.set_ylabel("SMA long")
        ax.set_title(
            f"{asset} -- Sortino by SMA(long, short) | lh_56y gross | smabuf 5% | vol<40%"
        )
        plt.colorbar(im, ax=ax, label="Sortino")
        # annotate cells
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                v = pivot.values[i, j]
                if not np.isnan(v):
                    ax.text(
                        j, i, f"{v:.2f}", ha="center", va="center",
                        color="black", fontsize=8,
                    )
        fig.tight_layout()
        heatmap_path = args.out_report_dir / f"{asset.lower()}_sortino_heatmap.png"
        fig.savefig(heatmap_path, dpi=120)
        plt.close(fig)
        print(f"[soxl_sma_sweep] Heatmap: {heatmap_path}")

    # Top 5 per asset
    for asset in ["SOXL", "SMH"]:
        sub = df[df["asset"] == asset].sort_values("sortino", ascending=False)
        print(f"\n[soxl_sma_sweep] === {asset} top 5 by Sortino ===")
        print(
            sub[["sma_long", "sma_short", "sortino", "sharpe", "cagr", "mdd", "trade_count"]]
            .head(5)
            .to_string(index=False)
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
