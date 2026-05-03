#!/usr/bin/env python3
"""Re-fetch corrupted batch_b — separate KMLM-only configs (38y) from DBMF (26y).

Issue detected: original batch_b had DBMFSIM (start 2000-01) clipping the entire
batch window to 26y, distorting L1/M1/M4 metrics.

Fix:
  batch_b1 (38y): M1, M4, L1 — KMLM-only or no-MF, all SIMs back to 1987
  batch_b2 (26y): M2, M3 — DBMF-containing, honest 26y window with caveat
"""
import sys
sys.path.insert(0, '/var/www/pessoal/ai-trade/studies/spy_beater_hunt/iterations/044-2026-05-01-iter038-rebaseline-monthly-ers-terminal-darf')

import json
import os
from pathlib import Path

import fetch_iter044 as base


# Reorganized batches
BATCH_B1_38Y = [
    {"slug": "M1_kmlm_no_rsst", "label": "M1 KMLM no RSST",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "KMLM"), (25, "TMF")]},
    {"slug": "M4_rsst_kmlm_blend", "label": "M4 RSST+KMLM blend",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (12.5, "RSST"), (12.5, "KMLM"), (25, "TMF")]},
    {"slug": "L1_cegb_proxy", "label": "L1 CEGB proxy",
     "allocation_real": [(40, "NTSX"), (25, "GDE"), (17.5, "KMLM"), (17.5, "TLT")]},
]

BATCH_B2_26Y = [
    {"slug": "M2_dbmf_no_rsst", "label": "M2 DBMF no RSST (26y window)",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "DBMF"), (25, "TMF")]},
    {"slug": "M3_kmlm_dbmf_blend", "label": "M3 KMLM+DBMF blend (26y window)",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (12.5, "KMLM"), (12.5, "DBMF"), (25, "TMF")]},
]


def fetch_and_save(batch, letter, sim_list, token):
    for p in batch:
        p["allocation_sim"] = base.decompose(p["allocation_real"], sim_list)
        p["drag_pct"] = base.compute_drag(p["allocation_real"])
    print(f"\nPOST batch '{letter}' ({len(batch)} configs)...")
    resp = base.post_with_retries(base.API_BACKTEST, base.build_payload(batch), token)
    out = base.DATA_DIR / f"backtest_{letter}.json"
    out.write_text(json.dumps({
        "portfolios": [{"slug": p["slug"], "label": p["label"],
                       "allocation_real": p["allocation_real"],
                       "allocation_sim": p["allocation_sim"],
                       "drag_pct": p["drag_pct"]} for p in batch],
        "response": resp,
    }, indent=2))
    print(f"  saved {out} ({out.stat().st_size//1024} KB)")
    for p, s in zip(batch, resp["stats"]):
        print(f"    {p['slug']:<25s} CAGR={s['cagr']:.2f}% MDD={s['max_drawdown']:.2f}% Sharpe={s['sharpe']:.4f}")


def main():
    token = os.environ.get("TESTFOLIO_TOKEN", "").strip()
    if not token:
        sys.exit("fatal: TESTFOLIO_TOKEN env var not set")
    sim_list = base.fetch_sim_list()

    # Overwrite the corrupted batch_b with clean splits
    fetch_and_save(BATCH_B1_38Y, "b", sim_list, token)  # 38y, replaces original batch_b
    fetch_and_save(BATCH_B2_26Y, "d", sim_list, token)  # 26y, NEW batch_d

    print("\nRe-fetch done. Run analyze_iter044.py.")


if __name__ == "__main__":
    main()
