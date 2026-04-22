"""Plot B3-SSO-static-quarterly equity curve vs SPY buy-hold.

Produces reports/phase_3_8/b3_pauchlyova/plot_b3_vs_spy_bh.png showing
three equity paths over 2004-11-18 → 2026-04-15 (GLD inception-limited
full window):

1. B3-SSO-static-quarterly (post-DARF 15% year-end) — the candidate.
2. SPY buy-hold raw (pre-tax) — traditional benchmark.
3. SPY buy-hold post-DARF 15% year-end — apples-to-apples rota B Inter.

Vertical bands mark the IS / OOS / FWD boundaries used in the Phase 3.8-1
honest validation (IS 2004-11-18→2015-12-31 / OOS 2016-01-01→2020-12-31 /
FWD 2021-01-01→2026-04-15).

Usage
-----

    .venv/bin/python scripts/phase3_8/plot_b3_vs_spy_bh.py

Output
------

- `reports/phase_3_8/b3_pauchlyova/plot_b3_vs_spy_bh.png` (1600×900 dpi=140)
- Terminal summary: CAGR/MDD/final equity for each series per window
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ai_trade.backtest.data.spx_tr_loader import fetch_ken_french_daily  # noqa: E402
from ai_trade.backtest.helpers.synthetic_letf import (  # noqa: E402
    TRADING_DAYS_PER_YEAR,
    synthesize_letf_returns_ffr_aware,
)
from ai_trade.backtest.strategies.phase3_8_b3_pauchlyova_static_trend import (  # noqa: E402
    B3Config,
    simulate_b3,
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "tiingo" / "daily" / "prices"
OUT_PNG = ROOT / "reports" / "phase_3_8" / "b3_pauchlyova" / "plot_b3_vs_spy_bh.png"

FULL_START = pd.Timestamp("2004-11-18")
FULL_END = pd.Timestamp("2026-04-15")
IS_END = pd.Timestamp("2015-12-31")
OOS_END = pd.Timestamp("2020-12-31")


def _load_adj_close(path: Path) -> pd.Series:
    df = pd.read_parquet(path)
    s = df["adj_close"].astype(float)
    s.index = pd.DatetimeIndex(s.index)
    return s.sort_index()


def build_panel() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    spy = _load_adj_close(DATA / "SPY.parquet").loc[FULL_START:FULL_END]
    sso = _load_adj_close(DATA / "SSO.parquet")
    tlt = _load_adj_close(DATA / "TLT.parquet").loc[FULL_START:FULL_END]
    gld = _load_adj_close(DATA / "GLD.parquet").loc[FULL_START:FULL_END]
    shv = _load_adj_close(DATA / "SHV.parquet")

    common = spy.index.intersection(tlt.index).intersection(gld.index)
    common = pd.DatetimeIndex(sorted(common))

    spy_ret = spy.reindex(common).pct_change().fillna(0.0)
    tlt_ret = tlt.reindex(common).pct_change().fillna(0.0)
    gld_ret = gld.reindex(common).pct_change().fillna(0.0)

    kf = fetch_ken_french_daily()
    ffr_annual = (kf["rf"].astype(float) * TRADING_DAYS_PER_YEAR).reindex(common).ffill().bfill()

    sso_real = sso.reindex(common).pct_change()
    sso_real_start = pd.Timestamp("2006-06-21")
    sso_synth = synthesize_letf_returns_ffr_aware(
        spy_ret, leverage=2.0, ffr_annualized=ffr_annual, expense_ratio=0.0095
    )
    sso_stitched = sso_synth.copy()
    mask = (common >= sso_real_start) & sso_real.notna()
    sso_stitched.loc[mask] = sso_real.loc[mask].astype(float)
    sso_stitched = sso_stitched.fillna(0.0)

    shv_raw = shv.reindex(common)
    shv_ret = shv_raw.pct_change()
    cash_daily = 0.04 / 252.0
    shv_ret = shv_ret.fillna(cash_daily)

    # Column name is "LETF" (generic) per B3Config.base_allocation keys.
    returns = pd.DataFrame(
        {"LETF": sso_stitched, "TLT": tlt_ret, "SPY": spy_ret, "GLD": gld_ret, "SHV": shv_ret},
        index=common,
    )

    spy_px = spy.reindex(common).ffill()
    letf_px_synth = (1.0 + sso_stitched).cumprod() * 100.0
    tlt_px = tlt.reindex(common).ffill()
    gld_px = gld.reindex(common).ffill()
    shv_px = shv_raw.ffill()
    if shv_px.isna().any():
        shv_px = shv_px.bfill()

    prices = pd.DataFrame(
        {"LETF": letf_px_synth, "TLT": tlt_px, "SPY": spy_px, "GLD": gld_px, "SHV": shv_px},
        index=common,
    )
    return returns, prices, spy_ret


def spy_buyhold_with_darf(spy_ret: pd.Series, tax_rate: float = 0.15) -> pd.Series:
    """SPY buy-hold equity curve with 15% DARF year-end realization.

    Simulates: on each Dec-31 (or last trading day of year), realize
    calendar-year gain; if positive, subtract tax_rate * realized gain.
    Losses within year net out; no cross-year carry. Applied as an
    equity step-down on the year-end day.
    """
    eq = (1.0 + spy_ret).cumprod()
    years = eq.index.year
    adjusted = eq.copy()
    year_start_eq = float(eq.iloc[0]) / float(1.0 + spy_ret.iloc[0])  # equity before first bar = 1
    running_tax = 0.0
    prev_year = int(years[0])
    year_start_val = 1.0
    out = []
    eq_running = 1.0
    for i, (dt, r) in enumerate(spy_ret.items()):
        eq_running = eq_running * (1.0 + float(r))
        y = dt.year
        is_last_of_year = (i == len(spy_ret) - 1) or (spy_ret.index[i + 1].year != y)
        if is_last_of_year:
            gain = eq_running - year_start_val
            if gain > 0:
                eq_running = eq_running - tax_rate * gain
            year_start_val = eq_running
        out.append(eq_running)
    return pd.Series(out, index=spy_ret.index, name="SPY_BH_post_DARF")


def cagr_mdd(eq: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> tuple[float, float, float]:
    sub = eq.loc[start:end]
    if len(sub) < 2:
        return 0.0, 0.0, float(sub.iloc[-1]) if len(sub) else 1.0
    years = (sub.index[-1] - sub.index[0]).days / 365.25
    cagr = (float(sub.iloc[-1]) / float(sub.iloc[0])) ** (1.0 / years) - 1.0
    peak = sub.cummax()
    mdd = float((sub / peak - 1.0).min())
    return cagr, mdd, float(sub.iloc[-1])


def main() -> int:
    print("Loading panel…")
    returns, prices, spy_ret = build_panel()
    print(f"Panel: {returns.index.min().date()} → {returns.index.max().date()}  n={len(returns)}")

    print("Running B3-SSO-static-quarterly on full window…")
    cfg = B3Config(
        letf_kind="SSO",
        trend_filter_on=False,
        rebal_cadence="quarterly",
        sma_period=200,
        tax_rate=0.15,
        commission_bps=0.0,
        spread_bps=5.0,
    )
    res = simulate_b3(returns, prices, cfg)
    b3_eq = res.equity

    print("Computing SPY buy-hold (raw + post-DARF)…")
    spy_bh_raw = (1.0 + spy_ret).cumprod()
    spy_bh_tax = spy_buyhold_with_darf(spy_ret, tax_rate=0.15)

    # --- Summary stats per window ---
    windows = [
        ("IS  (2004-11 → 2015-12)", FULL_START, IS_END),
        ("OOS (2016-01 → 2020-12)", IS_END + pd.Timedelta(days=1), OOS_END),
        ("FWD (2021-01 → 2026-04)", OOS_END + pd.Timedelta(days=1), FULL_END),
        ("FULL (2004-11 → 2026-04)", FULL_START, FULL_END),
    ]
    print()
    print(f"{'Window':<30}{'Series':<26}{'CAGR':>8}{'MDD':>10}{'Final':>10}")
    print("-" * 84)
    for label, s, e in windows:
        for name, eq in [
            ("B3-SSO-static-quarterly", b3_eq),
            ("SPY buy-hold (raw)    ", spy_bh_raw),
            ("SPY buy-hold (post-DARF)", spy_bh_tax),
        ]:
            cagr, mdd, final = cagr_mdd(eq, s, e)
            print(f"{label:<30}{name:<26}{cagr*100:>7.2f}%{mdd*100:>9.2f}%{final:>9.3f}x")
        print()

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(16, 9), dpi=140)

    ax.plot(b3_eq.index, b3_eq.values, label="B3-SSO-static-quarterly (post-DARF)",
            color="#1f77b4", linewidth=1.6)
    ax.plot(spy_bh_tax.index, spy_bh_tax.values, label="SPY buy-hold (post-DARF, rota B Inter)",
            color="#ff7f0e", linewidth=1.2, linestyle="--")
    ax.plot(spy_bh_raw.index, spy_bh_raw.values, label="SPY buy-hold (raw, pre-tax)",
            color="#2ca02c", linewidth=1.0, linestyle=":", alpha=0.75)

    ax.set_yscale("log")
    ax.set_ylabel("Equity (log scale, starting at 1.00)")
    ax.set_xlabel("Date")
    ax.set_title("B3 Pauchlyova static-SSO-quarterly vs SPY buy-hold\n"
                 "Full window 2004-11-18 → 2026-04-15  —  Phase 3.8-1 honest validation")

    # IS/OOS/FWD vertical bands
    ax.axvspan(FULL_START, IS_END, alpha=0.06, color="gray", label="_IS")
    ax.axvspan(IS_END, OOS_END, alpha=0.10, color="gold", label="_OOS")
    ax.axvspan(OOS_END, FULL_END, alpha=0.08, color="salmon", label="_FWD")

    # Annotate window labels
    for label, s, e, y_pos in [
        ("IS",  FULL_START, IS_END, 0.93),
        ("OOS", IS_END,     OOS_END, 0.93),
        ("FWD", OOS_END,    FULL_END, 0.93),
    ]:
        mid = s + (e - s) / 2
        ax.text(mid, y_pos, label, transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=11, fontweight="bold",
                color="#555555",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#bbbbbb", alpha=0.85))

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="upper left", fontsize=10, framealpha=0.9)

    # Stats annotation box
    full_b3 = cagr_mdd(b3_eq, FULL_START, FULL_END)
    full_spy_tax = cagr_mdd(spy_bh_tax, FULL_START, FULL_END)
    full_spy_raw = cagr_mdd(spy_bh_raw, FULL_START, FULL_END)
    stats_text = (
        f"FULL window stats:\n"
        f"  B3-SSO-static-qtr:      CAGR {full_b3[0]*100:5.2f}%  MDD {full_b3[1]*100:6.2f}%  final {full_b3[2]:5.2f}x\n"
        f"  SPY BH post-DARF:       CAGR {full_spy_tax[0]*100:5.2f}%  MDD {full_spy_tax[1]*100:6.2f}%  final {full_spy_tax[2]:5.2f}x\n"
        f"  SPY BH raw (pre-tax):   CAGR {full_spy_raw[0]*100:5.2f}%  MDD {full_spy_raw[1]*100:6.2f}%  final {full_spy_raw[2]:5.2f}x"
    )
    ax.text(0.02, 0.02, stats_text, transform=ax.transAxes,
            ha="left", va="bottom", fontsize=9, family="monospace",
            bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#999999", alpha=0.92))

    fig.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, bbox_inches="tight")
    print(f"\nSaved: {OUT_PNG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
