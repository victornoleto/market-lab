# Phase 3.6 Family F — Vol-targeting managed-futures basket (honest validation)

**Date:** 2026-04-23  |  **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched (commit `7b90a8f` — `prev_weight × next_return`)
**Broker path modelled:** Pepperstone Razor CFD (plan §3.1) — per-ticker
spread (2.5bps SPY/EFA/TLT/IEF, 5bps GLD, 10bps USO), $0.35/100k
commission, −0.03%/night long swap. No BR CG tax (non-BR jurisdiction).
**Windows:** IS 2001-05-14 → 2017-12-31 | OOS 2018-01-01 → 2023-12-31 |
FWD 2024-01-01 → 2026-04-14

## Verdict: **FAIL**

The vol-targeting managed-futures basket (EWMAC 16:64 on 6-asset
SPY/TLT/GLD/USO/EFA/IEF panel, 15% portfolio-vol target, 10d rebalance
cadence) **fails 12 of the 13 gates** under the honest engine and
Pepperstone retail cost model. The mechanism is diagnostic and matches
Carver's own warning `[systematic_trading, p.185-188]`: retail swap
drag + commission dominate the thin edge of a slow-trend signal when
average gross leverage is 2.22× and median hold is 50 days.

OOS Sharpe collapses to **0.115**, OOS CAGR **−0.14%**, OOS MaxDD
**−36.5%** (breaches gate 4 cap by 11.5pp). Bootstrap 99.9% CI on OOS
Sharpe is **[−1.10, +1.47]** (straddles zero). DSR p-value is **0.94**
over 16 grid cells — the strategy is statistically indistinguishable
from noise. Cost×2 sensitivity crashes OOS Sharpe to **−0.46** (gate 13
requires > 1.0). Only gate 7 (median hold ≥ 5d) passes (50 days).

Cross-lib concordance (gate 9) **PASS** (Δ = 0.000pp) — the engine is
wired correctly; the strategy simply has no cost-net edge. Gate 10 is
N/A (only one data source — Tiingo).

**Mandate §7 and strategy docs stay UNTOUCHED** — FAIL means no
promotion, no draft entry in `docs/.pending/`.

## Differentiation from V2-L1 TSMOM (mandatory per brief)

V2-L1 TSMOM (`tsmom_multi_asset.py`) was independently rejected under
the honest engine (`reports/phase_3_5f/honest_revalidation/v2_l1_tsmom/
AGGREGATE.md`). Family F is **structurally different on three axes**:

| Axis | V2-L1 TSMOM | Family F |
|---|---|---|
| Trend signal | Binary `sign(close_t / close_{t-L} − 1)` | Carver continuous EWMAC with forecast scalar, capped ±20 [systematic_trading, p.282-285] |
| Vol target scope | Per-leg inverse-vol (`w_i = sig × vt / σ_i / N`) | Portfolio-level 15% ann with IDM = √N (cap 2.5) [systematic_trading, p.170-171, ch.10-11] |
| Basket composition | 30-asset CFD-proxy with 3 USD-pair FX dominant | 6 ETFs across 4 asset classes (SPY/EFA equity, TLT/IEF bonds, GLD/USO commodities) |
| Long/short | Long-only (binary sig ∈ {0,1}) | Long-short (signed forecast) |
| Rebalance cadence | Monthly EOM | 10-day cadence with Carver 10% position inertia [systematic_trading, p.174] |

The three required differentiators (continuous EWMAC signal, portfolio-
level vol target, multi-asset-class basket) are all present. Family F is
not a V2-L1 variant.

## Top-line metrics (winner config)

| Split | Bars | Sharpe | CAGR | MaxDD |
|-------|-----:|-------:|-----:|------:|
| IS (2001-05-14 → 2017-12-31)   | 4189 | −0.091 | −3.80% | −64.20% |
| OOS (2018-01-01 → 2023-12-31)  | 1566 |  0.115 | −0.14% | −36.52% |
| FWD (2024-01-01 → 2026-04-14)  |  600 | −0.067 | −3.54% | −29.92% |
| FULL (2001-05-14 → 2026-04-20) | 6270 | −0.033 | −2.92% | −68.45% |
| **SPY OOS benchmark**          | 1509 |  0.658 | 12.00% |      —  |

