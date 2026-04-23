"""Defines the candidate portfolios for comparison.

Each portfolio has:
- a "real" spec (using current ETF tickers)
- a "proxy" spec (using long-history proxies where real ETFs are short)
- a category tag
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Portfolio:
    id: str
    name: str
    category: str
    description: str
    weights_real: dict[str, float]
    weights_proxy: dict[str, float]  # long-history replacement
    notes: str = ""


PORTFOLIOS: list[Portfolio] = [
    # ============================================================
    # BASELINE — user's current plan (from portfolio-aposentadoria.md §10)
    # ============================================================
    Portfolio(
        id="P0_current",
        name="Current plan (Plano C as-is)",
        category="baseline",
        description="User's factor-core portfolio as documented in portfolio-aposentadoria.md §10. "
                    "No leverage. 100% equity + 5% alts. 9 ETFs.",
        weights_real={
            "AVUS": 0.28, "SPMO": 0.10, "AVUV": 0.14,
            "AVDE": 0.14, "IDMO": 0.05, "AVDV": 0.09,
            "AVEM": 0.15,
            "IBIT": 0.03, "GLDM": 0.02,
        },
        # Long-run proxy: replace AVUS/AVUV with KF-synthetic (99yr), drop alts
        weights_proxy={
            "AVUS_syn_3f": 0.38,  # AVUS + SPMO proxy (no Mom factor)
            "AVUV_syn_3f": 0.14,
            "VEA": 0.19,  # AVDE+IDMO (short history, use VEA as DM proxy)
            "AVDV": 0.09,  # no long proxy — will limit window
            "VWO": 0.15,  # AVEM proxy
            "GLD": 0.05,  # alts lump
        },
        notes="Baseline. Backtests on 2019-09 onwards (real) or 1926+ (proxy).",
    ),

    # ============================================================
    # USER's specific SSO proposal
    # ============================================================
    Portfolio(
        id="P1_user_sso",
        name="User proposal: 50% SSO + rest factor",
        category="user_idea",
        description="User's question: 50% SSO to get 100% US equity exposure while freeing "
                    "10% of capital for DM+EM. Keeps factor tilts on DM/EM side only.",
        weights_real={
            "SSO": 0.50,
            "AVDE": 0.14, "IDMO": 0.05, "AVDV": 0.09,
            "AVEM": 0.15,
            "AVUV": 0.05,  # residual SCV tilt if wanted
            "IBIT": 0.01, "GLDM": 0.01,
        },
        weights_proxy={
            "SPY_2x_sim": 0.50,  # SSO long-run proxy w/ LETF fees
            "VEA": 0.19,  # AVDE+IDMO proxy
            "AVDV": 0.09,
            "VWO": 0.15,
            "AVUV_syn_3f": 0.05,
            "GLD": 0.02,
        },
    ),

    # ============================================================
    # Simple LETF buy-and-hold tests
    # ============================================================
    Portfolio(
        id="P2_sso_100",
        name="100% SSO buy-and-hold",
        category="letf_raw",
        description="Gayed's naked 2x SPY buy-and-hold. To quantify what the user trades off "
                    "against the full user_sso proposal.",
        weights_real={"SSO": 1.0},
        weights_proxy={"SPY_2x_sim": 1.0},
    ),

    Portfolio(
        id="P3_upro_100",
        name="100% UPRO buy-and-hold",
        category="letf_raw",
        description="3x SPY buy-and-hold. Historical MDD -99.9% (1929-42).",
        weights_real={"UPRO": 1.0},
        weights_proxy={"SPY_3x_sim": 1.0},
    ),

    Portfolio(
        id="P4_hfea",
        name="HFEA 55/45 UPRO/TLT",
        category="letf_rotation",
        description="Classic HFEA (Hedgefundie's Excellent Adventure). 3x SPY + long Treasuries "
                    "as diversifier. Quarterly rebalance to target. Annihilated 2022.",
        weights_real={"UPRO": 0.55, "TLT": 0.45},
        weights_proxy={"SPY_3x_sim": 0.55, "TLT": 0.45},
    ),

    # ============================================================
    # WisdomTree Efficient Core — return stacking via treasury overlay
    # ============================================================
    Portfolio(
        id="P5_ntsx_global",
        name="NTSX-family 60/30/10 global",
        category="efficient_core",
        description="Full WisdomTree 90/60 stack across US/DM/EM. Each dollar invested gives "
                    "~1.5x exposure (equity + treasuries overlay via futures).",
        weights_real={"NTSX": 0.60, "NTSI": 0.25, "NTSE": 0.10, "GLDM": 0.05},
        weights_proxy={
            "NTSX_syn": 0.60,  # 2006+
            "VEA": 0.25,  # NTSI proxy (no syn for DM 90/60)
            "VWO": 0.10,
            "GLD": 0.05,
        },
        notes="NTSX 90/60 = 90%SPX + 60% IEF-like treasuries. Capital efficiency 150%.",
    ),

    # ============================================================
    # Return Stacked Global
    # ============================================================
    Portfolio(
        id="P6_return_stacked",
        name="Return Stacked aggressive",
        category="return_stacked",
        description="Heavy use of Corey Hoffstein's Return Stacked ETFs — stack equity premium "
                    "with managed futures and bonds at 100/100 each. High cost but high diversification.",
        weights_real={
            "RSST": 0.30,  # 100% US stocks + 100% MF
            "RSSB": 0.30,  # 100% global stocks + 100% bonds
            "AVUV": 0.15,  # SCV tilt
            "AVDV": 0.10,
            "AVEM": 0.10,
            "GLDM": 0.05,
        },
        weights_proxy={
            "RSST_syn": 0.30,  # short history — will constrain window
            "NTSX_syn": 0.30,  # RSSB proxy (equity + bonds stacked)
            "AVUV_syn_3f": 0.15,
            "AVDV": 0.10,
            "VWO": 0.10,
            "GLD": 0.05,
        },
        notes="Return Stacked ETFs inception 2023+ so real backtest very short. Proxy uses "
              "NTSX_syn (2006+) and factor SMB/HML (1926+).",
    ),

    # ============================================================
    # Efficient core + factor stacked (the synthesis I recommend)
    # ============================================================
    Portfolio(
        id="P7_stacked_factor",
        name="Stacked factor core",
        category="hybrid_best",
        description="My synthesis: NTSX family for capital-efficient beta, AVUV/AVDV/AVEM for "
                    "factor tilts, DBMF as uncorrelated return stream, some gold and BTC.",
        weights_real={
            "NTSX": 0.30, "NTSI": 0.15, "NTSE": 0.10,  # core 55% w/ embedded bonds
            "AVUV": 0.15, "AVDV": 0.10, "AVEM": 0.05,  # factor tilts 30%
            "DBMF": 0.10,  # managed futures diversifier
            "GLDM": 0.03, "IBIT": 0.02,  # alts
        },
        weights_proxy={
            "NTSX_syn": 0.30,
            "VEA": 0.15, "VWO": 0.10,  # no NTSI/NTSE proxy
            "AVUV_syn_3f": 0.15, "AVDV": 0.10, "VWO": 0.05,
            "SPY_1x_sim": 0.10,  # DBMF long-run proxy is fraught — use mkt beta
            "GLD": 0.05,
        },
        notes="Embedded leverage ~1.2x via NTSX-family (90/60 on 55% = ~82% equity + ~33% bonds).",
    ),

    # ============================================================
    # Max CAGR candidate
    # ============================================================
    Portfolio(
        id="P8_max_cagr",
        name="Max CAGR candidate",
        category="max_cagr",
        description="Aggressive: heavy Nasdaq leverage + factor + some diversification. "
                    "Accepts large drawdowns.",
        weights_real={
            "TQQQ": 0.25, "SSO": 0.25, "AVUV": 0.20,
            "AVDV": 0.10, "AVEM": 0.10,
            "GLDM": 0.05, "IBIT": 0.05,
        },
        weights_proxy={
            "SPY_3x_sim": 0.25,  # rough TQQQ proxy (QQQ sims not in panel — we use SPY 3x)
            "SPY_2x_sim": 0.25,
            "AVUV_syn_3f": 0.20,
            "AVDV": 0.10, "VWO": 0.10,
            "GLD": 0.10,
        },
    ),

    # ============================================================
    # Max Sharpe candidate (balanced risk parity-ish)
    # ============================================================
    Portfolio(
        id="P9_max_sharpe",
        name="Max Sharpe candidate",
        category="max_sharpe",
        description="Risk parity-ish via return stacking: NTSX for levered 60/40 baseline + "
                    "factor tilts + MF + gold. Goal: best risk-adjusted return.",
        weights_real={
            "NTSX": 0.35, "NTSI": 0.15, "NTSE": 0.05,
            "AVUV": 0.12, "AVDV": 0.08,
            "DBMF": 0.10, "KMLM": 0.05,
            "GLDM": 0.08, "IBIT": 0.02,
        },
        weights_proxy={
            "NTSX_syn": 0.35,
            "VEA": 0.15, "VWO": 0.05,
            "AVUV_syn_3f": 0.12, "AVDV": 0.08,
            "SPY_1x_sim": 0.15,  # MF proxy — use mkt fallback
            "GLD": 0.10,
        },
    ),

    # ============================================================
    # Max terminal wealth w/ MDD ≤ 50% (constrained)
    # ============================================================
    Portfolio(
        id="P10_terminal_mdd50",
        name="Max terminal wealth / MDD ≤ 50%",
        category="constrained",
        description="Constrained to historical MDD ≤ ~50%. Light leverage via NTSX, strong "
                    "factor tilts, MF + gold for drawdown cushion.",
        weights_real={
            "NTSX": 0.25, "NTSI": 0.15, "NTSE": 0.10,
            "AVUS": 0.10, "AVUV": 0.15,
            "AVDV": 0.08, "AVEM": 0.05,
            "DBMF": 0.07,
            "GLDM": 0.03, "IBIT": 0.02,
        },
        weights_proxy={
            "NTSX_syn": 0.25,
            "VEA": 0.15, "VWO": 0.10,
            "AVUS_syn_3f": 0.10, "AVUV_syn_3f": 0.15,
            "AVDV": 0.08, "VWO": 0.05,
            "SPY_1x_sim": 0.07,  # MF proxy
            "GLD": 0.05,
        },
    ),

    # ============================================================
    # Max SWR (safe withdrawal rate) — retirement-phase
    # ============================================================
    Portfolio(
        id="P11_max_swr",
        name="Max SWR (retirement phase)",
        category="retirement",
        description="Glidepath END-STATE at age 60. Lower equity, higher MF + bonds, factor tilts "
                    "for real-return premium. For accumulation this has too little equity.",
        weights_real={
            "NTSX": 0.20, "NTSI": 0.10,
            "AVUV": 0.08, "AVDV": 0.05, "AVEM": 0.02,
            "DBMF": 0.15, "KMLM": 0.05,
            "TLT": 0.10, "IEF": 0.15,
            "GLDM": 0.08, "IBIT": 0.02,
        },
        weights_proxy={
            "NTSX_syn": 0.20,
            "VEA": 0.10,
            "AVUV_syn_3f": 0.08, "AVDV": 0.05, "VWO": 0.02,
            "SPY_1x_sim": 0.20,  # MF proxy
            "TLT": 0.10, "IEF": 0.15,
            "GLD": 0.10,
        },
    ),
]


if __name__ == "__main__":
    for p in PORTFOLIOS:
        total_real = sum(p.weights_real.values())
        total_proxy = sum(p.weights_proxy.values())
        print(f"{p.id:25s} ({p.category:18s}): real={total_real:.3f} proxy={total_proxy:.3f}")
        if abs(total_real - 1.0) > 1e-6:
            print(f"  WARN weight sum != 1: {total_real}")
        if abs(total_proxy - 1.0) > 1e-6:
            print(f"  WARN proxy sum != 1: {total_proxy}")
