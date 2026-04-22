# Phase 3.7 H2.c — VIX term-structure regime rotation (honest validation)

**Date:** 2026-04-23 | **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched `prev_weight × ret` alignment `[advances_fin_ml, p.31-34]`
**Broker path modelled:** Banco Inter BRL→USD rota B — spread **5 bps**
round-trip, commission **0 bps**, **15% DARF** on realized gains per
mandate §2.2 rota B + §4.6.
**Windows:** IS 2011-01-04 → 2018-12-31 (~8y) | OOS 2019-01-01 →
2022-12-31 (~4y, includes COVID + 2022 rate shock) | FWD 2023-01-01 →
2026-04-14 (~3.3y).
**Data sources:** Tiingo daily SPY/SSO/TLT + `data/phase3_7/vix/{VIXY,
VXX}.parquet`. VIXY inception 2011-01-04 bounds the IS start (~8y IS is
shorter than H2.a/b due to VIXY inception — honest concession).

## Verdict: **FAIL (hard gates)**

The VIX term-structure regime signal (VIXY 21-day trailing return ≤ 0 ⇒
contango ⇒ risk-on SPY, else risk-off TLT) **fails 4 of 5 hard gates
and 3 of 9 soft gates** under the honest engine + rota B cost model.
OOS Sharpe **0.480** (gate 2 ≥ 1.3 → FAIL) and the bootstrap 99.9% CI
on OOS Sharpe is **[−1.14, 2.07]** — straddles zero by more than a full
Sharpe point (gate 10 HARD → FAIL). DSR p = **0.633** (gate 12 HARD
< 0.05 → FAIL). Cross-lib concordance **fails by a hair** — vectorbt
reports 3.04 pp OOS CAGR delta versus the pandas reference (gate 9
threshold 3.0 pp → FAIL); root cause is the custom switch-cost + DARF
book-keeping that vectorbt's `from_orders` cannot replicate exactly.

PBO **0.413** passes the rota B threshold of 0.5 (gate 11 HARD → PASS)
but is high — the 6 grid cells (4 lookbacks × 2 feeds + 1 SSO) cluster
closely in Sharpe-full (0.22-0.58), suggesting the signal does "work
weakly" across variants but without a decisive winner. OOS IR vs SPY
buy-hold = **−0.24** (gate 8 ≥ 0.2 → FAIL): **SPY buy-hold in 2019-2022
beats the rotation by +5.8 pp CAGR** (13.1% vs 7.3%) while carrying a
similar 33.7% MDD — the rotation saves nothing on the drawdown side and
gives up alpha on the upside.

**Bozović 2024 and the Cboe consensus paper ARE real edges in the
literature**, but the reduced-form VIXY-trailing-return proxy does not
preserve the edge under rota B costs + DARF. The halt contract is not
triggered (regime is 70/30 on/off, not degenerate) but the strategy is
clearly non-winner.

**Mandate §7 and strategy docs stay UNTOUCHED.** FAIL = no promotion,
no pending draft.

## Top-line metrics

| Split | Bars | Sharpe | CAGR | MaxDD |
|-------|-----:|-------:|-----:|------:|
| IS  (2011-01-04 → 2018-12-31)   | 2011 |  0.531 |  6.01% | −24.69% |
| **OOS** (2019-01-01 → 2022-12-31) | **1008** | **0.480** | **7.32%** | **−34.32%** |
| FWD (2023-01-01 → 2026-04-14)   |  822 |  0.724 |  9.45% | −15.82% |
| FULL (2011-01-04 → 2026-04-14)  | 3841 |  0.546 |  7.08% | −34.32% |
| **SPY OOS buy-hold benchmark**  | 1008 |  0.660 | 13.10% | −33.70% |

Portfolio OOS underperforms SPY buy-hold by **−5.78 pp CAGR** with
roughly matching drawdown — the VIX regime filter **did not protect
capital in 2022** as the term-structure implied it would. Closer look:
the 70% long / 30% off regime mix produced drag-heavy switch costs
(312 switches over 15 years → ~21/year, each costing ~5 bps + DARF
realized gain) that ate the diversification benefit. Cumulative cost
drag **29.4 %** of equity + cumulative DARF **74.6 %** of equity over
full period (DARF is dominant — every RISK_ON → RISK_OFF transition
realizes the 15% tax hit).

## Winner config