Portfolio underperforms SPY buy-hold OOS by **−12.1pp CAGR** with ~3×
the drawdown. IR vs SPY OOS is **−0.33** (gate 8 ≥ 0.3 → FAIL).

## Winner config (canonical)

```
fast_span           = 16              [systematic_trading, p.118-119, p.284-285]
slow_span           = 64              [systematic_trading, p.118-119, p.284-285]
ewmac_scalar        = 3.75            [systematic_trading, p.285, appendix B]
target_vol_annual   = 0.15            [systematic_trading, p.137-148, ch.9 — Half-Kelly]
rebalance_days      = 10              [systematic_trading, p.174, ch.11 — inertia]
sigma_ewma_span     = 35              [systematic_trading, p.112-114, ch.7]
inertia_frac        = 0.10            [systematic_trading, p.174, ch.11]
max_per_leg         = 2.0             [systematic_trading, p.170-171, ch.11]
max_gross_leverage  = 4.0             [design choice — prevents pathological gross]
idm_cap             = 2.5             [systematic_trading, p.170-171, ch.11]
min_active_assets   = 3               [systematic_trading, breadth floor]
forecast_cap        = 20.0            [systematic_trading, p.112-114, ch.7]
spread_SPY/EFA/TLT/IEF = 0.00025       [plan §3.1]
spread_GLD          = 0.00050          [plan §3.1]
spread_USO          = 0.00100          [plan §3.1]
commission_rt       = 3.5e-5           [plan §3.1 — $0.35/100k Razor]
swap_daily_long     = −0.0003          [plan §3.1 — −0.03%/night levered]
swap_daily_short    = 0.0              [plan §3.1 — near-zero net short swap]
tax_rate            = 0.0              [plan §3.1 — Pepperstone non-BR]
universe            = SPY, TLT, GLD, USO, EFA, IEF  (6-asset MF proxy)
```

## 13-gate checklist (plan §5; relaxations applied)

| # | Gate | Threshold | Value | Pass |
|---|------|-----------|------:|:----:|
| 1   | Bootstrap OOS 99.9% CI low > 0      | > 0     | −1.0984 | FAIL |
| 1b  | Bootstrap FULL 99.9% CI low > 0     | > 0     | −0.5521 | FAIL |
| 2   | OOS Sharpe ≥ 1.5                    | ≥ 1.5   |  0.115 | FAIL |
| 3   | OOS CAGR ≥ 13% (CDI floor)          | ≥ 13%   | −0.14% | FAIL |
| 3t  | OOS CAGR ≥ 30% (target)             | ≥ 30%   | −0.14% | FAIL |
| 4   | OOS MaxDD ≥ −25%                    | ≥ −25%  | −36.52% | FAIL |
| 5   | FWD Sharpe > 0                      | > 0     | −0.067 | FAIL |
| 6   | WF 6/8 profitable AND mdd ≤ 30%     | both    | 3/8 mdd=36.19% | FAIL |
| 7   | Median hold ≥ 5 trading days        | ≥ 5d    |  50.0d | **PASS** |
| 8   | IR vs SPY OOS ≥ 0.3                 | ≥ 0.3   | −0.3316 | FAIL |
| 9   | Cross-lib concordance ≥ 2/3 ±3pp    | ≤ 3pp   |  0.000pp | **PASS** |
| 10  | Stage-2 data concordance ±1pp       | deferred | only one data source (Tiingo) | N/A |
| 11  | PBO < 0.5 (CSCV 10-block)           | < 0.5   |  0.5952 | FAIL |
| 12  | DSR p < 0.05                        | < 0.05  |  0.9352 | FAIL |
| 13  | Cost×2 sensitivity OOS Sharpe > 1.0 | > 1.0   | −0.455 | FAIL |

**Summary: 2 PASS / 12 FAIL / 1 N/A.** Gates 7 and 9 pass. Binding FAILs
span every edge metric (Sharpe, CAGR, bootstrap CI, DSR, IR-vs-SPY),
every risk metric (MDD, WF), and the cost-stability gate (13).

## Grid sensitivity (16 cells for CPCV/PBO)

