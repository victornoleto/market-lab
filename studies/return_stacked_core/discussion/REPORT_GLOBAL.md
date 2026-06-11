# REPORT — global variant: what is the best possible global portfolio?

Date: 2026-06-11. Status: **discovery-only research** (no deployment, no
mandate/capital change). Benchmark: **100% VT**. All numbers simulated, gross,
monthly rebalance. Windows: primary 2000-01-04..2026-05-21 (MFBLEND sleeves,
same fidelity standard as the US study); canonical 1988+ (KMLM-only MF,
MEDIUM fidelity); extended 1970+ (UMD splice, LOW fidelity). Pipeline:
`make_all.py --suite global` (g00→g07). Methodology: `METHODS.md`; gate:
`tables/global_verification.csv` (VT reproduces the saved benchmark exactly;
the canonical global curve reproduces at correlation 1.0000 with a documented
−0.60pp/yr financing-convention delta).

**Question chartered:** find the best possible *global* portfolio (the global
analog of the US discussion study).

---

## Headline answer

**A "best global portfolio" in the backtest sense does not exist — every
window says the same thing: international equity sleeves cost Sharpe, and the
unconstrained optimum of the global universe is a US-only mix.** What exists
is a *price curve for globalness* (fig g08) and a plateau that tolerates up to
~15-20% international sleeves. The honest output is therefore three tiers:

| Tier | Allocation | 2000+ CAGR/MDD/Sharpe | 1988+ | 1970+ (LOW fid.) |
|---|---|---|---|---|
| Performance-first | **US CORE 35 GDE / 40 RSST / 25 ZROZ** | 12.5% / −30.8% / 0.847 | 13.7% / −32.4% / 0.923 | 14.0% / −39.7% / 0.893 |
| **Balanced global (recommended global expression)** | **27.5 GDE / 7.5 NTSD / 30 RSST / 10 RSIT / 25 ZROZ** (≈17.5% intl sleeves) | 11.7% / −33.4% / 0.801 | 13.1% / −33.7% / 0.899 | **13.6% / −38.2% / 0.894** |
| Diversification-first | CORE-GLOBAL 20 GDE / 15 NTSD / 20 RSST / 20 RSIT / 25 ZROZ (35% intl sleeves) | 10.9% / −36.8% / 0.746 | 12.5% / −35.0% / 0.859 | 13.3% / −37.0% / 0.878 |
| Benchmark | 100% VT | 7.2% / −58.4% / 0.460 | 8.8% / −58.4% / 0.562 | 10.0% / −58.4% / 0.664 |

All three tiers crush VT everywhere (+3.6 to +5.3pp CAGR, 21-28pp shallower
MDD). The choice between tiers is an ex-ante diversification judgment, not a
backtest call — see §5.

## 1. The 10,626-node scan: the global core is NOT on the plateau

5-asset simplex {GDE, NTSD, RSST, RSIT, ZROZ}, 5% steps
(`tables/global_simplex_grid.csv`, figs g08-g09):

- Primary 2000+: argmax **45/0/25/0/30** (Sharpe 0.866 — both international
  sleeves at zero; this is the US plateau rediscovered). Plateau (≥95% of
  max): 296 contiguous nodes with ranges GDE 20-80, **NTSD 0-15**, RSST 0-50,
  **RSIT 0-20**, ZROZ 15-45. **CORE-GLOBAL 20/15/20/20/25 is outside** (Sharpe
  0.746, 80th percentile) — its 35% international total exceeds what the
  plateau tolerates. Same result in all 8 start dates (0/8 in plateau).
- Canonical 1988+ (includes the Japan bust and Asia crisis — a *bad* era for
  US-only): argmax **25/0/45/0/30** (Sharpe 0.929), plateau 441 nodes, NTSD
  0-20 / RSIT 0-20, CORE-GLOBAL still outside (0.859, 90th percentile).
- Anti-overfitting discipline unchanged: the scan is a descriptive map, not a
  selection device `[advances_fin_ml, p.208-211, p.222-223]`,
  `[testing_tuning, p.327-335]`.

**The price of globalness** (`tables/global_intl_price_curve.csv`, fig g08):
forcing NTSD+RSIT ≥ X% costs, on the primary window, Sharpe 0.866 (0%) →
0.840 (15%) → 0.830 (20%) → 0.788 (35%) → 0.725 (50%). Roughly **−0.01 Sharpe
per +5pp of forced international allocation**, halving to ~−0.005/5pp on the
1988 window. Two structural reads from the constrained optima:

1. **When forced to go international, the optimizer always buys RSIT first
   and NTSD last** (best constrained nodes: 45/0/10/15/30, 45/0/0/25/30…).
   RSIT wraps international equity *with* the managed-futures stack — the
   sleeve that actually defends; NTSD is levered US+intl equity with no
   diversifier (NTSD lost −74% in the GFC vs RSIT −48%, and −37% in 2022 vs
   RSIT **−2%**).
2. ZROZ's plateau range rises to 25-35% in most constrained optima —
   international equity needs *more* duration convexity, not less.

## 2. Why: international equity is not a diversifier here

