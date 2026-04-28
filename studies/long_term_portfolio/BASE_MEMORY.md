---
mission: "beat avg(SPY 1× b&h, VT 1× b&h) gross-of-tax Sharpe by ≥0.10 on ≥2 of 3 datasets"
total_iterations: 11
winners_found: 1
status: winner
latest_iteration: "011-2026-04-28-1537-ntsx-gde-kmlm-static"
cumulative_n_trials: 40
note: "Renamed from bestfolio_hunt_loop on 2026-04-28. Mission redefined to 'beat avg(SPY,VT)' (gross-of-tax), scoring.py reworked accordingly. Net-of-tax (Lei 14.754/2023, _shared/tax_engine.py) is reported as deploy-readiness diagnostic but does NOT gate. WINNER 2026-04-28: iter 011 NTSX+GDE+KMLM static stack — score 91/100, all 5 strict winner conditions met, 3/3 datasets clear +0.10 Sharpe edge, family-level robust (all 4 weight variants pass). Shell loop halts."
---

# Long-Term Portfolio Loop — BASE MEMORY

**Read FIRST every iteration.** Conversation history is empty; this
file + `iterations/NNN-*/` are continuity. Process: `PROMPT.md`. Infra:
`INFRASTRUCTURE.md`.

---

## Mission

Find ONE long-term portfolio strategy that **beats the average of
SPY 1× b&h and VT 1× b&h** (gross-of-tax) by **≥ 0.10 Sharpe on ≥ 2
of 3 datasets**, while passing the 7-gate battery and respecting CAGR
floor / MDD ceiling.

**Per-dataset benchmarks** (from `scoring.py` BENCHMARKS dict):

| dataset | benchmarks averaged | avg Sharpe | avg CAGR | max MDD (ceiling base) |
|---|---|---:|---:|---:|
| educational (56y) | VTSIM 56y + SPYSIM 40y | **0.671** | 10.73% | 58.35% |
| vt_real (17y) | VTSIM 17y + SPY 17y | **0.707** | 11.88% | 50.21% |
| ndx_real (16y) | QQQ 16y + SPY 16y | **0.924** | 16.98% | 35.12% |

**Winner threshold (Sharpe edge gate)**: candidate must reach Sharpe
≥ **0.77 / 0.81 / 1.02** on ≥ 2 of 3 datasets (avg + 0.10).

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

## Winners found

| # | iter | slug | status | edu S/CAGR/MDD | vt S/CAGR/MDD | ndx S/CAGR/MDD | note |
|---|---|---|---|---|---|---|---|
| 1 | 011 | ntsx-gde-kmlm-static | 🏆 WINNER (91/100) | 1.021 / 11.58% / 26.04% | 0.960 / 10.95% / 21.22% | 1.104 / 11.64% / 14.12% | Static 35% NTSX + 25% GDE + 40% KMLM stack. All 5 strict conditions met. 3/3 datasets beat avg(SPY,VT) +0.10 Sharpe edge (edu +0.350, vt +0.253, ndx +0.180). Net ≈ Gross (static buy-hold = no DARF until liquidation under Lei 14.754/2023). Family-level robust: all 4 weight variants pass; user's primary 40/30/30 also passes. Caveat: G1 PBO fails on real-data slots (config-noise within tightly-correlated grid), KMLMSIM synth pre-2020. |

---

## Top-K strategies ranked

| rank | iter | slug | score | tier | Sharpe (edu/vt/ndx) | CAGR (edu) | MDD (edu) |
|---|---|---|---|---|---|---|---|
| 1 | **011** | **ntsx-gde-kmlm-static** | **91** | 🏆 **WINNER** | **1.021/0.960/1.104** (gross) | **11.58%** | **26.04%** |
| 2 | 007 | haa-defensive-kmlm-cash | 75 | STRONG | 0.983/0.954/0.860 (net) | 12.15% | 20.81% |
| 3 | 009 | haa-gayed-trend-canary | 73 | PROMISING | 0.983/0.954/0.860 (net) | 12.15% | 20.81% |
| 4 | 008 | haa-dual-canary | 73 | PROMISING | 0.983/0.954/0.860 (net) | 12.15% | 20.81% |
| 5 | 006 | haa-rsit-synth | 71 | PROMISING | 0.869/0.897/0.837 (net) | 11.13% | 22.12% |

---

## Iteration log (newest first)

### 011 — 2026-04-28 — ntsx-gde-kmlm-static (🏆 WINNER, 91/100)