```python
H2VixTermConfig(
    lookback              = 21,      # trading days on VIXY trailing return
    signal_feed           = "VIXY",  # VIXY (2011+) vs VXX (2009+)
    long_asset            = "SPY",   # 1x SPY as canonical
    off_asset_return      = "TLT",   # bond off-leg
    sso_expense_annual    = 0.0091,  # used only for SSO variant
    commission_bps        = 0.0,     # Inter USD brokerage
    spread_bps            = 5.0,     # 5 bps round-trip
    tax_rate              = 0.15,    # 15% DARF BR rota B
    threshold             = 0.0,     # pure sign rule on VIXY trailing return
)
```

**Signal rule.** At close(t-1):
`vixy_21d_ret[t-1] = VIXY[t-1]/VIXY[t-1-21] - 1`
`regime[t] = 1 if vixy_21d_ret[t-1] <= 0 else 0`.
Apply `prev_weight × ret` (F2 alignment). Daily rebalance at close; swap
= 0 because both SPY and TLT are cash ETFs on Inter Intl (no CFD).

## 13-gate checklist (rota B per mandate §2.4)

| # | Gate | Level | Threshold | Value | Pass |
|---|------|:-----:|-----------|------:|:----:|
| 1   | IS Sharpe > 0.5                                 | soft    | > 0.5   | 0.531 | **PASS** |
| 2   | OOS Sharpe ≥ 1.3                                | soft    | ≥ 1.3   | 0.480 | **FAIL** |
| 3   | OOS CAGR tier (rota B)                          | warning | classify | 7.32% → **Folclore** | WARN |
| 4   | OOS MaxDD tier (rota B)                         | warning | classify | −34.32% → **Marginal** | WARN |
| 5   | FWD Sharpe > 0                                  | soft    | > 0     | 0.724 | **PASS** |
| 6   | Walk-forward 6/8 profitable                     | soft    | ≥ 6/8   | 7/8  mdd=32.12% | **PASS** |
| 7   | Median risk-on block ≥ 5 days                   | soft    | ≥ 5d    | 5.0d | **PASS** |
| 8   | IR vs SPY buy-hold OOS ≥ 0.2                    | soft    | ≥ 0.2   | −0.241 | **FAIL** |
| 9   | Cross-lib concordance ±3 pp OOS CAGR            | **hard** | ≤ 3 pp | 3.04 pp (vbt vs pandas) | **FAIL** |
| 10  | Bootstrap OOS 99.9% CI low > 0                  | **hard** | > 0     | −1.14 | **FAIL** |
| 10b | Bootstrap FULL 99.9% CI low > 0                 | **hard** | > 0     | −0.26 | **FAIL** |
| 11  | PBO < 0.5 (rota B)                              | **hard** | < 0.5   | 0.4127 | **PASS** |
| 12  | DSR p < 0.05                                    | **hard** | < 0.05  | 0.633 | **FAIL** |
| 13  | Cost×2 OOS Sharpe > 1.0 (1x SPY base)           | soft    | > 1.0   | 0.246 | **FAIL** |

**Hard gate summary:** 1/5 pass (PBO only). Gate 9 fails by a razor-
thin 0.04 pp — the vectorbt port of the strategy uses
`Portfolio.from_orders` with target-percent rebalancing and does NOT
replicate the DARF realization logic; we therefore treat the 3.04 pp
delta as *implementation-artifact* driven rather than a true alignment
bug, BUT the gate still FAILS per the letter of the rule. See halt-
contract audit below.

**Soft gate summary:** 3 of 9 fail. Gates 5/6/7 pass (strategy does
survive the post-2023 bond-rout forward window; walk-forward is 7/8
positive; holds are cleanly weekly).

## Grid sensitivity (6 configs)

| Tag | Lookback | Feed | Long | Off | Sharpe full |
|-----|---------:|:----:|:----:|:---:|------------:|
| lb10_vixy_spy  | 10 | VIXY | SPY | TLT | 0.225 |
| **lb21_vixy_spy (winner)** | **21** | **VIXY** | **SPY** | **TLT** | **0.546** |
| lb42_vixy_spy  | 42 | VIXY | SPY | TLT | 0.423 |
| lb63_vixy_spy  | 63 | VIXY | SPY | TLT | 0.344 |
| lb21_vxx_spy   | 21 | VXX  | SPY | TLT | 0.465 |
| lb21_vixy_sso  | 21 | VIXY | SSO | TLT | 0.585 |

Lookback 21 wins on Sharpe_full across both feeds. VXX underperforms
VIXY on same lookback by 0.08 pp Sharpe — VIXY's smoother ~1-month
futures basket is modestly better than VXX's front-month roll (both
bleed under contango, VXX more so). SSO variant is highest Sharpe_full
but only marginally (0.585 vs 0.546) — the 2x leverage doesn't add
meaningful edge and would carry SSO's 0.91% annual expense drag.

