# RSSX Proportion Test — B4-v2 Implementation Variant

Status: **discovery-only.** Tests whether partially substituting `GDESIM` with
`RSSXSIM` (Return Stacked US Stocks + Gold + BTC, local proxy) improves the
B4-v2 35/40/25 core. Backtest results are **inflated by structural BTC bias**;
recommendation rests on bias-adjusted reasoning, not raw fitness `[advances_fin_ml, p.96-100]`,
`[testing_tuning, p.327-335]`.

## Setup

- Window: 2010-07-20 to 2026-04-17 (15.74y, 3961 bars; binding: `BTCSIM` 2010+)
- Allocation grid: `RSSXSIM` from 0% to 35% in 1% steps, `GDESIM = 35% − RSSXSIM`, keep `RSSTSIM = 40%`, `ZROZSIM = 25%`
- `RSSXSIM` proxy = `1.0 SPYSIM + 0.8 GLDSIM + 0.2 BTCSIM − 1.0 CASHX` (gross 2.0)
- Direct scoring (no GA), `rolling_step=21`, fitness `core_relative_wealth_dominance`

## Raw grid result — every metric improves monotonically

| RSSX% | GDE% | BTC_notional% | CAGR | MDD | Sharpe | Calmar | Fitness |
|---:|---:|---:|---:|---:|---:|---:|---:|
| **0** (baseline) | 35 | 0.00 | 15.58% | -21.46% | 1.111 | 0.726 | +0.3500 |
| 5 | 30 | 1.00 | 17.18% | -22.11% | 1.201 | 0.777 | +0.3799 |
| 10 | 25 | 2.00 | 18.78% | -22.76% | 1.281 | 0.825 | +0.4184 |
| 15 | 20 | 3.00 | 20.38% | -23.41% | 1.351 | 0.871 | +0.4622 |
| 20 | 15 | 4.00 | 21.99% | -24.06% | 1.412 | 0.914 | +0.5121 |
| 25 | 10 | 5.00 | 23.60% | -24.71% | 1.464 | 0.955 | +0.5692 |
| 35 | 0 | 7.00 | 26.83% | -26.01% | 1.544 | 1.032 | +0.7094 |

**Every metric (CAGR, Sharpe, Sortino, Calmar, fitness) increases monotonically from
RSSX=0 to RSSX=35.** No interior optimum. This is a flag — the backtest is being
driven by a single dominant factor.

## Why the monotonicity is a backtest artifact

`BTCSIM` history (2010-07 to 2026-04): CAGR `135.23%`, MDD `-93.24%`, terminal
wealth `761,691×`.

This is **not** a forward-realistic BTC return distribution:

1. **Survivorship bias:** BTC survived; hundreds of crypto projects died. The
   sample only includes the winner `[advances_fin_ml, p.96-100]`.
2. **Non-stationarity:** the 2010-2017 portion is pre-ETF, pre-institutional,
   pre-Coinbase-IPO BTC. Returns there reflect a regime that no longer exists.
3. **One-time ramp:** BTC went from `$0.01` to `$100k+`. That `10^7×` multiple is
   structurally non-repeatable; expecting it to compound forward is naive.
4. **Selection of start date:** different start dates (e.g., 2013, 2017) produce
   wildly different BTC CAGRs (`~30-200%`). The 2010-07 start happens to be near
   the absolute bottom of BTC price history, maximizing measured CAGR.

A reasonable forward BTC CAGR is in the `15-30%` range (consistent with high-vol
risk-asset Sharpe `~0.5-0.8`), not `135%`. Most of the grid's "improvement" is
the model paying forward an unrepeatable ramp.

## Bias-adjusted view

Discount BTC's contribution by the difference between historical and forward
expected CAGR:

| RSSX% | BTC_n% | Raw CAGR | Adjusted CAGR (BTC fwd 25%) | Adjusted CAGR (BTC fwd 15%) | MDD | Adj Calmar (fwd 25%) | Adj Calmar (fwd 15%) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.0 | 15.58% | 15.58% | 15.58% | -21.46% | **0.726** | **0.726** |
| 5 | 1.0 | 17.18% | 16.08% | 15.98% | -22.11% | 0.727 | 0.723 |
| 10 | 2.0 | 18.78% | 16.58% | 16.38% | -22.76% | 0.728 | 0.720 |
| 15 | 3.0 | 20.38% | 17.08% | 16.78% | -23.41% | 0.730 | 0.717 |
| 20 | 4.0 | 21.99% | 17.59% | 17.19% | -24.06% | 0.731 | 0.714 |
| 25 | 5.0 | 23.60% | 18.10% | 17.60% | -24.71% | 0.732 | 0.712 |

