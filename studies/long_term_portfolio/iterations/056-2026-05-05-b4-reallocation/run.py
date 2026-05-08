#!/usr/bin/env python3
"""Iter 056 — B4 reallocation (Part A): combined SCV+momentum+BTC sleeves.

User question (recorded in plan fizzy-forging-bee):
    Iter 047 found B4+BTC5 (5% from ZROZ) is the best single-sleeve add-on
    to the B4 corrected baseline. Iter 052 separately tested 2.5/5/10% SCV
    (AVUV/VBR) and momentum (SPMO/MTUM/FMTM) sleeves — none beat B4+BTC5
    alone. The user now asks: combining 10% SCV + 10% momentum + 5% BTC
    (= 25% total drained from ZROZ), does the portfolio beat B4+BTC5?
    AND, if BTC is delivered via a stacked vehicle (BTGD or RSSX), can
    we draw funds from GDE / NTSX instead, preserving more equity?

Test grid (8 portfolios + SPY benchmark):

    P1  B4 base                25 NTSX / 25 GDE / 25 RSST / 25 ZROZ
    P2  B4 + 5 BTC spot        25 NTSX / 25 GDE / 25 RSST / 20 ZROZ / 5 BTC
    P3a B4 + 10 AVUV + 10 SPMO + 5 BTC (all from ZROZ -> 0)
    P3b B4 + 10 AVUV + 10 MTUM + 5 BTC (momentum alternative)
    P3c B4 + 10 AVUV + 10 SPMO (no BTC, ZROZ residual 5%)
    P4a 10/10/5 with BTGD reducing GDE                — GDE 20 / ZROZ 0 / BTGD 5
    P4b 10/10/5 with BTGD reducing GDE+ZROZ partial   — GDE 17.5 / ZROZ 2.5 / BTGD 5
    P5a 10/10/5 with RSSX reducing NTSX               — NTSX 20 / ZROZ 0 / RSSX 5
    P5b 10/10/5 with RSSX reducing NTSX+RSST          — NTSX 22.5 / RSST 22.5 / ZROZ 0 / RSSX 5

Window: clipped to BTCSIM (2010-07+) since most variants include BTC.

Citations:
    - B4 corrected baseline + BTC sleeve: spy_beater_hunt iter 047
      (LIVE_STRATEGY_B4_BTC5.md), 2026-05-03.
    - SCV/momentum sleeve negative results: spy_beater_hunt iter 052
      (run_iter052.py, 2026-05-03).
    - Capital-efficient stacking blueprint: [risk_parity, ch.5, p.10].
    - Avantis SCV/value tilts: [risk_parity, ch.2, p.37-41] Fama-French SCV;
      personal Plano C notes moved outside the public repo.
    - BTC sleeve as speculative satellite: `[machine_trading, p.202, ch.7]`.
    - BTGD synth: WisdomTree BTGD prospectus 2024-08.
    - RSSX synth: ReturnStacked RSSX whitepaper 2025-01.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.long_term_portfolio.testfolio_sweep import (
    attach_window_metrics,
    make_portfolio,
    run_sweep,
    spy_benchmark_portfolio,
    write_verdict,
)


SCRIPT_DIR = Path(__file__).parent
ITER_N = 56
HYPOTHESIS_SLUG = "b4-reallocation-combined-scv-momentum-btc"
PRIMARY_CITATION = (
    "[risk_parity, ch.5, p.10] capital-efficient stacking + "
    "[risk_parity, ch.2, p.37-41] Fama-French SCV + "
    "[stocks_on_the_move, p.21-30] Clenow momentum"
)


def build_portfolios() -> list[dict]:
    return [
        spy_benchmark_portfolio(),
        # P1: B4 base (control)
        make_portfolio(
            "P1_B4_base",
            "B4 base 25/25/25/25",
            [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")],
        ),
        # P2: B4+BTC5 spot from ZROZ (iter 047 winner — sanity reference)
        make_portfolio(
            "P2_B4_btc5_spot",
            "B4 + 5 BTC spot from ZROZ (iter 047 winner)",
            [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (20, "ZROZ"), (5, "BTC")],
        ),
        # P3a: 10/10/5 all from ZROZ, momentum=SPMO
        make_portfolio(
            "P3a_combo_spmo_btc",
            "B4 + 10 AVUV + 10 SPMO + 5 BTC from ZROZ",
            [(25, "NTSX"), (25, "GDE"), (25, "RSST"),
             (10, "AVUV"), (10, "SPMO"), (5, "BTC")],
        ),
        # P3b: 10/10/5 all from ZROZ, momentum=MTUM
        make_portfolio(
            "P3b_combo_mtum_btc",
            "B4 + 10 AVUV + 10 MTUM + 5 BTC from ZROZ",
            [(25, "NTSX"), (25, "GDE"), (25, "RSST"),
             (10, "AVUV"), (10, "MTUM"), (5, "BTC")],
        ),
        # P3c: SCV+momentum without BTC (residual ZROZ)
        make_portfolio(
            "P3c_combo_no_btc",
            "B4 + 10 AVUV + 10 SPMO, no BTC (5% ZROZ residual)",
            [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (5, "ZROZ"),
             (10, "AVUV"), (10, "SPMO")],
        ),
        # P4a: BTGD as BTC vehicle (5% sleeve), funded entirely from ZROZ.
        # Apples-to-apples vs P3a (same weights, BTC vehicle differs).
        make_portfolio(
            "P4a_btgd_5pct",
            "10/10/5 with BTGD as BTC vehicle, all from ZROZ",
            [(25, "NTSX"), (25, "GDE"), (25, "RSST"),
             (10, "AVUV"), (10, "SPMO"), (5, "BTGD")],
        ),
        # P4b: BTGD with bigger sleeve (10%) — extra 5% comes from GDE since
        # BTGD's 50% gold leg overlaps GDE's gold exposure.
        make_portfolio(
            "P4b_btgd_10pct_reduce_gde",
            "10/10/10 with BTGD; GDE 20 (BTGD gold overlap)",
            [(25, "NTSX"), (20, "GDE"), (25, "RSST"),
             (10, "AVUV"), (10, "SPMO"), (10, "BTGD")],
        ),
        # P5a: RSSX as BTC vehicle (5% sleeve), funded entirely from ZROZ.
        # Apples-to-apples vs P3a/P4a.
        make_portfolio(
            "P5a_rssx_5pct",
            "10/10/5 with RSSX as BTC vehicle, all from ZROZ",
            [(25, "NTSX"), (25, "GDE"), (25, "RSST"),
             (10, "AVUV"), (10, "SPMO"), (5, "RSSX")],
        ),
        # P5b: RSSX with bigger sleeve (10%) — extra 5% comes from NTSX since
        # RSSX's 100% S&P leg substitutes NTSX's equity leg, while RSSX's
        # second 100% (vol-weighted Gold 0.65 + BTC 0.35) adds gold AND btc
        # diversification on top — the "second stack" is NOT pure BTC.
        make_portfolio(
            "P5b_rssx_10pct_reduce_ntsx",
            "10/10/10 with RSSX; NTSX 20 (RSSX equity overlap)",
            [(20, "NTSX"), (25, "GDE"), (25, "RSST"),
             (10, "AVUV"), (10, "SPMO"), (10, "RSSX")],
        ),
    ]


def main() -> int:
    portfolios = build_portfolios()
    print(f"[iter056] running {len(portfolios)} portfolios via testfol.io API")
    rows = run_sweep(
        portfolios,
        start_date="2000-01-01",
        cache_dir=SCRIPT_DIR / "testfolio_data",
    )
    print(f"[iter056] sweep complete; window: {rows[0]['window']}")

    rows = attach_window_metrics(rows, bench_slugs=["SPY_1x"], windows_years=[3, 5, 10, 15])
    write_verdict(
        SCRIPT_DIR, ITER_N, HYPOTHESIS_SLUG, rows,
        bench_slugs=["SPY_1x"], primary_citation=PRIMARY_CITATION,
    )
    print(f"[iter056] wrote verdict.json + final_report.md")
    print()
    print("Top 3 by Sharpe:")
    ranked = sorted(rows, key=lambda r: -r["stats"]["sharpe"])[:3]
    for r in ranked:
        s = r["stats"]
        print(f"  {r['slug']:<28} CAGR {s['cagr']:>6.2f}%  "
              f"MDD {s['max_drawdown']:>7.2f}%  Sharpe {s['sharpe']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
