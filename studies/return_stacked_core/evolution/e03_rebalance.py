"""e03 — M4 rebalance-frequency study (PLAN.md).

Same weights, different rebalance period/offset. A frequency change only
counts as an improvement if the MINIMUM CAGR across all offsets still beats
monthly AND every offset keeps MDD >= -30% — otherwise it is
rebalance-timing luck (cf. HFEA quarterly read) `[testing_tuning, p.327-335]`.
"""
from __future__ import annotations

import pandas as pd

from studies.return_stacked_core.evolution import evo_data, evo_engine

PORTFOLIOS = {
    "CORE 35/40/25": {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25},
    "EW 33/33/33": {"GDESIM": 1 / 3, "RSSTSIM": 1 / 3, "ZROZSIM": 1 / 3},
    "3A in-cap argmax 45/25/30": {"GDESIM": 0.45, "RSSTSIM": 0.25, "ZROZSIM": 0.30},
    "RSBT structure 60/20/20": {"GDESIM": 0.60, "ZROZSIM": 0.20, "RSBTSIM": 0.20},
    "KMLM structure 55/10/15/20": {
        "GDESIM": 0.55, "RSSTSIM": 0.10, "ZROZSIM": 0.15, "KMLMSIM": 0.20,
    },
}

FREQS = {"Q": (3, 3), "S": (6, 6), "A": (12, 12)}  # months, n_offsets


def main() -> None:
    matrix = evo_data.load_primary_matrix()
    rows = []
    for pname, weights in PORTFOLIOS.items():
        eq_m = evo_engine.rebalanced_equity(matrix, weights)
        base = evo_engine.compute_metrics(eq_m)
        rows.append({"portfolio": pname, "freq": "M", "offset": 0, **base})
        for fname, (months, n_off) in FREQS.items():
            for off in range(n_off):
                eq = evo_engine.rebalanced_equity_offset(matrix, weights, months, off)
                m = evo_engine.compute_metrics(eq)
                rows.append({"portfolio": pname, "freq": fname, "offset": off, **m})

    df = pd.DataFrame(rows)
    df.to_csv(evo_data.TABLES_DIR / "rebalance_freq.csv", index=False)

    print("portfolio | freq | min/mean/max CAGR across offsets | worst MDD | verdict")
    for pname in PORTFOLIOS:
        sub = df[df["portfolio"] == pname]
        m_cagr = sub[sub["freq"] == "M"]["cagr"].iloc[0]
        m_mdd = sub[sub["freq"] == "M"]["mdd"].iloc[0]
        print(f"{pname}: M cagr={m_cagr:.4f} mdd={m_mdd:.4f}")
        for fname in FREQS:
            f = sub[sub["freq"] == fname]
            lo, mu, hi = f["cagr"].min(), f["cagr"].mean(), f["cagr"].max()
            wmdd = f["mdd"].min()
            improve = lo > m_cagr and wmdd >= evo_data.MDD_CAP
            print(
                f"  {fname}: cagr {lo:.4f}/{mu:.4f}/{hi:.4f} worst_mdd={wmdd:.4f} "
                f"-> {'IMPROVE' if improve else 'no (luck or cap breach)'}"
            )


if __name__ == "__main__":
    main()
