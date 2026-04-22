# Phase 3.7 H3.b — ETH Donchian ensemble independent signal (honest validation)

**Date:** 2026-04-22 | **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched `prev_weight × ret` alignment `[advances_fin_ml, p.31-34]`
**Broker path modelled:** Pepperstone ETHUSD CFD, rota A — spread **6 bps
per side** one-way (conservative center of 5-8 bps range for ETH),
commission **0** (crypto CFD), swap long **−0.0556%/day** (≈ −20%/yr),
swap short **+0.02083%/day** (≈ +7.5%/yr credit), leverage cap **2:1**
(Pepperstone retail crypto), **no DARF** per mandate §2.2 rota A +
`feedback_pepperstone_staging_and_darf.md`.
**Windows:** IS 2016-01-01 → 2020-06-30 (4.5y, 1637 crypto-bars) |
OOS 2020-07-01 → 2023-06-30 (3y, 1095 crypto-bars) |
FWD 2023-07-01 → 2026-04-14 (2.75y, 1018 crypto-bars).
Crypto trades 7 d/wk → 365 periods/yr annualization.
**Data source:** Tiingo ETH daily, 3882 bars 2015-08-08 → 2026-04-14
(`data/tiingo/daily/prices/ethusd.parquet`). Cross-validated vs Kraken
within 50bps per Phase 3.7-2 data sprint §6.

## Verdict: **FAIL**

The H3.b ETH Donchian ensemble independent signal **fails the explicit
halt condition (OOS n_trades = 45 < 50)**, and separately fails **2 of 4
hard gates + 3 of 9 soft gates** under the honest engine + Pepperstone
rota A cost model. OOS Sharpe collapses from a suspiciously stellar IS
**1.684** down to **0.659** — far below the ≥ 1.3 gate 2 soft target.
DSR p-value = **0.714** (gate 12 HARD < 0.05 → FAIL): the observed
OOS Sharpe is statistically indistinguishable from the noise-floor of
12 sibling configurations, even with `n_trials = 12`. The OOS 99.9%
bootstrap CI on Sharpe spans **[−1.33, +2.23]** — crosses zero by a
huge margin (gate 10 HARD → FAIL). Buy-and-hold ETH in the OOS window
annualizes Sharpe **1.25** vs our signal at **0.66**, producing
**IR = −1.23** against ETH BH (gate 8 ≥ 0.2 → FAIL) — the independent-
per-asset Donchian signal is **worse than doing nothing** in OOS crypto.
Median hold is exactly **2 days** (time-stop dominates ATR trail →
gate 7 PASS but exit rule is structurally time-bound, not trend-bound).

**Positive signals (narrow):** cross-lib concordance **passes**
(vectorbt vs pandas ref Δ = 0.44 pp OOS CAGR, gate 9 HARD < 3pp →
PASS). PBO passes (0.17 < 0.5). FULL bootstrap CI low = 0.16 > 0 (gate
10b PASS). WF 7/8 profitable (gate 6 PASS). FWD Sharpe 1.02 (gate 5
PASS). **None of these salvage the DSR + OOS-bootstrap + IR failures,
and the halt trigger is definitive.**

**Mandate §7 and frozen files stay UNTOUCHED.** FAIL = no promotion,
no pending draft in `docs/.pending/`.

**Next-step recommendation:** The signal is statistically indistinguishable
from noise in the OOS crypto regime (2020-07 → 2023-06). Two avenues
remain: (a) **drop H3.b entirely** — Pepperstone BTC+ETH adaptation of
Zarattini-Pagani-Barbon 2025 cannot replicate cross-sectional top-20
rotation edge with N=2 fixed, per Phase 3.7-2 §6.3 warning; (b) **widen
universe to venue-side** (if ever a broker offers top-10 crypto CFDs),
out of scope for this hunt. H3.a BTC sibling is being validated in
parallel — if BTC also fails, **H3 family is dead**.

## Top-line metrics

| Split | Bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-----:|-------:|-----:|------:|-------------:|
| IS  (2016-01-01 → 2020-06-30)  | 1637 | **1.684** | **14.01%** | −7.94% | 1.731 |
| **OOS** (2020-07-01 → 2023-06-30) | **1095** | **0.659** | **3.63%** | **−4.64%** | **1.113** |
| FWD (2023-07-01 → 2026-04-14)  | 1018 |  1.023 |  3.95% | −2.17% | 1.113 |
| FULL (2015-08-08 → 2026-04-14) | 3864 |  1.200 |  7.02% | −9.79% | 2.136 |
| **ETH OOS buy-hold benchmark** | **1095** | **1.253** | **48.45%** | −79.64% | 3.266 |

Portfolio OOS underperforms ETH buy-hold by **−44.8 pp CAGR**. Even
accounting for ETH BH's catastrophic **−79.6% MaxDD** (which our signal
avoids — MDD only −4.64%), the risk-adjusted picture still favors buy-
hold by a large margin (ETH BH Sharpe **1.25** vs our **0.66**, IR
= **−1.23**). This is the classic "trend-following on buy-and-hold asset
with strong bull trend in OOS" trap — the signal sits flat during the
2020-2021 bull run, then trades on whipsaw during the 2022 bear, eating
2-day time-stops in both regimes.