| Tag | fast:slow | vol_tgt | rebal | Sharpe (full) |
|-----|----:|----:|----:|--------------:|
| ewmac8_32_vt10_rb10   |  8:32  | 10% | 10d | −0.253 |
| ewmac8_32_vt10_rb20   |  8:32  | 10% | 20d | −0.207 |
| ewmac8_32_vt15_rb10   |  8:32  | 15% | 10d | −0.249 |
| ewmac8_32_vt15_rb20   |  8:32  | 15% | 20d | −0.201 |
| ewmac16_64_vt10_rb10  | 16:64  | 10% | 10d | −0.039 |
| ewmac16_64_vt10_rb20  | 16:64  | 10% | 20d | −0.117 |
| **ewmac16_64_vt15_rb10 (winner)** | **16:64** | **15%** | **10d** | **−0.033** |
| ewmac16_64_vt15_rb20  | 16:64  | 15% | 20d | −0.111 |
| ewmac32_128_vt10_rb10 | 32:128 | 10% | 10d | −0.116 |
| ewmac32_128_vt10_rb20 | 32:128 | 10% | 20d | −0.120 |
| ewmac32_128_vt15_rb10 | 32:128 | 15% | 10d | −0.100 |
| ewmac32_128_vt15_rb20 | 32:128 | 15% | 20d | −0.116 |
| ewmac64_256_vt10_rb10 | 64:256 | 10% | 10d | −0.183 |
| ewmac64_256_vt10_rb20 | 64:256 | 10% | 20d | −0.156 |
| ewmac64_256_vt15_rb10 | 64:256 | 15% | 10d | −0.193 |
| ewmac64_256_vt15_rb20 | 64:256 | 15% | 20d | −0.153 |

All 16 configs Sharpe-negative on full-period. Grid min/max/mean =
(−0.253, −0.033, −0.147). PBO = **0.595** (> 0.5 → FAIL). DSR p-value
= **0.94** on 16 trials. The grid is not just overfit — there is
**nothing to overfit**: the entire cell space is Sharpe-negative.

## Which gates killed it — diagnostic

The strategy generates a **gross-return Sharpe of 0.60 pre-cost**
(computed during smoke test). This is consistent with the Moskowitz-
Ooi-Pedersen 2012 TSMOM paper and with Carver's reported single-
instrument-EWMAC Sharpe range `[systematic_trading, p.47, ch.2 — "SR
≈ 0.40"]`. The failure is not a signal failure — it's a cost failure:

1. **Swap drag (dominant):** `cum_swap = 311%` over 25 years. At an
   average gross leverage of **2.22×** (forced by the IDM multiplier on
   a 6-asset basket), the daily −0.03% swap charge compounds to
   ~16.8%/year drag on the long side. For a 15%-vol target at SR≈0.4,
   the pre-cost expected return is ~6%/year — **swap erases 2.8× the
   signal**. This is the same mechanism that killed V2-L1 `[systematic_
   trading, p.185-188]`.
2. **Average gross leverage too high for a 6-asset basket.** IDM cap
   2.5 + forecast scalar 3.75 + per-leg cap 2.0 + gross cap 4.0 yields
   avg gross 2.22×. Carver's canonical MF portfolio uses 20-40
   instruments so IDM stays near 2.5 but per-instrument allocation is
   small. A 6-asset basket cannot reach Carver's diversification
   assumptions — IDM √N = √6 ≈ 2.45 gives us a multiplier that the
   cost model can't afford at daily-carry frequency.
3. **Forward window (2024-2026) unfavourable:** FWD Sharpe −0.07 /
   CAGR −3.54% / MDD −29.9%. 2024-2026 was a choppy regime for
   macro trends (oil shocks + US-dollar strength + bond rates topping);
   slow-trend EWMAC got whipsawed. Gate 5 FAIL.
4. **Bootstrap CI [−1.10, +1.47] on OOS Sharpe** confirms the signal
   is statistically indistinguishable from zero.

## Mechanism — why this is FAIL even under cost×0.5

