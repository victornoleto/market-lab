---
mission: "beat SPY 1× b&h gross-of-tax Sharpe by ≥0.05 on ≥2/3 datasets, MDD ≤ SPY, CAGR floor warning-only (mandate reframing 2026-04-29)"
mission_legacy: "beat avg(SPY 1× b&h, VT 1× b&h) Sharpe by ≥0.10 on ≥2/3 (iters 001-022 published scores anchored here)"
total_iterations: 43
winners_found: 6
status: hunting
latest_iteration: "043-2026-04-30-F1-TLT-variation"
latest_score: 90  # WINNER NEW; Phase 3B TLT-slot sensitivity on F1+SPLIT; baseline (TLT 15%) wins Sharpe 3/3 vs all 3 alternatives — recommendation reaffirmed
recommended_mf_sleeve: SPLIT  # 50/50 KMLMSIM + DBMFSIM for iter 023 chassis: best 26y-intersection Sharpe (1.0004) + best MDD (19.91%) + AUM stability via $3.2B DBMF
final_report_complete: true  # FINAL_REPORT_seven_portfolios.md produced 2026-04-30 (Task 23); 4 finalists scored (F4/F5/F6 skipped per Phase 1 routing — no global sleeves survived)
final_recommendation: "F1-iter023-with-SPLIT"  # CONFIRMED iter 043: iter 023 chassis (NTSX 25 / GDE 25 / KMLM 17.5 / DBMF 17.5 / TLT 15) — TLT slot variations all degrade Sharpe (KILL #1 fires); equity-heavy (no_tlt_to_equity) +1.68pp CAGR but +7.22pp MDD; RSSB-replaces-TLT redundant with NTSX bond leg (+7.28pp MDD); MF-only fallback ≈ baseline (Sharpe −0.04, MDD +0.13pp)
beats_incumbent: false  # iter 014 incumbent score 93 still > 91
cumulative_n_trials: 156  # 152 + 4 (iter 043 TLT variation)
incumbent_winner_iter: "014-2026-04-28-1920-intl-equity-tilt-on-iter011"
incumbent_winner_score: 93
strongest_substantive_advance: "023-2026-04-29-0150-iter011-plus-TLT-sleeve"
strongest_substantive_score_new: 86  # STRONG NEW SPY-only
strongest_substantive_score_legacy: 91  # WINNER LEGACY avg(SPY,VT)
note: "MANDATE REFRAMING 2026-04-29 (user-approved A.1-A.4): SPY-only baseline (was avg(SPY,VT)), Sharpe edge +0.05 (was +0.10), CAGR floor WARNING-ONLY (no longer blocks WINNER), MDD ≤ SPY strict (was +5pp slack). Iters 001-022 keep LEGACY published scores (cross-iter consistency); iter 023+ uses NEW. Justification: VT averaged in regime-mismatched intl-equity drag artifact 2010-2024, lowering vt_real bar artificially (Sharpe 0.71 avg vs 0.90 SPY-only); 0.05 hurdle separates signal from noise per [advances_fin_ml, p.222-223] DSR; CAGR-warning-only allows defensive Sharpe-frontier strategies (iter 019/020) to qualify per [risk_parity, ch.5]; MDD strict tightens to production-deploy reality. Code change: scoring.py exposes spy_benchmark/avg_benchmark/legacy_benchmarks, primary_benchmarks defaults to SPY-only, SHARPE_EDGE_HURDLE=0.05, MDD_CEILING_SLACK=0.0, _check_winner_conditions removes CAGR check. Prior note: ITER 015 (A.1 NTSX+NTSI+NTSE+GDE+KMLM 5-asset literal user thesis) — tier WINNER 93/100 5/5 conds LEGACY, ties iter 014 (93=93). DIRECTION A NOW CLOSED END-TO-END (012 RSSB, 013 VBRSIM, 014 VXUSSIM, 015 NTSI/NTSE — all subordinate to iter 011 on ≥2/3 deploy windows). proxies.py NTSX/NTSI/NTSE synth shared validated parity 2026-04-28."
---

# Long-Term Portfolio Loop — BASE MEMORY

**Read FIRST every iteration.** Conversation history is empty; this
file + `iterations/NNN-*/` are continuity. Process: `PROMPT.md`. Infra:
`INFRASTRUCTURE.md`.

> **Mandate reframing 2026-04-29** (A.1-A.4, user-approved): Mission switched
> from avg(SPY,VT)+0.10 to **SPY-only +0.05**, MDD ≤ SPY strict, CAGR floor
> warning-only. Iters 001-022 retain LEGACY scores (cross-iter consistency);
> iter 023+ uses NEW. See frontmatter `note` field for full rationale and code
> changes.

---

## Mission

**NEW (iter 023+)**: Find ONE long-term portfolio strategy that **beats SPY
1× b&h** (gross-of-tax) by **≥ 0.05 Sharpe on ≥ 2 of 3 datasets**, with
**MDD ≤ SPY** on ≥2/3 and passing the 7-gate battery. CAGR floor (≥0.8 ×
SPY CAGR on ≥2/3) is reported as warning but does not block WINNER.

**LEGACY (iters 001-022)**: Beat **avg(SPY,VT) + 0.10** Sharpe on ≥2/3,
with MDD ≤ avg+5pp and CAGR ≥ 0.8 × avg on ≥2/3 (CAGR was gating).

**Per-dataset benchmarks NEW (SPY-only, scoring.spy_benchmark)**:

| dataset | NEW benchmark | NEW Sharpe | NEW CAGR | NEW MDD (strict ceiling) |
|---|---|---:|---:|---:|
| **lh_56y** (1970+) | SPYSIM 40y | **0.680** | 11.47% | 55.14% |
| vt_real (17y) | SPY Tiingo 17y | **0.900** | 14.97% | 33.70% |
| ndx_real (16y) | SPY Tiingo 16y | **0.900** | 14.97% | 33.70% |

**Winner threshold NEW (SPY + 0.05)**: ≥ **0.730 / 0.950 / 0.950** on ≥2/3.

**Per-dataset benchmarks LEGACY (avg(SPY,VT), scoring.avg_benchmark)**:

| dataset | LEGACY benchmarks averaged | avg Sharpe | avg CAGR | max MDD (ceiling base) |
|---|---|---:|---:|---:|
| **lh_56y** (1970+) | VTSIM 56y + SPYSIM 40y | **0.671** | 10.73% | 58.35% |
| vt_real (17y) | VTSIM 17y + SPY 17y | **0.707** | 11.88% | 50.21% |
| ndx_real (16y) | QQQ 16y + SPY 16y | **0.924** | 16.98% | 35.12% |

**Winner threshold LEGACY (avg + 0.10)**: ≥ **0.77 / 0.81 / 1.02** on ≥2/3.