(`tables/global_corr_full_monthly.csv`, `global_crisis_capture.csv`, figs
g06-g07): monthly correlation SPY~VXUS = **0.854** (vs gold +0.17, MF −0.21,
ZROZ −0.14 against VT). In VT's 32 worst months (avg −8.5%): SPY −7.7%,
**VEA −8.8%, VXUS −8.8%, VWO −9.4%** — international equity falls *more* than
the global market in crashes, while gold +0.6%, MF +2.3%, ZROZ +3.7%. Adding
intl equity diversifies *who issues your equity risk*, not *whether you have
equity risk*. The three alternative sleeves do the crisis work in every
window; geography never does `[risk_parity, ch.5]`.

EM beta is the same story, worse: the +10% VWO pro-rata add (G9) lowered both
CAGR and Sharpe (0.719 vs 0.746) on 2000+.

## 3. Ablation verdicts (`tables/global_ablations_*.csv`, fig g12)

- **NTSI vs NTSD** (intl equity + US bonds vs US+intl equity): NTSI swap is
  mildly better (Sharpe 0.765 vs 0.746) and the benchmark-purist mix with
  NTSI (G2: 25/10/25/15/25) is better still (0.796) — if you hold an
  intl-equity efficient core, the bond-stacked version is the right one.
- **RSSB for ZROZ is the worst single change tested** (Sharpe 0.609, MDD
  −52.4%): VT+IEF stacked has no convexity and 2022 hits both legs — same
  failure mode as HFEA, milder dose.
- **NTSG core** (35 NTSG / 40 RSST / 25 ZROZ — global equity in ONE fund):
  Sharpe 0.744 ≈ CORE-GLOBAL with a slightly better MDD (−29.7%) and 3 fewer
  funds. If the goal is *simplicity* with VT-like geography, this is the
  cleanest expression; it costs ~1.2pp CAGR vs half-intl.
- **No-ZROZ renorm**: Sharpe −0.12, MDD −52.7% — identical lesson to the US
  study; the duration sleeve is non-negotiable in this construction.
- 1990 recession and Asia/LTCM 1998 (1988-window extras): both cores beat VT
  (e.g. Asia crisis: VT −6.9%, CORE-GLOBAL +23.8%, US CORE +29.5%).

## 4. The honest counterweight: 1970+ shrinks the cost to ~zero

On the longest (LOW-fidelity) window — which contains the 1970s-80s era of
*international* outperformance that 1988+ and 2000+ exclude —
(`tables/global_extended_metrics.csv`, fig g11):

| Portfolio (1970-2026, haircut MF) | CAGR | MDD | Sharpe |
|---|---|---|---|
| US CORE | 13.95% | −39.7% | 0.893 |
| **Half-intl 27.5/7.5/30/10/25** | 13.62% | −38.2% | **0.894** |
| CORE-GLOBAL 20/15/20/20/25 | 13.26% | −37.0% | 0.878 |
| 100% VT | 10.03% | −58.4% | 0.664 |

At moderate international weight, the 56-year Sharpe **ties** the US core.
The 2000+ "globalness cost" is partly an artifact of the US-dominance era
(2009-2026). This is exactly the regime argument for holding *some*
international: if the next decade looks like 1970-1988 instead of 2009-2026,
the global tilt is free insurance; if it looks like 2009-2026 again, it costs
~1pp/yr at the half-intl dose.

## 5. Consolidated verdict

1. **"Best possible global portfolio" by backtest = don't go global** — the
   unconstrained optimum is US-only in every window. We refuse to promote
   that argmax for the same reason we refused 45/25/30 in the US study.
2. **If global exposure is a policy choice** (ex-ante humility about US
   dominance persisting), the evidence shapes *how* to do it:
   - keep total international sleeves at **10-20%** (inside/near plateau
     tolerance; the 1970+ window says this dose is ~free);
   - route it **through RSIT** (MF-stacked wrapper, −2% in 2022) first, NTSD
     last (no diversifier, −74% in GFC); NTSI over NTSD if used;
   - keep **ZROZ at 25-30%**, never swap it for RSSB;
   - recommended expression: **27.5 GDE / 7.5 NTSD / 30 RSST / 10 RSIT /
     25 ZROZ** (grid-clean variant: 30/5/30/10/25), ≈ 64% US + 11% intl
     equity look-through, 40% MF, ~25% gold, 25% ZROZ.
3. **The canonical CORE-GLOBAL 20/15/20/20/25 stays valid as the
   maximum-diversification expression** — outside the Sharpe plateau, but
   still +3.6pp CAGR and −21pp MDD vs VT, and the right choice for whoever
   weighs single-country risk above backtest Sharpe. It is a judgment call,
   not a data call; the data only prices it (−0.05 to −0.10 Sharpe vs the
   half-intl dose).

**Caveats:** intl sims (VEA/VXUS/VT) are index reconstructions pre-inception;
the MF-proxy sensitivity caveat from the US study applies unchanged (KMLM-only
sleeves on 1988+, MFBLEND on 2000+); financing convention documented in g00
(−0.60pp/yr vs the old saved payload); everything gross of taxes/costs
`[testing_tuning, p.327-335]`.
