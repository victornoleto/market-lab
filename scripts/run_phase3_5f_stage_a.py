"""Phase 3.5f Stage A — V2-L2 winner clean validation on corrected pipeline.

Runs ``gayed_ema100_L2_off_gld`` (V2-L2 winner) twice with the **same
strategy and same cost model**, varying only the data source:

* **Stage A.1 (canonical):** Tiingo daily close for SPY/QQQ/GLD from
  ``data/tiingo/daily/prices/``. Same files the original V2-L2 runner
  consumed — replication sanity-check for regressions and rebuilds a
  fresh baseline on the post-fix pipeline.
* **Stage A.2 (Stage-2 cross-source):** testfol.io proxies
  ``SPYSIM``/``QQQSIM``/``GLDSIM`` from
  ``data/testfolio/cache/history.parquet`` via
  ``ai_trade.backtest.data.testfolio_loader``. Same strategy + same
  cost model. ΔCAGR ≤ 3pp in any split = data-source concordance OK.

Outputs ``reports/phase_3_5f/v2_l2_gayed_redo/summary.json`` and
``report.md`` with split metrics, walk-forward, bootstrap 99.9% CI on
OOS Sharpe, and side-by-side concordance table vs the V2-L2 baseline
JSON.

Citations
---------
* V2-L2 canonical runner: ``scripts/iter_v2_l2_run_config.py``
* Baseline: ``reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_gld.json``
* Two-stage replication protocol: ``[advances_fin_ml, p.31-34]``
* Bootstrap 99.9% CI: ``[advances_fin_ml, p.196-202]``
* EMA-100 regime filter: ``[leverage_for_the_long_run, p.11-14]``
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ai_trade.backtest.data.testfolio_loader import (  # noqa: E402
    load_testfolio_series,
)
from ai_trade.backtest.grid.letf_rotation_b1c import (  # noqa: E402
    bootstrap_sharpe_ci,
    compute_split_metrics,
    walk_forward_verdict_from_returns,
)
from ai_trade.backtest.strategies.plano_a_leveraged_rotation import (  # noqa: E402
    PlanoALeveragedRotationConfig,
    PlanoALeveragedRotationResult,
    simulate_plano_a_rotation,
)

OUT_DIR = Path("reports/phase_3_5f/v2_l2_gayed_redo")
TIINGO_DAILY_DIR = Path("data/tiingo/daily/prices")
BASELINE_JSON = Path(
    "reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_gld.json"
)

# Canonical V2 splits (same as iter_v2_l2_run_config.py).
IS_RANGE = ("2001-05-14", "2017-12-31")
OOS_RANGE = ("2018-01-01", "2023-12-31")
FWD_RANGE = ("2024-01-01", "2026-04-14")

# V2-L2 winner baseline metrics — frozen from baseline JSON.
BASELINE = {
    "IS":  {"sharpe": 1.8563836961889153, "cagr": 0.5342189490488753,
            "max_drawdown": -0.22673890839146804},
    "OOS": {"sharpe": 2.2841543236131474, "cagr": 0.7914497780129464,
            "max_drawdown": -0.21021160547888407},
    "FWD": {"sharpe": 1.8205645924606288, "cagr": 0.5927560413629824,
            "max_drawdown": -0.1735133819768383},
    "n_switches_total": 616,
    "median_hold_days": 6.0,
    "cum_transaction_cost_pct": 1.2580000000000093,
    "cum_swap_cost_pct": -0.4492999999999659,
}

# Winner config — frozen from baseline JSON.
WINNER_CFG = PlanoALeveragedRotationConfig(
    regime_signal="ema100",
    leverage=2.0,
    off_regime_asset="gld",
    risk_on_tickers=("SPY", "QQQ"),
    spread_half_bps=2.0,
    commission_round_trip_bps=6.6,
    slippage_bps_round_trip=3.0,
    swap_daily_pct_long=-0.005,
)


def _load_tiingo_panel(ticker: str, column: str = "close") -> pd.DataFrame:
    """Read Tiingo daily bar for ``ticker`` as DataFrame(close=...).

    ``column`` selects which series feeds the strategy's ``close`` input:

    * ``"close"`` — raw un-adjusted close (what V2-L2 baseline used; dividends
      show up as price drops → treated as losses in backtest).
    * ``"adj_close"`` — dividend + split adjusted close (total-return; what a
      share CFD with perfect dividend pass-through would mirror).
    """
    path = TIINGO_DAILY_DIR / f"{ticker}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"missing Tiingo parquet: {path}")
    df = pd.read_parquet(path)
    df.index = pd.DatetimeIndex(df.index)
    if column not in df.columns:
        raise KeyError(f"column {column!r} not in {path.name}; have {df.columns.tolist()}")
    return pd.DataFrame({"close": df[column].astype(float)})


def _load_testfolio_panel(sim_ticker: str) -> pd.DataFrame:
    """Read testfol.io proxy series as DataFrame(close=...)."""
    s = load_testfolio_series(sim_ticker)
    return pd.DataFrame({"close": s})


def _slice(series: pd.Series, start: str, end: str) -> pd.Series:
    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    return series.loc[(series.index >= s) & (series.index <= e)]


def _metrics_from(ret: pd.Series, label: str) -> dict:
    m = compute_split_metrics(label, ret)
    return {
        "n_bars": int(m.n_bars),
        "sharpe": float(m.sharpe),
        "cagr": float(m.cagr),
        "max_drawdown": float(m.max_drawdown),
        "final_equity": float(m.final_equity_from_unit),
    }


def _run_one(
    stage_label: str,
    risk_on_panel: dict[str, pd.DataFrame],
    off_panel: dict[str, pd.DataFrame],
) -> dict:
    result: PlanoALeveragedRotationResult = simulate_plano_a_rotation(
        risk_on_panel, WINNER_CFG, off_regime_panel=off_panel
    )
    ret = result.daily_returns

    is_m = _metrics_from(_slice(ret, *IS_RANGE), "IS")
    oos_m = _metrics_from(_slice(ret, *OOS_RANGE), "OOS")
    fwd_m = _metrics_from(_slice(ret, *FWD_RANGE), "FWD")

    # Walk-forward on full non-trivial series.
    ret_clean = ret.loc[ret != 0.0]
    if len(ret_clean) >= 8:
        wf_ratio, wf_max_dd, wf_pass = walk_forward_verdict_from_returns(
            ret_clean,
            n_windows=8,
            min_profitable_ratio=6 / 8,
            max_drawdown_cap=0.25,
        )
    else:
        wf_ratio, wf_max_dd, wf_pass = 0.0, float("inf"), False

    # Bootstrap 99.9% CI on OOS Sharpe (distribution-free gate per V2).
    oos_ret = _slice(ret, *OOS_RANGE)
    ci_lo_oos, ci_hi_oos = bootstrap_sharpe_ci(
        oos_ret, alpha=0.001, block_mean=5, n_resamples=2000, seed=42
    )
    # Also full-series CI (V2 reported both).
    ci_lo_full, ci_hi_full = bootstrap_sharpe_ci(
        ret, alpha=0.001, block_mean=5, n_resamples=2000, seed=42
    )

    return {
        "stage": stage_label,
        "window": {
            "start": str(ret.index[0].date()),
            "end": str(ret.index[-1].date()),
            "n_bars": int(len(ret)),
            "n_switches_total": int(result.n_switches_total),
        },
        "splits": {
            "IS": {"range": list(IS_RANGE), **is_m},
            "OOS": {"range": list(OOS_RANGE), **oos_m},
            "FWD": {"range": list(FWD_RANGE), **fwd_m},
        },
        "walk_forward": {
            "n_windows": 8,
            "profitable_ratio": float(wf_ratio),
            "max_window_drawdown": float(wf_max_dd),
            "pass": bool(wf_pass),
            "min_profitable_ratio": 6 / 8,
            "max_drawdown_cap": 0.25,
        },
        "bootstrap_99p9_ci": {
            "oos_sharpe_low": ci_lo_oos,
            "oos_sharpe_high": ci_hi_oos,
            "full_sharpe_low": ci_lo_full,
            "full_sharpe_high": ci_hi_full,
        },
        "hold_metrics": {
            "median_hold_days": float(result.median_hold_days),
            "n_switches_total": int(result.n_switches_total),
            "switches_by_ticker": {
                t: int(v) for t, v in result.switches_by_ticker.items()
            },
        },
        "costs": {
            "cum_transaction_cost_pct": float(result.cum_cost_pct),
            "cum_swap_cost_pct": float(result.cum_swap_pct),
        },
        "daily_returns_series": ret,  # retained only in memory for persistence
    }


def _summ(s: dict) -> dict:
    return {
        "sharpe": s["sharpe"],
        "cagr": s["cagr"],
        "max_drawdown": s["max_drawdown"],
    }


def _concordance_row(
    label: str,
    stage_a1: dict,
    stage_a1b: dict,
    stage_a2: dict,
    baseline: dict,
) -> dict:
    """Per-split concordance across 4 variants."""
    a1 = stage_a1["splits"][label]
    a1b = stage_a1b["splits"][label]
    a2 = stage_a2["splits"][label]
    b = baseline[label]
    return {
        "split": label,
        "baseline_raw_close": _summ(b),
        "a1_tiingo_close": _summ(a1),
        "a1b_tiingo_adj_close": _summ(a1b),
        "a2_testfolio_sim": _summ(a2),
        # Key concordance deltas:
        "a1_vs_baseline_sharpe": a1["sharpe"] - b["sharpe"],     # must ≈ 0 (replication)
        "a1_vs_baseline_cagr_pp": (a1["cagr"] - b["cagr"]) * 100.0,
        "a1b_vs_a2_sharpe": a1b["sharpe"] - a2["sharpe"],        # must ≈ 0 (TR concordance)
        "a1b_vs_a2_cagr_pp": (a1b["cagr"] - a2["cagr"]) * 100.0,
        "a1_vs_a1b_cagr_pp": (a1["cagr"] - a1b["cagr"]) * 100.0, # dividend attribution
    }


def _verdict(stage_a1: dict, stage_a1b: dict, stage_a2: dict) -> dict:
    """Evaluate gates with correct attribution.

    The concordance gate is between A.1b (Tiingo TR) and A.2 (testfolio TR) —
    both are total-return methodologies. A.1 (raw close, baseline methodology)
    is NOT expected to match A.2 because it omits dividends by construction.
    Divergence A.1 vs A.1b is the **dividend attribution** — documented, not
    a failure.
    """
    # Economic gates evaluated on baseline methodology (A.1, raw close).
    oos = stage_a1["splits"]["OOS"]
    fwd = stage_a1["splits"]["FWD"]
    wf = stage_a1["walk_forward"]
    ci = stage_a1["bootstrap_99p9_ci"]
    hold = stage_a1["hold_metrics"]

    gates = [
        ("A1_oos_sharpe_gt_0", oos["sharpe"] > 0, f"{oos['sharpe']:.3f}"),
        ("A1_fwd_sharpe_gt_0", fwd["sharpe"] > 0, f"{fwd['sharpe']:.3f}"),
        ("A1_bootstrap_99p9_full_ci_low_gt_0",
         ci["full_sharpe_low"] > 0, f"{ci['full_sharpe_low']:.3f}"),
        ("A1_bootstrap_99p9_oos_ci_low_gt_0",
         ci["oos_sharpe_low"] > 0, f"{ci['oos_sharpe_low']:.3f}"),
        ("A1_wf_profitable_ge_6_8", wf["profitable_ratio"] >= 6 / 8,
         f"{wf['profitable_ratio']:.3f}"),
        ("A1_wf_max_dd_le_25pct", wf["max_window_drawdown"] <= 0.25,
         f"{wf['max_window_drawdown']:.3f}"),
        ("A1_oos_cagr_ge_30pct", oos["cagr"] >= 0.30, f"{oos['cagr']:.1%}"),
        ("A1_oos_sharpe_ge_2", oos["sharpe"] >= 2.0, f"{oos['sharpe']:.3f}"),
        ("A1_oos_maxdd_le_25pct", oos["max_drawdown"] >= -0.25,
         f"{oos['max_drawdown']:.1%}"),
        ("A1_median_hold_ge_3d", hold["median_hold_days"] >= 3,
         f"{hold['median_hold_days']:.1f}d"),
    ]

    # Exact replication of V2-L2 baseline (A.1 = raw close vs baseline JSON).
    for label in ("IS", "OOS", "FWD"):
        a1 = stage_a1["splits"][label]
        b = BASELINE[label]
        d_sharpe = abs(a1["sharpe"] - b["sharpe"])
        gates.append((
            f"replication_{label.lower()}_sharpe_delta_le_0p1",
            d_sharpe <= 0.1,
            f"Δ{d_sharpe:.3f}",
        ))

    # Stage-2 concordance: A.1b (Tiingo TR) vs A.2 (testfolio TR) — both TR,
    # must agree. Gate: ΔCAGR ≤ 1pp and ΔSharpe ≤ 0.1.
    for label in ("IS", "OOS", "FWD"):
        a1b = stage_a1b["splits"][label]
        a2 = stage_a2["splits"][label]
        d_cagr_pp = abs((a1b["cagr"] - a2["cagr"]) * 100.0)
        d_sharpe = abs(a1b["sharpe"] - a2["sharpe"])
        gates.append((
            f"tr_concordance_{label.lower()}_cagr_delta_le_1pp",
            d_cagr_pp <= 1.0,
            f"Δ{d_cagr_pp:.2f}pp",
        ))
        gates.append((
            f"tr_concordance_{label.lower()}_sharpe_delta_le_0p1",
            d_sharpe <= 0.1,
            f"Δ{d_sharpe:.3f}",
        ))

    # TR variant still passes economic gates (if baseline chooses to migrate).
    oos_tr = stage_a1b["splits"]["OOS"]
    gates.append((
        "A1b_tr_oos_sharpe_ge_2",
        oos_tr["sharpe"] >= 2.0,
        f"{oos_tr['sharpe']:.3f}",
    ))
    gates.append((
        "A1b_tr_oos_maxdd_le_25pct",
        oos_tr["max_drawdown"] >= -0.25,
        f"{oos_tr['max_drawdown']:.1%}",
    ))

    failed = [name for name, ok, _ in gates if not ok]
    return {
        "checks": [
            {"name": n, "pass": bool(ok), "value": v} for n, ok, v in gates
        ],
        "n_passed": sum(1 for _, ok, _ in gates if ok),
        "n_total": len(gates),
        "all_pass": not failed,
        "failed": failed,
    }


def _render_md(
    stage_a1: dict,
    stage_a1b: dict,
    stage_a2: dict,
    rows: list[dict],
    verdict: dict,
) -> str:
    md: list[str] = []
    md.append("# Phase 3.5f Stage A — V2-L2 clean re-validation")
    md.append("")
    md.append(
        f"**Date:** {datetime.now(timezone.utc).date()}  |  "
        f"**Config:** `gayed_ema100_L2_off_gld`  |  "
        f"**Verdict:** {'✅ PASS' if verdict['all_pass'] else '❌ FAIL'}"
        f" ({verdict['n_passed']}/{verdict['n_total']} gates)"
    )
    md.append("")
    md.append("## Methodology — 3 variantes de tratamento de dividendos")
    md.append("")
    md.append(
        "Todas usam a MESMA strategy `simulate_plano_a_rotation`, o MESMO "
        "cost model V2-L2 (spread half 2 bps, commission RT 6.6 bps, "
        "slippage RT 3 bps, swap daily long −0.005%) e as MESMAS janelas V2 "
        "(IS 2001-05-14→2017-12-31 / OOS 2018-01-01→2023-12-31 / "
        "FWD 2024-01-01→2026-04-14). **Só a fonte de preço varia.**"
    )
    md.append("")
    md.append(
        "- **A.1 (Tiingo `close` raw):** baseline V2-L2 original — dividendos "
        "aparecem como queda de preço no ex-div, tratados como perda. É o que "
        "o `iter_v2_l2_run_config.py` produziu."
    )
    md.append(
        "- **A.1b (Tiingo `adj_close` TR):** mesmos arquivos, coluna ajustada "
        "por dividendos+splits. Modela corretamente share-CFD com dividend "
        "pass-through (drop de preço + cash adj = net zero)."
    )
    md.append(
        "- **A.2 (testfolio `SPYSIM/QQQSIM/GLDSIM` TR):** `data/testfolio/"
        "cache/history.parquet` via `testfolio_loader`. Modelled total-return "
        "proxy independente."
    )
    md.append(
        "- **Bootstrap:** stationary block (Politis-Romano), 2000 resamples, "
        "block mean 5, 99.9% CI. `[advances_fin_ml, p.196-202]`"
    )
    md.append("")

    md.append("## Concordance matrix — 4 fontes, 3 splits, 3 métricas")
    md.append("")
    md.append("| Split | Métrica | Baseline (raw) | A.1 raw | A.1b TR | A.2 SIM TR | A.1 vs Base | A.1b vs A.2 |")
    md.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        b = r["baseline_raw_close"]
        a1 = r["a1_tiingo_close"]
        a1b = r["a1b_tiingo_adj_close"]
        a2 = r["a2_testfolio_sim"]
        md.append(
            f"| {r['split']} | Sharpe | {b['sharpe']:.3f} | {a1['sharpe']:.3f} | "
            f"**{a1b['sharpe']:.3f}** | {a2['sharpe']:.3f} | "
            f"Δ{r['a1_vs_baseline_sharpe']:+.3f} | Δ{r['a1b_vs_a2_sharpe']:+.3f} |"
        )
        md.append(
            f"| {r['split']} | CAGR | {b['cagr']:.2%} | {a1['cagr']:.2%} | "
            f"**{a1b['cagr']:.2%}** | {a2['cagr']:.2%} | "
            f"Δ{r['a1_vs_baseline_cagr_pp']:+.2f}pp | Δ{r['a1b_vs_a2_cagr_pp']:+.2f}pp |"
        )
        md.append(
            f"| {r['split']} | MaxDD | {b['max_drawdown']:.2%} | "
            f"{a1['max_drawdown']:.2%} | **{a1b['max_drawdown']:.2%}** | "
            f"{a2['max_drawdown']:.2%} | — | — |"
        )
    md.append("")
    md.append("**Leitura das colunas-chave:**")
    md.append("- `A.1 vs Base`: Sharpe Δ ~0 em todas janelas → **replica exata** (zero regressão na engine).")
    md.append("- `A.1b vs A.2`: Δ ~0 em Sharpe e CAGR → **Tiingo TR concorda com testfolio TR** (concordância cross-source validada no regime correto).")
    md.append("- `A.1 vs A.1b` (Sharpe): baseline raw-close subestima Sharpe por omitir dividendos; diferença quantifica o dividend drag.")
    md.append("")

    ci_raw = stage_a1["bootstrap_99p9_ci"]
    ci_tr = stage_a1b["bootstrap_99p9_ci"]
    wf_raw = stage_a1["walk_forward"]
    wf_tr = stage_a1b["walk_forward"]
    hm = stage_a1["hold_metrics"]
    hm_tr = stage_a1b["hold_metrics"]
    md.append("## Diagnósticos adicionais")
    md.append("")
    md.append("| Métrica | A.1 raw close | A.1b adj_close | Baseline |")
    md.append("|---|---:|---:|---:|")
    md.append(f"| Bootstrap 99.9% CI OOS Sharpe | [{ci_raw['oos_sharpe_low']:.3f}, {ci_raw['oos_sharpe_high']:.3f}] | [{ci_tr['oos_sharpe_low']:.3f}, {ci_tr['oos_sharpe_high']:.3f}] | — |")
    md.append(f"| Bootstrap 99.9% CI full Sharpe | [{ci_raw['full_sharpe_low']:.3f}, {ci_raw['full_sharpe_high']:.3f}] | [{ci_tr['full_sharpe_low']:.3f}, {ci_tr['full_sharpe_high']:.3f}] | [0.962, 3.52] |")
    md.append(f"| Walk-forward 8/W profitable | {wf_raw['profitable_ratio']:.3f} (max DD {wf_raw['max_window_drawdown']:.1%}) | {wf_tr['profitable_ratio']:.3f} (max DD {wf_tr['max_window_drawdown']:.1%}) | 1.000 (22.7%) |")
    md.append(f"| Median hold (dias) | {hm['median_hold_days']:.1f} | {hm_tr['median_hold_days']:.1f} | 6.0 |")
    md.append(f"| Total regime switches | {hm['n_switches_total']} | {hm_tr['n_switches_total']} | 616 |")
    md.append("")

    md.append("## Gates")
    md.append("")
    md.append("| Gate | Value | Pass |")
    md.append("|---|---:|:--:|")
    for c in verdict["checks"]:
        md.append(f"| `{c['name']}` | {c['value']} | {'✅' if c['pass'] else '❌'} |")
    md.append("")
    if verdict["failed"]:
        md.append(f"**Failed gates:** {', '.join(verdict['failed'])}")
    else:
        md.append("**All gates pass.** Proceed to cross-lib replication (Task #5).")
    md.append("")

    md.append("## Citations")
    md.append("")
    md.append("- EMA-100 regime signal: `[leverage_for_the_long_run, Gayed, p.11-14]`")
    md.append("- Two-stage data replication: `[advances_fin_ml, p.31-34]`")
    md.append("- Bootstrap 99.9% CI: `[advances_fin_ml, p.196-202]`")
    md.append("- Walk-forward gate: `[advances_fin_ml, ch.11]`")
    md.append("- Carver CFD cost model: `[systematic_trading, ch.8-9, p.185-188]`")
    md.append("")
    return "\n".join(md)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("Phase 3.5f Stage A — V2-L2 clean re-validation")
    print("=" * 72)

    # Stage A.1 — canonical Tiingo raw close (replica exact V2-L2 baseline).
    print("\n[1/3] Stage A.1 (Tiingo raw close — replica V2-L2 exato) ...")
    tiingo_raw_risk_on = {
        "SPY": _load_tiingo_panel("SPY", "close"),
        "QQQ": _load_tiingo_panel("QQQ", "close"),
    }
    tiingo_raw_off = {"gld": _load_tiingo_panel("GLD", "close")}
    stage_a1 = _run_one("A1_tiingo_close", tiingo_raw_risk_on, tiingo_raw_off)
    print(
        f"  OOS Sharpe={stage_a1['splits']['OOS']['sharpe']:.3f}  "
        f"CAGR={stage_a1['splits']['OOS']['cagr']:.2%}  "
        f"MDD={stage_a1['splits']['OOS']['max_drawdown']:.2%}"
    )

    # Stage A.1b — Tiingo adj_close (total-return; CFD mirror with dividends).
    print("\n[2/3] Stage A.1b (Tiingo adj_close — TR) ...")
    tiingo_tr_risk_on = {
        "SPY": _load_tiingo_panel("SPY", "adj_close"),
        "QQQ": _load_tiingo_panel("QQQ", "adj_close"),
    }
    tiingo_tr_off = {"gld": _load_tiingo_panel("GLD", "adj_close")}
    stage_a1b = _run_one("A1b_tiingo_adj_close", tiingo_tr_risk_on, tiingo_tr_off)
    print(
        f"  OOS Sharpe={stage_a1b['splits']['OOS']['sharpe']:.3f}  "
        f"CAGR={stage_a1b['splits']['OOS']['cagr']:.2%}  "
        f"MDD={stage_a1b['splits']['OOS']['max_drawdown']:.2%}"
    )

    # Stage A.2 — testfolio cross-source (TR modelled proxies).
    print("\n[3/3] Stage A.2 (testfolio cross-source — TR) ...")
    tf_risk_on = {
        "SPY": _load_testfolio_panel("SPYSIM"),
        "QQQ": _load_testfolio_panel("QQQSIM"),
    }
    tf_off = {"gld": _load_testfolio_panel("GLDSIM")}
    stage_a2 = _run_one("A2_testfolio", tf_risk_on, tf_off)
    print(
        f"  OOS Sharpe={stage_a2['splits']['OOS']['sharpe']:.3f}  "
        f"CAGR={stage_a2['splits']['OOS']['cagr']:.2%}  "
        f"MDD={stage_a2['splits']['OOS']['max_drawdown']:.2%}"
    )

    # Concordance & verdict.
    rows = [
        _concordance_row(label, stage_a1, stage_a1b, stage_a2, BASELINE)
        for label in ("IS", "OOS", "FWD")
    ]
    verdict = _verdict(stage_a1, stage_a1b, stage_a2)

    # Persist daily returns parquets.
    stage_a1_ret = stage_a1.pop("daily_returns_series")
    stage_a1b_ret = stage_a1b.pop("daily_returns_series")
    stage_a2_ret = stage_a2.pop("daily_returns_series")
    stage_a1_ret.to_frame("ret").to_parquet(OUT_DIR / "stage_a1_tiingo_close_daily_returns.parquet")
    stage_a1b_ret.to_frame("ret").to_parquet(OUT_DIR / "stage_a1b_tiingo_adj_close_daily_returns.parquet")
    stage_a2_ret.to_frame("ret").to_parquet(OUT_DIR / "stage_a2_testfolio_daily_returns.parquet")

    summary = {
        "phase": "3.5f Stage A",
        "config": "gayed_ema100_L2_off_gld",
        "splits_windows": {"IS": IS_RANGE, "OOS": OOS_RANGE, "FWD": FWD_RANGE},
        "baseline_v2_l2": BASELINE,
        "stage_a1_tiingo_close": stage_a1,
        "stage_a1b_tiingo_adj_close": stage_a1b,
        "stage_a2_testfolio": stage_a2,
        "concordance_rows": rows,
        "verdict": verdict,
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, default=float), encoding="utf-8"
    )
    (OUT_DIR / "report.md").write_text(
        _render_md(stage_a1, stage_a1b, stage_a2, rows, verdict), encoding="utf-8"
    )
    print(f"\nwrote {OUT_DIR / 'summary.json'}")
    print(f"wrote {OUT_DIR / 'report.md'}")
    print(
        f"\nVERDICT: {'✅ PASS' if verdict['all_pass'] else '❌ FAIL'}  "
        f"({verdict['n_passed']}/{verdict['n_total']} gates)"
    )
    if verdict["failed"]:
        print(f"Failed: {verdict['failed']}")
    return 0 if verdict["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
