---
mission: "Find ONE long-term strategy with mean CAGR ≥ SPY (13.80%) AND mean MDD ≤ SPY (40.85%) AND surviving 7-gate battery on ≥ 2/3 datasets"
target_total_iterations: 50
total_iterations: 2
winners_found: 0
closest_to_winner: "a2_sma150_2xsso (iter 002): CAGR 14.82% PASS, MDD 43.49% (gap +2.64pp from 40.85% ceiling), gates 4/4/4 PASS"
status: hunting
latest_iteration: "002-2026-04-29-A2-LRS-sensitivity-sweep"
latest_score: 63
latest_tier: PROMISING
latest_bars_met: 2  # CAGR ✓, gates ✓, MDD ✗
cumulative_n_trials: 10
direction_status:
  A1_200d_SMA_3x_UPRO: "PROMISING (iter 001) — CAGR-rich, MDD-bottlenecked"
  A2_faster_signal: "CLOSED (iter 002 KILL #7) — faster SMA/EMA make MDD WORSE"
  A2_threshold_buffer: "CLOSED (iter 002 KILL #8) — buffer ≥5% makes MDD worse"
  A2_lower_leverage: "PROMISING (iter 002) — 2× SSO best near-miss yet"
  B1_HFEA_classical: "NOT YET RUN — TMFSIM ready"
  C1_vol_targeted: "NOT YET RUN"
parent_loop: "studies/long_term_portfolio (43 iters, F1+SPLIT incumbent fallback)"
note: "Forked 2026-04-29. Iter 001 PROMISING 67/100: CAGR✓ MDD✗ Gates✓. Iter 002 PROMISING 63/100 sensitivity sweep: KILL #7+#8 fired — faster signal/buffer make MDD WORSE not better. KILL #9 NOT fired — 2× SSO is the only lever that helped (closest config to WINNER yet, gap only +2.64pp on MDD). Next iter 003 should test variants of (lower leverage + 200d SMA + alternative off-regime) since that's the only direction not yet exhausted within Tier 1. F1+SPLIT remains deploy fallback if 50-iter hunt fails."
---

# spy_beater_hunt — BASE MEMORY

**Read FIRST every iteration.** Conversation history is empty; this file + `iterations/NNN-*/` are continuity. Process: see `SPEC.md`. Infra: `INFRASTRUCTURE.md`.

---

## Mission (recap)

Find ONE long-term strategy with:
- **Mean CAGR ≥ 13.80%** (SPY 3-dataset mean)
- **Mean MDD ≤ 40.85%** (SPY 3-dataset mean)
- **7-gate battery passes ≥ 2/3 datasets**

Per-dataset SPY benchmarks:
| dataset | window | SPY CAGR | SPY MDD |
|---|---|---:|---:|
| lh_56y | 1986-2026 (40y) | 11.47% | 55.14% |
| vt_real | 2008-2026 (~17y) | 14.97% | 33.70% |
| ndx_real | 2010-2026 (16y) | 14.97% | 33.70% |
| **mean** | | **13.80%** | **40.85%** |

---

## Why this hunt exists (context for any iter)

Long_term_portfolio loop concluded 2026-04-29 with F1+SPLIT (NTSX 25 + GDE 25 + KMLM 17.5 + DBMF 17.5 + TLT 15) as deploy-ready candidate. Mean CAGR 10.76% (gap −3.04pp vs SPY mean 13.80%), Mean MDD 16.76% (24pp better than SPY).

User feedback: "MUITO DIFÍCIL seguir uma estratégia que não vai bater o SPY em CAGR" — psychologically + behavioral concern, even if 30y math favors better Sharpe.

This hunt explicitly addresses the CAGR gap. Most defensible paths: leverage + regime gate (Gayed LRS) or HFEA leveraged barbell.

---

## Reuse from long_term_portfolio

This loop reuses the foundation:
- `studies/long_term_portfolio/synths.py` — 8 synth functions (NTSD/AVUV/AVDV/AVEM/SPMO/IDMO/RSST/CTA-proxy)
- `studies/long_term_portfolio/run_iter.py` — execution helper (portfolio_returns_from_config, run_iter_full)
- `studies/long_term_portfolio/proxies.py` — NTSX/NTSI/NTSE blueprints
- `studies/long_term_portfolio/datasets.py` — load_prices for 3 datasets
- `studies/long_term_portfolio/scoring.py` — adaptable; spy_beater_hunt has its own scoring rubric (CAGR-anchored)

NEW synths likely needed (NOT in long_term_portfolio):
- TMFSIM (3× LTT for HFEA) — synth via `TLTSIM × 3 - 1.5%/y daily-reset decay`
- HFEA-blend strategies
- Regime-gated leveraged equity (UPRO + 200d SMA on SPY)

---

## Iteration log (newest first)

### iter 002 — A2 LRS sensitivity sweep (SMA/EMA × window × buffer × leverage) (2026-04-29)