## Winner config (best IS Sharpe, no OOS peek)

```python
H3EthDonchianConfig(
    donchian_lookbacks   = (20, 40, 80),   # ensemble, slow (Turtle N=20 + 2x + 4x)
    atr_period           = 20,              # Wilder ATR (Penfold p.338-343)
    atr_multiplier       = 2.0,             # canonical 2·ATR trail
    time_stop_days       = 2,               # hunt prompt H3.b ≤ 2d swap-budget
    risk_per_trade       = 0.010,           # 1% per-trade (literal prompt formula)
    max_leverage         = 2.0,             # Pepperstone retail crypto cap
    spread_one_way       = 6.0e-4,          # 6 bps (ETHUSD mid of 5-8)
    commission_round_trip = 0.0,            # crypto CFD commission-free
    swap_daily_long      = -5.556e-4,       # -0.0556%/d (-20%/yr)
    swap_daily_short     = 2.083e-4,        # +0.0208%/d (+7.5%/yr credit)
    tax_rate             = 0.0,             # no DARF rota A
    allow_short          = True,            # bidirectional
)
```

**Winner picked by best IS Sharpe** over a 18-cell sweep
(risk ∈ {0.5%, 1.0%, 1.5%} × lookback-sets ∈ {(5,10,20), (10,20,40),
(20,40,80)} × atr_multiplier ∈ {2.0, 3.0}). No OOS peek. The (20,40,80)
slow-Donchian ensemble consistently gave the highest IS Sharpe across
all risk levels (1.68 → 1.71), reflecting the 2016-2020 IS regime's
preference for slower, lower-frequency breakouts (fewer whipsaws in
ETH's 2018 bear). Risk level is scale-linear in CAGR but neutral on
Sharpe — 1% is the canonical middle.

**Size-cap utilization.** At risk=1% and ETH volatility ~3-6%/day, the
raw weight `0.01 × price / ATR` ≈ 16% avg (1st decile 3%, 9th decile
32%), well below the 200% cap → leverage cap is rarely binding in practice
(sizing is ATR-bound, not leverage-bound).

## 13-gate scoreboard (rota A, Pepperstone CFD ETHUSD)

| # | Gate | Level | Value | Verdict |
|--:|------|:------|------:|:-------:|
| 1 | IS Sharpe > 0.5 | soft | 1.684 | **PASS** |
| 2 | OOS Sharpe ≥ 1.3 | soft | 0.659 | **FAIL** |
| 3 | OOS CAGR tier rota A | warning | 3.63% → **Folclore** | WARN |
| 4 | OOS MDD tier rota A | warning | −4.64% → **Excelente** | WARN |
| 5 | FWD Sharpe > 0 | soft | 1.023 | **PASS** |
| 6 | Walk-forward 6/8 profitable | soft | 7/8 (max_win_mdd 7.38%) | **PASS** |
| 7 | Median hold 1-2d (swap-compat) | soft | 2.0 d | **PASS** |
| 8 | IR vs ETH BH ≥ 0.2 | soft | −1.2254 | **FAIL** |
| 9 | Cross-lib concordance ±3pp CAGR | **hard** | Δ = 0.443 pp | **PASS** |
| 10 | Bootstrap OOS 99.9% CI low > 0 | **hard** | [−1.33, +2.22] | **FAIL** |
| 10b | Bootstrap FULL 99.9% CI low > 0 | **hard** | [+0.16, +2.06] | **PASS** |
| 11 | PBO < 0.5 | **hard** | 0.167 (n_combos=252) | **PASS** |
| 12 | DSR p < 0.05 | **hard** | 0.7139 | **FAIL** |
| 13 | cost×2 Sharpe > 0.8 (leveraged) | soft | 0.560 | **FAIL** |

**Plus halt trigger:** OOS n_trades = **45 < 50** → explicit FAIL per
hunt prompt halt contract. Recommendation in plan: widen universe →
**already executed** (we use the widest Tiingo ETH daily window
available, 2016-2026, so the halt signals "signal is too selective
for the gate calendar" not "data is scarce"). The structural issue is
the **slow Donchian ensemble (20,40,80)** + **2-day time-stop** — with
OOS having only 3 years and the slow breakouts rare, hitting 50 OOS
trades would require loosening lookbacks to (5,10,20), which lost IS
Sharpe (1.14 vs 1.68) — the ensemble-strength/trade-count tradeoff
blocks both paths.

## Data & audits

* **Look-ahead audit:** Donchian bands use `rolling(N).max/min()` on
  `high`/`low` with `.shift(1)` (strictly prior-bar data). ATR uses
  Wilder EWM on TR(t-1) with `.shift(1)`. Entry/exit tested at
  `close_t` against bands defined by t-1 data. Daily-return alignment
  = `prev_weight × ret` (`weights.shift(1).fillna(0.0)`) per
  `[advances_fin_ml, p.31-34]`. F2 patch preserved.
* **Cost accounting:** `cum_spread_pct = 3.15%` cumulative over 10.6y,
  `cum_swap_pct = 2.24%` cumulative, `cum_commission_pct = 0%` (CFD).
  Swap applied DAILY on absolute prior-bar weight, sign-aware (short
  credit offsets long debit).
* **Crypto 7d/wk:** weekend bars treated as real bars, confirmed by
  28.5% Sat/Sun fraction in ETH feed (Phase 3.7-2 §6 integrity).
* **Cross-lib:** vectorbt Portfolio.from_signals with boolean entries
  derived from weight-direction transitions. OOS CAGR: pandas ref
  3.63%, vectorbt 3.19%, Δ = **0.44 pp** (< 3pp gate 9 target).

## Sensitivity grid (12 configs, used for PBO + DSR)

| tag | lookbacks | atr_k | ts | risk | allow_short | Sharpe_full |
|---|---|--:|--:|---:|:-:|--:|
| r10_lb20-40-80_k2 (winner) | (20,40,80) | 2.0 | 2 | 0.010 | ✅ | 1.200 |
| r10_lb20-40-80_k3 | (20,40,80) | 3.0 | 2 | 0.010 | ✅ | 1.215 |
| r10_lb10-20-40_k2 | (10,20,40) | 2.0 | 2 | 0.010 | ✅ | 1.016 |
| r10_lb10-20-40_k3 | (10,20,40) | 3.0 | 2 | 0.010 | ✅ | 1.030 |
| r10_lb5-10-20_k2 | (5,10,20) | 2.0 | 2 | 0.010 | ✅ | 0.803 |
| r10_lb5-10-20_k3 | (5,10,20) | 3.0 | 2 | 0.010 | ✅ | 0.816 |
| r5_lb20-40-80_k2 | (20,40,80) | 2.0 | 2 | 0.005 | ✅ | 1.200 |
| r15_lb20-40-80_k2 | (20,40,80) | 2.0 | 2 | 0.015 | ✅ | 1.200 |
| r10_lb20-40-80_k2_nshort | (20,40,80) | 2.0 | 2 | 0.010 | ❌ | 1.269 |
| r10_lb10-20-40_k2_nshort | (10,20,40) | 2.0 | 2 | 0.010 | ❌ | 1.176 |
| r10_lb20-40-80_k2_ts3 | (20,40,80) | 2.0 | 3 | 0.010 | ✅ | 0.991 |
| r10_lb20-40-80_k2_ts5 | (20,40,80) | 2.0 | 5 | 0.010 | ✅ | **1.392** |

Interesting: loosening the time-stop to 5 days (ts=5) gives the highest
Sharpe_full (1.39) — implying the 2-day prompt cap is costing us. Still,
even 1.39 Sharpe_full is pedestrian vs ETH buy-hold 1.25; and **OOS
validation of the 5-day variant is not a winner-eligible path** because
it violates the hunt-prompt swap-budget hard cap (≤ 2 days).

## Citation index

* `[zarattini_pagani_barbon_2025]` — Zarattini, Pagani, Barbon 2025 SSRN
  5209907 — base paper (rotational top-20 crypto, here reformulated as
  per-asset independent Donchian).
* `[universal_trend_tactics, p.295-299]` — Donchian / Turtle System
  channel breakout N=20 benchmark.
* `[universal_trend_tactics, p.338-343]` — Wilder ATR trailing stop,
  the canonical cut-losses-short exit.
* `[universal_trend_tactics, p.291]` — fixed-fraction risk-per-trade
  sizing.
* `[advances_fin_ml, p.31-34]` — F2-patched `prev_weight × ret`
  alignment audit.
* `[advances_fin_ml, p.196-202]` — Politis-Romano stationary bootstrap
  (block_mean=5, n=2000, α=0.001).
* `[advances_fin_ml, p.208-211, p.275]` — CSCV PBO + DSR under multiple-
  testing.
* `docs/investment-mandate.md §2.4` — 13-gate framework + hard-block list.
* `docs/investment-mandate.md §3.1` — Pepperstone rota A cost model.
* `feedback_pepperstone_staging_and_darf.md` — no-DARF on Pepperstone
  per user decision 2026-04-22.
* `docs/research/2026-04-23-phase3.7-2-data-sprint.md §6.3` —
  independent-per-asset adaptation rationale (Pepperstone BTC+ETH only).

## Artifacts persisted

* `reports/phase_3_7/h3_eth_donchian/AGGREGATE.json` — full numeric payload.
* `reports/phase_3_7/h3_eth_donchian/AGGREGATE.md` — this document.
* `reports/phase_3_7/h3_eth_donchian/daily_returns_ETH.parquet` — winner
  net daily returns, full period.
* `reports/phase_3_7/h3_eth_donchian/daily_returns_cost2x.parquet` —
  cost×2 sensitivity returns.
* `reports/phase_3_7/h3_eth_donchian/config_grid.csv` — 12-cell grid.