## Bootstrap 99.9% CI (stationary block, Politis-Romano 1994, block_mean=5)

- **OOS Sharpe 99.9% CI = [−1.14, 2.07]** — straddles zero by a wide
  margin. Gate 10 HARD fails.
- **FULL Sharpe 99.9% CI = [−0.26, 1.29]** — ditto. Gate 10b HARD fails.
- Interpretation: the observed OOS Sharpe 0.480 is well inside the
  noise band; a replicate universe under the same DGP could easily
  return a Sharpe of −1 or +2. The signal is statistically
  **indistinguishable from a coin-flip rotation** at the 99.9%
  confidence level.

## Cross-lib concordance (vectorbt 0.28.5)

- status = **ok**, n common days = 1008
- ref (pandas) OOS CAGR = 7.32%
- vbt OOS CAGR = 10.36% (approx; vbt cannot replicate DARF book-keeping)
- **Δ CAGR = 3.04 pp (HARD FAIL; threshold ≤ 3.0 pp)**

The 3.04 pp gap is almost entirely **DARF-realization artifact**:
vectorbt's `from_orders` path does not simulate the BR-specific 15%
tax on RISK_ON-exit profits, so the vbt equity curve is ~3 pp CAGR
higher OOS than the reference. **This is expected divergence, not
an engine bug** — but the gate is binary and we report it honestly as
FAIL.

## Degenerate-regime audit (halt contract)

- Fraction risk-on = **70.04%** over 3841 full-period bars.
- Fraction risk-off = 29.96%.
- 312 regime switches (median on-block = 5.0 days).
- NOT degenerate (threshold was ≤ 2% OR ≥ 98% to trigger halt). **Halt
  not triggered.**

## Cost dissection (rota B Inter)

- Cumulative switch cost drag over full period = **29.4 %** of equity.
- Cumulative DARF drag = **74.6 %** of equity (7,463 bp over 15y ≈ 4.9
  % /yr realized-gain tax drag).
- Combined = ~7 % /yr in drag — this alone would consume Sharpe 0.5
  portfolio into Sharpe ~0.1 net-of-all-frictions.
- **Conclusion on rota B:** the strategy fundamentally does not have
  enough gross edge to survive rota B's DARF realization cadence. Under
  a no-DARF (Pepperstone-style) cost model it would be materially
  better but still fails gate 2 OOS Sharpe ≥ 1.3.

## Honest interpretation

The Phase 3.7-1 literature sprint entry for Bozović 2024 (IRFA v95
Part A) documented the paper as "prior ALTO, fit Pepperstone"; this
H2.c hunt tests a **reduced-form proxy** (VIXY trailing return) rather
than the paper's native VIX-spot-scaling mechanism. The reduced form
preserves neither the Sharpe nor the alpha the paper reports. Two
interpretations are mutually consistent with FAIL here:

1. **The proxy is too weak** — VIXY is a roll-decay-heavy ETF; its
   trailing return is dominated by roll yield in contango and by jump-
   responsive VIX spikes in backwardation. The sign rule
   over-emphasizes short backwardation episodes (where VIXY has just
   jumped up) as risk-off, missing the fact that the *following weeks*
   are usually strong risk-on (post-VIX spike mean reversion).
2. **The edge was cost-sensitive in the paper** — Božović 2024 reports
   "with transaction costs, improvement becomes substantial" but the
   cost model in the paper is not BR-DARF-aware. Applying 15% DARF on
   every realized RISK_ON-exit gain eats the edge.

**Recommendation to Phase 3.7-3 lead:** before abandoning the VIX-
filter family, H2.a (Božović's native VIX-spot scaling of SPX factor
exposure) is the stronger implementation and should be tested
separately — the T2.Paper1 entry gives the algebra for it.

## Files produced

- `AGGREGATE.json` — gate table + splits + grid + bootstrap + cross-lib.
- `daily_returns_winner.parquet` — winner daily net returns.
- `daily_returns_cost2x.parquet` — cost×2 sensitivity daily returns.
- `config_grid.csv` — 6-cell grid with Sharpe_full per cell.

## Sign-off

- **Gates hard-block remaining failed:** 4 (gates 9, 10, 10b, 12).
- **Per mandate §2.4:** PASS requires all hard gates. This strategy is
  **non-winner**, no promotion, no pending draft. Mandate, existing
  strategies, and frozen files UNTOUCHED.
- **Next-step recommendation:** recommend H2.a (Božović native VIX-spot
  scaling) before closing the T2 family; if H2.a also fails, the
  T2 family can be closed and effort redirected to H3 (Donchian
  crypto) or H4 (confidence-weighted meta-layer).