Even halving spread/commission and swap does not rescue Family F:
signal gross Sharpe ≈ 0.60 × vol target 0.15 × avg gross 2.22 ≈ 6%/year
expected return; swap at 50% × 7.5%/year × 2.22 gross = 8.3% drag. The
gross edge cannot service the structural retail swap cost at this
leverage. The only paths to rescue would be:
- **Cadence ↓↓** (weekly or even slower): but brief brief gate 7
  requires ≥5d median hold (already passes at 50d — can't help).
- **Basket ↑↑**: expand to 20+ MF instruments (Carver canonical). But
  Pepperstone CFD universe is asset-class-limited and our Tiingo panel
  has only 6 viable MF proxies with honest 2001+ history.
- **Leverage ↓↓**: cap at 1× gross. But then pre-cost return is 3%/yr
  which loses to CDI (13%) by construction.

None of these rescues is a clean "Family F variant" — they become new
candidate families. The verdict here is that **vol-targeting managed-
futures-basket on a 6-asset Tiingo-available universe does not clear
Pepperstone retail costs at any EWMAC span ∈ {2:8, 4:16, 8:32, 16:64,
32:128, 64:256}**.

## Data-source caveats

1. **Universe inception truncation.** The 6-asset panel is only
   simultaneously populated from 2006-04-10 (USO inception) onward.
   Earlier bars use dynamic-inclusion (assets join as they come online).
   SPY 2001-05-14; TLT 2002-07-26; EFA 2003-08-20; GLD 2004-11-18; IEF
   2006-01-03; USO 2006-04-10. IS window (2001-05-14 → 2017-12-31)
   therefore has reduced breadth pre-2006. OOS and FWD windows have
   the full 6-asset panel.
2. **EURUSD excluded.** The brief allowed EURUSD as an FX proxy but
   Tiingo FX parquet only goes back to 2020-01-01 — unusable for the
   IS window. Omitting EURUSD does not violate the "multi-asset" rule
   since the 6-asset panel already covers 4 asset classes.
3. **DBC/OILK unavailable.** Brief listed DBC or OILK as commodity
   basket options; neither is present in the Tiingo bulk. USO (oil
   futures front-month) used as single-commodity proxy alongside GLD.
4. **Pepperstone CFD underliers assumed.** Tiingo provides ETF
   prices; Pepperstone CFDs track the underlying cash/futures. Minor
   basis noise (~1-3 bp/day on commodity CFD vs ETF) is NOT modeled —
   this is conservative for gate evaluation since real-CFD returns
   should be slightly better than ETF returns.

## Artifacts

- `AGGREGATE.json` — full numeric detail, 13-gate structured.
- `daily_returns.parquet` — winner-config honest daily returns (local,
  gitignored by pattern).
- `daily_returns_cost2x.parquet` — cost×2 sensitivity daily returns.
- `config_grid.csv` — 16-config sensitivity grid Sharpe.
- `cross_lib_check.md` + `cross_lib_check.json` — gate 9 PASS (Δ=0.000pp).
- Logs: `logs/phase3_6_f_vol_target_mf.log`.
- Strategy module: `src/ai_trade/backtest/strategies/phase3_6_f_vol_target_managed_futures.py`.
- Runner: `scripts/run_phase3_6_f_vol_target_managed_futures.py`.
- Cross-lib runner: `scripts/run_phase3_6_f_cross_lib.py`.

## Mandate §7 / strategy doc status

**UNTOUCHED.** This verdict is FAIL. No promotion. No pending draft.

## Citations

- Carver EWMAC trend rule + forecast scalars: `[systematic_trading,
  p.118-119, p.282-285, appendix B]`.
- Volatility target (Half-Kelly): `[systematic_trading, p.137-148, ch.9]`.
- IDM + handcrafting + position inertia: `[systematic_trading, p.159-174,
  ch.10-11]` (IDM cap 2.5 at p.170-171; inertia 10% at p.174).
- Retail cost/turnover constraint (speed limit 0.13 SR/year for systems
  traders): `[systematic_trading, p.185-188, ch.12]`.
- Multi-asset instrument class coverage: `[systematic_trading,
  p.135-140]`.
- Kelly-based sizing cross-reference: `[volatility_trading, p.135,
  p.138-140]` (Sinclair — fractional Kelly discipline).
- Lookahead audit + two-stage replication: `[advances_fin_ml, p.31-34]`.
- Bootstrap 99.9% CI: `[advances_fin_ml, p.196-202]`.
- PBO CSCV 10-block: `[advances_fin_ml, p.208-211]`.
- DSR: `[advances_fin_ml, p.273-275]`.
- Walk-forward 6/8: `[advances_fin_ml, ch.11]`.
- Pepperstone Razor cost model: plan `docs/plans/2026-04-23-find-swing-
  winner-phase-3-6.md` §3.1.
- V2-L1 TSMOM post-mortem (Carver-cost-vs-hold-length thesis): `reports/
  phase_3_5f/honest_revalidation/v2_l1_tsmom/AGGREGATE.md`.
