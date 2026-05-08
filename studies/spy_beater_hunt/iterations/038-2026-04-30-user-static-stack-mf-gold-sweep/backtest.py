"""Iter 038: USER STATIC STACK + MF + GOLD SWEEP.

Comprehensive sweep of user-proposed simple buy-hold portfolio across:

  Axis 1 — Equity stacking source: NTSX (90/60 SPY/IEF) vs RSSB (100/100
           Global/Bonds) vs raw SPY
  Axis 2 — Gold exposure: GDE (90/90 SPY/Gold capital-efficient) — held
           constant in most configs since literature converges on it.
  Axis 3 — Managed Futures source: RSST (100/100 SPY/MF stacking) vs
           KMLM (Mount Lucas pure trend, no equity) vs DBMF (DBi managed
           futures, includes equity long/short) vs blends.
  Axis 4 — Duration leverage: TMF (3x TLT LETF, decay-prone) vs TLT (1x)
           vs ZROZ (zero-coupon LTT, longer duration but no LETF decay)
           vs none.
  Axis 5 — Allocation tilt: equal-weight 25/25/25/25 vs gold-heavy vs
           equity-heavy vs conservative + literature-derived (CEGB).

Literature priors (research 2026-04-30):
  - TMF max DD historico -92%, std 3x TLT — 2022 inflationary regime
    catastrophic. Most published portfolios use 10-15% TMF, NOT 25%.
  - Capital Efficient Golden Butterfly (CEGB, RiskParityChronicles):
    40 NTSX + 35 RSBT + 25 GDE (RSBT = bonds + trend).
  - 67 NTSX + 33 diversifiers is bogleheads template.
  - KMLM: no equity index, purest trend-decorrelation. KMLM-DBMF corr 0.70.
  - RSST author advice: never give up treasury bonds entirely.

NO new infra. Reuses 'static' spec. 771 tests baseline preserved.

Citations:
  [risk_parity, ch.5, p.10] Carlson — capital-efficient stacking baseline
  [ilmanen_expected_returns, ch.19] — managed futures crisis-alpha
  [leverage_for_the_long_run, ch.3-4] — LETF decay (TMF) mechanics
  Bridgewater All-Weather (Dalio) — 4-asset risk-parity foundation
  RiskParityChronicles (CEGB literature) — stacked allocation template
  optimizedportfolio.com (NTSX/RSST/RSSB/GDE reviews)
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 38
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "user-static-stack-mf-gold-sweep"
PRIMARY_CITATION = (
    "User-proposed 2026-04-30 baseline (testfol.io 1987+ CAGR 13.79% / MDD 30.91%) + "
    "RiskParityChronicles CEGB (40 NTSX + 35 RSBT + 25 GDE) + "
    "[risk_parity, ch.5, p.10] Carlson stacking + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha + "
    "[leverage_for_the_long_run, ch.3-4] LETF decay (TMF) + "
    "optimizedportfolio.com fund reviews + Bogleheads NTSX template"
)

PRIOR_CUMULATIVE_N_TRIALS = 144
N_CONFIGS = 14
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 158


CONFIGS = {
    # ANCHOR: user's exact proposed allocation
    "B1_user_baseline_25tmf": {
        "type": "static",
        "weights": {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "TMFSIM": 0.25},
    },

    # === DURATION LEVERAGE AXIS ===
    # Test if TMF (3x) is the right duration choice
    "B2_tmf10_balanced": {
        # TMF dose-down per literature (10% TMF + 30% each of equity/gold/MF)
        "type": "static",
        "weights": {"NTSXSIM": 0.30, "GDESIM": 0.30, "RSSTSIM": 0.30, "TMFSIM": 0.10},
    },
    "B3_tlt_instead_of_tmf": {
        # 1x duration via TLT — same notional weight, no LETF decay
        "type": "static",
        "weights": {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "TLTSIM": 0.25},
    },
    "B4_zroz_instead_of_tmf": {
        # Zero-coupon LTT — even longer duration than TLT, no LETF decay
        "type": "static",
        "weights": {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "ZROZSIM": 0.25},
    },
    "B5_no_duration": {
        # Pure stacked equity + gold + MF, no duration
        "type": "static",
        "weights": {"NTSXSIM": 0.35, "GDESIM": 0.35, "RSSTSIM": 0.30},
    },

    # === MF SOURCE AXIS ===
    # Replace RSST (which has internal SPY exposure) with explicit MF ETFs
    "M1_kmlm_no_rsst": {
        # Pure KMLM trend (no equity in MF leg) — purest decorrelation
        "type": "static",
        "weights": {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.25, "TMFSIM": 0.25},
    },
    "M2_dbmf_no_rsst": {
        # DBMF (most institutional MF, includes equity long/short)
        "type": "static",
        "weights": {"NTSXSIM": 0.25, "GDESIM": 0.25, "DBMFSIM": 0.25, "TMFSIM": 0.25},
    },
    "M3_kmlm_dbmf_blend": {
        # 50/50 KMLM + DBMF (corr 0.70 — partial decorrelation)
        "type": "static",
        "weights": {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.125, "DBMFSIM": 0.125, "TMFSIM": 0.25},
    },
    "M4_rsst_kmlm_blend": {
        # RSST + KMLM split (RSST trend + KMLM pure trend, double dose of trend exposure)
        "type": "static",
        "weights": {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.125, "KMLMSIM": 0.125, "TMFSIM": 0.25},
    },

    # === LITERATURE-DERIVED ===
    "L1_cegb_proxy": {
        # Capital Efficient Golden Butterfly approximation (RSBT not available — use KMLM+TLT)
        # Original: 40 NTSX + 35 RSBT + 25 GDE; RSBT = 100% bonds + 100% trend, so split 17.5+17.5
        "type": "static",
        "weights": {"NTSXSIM": 0.40, "GDESIM": 0.25, "KMLMSIM": 0.175, "TLTSIM": 0.175},
    },
    "L2_bogleheads_67ntsx": {
        # 67 NTSX + 33 diversifiers (literature default template)
        # 67 NTSX + 11 GLD + 11 KMLM + 11 ZROZ
        "type": "static",
        "weights": {"NTSXSIM": 0.67, "GLDSIM": 0.11, "KMLMSIM": 0.11, "ZROZSIM": 0.11},
    },

    # === ALLOCATION TILT AXIS ===
    "T1_gold_heavy": {
        # More gold (35% via GDE), less duration
        "type": "static",
        "weights": {"NTSXSIM": 0.20, "GDESIM": 0.35, "RSSTSIM": 0.25, "TMFSIM": 0.20},
    },
    "T2_equity_heavy": {
        # More equity stacking (35% NTSX), less duration
        "type": "static",
        "weights": {"NTSXSIM": 0.35, "GDESIM": 0.25, "RSSTSIM": 0.25, "TMFSIM": 0.15},
    },
    "T3_rssb_global": {
        # RSSB (Global stocks + Bonds 100/100) instead of NTSX (US-only)
        # Diversifies away from US-equity-only
        "type": "static",
        "weights": {"RSSBSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "TMFSIM": 0.25},
    },
}


if __name__ == "__main__":
    verdict = run_iter_spy_beater(
        iter_n=ITER_N,
        iter_dir=ITER_DIR,
        hypothesis_slug=HYPOTHESIS_SLUG,
        primary_citation=PRIMARY_CITATION,
        configs=CONFIGS,
        datasets_to_test=("lh_56y", "spy_real"),
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
    )

    print(f"\n{'=' * 80}")
    print(f"Iter {ITER_N:03d} — {HYPOTHESIS_SLUG}")
    print(f"{'=' * 80}")
    print(f"Selected: {verdict['selected_config']}  Gross={verdict['total_score']}  Net={verdict.get('net_total_score','n/a')}")
    print()
    print(f"{'config':<28} {'Sh_lh':>6} {'CAGR_lh':>8} {'MDD_lh':>8} {'Sh_spy':>7} {'CAGR_spy':>9} {'MDD_spy':>9}")
    print('-' * 90)
    for cfg_name, ds_metrics in verdict["all_configs_metrics"].items():
        lh = ds_metrics["lh_56y"]
        sp = ds_metrics["spy_real"]
        print(
            f"{cfg_name:<28} "
            f"{lh['sharpe']:>6.3f} {lh['cagr']*100:>7.2f}% {lh['mdd']*100:>7.2f}% "
            f"{sp['sharpe']:>7.3f} {sp['cagr']*100:>8.2f}% {sp['mdd']*100:>8.2f}%"
        )