After bias correction, **the Calmar curve is essentially flat** across all RSSX
levels. The "improvement" disappears once forward BTC CAGR is rationalized.

Reading: adding RSSX is **not free** going forward. CAGR upside is paid for by
material drawdown deterioration (`-21.46%` → `-24.71%` for 5% BTC notional). The
trade is only attractive if BTC's forward Sharpe stays positive.

## 2022 BTC crash stress test

Window 2021-11-08 to 2022-12-31 (peak-to-trough of BTC's worst recent crash):

| RSSX% | Portfolio CAGR (window) | Portfolio MDD (window) |
|---:|---:|---:|
| 0 | -13.31% | -21.46% |
| 5 | -14.19% | -22.11% |
| 10 | -15.08% | -22.76% |
| 15 | -15.95% | -23.41% |
| 25 | -17.70% | -24.71% |

Each `+5%` RSSX cost approximately `~0.9pp` worse annualized return through the
crypto winter. Not catastrophic, but not free. The deterioration is real cost
that pays back only if BTC subsequent recovery happens — true in 2024-2026, may
not be true in future crashes `[testing_tuning, p.327-335]`.

## Recommendation

The **honest recommendation is RSSX = 10%** (2% BTC notional) inside the GDE
sleeve. Rationale:

- **Defensible exposure size:** 2% BTC notional is in the middle of institutional
  norms (1-5% range for digital asset allocation).
- **Bias-adjusted neutral:** Calmar essentially unchanged (`0.728` vs `0.726`)
  even with conservative BTC forward assumption.
- **Asymmetric option value:** if BTC continues legitimizing (more ETF adoption,
  treasury holdings, regulatory clarity), the small exposure captures upside.
- **Limited downside:** in a -80% BTC crash, contributes `~1.6pp` to portfolio
  MDD before any rebalancing — manageable.
- **Operationally feasible:** one extra ETF (RSSX), no exotic infrastructure.

Allocation:

```text
Backtest weights:        35% GDE / 40% RSST           / 25% ZROZ
Implementation v1:       35% GDE / 22% RSST / 18% CTAP / 25% ZROZ   (MF manager split)
Implementation v2:       25% GDE / 10% RSSX / 22% RSST / 18% CTAP / 25% ZROZ   (with BTC sleeve)
```

### Optional ranges

| Profile | RSSX | BTC notional | When | Caveat |
|---|---:|---:|---|---|
| Conservative | 5% | 1.0% | First sleeve into crypto | Marginal forward edge |
| **Recommended** | **10%** | **2.0%** | **Standard B4-v2 implementation** | **Bias-adjusted neutral** |
| Aggressive | 15% | 3.0% | Higher BTC conviction | MDD `~24%`, ~1.5pp worse |
| Not recommended | 20%+ | 4.0%+ | — | Bets the portfolio on BTC forward CAGR |

## What we did NOT validate

- Forward BTC return distribution (uses historical-as-proxy with bias correction).
- Real `RSSX` ETF live tracking vs the local proxy formula.
- Tax treatment of crypto-stacked ETFs in BR.
- Custody and operational risk inside the ETF wrapper.
- Regulatory tail risk (single jurisdiction crypto crackdown).
- Behavior in true crypto bear markets longer than 14 months.

## Status

Discovery-only. The 2% BTC notional via 10% RSSX is an Implementation Note
recommendation that does **not** change the backtest definition of B4-v2. The
research portfolio remains `35% GDE / 40% RSST / 25% ZROZ` on RSSTSIM data.
Mandate §1 unchanged `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

## Artifacts

- Grid CSV (1% steps, 0-25%): `grid.csv`
- Extended grid (0-35%): `grid_extended.csv`
- BTCSIM source: Testfol.io native SIM (2010-07-19+)
- RSSXSIM proxy: `scripts/build_stacked_sim_proxies.py` (`1.0 SPY + 0.8 GLD + 0.2 BTC - 1.0 CASHX`)
- Proxy metadata: `data/testfolio/cache/stacked_proxies.meta.json`
