#!/usr/bin/env python3
"""G3f — pure TQQQ/QQQ swap (no diversifiers).

Bull: 100% TQQQ (above 200d SMA QQQ)
Bear: 100% QQQ (below 200d SMA QQQ)

Difference vs G3e (Gayed-NDX): bear preserves equity exposure (QQQ) instead
of fleeing to bonds (IEF).
"""
from __future__ import annotations

import json
import os
import sys

import fetch_g3 as base


def variant_g3f_pure_tqqq_qqq() -> tuple[str, list[dict], float, float]:
    """100% TQQQ bull → 100% QQQ bear (pure NDX regime swap)."""
    bull_drag = base.ER["TQQQ"]
    bear_drag = base.ER["QQQ"]
    return (
        "G3f — TQQQ 100 / QQQ 100 (pure NDX swap, no diversifiers)",
        [
            base.alloc_leg("Bull TQQQ", True, [
                ("QQQSIM?L=3&E=0.84", 100),
            ], drag_pct=bull_drag),
            base.alloc_leg("Bear QQQ", False, [
                ("QQQSIM", 100),
            ], drag_pct=bear_drag),
        ],
        bull_drag, bear_drag,
    )


def main() -> int:
    token = os.environ.get("TESTFOLIO_TOKEN", "").strip()
    if not token:
        sys.exit("fatal: TESTFOLIO_TOKEN env var not set.")
    base.DATA_DIR.mkdir(parents=True, exist_ok=True)

    name, allocs, bull_drag, bear_drag = variant_g3f_pure_tqqq_qqq()
    print(f"Variant g3f_pure_tqqq_qqq: {name}")
    print(f"  bull drag = {bull_drag:.4f}%, bear drag = {bear_drag:.4f}%")

    payload = base.build_tactical_payload(name, allocs)
    resp = base.post_with_retries(base.API_TACTICAL, payload, token)
    out = base.DATA_DIR / "g3f_pure_tqqq_qqq.json"
    out.write_text(json.dumps(resp, indent=2))
    print(f"  saved {out} ({out.stat().st_size//1024} KB)")

    if "stats" in resp and resp["stats"]:
        for s in resp["stats"]:
            lab = s.get("name", "?")
            cagr = s.get("cagr", 0)
            mdd = s.get("max_drawdown", 0)
            sharpe = s.get("sharpe", 0)
            print(f"    [{lab}] CAGR={cagr:.2f}% MDD={mdd:.2f}% Sharpe={sharpe:.4f}")

    print("\nRun analyze_g3.py (after small edit to add g3f_pure_tqqq_qqq) to refresh metrics.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