- Hypothesis: User's literal architectural preference — 40% NTSX + 30% GDE + 30% KMLM static capital-efficient stack — untested across 10 prior iters; tested under the redefined avg(SPY,VT) gross-of-tax mission.
- Citations: `[risk_parity, ch.5, p.10]`; `[stocks_on_the_move, p.21-30]`; gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 4 pre-committed configs (`user_primary_403030`, `equal_weight_333333`, `equity_tilted_502525`, `mf_tilted_352540`); selected `mf_tilted_352540` by max mean(gross_Sharpe / avg(SPY,VT)_Sharpe). Datasets: educational (1995-2026 31y), vt_real (17y), ndx_real (16y).
- Result: gross Sharpe **1.021 / 0.960 / 1.104** (edges **+0.350 / +0.253 / +0.180** vs avg(SPY,VT)); gates **7/7 / 6/7 / 6/7**; DSR p **1.79e-6 / 1.36e-3 / 4.07e-4**. All 5 strict winner conditions met. **3/3 datasets clear +0.10 Sharpe edge**; family-level robust (all 4 weight variants pass — user's 40/30/30 also passes WINNER on Sharpe edge).
- Net (informational): Sharpe **1.021 / 0.960 / 1.104** ≈ gross (static buy-hold + Lei 14.754/2023 PF direta = no realized gains until liquidation; daily-Sharpe tax-neutral).
- Score breakdown: Sharpe edge 25/25; gates 21/25 (cross-dataset bonus); DSR 15/15; CAGR floor 10/15 (ndx misses by 0.46pp); MDD ceiling 15/15; robustness 5/5 (100% positive 5y rolling Sharpe across 27 windows).
- Lesson: User's instinct ("diversified + leveraged through stacking, no rotation cost") was correct. Mission redefinition matters — DE-005 closed plain static stacks under iter009 benchmark; under avg(SPY,VT) the same architecture is winner. Capital efficiency via NTSX/GDE futures overlay is the only leverage path that has produced a winner across either loop. Crisis-alpha decoupling via KMLM provides the marginal +0.05-0.15 Sharpe edge. Caveats: G1 PBO fails on vt/ndx (within-family weight selection at noise level — robust at family level); KMLMSIM synth pre-2020.

### 010 — 2026-04-28 — haa-vol-throttle (PROMISING, 60/100)

- Hypothesis: Keep iter 009 HAA+Gold assets/canary unchanged and add a Carver-style realized-volatility throttle to only the 85% dynamic sleeve.
- Citations: `[systematic_trading, p.137-148]`; `[systematic_trading, p.196-197]`; `[stocks_on_the_move, ch.6]`; gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 4 pre-committed configs (`no_throttle`, `vol12`, `vol15`, `vol18`); selected `vol12` by mean Sharpe / iter009 Sharpe; AnnualDarfEngine net-of-tax; educational/vt_real/ndx_real.
- Result: net Sharpe **1.020 / 0.955 / 0.881**; gates **7/7 / 7/7 / 7/7**; DSR p **3.67e-06 / 2.34e-03 / 9.38e-03**. Kill fired: edu Sharpe gain vs baseline was +0.037 (< +0.05) and 0 datasets beat iter009 by +0.10.
- Score breakdown: Sharpe edge 0/25; gates 25/25; DSR 15/15; CAGR floor 0/15; MDD ceiling 15/15; robustness 5/5.
- Lesson: Vol throttling cleaned drawdowns (edu MDD 14.86%) but converted HAA+Gold into a lower-CAGR defensive variant; useful for capital preservation, not the missing Sharpe-frontier edge.

### 009 — 2026-04-28 — haa-gayed-trend-canary (PROMISING, 73/100)

- Hypothesis: Keep iter 009 HAA+Gold assets unchanged and alter only the binary HAA trigger with simple `SPYSIM`/`VTSIM` Gayed-style 10-month trend modes.
- Citations: `[leverage_for_the_long_run, p.40-60]`; `[stocks_on_the_move, ch.6]`; gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 4 pre-committed canary modes (`vwo_original`, `spy_trend`, `vt_trend`, `vwo_and_spy_trend`); selected `vwo_original` by mean Sharpe / iter009 Sharpe; AnnualDarfEngine net-of-tax; educational/vt_real/ndx_real.
- Result: net Sharpe **0.983 / 0.954 / 0.860**; gates **7/7 / 7/7 / 6/7**; DSR p **8.88e-06 / 2.36e-03 / 1.15e-02**. Kill fired: educational Sharpe <= 1.120 and 0 datasets beat iter009 by +0.10.
- Score breakdown: Sharpe edge 0/25; gates 23/25; DSR 15/15; CAGR floor 15/15; MDD ceiling 15/15; robustness 5/5.
- Lesson: The original `VWOSIM` canary was selected again; simple SPY/VT trend filters either cut CAGR or raised real-window MDD. The next timing edge must use a qualitatively different non-price/regime input, not broad-equity moving average.

### 008 — 2026-04-28 — haa-dual-canary (PROMISING, 73/100)

- Hypothesis: `VWOSIM`/`VTISIM` dual canary for HAA+Gold. Result: 0.983/0.954/0.860 Sharpe; gates 7/7, 7/7, 6/7; score 73.
- Lesson: original `VWOSIM` selected again; second broad-equity canary did not improve state classification. `[stocks_on_the_move, p.63-65]`

### 007 — 2026-04-28 — haa-defensive-kmlm-cash (STRONG, 75/100)

- Hypothesis: swap HAA defensive assets to KMLM/CASH variants. Result: 0.983/0.954/0.860 Sharpe; gates 7/7 x3; score 75.
- Lesson: original `IEFSIM/BNDSIM/CASHX` defense won; missing edge is canary timing, not simple defensive assets. `[stocks_on_the_move, ch.6]`

### 006 — 2026-04-28 — haa-rsit-synth (PROMISING, 71/100)

- Hypothesis: synthetic `RSIT_PROXY = VEASIM + KMLMSIM - 50bps/y` inside HAA. Result: 0.869/0.897/0.837 Sharpe; gates 6/7, 6/7, 7/7; score 71.
- Lesson: more embedded managed futures on international equity worsened Sharpe/PBO; closed until live RSIT data exists. `[risk_parity, ch.5]`

### 005 — 2026-04-28 — haa-rsst-rssb-cta (PROMISING, 70/100)

- Hypothesis: RSST/RSSB/CTA offensive substitution in HAA. Result: 0.953/1.028/0.946 Sharpe; gates 7/7 x3; score 70.
- Lesson: robust, but extra diversifiers traded CAGR for MDD and did not add Sharpe edge. `[risk_parity, ch.5]`

### 004 — 2026-04-28 — haa-global-factor-tilt (PROMISING, 69/100)

- Hypothesis: simple international small/value tilt inside HAA. Result: 0.990/0.955/0.861 Sharpe; gates 6/7 x3; score 69.
- Lesson: reshuffled risk-on equity exposure; PBO unstable and no Sharpe-frontier advance. `[stocks_on_the_move, ch.6]`

### 003 — 2026-04-28 — global-factor-cta-stack (MARGINAL, 54/100)

- Hypothesis: static global/factor/CTA stack. Result: 0.823/0.742/0.910 Sharpe; gates 6/7 x3; score 54.
- Lesson: low turnover preserved CAGR but lost HAA drawdown control; MDD 27-42% is too high. `[risk_parity, p.1-2]`

### 002 — 2026-04-28 — composite-momentum-standard (MARGINAL, 55/100)

- Hypothesis: SPY200 top-4 inverse-vol composite momentum. Result: 0.940/0.958/0.957 Sharpe; gates 7/7 x3; score 55.
- Lesson: robust but return-capped; IEF/gold defense and annual DARF drag left too little CAGR. `[stocks_on_the_move, p.21-30]`

### 001 — 2026-04-28 — baa-g12-balanced (MARGINAL, 58/100)

- Hypothesis: plain BAA-G12 Balanced. Result: 0.975/0.792/0.782 Sharpe; gates 7/7, 7/7, 6/7; score 58.
- Lesson: robust drawdown reducer, but too defensive/tax-dragged and never beats HAA+Gold. `[stocks_on_the_move, ch.6]`

---

## Promising unexplored directions (prioritized)

**Loop status: WINNER (iter 011) — shell loop halts.** The directions below
are deferred follow-ups, not active hunt items.

### Deferred — live-data validation of iter 011 winner (highest priority)

1. **Pull live VT and KMLM daily prices** from Tiingo to replace VTSIM/KMLMSIM
   proxies. Re-run gates on the live-data window only (KMLM live since
   2020-12) to confirm the synth period is not the source of the Sharpe edge.
2. **Sensitivity grid**: re-run iter 011 with KMLM swapped for DBMF or
   `RSST_PROXY` to see if the MF sleeve effect generalizes vs a KMLM-specific
   artifact.
3. **Mandate §7 override draft**: prepare the mandate override request for
   Plano C deployment of iter 011. Does NOT auto-deploy — requires signed
   user override per CLAUDE.md mandate §1.

### Deferred — international stack expansion

Add NTSI / NTSE / RSSB to the iter 011 family for a "global capital-efficient
stack" candidate. Worth testing only if the live-data validation above
confirms the iter 011 edge holds. Otherwise it is premature complexity.

### Closed by iter 011

- ~~NTSX + GDE + RSST static (RSST variant)~~ — superseded; static stack
  family is now confirmed winner under the redefined mission. RSST swap is
  a sensitivity question, not a fresh direction.

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
