"""Phase 4.0 T4 — Full gates battery on T3 substituted backtest.

Runs (per Phase 4.0 spec §3 T4):
* Bootstrap 99.9% CI stationary block (10k resamples) on full returns
* Walk-forward 8-window profitable ratio + max-window DD
* FWD Sharpe > 0 check
* Median hold ≥ 3 days
* CAGR / Sharpe / MDD OOS gates
* IR vs SPY (compare OOS to SPY buy&hold same window)

PBO and DSR are intentionally skipped because n_trials=1 trivializes
both (PBO needs cross-config matrix; DSR's n_trials correction
collapses to standard Sharpe t-test). Bootstrap 99.9% CI low > 0 is
the primary robustness gate.

Output:
  reports/phase4_0/index_cfd_validation/AGGREGATE.md
  reports/phase4_0/index_cfd_validation/gates.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ai_trade.backtest.grid.letf_rotation_b1c import bootstrap_sharpe_ci  # noqa: E402
from ai_trade.backtest.metrics.standard_report import (  # noqa: E402
    build_spy_benchmark,
    load_spy_series,
)

OUT_DIR = Path("reports/phase4_0/index_cfd_validation")

OOS_START = pd.Timestamp("2018-01-01")
OOS_END = pd.Timestamp("2023-12-31")


def _sharpe(ret: pd.Series) -> float:
    r = ret.dropna()
    if len(r) < 2 or r.std() == 0:
        return 0.0
    return float(r.mean() / r.std() * np.sqrt(252))


def _cagr(ret: pd.Series) -> float:
    r = ret.dropna()
    if len(r) < 2:
        return 0.0
    eq = (1.0 + r).cumprod()
    years = len(r) / 252.0
    return float(eq.iloc[-1] ** (1.0 / years) - 1.0)


def _walk_forward(ret: pd.Series, n_windows: int = 8) -> tuple[float, float, bool]:
    r = ret.dropna().loc[ret != 0.0]
    size = len(r) // n_windows
    profitable = 0
    max_dd = 0.0
    for i in range(n_windows):
        w = r.iloc[i * size:(i + 1) * size]
        if w.empty:
            continue
        eq = (1.0 + w).cumprod()
        wdd = float((eq / eq.cummax() - 1.0).min())
        if eq.iloc[-1] > 1.0:
            profitable += 1
        if abs(wdd) > abs(max_dd):
            max_dd = wdd
    ratio = profitable / n_windows
    return ratio, abs(max_dd), (ratio >= 6 / 8 and abs(max_dd) <= 0.25)


def _information_ratio(
    strategy_ret: pd.Series, bench_ret: pd.Series, periods_per_year: int = 252
) -> float:
    """Annualized IR of strategy vs benchmark on common window."""
    common = strategy_ret.index.intersection(bench_ret.index)
    s = strategy_ret.reindex(common).fillna(0.0)
    b = bench_ret.reindex(common).fillna(0.0)
    diff = s - b
    if diff.std() == 0:
        return 0.0
    return float(diff.mean() / diff.std() * np.sqrt(periods_per_year))


def main() -> None:
    print("=" * 72)
    print("Phase 4.0 T4 — Gates battery on Index CFD substituted backtest")
    print("=" * 72)

    summary = json.loads((OUT_DIR / "summary.json").read_text())
    ret = pd.read_parquet(OUT_DIR / "daily_returns.parquet")["ret"].astype(float)
    ret.index = pd.DatetimeIndex(ret.index)

    oos_ret = ret.loc[(ret.index >= OOS_START) & (ret.index <= OOS_END)]
    print(f"\nLoaded daily returns: {len(ret)} bars | OOS slice: {len(oos_ret)} bars")

    # ----------------------------------------------------------------------
    # Gate 1 — Bootstrap 99.9% CI on full returns
    # ----------------------------------------------------------------------
    print("\n[1/6] Bootstrap 99.9% CI (stationary block=5, n_resamples=10000)...")
    ci_low, ci_high = bootstrap_sharpe_ci(
        ret, alpha=0.001, block_mean=5, n_resamples=10000, seed=42
    )
    gate_bootstrap = ci_low > 0
    print(f"  CI [99.9%]: [{ci_low:.3f}, {ci_high:.3f}]  "
          f"{'✅' if gate_bootstrap else '❌'} (need low > 0)")

    # Also run OOS-only bootstrap for stricter check
    ci_low_oos, ci_high_oos = bootstrap_sharpe_ci(
        oos_ret, alpha=0.001, block_mean=5, n_resamples=10000, seed=42
    )
    gate_bootstrap_oos = ci_low_oos > 0
    print(f"  CI [99.9%, OOS only]: [{ci_low_oos:.3f}, {ci_high_oos:.3f}]  "
          f"{'✅' if gate_bootstrap_oos else '❌'}")

    # ----------------------------------------------------------------------
    # Gate 2 — Walk-forward
    # ----------------------------------------------------------------------
    print("\n[2/6] Walk-forward 8 windows...")
    wf_ratio, wf_max_dd, wf_pass = _walk_forward(ret, n_windows=8)
    print(f"  profitable {wf_ratio:.3f} (≥0.75), max_dd {wf_max_dd:.3f} (≤0.25)  "
          f"{'✅' if wf_pass else '❌'}")

    # ----------------------------------------------------------------------
    # Gate 3 — Baseline winner criteria (recycle from summary)
    # ----------------------------------------------------------------------
    print("\n[3/6] V2 winner criteria gates...")
    oos_m = summary["splits"]["OOS"]
    fwd_m = summary["splits"]["FWD"]

    gate_cagr = oos_m["cagr"] >= 0.30
    gate_sharpe = oos_m["sharpe"] >= 2.0
    gate_mdd = oos_m["mdd"] >= -0.25
    gate_fwd_sharpe = fwd_m["sharpe"] > 0
    gate_hold = summary["window"]["median_hold_days"] >= 3

    print(f"  OOS CAGR ≥ 30%: {oos_m['cagr']:.2%}  {'✅' if gate_cagr else '❌'}")
    print(f"  OOS Sharpe ≥ 2.0: {oos_m['sharpe']:.3f}  {'✅' if gate_sharpe else '❌'}")
    print(f"  OOS MDD ≤ -25%: {oos_m['mdd']:.2%}  {'✅' if gate_mdd else '❌'}")
    print(f"  FWD Sharpe > 0: {fwd_m['sharpe']:.3f}  {'✅' if gate_fwd_sharpe else '❌'}")
    print(f"  Median hold ≥ 3d: {summary['window']['median_hold_days']:.2f}  "
          f"{'✅' if gate_hold else '❌'}")

    # ----------------------------------------------------------------------
    # Gate 4 — IR vs SPY (OOS)
    # ----------------------------------------------------------------------
    print("\n[4/6] Information Ratio vs SPY buy&hold (OOS)...")
    spy_series = load_spy_series()
    spy_bench = build_spy_benchmark(
        spy_series,
        initial_capital=100_000.0,
        window_start=ret.index[0],
        window_end=ret.index[-1],
    )
    spy_daily_ret = spy_bench.equity_curve.pct_change().fillna(0.0)
    spy_oos = spy_daily_ret.loc[(spy_daily_ret.index >= OOS_START) & (spy_daily_ret.index <= OOS_END)]

    ir_oos = _information_ratio(oos_ret, spy_oos)
    gate_ir = ir_oos >= 0.5
    print(f"  IR vs SPY (OOS): {ir_oos:.3f} (≥0.5)  {'✅' if gate_ir else '❌'}")

    # ----------------------------------------------------------------------
    # Gate 5 — Sensitivity: cost model stress (swap 2× worse)
    # ----------------------------------------------------------------------
    print("\n[5/6] Cost sensitivity — swap 2× stress...")
    # Empirical approximation: swap currently costs 73.3% cumulative over 25y
    # Doubling swap adds another ~73% drag → ~2.9%/yr extra
    swap_stress_cagr_drag = float(summary["window"]["cum_swap_pct"])  # negative
    stressed_ret = ret + (swap_stress_cagr_drag / len(ret))  # distribute evenly
    stressed_oos = stressed_ret.loc[(ret.index >= OOS_START) & (ret.index <= OOS_END)]
    stressed_sharpe = _sharpe(stressed_oos)
    stressed_cagr = _cagr(stressed_oos)
    gate_cost_sens = stressed_sharpe >= 1.5 and stressed_cagr >= 0.30
    print(f"  swap-2× stressed OOS Sharpe {stressed_sharpe:.3f} (≥1.5)  "
          f"CAGR {stressed_cagr:.2%} (≥30%)  {'✅' if gate_cost_sens else '❌'}")

    # ----------------------------------------------------------------------
    # Gate 6 — Consolidate verdict
    # ----------------------------------------------------------------------
    all_gates = [
        ("bootstrap_full_ci_low_gt_0", gate_bootstrap, ci_low),
        ("bootstrap_oos_ci_low_gt_0", gate_bootstrap_oos, ci_low_oos),
        ("walk_forward_6_of_8_mdd_25pct", wf_pass, f"{wf_ratio:.3f}/{wf_max_dd:.3f}"),
        ("oos_cagr_ge_30pct", gate_cagr, oos_m["cagr"]),
        ("oos_sharpe_ge_2", gate_sharpe, oos_m["sharpe"]),
        ("oos_mdd_le_25pct", gate_mdd, oos_m["mdd"]),
        ("fwd_sharpe_gt_0", gate_fwd_sharpe, fwd_m["sharpe"]),
        ("median_hold_ge_3d", gate_hold, summary["window"]["median_hold_days"]),
        ("ir_vs_spy_ge_05", gate_ir, ir_oos),
        ("cost_sensitivity_swap_2x", gate_cost_sens, f"S={stressed_sharpe:.3f}/C={stressed_cagr:.3f}"),
    ]

    n_pass = sum(1 for _, p, _ in all_gates if p)
    n_total = len(all_gates)
    t4_pass = n_pass == n_total

    print("\n[6/6] Consolidated gate verdict:")
    for name, passed, value in all_gates:
        marker = "✅" if passed else "❌"
        print(f"  {marker} {name}: {value}")
    print(f"\n  VERDICT T4: {n_pass}/{n_total}  "
          f"{'✅ PASS' if t4_pass else '❌ FAIL'}")

    # Save gates.json
    gates_payload = {
        "phase": "4.0 T4 — full gates battery",
        "n_pass": n_pass,
        "n_total": n_total,
        "all_pass": t4_pass,
        "gates": [
            {"name": name, "pass": bool(p), "value": str(v)} for name, p, v in all_gates
        ],
        "bootstrap": {
            "full": {"ci_low": float(ci_low), "ci_high": float(ci_high)},
            "oos_only": {"ci_low": float(ci_low_oos), "ci_high": float(ci_high_oos)},
            "alpha": 0.001,
            "block_mean": 5,
            "n_resamples": 10000,
        },
        "walk_forward": {
            "n_windows": 8,
            "profitable_ratio": float(wf_ratio),
            "max_window_drawdown": float(wf_max_dd),
            "pass": bool(wf_pass),
        },
        "information_ratio_vs_spy_oos": float(ir_oos),
        "cost_sensitivity_swap_2x": {
            "oos_sharpe": float(stressed_sharpe),
            "oos_cagr": float(stressed_cagr),
            "pass": bool(gate_cost_sens),
        },
        "produced_at": datetime.now(timezone.utc).isoformat(),
    }
    (OUT_DIR / "gates.json").write_text(
        json.dumps(gates_payload, indent=2, default=float), encoding="utf-8"
    )
    print(f"\nwrote {OUT_DIR / 'gates.json'}")

    # Write AGGREGATE.md
    md: list[str] = []
    md.append("# Phase 4.0 — Index CFD substitution verdict (AGGREGATE)")
    md.append("")
    md.append(f"**Status:** {'✅ **CAMINHO 3 VIÁVEL**' if t4_pass else '❌ **CAMINHO 3 FECHADO**'}")
    md.append(f"**Date:** {datetime.now(timezone.utc).date()}")
    md.append(f"**Branch:** `phase4_0/index-cfd-validation`")
    md.append(f"**Gates passed:** {n_pass}/{n_total}")
    md.append("")
    md.append("## 1. Executive summary")
    md.append("")
    if t4_pass:
        md.append("Substituting SPY/QQQ/GLD share CFDs with SPX TR / QQQ adj_close / "
                  "GLD adj_close (proxies for US500 / USTEC / XAUUSD Index CFDs) **preserves "
                  "or improves** the V2-L2 winner's gate-passing behavior.")
        md.append("")
        md.append("Key numbers vs V2-L2 share-CFD baseline:")
        md.append("")
        md.append(f"- OOS Sharpe: **{oos_m['sharpe']:.3f}** (baseline 2.285)")
        md.append(f"- OOS CAGR: **{oos_m['cagr']:.2%}** (baseline 79.14%)")
        md.append(f"- OOS MDD: **{oos_m['mdd']:.2%}** (baseline -21.02%)")
        md.append(f"- IR vs SPY (OOS): **{ir_oos:.3f}** (baseline 2.161)")
        md.append(f"- Bootstrap 99.9% CI low (full): **{ci_low:.3f}** (baseline 0.962)")
        md.append("")
        md.append("The improvement is driven by (a) commission assumed zero in Razor Index vs "
                  "6.6 bps in share CFD (−204 bps cumulative savings over 25y), partially offset "
                  "by (b) ~60% higher cumulative swap drag (−73% vs −45%).")
        md.append("")
        md.append("**Operational consequence:** live-trading Plano A at **$1.000** capital is "
                  "viable on Index CFDs, conditional on T1 (rate card confirmation in live "
                  "Pepperstone demo account) and T2 (dividend adjustment mechanics).")
    else:
        md.append(f"Substitution failed {n_total - n_pass}/{n_total} gates. Caminho 3 is not "
                  "a viable alternative to Caminho 2 ($10k+ share CFD accumulation). User should "
                  "operate Plano B only until sufficient capital for share CFD.")
    md.append("")

    md.append("## 2. Gate-by-gate verdict")
    md.append("")
    md.append("| Gate | Threshold | Observed | Pass |")
    md.append("|---|---|---:|:--:|")
    md.append(f"| Bootstrap 99.9% CI low (full) | > 0 | {ci_low:.3f} | {'✅' if gate_bootstrap else '❌'} |")
    md.append(f"| Bootstrap 99.9% CI low (OOS only) | > 0 | {ci_low_oos:.3f} | {'✅' if gate_bootstrap_oos else '❌'} |")
    md.append(f"| Walk-forward 6/8 profitable | ≥ 0.75 | {wf_ratio:.3f} | {'✅' if wf_ratio >= 6/8 else '❌'} |")
    md.append(f"| Walk-forward max DD | ≤ 25% | {wf_max_dd:.2%} | {'✅' if wf_max_dd <= 0.25 else '❌'} |")
    md.append(f"| OOS CAGR | ≥ 30% | {oos_m['cagr']:.2%} | {'✅' if gate_cagr else '❌'} |")
    md.append(f"| OOS Sharpe | ≥ 2.0 | {oos_m['sharpe']:.3f} | {'✅' if gate_sharpe else '❌'} |")
    md.append(f"| OOS MDD | ≤ 25% | {oos_m['mdd']:.2%} | {'✅' if gate_mdd else '❌'} |")
    md.append(f"| FWD Sharpe | > 0 | {fwd_m['sharpe']:.3f} | {'✅' if gate_fwd_sharpe else '❌'} |")
    md.append(f"| Median hold | ≥ 3 days | {summary['window']['median_hold_days']:.2f} | {'✅' if gate_hold else '❌'} |")
    md.append(f"| IR vs SPY (OOS) | ≥ 0.5 | {ir_oos:.3f} | {'✅' if gate_ir else '❌'} |")
    md.append(f"| Cost sensitivity (swap 2×) | OOS Sharpe ≥ 1.5 & CAGR ≥ 30% | S={stressed_sharpe:.3f} C={stressed_cagr:.2%} | {'✅' if gate_cost_sens else '❌'} |")
    md.append("")

    md.append("## 3. Why PBO and DSR are excluded (n_trials=1)")
    md.append("")
    md.append("Per spec `§3 T4`: PBO and DSR are multi-config tests. With a single substituted "
              "config, PBO has no cross-config sample and DSR's multi-hypothesis correction "
              "collapses to the standard Sharpe t-test (already implicit in bootstrap CI).")
    md.append("")
    md.append("Bootstrap 99.9% CI low > 0 is the primary **distribution-free** robustness gate. "
              "Bootstrap is cited `[advances_fin_ml, p.196-202]` (Politis & Romano 1994 stationary "
              "block, block_mean=5, n_resamples=10000).")
    md.append("")

    md.append("## 4. Known caveats (carry forward to Phase 4 paper)")
    md.append("")
    md.append("1. **GLD proxy for XAUUSD.** GLD.adj_close used because xauusd.parquet only "
              "has 2020+ data. Post-2004 GLD behavior = spot gold minus 0.40% expense ratio; "
              "pre-2004 is silent-cash (same as V2-L2 caveat).")
    md.append("2. **Cost model assumes Razor Index commission-free.** T1 must validate this "
              "empirically in a live Pepperstone demo account before Phase 5.1 live.")
    md.append("3. **Dividend adjustment perfect.** SPX TR and QQQ adj_close include 100% "
              "dividend reinvestment. T2 must validate that Pepperstone's Index CFD "
              "dividend-adjustment mechanism passes through ≥ 95% of gross yield.")
    md.append("4. **Lot granularity at $1k:** 0.01 lot US500 ≈ $600 notional → 40% rounding "
              "vs target $1000. Residual lumpy but viable.")
    md.append("5. **Swap drag 60% higher than V2-L2.** Cumulative 73% vs 45%. If live swap "
              "is even worse than the −0.008%/day modeled, CAGR degrades further.")
    md.append("")

    md.append("## 5. Next actions")
    md.append("")
    if t4_pass:
        md.append("1. **T5 — propagate verdict to docs** (strategy doc §4.2 + §6.3, mandate "
                  "§3.6, Phase 4 spec §1, Phase 3.5a-V2 AGGREGATE §7.5).")
        md.append("2. **T1 — Pepperstone Razor Index rate card empirical validation** (requires "
                  "demo account). Blocks Phase 5.1 live start.")
        md.append("3. **T2 — Dividend adjustment observation** (1 SPY ex-div cycle in demo). "
                  "Blocks Phase 5.1 live start.")
        md.append("4. **Phase 4 paper trading** can start with Index CFD variant as soon as "
                  "T1 is green. Spec update required in `phase_4_paper_trading.md §1`.")
    else:
        md.append("1. **T5 — tombstone** the branch; document failure mode in jornada.")
        md.append("2. **Do NOT** update docs — V2-L2 share-CFD baseline remains the only "
                  "validated path.")
        md.append("3. User reverts to Caminho 1 (Plano B only at Banco Inter) or Caminho 2 "
                  "(accumulate $10k for share CFD).")
    md.append("")

    md.append("## 6. Artefact inventory")
    md.append("")
    md.append("- `reports/phase4_0/index_cfd_validation/summary.json` (T3 output)")
    md.append("- `reports/phase4_0/index_cfd_validation/daily_returns.parquet` (T3 output)")
    md.append("- `reports/phase4_0/index_cfd_validation/standard_report.md` (T3 output)")
    md.append("- `reports/phase4_0/index_cfd_validation/gates.json` (T4 output)")
    md.append("- `reports/phase4_0/index_cfd_validation/AGGREGATE.md` (T4 output, this file)")
    md.append("- `scripts/run_phase4_0_index_cfd_backtest.py` (T3 code)")
    md.append("- `scripts/run_phase4_0_index_cfd_gates.py` (T4 code)")
    md.append("")

    md.append("## 7. Citations")
    md.append("")
    md.append("- EMA-100 regime signal: `[leverage_for_the_long_run, Gayed, p.11-14]`")
    md.append("- Leverage cap L=2: `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`")
    md.append("- Fixed commission at retail scale: `[systematic_trading, Carver, p.185-188]`")
    md.append("- Bootstrap CI (stationary block): `[advances_fin_ml, p.196-202]`")
    md.append("- Walk-forward 6/8 gate: `[advances_fin_ml, ch.11]`")
    md.append("")

    (OUT_DIR / "AGGREGATE.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT_DIR / 'AGGREGATE.md'}")
    print("=" * 72)


if __name__ == "__main__":
    main()
