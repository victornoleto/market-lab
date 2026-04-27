"""Re-score iters 002-074 with relaxed (per-iter) DSR n_trials.

Reads each iteration's `verdict.json` + `results.json`, recomputes DSR
p-value using `n_trials = configs_tested` (instead of cumulative), and
re-runs `score_strategy()` with the relaxed metrics. Output:

* `iterations/NNN-*/verdict_v2.json` — relaxed-rubric verdict
* `studies/global_factor_tilt_loop/RESCORE_V2_SUMMARY.md` — Top-K under v2

The original `verdict.json` is preserved untouched for audit.

Citation: `[advances_fin_ml, p.222-223]` — DSR formula; convention
change documented in `WINNER_AND_RANKING.md` §3 (2026-04-25).
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies/global_factor_tilt_loop"))

from ai_trade.backtest.validation.dsr import dsr  # noqa: E402
from scoring import (BENCHMARKS, DatasetMetrics, Gates,  # noqa: E402
                     score_strategy)


def returns_for(results: dict, ds: str, cfg_id: str) -> np.ndarray | None:
    rs = results.get("returns_series", {}).get(ds, {}).get(cfg_id)
    if not rs or "net_returns" not in rs:
        return None
    return np.asarray(rs["net_returns"], dtype=float)


def pick_top_cfg(results: dict, ds: str) -> str | None:
    runs = results.get("runs", {}).get(ds, {})
    if not isinstance(runs, dict) or not runs:
        return None
    return max(runs.items(),
               key=lambda kv: kv[1].get("sharpe", float("-inf")))[0]


def rescore_iter(iter_dir: Path) -> dict | None:
    verdict_path = iter_dir / "verdict.json"
    results_path = iter_dir / "results.json"
    if not verdict_path.exists() or not results_path.exists():
        return None

    v = json.loads(verdict_path.read_text())
    res = json.loads(results_path.read_text())

    iter_id = int(re.match(r"(\d+)", iter_dir.name).group(1))

    # iters 075+ already use the relaxed per-iter DSR convention natively
    # (PROMPT.md was updated 2026-04-25 23:20 before iter 075 started).
    # Their verdict.json is already v2-equivalent — just pass through.
    if iter_id >= 75:
        out = dict(v)  # shallow copy
        out["iter_id"] = iter_id
        out["v2_meta"] = {
            "convention": "per-iter DSR n_trials (native — iter 075+ used relaxed PROMPT)",
            "n_trials_v2": v.get("configs_tested", 1),
            "n_trials_v1_cumulative": v.get("cumulative_n_trials", 0),
            "v1_score": v.get("total_score", 0),
            "v1_winner_met": v.get("winner_conditions_met", False),
            "passthrough": True,
        }
        (iter_dir / "verdict_v2.json").write_text(json.dumps(out, indent=2, default=str))
        return out
    n_trials_v2 = int(v.get("configs_tested", 1) or 1)
    if n_trials_v2 < 1:
        n_trials_v2 = 1

    metrics_v1 = v.get("metrics_used", {})
    new_dsr_p: dict[str, float | None] = {}

    for ds in ("educational", "vt_real", "ndx_real"):
        # iter 014 had configs_tested=0 and empty metrics — skip
        if ds not in metrics_v1:
            continue
        sharpe_v1 = metrics_v1[ds].get("sharpe")
        if sharpe_v1 is None:
            new_dsr_p[ds] = None
            continue
        # Find returns series for top cfg per dataset
        cfg = pick_top_cfg(res, ds)
        if cfg is None:
            cfg = v.get("top_candidate", {}).get(ds) if isinstance(v.get("top_candidate"), dict) else None
        if cfg is None:
            new_dsr_p[ds] = metrics_v1[ds].get("dsr_p_value")
            continue
        ret = returns_for(res, ds, cfg)
        if ret is None or len(ret) < 60:
            new_dsr_p[ds] = metrics_v1[ds].get("dsr_p_value")
            continue
        try:
            r = dsr(ret, n_trials=n_trials_v2)
            new_dsr_p[ds] = float(r.p_value)
        except Exception as e:
            print(f"  iter {iter_id} {ds}: dsr() failed ({e}); keep v1")
            new_dsr_p[ds] = metrics_v1[ds].get("dsr_p_value")

    # Build relaxed metrics + relaxed gates (G2 follows new p<0.05 with v2 p)
    metrics_v2 = {}
    for ds in ("educational", "vt_real", "ndx_real"):
        if ds not in metrics_v1:
            metrics_v2[ds] = DatasetMetrics(sharpe=0.0, cagr=0.0, mdd=1.0)
            continue
        m = metrics_v1[ds]
        metrics_v2[ds] = DatasetMetrics(
            sharpe=m.get("sharpe", 0.0),
            cagr=m.get("cagr", 0.0),
            mdd=m.get("mdd", 1.0),
            dsr_p_value=new_dsr_p.get(ds, m.get("dsr_p_value")),
        )

    # Build gates_v2: keep G1, G3-G7 from original; recompute G2 from new p
    gate_details = v.get("gate_details", {})
    gates_v2 = {}
    for ds in ("educational", "vt_real", "ndx_real"):
        gd = gate_details.get(ds, {}) if isinstance(gate_details, dict) else {}
        # Helpers — verdicts have sometimes-string-typed booleans
        def b(key: str, default: bool) -> bool:
            val = gd.get(key, default)
            if isinstance(val, str):
                return val.lower() == "true"
            return bool(val)

        # G2 v2 directly from recomputed p-value
        new_p = new_dsr_p.get(ds)
        g2 = (new_p is not None) and (new_p < 0.05)

        gates_v2[ds] = Gates(
            g1_pbo=b("G1_pbo_pass", False),
            g2_dsr=g2,
            g3_wf=b("G3_wf_pass", False),
            g4_oos=b("G4_oos_pass", False),
            g5_fwd=b("G5_fwd_pass", False),
            g6_bootstrap=b("G6_boot_pass", False),
            g7_crosslib=b("G7_xlib_pass", False),
        )

    res_v2 = score_strategy(metrics_v2, gates_v2,
                            cumulative_n_trials=v.get("cumulative_n_trials", 0))

    out = res_v2.to_dict()
    out["configs_tested"] = n_trials_v2
    out["primary_citation"] = v.get("primary_citation", "")
    out["hypothesis_slug"] = v.get("hypothesis_slug", iter_dir.name)
    out["iter_id"] = iter_id
    out["v2_meta"] = {
        "convention": "per-iter DSR n_trials (relaxed 2026-04-25)",
        "n_trials_v2": n_trials_v2,
        "n_trials_v1_cumulative": v.get("cumulative_n_trials", 0),
        "v1_score": v.get("total_score", 0),
        "v1_winner_met": v.get("winner_conditions_met", False),
        "v1_dsr_p_per_dataset": {ds: metrics_v1.get(ds, {}).get("dsr_p_value")
                                  for ds in ("educational", "spy_real", "ndx_real")},
        "v2_dsr_p_per_dataset": new_dsr_p,
    }

    (iter_dir / "verdict_v2.json").write_text(json.dumps(out, indent=2, default=str))
    return out


def main() -> None:
    iter_dirs = sorted(Path(ROOT / "studies/global_factor_tilt_loop/iterations").glob("0*"))
    rows = []
    for d in iter_dirs:
        try:
            v2 = rescore_iter(d)
        except Exception as e:
            print(f"  skip {d.name}: {e}")
            continue
        if v2 is None:
            continue
        rows.append(v2)
        print(f"iter {v2['iter_id']:>3}: v1={v2['v2_meta']['v1_score']:>3} → "
              f"v2={v2['total_score']:>3} ({v2['tier']:<10}) "
              f"winner: v1={str(v2['v2_meta']['v1_winner_met']):<5} → "
              f"v2={str(v2['winner_conditions_met'])} | {v2['hypothesis_slug']}")

    rows.sort(key=lambda r: -r["total_score"])

    summary = ROOT / "studies/global_factor_tilt_loop/RESCORE_V2_SUMMARY.md"
    with summary.open("w") as fh:
        fh.write("# Rescore v2 — relaxed DSR convention (2026-04-25)\n\n")
        fh.write("DSR n_trials switched from cumulative-loop-budget to per-iteration "
                 "configs_tested. See `WINNER_AND_RANKING.md` §3 for rationale.\n\n")
        winners = [r for r in rows if r["winner_conditions_met"]]
        fh.write(f"**Winner_conditions met under v2: {len(winners)}/{len(rows)} iters**\n\n")
        if winners:
            fh.write("## Iters meeting all 5 strict winner conditions (v2)\n\n")
            fh.write("| iter | v1→v2 score | tier | slug |\n|---|---|---|---|\n")
            for r in winners:
                fh.write(f"| {r['iter_id']} | {r['v2_meta']['v1_score']}→{r['total_score']} "
                         f"| {r['tier']} | `{r['hypothesis_slug']}` |\n")
            fh.write("\n")

        fh.write("## Top-25 by v2 score\n\n")
        fh.write("| rank | iter | v1 | **v2** | tier | winner_met (v2) | slug |\n")
        fh.write("|---|---|---|---|---|---|---|\n")
        for i, r in enumerate(rows[:25], 1):
            fh.write(f"| {i} | {r['iter_id']} | {r['v2_meta']['v1_score']} | "
                     f"**{r['total_score']}** | {r['tier']} | "
                     f"{'✅' if r['winner_conditions_met'] else '—'} | "
                     f"`{r['hypothesis_slug']}` |\n")

    print(f"\nWrote {summary}")
    print(f"v2 winners: {len([r for r in rows if r['winner_conditions_met']])}/{len(rows)}")


if __name__ == "__main__":
    main()
