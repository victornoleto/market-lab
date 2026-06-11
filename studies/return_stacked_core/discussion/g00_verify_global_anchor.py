#!/usr/bin/env python3
"""g00 — global anchor gate: reproduce the saved RSC-Global curves or abort.

Hard gates (exit 1 on failure), window 1988-01-04..2026-05-21:

    100% VTSIM buy-hold       → CAGR 8.77% ± 0.10pp, MDD −58.35% ± 0.10pp,
                                Sharpe 0.562 ± 0.005  (exact-source check)
    Global simple NTSD/RSIT   → daily-return corr vs saved curve ≥ 0.999
                                (composition identity)

Documented divergence (NOT a failure): the saved curve embeds the old
testfol payload financing (CAGR 13.10%); this study's standard financing
(2%/yr spread on 100%-stack legs, plain CASHX on 90/60 legs — same as the US
discussion pipeline) yields a slightly different level. The delta is recorded
in tables/global_verification.csv and must stay within ±0.9pp CAGR
`[testing_tuning, p.327-335]`.
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

GLOBAL_CORE_KM = {
    "GDESIM": 0.20, "NTSDSIM": 0.15, "RSST_KM": 0.20, "RSIT_KM": 0.20,
    "ZROZSIM": 0.25,
}
VT_ANCHOR = {"cagr": 0.0877, "mdd": -0.5835, "sharpe": 0.562}
SAVED_GLOBAL_CAGR = 0.1310


def main() -> int:
    rows: list[dict] = []
    failures: list[str] = []

    saved = dd.load_saved_global_curves()
    g88 = dd.load_global_1988_returns()

    # Gate 1: VT buy-hold reproduces the saved benchmark exactly.
    vt = engine.compute_metrics(engine.equity_from_returns(g88["VTSIM"]))
    for key, target in VT_ANCHOR.items():
        tol = 0.005 if key == "sharpe" else 0.0010
        ok = abs(vt[key] - target) <= tol
        rows.append({"check": f"vt_{key}", "value": vt[key], "target": target,
                     "passed": ok})
        if not ok:
            failures.append(f"VT {key}: got {vt[key]:.4f}, want {target} ± {tol}")
    print(f"VT 1988+: CAGR {vt['cagr']:.2%} MDD {vt['mdd']:.2%} "
          f"Sharpe {vt['sharpe']:.3f}")

    # Gate 2: composition identity vs the saved Global simple curve.
    core_eq = engine.rebalanced_equity(g88, GLOBAL_CORE_KM)
    core = engine.compute_metrics(core_eq)
    saved_ret = saved["Global simple NTSD/RSIT"].pct_change().dropna()
    ours_ret = core_eq.pct_change().dropna()
    common = saved_ret.index.intersection(ours_ret.index)
    corr = float(saved_ret.loc[common].corr(ours_ret.loc[common]))
    corr_ok = corr >= 0.999
    rows.append({"check": "global_simple_composition_corr", "value": corr,
                 "target": 0.999, "passed": corr_ok})
    if not corr_ok:
        failures.append(f"Global simple composition corr {corr:.4f} < 0.999")

    # Documented financing-convention divergence vs saved level.
    delta = core["cagr"] - SAVED_GLOBAL_CAGR
    delta_ok = abs(delta) <= 0.009
    rows.append({"check": "global_simple_cagr_delta_vs_saved", "value": delta,
                 "target": 0.009, "passed": delta_ok})
    if not delta_ok:
        failures.append(f"Global simple CAGR delta vs saved {delta:+.2%} > 0.9pp")
    print(f"Global simple (this study's financing): CAGR {core['cagr']:.2%} "
          f"MDD {core['mdd']:.2%} Sharpe {core['sharpe']:.3f} | "
          f"corr vs saved {corr:.5f} | dCAGR vs saved payload {delta:+.2%}")

    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(dd.TABLES_DIR / "global_verification.csv", index=False)

    if failures:
        print("\nGLOBAL ANCHOR GATE FAILED:")
        for f in failures:
            print(" -", f)
        return 1
    print("\nGLOBAL ANCHOR GATE PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
