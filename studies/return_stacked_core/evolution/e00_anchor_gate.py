"""e00 — anchor gate: abort the study unless the canonical CORE reproduces.

Targets (discussion/tables/ablations_primary.csv A0 + simplex_grid.csv
45/25/30 row). Tolerance 1e-5 absolute — same engine, same data, so any
drift means the data layer changed under us.
"""
from __future__ import annotations

import sys

import pandas as pd

from studies.return_stacked_core.evolution import evo_data, evo_engine

TOL = 1e-5

CHECKS = [
    # (name, weights, cagr, mdd, sharpe)
    ("CORE 35/40/25", evo_data.CORE_WEIGHTS, 0.125241, -0.307605, 0.846870),
    (
        "simplex argmax 45/25/30",
        {"GDESIM": 0.45, "RSSTSIM": 0.25, "ZROZSIM": 0.30},
        0.128352,
        -0.296761,
        0.865764,
    ),
]


def main() -> int:
    matrix = evo_data.load_primary_matrix()
    rows = []
    ok = True
    for name, weights, cagr, mdd, sharpe in CHECKS:
        eq = evo_engine.rebalanced_equity(matrix, weights)
        m = evo_engine.compute_metrics(eq)
        d_cagr = abs(m["cagr"] - cagr)
        d_mdd = abs(m["mdd"] - mdd)
        d_sharpe = abs(m["sharpe"] - sharpe)
        passed = max(d_cagr, d_mdd, d_sharpe) < TOL
        ok &= passed
        rows.append(
            {
                "check": name,
                "cagr": m["cagr"],
                "mdd": m["mdd"],
                "sharpe": m["sharpe"],
                "target_cagr": cagr,
                "target_mdd": mdd,
                "target_sharpe": sharpe,
                "max_abs_diff": max(d_cagr, d_mdd, d_sharpe),
                "pass": passed,
            }
        )
        print(
            f"{name}: cagr={m['cagr']:.6f} mdd={m['mdd']:.6f} "
            f"sharpe={m['sharpe']:.6f} -> {'PASS' if passed else 'FAIL'}"
        )

    # New-sleeve sanity: standalone metrics, recorded for the report.
    for sleeve in ["RSBTSIM", "RSSBSIM", "QQQSIM", "GLDSIM", "KMLMSIM"]:
        eq = evo_engine.equity_from_returns(matrix[sleeve])
        m = evo_engine.compute_metrics(eq)
        rows.append(
            {"check": f"standalone {sleeve}", "cagr": m["cagr"], "mdd": m["mdd"],
             "sharpe": m["sharpe"], "target_cagr": None, "target_mdd": None,
             "target_sharpe": None, "max_abs_diff": None, "pass": True}
        )
        print(f"standalone {sleeve}: cagr={m['cagr']:.4f} mdd={m['mdd']:.4f} sharpe={m['sharpe']:.4f}")

    evo_data.TABLES_DIR.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(evo_data.TABLES_DIR / "verification.csv", index=False)
    if not ok:
        print("ANCHOR GATE FAILED — do not run e01+.", file=sys.stderr)
        return 1
    print("anchor gate PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
