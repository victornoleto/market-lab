---
mission: "Find ONE long-term strategy with mean CAGR ≥ SPY (13.80%) AND mean MDD ≤ SPY (40.85%) AND surviving 7-gate battery on ≥ 2/3 datasets"
total_iterations: 0
winners_found: 0
status: bootstrapped
latest_iteration: null
latest_score: null
cumulative_n_trials: 0
parent_loop: "studies/long_term_portfolio (43 iters, F1+SPLIT incumbent fallback)"
note: "Forked 2026-04-29 from long_term_portfolio after F1+SPLIT (mean CAGR 10.76%) failed user's CAGR-vs-SPY criterion. Mission redefined: CAGR-anchored. Most defensible hypothesis directions: Gayed LRS [leverage_for_the_long_run, ch.3-4] (UPRO/TQQQ + 200d SMA gate) and HFEA-style leveraged barbells (UPRO + TMF synth). F1+SPLIT remains deploy fallback if hunt fails."
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

(Empty — bootstrapped 2026-04-29.)

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