- **Tier**: PROMISING **63/100** (winner_conditions_met = False, 2/3 bars)
- **Selected**: `a2_sma200_th2_3xupro` (highest Sharpe — but NOT the closest-to-winner)
- **Closest-to-winner**: `a2_sma150_2xsso` (CAGR 14.82% PASS, MDD 43.49% — gap +2.64pp from ceiling)
- **Configs tested (6)**: SMA100/SMA200+th2/SMA200+th5/EMA150+th2/SMA150-2xSSO/EMA100+th2-2xSSO
- **KILL #7 FIRED** (signal speed): SMA100 MDD 64.07% > SMA200 50.57% → faster signal HURTS MDD
- **KILL #8 FIRED** (threshold buffer): th2 ≈ pure (no benefit), th5 MDD 65.94% (active harm)
- **KILL #9 NOT FIRED**: 2× SSO MDD 43.49% (best of all configs) → lower leverage IS the lever
- **Per-config (mean across 3 datasets)**:
  | config                  | CAGR    | MDD    | bars (CAGR/MDD/gates) |
  |-------------------------|--------:|-------:|:----------------------|
  | a2_sma100_3xupro        | 19.01%  | 64.07% | ✓/✗/?                 |
  | a2_sma200_th2_3xupro    | 21.62%  | 57.57% | ✓/✗/✓                 |
  | a2_sma200_th5_3xupro    | 19.57%  | 65.94% | ✓/✗/?                 |
  | a2_ema150_th2_3xupro    | 19.55%  | 71.69% | ✓/✗/?                 |
  | **a2_sma150_2xsso**     | **14.82%** | **43.49%** | **✓/✗/✓ (closest)** |
  | a2_ema100_th2_2xsso     | 14.58%  | 56.28% | ✓/✗/?                 |
- **Key finding**: 200d SMA + 2× SSO + IEF off is the ONLY surviving direction
  in Tier 1. Next iter 003 should test: 1.5× lev variants, 2× SSO with longer
  windows (250d/300d), 2× SSO with KMLM/DBMF off-regime.
- **DSR caveat**: worst p = 0.0516 just above 0.05 threshold (n_trials=10
  starting to bite); future iters should test 4 configs not 6 to slow inflation.
- **Citations**: `[leverage_for_the_long_run, ch.3-4, p.40-60]` (validated);
  `[advances_fin_ml, p.222-223]` DSR multi-testing penalty.

### iter 001 — A1 Gayed LRS UPRO + 200d SMA gate (2026-04-29)

- **Tier**: PROMISING **67/100** (winner_conditions_met = False, 2/3 bars)
- **Selected**: `a1_lrs_split` (50% UPROSIM + 50% SSOSIM when SPY > 200d MA, 100% IEFSIM when off)
- **Bars**: CAGR ✓ (mean 19.01%, +5.21pp), MDD ✗ (mean 50.57%, +9.72pp over ceiling), Gates ✓ (6/6/5)
- **KILL #6 monitor**: NOT triggered (a1_pure_lrs CAGR 21.04% >> 13.80%)
- **Per-dataset (selected)**:
  | dataset  | Sharpe | CAGR    | MDD    | gates | DSR p     |
  |----------|-------:|--------:|-------:|------:|----------:|
  | lh_56y   | 0.670  | 16.91%  | 54.70% | 6/7   | 7.91e-04  |
  | vt_real  | 0.784  | 20.68%  | 48.50% | 6/7   | 1.34e-02  |
  | ndx_real | 0.753  | 19.43%  | 48.50% | 5/7   | 2.63e-02  |
- **Lesson**: Gayed LRS is structurally CAGR-rich but MDD-bottlenecked.
  WF within-window max_mdd 0.40-0.55 across all 3 datasets — 200d SMA is
  too laggy for tail-risk (1987, 2008, 2020, 2022). Citation:
  `[leverage_for_the_long_run, ch.3-4, p.40-60]`.
- **Direction status**: not WINNER. Continue per user plan to iter 002 (B1
  HFEA classical) per `PROMISING_DIRECTIONS.md` ranking.

---

## Promising unexplored directions

See `PROMISING_DIRECTIONS.md` for the full ranked list. Highlights:

### Tier 1 (literature-strong, deployable)
- **A1 Gayed LRS UPRO 200d-SMA** — 100% UPRO when SPY > 200d MA, else IEF. Cite `[leverage_for_the_long_run, ch.3-4, p.40-60]`.
- **B1 HFEA classical 55/45** — 55% UPRO + 45% TMF (3× SPY + 3× LTT) quarterly rebalanced. Bogleheads 2019.
- **A2 Gayed LRS TQQQ 200d-SMA** — concentrate growth, regime-gated.

### Tier 2 (literature-supported, more risk)
- **B2 HFEA modern 60/40** — 60% UPRO + 40% TMF
- **C1 Vol-targeted SPY 1.5×** — UPRO when 60d vol < 15%, else SPY
- **A3 Mixed Gayed (UPRO + KMLM + TLT)** — leverage + crisis-alpha

### Tier 3 (exploratory)
- **D1 Concentrated growth + regime** — QQQ 100% with monthly momentum gate
- **C2 CAPE-timing** — equity when CAPE < median, bonds when above

---

## Pre-flight checklist before iter 001

Before starting iter 001:
1. Verify testfolio cache has UPROSIM, SSOSIM, TQQQSIM, QLDSIM (already confirmed yes per exploration)
2. Build TMFSIM synth (TLTSIM × 3 - 1.5%/y decay) — TDD test
3. Build LRS engine (200d SMA gate on price series, T+1 lag, no peek-ahead) — TDD test
4. Pick first iter hypothesis from Tier 1 (recommended: A1 Gayed LRS UPRO)

---

## Citations (loop-wide)

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA on LETFs
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking (long_term_portfolio baseline)
- `[advances_fin_ml, p.208-211]` PBO via CSCV
- `[advances_fin_ml, p.222-223]` DSR
- `[advances_fin_ml, p.196-202]` bootstrap CI
- `[advances_fin_ml, p.31-34]` cross-lib + factor framework
- HFEA classical (Hedgefundie Bogleheads 2019) — leveraged barbell
- Frazzini-Israel-Moskowitz 2018 — UMD long-only capture rate
