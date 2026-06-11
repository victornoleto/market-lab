#!/usr/bin/env python3
"""s00 — anchor gate: reproduce the canonical RSC numbers or abort the pipeline.

Hard-fails (exit 1) unless, on the sleeve-matrix window 2000-01-04..2026-05-21
with monthly first-trading-day rebalancing:

    CORE 35/40/25  → CAGR 12.40% ± 0.15pp, MDD −30.76% ± 0.10pp, Sharpe 0.838 ± 0.010
    SPYSIM b&h     → CAGR  8.39% ± 0.15pp, MDD −55.14% ± 0.10pp, Sharpe 0.514 ± 0.010

Also verifies proxy compositions (descriptive, recorded in
tables/verification.csv):

    GDESIM  ≈ 0.9*SPY + 0.9*GLD − 0.8*CASHX   (daily corr > 0.98, monthly > 0.99,
                                               |ΔCAGR| < 0.8pp/yr — ER 0.20% + tracking)
    NTSXSIM ≈ 0.9*SPY + 0.6*IEF − 0.5*CASHX   (daily corr > 0.98, monthly > 0.99)

Daily correlation sits below 1 because the saved sims carry intra-month
weight drift (the real funds rebalance their internal stack on a schedule,
not daily); at monthly horizon the drift washes out — measured 0.9969 (GDE)
and 0.9967 (NTSX) on 2000-01..2026-05.

Anti-overfitting rationale for gating before any new analysis:
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
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

CORE_WEIGHTS = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}

ANCHOR = {
    "core": {"cagr": 0.1240, "mdd": -0.3076, "sharpe": 0.838},
    "spy": {"cagr": 0.0839, "mdd": -0.5514, "sharpe": 0.514},
}
TOL = {"cagr": 0.0015, "mdd": 0.0010, "sharpe": 0.010}


def _check(label: str, got: dict, want: dict, rows: list, failures: list) -> None:
    for key, target in want.items():
        value = float(got[key])
        ok = abs(value - target) <= TOL[key]
        rows.append(
            {
                "check": f"anchor_{label}_{key}",
                "value": value,
                "target": target,
                "tolerance": TOL[key],
                "passed": ok,
            }
        )
        if not ok:
            failures.append(f"{label}.{key}: got {value:.4f}, want {target:.4f} ± {TOL[key]}")


def main() -> int:
    returns = dd.load_primary_returns()
    rows: list[dict] = []
    failures: list[str] = []

    core_eq = engine.rebalanced_equity(returns, CORE_WEIGHTS)
    core = engine.compute_metrics(core_eq)
    _check("core", core, ANCHOR["core"], rows, failures)

    spy_eq = engine.equity_from_returns(returns["SPYSIM"])
    spy = engine.compute_metrics(spy_eq)
    _check("spy", spy, ANCHOR["spy"], rows, failures)

    monthly = dd.monthly_returns(
        returns[["GDESIM", "SPYSIM", "GLDSIM", "CASHX", "NTSXSIM", "IEFSIM"]]
    )

    def composition_check(
        label: str, sim: str, blueprint_daily: pd.Series, blueprint_monthly: pd.Series
    ) -> None:
        common = blueprint_daily.index.intersection(returns[sim].dropna().index)
        corr_d = float(returns[sim].loc[common].corr(blueprint_daily.loc[common]))
        corr_m = float(monthly[sim].corr(blueprint_monthly))
        cagr_sim = engine.compute_metrics(
            engine.equity_from_returns(returns[sim].loc[common])
        )["cagr"]
        cagr_bp = engine.compute_metrics(
            engine.equity_from_returns(blueprint_daily.loc[common])
        )["cagr"]
        gap = abs(cagr_sim - cagr_bp)
        ok = corr_d > 0.98 and corr_m > 0.99 and gap < 0.008
        rows.append(
            {"check": f"{label}_corr_daily", "value": corr_d, "target": 0.98,
             "tolerance": float("nan"), "passed": corr_d > 0.98}
        )
        rows.append(
            {"check": f"{label}_corr_monthly", "value": corr_m, "target": 0.99,
             "tolerance": float("nan"), "passed": corr_m > 0.99}
        )
        rows.append(
            {"check": f"{label}_cagr_gap", "value": gap, "target": 0.008,
             "tolerance": float("nan"), "passed": gap < 0.008}
        )
        if not ok:
            failures.append(
                f"{label}: corr_d={corr_d:.4f}, corr_m={corr_m:.4f}, |dCAGR|={gap:.4%}"
            )
        print(f"{label}: corr_daily={corr_d:.4f} corr_monthly={corr_m:.4f} dCAGR={gap:.2%}")

    # GDE: 90% SPY + 90% gold, 80% excess notional financed at CASHX.
    composition_check(
        "gde_composition",
        "GDESIM",
        (0.9 * returns["SPYSIM"] + 0.9 * returns["GLDSIM"] - 0.8 * returns["CASHX"]).dropna(),
        0.9 * monthly["SPYSIM"] + 0.9 * monthly["GLDSIM"] - 0.8 * monthly["CASHX"],
    )
    # NTSX blueprint per proxies.PROXY_LEGS (WisdomTree 90/60/-50).
    composition_check(
        "ntsx_blueprint",
        "NTSXSIM",
        (0.9 * returns["SPYSIM"] + 0.6 * returns["IEFSIM"] - 0.5 * returns["CASHX"]).dropna(),
        0.9 * monthly["SPYSIM"] + 0.6 * monthly["IEFSIM"] - 0.5 * monthly["CASHX"],
    )

    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(dd.TABLES_DIR / "verification.csv", index=False)

    print(
        f"CORE 35/40/25  CAGR={core['cagr']:.2%} MDD={core['mdd']:.2%} "
        f"Sharpe={core['sharpe']:.3f}  ({core['start']}..{core['end']})"
    )
    print(
        f"SPYSIM b&h     CAGR={spy['cagr']:.2%} MDD={spy['mdd']:.2%} "
        f"Sharpe={spy['sharpe']:.3f}"
    )
    if failures:
        print("\nANCHOR GATE FAILED:")
        for f in failures:
            print(" -", f)
        return 1
    print("\nANCHOR GATE PASSED — pipeline may proceed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
