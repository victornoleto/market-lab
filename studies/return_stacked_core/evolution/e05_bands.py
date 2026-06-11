"""e05 — Round 4: threshold/tolerance-band rebalancing + annual on 1988+.

Band rule: hold target weights; on any day where some sleeve's *effective*
weight drifts beyond ``band`` (relative to its target, e.g. 0.20 means
weight outside [0.8t, 1.2t]), reset to targets BEFORE that day's return —
same reset convention as the calendar engine. Mechanism: risk-triggered
momentum harvesting `[systematic_trading, p.137-148]`. Verdict rule
(PLAN.md Round 4): improvement requires CAGR > monthly AND MDD >= -30%
AND the same for both neighboring bands `[testing_tuning, p.327-335]`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.return_stacked_core.evolution import evo_data, evo_engine

BANDS = [0.10, 0.15, 0.20, 0.25, 0.33, 0.50]

PORTFOLIOS = {
    "CORE 35/40/25": {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25},
    "EW 33/33/33": {"GDESIM": 1 / 3, "RSSTSIM": 1 / 3, "ZROZSIM": 1 / 3},
    "3A in-cap argmax 45/25/30": {"GDESIM": 0.45, "RSSTSIM": 0.25, "ZROZSIM": 0.30},
    "RSBT structure 60/20/20": {"GDESIM": 0.60, "ZROZSIM": 0.20, "RSBTSIM": 0.20},
    "KMLM structure 55/10/15/20": {
        "GDESIM": 0.55, "RSSTSIM": 0.10, "ZROZSIM": 0.15, "KMLMSIM": 0.20,
    },
}

MAP88 = {"RSSTSIM": "RSST88", "RSBTSIM": "RSBT88"}


def band_rebalanced_equity(
    asset_returns: pd.DataFrame, weights: dict[str, float], band: float
) -> pd.Series:
    cols = list(weights.keys())
    rets = asset_returns[cols].dropna(how="any")
    w = np.array([weights[c] for c in cols], dtype=float)
    r = rets.to_numpy(dtype=float)
    n = r.shape[0]
    equity = np.empty(n, dtype=float)
    value = 1.0
    holdings = w * value
    lo, hi = w * (1.0 - band), w * (1.0 + band)
    for i in range(n):
        eff = holdings / value
        if np.any(eff < lo) or np.any(eff > hi):
            holdings = w * value
        holdings = holdings * (1.0 + r[i])
        value = float(holdings.sum())
        equity[i] = value
    return pd.Series(equity, index=rets.index, name="equity")


def main() -> None:
    matrix = evo_data.load_primary_matrix()
    rows = []
    for pname, weights in PORTFOLIOS.items():
        eq_m = evo_engine.rebalanced_equity(matrix, weights)
        base = evo_engine.compute_metrics(eq_m)
        rows.append({"portfolio": pname, "band": "monthly", **base})
        for band in BANDS:
            eq = band_rebalanced_equity(matrix, weights, band)
            m = evo_engine.compute_metrics(eq)
            rows.append({"portfolio": pname, "band": band, **m})

    df = pd.DataFrame(rows)

    # Verdict per portfolio/band (parameter-plateau rule).
    verdicts = []
    for pname in PORTFOLIOS:
        sub = df[df["portfolio"] == pname].reset_index(drop=True)
        m_cagr = sub[sub["band"] == "monthly"]["cagr"].iloc[0]
        print(f"\n{pname}: monthly cagr={m_cagr:.4f} mdd={sub['mdd'].iloc[0]:.4f}")
        band_rows = sub[sub["band"] != "monthly"].reset_index(drop=True)
        ok = (band_rows["cagr"] > m_cagr) & (band_rows["mdd"] >= evo_data.MDD_CAP)
        for i, brow in band_rows.iterrows():
            neigh = [j for j in (i - 1, i + 1) if 0 <= j < len(band_rows)]
            plateau = bool(ok[i] and all(ok[j] for j in neigh))
            verdicts.append(
                {"portfolio": pname, "band": brow["band"], "cagr": brow["cagr"],
                 "mdd": brow["mdd"], "beats_monthly_in_cap": bool(ok[i]),
                 "plateau_improvement": plateau}
            )
            print(
                f"  band {brow['band']:>5}: cagr={brow['cagr']:.4f} "
                f"mdd={brow['mdd']:.4f} ok={bool(ok[i])} plateau={plateau}"
            )

    # Annual rebalance on the 1988+ window (does the MDD knob hold?).
    lw = evo_data.load_longwindow_matrix()
    print("\n1988+ annual-rebalance check (12 offsets):")
    lw_rows = []
    for pname, weights in PORTFOLIOS.items():
        w88 = {MAP88.get(k, k): v for k, v in weights.items()}
        mm = evo_engine.compute_metrics(evo_engine.rebalanced_equity(lw, w88))
        cagrs, mdds = [], []
        for off in range(12):
            m = evo_engine.compute_metrics(
                evo_engine.rebalanced_equity_offset(lw, w88, 12, off)
            )
            cagrs.append(m["cagr"])
            mdds.append(m["mdd"])
        lw_rows.append(
            {"portfolio": pname, "monthly_cagr": mm["cagr"], "monthly_mdd": mm["mdd"],
             "annual_cagr_min": min(cagrs), "annual_cagr_mean": float(np.mean(cagrs)),
             "annual_cagr_max": max(cagrs), "annual_mdd_worst": min(mdds)}
        )
        print(
            f"  {pname}: monthly {mm['cagr']:.4f}/{mm['mdd']:.4f} | annual cagr "
            f"{min(cagrs):.4f}/{np.mean(cagrs):.4f}/{max(cagrs):.4f} worst_mdd={min(mdds):.4f}"
        )

    df.to_csv(evo_data.TABLES_DIR / "bands.csv", index=False)
    pd.DataFrame(verdicts).to_csv(evo_data.TABLES_DIR / "bands_verdicts.csv", index=False)
    pd.DataFrame(lw_rows).to_csv(evo_data.TABLES_DIR / "annual_1988.csv", index=False)
    n_improve = sum(v["plateau_improvement"] for v in verdicts)
    print(f"\nplateau improvements: {n_improve}/{len(verdicts)}")


if __name__ == "__main__":
    main()