**Beat-incumbent threshold (current incumbent: iter 014, score 93)**: a NEW iter
becomes the incumbent winner only if `total_score > 93` (iter 014's score)
OR Sharpe edge ≥ +0.10 vs iter 014 on ≥ 2 of 3 datasets — i.e., lh_56y
≥ 1.155, vt_real ≥ 0.985, ndx_real ≥ 1.152.

**Caveat on iter 014 incumbency** (read every iter): iter 014 advanced the
incumbent on the score gate (93 > 91) but FAILS the Sharpe-edge gate vs
iter 011 (loses Sharpe on vt_real and ndx_real, ties on lh_56y). The score
advance is partially a benchmark-migration artifact (iter 011 was scored on
legacy `educational` window, iter 014 on the new lh_56y framework). Future
hunting should treat iter 011 (NTSX+GDE+KMLM 35/25/40) as the substantive
benchmark for live windows even though iter 014 holds the rule-defined
incumbent slot. **For deploy-readiness conversations, iter 011 is still
the architectural reference.**

**Context from related research (read alongside)**:
- `_archive/strategy_hunt_loop/FINAL_REPORT.md` — 78 iters, 1 strict
  winner (iter 079 multi-asset top-K momentum). The "DON'T retest"
  section consolidates 57 closed dead-end families.
- `_archive/strategy_hunt_loop/WINNER/iter_035-*` and `iter_079-*` —
  best long-window-validated strategies on 40y synth (iter 035 CAGR
  19.6%, iter 079 strict 5/5 winner). These ARE referenced when
  comparing Pareto frontier — but our mission is now SPY+VT, not iter 035.
- `global_factor_tilt_loop/iterations/009-*` — HAA+Gold reference,
  Sharpe frontier of the predecessor loop (gross 1.120 edu).

**Tax model**: gating uses gross-of-tax. Net-of-tax via
`studies/_shared/tax_engine.py` (`AnnualDarfEngine`, Lei 14.754/2023)
is computed and reported in `final_report.md` as deploy-readiness
diagnostic only — does NOT influence tier or winner status.

Winner criteria live in `WINNER_AND_RANKING.md`.
Dead-ends live in `DEAD_ENDS.md`.

**Hard context**: mandate §1 MAINTENANCE MODE (2026-04-23) applies to
short-hold strategies (Plano A/B/D dormant). The long-term portfolio
thesis is the LIVE workstream — any winner here is a candidate
requiring mandate §7 override before deployment.

---

## Incumbent winner (the bar to beat)

| iter | slug | score | lh_56y S/CAGR/MDD | vt_real S/CAGR/MDD | ndx_real S/CAGR/MDD | note |
|---|---|---|---|---|---|---|
| **014** | intl-equity-tilt-on-iter011 | **93/100 🏆** | 1.055 / 11.78% / 29.52% (1986-2026 40y eff) | 0.885 / 11.14% / 27.99% | 1.052 / 12.11% / 18.40% | Static 35% NTSX + 10% VXUSSIM + 25% GDE + 30% KMLM. All 5 strict conds met vs avg(SPY,VT) (3/3 +0.10 edges). Score 93 > iter 011's 91 → mechanical beats_incumbent=true. **CAVEAT**: substantively LOSES Sharpe to iter 011 on 2/3 datasets (lh_56y +0.009, vt_real −0.075, ndx_real −0.052). Score advance partially due to benchmark migration (iter 011 was on legacy `educational`). For deploy-readiness conversations, iter 011 (NTSX+GDE+KMLM 35/25/40) is the substantive architectural reference. iter 014 differs from iter 011 only by a 10% VXUSSIM swap (35/10/25/30 vs 35/0/25/40) — modest diversification benefit on long-history balanced against modest live-window drag. |
| **011** | ntsx-gde-kmlm-static | 91/100 (legacy benchmarks) | 1.046 (lh_56y retro) / 11.58% / 26.04% (1995-2026 31y legacy) | 0.960 / 10.95% / 21.22% | 1.104 / 11.64% / 14.12% | (PRIOR INCUMBENT 2026-04-28 → demoted to substantive reference 2026-04-28). Static 35% NTSX + 25% GDE + 40% KMLM stack. All 5 strict conditions met under legacy edu benchmarks. **Wins Sharpe vs iter 014 on vt_real and ndx_real**; tied on lh_56y. The architectural ceiling for constant-weight stacks; iter 014's incumbency is rule-mechanical (score advance), not substantive (Sharpe regression on live windows). |

---

## Top-K strategies ranked

Original score earned on legacy `educational` window (1995-2026, 31y). After
retro re-backtest 2026-04-28, every iter also has lh_56y numbers — note the
ranking shifts substantially under lh_56y (iters using KMLM benefit from the
FF-MoM splice 1986-1988, an academic equity-momentum proxy with Sharpe ~1.9
vs KMLM's long-run ~0.5; pre-1988 KMLM-heavy returns are ~3× overstated).

| rank | iter | slug | score | tier | scoring basis | **lh_56y gross Sharpe (loose)** | lh_56y strict | lh_56y window |
|---|---|---|---|---|---|---|---|---|
| **NEW** | **023** | **iter011-plus-TLT-sleeve** | **86 NEW / 91 LEGACY** | **STRONG NEW / WINNER LEGACY** ⭐ ★ | NEW SPY-only +0.05 | **1.189** ⭐ | **1.106** ⭐ | 1986-2026 (40y eff) |
| 1 | **014** | **intl-equity-tilt-on-iter011** | **93 🏆** | **WINNER LEGACY (mechanical incumbent ⚠️)** | LEGACY avg(SPY,VT)+0.10 | **1.055** | n/a | 1986-2026 (40y eff) |
| 2 | **015** | A1-5asset-global-stack | **93** | WINNER LEGACY (tier) ⚠️ | LEGACY | 1.081 | 1.007 | 1986-2026 4-asset / 1994-2026 5-asset |
| 3 | **016** | **B5-UMD-overlay** | **91** | WINNER LEGACY (tier, first +signal) ⭐ | LEGACY | **1.223** ⭐ | **1.133** ⭐ | 1986-2026 (40y eff) |
| 4 | **011** | ntsx-gde-kmlm-static | **91** | WINNER LEGACY (substantive ref) | LEGACY | 1.046 | 1.045 | 1986-2026 (40y) |
| 4 | **013** | factor-tilt-on-iter011 | **91** | WINNER LEGACY (tier) ⚠️ | LEGACY | **1.126** ⭐ | n/a | 1986-2026 (40y eff) |
| **NEW** | **025** | iter011-VXX-real-diagnostic | **83 NEW / 93 LEGACY** | STRONG NEW / WINNER LEGACY (DE-025) | NEW | 1.107 | 1.078 | 2009-2026 (effective) |
| **NEW** | **024** | iter011-MDD-trigger-defensive | **82 NEW / 87 LEGACY** | STRONG NEW / STRONG LEGACY (DE-024) | NEW | 1.145 | 1.062 | 1986-2026 (40y eff) |
| 5 | **012** | ntsx-gde-rssb-kmlm-global-stack | **88** | STRONG LEGACY | LEGACY | 1.011 | n/a | 1986-2026 (40y eff) |
| — | 007 | haa-defensive-kmlm-cash | 75 | STRONG | 0.983 (net) | **1.150** ⭐ | 1994-2026 (32y) |
| — | 008 | haa-dual-canary | 73 | PROMISING | 0.983 (net) | 1.120 | 1994-2026 (32y) |
| — | 009 | haa-gayed-trend-canary | 73 | PROMISING | 0.983 (net) | 1.120 | 1994-2026 (32y) |
| — | 006 | haa-rsit-synth | 71 | PROMISING | 0.869 (net) | **1.154** ⭐ | 1994-2026 (32y) |
| — | 005 | haa-rsst-rssb-cta | 70 | PROMISING | 0.953 (net) | **1.253** ⭐ | 1994-2026 (32y) |
| — | 004 | haa-global-factor-tilt | 69 | PROMISING | 0.990 (net) | **1.117** ⭐ | 1994-2026 (32y) |
| — | 010 | haa-vol-throttle | 60 | PROMISING | 1.020 (net) | **1.179** ⭐ | 1994-2026 (32y) |
| — | 001 | baa-g12-balanced | 58 | MARGINAL | 0.975 (net) | 1.094 | 1995-2026 (31y) |
| — | 002 | composite-momentum-standard | 55 | MARGINAL | 0.940 (net) | 1.024 | 1994-2026 (32y) |
| — | 003 | global-factor-cta-stack | 54 | MARGINAL | 0.823 (net) | 0.839 | 1994-2026 (32y) |

⭐ = retro lh_56y gross Sharpe ABOVE iter 011 (1.046). Caveat: iter 011 has
40y window (8y more than HAA-style iters bottlenecked by VWOSIM 1994). The
1986-1994 KMLM portion uses FF MoM proxy → expected to slightly overstate
iter 011's lh_56y Sharpe; iter 011 is still likely competitive but not
dominant on lh_56y. Apples-to-apples comparison requires same-window cropping
(future work: align all to 1994-2026 or use a non-KMLM-dependent benchmark).

⚠️ = tier WINNER per scoring rubric (≥90 + winner_conds_met=true vs avg(SPY,VT))
but does NOT advance the iter 011 incumbent (ties on score 91=91, fails the
+0.10 Sharpe edge gate on all 3 datasets). Listed alongside iter 011 in top-K
because rubric says WINNER, but BASE_MEMORY's `incumbent_winner_iter` stays 011.

---

## Iteration log (newest first)

### 043 — 2026-04-30 — F1-TLT-variation (WINNER NEW 90 — Phase 3B TLT-slot sensitivity; baseline reaffirmed, KILL #1 fires for all 3 alternatives)

- **Phase 3B TLT-slot variation diagnostic.** Hypothesis: F1+SPLIT recommendation (NTSX 25 + GDE 25 + KMLM 17.5 + DBMF 17.5 + TLT 15) keeps 15% TLT as duration hedge — does removing/replacing TLT improve the portfolio? User-driven question pre-finalisation: equity > bonds for accumulation, but does the data support removing TLT? Citation `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking + `[ilmanen_expected_returns, ch.19]` duration-vs-MF crisis-alpha + ReSolve/Newfound RSSB methodology (2023).
- 4 configs: `f1_split_baseline` (TLT 15%, current rec), `f1_no_tlt_to_equity` (TLT→NTSX/GDE +7.5 each), `f1_no_tlt_to_mf` (TLT→KMLM/DBMF +3.75 each), `f1_rssb_replaces_tlt` (TLT 15%→RSSB 15%).
- **Means across 3 datasets (lh_56y, vt_real, ndx_real)**:
  - `f1_split_baseline` (baseline): Sharpe **1.067**, CAGR 10.62%, MDD 17.63% ← winner
  - `f1_no_tlt_to_equity`:           Sharpe 0.992, CAGR **12.30%**, MDD 24.84% (Δ Sharpe −0.075, Δ CAGR +1.68pp, Δ MDD +7.22pp)
  - `f1_no_tlt_to_mf`:                Sharpe 1.026, CAGR 10.68%, MDD 17.76% (Δ Sharpe −0.041, Δ CAGR +0.06pp, Δ MDD +0.13pp)
  - `f1_rssb_replaces_tlt`:           Sharpe 0.955, CAGR 11.44%, MDD 24.91% (Δ Sharpe −0.112, Δ CAGR +0.82pp, Δ MDD +7.28pp)
- **KILL #1 ✅ FIRES**: no alternative beats baseline mean Sharpe on ≥1/3 datasets — baseline wins Sharpe **3/3** vs every alternative.
- **KILL #6 (capital accumulation: CAGR > +0.5pp AND MDD ≤ +5pp on ≥2/3)**: f1_no_tlt_to_equity fails MDD (+7.22pp); f1_rssb_replaces_tlt fails MDD (+7.28pp); f1_no_tlt_to_mf fails CAGR (+0.06pp < +0.5pp threshold). All 3 alternatives **fail** capital-accumulation test.
- **Surprise finding — RSSB is structurally redundant**: f1_rssb_replaces_tlt is the worst alternative (Sharpe −0.112, MDD +7.28pp) despite the appealing "stocks AND bonds in one ticker" thesis. Mechanism: RSSB (100% global stocks + 100% Treasury via derivatives) at 15% becomes 30% effective exposure, but the 15% Treasury leg is correlated with NTSX's embedded 15% IEF bond leg (already in baseline), so the marginal duration is degraded; meanwhile the 15% added stocks dominate drawdowns since NTSX+GDE already provide 45% equity exposure. Replacing pure-bond TLT with stocks-overlaid RSSB **reduces effective bond hedge AND adds equity beta** — the worst-of-both-worlds in a portfolio that already saturates the 60/40 frontier with NTSX+GDE.
- **f1_no_tlt_to_mf is deploy-equivalent fallback**: Δ Sharpe −0.041, Δ MDD +0.13pp, Δ CAGR +0.06pp — basically baseline. Useful if real-money MF AUM concentration becomes a deploy concern (50% in two MF tickers); otherwise no improvement.
- **f1_no_tlt_to_equity is the canonical CAGR-vs-MDD trade**: +1.68pp CAGR for +7.22pp MDD — typical "more equity = more compounding, bigger crashes". Sharpe degrades. Not recommended for any user not already pre-committed to high-equity stacks.
- **Final recommendation reaffirmed**: F1+SPLIT (`f1_split_baseline`) stands as the production recommendation. User-decision-relevant insight: in a portfolio that already contains levered equity-plus-bonds stacks (NTSX 25 + GDE 25 = 45% equity-stack with embedded ~30% bond exposure), the dedicated 15% TLT sleeve is **not redundant** — it's the cheapest marginal drawdown insurance available. Removing it for more equity (no_tlt_to_equity) or for stacked-equity-plus-bonds (RSSB) trades 1.0-1.7pp CAGR for 7+pp MDD.
- **Mandate score**: 90/100 WINNER NEW (winner_conds met), DSR p=2.58e-05 / 5.50e-04 / 1.50e-04 (cumulative_n_trials=156). Score is per-config metric for `f1_split_baseline` selected (baseline = winner of variation sweep).
- **Phase 3 implication**: F1+SPLIT confirmed end-to-end (Phase 3 MF sleeve diagnostic + Phase 3B TLT slot diagnostic). FINAL_REPORT_seven_portfolios.md recommendation `F1-iter023-with-SPLIT` is robust to both deploy-relevant axes tested. Task 24 (user decision + mandate §7 override) ready to execute.

### 042 — 2026-04-30 — MF-sensitivity (STRONG NEW 88 — Phase 3 deploy diagnostic; deploy recommendation = SPLIT 50/50 KMLM+DBMF on apples-to-apples 26y intersection)

- **Phase 3 MF-sleeve deploy diagnostic.** Hypothesis: substitute iter 023's 35% KMLMSIM with DBMF / 50-50 split / CTA-proxy and determine deploy-ready MF sleeve recommendation under AUM stability constraint (DBMF $3.2B vs KMLM $600M for 20-30y). Holds NTSX 25 / GDE 25 / TLT 15 constant. KILL #1 not applicable (deploy diagnostic, not sleeve test). Citation `[ilmanen_expected_returns, ch.19]` MF crisis-alpha + iMGP DBi DBMF prospectus + KFA MLM Index prospectus + Simplify CTA prospectus.
- 4 configs: `mf_kmlm` (baseline iter 023), `mf_dbmf` (full DBMF), `mf_split` (50/50 KMLM+DBMF 17.5%/17.5%), `mf_cta_proxy` (INCOMPLETE — structurally = mf_kmlm because Altis multi-strategy engine not modeled in testfolio).
- Selector picked `mf_kmlm` (full 38y lh_56y window Sharpe 1.111) by `max mean(Sharpe/SPY_Sharpe)` across datasets — **but this is window-biased**: KMLMSIM 1988+ vs DBMFSIM 2000+. The selector compares kmlm on 38y vs dbmf/split on 26y on lh_56y — NOT apples-to-apples.
- **Apples-to-apples 26y intersection (2000-2026)** on lh_56y:
  - mf_kmlm  truncated: Sharpe **0.9626**, CAGR 9.73%, MDD 21.13% ← worst
  - mf_dbmf  native:    Sharpe **0.9947**, CAGR 10.42%, MDD 21.78%
  - mf_split native:    Sharpe **1.0004**, CAGR 10.10%, MDD 19.91% ← best Sharpe + best MDD
- **Deploy recommendation = SPLIT** (50/50 KMLMSIM + DBMFSIM, 17.5% each). Rationale per hypothesis decision rule: split Sharpe ≥ both within 0.05 (split−DBMF=+0.006, split−KMLM=+0.038) ⇒ recommend split for engine diversification. Bonus: best 26y MDD (19.91%), AUM stability (50% sleeve at $3.2B DBMF), engine diversification (KMLM pure-trend KFA Index + DBMF SG CTA Index replication). CAGR cost vs DBMF: −0.32pp; acceptable trade-off.
- **Why not pure KMLM?** Full-window Sharpe 1.111 is a window artifact — 1988-1999 includes KMLM Index's golden trend era (LTCM '98 vol harvest, '90s commodity trends) not representative of 20-30y forward.
- **Why not pure DBMF?** Hypothesis rule "DBMF Sharpe ≈ KMLM within 0.05 ⇒ recommend DBMF for AUM" fires (Δ+0.032), but split rule trumps because split captures the AUM advantage of DBMF (50% of sleeve at $3.2B issuer) while retaining KMLM track record + transparency.
- **CTA Simplify INCOMPLETE flag**: `mf_cta_proxy` is KMLMSIM duplicated. Simplify CTA's Altis Partners engine (multi-strategy: trend + carry + mean-reversion + risk-off overlay) needs a sub-strategy synth before honest comparison. Future work.
- **Mandate score**: 88/100 STRONG NEW (winner_conds met), DSR p=2.96e-09 / 9.59e-04 / 5.18e-04 (cumulative_n_trials=152). The selected `mf_kmlm` row is the full-window incumbent metrics; the deploy-ready sleeve choice from this iter is `SPLIT`, not the auto-selected baseline.
- **Phase 3 implication**: Deploy diagnostic complete. The iter 023 chassis (NTSX 25 / GDE 25 / MF 35 / TLT 15) is robust to MF engine choice — all 3 honest configs pass SPY+0.05 winner conditions. Deploy recommendation **SPLIT** maximises Sharpe + minimises MDD + diversifies issuer/engine; pure-DBMF is acceptable second choice (CAGR-leader); pure-KMLM for users prioritising 38y history quote (acknowledging window bias). Task 23 (FINAL_REPORT_seven_portfolios.md) should anchor the iter 023 chassis MF sleeve as `SPLIT` for production deploy guidance.

### 041 — 2026-04-30 — F7-US-Stacked-MF (WINNER NEW 91 — Phase 2 finalist 3/3, RSST stacked-MF, KILL #2 fires monotonic, KILL #4 vs iter 023 fires lh_56y)

- **Phase 2 finalist construction iter 3/3.** Hypothesis: stacked managed-futures via RSST (ReturnStacked US Equity & MF, 100% SPY + 100% KMLM via 2× notional) combined with NTSX/GDE/KMLM/TLT. F7 is **independent of Phase 1** sleeve findings (RSST is its own axis). 4 configs sweep RSST 15→50%. KILL #5 already validated pre-iter 030 (RSST standalone Sharpe < 1.5). Citation `[risk_parity, ch.5]` Carlson + ReSolve/Newfound Return Stacked methodology (2023).
- Selected `f7_lite` (NTSX 25 + RSST 15 + GDE 25 + KMLM 20 + TLT 15). Gross Sharpe **1.072 / 0.978 / 1.144**. CAGR 12.73% / 11.90% / 12.86%. Score **91/100 WINNER NEW** (winner_conds=True: 3/3 +0.05 vs SPY, gates, MDD strict, DSR p<0.05). Notional ~150%.
- **vs iter 023 baseline (1.189 / 1.004 / 1.135)**: −0.117 / −0.026 / **+0.009**. Wins ndx_real cosmetic, loses lh_56y substantive, near-flat vt_real. CAGR is HIGHER on all 3 datasets (12.73% vs 11.52% iter 023) — RSST adds notional that improves CAGR but marginally degrades Sharpe.
- **RSST weight sweep (KILL #2 monotonic regression)**:
  - `f7_lite` (15% RSST):       1.072 / 0.978 / 1.144 ← selected
  - `f7_balanced` (30% RSST):   1.068 / 0.958 / 1.121
  - `f7_rsst_heavy` (40% RSST): 1.058 / 0.942 / 1.108
  - `f7_pure_stack` (50% RSST, NTSX 0%): 1.057 / 0.925 / 1.080
  - **KILL #2 ✅ FIRES**: Sharpe falls monotonically with RSST weight on ALL 3 datasets. RSST stacking philosophy does NOT improve over separate NTSX+KMLM sleeves; the 2× notional adds CAGR but the 50/50 SPY+KMLM internal split is sub-optimal vs iter 023's 35% KMLM standalone.
- **KILL #1 (no-positive-config) ✅ SURVIVES**: f7_lite beats iter 023 on 1/3 datasets (ndx_real +0.009) — barely. Cosmetic.
- **KILL #4 (frankenstein degradation, independent axis)**: F7 best Sharpe lh_56y 1.072 < iter 023 baseline 1.189 by 0.117 — **KILL #4 FIRES on lh_56y**. Stacked-MF philosophy degrades long-history Sharpe relative to iter 023's diversified-stacking blend. F7 **wins WINNER tier** purely on the SPY-only +0.05 mandate (all 3 datasets clear SPY+0.05) + CAGR/MDD/DSR gates, NOT on Sharpe edge vs iter 023.
- **Mechanism**: RSST 100% SPY + 100% KMLM in a single wrapper is structurally equivalent to a 50/50 NTSX+KMLM blend (NTSX = 90%SPY+60%IEF). Adding RSST to a portfolio that already has NTSX (90%SPY) creates SPY beta concentration without benefit — the IEF sleeve in NTSX is more diversifying than KMLM at the margin (per `[risk_parity, ch.5]` 60/40 stack default).
- **Phase 2 implication**: F7 best (f7_lite, score 91) beats F2 best (f2_spmo_heavy, score 85) and F3 best (f3_spmo_5_subKMLM, score 88) on score, but loses Sharpe substantively to F1 (iter 023, score 86 NEW / 91 LEGACY) on lh_56y. Stacked-MF philosophy validated as **dominated** by separate-sleeve diversification. Phase 2 winner selection (Task 21) likely settles on F1 (iter 023) on Sharpe + simplicity; F7 is the strongest CAGR-frontier finalist if user prioritises CAGR ≥ 12% over Sharpe edge.

### 040 — 2026-04-30 — F3-US-Hybrid-SPMO (STRONG NEW 88 — Phase 2 finalist 2/3, SPMO sleeve add validates, KILL #2 fires monotonic)

- **Phase 2 finalist construction iter 2/3.** Hypothesis: F3 = iter 023 (NTSX+GDE+KMLM+TLT) + SPMO at 4 weights (5/10/15/20%) using KMLM-substitution rule (Phase 1B iter 036 finding: subKMLM peaks ndx_real +0.044). Citation `[risk_parity, ch.5, p.10]` + `[stocks_on_the_move, p.21-30]`.
- Selected `f3_spmo_5_subKMLM` (NTSX 25 + GDE 25 + KMLM 30 + TLT 15 + SPMO 5). Gross Sharpe **1.107 / 1.008 / 1.173**. CAGR 11.40% / 10.63% / 11.49%. Score **88/100 STRONG NEW**.
- **vs iter 023 baseline (1.189 / 1.004 / 1.135)**: −0.082 / **+0.004** / **+0.038**. Beats on 2/3 datasets (vt_real cosmetic, ndx_real substantive +0.038). Matches Phase 1B iter 036 subKMLM finding (ndx_real +0.044 at SPMO 10%) within ~0.006 of expectation; SPMO at 5% is the sweet spot here.
- **SPMO weight sweep (KILL #2 monotonic regression)**:
  - `f3_spmo_5_subKMLM`:  1.107 / 1.008 / 1.173 ← selected
  - `f3_spmo_10_subKMLM`: 1.087 / 0.994 / 1.179 (peak ndx_real)
  - `f3_spmo_15_subKMLM`: 1.060 / 0.973 / 1.174
  - `f3_spmo_20_subKMLM`: 1.028 / 0.947 / 1.162
  - **KILL #2 ✅ FIRES on lh_56y/vt_real (monotonic decline)**, but ndx_real shows peak at 10% (1.179, +0.044 vs iter 023) — **non-monotonic on ndx_real**. Mixed signal: SPMO adds momentum tilt that boosts ndx_real but dilutes KMLM crisis-alpha → lh_56y degradation. 5% is the cleanest blend (best 2/3 scoreboard).
- **KILL #1 (no-positive-config) ✅ SURVIVES**: f3_spmo_5_subKMLM beats iter 023 on 2/3 datasets (vt_real +0.004 cosmetic, ndx_real +0.038 substantive).
- **KILL #4 (frankenstein degradation vs iter 023 + SPMO Phase 1)**: F3 best lh_56y 1.107 < iter 023 baseline 1.189 by 0.082 — degrades. F3 best ndx_real 1.173 ~= SPMO Phase 1 best 1.167. F3 mean across datasets = (1.107+1.008+1.173)/3 = **1.096** vs iter 023 mean **1.109** — **0.013 below** iter 023 mean. Borderline KILL #4 (Sharpe degraded but ndx_real edge gained). Per spec, F3 finalist remains valid since SPMO addition is mildly net-positive on the dataset that mattered (ndx_real); F1 (iter 023 unchanged) remains an option for users who weight lh_56y heavier.
- **Phase 2 implication**: F3 score 88 beats F2 (85) but loses to F7 (91) and incumbent iter 023 (86 NEW / 91 LEGACY). F3 is the strongest US-Hybrid finalist if user prioritises ndx_real edge in deploy regime (2010-2024 US-large-cap regime).

### 039 — 2026-04-30 — F2-US-Factor-only (STRONG NEW 85 — Phase 2 finalist 1/3, pure factor philosophy non-additive, KILL #4 fires)

- **Phase 2 finalist construction iter 1/3.** Hypothesis: pure factor philosophy with VTI vanilla + AVUV small-value + SPMO momentum + KMLM/TLT/GLD diversifiers. **6 ETFs, 100% notional, no leverage**. AVUV included despite Phase 1A/1B negative substantive (best subGDE Δ lh_56y −0.021 is least bad of Avantis family). 4 configs sweep balanced vs factor-heavy vs sleeve-tilted weights. Citation `[risk_parity, ch.2, p.37-41]` Fama-French + `[stocks_on_the_move, p.21-30]` Clenow.
- Selected `f2_spmo_heavy` (VTI 30 + AVUV 10 + SPMO 20 + KMLM 20 + TLT 10 + GLD 10). Gross Sharpe **1.086 / 0.874 / 1.087**. CAGR 11.38% / 9.79% / 11.35%. Score **85/100 STRONG NEW**.
- **vs iter 023 baseline (1.189 / 1.004 / 1.135)**: −0.103 / −0.130 / −0.048. Loses on 3/3 datasets — most degradation of the 3 Phase 2 finalists.
- **Configs grid (Sharpe lh / vt / ndx)**:
  - `f2_balanced` (VTI 35 + AVUV 15 + SPMO 10 + ...):     1.065 / 0.857 / 1.056
  - `f2_factor_heavy` (VTI 25 + AVUV 25 + SPMO 15 + ...): 1.040 / 0.818 / 1.022
  - `f2_avuv_heavy` (VTI 30 + AVUV 25 + SPMO 5 + ...):    1.057 / 0.828 / 1.013
  - `f2_spmo_heavy` (VTI 30 + AVUV 10 + SPMO 20 + ...):   1.086 / 0.874 / 1.087 ← selected
  - **SPMO-heavy wins** consistent with Phase 1 findings (SPMO is the only +signal sleeve); AVUV-heavy is the worst, factor-heavy (both AVUV+SPMO maxed) is also worse than balanced.
- **KILL #1 (no-positive-config) ✅ FIRES**: 0/3 datasets beat iter 023 under any of the 4 configs. F2 cannot achieve the +signal threshold without leverage.
- **KILL #4 (frankenstein degradation vs constituent Phase 1 best) ✅ FIRES on all 3 datasets**:
  - AVUV Phase 1 best: lh 1.115 / vt 0.996 / ndx 1.140 (iter 028).
  - SPMO Phase 1 best: lh 1.117 / vt 1.009 / ndx 1.167 (iter 030).
  - **Constituent mean**: lh **1.116** / vt **1.003** / ndx **1.153**.
  - F2 best: lh 1.086 / vt 0.874 / ndx 1.087.
  - **F2 < constituent mean on ALL 3 datasets** by 0.030 / 0.129 / 0.066. Combination is **non-additive** — the AVUV+SPMO+VTI factor stack has high internal correlation (all US large/mid cap), so the marginal Sharpe of SPMO is diluted when both factors share equity beta with vanilla VTI.
- **Mechanism**: pure-factor 1× equity stack has no leverage to amplify factor alpha; KMLM 20% + TLT 10% + GLD 10% diversification is similar to iter 023's KMLM 35% + TLT 15% but lacks NTSX/GDE's stacked bond carry. Factor alpha alone (~30bps/y AVUV + ~50bps/y SPMO capture) cannot compensate for the absent IEF/IEFA bond stack carry.
- **Phase 2 implication**: F2 finalist passes the structural construction bar (verdict tier STRONG, score 85) but is the **weakest of the 3 Phase 2 finalists** on Sharpe and on KILL #4. Recommended for users prioritising simplicity (6 single-style ETFs, no stacking wrappers, lowest TER) over Sharpe edge — but strictly worse than iter 023 on the gross Sharpe metric. Confirms `[risk_parity, ch.2]` insight: pure factor portfolios cannot match cap-efficient stacking in the 2010-2024 US-large-cap regime.

### 038 — 2026-04-29 — AVEM-realloc (STRONG NEW 79 — Phase 1B sub-source variation FINAL, KILL #1 fires, worst Phase 1B sleeve)

- **Phase 1B sub-source variation iter 6/6 (FINAL).** Hypothesis: Phase 1A iter 032 AVEM failure (BOTH KILLs fired, steepest decline of all 6 Phase 1A sleeves, Δ −0.107 / −0.035 / −0.020). Retests at fixed 10% under 3 sub sources. Citation `[ilmanen_expected_returns, ch.19]`.
- Synth: AVEMSIM = `VWOSIM + 125bps/y tilt premium`. INCOMPLETE — VWOSIM passive EM, 125bps highest of AV* family.
- **WINDOW CAVEAT (CRITICAL)**: VWOSIM starts 1994-05-04 → effective lh_56y = 32y (1994-2026), NOT 56y. Sub-source variation does not change this. 1994-2026 was US-large-cap regime ~3-4pp/yr CAGR ahead of EM, biasing test. vt_real (2008+) and ndx_real (2010+) apples-to-apples vs other iters.
- Selected `avem10_subGDE` (10% AVEM, sub from GDE). Gross Sharpe **1.093 / 0.920 / 1.070**. Score 79/100 STRONG.
- vs iter 023 substantively: **−0.096 / −0.084 / −0.065** — loses on **3/3 datasets**.
- **Substitution source comparison (10% AVEM, fixed weight)**:
  - `subGDE` (selected): 1.0928 / 0.9203 / 1.0704 → Δ −0.096 / −0.084 / −0.065
  - `subNTSX`:           1.0727 / 0.9284 / 1.0664 → Δ −0.116 / −0.076 / −0.069
  - `subKMLM`:           1.0247 / 0.9181 / 1.0879 → Δ −0.164 / −0.086 / −0.047
  - **Best sub = GDE**; **worst = KMLM** (lh_56y −0.164).
- **KILL #1 (no-positive-config) ✅ FIRES**: 0/3 datasets beat iter 023 under any sub source. Live windows (vt_real and ndx_real, apples-to-apples) confirm subordination — window caveat does not save AVEM.
- **AVEM sleeve closure REAFFIRMED.** Worst Phase 1B sleeve overall (Δ vt_real −0.084 vs second-worst IDMO −0.070).
- **Phase 1A+1B combined finding**: ALL 3 Avantis factor sleeves (AVUV/AVDV/AVEM) closed under sub-source variation. F5 Global Factor-only finalist cannot proceed with non-momentum factors. **Phase 1B COMPLETE (6/6 iters).**

### 037 — 2026-04-29 — IDMO-realloc (STRONG NEW 81 — Phase 1B sub-source variation, KILL #1 fires, cosmetic edge lost)

- **Phase 1B sub-source variation iter 5/6.** Hypothesis: Phase 1A iter 031 IDMO failure (KILL #2 fired, KILL #1 cosmetic 1/3 ndx_real +0.005). Retests at fixed 10% under 3 sub sources. Citation `[ilmanen_expected_returns, ch.19]` + `[stocks_on_the_move, p.21-30]`.
- Synth: IDMOSIM = `VEASIM + 0.60 × UMD_KF − 60bps/y`. INCOMPLETE — uses US UMD_KF as proxy for intl momentum (per AMP 2013, intl momentum has 0.5-0.7 corr with US, may overstate edge by 10-30%). KILL #3 PASS (synth standalone Sharpe ~0.726).
- Selected `idmo10_subGDE` (10% IDMO, sub from GDE). Gross Sharpe **1.137 / 0.934 / 1.102**. Score 81/100 STRONG.
- vs iter 023 substantively: **−0.052 / −0.070 / −0.033** — loses on **3/3 datasets**.
- **Substitution source comparison (10% IDMO, fixed weight)**:
  - `subGDE` (selected): 1.1375 / 0.9339 / 1.1019 → Δ −0.052 / −0.070 / −0.033
  - `subNTSX`:           1.1028 / 0.9465 / 1.1034 → Δ −0.086 / −0.058 / −0.032
  - `subKMLM`:           1.0659 / 0.9453 / 1.1291 → Δ −0.123 / −0.059 / −0.006
  - **Best sub = GDE**; **worst = KMLM** (lh_56y −0.123).
- **KILL #1 (no-positive-config) ✅ FIRES**: 0/3 datasets beat iter 023 under any sub source. Phase 1A's cosmetic ndx_real +0.005 edge lost at 10% under any sub source (drops to −0.033 subGDE, −0.006 subKMLM).
- **IDMO clearly subordinate to SPMO** at every sub source. SPMO at 10% subKMLM gave ndx_real **+0.044**; IDMO at 10% subKMLM gives **−0.006** (−0.050 worse). Confirms intl momentum factor structurally weaker (AMP 2013 + IDMOSIM US-UMD proxy weakness).
- **IDMO sleeve closure REAFFIRMED.** SPMO is the only momentum sleeve for Phase 2.

### 036 — 2026-04-29 — SPMO-realloc (STRONG NEW 86 — Phase 1B sub-source variation, ndx_real +signal CONFIRMED ROBUST)

- **Phase 1B sub-source variation iter 4/6.** Highest-priority Phase 1B test — Phase 1A iter 030 SPMO was the only sleeve to survive both KILLs (Δ −0.072 / +0.005 / +0.032). Retests at fixed 10% under 3 sub sources to test if reallocating sub source amplifies ndx_real +signal or recovers lh_56y drag. Citation `[stocks_on_the_move, p.21-30]` Clenow + JT 1993.
- Synth: SPMOSIM = `SPYSIM + 0.60 × UMD_KF − 35bps/y`. KILL #3 PASS: standalone Sharpe = 0.828 (< 1.5).
- Selected `spmo10_subGDE` (10% SPMO, sub from GDE). Gross Sharpe **1.161 / 0.987 / 1.157**. Score 86/100 STRONG.
- vs iter 023 substantively: **−0.028 / −0.017 / +0.022** — beats iter 023 on **1/3 datasets** (ndx_real +0.022 substantive).
- **Substitution source comparison (10% SPMO, fixed weight)**:
  - `subGDE` (selected): 1.1611 / 0.9873 / 1.1570 → Δ −0.028 / −0.017 / **+0.022**
  - `subNTSX`:           1.1300 / 0.9998 / 1.1587 → Δ −0.059 / −0.004 / **+0.024**
  - `subKMLM`:           1.0869 / 0.9939 / 1.1789 → Δ −0.102 / −0.010 / **+0.044** ⭐
  - **All 3 sub sources beat iter 023 on ndx_real**. subKMLM maximizes ndx_real edge (+0.044, larger than Phase 1A's +0.032) at the cost of worst lh_56y. subGDE preserves lh_56y best.
- **KILL #1 (no-positive-config) ✅ SURVIVES**: 1/3 datasets beat iter 023 under every sub source. ndx_real +signal **structural and robust**.
- **SPMO is the ONLY Phase 1A/1B sleeve with robust ndx_real +signal across all reallocation patterns.** Range +0.022 to +0.044 across 6 configs (4 Phase 1A + 3 Phase 1B − overlap). Cross-sectional momentum on QQQ universe is the binding mechanism.
- vs Phase 1A best: subGDE 10% improves lh_56y (+0.044, 1.117→1.161) but loses cosmetic vt_real edge and ndx_real (+0.032→+0.022). subKMLM 10% pushes ndx_real to new high (+0.044) but at lh_56y cost.
- **Phase 2 implication**: SPMO at 5-10% remains the strongest single Phase 1 finding. F2 US Factor-only / F3 US Hybrid both should include SPMO. subGDE preferred for lh_56y preservation; subKMLM for ndx_real maximization. Phase 1A's `spmo_lite` (5% balanced) is the highest 2/3-dataset blend.

### 035 — 2026-04-29 — AVDV-realloc (STRONG NEW 84 — Phase 1B sub-source variation, KILL #1 reaffirmed)

- **Phase 1B sub-source variation iter 3/6.** Hypothesis: Phase 1A iter 029 AVDV (intl SCV) failure (BOTH KILLs fired, Δ −0.108 / −0.019 / −0.012) used balanced 50/50 substitution. Retests at fixed 10% under 3 sub sources. Citation `[ilmanen_expected_returns, ch.19]`.
- Synth: AVDVSIM = `VSSSIM + 100bps/y tilt premium`. INCOMPLETE.
- Selected `avdv10_subGDE` (10% AVDV, sub from GDE). Gross Sharpe **1.111 / 0.957 / 1.092**. Score 84/100 STRONG.
- vs iter 023 substantively: **−0.078 / −0.047 / −0.043** — loses on **3/3 datasets**.
- **Substitution source comparison (10% AVDV, fixed weight)**:
  - `subGDE` (selected): 1.1113 / 0.9569 / 1.0920 → Δ −0.078 / −0.047 / −0.043
  - `subNTSX`:           1.0872 / 0.9614 / 1.0855 → Δ −0.102 / −0.043 / −0.050
  - `subKMLM`:           1.0519 / 0.9532 / 1.1063 → Δ −0.137 / −0.051 / −0.029
  - **Best sub = GDE**; **worst = KMLM** (lh_56y −0.137).
- **KILL #1 (no-positive-config) ✅ REAFFIRMED**: 0/3 datasets beat iter 023 under any sub source. Same pattern as Phase 1A.
- vs Phase 1A best: subGDE 10% improves lh_56y (+0.030) but degrades vt_real (−0.028) and ndx_real (−0.031). Net no improvement.
- **AVDV sleeve closure REAFFIRMED.** All 3 Avantis factor sleeves (AVUV/AVDV/AVEM) confirmed subordinate under sub-source variation. F5 Global Factor-only finalist (iter 036 original sweep) cannot proceed.

### 034 — 2026-04-29 — AVUV-realloc (STRONG NEW 86 — Phase 1B sub-source variation, KILL #1 fires, lh_56y near-parity)

- **Phase 1B sub-source variation iter 2/6.** Hypothesis: Phase 1A iter 028 AVUV failure (KILL #2 fired, KILL #1 cosmetic 1/3 ndx_real +0.005) used balanced 50/50 substitution from NTSX+KMLM. Retests at fixed 10% AVUV under 3 sub sources. Citation `[risk_parity, ch.2, p.37-41]` Fama-French SCV.
- Synth: AVUVSIM = `VBRSIM + 75bps/y tilt premium`. INCOMPLETE.
- Selected `avuv10_subGDE` (10% AVUV, sub from GDE 25%→15%). Gross Sharpe **1.168 / 0.975 / 1.122**. Score 86/100 STRONG.
- vs iter 023 substantively: **−0.021 / −0.029 / −0.013** — loses on **3/3 datasets**.
- **Substitution source comparison (10% AVUV, fixed weight)**:
  - `subGDE` (selected): 1.1681 / 0.9753 / 1.1219 → Δ −0.021 / −0.029 / −0.013 *(lh_56y near-parity!)*
  - `subNTSX`:           1.1324 / 0.9841 / 1.1194 → Δ −0.057 / −0.020 / −0.016
  - `subKMLM`:           1.0832 / 0.9683 / 1.1327 → Δ −0.106 / −0.036 / −0.002
  - **Best sub = GDE** (cleanest lh_56y improvement of any Phase 1B iter); **worst = KMLM** (lh_56y −0.106).
- **KILL #1 (no-positive-config) ✅ FIRED**: 0/3 datasets beat iter 023 under any sub source. Phase 1A's cosmetic ndx_real +0.005 edge is lost at 10% weight under any sub source.
- vs Phase 1A best: `subGDE` 10% improves lh_56y substantially (+0.052) but loses Phase 1A's cosmetic ndx_real edge (−0.018) and degrades vt_real (−0.021). Net no improvement on the +signal criterion.
- **AVUV sleeve subordinate to iter 023 reaffirmed.** subGDE's near-parity lh_56y (1.168 vs 1.189) is the cleanest sub-source improvement in Phase 1B but does not cross the +signal threshold. AVUV at 5% in F3 Hybrid (Phase 2 iter 034 original sweep) remains plausible per Phase 1A cosmetic edge; Phase 1B does **not** elevate AVUV to winner candidate.

### 033 — 2026-04-29 — NTSD-realloc (STRONG NEW 81 — Phase 1B sub-source variation, KILL #1 reaffirmed)

- **Phase 1B sub-source variation iter 1/6.** Hypothesis: Phase 1A iter 027 NTSD failure (KILL #1+#2 fired, Δ vs iter 023 −0.097 / −0.024 / −0.010) used balanced 50/50 substitution from NTSX+KMLM. Phase 1B retests at fixed 10% NTSD weight under 3 alternative sub sources: NTSX-only, GDE-only, KMLM-only. Citation `[risk_parity, ch.5, p.10]` + WisdomTree NTSD prospectus 2026-03-19. KILL #3 N/A (NTSDSIM is literal blueprint).
- Synth: NTSDSIM = `0.90 SPYSIM + 0.60 VEASIM − 75bps/y`. INCOMPLETE — active management unmodeled.
- Selected `ntsd10_subGDE` (10% NTSD, sub from GDE 25%→15%). Gross Sharpe **1.101 / 0.946 / 1.109**. NEW: 2/3 +0.05 vs SPY (vt_real 0.946 misses by 0.004). Score 81/100 STRONG (winner_conds=True per gates+DSR; vt_real Sharpe just below the +0.05 hurdle but cross-dataset thresholds clear).
- vs iter 023 substantively: **−0.088 / −0.058 / −0.026** — loses on **3/3 datasets**.
- **Substitution source comparison (10% NTSD, fixed weight)**:
  - `subGDE` (selected): 1.1008 / 0.9461 / 1.1089 → Δ −0.088 / −0.058 / −0.026
  - `subNTSX`:           1.0716 / 0.9562 / 1.1077 → Δ −0.117 / −0.048 / −0.027
  - `subKMLM`:           1.0225 / 0.9369 / 1.1149 → Δ −0.166 / −0.067 / −0.020
  - **Best sub = GDE** (cuts equity carry); **worst sub = KMLM** (cuts crisis-alpha; lh_56y −0.166).
- **KILL #1 (no-positive-config) ✅ REAFFIRMED**: 0/3 datasets beat iter 023 under any sub source (criterion ≥1/3). Phase 1A failure was **not** a sub-source artifact — structural sleeve subordination.
- vs Phase 1A best: subGDE 10% improves lh_56y (+0.009) but degrades vt_real (−0.034) and ndx_real (−0.016). Net no improvement.
- **NTSD sleeve closure REAFFIRMED.** F4 Global Stacking finalist (iter 035) confirmed not viable via NTSD-stacking alone.

### 032 — 2026-04-29 — AVEM-add (WINNER NEW 90 — BOTH KILLs fired, sleeve CLOSED, 32y window)

- Phase 1 single-axis isolation iter 6/6 (LAST). Hypothesis: Avantis EM Equity factor-tilted at 1x notional adds Sharpe via low-correlation diversification to iter 023's developed-market stack. 4 configs sweep AVEM 5/10/15/20%. Citation `[ilmanen_expected_returns, ch.19]` intl + EM diversification.
- Synth: AVEMSIM = `VWOSIM + 125bps/y tilt premium`. INCOMPLETE — VWOSIM passive, 125bps highest of AV* family.
- **WINDOW CAVEAT (CRITICAL)**: VWOSIM starts 1994-05-04 → effective lh_56y window = **32y (1994-2026)**, NOT 56y. Verified at runtime: 8042 daily obs vs iter 023's full 56y. vt_real (2008+) and ndx_real (2010+) windows unaffected (apples-to-apples).
- Selected `avem_lite` (5% AVEM). Gross Sharpe **1.082 / 0.969 / 1.115**. Score 90/100 WINNER NEW (iter 023 base still beats SPY).
- vs iter 023 substantively: **−0.107 / −0.035 / −0.020** — loses on **3/3 datasets**.
- **KILL #1 (no-positive-config) ✅ FIRED**: 0/3 datasets beat iter 023 (criterion ≥1/3). lh_56y caveat: 32y window 1994-2026 was a US-large-cap regime ~3-4pp/yr CAGR ahead of EM, so window is biased against EM-tilted portfolios — but vt_real and ndx_real losses are on identical windows to iter 023.
- **KILL #2 (monotonic regression) ✅ FIRED**: Sharpe falls monotonically with AVEM weight 5%→20% on ALL 3 datasets (Δ −0.107 / −0.133 / −0.110). Steepest decline of all 6 Phase 1 sleeves.
- **AVEM sleeve CLOSED.** Combined with iter 029 AVDV closure: **all 3 Avantis factor sleeves (AVUV/AVDV/AVEM) failed.** F5 Global Factor-only (iter 036) cannot proceed with non-momentum factors — only SPMO remains positive. **F5 should be skipped or rebuilt as SPMO-only.** F6 Global Hybrid (iter 037) likely degenerates to "iter 023 + 5-15% SPMO" ≈ F3 US Hybrid.

### 031 — 2026-04-29 — IDMO-synth (WINNER NEW 90 — KILL #2 fired, KILL #1 cosmetic, sleeve subordinate to SPMO)

- Phase 1 single-axis isolation iter 5/6. Hypothesis: intl mirror of SPMO (Invesco S&P Intl Developed Momentum). Tests intl cross-sectional momentum factor; per Jegadeesh-Titman 1993 + Asness-Moskowitz-Pedersen 2013, intl momentum has ~0.5-0.7 correlation with US momentum (lower than passive intl-equity). 4 configs sweep IDMO 5/10/15/20%. Citation `[ilmanen_expected_returns, ch.19]` + `[stocks_on_the_move, p.21-30]`.
- Synth: IDMOSIM = `VEASIM + 0.60 × UMD_KF − 60bps/y`. INCOMPLETE — uses **US UMD_KF** as proxy for intl momentum factor (biggest caveat); 60bps reflects IDMO's higher TER vs SPMO; may overstate edge by 10-30% per AMP 2013 correlation.
- **KILL #3 (no-free-lunch) ✅ PASS**: standalone Sharpe = **0.726** (< 1.5). Matches real IDMO live 0.5-0.7 since 2017.
- Selected `idmo_lite` (5% IDMO). Gross Sharpe **1.107 / 0.984 / 1.140**. NEW: 3/3 +0.05 vs SPY ✓ (winner_conds=True). Score 90/100 WINNER.
- vs iter 023 substantively: **−0.082 / −0.020 / +0.005** — beats iter 023 on **1/3 datasets** (ndx_real +0.005 cosmetic).
- **KILL #1 (no-positive-config) survives narrowly**: 1/3 datasets beat iter 023 (cosmetic, criterion ≥1/3).
- **KILL #2 (monotonic regression) ✅ FIRED**: Sharpe falls monotonically with IDMO weight 5%→20% on ALL 3 datasets (Δ −0.069 / −0.105 / −0.066).
- **IDMO subordinate to SPMO** at every weight: SPMO ndx_real +0.032 substantive vs IDMO ndx_real +0.005 cosmetic. SPMO non-monotonic (peak at 15%) vs IDMO strictly monotonic-falling. **NOT recommended for Phase 2.** F5/F6 finalists lose another sleeve; only AVEM remains for Global side.

### 030 — 2026-04-29 — SPMO-synth (STRONG NEW 84 — FIRST POSITIVE Phase 1 SLEEVE)

- Phase 1 single-axis isolation iter 4/6. Hypothesis: capture iter 016's UMD-academic +signal in deployable form via SPMO synth (S&P momentum ETF; embeds SPY beta + cross-sectional momentum overlay). Per Frazzini-Israel-Moskowitz 2018, real momentum ETFs capture ~60-70% of UMD long-short premium. 4 configs sweep SPMO 5/10/15/20%. Citation `[stocks_on_the_move, p.21-30]` + Jegadeesh-Titman 1993.
- Synth: SPMOSIM = `SPYSIM + 0.60 × UMD_KF − 35bps/y`. INCOMPLETE — 0.60 capture coefficient is FIM 2018 estimate; real SPMO live Sharpe 0.7-0.9 since 2015 inception.
- **KILL #3 (no-free-lunch synth) ✅ PASS**: SPMO standalone Sharpe = **0.828** (well below 1.5 threshold). Matches real SPMO live Sharpe — synth honest.
- Selected `spmo_lite` (5% SPMO). Gross Sharpe **1.117 / 1.009 / 1.167**. NEW: 3/3 +0.05 vs SPY ✓ (winner_conds=True). Score 84/100 STRONG.
- vs iter 023 substantively: **−0.072 / +0.005 / +0.032** — beats iter 023 on **2/3 datasets** (vt_real cosmetic, ndx_real substantive +0.032). lh_56y drag from KMLM-FFmom splice 1986-1988 (KMLM heavy iter 023 has FF-MoM Sharpe ~1.9 splice vs SPMO synth's UMD Sharpe).
- **KILL #1 (no-positive-config) SURVIVES**: 2/3 datasets beat iter 023 (criterion ≥1/3).
- **KILL #2 (monotonic regression) DOES NOT FIRE**: ndx_real Sharpe **non-monotonic** with weight (lite=1.167, mod=1.175, med=1.179, heavy=1.177 — peak at 15%). Criterion required all 3 datasets monotonic falling — vt_real and lh_56y fall, but ndx_real does not.
- **FIRST positive sleeve in Phase 1.** Recommended for Phase 2 inclusion at 5-15% weight in F2 (iter 033), F3 (iter 034), F6 (iter 037). Confirms iter 016 UMD edge survives in deployable form (~40% capture vs iter 016's pure UMD academic edge).

### 029 — 2026-04-29 — AVDV-add (STRONG NEW 88 — BOTH KILLs fired, sleeve CLOSED)

- Phase 1 single-axis isolation iter 3/6. Hypothesis: intl mirror of AVUV (Avantis Intl Small-Cap Value); user-cited 2025 ~40% return suggests intl SCV regime cycle inverted vs US 2025. Tests factor + geographic combined axis. 4 configs sweep AVDV 5/10/15/20%; NTSX+KMLM each absorb the cut. Citation `[ilmanen_expected_returns, ch.19]` intl factor diversification.
- Synth: AVDVSIM = `VSSSIM + 100bps/y tilt premium`. INCOMPLETE — VSSSIM is passive intl small-cap, no quality screen.
- Selected `avdv_lite` (5% AVDV). Gross Sharpe **1.081 / 0.985 / 1.123**. Score 88/100 STRONG NEW.
- vs iter 023 substantively: **−0.108 / −0.019 / −0.012** — loses on **3/3 datasets**. Worse than AVUV (iter 028) on long-history.
- **KILL #1 (no-positive-config) ✅ FIRED**: best config beats iter 023 on **0/3** datasets (criterion: ≥1/3). Hard fire.
- **KILL #2 (monotonic regression) ✅ FIRED**: Sharpe falls monotonically with AVDV weight on ALL 3 datasets (Δ lh_56y −0.035, vt_real −0.078, ndx_real −0.076).
- **AVDV sleeve CLOSED.** F5 Global Factor-only (iter 036) probability reduced significantly — both AVUV and AVDV failed. F6 Global Hybrid (iter 037) also weakened. User's 2025 +40% AVDV is single-year regime artifact; lh_56y window says intl SCV at 1× cannot beat iter 023 levered stack at any weight.

### 028 — 2026-04-29 — AVUV-add (STRONG NEW 88 — KILL #2 fired, KILL #1 cosmetic 1/3)

- Phase 1 single-axis isolation iter 2/6. Hypothesis: Avantis US small-cap value factor (size+value+profitability) at 1x notional outside the wrapper recovers what iter 013's VBRSIM tilt couldn't (post-2008 "death of value" regime). 4 configs sweep AVUV 5/10/15/20%; NTSX+KMLM each absorb the cut. Citation `[risk_parity, ch.2, p.37-41]` Fama-French SCV.
- Synth: AVUVSIM = `VBRSIM + 75bps/y tilt premium`. INCOMPLETE — VBRSIM is passive (no quality screen), 75bps tilt is estimate.
- Selected `avuv_lite` (5% AVUV). Gross Sharpe **1.115 / 0.996 / 1.140**. NEW: 3/3 +0.05 vs SPY ✓ (winner_conds=True). Score 88/100.
- vs iter 023 substantively: **−0.074 / −0.008 / +0.005** — beats iter 023 on **1/3** datasets (ndx_real +0.005 cosmetic).
- **KILL #1 (no-positive-config) survives** — barely (criterion: ≥1/3 datasets; 1/3 passes but the edge is below noise).
- **KILL #2 (monotonic regression) ✅ FIRED**: Sharpe falls monotonically with AVUV weight 5%→20% on ALL 3 datasets (Δ lh_56y −0.026, vt_real −0.059, ndx_real −0.042). Same structural pattern as iter 013 VBRSIM tilt.
- **Decision**: sleeve **marginal/closed substantively**. AVUV at 5% may still be relevant for Phase 2 F3 Hybrid (iter 034) given +0.005 ndx_real edge survives KILL #1, but does not beat iter 023 on 2/3 datasets. F2 US Factor-only (iter 033) probability reduced to ~25% — 1× factor stack unlikely to beat 1.5×-leveraged iter 023. Confirms iter 013's findings: small-cap value factor at 2010-2024 underperformance regime is absorbed by KMLM crisis-alpha.

### 027 — 2026-04-29 — NTSD-swap (WINNER NEW 90 — but BOTH KILLs fired, sleeve CLOSED)

- **Phase 1 / sweep iter 027-039 first execution.** Hypothesis: NTSD adds intl-developed equity stacked inside a 1.5x levered wrapper (90% SPY + 60% VEA futures); tests whether intl equity inside the wrapper recovers iter 014/015's failed external overlays. 4 configs sweep NTSD 5/10/15/20%, NTSX absorbs the cut. Citation `[risk_parity, ch.5, p.10]` + WisdomTree NTSD prospectus 2026-03-19.
- Synth: NTSDSIM = `0.90 SPYSIM + 0.60 VEASIM − 75bps/y`. INCOMPLETE — active management unmodeled.
- Selected `ntsd_lite_2055` (5% NTSD). Gross Sharpe **1.092 / 0.980 / 1.125**. NEW: 3/3 +0.05 vs SPY ✓ (winner_conds=True). LEGACY: 95/100 WINNER. Score 90/100 NEW reflects iter 023 base quality, NOT NTSD contribution.
- vs iter 023 substantively: **−0.097 / −0.024 / −0.010** — loses on **3/3 datasets**. Mean Sharpe 1.066 < iter 023 mean 1.109.
- **KILL #1 (no-positive-config) ✅ FIRED**: best config beats iter 023 on **0/3** datasets (criterion: ≥1/3). Hard fire.
- **KILL #2 (monotonic regression) ✅ FIRED**: Sharpe falls monotonically with NTSD weight 5%→20% on ALL 3 datasets (Δ lh_56y −0.067, vt_real −0.075, ndx_real −0.056). Same structural pattern as iter 014 VXUSSIM.
- **NTSD sleeve CLOSED.** F4 Global Stacking finalist (iter 035) cannot proceed — per SWEEP_PLAN §"Phase 2 fallback rules" recommend skip iter 035, F4 = "global stacking not viable" (consistent with iter 014/015 closures). NTSD adds intl beta but synth shows no Sharpe edge on lh_56y; intl-equity diversification is regime-dependent and lh_56y window rewards US large-cap.

### 026 — 2026-04-29 — iter011-MTUM-real (DATA-LIMITED DEAD-END)

- **Status: `data_limited`** — backtest never run.
- Plan: test investable momentum (MTUM/SPMO/IDMO live) as deployable substitute for iter 016 UMD academic. 4 configs sweep MTUM 10-25% on iter 011 base.
- Pre-run inventory: MTUM/SPMO/IDMO ❌ Tiingo cache; ❌ testfolio synth; Tiingo subscription cancelled (TIINGO_API_KEY empty). Tiingo bulk script (32 ETFs) has zero factor ETFs. Testfolio cache has zero MTUMSIM.
- B.5 momentum direction is **paused, not closed** — iter 016 UMD academic edge (+0.088 lh_56y strict / −0.016 vt_real / +0.047 ndx_real) stays the standing reference. Per [Frazzini-Israel-Moskowitz 2018], MTUM real would capture ~60% of UMD edge → estimated +0.05 lh_56y deployable edge.
- **DE-026** logged as DATA-LIMITED dead-end (similar to iter 021 sector rotation 4-asset). Reactivation requires Tiingo subscription resumption or MTUMSIM testfolio synth construction.
- No verdict.json — build_zoo_plot.py skips iters without verdict; this entry is documentation-only.

### 025 — 2026-04-29 — iter011-VXX-real-diagnostic (STRONG NEW 83 / WINNER LEGACY 93, DE-025)

- Hypothesis: substitute iter 022's synthetic tail-hedge with REAL VXX (Tiingo, 2009-01-30+). 4 configs sweep 2.5/5/7.5/10% VXX substituting from KMLM. **Methodological diagnostic** — quantifies gap between synthetic +5pp Sharpe artifact (iter 022) and deployable reality.
- Pre-run no-free-lunch sanity check ✅ PASS: VXX standalone Sharpe **−0.738**, CAGR **−51%/yr**, MDD **−100%** (legitimate destroyer of capital).
- Selected `vxx_lite_3525_375_25` (2.5% VXX, least bad). Gross Sharpe **1.107 / 0.921 / 1.097**. NEW: 2/3 +0.05 vs SPY (vt_real misses by 0.029). LEGACY: 3/3 +0.10 vs avg(SPY,VT) (avg vt_real 0.707 baseline easier).
- vs iter 011 substantively: **+0.061 / −0.039 / −0.007** (loose). LOSES vt_real and ndx_real.
- **KILL #1 (no-free-lunch monotonic) ✅ PASS**: Sharpe decreases monotonically as VXX% rises 2.5%→10% in ALL 3 datasets (lh_56y −0.125, vt_real −0.280, ndx_real −0.243). Decay structurally beats tail-hedge benefit at every weight.
- Gap iter 022 synthetic vs iter 025 real (10% VXX): lh_56y 1.520 → 0.982 (Δ −0.538), vt_real 1.710 → 0.641 (Δ −1.069), ndx_real 1.684 → 0.854 (Δ −0.830). Synthetic model overstated Sharpe by 0.5-1.1 points across datasets — confirms iter 022 score 100/100 was 100% model failure.
- Direction B.3 (continuous tail-hedge with VXX) closed. Spitznagel's Universa real-implementation +1-2pp CAGR uplift requires OTM puts + short-vol overlay, not just buying VXX. **DE-025 written**.

### 024 — 2026-04-29 — iter011-MDD-trigger-defensive (STRONG NEW 82 / STRONG LEGACY 87, DE-024)

- Hypothesis: regime-conditional defensive shift — when SPY 21d return < threshold (drawdown signal), reduce 50% NTSX, add 17.5% TLT or CASH. 3 configs (≤3 to limit DSR penalty per [advances_fin_ml, p.222]): mdd_trigger_10pct_TLT, _15pct_TLT, _15pct_CASH. Forward-looking signal (.shift(1) — no peek).
- Selected `mdd_trigger_10pct_TLT`. Gross Sharpe **1.145 / 0.982 / 1.123**. NEW: 3/3 +0.05 vs SPY ✓. winner_conds=True.
- vs iter 011 substantively: **+0.099 / +0.022 / +0.019** loose (3/3 positive but lh_56y just shy of +0.10 hurdle). Strict: +0.017 / +0.019 / +0.016.
- Trigger pct_on **= 1-2%** — defensive almost never activates. Strategy is iter 011 base 99% of trading days + brief defensive shifts during 2008/2020/2022 crisis windows. Concentrated tail-risk reduction in <1% of days, recovers <1% of static-TLT-benefit.
- **Dominated by iter 023 TLT-static** in every dataset (1.189 vs 1.145, 1.004 vs 0.982, 1.135 vs 1.123). TLT continuously > TLT episodically.
- Cross-config: 3 configs cluster within 0.01 mean Sharpe. PBO N=3 warning (CSCV unstable below N=4).
- Lesson: **rare-event regime trigger fires too rarely to drive significant alpha** in long-history portfolio mandate. Closing Direction B.2. **DE-024 written**.

### 023 — 2026-04-29 — iter011-plus-TLT-sleeve (STRONG NEW 86 / WINNER LEGACY 91 — first multi-dataset substantive +signal under NEW)

- **First iter under NEW SPY-only mandate** (post-reframing 2026-04-29).
- Hypothesis: extract iter 020's sub-finding (`aw_levered_NTSX_GDE_TLT` was the only loop config to beat iter 011 ndx_real 1.120 vs 1.104). Test isolated TLT 15-30% sleeve on iter 011 base substituting from NTSX/KMLM. 4 configs.
- Selected **`tlt_mod_25_25_35_15`** (15% TLTSIM, 25/25/35/15 NTSX/GDE/KMLM/TLT). Gross Sharpe **1.189 / 1.004 / 1.135**. NEW: 3/3 +0.05 vs SPY ✓ (+0.509/+0.104/+0.235). winner_conds=True. LEGACY: WINNER 91/100 (3/3 +0.10 vs avg, all 5 LEGACY conds met).
- vs iter 011 substantively: **+0.143 / +0.044 / +0.031** loose, +0.061 / +0.042 / +0.029 strict — **+signal across all 3 datasets**, first since iter 011 itself.
- **MDD better than iter 011 across all 3 datasets**: lh_56y 21.13% vs 26.04% (−4.9pp), vt_real 17.40% vs 21.22% (−3.8pp), ndx_real 11.76% vs 14.12% (−2.4pp).
- Cross-config: TLT 15% optimal; 30% degrades. 4 configs cluster within 0.02 mean Sharpe (robust selection). KMLM-heavy (35%) preserves crisis-alpha; over-substituting KMLM costs Sharpe.
- Score 86 < 90 (NEW) STRONG due to: c2 gates 21/25 (PBO partial vt_real 0.572 + ndx_real 0.580), c4 CAGR 5/15 (warning-only — vt_real 10.13% and ndx_real 10.62% < SPY 0.8×14.97% = 11.98%). winner_conds=True (4 active conds met).
- **Mandate §7 override candidate**: yes (LEGACY winner; NEW STRONG with winner_conds=True; substantive Sharpe AND MDD edge vs iter 011). Trade-off: CAGR drag 0.8-1.0pp on live windows. Production deployable: NTSX/GDE/KMLM/TLT all live ETFs.
- Direction B.1 (TLT diversifier) confirmed positive. **iter 023 is the strongest non-iter-011 candidate in the loop.**

### 022 — 2026-04-29 — C5-tail-hedge ⚠️ MODEL-ARTIFACT WINNER (DO NOT USE)

- **🚨 Score 100/100, Sharpe 1.520 / 1.710 / 1.684 — but this is SYNTHETIC-MODEL ARTIFACT, NOT a deployable winner.**
- Hypothesis: synthetic convex tail hedge (when SPY 21d return < −5%, hedge_r = 2.0 × abs(spy_daily_neg); else −0.04%/day premium decay). Added at 5/7.5/10/15% to iter 011 base, substituted from KMLM.
- Selected `tail_15pct`. Edge vs avg(SPY,VT) +0.85/+1.00/+0.76, MDD 17.86/9.54/7.33%. ALL gates pass 7/7×3. DSR p ~0. Tier WINNER 100/100.
- **The 100/100 score IS THE PROOF OF MODEL FAILURE** — no real long-term portfolio strategy clears every gate at every threshold. Hedge model bias sources: (1) no vega cost (real puts cost more in vol spikes); (2) hindsight via 21d trigger (model sees drawdown before paying); (3) wrong path-dependence (real puts pay strike-spot at expiry, not 2× daily compounded); (4) no spread/liquidity drag (real ATM puts ~6%/yr premium realistic).
- **Honest interpretation**: realistic edge ~+0.05 to +0.15 Sharpe (net of true premium), not +0.85. Monotonic improvement with hedge weight (5%→15%) is itself a red flag — real options have non-linear premium acceleration.
- **DE-022 logged as METHODOLOGICAL DEAD-END not strategy dead-end**: cannot conclude tail-hedging is good or bad in this universe; only that this synthetic model is invalid.
- Cannot count as substantive winner. **Substantive incumbent remains iter 011** (Sharpe 1.046/0.960/1.104). Mechanical incumbent remains iter 014 (Sharpe 1.055/0.885/1.052) per loop rule. iter 016 UMD overlay (Sharpe 1.223/0.943/1.150) is the only positive substantive signal in fila 016-022.
- Lesson for future iters: when adding a synthetic asset whose returns are MODELED (not measured), add no-free-lunch sanity checks (e.g., assert hedge Sharpe < benchmark Sharpe alone, or assert worsening as weight rises beyond optimal). A proper deployable test would require actual SPY put options data (Tiingo doesn't have) or VXX/VIXY proxy with realistic decay.

### 021 — 2026-04-29 — C4-sector-rotation (PROMISING 69/100, NOT WINNER, KILL #1, DE-021 — DATA-LIMITED)

- Hypothesis: sector rotation top-K monthly by 6m momentum. Universe restricted to 4 SPDR sectors (XLE/XLF/XLK/XLU) — the only ones with full Tiingo 2003-08+ history; 5 other sectors (XLB/XLI/XLP/XLV/XLY) start 2014-01 only. 4 configs: K=1,2,3 × fallback TLT or KMLM.
- Selected `sec4_K2_TLT`. Gross Sharpe 0.708 / 0.762 / 0.788 — Sharpe edges fail 3/3 (max +0.056 vs avg(SPY,VT)). MDD 34-43% (worst of any iter). vs iter 011: −0.34 / −0.20 / −0.32. Tier PROMISING 69/100.
- KILL #1 fires hard.
- Lesson: 4-sector universe is too narrow — XLE/XLF/XLK/XLU all share strong equity beta during crises (2008, 2020), so rotation can't escape drawdown. Test is **inconclusive but biased toward fail** (data-limited). Full 9-sector test would require Yahoo Finance backfill to 1998 SPDR inception (~1-2h infra, deferred). DE-021 logged with caveat.

### 020 — 2026-04-28 — C3-all-weather (STRONG 83/100, NOT WINNER, defensive CAGR drag)

- Hypothesis: 4 All-Weather variants — textbook 30/40/15/15 (gold sub for commodities since DBC unavailable), Browne permanent 25/25/25/25, levered (40 NTSX + 30 GDE + 15 KMLM + 15 TLT), inv-vol risk parity 4-asset.
- Selected `aw_browne_25252525`. Gross Sharpe **1.114 / 0.984 / 1.097** with edges +0.442/+0.277/+0.173 vs avg(SPY,VT) — **excellent MDD 17.15% across all** (cleanest of any iter), but CAGR 6.6-7.65% fails floor 3/3. Score 83, tier STRONG, **winner_conditions_met=FALSE**.
- vs iter 011: lh_56y +0.068, vt_real +0.024, ndx_real −0.007 — modest positives but no advance.
- Notable highlights: `aw_inv_vol_4asset` lh_56y **1.143** (highest non-UMD Sharpe in loop). `aw_levered_NTSX_GDE_TLT` ndx_real **1.120** — only iter to beat iter 011's 1.104 (modest +0.016 win).
- Lesson: All-Weather family is defensive by design — Sharpe excellent but CAGR cap'd 6-8%. Same failure mode as iter 019: doesn't fit CAGR-target mandate. Useful risk-parity perspective for future "iter 011 + TLT sleeve" extension if pursued.

### 019 — 2026-04-28 — C2-vol-managed-60-40 (STRONG 81/100, NOT WINNER, KILL #1 narrowly avoided)

- Hypothesis: vol-targeting on 60/40 cap-efficient base (60% NTSX + 40% IEF) — weight = clamp(target_vol / realized_60d_vol, [0.5, 2.0]). 4 configs: target_vol 8/10/12/15%.
- Selected `vt_8pct`. Gross Sharpe 0.991 / 1.052 / 1.117 — Sharpe edge vs avg(SPY,VT) clears 3/3 (+0.32/+0.35/+0.19), BUT **CAGR floor fails 3/3** (8.13% / 9.32% / 9.71% < 0.8 × bench). Score 81/100, tier STRONG, **winner_conditions_met=FALSE**.
- vs iter 011: lh_56y −0.055 / vt_real **+0.092** (close to +0.10 hurdle) / ndx_real +0.013. Modest Sharpe gain on vt_real, CAGR ~3pp lower across the board.
- Lesson: classic Carver tradeoff — vol-targeting removes left-tail variance but also caps right-tail upside, so CAGR drops proportionally. Mechanism works as advertised but doesn't fit a CAGR-sensitive long-term portfolio mandate. Not competitive with capital-efficient stacks for this loop's mission.

### 018 — 2026-04-28 — C1-Antonacci-GEM (PROMISING 74/100, NOT WINNER, KILL #1, DE-018)

- Hypothesis: pivot to qualitatively different mechanism — Antonacci-style monthly top-K cross-class momentum across SPYSIM/QQQSIM/VEASIM/VWOSIM/TLTSIM/GLDSIM/KMLMSIM. 4 configs: 5/6/7-asset universe variants × K=2,3.
- Selected `gem_6asset_K2` (SPY/QQQ/VEA/TLT/GLD/KMLM, K=2, fallback KMLM). Gross Sharpe **0.763 / 0.888 / 0.889** — only vt_real clears +0.10 edge vs avg(SPY,VT). winner_conditions_met=FALSE. Score 74/100, tier PROMISING.
- vs iter 011: **lh_56y −0.283, vt_real −0.072, ndx_real −0.215** — massive regression on long-history and ndx_real.
- KILL #1 fires. Closes C.1 in this universe.
- Lesson: cross-class top-K monthly momentum doesn't beat static cap-efficient stack iter 011 in testfolio universe + lh_56y window. Three reasons: (1) equity-dominant regimes punish switching (2010-2024 was 14y US-equity dominance, monthly switching adds whipsaw + DARF cost); (2) long-history exposes weakness vs iter 011's static stack with KMLM crisis-alpha; (3) vt_real-only positive (17y window has GFC + 2020 + 2022 — three regime shifts where switching helps, but too narrow to generalize). Contrast iter 079 archive (Sharpe 1.094 strict winner) — different universe (more equity diversifiers), shorter window (Tiingo SPY 17y only), different lookback. **DE-018 written**.

### 017 — 2026-04-28 — B6-VBRSIM-regime-gated (STRONG 82/100, KILL #1 fired, DE-017)

- Hypothesis: test whether binary regime gate (VBRSIM weight = 25% when signal ON, 0% when OFF, KMLM absorbs slack) recovers iter 013's lh_56y advantage without the live-window cost. 3 pre-committed configs (≤3 to limit DSR penalty): mom12 (12-1m return > 0), value (36m Sharpe > 0.5), dual (mom12 OR value).
- Citations: `[advances_fin_ml, p.208-211, p.222-223]` PBO/DSR discipline; `[stocks_on_the_move, p.21-30]` time-series momentum; `[risk_parity, ch.5, p.10]`.
- Selected: `vbrsim_value` (signal = 36m Sharpe > 0.5, pct_on avg 66%). Gross Sharpe **1.043 / 0.884 / 0.967** (loose), strict 0.970 / 0.886 / 0.969. Score **82/100, tier STRONG**. Δ vs iter 011 strict: −0.075 / −0.074 / −0.135. Δ vs iter 013 constant-weight: **−0.083 / −0.039 / −0.108** — regime gate makes things WORSE on every dataset.
- KILL #1 fired: best-of-grid loses iter 011 substantively on 3/3 strict AND fails to match iter 013's +0.080 lh_56y advantage (iter 017 is +0.003 vs iter 013's +0.080). KILL #2 not informative: PBO N=3 triggers framework warning (CSCV unstable below N=4).
- Lesson: regime-gating on a single existing-winner factor doesn't recover the dormant value premium. Three reasons: (1) signal lag (36m Sharpe / 12-1m return turn ON 6-12m late, missing early premium reset); (2) whipsaw cost (~5-15bp/yr in deploy via DARF on rebalances); (3) regime classification noise on ~30y data. Adding ~50bp of complexity costs −80bp of gross Sharpe lh_56y. **Family B-direction now CLOSED end-to-end**: B.4 (constant VBRSIM, iter 013), B.5 (UMD overlay, iter 016 — only positive), B.6 (regime-gated VBRSIM, iter 017). Only iter 016 has a substantive edge in B-family. **DE-017 written**.

### 016 — 2026-04-28 — B5-UMD-overlay (WINNER tier 91/100, FIRST POSITIVE SIGNAL since iter 011 — beats iter 011 on 2/3 datasets)

- Hypothesis: pivot from size+value/geographic axes to **structurally distinct factor**: UMD (Up Minus Down, Fama-French academic momentum, 1926+, daily UMD+RF via `ff_momentum_proxy`). UMD is cross-sectional equity momentum with positive 2017-2024 run when value lagged + convex crisis behavior (positive 2008, 2020). 4 configs UMD overlay 10/15/20/25% on iter 011 base (UMD substitutes from KMLM portion, preserves NTSX+GDE cap-efficient core).
- Citations: `[stocks_on_the_move, p.21-30]` Clenow + Jegadeesh-Titman 1993; `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking; `[risk_parity, ch.2, p.37-41]` factor framework; gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 4 pre-committed configs; selected `umd_heavy_3025_20_25` (30% NTSX + 25% GDE + 20% KMLM + 25% UMD). Datasets: lh_56y / vt_real / ndx_real.
- Result: gross Sharpe **1.223 / 0.943 / 1.150** (loose) — edges vs avg(SPY,VT) **+0.551 / +0.237 / +0.227** — 3/3 datasets clear +0.10. Strict: **1.133 / 0.944 / 1.151**. Gates **7/7 / 6/7 / 6/7** (live windows G1 PBO fail 0.55-0.57, same family-selection mode as iter 011). DSR p **1.78e-15 / 1.78e-3 / 2.25e-4**. Tier WINNER, score 91/100. **beats_incumbent=false** mechanically (score 91 < 93, edge ≥+0.10 vs iter 014 only on 1/3 datasets — fails ≥2/3).
- **vs iter 011 substantive**: **+0.177 / −0.017 / +0.046 loose**; **+0.088 / −0.016 / +0.047 strict**. Wins 2/3 substantively, loses ~0.02 on vt_real. Strict edge on lh_56y +0.088 narrowly misses +0.10 hurdle. **First iter since iter 011 to be substantively positive across multiple datasets**.
- Net (informational): Sharpe ≈ gross (static stack tax-perfect).
- Score breakdown: Sharpe edge 25/25; gates 21/25 (lh_56y 7/7, vt 6/7, ndx 6/7); DSR 15/15; CAGR floor 10/15 (ndx_real 11.77% < 13.59%); MDD ceiling 15/15; robustness 5/5.
- **No KILL fires**: lh_56y G3 WF passes (max win MDD 22.09% < 25%) — first iter to clear that gate. UMD's positive 2008/2020 helps cap window MDDs.
- **Cross-config pattern (NEW)**: lh_56y monotonic UPWARD with UMD weight (1.161→1.223 over 10%→25%), vt_real gentle decline (−0.027 range, all >0.94), ndx_real flat. **First iter where live windows DON'T monotonically regress** as new factor weight rises.
- Lesson: UMD is structurally distinct from VBRSIM/VXUSSIM (higher raw Sharpe 0.75 vs ~0.5; positive 2017-2024 run; convex crisis behavior). Factor diversification works when factor is qualitatively orthogonal, not just labeled "different". **Caveat**: UMD is academic (long-short gross-of-cost); investable proxies (MTUM/SPMO/IDMO) capture ~60-70% of UMD due to long-only constraint + costs → real-world edge likely shrinks to ~+0.05 lh_56y, marginal but still positive. Next: iter 017 B.6 VBRSIM regime-gated (test whether regime-gating recovers value factor); deferred sub-iter to test investable momentum (MTUM live 2013+) for deploy-relevance.

### 015 — 2026-04-28 — A1-5asset-global-stack (WINNER tier, 93/100, TIES iter 014 — DIRECTION A CLOSED end-to-end)

- Hypothesis: build the literal user A.1 thesis — 5-asset global capital-efficient stack (NTSX + NTSI + NTSE + GDE + KMLM) — by **synthesizing NTSI/NTSE testfolio-style** for the first time. NTSI = 0.90 VEASIM + 0.60 IEFSIM − 0.50 CASHX (intl-developed 1.5× stack); NTSE = 0.90 VWOSIM + 0.60 IEFSIM − 0.50 CASHX (EM 1.5× stack). Same 90/60/−50 WisdomTree blueprint as NTSX (validated deploy_studies 2026-04-26). Geographic equity rebalance INSIDE the leveraged wrapper instead of sleeve-add OUTSIDE it (which 012/013/014 already proved subordinate). Grid mixes 4-asset (no NTSE, full lh_56y) with 5-asset (with NTSE, 1994+ eff via VWOSIM bottleneck) to isolate EM contribution.
- Citations: `[risk_parity, ch.5, p.10]` (Carlson cap-efficient stacking + WisdomTree NTSX/NTSI/NTSE prospectus 2024); `[ilmanen, ch.19]` (global equity diversification rationale); `[stocks_on_the_move, p.21-30]` (KMLM crisis-alpha retained); gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 4 pre-committed configs (`intl_dev_3025_GK_2025`, `intl_dev_lite_3515_GK_2030`, `global_lit_3015_10_GK_2520`, `global_em_heavy_2520_15_2020`); selected `intl_dev_lite_3515_GK_2030` (35% NTSX + 15% NTSI + 20% GDE + 30% KMLM, 4-asset variant) by max mean(gross_Sharpe / avg(SPY,VT)_Sharpe). Datasets: lh_56y / vt_real / ndx_real.
- Result: gross Sharpe **1.081 / 0.877 / 1.048** (edges vs avg(SPY,VT) **+0.410 / +0.171 / +0.124** — 3/3 datasets clear +0.10); gates **6/7 / 7/7 / 7/7**; DSR p **2.03e-12 / 4.00e-3 / 9.03e-4**. **All 5 strict winner conditions met → tier WINNER, score 93/100.** **TIES iter 014 (93=93, NOT >) → beats_incumbent=false** per rule. Sharpe-edge gate vs iter 014 fails 3/3 (Δ +0.026 / −0.008 / −0.004 — within noise on all). Sharpe-edge gate vs iter 011 (substantive incumbent) fails 3/3 substantively: lh_56y +0.035 LOOSE / **−0.038 STRICT**, vt_real **−0.083**, ndx_real **−0.056**.
- Net (informational): Sharpe **1.081 / 0.877 / 1.048** ≈ gross (static stack, year-end DARF, daily-Sharpe tax-neutral; same tax-perfect property as iter 011).
- Score breakdown: Sharpe edge 25/25; gates 23/25 (lh_56y G3 WF fails — one window MDD 28.0% > 25%); DSR 15/15 (cumulative_n_trials=56); CAGR floor 10/15 (ndx_real 11.57% < 13.59%); MDD ceiling 15/15; robustness 5/5 (52/52 rolling-5y windows positive, min 0.35 max 1.99).
- **PRE-COMMITTED KILLS FIRED**: KILL #2 (5-asset uniformly < 4-asset) **✅ FIRES** — best 5-asset (0.964/0.796/0.974) loses best 4-asset (1.081/0.877/1.048) on all 3 datasets (Δ −0.12 / −0.08 / −0.07). EM-as-component within 1.5× wrapper is structurally subordinate. KILL #3 (cross-config monotonic regression) **✅ FIRES** — intl-equity weight 15%→35% monotonically reduces Sharpe on ALL 3 datasets. KILL #1 PARTIAL — best-of-grid loses iter 011 on 2/3 deploy windows (3/3 strict).
- Lesson: **DIRECTION A NOW CLOSED END-TO-END** — both structural variants tested. Sleeve-add (012 RSSB / 013 VBRSIM / 014 VXUSSIM) AND component-swap (015 NTSI/NTSE) both subordinate to iter 011 on live windows. The 2010-2026 US-large-cap regime is so dominant that ANY deviation from pure US equity in the equity sleeve costs Sharpe — whether at 1× notional outside the wrapper or 1.5× notional inside it. **Iter 011 NTSX is the architectural ceiling for static cap-efficient stacks in this regime**. STRICT-window diagnostic added (011/012/013/014 loose convention silently inflates lh_56y Sharpe via partial-stack pre-bottleneck rows; selected strict 1.007 < loose 1.081). Next iter (016) MUST pivot: **B.6 regime-conditional factor** (highest priority — VBRSIM weight = f(value spread or factor momentum), pre-commit ≤3 configs) OR **C fundamentally different mechanism** (Antonacci GEM cross-class top-K, vol-managed 60/40) OR **stop hunting & declare iter 011 deploy-ready** (4 consecutive iters fail to advance — defensible). NEW INFRA: `proxies.py` module shared across iters (NTSX/NTSI/NTSE synth, parity-validated 2026-04-28).

### 014 — 2026-04-28 — intl-equity-tilt-on-iter011 (WINNER, 93/100, beats_incumbent=true mechanically — but iter 011 wins Sharpe on 2/3 live windows)

- Hypothesis: Inject `VXUSSIM` (Total International ex-US Stock Market, testfolio synth analog of Vanguard VXUS, 1× notional, zero Treasury) into iter 011's NTSX+GDE+KMLM stack at 4 weight intensities (10/20/25/30%). Tests Direction A.3 from BASE_MEMORY — the residual clean axis after iter 012 closed RSSB-style intl exposure (Treasury overlap, DE-013) and iter 013 closed US factor tilt (post-2008 "death of value", DE-014). VXUSSIM isolates pure intl-equity diversification, sidestepping both prior failure modes.
- Citations: `[risk_parity, ch.5, p.10]` (Carlson cap-efficient stacking, NTSX/GDE retained); `[ilmanen, ch.19]` (global equity diversification rationale); `[stocks_on_the_move, p.21-30]` (KMLM crisis-alpha retained); gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 4 pre-committed configs (`intl_lite_35253010`, `intl_moderate_30202525`, `intl_balanced_25252525`, `intl_heavy_25302025`); selected `intl_lite_35253010` (10% VXUSSIM) by max mean(gross_Sharpe / avg(SPY,VT)_Sharpe). Datasets: lh_56y / vt_real / ndx_real.
- Result: gross Sharpe **1.055 / 0.885 / 1.052** (edges vs avg(SPY,VT) **+0.384 / +0.178 / +0.129** — 3/3 datasets clear +0.10); gates **6/7 / 7/7 / 7/7**; DSR p **7.74e-12 / 3.66e-3 / 8.53e-4**. **All 5 strict winner conditions met → tier WINNER, score 93/100.** **Score 93 > iter 011's 91 → beats_incumbent mechanically true** per rule (score-OR clause). **BUT vs iter 011 substantively**: Sharpe Δ **+0.009 / −0.075 / −0.052** (LOSES on vt_real and ndx_real, ties on lh_56y). 0/3 datasets clear +0.10 vs iter 011. Score advance is partly benchmark-migration artifact (iter 011 scored on legacy `educational`). Per rule, iter 014 takes incumbent slot; report flags substantive caveat.
- Net (informational): Sharpe **1.055 / 0.885 / 1.052** ≈ gross (static stack, year-end DARF, daily-Sharpe tax-neutral).
- Score breakdown: Sharpe edge 25/25 (3/3 +0.10 vs avg); gates 23/25 (lh_56y G3 WF fails — one window MDD 29.5% > 25%); DSR 15/15; CAGR floor 10/15 (ndx_real 12.11% < 13.58% = 0.8 × bench); MDD ceiling 15/15; robustness 5/5 (52/52 rolling-5y windows positive, min 0.33 max 1.94).
- Lesson: VXUSSIM 10% → 30% Sharpe **MONOTONICALLY DECREASES on ALL 3 datasets** (including lh_56y where iter 013's factor tilt monotonically helped). Stronger structural signal than iter 013 — intl-equity tilt is even less compatible with iter 011's architecture than US factor tilt was. **3 sleeve-injection iters in a row (012/013/014) confirm: constant-weight sleeve injection on iter 011 is a CLOSED axis.** Closing direction A.3 → DE-015. Next iter must pivot: regime-conditional factor (B.6) OR replace-not-augment (A.1 NTSI/NTSE proxy synthesis required first) OR fundamentally different mechanism (Antonacci GEM, vol-managed 60/40 from archive).

### 013 — 2026-04-28 — factor-tilt-on-iter011 (WINNER tier, 91/100, DE-014)

- 4 configs VBRSIM (US small-cap value, 10/20/25/30%) on iter 011 base; selected `factor_lite_30253510` (10%). Gross S 1.126/0.923/1.075 — 5/5 strict conds vs avg(SPY,VT), but Sharpe vs iter 011 +0.080/−0.037/−0.029 (only beats lh_56y, score TIES at 91). `[risk_parity, ch.2, p.37-41]`
- Lesson: factor tilt monotonically helps lh_56y (+0.06→+0.085) but hurts vt/ndx (−0.04→−0.14) — post-2008 "death of value" regime. Closing constant-weight factor; needs regime filter.

### 012 — 2026-04-28 — ntsx-gde-rssb-kmlm-global-stack (STRONG, 88/100, DE-013)

- 4 configs RSSB injection on iter 011 base; selected `rssb_moderate_25252525`. Gross S 1.011/0.851/1.021 — all 5 strict winner conds met vs avg(SPY,VT) but LOSES iter 011 on all 3 datasets (−0.035/−0.109/−0.083). `[risk_parity, ch.5, p.10]`
- Lesson: RSSB's Treasury overlay duplicates NTSX's IEF; intl-equity sleeve dragged in post-2010 regime.

### 011 — 2026-04-28 — ntsx-gde-kmlm-static (🏆 WINNER, 91/100)

- 4 configs static NTSX/GDE/KMLM stack; selected `mf_tilted_352540` (35/25/40). Gross S 1.021/0.960/1.104 — 3/3 datasets +0.10 edge vs avg(SPY,VT). `[risk_parity, ch.5, p.10]`
- Lesson: capital-efficient stack (NTSX+GDE) + KMLM crisis-alpha is the only winner architecture across this loop and predecessor.

### 010 — 2026-04-28 — haa-vol-throttle (PROMISING, 60/100, DE-012)

- HAA+Gold with 63d vol throttle on 85% dyn sleeve. Sharpe 1.020/0.955/0.881; 7/7 × 3 but 0 datasets +0.10 vs iter009. `[systematic_trading, p.137-148]`
- Lesson: vol throttle reduces MDD but converts HAA into low-CAGR defensive.

### 009 — 2026-04-28 — haa-gayed-trend-canary (PROMISING, 73/100, DE-011)

- HAA+Gold with SPYSIM/VTSIM 10-mo trend canary modes; original VWOSIM re-selected. S 0.983/0.954/0.860. `[leverage_for_the_long_run, p.40-60]`
- Lesson: simple broad-equity trend not a better state classifier than VWO momentum.

### 008 — 2026-04-28 — haa-dual-canary (PROMISING, 73/100, DE-010)

- VWOSIM/VTISIM dual canary; vwo_only selected. S 0.983/0.954/0.860; ndx PBO 0.552 fails. `[stocks_on_the_move, p.63-65]`
- Lesson: second broad-equity canary did not improve state classification.

### 007 — 2026-04-28 — haa-defensive-kmlm-cash (STRONG, 75/100, DE-009)

- Swap HAA defensive variants; original IEF/BND/CASH re-selected. S 0.983/0.954/0.860; 7/7 × 3. `[stocks_on_the_move, ch.6]`
- Lesson: missing edge is canary timing, not defensive assets.

### 006 — 2026-04-28 — haa-rsit-synth (PROMISING, 71/100, DE-008)

- Synthetic RSIT_PROXY=VEASIM+KMLMSIM−50bps inside HAA. S 0.869/0.897/0.837; PBO 0.714/0.845 fails. `[risk_parity, ch.5]`
- Lesson: more embedded MF on intl-equity worsened Sharpe/PBO; defer until live RSIT.

### 005 — 2026-04-28 — haa-rsst-rssb-cta (PROMISING, 70/100, DE-007)

- RSST/RSSB/CTA offensive substitution in HAA. S 0.953/1.028/0.946; 7/7 × 3 but no +0.10 edge. `[risk_parity, ch.5]`
- Lesson: extra stacked diversifiers traded CAGR for MDD.

### 004 — 2026-04-28 — haa-global-factor-tilt (PROMISING, 69/100, DE-006)

- Intl small/value tilt inside HAA offensive. S 0.990/0.955/0.861; PBO 0.885/0.869/0.694 fails. `[stocks_on_the_move, ch.6]`
- Lesson: reshuffled risk-on equity exposure; unstable tilt selection.

### 003 — 2026-04-28 — global-factor-cta-stack (MARGINAL, 54/100, DE-005)

- Static global/factor/CTA stack; stack_gde_heavy selected. S 0.823/0.742/0.910; MDD 27-42%. `[risk_parity, p.1-2]`
- Lesson: low turnover preserved CAGR but lost HAA drawdown control.

### 002 — 2026-04-28 — composite-momentum-standard (MARGINAL, 55/100, DE-004)

- SPY200 top-4 inverse-vol composite momentum. S 0.940/0.958/0.957; 7/7 × 3 but return-capped. `[stocks_on_the_move, p.21-30]`
- Lesson: defensive 60/40 IEF/gold sleeve too low-return; annual DARF drag.

### 001 — 2026-04-28 — baa-g12-balanced (MARGINAL, 58/100, DE-003)

- BAA-G12 Balanced. S 0.975/0.792/0.782; 7/7, 7/7, 6/7. `[stocks_on_the_move, ch.6]`
- Lesson: too defensive/tax-dragged; never beats HAA+Gold.

---

## Promising unexplored directions (prioritized)

**Loop status: HUNTING past incumbent iter 011.** The user's explicit thesis
is "exposição global + fatores" — iter 011 has zero international equity and
zero factor tilt. Next iters should attack that gap.

### A. Global capital-efficient stack (iter 011 architecture, internationalized)

Replace pure-US NTSX with intl variants. Candidate:

1. ~~**NTSX + NTSI + NTSE + GDE + KMLM** (5-asset capital-efficient global stack)~~
   — **CLOSED iter 015 (DE-016)**: NTSI/NTSE synthesized testfolio-style for
   first time (`studies/long_term_portfolio/proxies.py`); 4 configs tested
   (mix of 4-asset / 5-asset); selected `intl_dev_lite_3515_GK_2030` hit tier
   WINNER 93/100 vs avg(SPY,VT) but TIES iter 014 score and fails Sharpe-edge
   gate vs iter 011 substantively (lh_56y +0.035 loose / **−0.038 strict**,
   vt_real **−0.083**, ndx_real **−0.056**). KILL #2 fired (5-asset uniformly
   < 4-asset → EM-as-component dead). KILL #3 fired (intl-equity weight
   monotonically reduces Sharpe on all 3 datasets). Component-swap inside
   the leveraged wrapper has the same regime-mismatch failure mode as
   sleeve-add outside it.
2. ~~**NTSX + GDE + RSSB + KMLM**~~ — **CLOSED iter 012 (DE-013)**: RSSB sleeve
   regresses Sharpe vs iter 011 across all 3 datasets (−0.030 / −0.109 / −0.083).
   RSSB's Treasury overlay overlaps NTSX's IEF exposure; intl-equity sleeve dragged
   in 2010-2026 regime. STRONG vs avg(SPY,VT) but does not advance incumbent.
3. ~~**NTSX + VXUS overlay + GDE + KMLM**~~ — **CLOSED iter 014 (DE-015)**:
   VXUSSIM 10/20/25/30% sweep on iter 011 base → tier WINNER 93/100 vs
   avg(SPY,VT) (5/5 strict conds) and mechanically takes incumbent (score
   93 > 91). BUT cross-config monotonic finding: Sharpe **decreases on
   ALL 3 datasets** as VXUSSIM rises 10%→30% (lh_56y 1.055→0.989,
   vt_real 0.885→0.744, ndx_real 1.052→0.917). **Loses Sharpe to iter
   011 on vt_real and ndx_real**, ties on lh_56y. Cleaner failure
   pattern than iter 012 (RSSB) — confirms intl-equity drag in
   2010-2026 is real and independent of Treasury overlap.

### B. Factor tilts on the iter 011 base — partially CLOSED

iter 011 has zero factor tilt. Constant-weight US factor tilt CLOSED iter 013
(DE-014). Remaining sub-axes:

4. ~~**Iter 011 + AVUV/AVDV core (constant weight)**~~ — **CLOSED iter 013
   (DE-014)**: VBRSIM 10/20/25/30% sweep on iter 011 base improves lh_56y
   monotonically (+0.060 → +0.085) but degrades vt_real / ndx_real
   monotonically (−0.04 → −0.14, −0.03 → −0.13). Selected lightest config
   (10%) is tier WINNER vs avg(SPY,VT) but does not advance iter 011
   incumbent. Constant-weight factor tilt is structurally subordinate
   on post-2008 windows (well-documented "death of value" regime).
5. **Iter 011 + UMD (Fama-French momentum) overlay** (now higher priority
   after iter 013) — 20% direct UMD factor exposure as Sharpe enhancer.
   UMD daily 1926+ on disk now. Different factor (momentum vs size+value),
   different post-2008 behavior (momentum had multiple positive years
   2017-2024 while value lagged). `[stocks_on_the_move, ch.6]` +
   Fama-French (1993).
6. **Iter 011 + factor with regime filter** (NEW direction emerging from
   iter 013's structural finding) — factor weight conditional on a
   value-spread (CAPE differential) or factor-momentum signal (12-1
   factor return). VBRSIM only when premium is "live"; KMLM/GDE
   otherwise. Pre-commit ≤ 3 configs to avoid the prior loop's
   "regime gate on existing winner" DSR-regression trap
   (`_archive` strategy_hunt_loop dead-ends 3-4).
7. ~~**NTSX + GDE + KMLM + AVUV + AVDV**~~ — would be a superset of iter
   013's grid; expected to fail by the same regime-mismatch logic.
   Defer until either #5 (UMD) or #6 (regime-filtered factor) shows
   positive signal.

### C. Live-data validation (deferred until A or B winner)

Run only if a candidate from A/B beats iter 011 — then validate on
post-2020 live KMLM, post-2018 live NTSX, post-live VT (when pulled).
This is the deploy-readiness gate, not a hunt direction.

### Closed by iter 011

- ~~NTSX + GDE + RSST static~~ — superseded by iter 011; sensitivity question.
- ~~NTSX + GDE + KMLM 40/30/30 (user primary)~~ — same family as iter 011's
  35/25/40 winner (passes too); not a fresh direction.

---

## Structural dead-ends (carry-over from global_factor_tilt_loop)

These were proven dead-ends in the predecessor loop. Same universe:
full text in `DEAD_ENDS.md`.

1. **2× single-asset global-equity LETF + binary SMA**: VTSIM base Sharpe
   (0.61) already matches Gayed LRS target → zero improvement. `[leverage_for_the_long_run, p.17]`
2. **VAA breadth with higher-notional equity (for Sharpe-max)**: GDESIM
   in offensive adds variance faster than returns; HAA canary dominates
   VAA breadth on Sharpe.
3. **Plain BAA-G12 Balanced in current universe**: robust drawdown reducer
   but too defensive/tax-dragged; net Sharpe 0.975/0.792/0.782 and CAGR
   below 0.8× iter009 on all datasets. `[stocks_on_the_move, ch.6]`
4. **Composite Momentum Standard with SPY200 top-4 inverse-vol**: robust
   7/7 gates × 3 but return-capped; net Sharpe 0.940/0.958/0.957, CAGR
   below HAA+Gold on all datasets, MDD too high on vt/ndx.
5. **Plain static global/factor/CTA stack**: low turnover restores CAGR
   floors but gives up HAA canary drawdown control; net Sharpe
   0.823/0.742/0.910 and MDD 27-42% fail the Sharpe/MDD frontier.
6. **Simple HAA international small/value tilt**: preserves HAA MDD but
   sacrifices Sharpe/CAGR; net Sharpe 0.990/0.955/0.861 and PBO
   0.885/0.869/0.694 show unstable tilt selection. `[stocks_on_the_move, ch.6]`
7. **Simple HAA RSST/RSSB/CTA offensive substitution**: robust 7/7 gates but
   lower-return; net Sharpe 0.953/1.028/0.946 and zero +0.10 Sharpe edges.
   Extra stacked diversifiers trade CAGR for MDD after iter009. `[risk_parity, ch.5]`
8. **Synthetic HAA RSIT offensive sleeve**: clears CAGR/MDD and DSR but loses
   Sharpe badly; net Sharpe 0.869/0.897/0.837 and PBO 0.714/0.845 on global
   windows. More embedded MF on international equity is not the missing edge.
   `[risk_parity, ch.5]`
9. **Simple HAA KMLM/CASH defensive swaps**: statistically robust but no
   improvement; original `IEFSIM/BNDSIM/CASHX` defense was selected with net
   Sharpe 0.983/0.954/0.860, while KMLM-heavy defense raised MDD to 27.49%.
   The next edge must change canary timing, not defensive assets.
   `[stocks_on_the_move, ch.6]`
10. **Simple HAA dual broad-equity canary (`VWOSIM` + `VTISIM`)**: original
   `VWOSIM` canary was selected again; `VTISIM` variants lowered Sharpe and
   the ndx_real PBO failed at 0.552. The next timing edge must use a
   qualitatively different trend/regime input. `[stocks_on_the_move, p.63-65]`
11. **Simple Gayed SPY/VT trend input as HAA canary**: original `VWOSIM`
    selected again; SPY/VT trend filters either cut CAGR or raised real-window
    MDD, with net Sharpe 0.983/0.954/0.860 and no +0.10 Sharpe edge.
    `[leverage_for_the_long_run, p.40-60]`
12. **Simple HAA dynamic-sleeve volatility throttle**: `vol12` passed 7/7
    gates across all datasets and reduced MDD, but failed every CAGR floor
    and produced net Sharpe 1.020/0.955/0.881 with zero +0.10 Sharpe edges.
    Drawdown throttling is not the missing return source. `[systematic_trading, p.137-148]`
13. **NTSX+GDE+RSSB+KMLM 4-asset global stack (iter 011 internationalized)**:
    selected `rssb_moderate_25252525` produced gross Sharpe 1.011/0.851/1.021
    — STRONG 88/100 vs avg(SPY,VT) (5/5 strict conditions met) but LOSES vs
    iter 011 incumbent on Sharpe across all 3 datasets (−0.030 / −0.109 / −0.083).
    Pre-committed kill #1 fired. RSSB's Treasury overlay overlaps NTSX's IEF;
    intl-equity sleeve dragged in 2010-2026 regime. `[risk_parity, ch.5, p.10]`
14. **Constant-weight US factor tilt on iter 011 base (NTSX + GDE + KMLM +
    VBRSIM 10/20/25/30%)**: selected `factor_lite_30253510` (10% VBRSIM)
    hit tier WINNER 91/100 vs avg(SPY,VT) — all 5 strict conditions met,
    3/3 +0.10 edge vs passive baseline. But ties iter 011's score (91=91,
    not >) and only +0.080 on lh_56y while LOSING on vt_real (−0.037)
    and ndx_real (−0.029). Cross-config monotonic finding: factor tilt
    helps lh_56y (+0.060→+0.085 over 10%→30%) but hurts both live
    windows (−0.04→−0.14, −0.03→−0.13). Post-2008 "death of value"
    regime makes constant-weight factor tilt structurally subordinate
    to iter 011 on deploy-relevant windows. `[risk_parity, ch.2, p.37-41]`,
    `[stocks_on_the_move, ch.6, p.21-30]`
16. **A.1 — 5-asset global capital-efficient stack (NTSX + NTSI + NTSE +
    GDE + KMLM, component-swap inside the 1.5× wrapper)**: iter 015
    synthesized NTSI/NTSE testfolio-style for first time
    (`proxies.py`, 90/60/−50 WisdomTree blueprint). Selected
    `intl_dev_lite_3515_GK_2030` (4-asset variant) hit tier WINNER 93/100
    vs avg(SPY,VT) (5/5 strict conds, 3/3 +0.10 edges). TIES iter 014's
    score (93=93, NOT >); fails Sharpe-edge gate vs both incumbents on
    all 3 datasets (Δ vs iter 011: +0.035 loose / **−0.038 strict** lh_56y,
    **−0.083** vt_real, **−0.056** ndx_real). KILL #2 fired: 5-asset configs
    (with NTSE) uniformly Sharpe-regress vs 4-asset (no NTSE) on all 3
    datasets — EM-as-component within 1.5× wrapper is structurally
    subordinate. KILL #3 fired: intl-equity weight monotonically reduces
    Sharpe on all 3 datasets (15%→35%). **Direction A is now CLOSED end-
    to-end** — both sleeve-add (012/013/014) and component-swap (015)
    structural variants exhausted; iter 011 NTSX is the architectural
    ceiling for static cap-efficient stacks in the 2010-2026 US-large-
    cap-dominant regime. `[risk_parity, ch.5, p.10]`, `[ilmanen, ch.19]`.

15. **Constant-weight intl-equity tilt on iter 011 base (NTSX + VXUSSIM +
    GDE + KMLM, VXUSSIM 10/20/25/30%)**: selected `intl_lite_35253010`
    (10% VXUSSIM) hit tier WINNER 93/100 vs avg(SPY,VT) — all 5 strict
    conditions met, 3/3 +0.10 edge vs passive baseline; score 93 > 91 →
    mechanically advances iter 011 incumbent. BUT cross-config monotonic
    finding: Sharpe DECREASES on **all 3 datasets** as VXUSSIM rises 10%
    → 30% (lh_56y −0.066, vt_real −0.141, ndx_real −0.135). Substantively
    LOSES Sharpe to iter 011 on vt_real (−0.075) and ndx_real (−0.052),
    ties on lh_56y (+0.009). 3rd consecutive sleeve-injection failure
    (012, 013, 014) confirms iter 011 is the architectural ceiling for
    constant-weight stacks; next research must pivot to regime-conditional
    weighting OR architectural replacement (NTSI/NTSE proxy synthesis).
    `[risk_parity, ch.5, p.10]`, `[ilmanen, ch.19]`, `[stocks_on_the_move, p.21-30]`

---

## Binding constraints (mandate §1, §5, §7)

- **NEVER modify `docs/investment-mandate.md`** — even a winner is a
  candidate, not auto-deploy.
- **Citations obrigatórias** (CLAUDE.md Regra 2): every decision cites
  `[book.slug, p.X]`.
- **7-gate battery** mandatory per `WINNER_AND_RANKING.md`
- **AnnualDarfEngine only** for net-of-tax: `tax_engine_v2.py`
  (`studies/global_factor_tilt_loop/`). NEVER use `DarfCostBasisEngine`.
- **Pytest baseline (461) stays green** — never reduce passing count
- **Max 2h wall-time** per iteration
- **NEVER `git commit`** — `run_loop.sh` handles commits
- **DO NOT touch** `studies/strategy_hunt_loop/`, `studies/gold_swing_loop/`,
  `studies/global_factor_tilt_loop/` — parallel sessions / frozen loop
