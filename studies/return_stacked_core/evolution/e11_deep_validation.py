"""e11 — Round 8: deep-validation battery on the unique 5/6-gate candidate.

Candidate: 45/25/30 GDE/RSST/ZROZ, 20% tolerance bands, vs CORE 35/40/25
monthly. B1 dense starts, B2 band continuum, B3 joint block bootstrap
(fixed seed — deterministic), B4 weekly trigger cadence (PLAN.md Round 8;
thresholds fixed before running) `[advances_fin_ml, p.222-223]`,
`[testing_tuning, p.327-335]`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.return_stacked_core.evolution import evo_data, evo_engine
from studies.return_stacked_core.evolution.e07_band_simplex import (
    band_simulate_matrix,
)

ASSETS = ["GDESIM", "RSSTSIM", "ZROZSIM"]
CAND_W = np.array([0.45, 0.25, 0.30])
CORE_W = np.array([0.35, 0.40, 0.25])
CORE_WD = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}
BAND = 0.20
SEED = 42
N_PATHS = 1000
BLOCK = 63
REB_TD = 21  # monthly analog on bootstrap paths


def cagr_mdd(equity: np.ndarray, years: float) -> tuple[np.ndarray, np.ndarray]:
    term = equity[-1] / equity[0]
    cagr = term ** (1.0 / years) - 1.0
    peak = np.maximum.accumulate(equity, axis=0)
    mdd = (equity / peak - 1.0).min(axis=0)
    return cagr, mdd


def simulate_paths_band(r: np.ndarray, w: np.ndarray, band: float) -> np.ndarray:
    """Equity (n_days, n_paths) — band rule per path; r is (days, paths, assets)."""
    n_days, n_paths, _ = r.shape
    values = np.ones(n_paths)
    holdings = np.tile(w, (n_paths, 1))
    lo, hi = w * (1 - band), w * (1 + band)
    equity = np.empty((n_days, n_paths))
    for i in range(n_days):
        eff = holdings / values[:, None]
        trig = ((eff < lo) | (eff > hi)).any(axis=1)
        if trig.any():
            holdings[trig] = w * values[trig, None]
        holdings = holdings * (1.0 + r[i])
        values = holdings.sum(axis=1)
        equity[i] = values
    return equity


def simulate_paths_periodic(r: np.ndarray, w: np.ndarray, every: int) -> np.ndarray:
    n_days, n_paths, _ = r.shape
    values = np.ones(n_paths)
    holdings = np.tile(w, (n_paths, 1))
    equity = np.empty((n_days, n_paths))
    for i in range(n_days):
        if i % every == 0:
            holdings = w * values[:, None]
        holdings = holdings * (1.0 + r[i])
        values = holdings.sum(axis=1)
        equity[i] = values
    return equity


def main() -> None:
    matrix = evo_data.load_primary_matrix()
    rets = matrix[ASSETS].dropna(how="any")
    results = {}

    # ---- B1: dense quarterly start grid ---------------------------------
    starts = pd.date_range("2000-01-01", "2016-12-31", freq="QS")
    wins, rows_b1 = 0, []
    for s in starts:
        sub = rets.loc[s:]
        cc = evo_engine.compute_metrics(
            evo_engine.rebalanced_equity(matrix.loc[s:], CORE_WD)
        )["cagr"]
        eq = band_simulate_matrix(sub, CAND_W[None, :], BAND)
        mc = evo_engine.metrics_from_matrix(eq, sub.index)["cagr"].iloc[0]
        wins += int(mc > cc)
        rows_b1.append({"start": str(s.date()), "cand_cagr": mc, "core_cagr": cc})
    b1_share = wins / len(starts)
    results["B1"] = {"share": b1_share, "n": len(starts), "pass": b1_share >= 0.80}
    print(f"B1 dense starts: {wins}/{len(starts)} = {b1_share:.1%} (need >=80%) "
          f"-> {'PASS' if results['B1']['pass'] else 'FAIL'}")

    # ---- B2: band continuum 10..30% -------------------------------------
    ok_flags, rows_b2 = [], []
    for b in range(10, 31):
        band = b / 100.0
        eq = band_simulate_matrix(rets, CAND_W[None, :], band)
        m = evo_engine.metrics_from_matrix(eq, rets.index)
        ok = bool(
            m["cagr"].iloc[0] > evo_data.CORE_CAGR
            and m["mdd"].iloc[0] >= evo_data.MDD_CAP
        )
        ok_flags.append(ok)
        rows_b2.append({"band": band, "cagr": m["cagr"].iloc[0],
                        "mdd": m["mdd"].iloc[0], "ok": ok})
    longest = max(
        (len(list(g)) for k, g in __import__("itertools").groupby(ok_flags) if k),
        default=0,
    )
    results["B2"] = {
        "n_ok": sum(ok_flags), "longest_run": longest,
        "pass": sum(ok_flags) >= 15 and longest >= 8,
    }
    print(f"B2 band continuum: {sum(ok_flags)}/21 ok, longest run {longest} "
          f"(need >=15 & run>=8) -> {'PASS' if results['B2']['pass'] else 'FAIL'}")

    # ---- B3: joint block bootstrap ---------------------------------------
    r = rets.to_numpy()
    n_days = r.shape[0]
    years = (rets.index[-1] - rets.index[0]).days / 365.25
    rng = np.random.default_rng(SEED)
    n_blocks = int(np.ceil(n_days / BLOCK))
    starts_idx = rng.integers(0, n_days - BLOCK, size=(N_PATHS, n_blocks))
    idx = (starts_idx[:, :, None] + np.arange(BLOCK)[None, None, :]).reshape(
        N_PATHS, -1
    )[:, :n_days]
    paths = r[idx]                      # (paths, days, assets)
    paths = np.transpose(paths, (1, 0, 2))  # (days, paths, assets)

    eq_cand = simulate_paths_band(paths, CAND_W, BAND)
    eq_core = simulate_paths_periodic(paths, CORE_W, REB_TD)
    cagr_c, mdd_c = cagr_mdd(eq_cand, years)
    cagr_k, mdd_k = cagr_mdd(eq_core, years)
    spread_pos = float((cagr_c > cagr_k).mean())
    incap = float((mdd_c >= evo_data.MDD_CAP).mean())
    med_mdd = float(np.median(mdd_c))
    shallower = float((mdd_c > mdd_k).mean())
    results["B3"] = {
        "spread_pos": spread_pos, "incap_share": incap,
        "median_mdd": med_mdd, "shallower_share": shallower,
        "spread_p05": float(np.percentile(cagr_c - cagr_k, 5)),
        "pass": spread_pos >= 0.95 and incap >= 0.60
        and med_mdd >= evo_data.MDD_CAP and shallower >= 0.80,
    }
    print(
        f"B3 bootstrap (n={N_PATHS}, block={BLOCK}, seed={SEED}): "
        f"spread>0 in {spread_pos:.1%} (>=95%), in-cap {incap:.1%} (>=60%), "
        f"median MDD {med_mdd:.4f} (>=-0.30), shallower-than-CORE {shallower:.1%} "
        f"(>=80%), spread p05 {results['B3']['spread_p05']:+.4f} "
        f"-> {'PASS' if results['B3']['pass'] else 'FAIL'}"
    )

    # ---- B4: weekly trigger cadence --------------------------------------
    rw = rets.to_numpy()
    values, holdings = 1.0, CAND_W.copy()
    lo, hi = CAND_W * (1 - BAND), CAND_W * (1 + BAND)
    eq = np.empty(rw.shape[0])
    for i in range(rw.shape[0]):
        if i % 5 == 0:  # check only every 5th trading day
            eff = holdings / values
            if (eff < lo).any() or (eff > hi).any():
                holdings = CAND_W * values
        holdings = holdings * (1.0 + rw[i])
        values = holdings.sum()
        eq[i] = values
    cagr_w = (eq[-1] / eq[0]) ** (1.0 / years) - 1.0
    peak = np.maximum.accumulate(eq)
    mdd_w = float((eq / peak - 1.0).min())
    results["B4"] = {
        "cagr": float(cagr_w), "mdd": mdd_w,
        "pass": cagr_w > evo_data.CORE_CAGR and mdd_w >= evo_data.MDD_CAP,
    }
    print(f"B4 weekly cadence: cagr={cagr_w:.4f} mdd={mdd_w:.4f} "
          f"-> {'PASS' if results['B4']['pass'] else 'FAIL'}")

    pd.DataFrame(rows_b1).to_csv(evo_data.TABLES_DIR / "deepval_b1_starts.csv", index=False)
    pd.DataFrame(rows_b2).to_csv(evo_data.TABLES_DIR / "deepval_b2_bands.csv", index=False)
    pd.DataFrame(
        {"cagr_cand": cagr_c, "cagr_core": cagr_k, "mdd_cand": mdd_c, "mdd_core": mdd_k}
    ).to_csv(evo_data.TABLES_DIR / "deepval_b3_bootstrap.csv", index=False)
    summary = pd.DataFrame(
        [{"check": k, **v} for k, v in results.items()]
    )
    summary.to_csv(evo_data.TABLES_DIR / "deepval_summary.csv", index=False)
    n_pass = sum(v["pass"] for v in results.values())
    print(f"\nbattery: {n_pass}/4 pass")


if __name__ == "__main__":
    main()
