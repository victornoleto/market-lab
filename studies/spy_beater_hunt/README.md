# spy_beater_hunt

**Status**: PROPOSED — bootstrapped 2026-04-29 after long_term_portfolio sweep concluded with F1+SPLIT (CAGR 10.76% < SPY 13.80%).

**Mission**: Find ONE long-term portfolio strategy with **mean CAGR ≥ SPY (13.80%)** AND **mean MDD ≤ SPY (40.85%)** AND surviving the 7-gate battery (PBO/DSR/WF/Bootstrap/CrossLib) on ≥ 2/3 datasets (lh_56y / vt_real / ndx_real).

This is a **harder bar than long_term_portfolio's** — that loop's mission was Sharpe-edge anchored (CAGR was warning-only). User feedback after 43-iter sweep: "MUITO DIFÍCIL seguir uma estratégia que não vai bater o SPY em CAGR." This hunt directly addresses that.

---

## Why fork instead of extending long_term_portfolio?

1. **Different mission, different gates**: spy_beater is CAGR-anchored (bar = SPY's 13.80% mean). long_term_portfolio was Sharpe-anchored (bar = SPY + 0.05).
2. **Different design philosophy**: F1+SPLIT trades CAGR for Sharpe/MDD via stacking + crisis-alpha. This hunt explicitly seeks higher CAGR — likely via leveraged equity + regime gates (Gayed LRS family) OR tactical leveraged barbells (HFEA family).
3. **Avoid mission creep**: long_term_portfolio's BASE_MEMORY + WINNER_AND_RANKING are tuned for the prior mission. Reframing them invalidates 43 iters of cross-iter comparability.
4. **Reuse infra, not mission**: this hunt reuses `studies/long_term_portfolio/synths.py`, `run_iter.py`, `proxies.py`, `datasets.py` — but has its own scoring/winner criteria.

---

## Mission honesty calibration

**Why this might fail (be prepared)**:
- 43 prior iters with F1+SPLIT as best couldn't produce CAGR > SPY mean
- bestfolio_meta_wf_hunt parallel session investigation confirmed bestfolio's 19.8% claim is NOT replicable in our gate-screened universe (kill K3 fired iter 001)
- The 13.80% SPY mean is dragged up by 2008-2024 vt_real/ndx_real Tiingo windows (14.97% each); lh_56y SPY is only 11.47% (F1 already beats this)
- Most strategies that beat SPY long-term do so via Sharpe gain (lower vol), not CAGR uplift — fundamental risk-return tradeoff

**Why it might succeed**:
- We haven't exhaustively tested **leveraged equity + regime gate** (Gayed LRS family) — `[leverage_for_the_long_run, p.40-60, ch.3-4]` shows 200d SMA gate dramatically reduces LETF decay
- HFEA classical (3× SPY + 3× LTT) backtest beats SPY historically — but huge regime risk (2022 was catastrophic)
- Stacked equity (NTSX + GDE) at higher leverage might unlock CAGR + Sharpe simultaneously
- Concentrated growth (QQQ + leverage + regime gate) tracks growth premium directly

**The bar is exact, not approximate**. We accept "winner" only if BOTH (CAGR ≥ 13.80% AND MDD ≤ 40.85% AND gates pass). Near-miss = not a winner.

---

## Files

| file | purpose |
|---|---|
| `README.md` | this file |
| `SPEC.md` | mission spec + gate definitions + winner criteria |
| `BASE_MEMORY.md` | iteration log + frontmatter (loop state) |
| `WINNER_AND_RANKING.md` | tier rubric (CAGR/MDD-anchored, distinct from long_term_portfolio) |
| `INFRASTRUCTURE.md` | what to reuse from long_term_portfolio (synths.py / run_iter.py / scoring.py adaptations) |
| `PROMISING_DIRECTIONS.md` | ranked list of hypotheses pre-loaded for the hunt |
| `iterations/` | one dir per iter (bootstrapped empty) |

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA gate on leveraged equity
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking baseline
- `[advances_fin_ml, p.208-211]` PBO via CSCV
- `[advances_fin_ml, p.222-223]` DSR
- `[advances_fin_ml, p.196-202]` bootstrap CI
- HFEA classical (Hedgefundie's Excellent Adventure, Bogleheads forum 2019)

---

## Mandate context

This hunt operates under mandate §1 MAINTENANCE MODE (2026-04-23). Any winner candidate goes through mandate §7 override request, same as F1+SPLIT.

The current default position remains **F1+SPLIT** if this hunt fails to find a strategy that satisfies both bars. F1+SPLIT is empirically validated and deploy-ready; spy_beater_hunt seeks improvement, not replacement of the safety net.
