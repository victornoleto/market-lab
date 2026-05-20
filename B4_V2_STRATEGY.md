# B4-v2 — Static Core Strategy (Discovery-Only)

Status: **internal research winner / discovery-only.** This document summarizes the
strongest static, long-only, monthly-rebalanced ETF portfolio found in
`studies/static_spy_beater_portfolio/` as of 2026-05-19. It does not authorize
deployment, capital reallocation, or a mandate change. The repository remains under
maintenance mode (see `docs/investment-mandate.md` §1 and `docs/CURRENT_STATE.md`).

## TL;DR

**B4-v2 = 35% GDESIM / 40% RSSTSIM / 25% ZROZSIM**, monthly rebalance, long-only,
gross `1.0`, no negative external cash. Over `1988-01-04..2026-04-17` it beats SPY by
`+4.24pp` CAGR with `~25.20pp` less full-period MDD, and beats the original B4 reference
by `+1.27pp` CAGR while only deepening MDD by `~2.02pp`.

## Allocation

| Sleeve | Weight | Role | Embedded exposure |
|---|---:|---|---|
| `GDESIM` | 35% | Capital-efficient US equity + gold stack | 90% SPY + 90% Gold |
| `RSSTSIM` | 40% | US equity + managed futures stack | 100% SPY + 100% MF |
| `ZROZSIM` | 25% | Long zero-coupon Treasury convexity | 25+ year duration |

Effective exposure per $1 portfolio:

| Family | Approx. notional |
|---|---:|
| US large equity | 0.715 |
| Managed futures | 0.400 |
| Gold | 0.315 |
| Zero-coupon Treasury | 0.250 |
| Embedded financing | -0.680 |

Long-only with gross weight `1.0` and no negative external `CASHX`. Negative financing
above is embedded inside capital-efficient ETF simulations, not external margin
`[leverage_for_the_long_run, p.13]`.

## Key Metrics (1988-01-04 to 2026-04-17)

| Portfolio | CAGR | MDD | Sharpe | Sortino | Calmar | Ulcer | Terminal wealth |
|---|---:|---:|---:|---:|---:|---:|---:|
| **B4-v2 (35/40/25 core)** | **15.70%** | **-29.94%** | **1.040** | **1.484** | **0.524** | **0.068** | **265x** |
| B4 original (25/25/25/25 NTSX/GDE/RSST/ZROZ) | 14.43% | -27.92% | 1.018 | 1.449 | 0.517 | 0.067 | 174x |
| B4-like stacked (margin, Testfol.io ref) | 13.75% | -28.42% | 0.981 | 1.400 | 0.484 | 0.069 | 139x |
| SPYSIM buy-hold | 11.46% | -55.14% | 0.691 | 0.884 | 0.208 | 0.135 | 64x |
| GA robust lead (50 RSST / 35 GDE / 10 SPY / 5 ZROZ) | 16.81% | -41.20% | 0.972 | 1.338 | 0.408 | 0.088 | 383x |
| GA aggressive lead (35 GDE / 50 RSST / 5 TQQQ / 10 ZROZ) | 17.97% | -49.37% | 0.972 | 1.351 | 0.364 | 0.109 | 558x |

GA challengers buy `1-2pp` extra CAGR at `7-15pp` worse MDD and worse Calmar; rejected
under the core-relative-dominance objective `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.222-223]`.

## Rolling Behavior vs SPY

| Horizon | CAGR p10 | CAGR median | MDD p10 | Rel-wealth p10 vs SPY | Rel-wealth median vs SPY | Latest rel-wealth |
|---|---:|---:|---:|---:|---:|---:|
| 3y | 6.42% | 14.28% | -28.02% | -9.84% | +10.97% | -0.07% |
| 5y | 8.71% | 14.55% | -29.89% | -8.59% | +17.97% | +8.72% |
| 10y | 11.49% | 14.42% | -29.94% | -4.25% | +60.20% | -5.99% |
| 15y | 12.37% | 14.46% | -29.94% | +12.88% | +109.54% | +7.24% |

Not a flawless rolling dominator at 3y/5y/10y p10; strength is long-horizon
compounding with materially shallower full-period drawdown. 15y p10 turns positive.

## Regime Diagnostics

| Regime | B4-v2 terminal wealth | B4-v2 MDD | Wealth vs SPY |
|---|---:|---:|---:|
| Dot-com drawdown | 0.812x | -29.94% | 1.53x |
| GFC drawdown | 0.870x | -28.02% | 1.92x |
| QE bull | 3.699x | -14.61% | 1.04x |
| Covid crash | 0.832x | -20.00% | 1.25x |
| Inflation/rates shock | 0.822x | -21.46% | 1.05x |
| Recent recovery | 1.999x | -14.41% | 1.03x |

Beat SPY wealth in every named regime. Beat B4 original in GFC, inflation shock and
recent recovery; B4 original slightly better in dot-com, QE bull and Covid crash.

## Why This is the Internal Winner

- Best no-external-margin point found by the local B4-like Pareto search
  (`studies/static_spy_beater_portfolio/results/local_pareto_b4_no_margin/`).
- Follow-up GA searches with levered equity (`SSOSIM`/`UPROSIM`/`QLDSIM`/`TQQQSIM`),
  cash, managed futures (`KMLMSIM`), SCV (`VBRSIM`), value (`EFVSIM`) and momentum
  (`MTUMSIM`) sleeves converged back to this same core.
- **Stacked-ETF expansion triage (2026-05-19, 3 seeds × 21 tickers, 8 local proxies
  CTAP/RSBT/RSIT/HOLD/MATE/ESBG/GDT/ALLW + Testfol.io NTSX/NTSD/NTSI/BTAL/IEI/STIP/
  GSG/LTPZ):** GA best fitness `0.2681` vs core `0.3500` — **core survived**. No
  alternative stacked sleeve or international/alpha sleeve made it into any seed's
  top-5. See `studies/static_spy_beater_portfolio/results/ga_b4v2_stacked_triage/REPORT.md`.
- Higher-CAGR challengers bought less than `~1.5pp` extra CAGR for `7-15pp` worse MDD
  and failed the core-relative-dominance objective `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.222-223]`.

## Implementation Notes

The backtest defines the **economic exposure** of the portfolio. The choice of *which
concrete ETFs* deliver that exposure is an implementation decision that can diversify
single-manager risk without changing the research result.

### MF sleeve: split RSST + CTAP

The 40% `RSSTSIM` sleeve in the backtest represents a `100% SPY + 100% MF` stack.
Two live ETFs deliver this concept with different MF managers:

| ETF | Inception | MF manager | Style |
|---|---|---|---|
| RSST (Return Stacked US Stocks & MF) | 2023-09-06 | Newfound Research (proprietary) | Multi-asset trend, monthly aggregation |
| CTAP (Simplify US Equity PLUS MF) | 2025-12-09 | Simplify Asset Management (proprietary) | Trend + dynamic vol-targeting |

**Recommended implementation split: 55% RSST / 45% CTAP** within the 40% MF stack
sleeve.

Translated allocation (MF split only — full implementation also splits the gold
sleeve; see "Final composed implementation" below):

```text
Backtest weights:                  35% GDE / 40% RSST           / 25% ZROZ
After MF split (intermediate):     35% GDE / 22% RSST / 18% CTAP / 25% ZROZ
```

### Why diversify MF managers

Live data 2025-12-09 to 2026-05-19 (111 daily bars, common window) shows the two
products are **structurally similar but functionally divergent**:

| Metric | RSST | CTAP |
|---|---:|---:|
| Total return (5.3m) | +19.32% | +30.59% |
| Annualized vol | 22.67% | 23.78% |
| Max DD (window) | -11.71% | -9.02% |
| Daily return correlation between the two | 0.554 | |

The `0.554` daily-return correlation is the key signal. Both products are
mechanically `100% SPY + 100% MF`, so the shared SPY component alone should produce
correlation `~0.5` if the MF strategies were independent. Decomposition:

```text
Cor(RSST, CTAP)  ≈ [Var(SPY) + Cov(MF_R, MF_C)] / sqrt(Var(RSST) × Var(CTAP))
Observed         = 0.554
Implied          → Cor(MF_R, MF_C) ≈ 0.10–0.20
```

The two MF strategies (Newfound vs Simplify) are **almost orthogonal in daily
returns** despite implementing the same concept. This produces real manager-
diversification benefit, not just operational redundancy `[risk_parity, p.80-81]`.

### Why 55/45 and not 50/50

CTAP has only 5.3 months of live track record (inception 2025-12-09). Operational
risks of a recently-launched fund (PM departure, strategy drift, low AUM run,
process failure) are non-negligible. Weighting toward the more mature RSST while
still capturing the bulk of the diversification benefit is the prudent trade-off.

When CTAP accumulates 18-24 months of live history without operational issues,
rebalance toward 50/50 becomes justified.

### What the 5.3-month return spread does NOT show

CTAP's `+11.27pp` return advantage over RSST in this window is **not** evidence
that CTAP's manager is better. With `n=111` daily observations, this is well
within normal range of two MF managers running different signal aggregations on
overlapping universes. In a different 5-month window, RSST could lead by the same
margin. The recommendation rests on the **correlation** signal (which is robust to
short windows) — not the **return spread** (which is noise-dominated)
`[advances_fin_ml, p.208-211]`.

### What does not change

- Backtest weights and metrics: still `35/40/25` with `RSSTSIM` as the MF sleeve.
- Expected CAGR/MDD/Calmar: identical to the canonical numbers above.
- Mandate §1: unchanged, discovery-only.

The MF split is purely an implementation refinement that reduces single-product
risk without altering the research conclusion.

### Gold sleeve: split GDE + RSSX

The 35% `GDESIM` sleeve in the backtest represents a `90% SPY + 90% Gold` stack.
A second-source product (RSSX) delivers a similar capital-efficient gold-stacked
profile **with an additional Bitcoin sleeve managed by risk parity vol-targeting**:

| ETF | Inception | Exposure model | Crypto component |
|---|---|---|---|
| GDE (WisdomTree Efficient Gold Plus) | 2022-06 | 90% SPY + 90% Gold (static) | None |
| RSSX (Return Stacked US Stocks & Gold/Bitcoin) | 2024 | 100% SPY + 100% (Gold/Bitcoin via risk parity) | Dynamic 5-25% BTC inside the Gold/BTC sleeve |

**Recommended implementation split: 50% GDE / 50% RSSX** within the 35% sleeve.

### RSSX risk parity mechanism (per prospectus April 2026)

The Gold/Bitcoin sleeve inside RSSX is **not statically weighted**. Per the
prospectus (page 56), ReSolve Asset Management SEZC manages this sleeve under
risk parity:

> "the allocation between gold and bitcoin will be dynamically adjusted so that
> each asset contributes equally to the overall portfolio risk. This means that
> the Gold/Bitcoin strategy will typically allocate a larger percentage of its
> assets to the asset class with lower forecasted volatility."
>
> "the Gold/Bitcoin strategy will generally allocate **between 75% and 95% of
> its assets to gold and between 5% and 25% to bitcoin**."

Operational properties:

- **BTC crashes:** when BTC realized volatility spikes (e.g., 2022 crypto
  winter), the mechanism trims BTC weight toward `5%` and raises Gold toward
  `95%`. BTC's contribution to portfolio drawdown is structurally bounded.
- **BTC calm periods:** weight can rise toward `25%` (the cap), capturing more
  upside when crypto stabilizes.
- **Forward asymmetry:** the vol-targeting creates asymmetric crypto exposure —
  upside in bull markets, dampened downside in bear markets `[risk_parity, p.80-81]`.
- **Implementation:** Bitcoin exposure is gained through **bitcoin futures,
  swaps, and Underlying Bitcoin ETFs/ETPs** (not direct spot bitcoin). A wholly-
  owned Cayman Islands Subsidiary handles non-RIC-qualifying income from the
  futures/swap exposure.
- **Sub-advisers:** Newfound Research (US Equity sleeve, same operator as RSST)
  and ReSolve Asset Management SEZC (Gold/BTC sleeve).
- **Total ER: 0.67%** (management fee `0.65%` + AFFE `0.02%`).

### Effective Bitcoin notional under 50/50 GDE/RSSX

Per `$1` of portfolio at `17.5% RSSX` allocation:

| Regime | BTC weight inside RSSX | Portfolio BTC notional |
|---|---:|---:|
| Calm crypto (BTC vol ≈ Gold vol) | ~25% (cap) | ~4.4% |
| Typical (BTC vol ≈ 4-5× Gold vol) | ~15-20% | ~2.6-3.5% |
| Stressed (BTC vol > 6× Gold vol) | ~5-10% | ~0.9-1.75% |

The portfolio BTC notional sits in the industry-prudent `1-5%` band across all
regimes. The vol-targeting mechanism acts as an automatic stabilizer — no
manual rebalancing needed in crashes `[risk_parity, p.80-81]`,
`[testing_tuning, p.327-335]`.

### Why 50/50 GDE/RSSX (not 70/30 or 60/40)

The earlier 60/40 RSST/CTAP recommendation kept CTAP underweighted because of
CTAP's `5.3m` live track record. RSSX is a different case:

- **Risk floor is structural, not just operational.** Vol-targeting on the BTC
  sleeve provides a mechanical downside cap — the fund cannot run away with
  excess BTC exposure even if the PM is asleep.
- **Same operator family.** Newfound (US Equity) is the same sub-adviser as
  RSST. Operational integration risk is low.
- **No manager-style divergence to hedge against.** GDE and RSSX use static and
  vol-targeted mechanisms respectively; they're complementary, not redundant.
- **Backtest signal:** the RSSX proportion test (`results/rssx_proportion_test/`)
  showed bias-adjusted Calmar improvement plateaus around `RSSX = 17-22%`, with
  monotonic gains beyond mostly attributable to BTC backtest bias.

### Final composed implementation

```text
Backtest weights:    35% GDE                              / 40% RSST                / 25% ZROZ
Implementation:      17.5% GDE   / 17.5% RSSX             / 22% RSST / 18% CTAP     / 25% ZROZ
                     50/50 split of GDE sleeve              55/45 split of MF sleeve   unchanged
```

Approximate effective exposure per `$1` portfolio (typical-vol regime):

| Family | Backtest 35/40/25 | Implementation 17.5/17.5/22/18/25 | Delta |
|---|---:|---:|---:|
| US large equity | 0.715 | 0.733 | +1.8pp |
| Managed futures (Newfound) | 0.400 | 0.220 | -18pp |
| Managed futures (Simplify) | 0.000 | 0.180 | +18pp |
| Gold | 0.315 | ~0.290 | ~-2pp |
| Bitcoin | 0.000 | ~0.026-0.035 | new |
| Zero-coupon Treasury | 0.250 | 0.250 | 0 |
| Embedded financing | -0.680 | ~-0.715 | ~-3.5pp |
| Gross | 1.680 | ~1.715 | +3.5pp |

Total MF exposure unchanged at `40%`; total Gold drops `~2pp` to fund a `~3%`
BTC sleeve. Slightly more gross leverage (`+3.5pp`) reflects RSSX gross `2.0` vs
GDE gross `1.8`.

### Caveats specific to the gold sleeve split

- **No backtest validation.** The backtest evaluates `35% GDESIM` exposure; the
  RSSX proxy showed monotonically-improving results inflated by BTC's `2010-2026`
  ramp (`135%` historical CAGR, structurally non-repeatable). The recommendation
  rests on the vol-targeting mechanism documented in the prospectus, not on
  proxy backtest fitness.
- **BR investor access:** confirm RSSX is available via Inter Internacional or
  XP before commitment.
- **Tax treatment:** crypto-stacked ETFs through a Cayman subsidiary may have
  different distribution/tax behavior than gold-only stacked ETFs. Check IR
  treatment for the BTC futures component.
- **Operational risk:** RSSX inception is `2024+`, AUM is small relative to GDE.
  Single-fund failure mode is non-zero.
- **Regulatory tail:** crypto regulation can change rapidly; the BTC futures
  market is more exposed than spot BTC in some scenarios.

### Other sleeves: no equivalent split

- **RSST 22% + CTAP 18%:** MF manager diversification (see section above).
- **GDE 17.5% + RSSX 17.5%:** gold sleeve + BTC convexity (this section).
- **ZROZ 25%:** mechanical long-duration Treasury exposure, no manager skill
  component to diversify. Alternatives like `EDV` are similar in profile but
  offer no improvement.

## Core-Satellite Configuration: 70% B4-v2 / 30% T3d-K2 Rotation

This section extends B4-v2 from a 100%-allocation strategy to a **core-satellite
portfolio** where 70% of capital sits in the passive B4-v2 core and 30% sits in
an active LETF rotation satellite (`T3d-K2`, the incumbent winner of
`studies/letf_rotation_hunt/`). The goal is to lift portfolio CAGR while
preserving the core's drawdown profile, exploiting the moderate correlation
(0.467) between the two strategies `[risk_parity, p.80-81]`.

### Satellite strategy: T3d-K2 (LETF rotation)

**Config name:** `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`
**Source study:** `studies/letf_rotation_hunt/` — iter 022, study winner

**Signal mechanics:**

The strategy holds **one of two states**, evaluated at month-end on the QQQ
underlying:

1. **Risk-ON:** hold `QLD` (ProShares Ultra QQQ, 2× Nasdaq-100)
2. **Risk-OFF:** hold `ZROZ` (PIMCO 25+ Year Zero-Coupon Treasury)

State transition uses a **vote-of-K=2** rule among four binary indicators
applied to QQQ:

| Indicator | Signal definition | Citation |
|---|---|---|
| `SMA250` | QQQ close > 250-day SMA → bullish | `[trend_following, ch.5]` |
| `SMA100` | QQQ close > 100-day SMA → bullish | `[trend_following, ch.5]` |
| `vol21_40` | 21-day realized vol of QQQ between 21% and 40% (annualized) → bullish | `[volatility_trading, p.95-110]` |
| `ar30_off` | Autoregressive AR(1) coefficient of QQQ over 30-day window > 0 → bullish | `[advances_fin_ml, ch.5]` |

If **at least 2 of 4** indicators are bullish, go risk-ON (`QLD`). Otherwise,
risk-OFF (`ZROZ`). Rebalance evaluated at end of each month; trade only on
state changes.

**Validation status:**

- Score: **82 (STRONG)** at study close, of which `90` is the deploy threshold
- Gates passing: **6/7** (G1 PBO `0.421` passes, G3 redesign benchmark-relative
  MDD passes, etc.)
- Sortino (LH 56y, untaxed): `1.3246`
- Sharpe (LH 56y, untaxed): `0.919`
- CAGR (LH 56y, untaxed): `31.08%`
- MDD (LH 56y, untaxed): `-64.50%`
- pct_time_above_SPY: `100%`
- crises beat SPY: `2/4` (GFC 2008 + COVID 2020)
- Cumulative trials (post-T5-expansion): `426`

Tax-aware version (`t3d_k2_taxed`, 15% IR annual DARF):

- CAGR: `22.51%` (vs `31.08%` untaxed — `~8.6pp` tax drag)
- MDD: `-59.43%`
- Sortino: `0.979`
- 366 sale events over 31 calendar years

### Why 70/30 (size sweep, tax-aware)

Sweep across allocations from `100%` core to `60/40`, common window
`1988-2026` (38.28y, 9645 daily bars), annual rebalance, tax-aware:

| Plano C % | T3d-K2 % | CAGR | MDD | Sharpe | Sortino | Calmar | Terminal wealth |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0 | 15.70% | -29.94% | 1.040 | 1.484 | 0.524 | 265× |
| 85 | 15 | 17.41% | **-27.80%** | 1.060 | 1.506 | 0.627 | 467× |
| 80 | 20 | 17.92% | -27.85% | 1.047 | 1.479 | **0.644** | 550× |
| 75 | 25 | 18.39% | -28.94% | 1.029 | 1.443 | 0.636 | 642× |
| **70** | **30** | **18.84%** | **-30.80%** | **1.006** | **1.400** | **0.612** | **741×** |
| 65 | 35 | 19.26% | -32.74% | 0.982 | 1.356 | 0.588 | 848× |
| 60 | 40 | 19.65% | -34.77% | 0.957 | 1.312 | 0.565 | 961× |

Reading:

- **80/20 is the Calmar peak** (`0.644`) — the absolute "best risk-adjusted"
  point. MDD `-27.85%` actually **beats** 100% Plano C (`-29.94%`) thanks to
  the moderate-correlation diversification.
- **70/30 (chosen) trades a small Calmar drop for `+1.45pp` CAGR vs 100% Plano
  C**, with MDD only `+0.86pp` worse. The Calmar `0.612` still materially
  beats 100% Plano C (`0.524`).
- Beyond 65/35, the satellite share starts degrading the portfolio's risk
  profile faster than it adds return.

The choice of `70/30` reflects a CAGR-tilt within the prudent zone. Investors
prioritizing pure risk-adjusted return could pick `80/20`; those wanting more
satellite exposure could pick `75/25` or `70/30`. Above `60/40`, the marginal
CAGR gains compress while MDD deteriorates faster.

### Why this works: correlation diagnostics

Daily-return correlation matrix (1988-2026, tax-aware):

| | Plano C | T3d-K2 | T3d-K2-TQQQ | iter30 proxy |
|---|---:|---:|---:|---:|
| Plano C | 1.000 | 0.467 | 0.468 | 0.467 |
| T3d-K2 | 0.467 | 1.000 | 0.998 | 0.998 |

Correlation `0.467` is **moderate** — high enough that the satellite has real
market exposure (not just cash drag), low enough that the diversification is
genuine. Critically, when Plano C is in stress (equity bear regime), T3d-K2 is
typically in risk-OFF holding ZROZ → the two strategies' worst drawdowns occur
in different historical windows, which is why blended MDD stays near the core's.

### Operational details

| Aspect | Detail |
|---|---|
| Rebalance frequency | Monthly (signal evaluated end-of-month) |
| Trade trigger | Only on state change (Vote-K=2 flips) |
| Expected trade frequency | ~12 state changes per decade (3-4 per year average) |
| Tax events | One realized P&L event per state change (DARF anual) |
| Underlying universe | QQQ (signal computation only — not held); QLD (2x), ZROZ |
| Broker requirement | Inter Internacional, XP Internacional, or US broker (IBKR) |
| Indicator computation | Daily, but only month-end votes count; signals re-computed each EOM |

### Final composed implementation (with core-satellite + RSST/CTAP + GDE/RSSX splits)

```text
Total portfolio = 70% B4-v2 core  +  30% T3d-K2 satellite

B4-v2 core composition (within the 70%):
  17.5% GDE        / 17.5% RSSX               (gold/BTC sleeve, 50/50 split)
  22%   RSST       / 18%   CTAP               (MF sleeve, 55/45 split)
  25%   ZROZ                                  (Treasury sleeve, unsplit)
  (these add to 100% of the 70% allocation)

Translated to total portfolio weights:
  12.25% GDE       /  12.25% RSSX             (8.575% of total each)
  15.40% RSST      /  12.60% CTAP             (10.78% of total RSST, 8.82% of total CTAP)
  17.50% ZROZ                                 (= 25% × 70%)
  30%    T3d-K2 satellite                     (QLD ↔ ZROZ rotation)

When the satellite is in risk-ON:
  effective holdings ≈ 12.25 GDE / 12.25 RSSX / 15.4 RSST / 12.6 CTAP / 17.5 ZROZ / 30 QLD
When the satellite is in risk-OFF:
  effective holdings ≈ 12.25 GDE / 12.25 RSSX / 15.4 RSST / 12.6 CTAP / 47.5 ZROZ
```

### Caveats specific to the core-satellite blend

- **Mandate §1 contradiction.** Current mandate prescribes `100% Plano C`.
  Activating a `30%` satellite is a structural mandate change that must be
  formally approved via the §7 override path with documented rationale.
- **No blend-level validation gates.** T3d-K2 has 6/7 individual gates passing
  but PBO/DSR/walk-forward have **not** been run at the blended 70/30 portfolio
  level. The blend correlation/metrics shown above are diagnostic, not formal
  validation `[advances_fin_ml, p.208-211]`.
- **Tax-aware backtest assumes annual DARF realization.** Real BR tax timing
  is per-event with monthly limits and offset rules; actual tax drag could
  differ.
- **T3d-K2 score `82 < 90` deploy threshold.** The deploy-eligible gate from
  the original study spec was never cleared. Running it as a satellite is a
  weaker bar than running it standalone, but still requires §7 documentation.
- **Signal robustness.** The vote-K=2 mechanism survived multiple validation
  rounds, but live-data behavior post-2026-05 has not been observed. The
  letf_rotation_hunt loop continues post-close exploration; if a successor
  strategy displaces T3d-K2 in a future iteration, the satellite should
  follow.
- **Sortino slight drop in blend (`1.484` → `1.400`).** The blend marginally
  underperforms 100% Plano C on Sortino specifically because T3d-K2's tail
  losses (e.g., 1999-2002, 2007-2009, 2022) are deeper than the core. Sharpe
  is essentially flat (`1.040` → `1.006`).

### Status

**Discovery-only.** This is a research target portfolio, not a deploy
authorization. Before activating the 70/30 structure with real capital:

1. Re-validate T3d-K2 with current data (out-of-sample post-2026-05-10).
2. Run PBO/DSR/walk-forward at the blend level (not just standalone).
3. Document mandate §7 override rationale.
4. Choose broker (IBKR Inter Internacional, etc.) and confirm product
   availability for QLD + ZROZ + all B4-v2 ETFs.
5. Verify tax reporting workflow for monthly state changes
   `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

## Leveraged Variant via IBKR Margin (optional uplift)

This section evaluates running the 70/30 core-satellite portfolio at leverage
factors between `1.0×` and `2.0×` using IBKR margin financing. **This is an
optional uplift, not part of the baseline recommendation.** Leverage trades
CAGR for drawdown amplification and introduces margin-call risk
`[leverage_for_the_long_run, p.13]`, `[investment_mandate, §3]`.

### IBKR margin mechanics

Two margin regimes are available for BR-resident investors:

| Regime | Initial margin | Maintenance | Practical max leverage | Min account |
|---|---:|---:|---:|---:|
| **Reg-T (Regulation T)** | 50% | 25% | **2.0×** | None |
| **Portfolio Margin (PM)** | 15-25% (risk-based) | dynamic SPAN-like | 4-7× (theoretical) | USD 110k |

For leveraged ETF sleeves (RSST, GDE, RSSX, QLD), Reg-T treats each leg
individually with 50%/25% rules. Portfolio Margin uses a Span-style risk model
that can permit higher leverage on a diversified book, but requires the larger
minimum account.

### Financing cost (current IBKR rates, USD margin)

| Tier | Account balance USD | Approximate annual rate |
|---|---|---:|
| 1 | < 100k | SOFR + 1.5% ≈ **6.5-7%** |
| 2 | 100k - 1M | SOFR + 1.0% ≈ 6.0% |
| 3 | 1M - 3M | SOFR + 0.75% ≈ 5.75% |
| 4 | > 3M | SOFR + 0.5% ≈ 5.5% |

Analysis below uses **7% annual financing** (conservative for tier-1 accounts).
Real cost varies with SOFR — a `+200bp` SOFR move would compress the leverage
spread materially.

### Leverage sweep on 70/30 blend (1988-2026, tax-aware, 7% financing)

| Leverage | CAGR | MDD | Sharpe | Sortino | Calmar | Δ CAGR vs L=1 | Δ MDD vs L=1 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| **1.00** | **18.84%** | **-30.80%** | **1.006** | **1.400** | **0.612** | — | — |
| 1.10 | 19.86% | -33.84% | 0.974 | 1.355 | 0.587 | +1.02pp | -3.04pp |
| **1.25** | **21.31%** | -39.25% | 0.935 | 1.301 | 0.543 | **+2.47pp** | -8.46pp |
| **1.50** | **23.56%** | -47.55% | 0.887 | 1.234 | 0.495 | **+4.72pp** | -16.75pp |
| 1.75 | 25.56% | -54.96% | 0.853 | 1.187 | 0.465 | +6.72pp | -24.16pp |
| 2.00 | 27.31% | -61.53% | 0.828 | 1.151 | 0.444 | +8.47pp | -30.73pp |

### Reading

- **L=1.10:** +1pp CAGR for 3pp worse MDD — marginal benefit; gestão extra não
  compensa.
- **L=1.25:** +2.47pp CAGR for 8.46pp worse MDD — sweet spot moderate.
- **L=1.50:** +4.72pp CAGR for 16.75pp worse MDD — sweet spot agressivo;
  MDD `~-47.5%` ainda gerenciável historicamente.
- **L=1.75:** entra em "margin call zone" — MDD `-55%` está perto do gatilho
  Reg-T maintenance em quase qualquer cenário de stress histórico.
- **L=2.00:** **risk of ruin material** — MDD `-61.5%` historicamente
  realizado significaria liquidação forçada antes da recuperação em
  cenários como GFC 2008 ou COVID 2020.

### Effective gross leverage (compound risk)

The B4-v2 implementation already has embedded leverage from stacked ETFs
(`RSSTSIM`, `CTAPSIM`, `GDESIM`, `RSSXSIM`). External margin compounds this:

| External leverage | Effective gross exposure |
|---:|---:|
| 1.00 | ~1.65× |
| 1.25 | ~2.06× |
| **1.50** | **~2.48×** |
| 1.75 | ~2.89× |
| **2.00** | **~3.30×** |

At `L=2.0` external, the effective economic exposure runs `~3.3×` on the
investor's net worth. This is materially more aggressive than headline `2.0×`
suggests `[leverage_for_the_long_run, p.40-60]`.

### Margin call mechanics (Reg-T example)

For `L=1.5` with USD 100k of own capital:

| Scenario | Total value | Equity | Equity ratio | Outcome |
|---|---:|---:|---:|---|
| Initial | $150k | $100k | 67% | OK |
| -30% drop | $105k | $55k | 52% | OK |
| -50% drop (GFC-like) | $75k | $25k | 33% | OK (above 25%) |
| **-60% drop** (extrapolated L=1.5 MDD) | **$60k** | **$10k** | **17%** | **MARGIN CALL** — broker liquidates |
| -70% drop | $45k | -$5k | <0% | Equity wiped out |

When equity ratio drops below 25%, IBKR Reg-T forces liquidation to restore
the ratio. **Critically:** broker sells at market-bottom prices, so you
realize losses **without** participating in the subsequent recovery. This is
why `L=1.75+` is unsafe — the historical MDD exceeds the margin call gate.

### BR investor specifics

| Risk | Detail |
|---|---|
| Currency | Returns are USD-denominated; BRL/USD vol amplifies by leverage |
| Tax on interest | Margin interest paid in USD typically **not deductible** against capital gains in BR (operational cost, not loss) — adds to effective drag |
| Liquidation timezone | Margin call may trigger ~03:00 BRT (US market open); reaction window very tight |
| Rate risk | If SOFR rises from 4.5% to 7%, financing cost becomes 9-10%; leverage spread vs CAGR shrinks materially |
| Reporting | DARF mensal still applies; leverage doesn't change tax events but amplifies amounts |

### Recommended leverage by profile

| Profile | L | CAGR | MDD | Rationale |
|---|---:|---:|---:|---|
| **Conservative (default)** | **1.00** | 18.84% | -30.80% | Risk floor unchanged; no margin call risk; baseline recommendation |
| **Moderate** | **1.25** | 21.31% | -39.25% | +2.47pp CAGR with manageable MDD increase; well below margin call zone in historical stress |
| **Aggressive** | **1.50** | 23.56% | -47.55% | +4.72pp CAGR; MDD -47.55% near but below margin call gate; requires active monitoring |
| Not recommended | 1.75 | 25.56% | -54.96% | Historical MDD reaches margin call gate at multiple events |
| **Prohibited** | **2.00** | 27.31% | -61.53% | Forced liquidation in GFC/COVID-like events; risk of ruin material |

### Sanity check vs mandate §3 (Plano A DORMANT)

Mandate §3 prescribes "alavancagem por sweep 1:1→1:200 × Kelly f/2" for the
DORMANT Plano A multi-asset CFD strategy. Applied here:

- Portfolio Sharpe `~1.0` → Kelly full `≈ Sharpe² = 1.0`
- Kelly fractional (Kelly/2) → optimal leverage `≈ 1.5×`

The empirical sweet spot `L=1.25-1.50` matches the Kelly/2 prescription
independently `[testing_tuning, p.197-210]`. This is a useful cross-check
against the formal risk framework.

### Operational steps to activate leverage

1. **Open IBKR account** (BR residents OK with Form W-8BEN).
2. **Fund account** in USD via TED.
3. **Build base portfolio** (`L=1.0`): 70% B4-v2 implementation
   (GDE/RSSX/RSST/CTAP/ZROZ split) + 30% T3d-K2 satellite (QLD ↔ ZROZ
   rotation).
4. **Apply margin** to reach target leverage (`L=1.25` or `L=1.50`).
5. **Set IBKR alerts** for equity ratio approaching 30% (early warning before
   25% maintenance threshold).
6. **Active monitoring:** re-balance leverage when portfolio drifts more than
   `±5pp` from target `L` (e.g., add margin if `L` drops from 1.5 to 1.4 after
   a rally; reduce if it rises from 1.5 to 1.6 after a drawdown).
7. **Tax workflow:** track margin interest separately for IRPF reporting;
   confirm with BR tax advisor if any deductibility paths exist (most likely
   not, but verify case-by-case).

### Caveats specific to leveraged variant

- **No PBO/DSR/walk-forward at leverage levels.** The leverage sweep above is
  pure historical backtest extrapolation. Real-money behavior with margin
  calls, slippage on liquidation, and currency volatility was not modeled
  `[advances_fin_ml, p.208-211]`.
- **Backtest does NOT model margin call dynamics.** The MDD numbers assume
  the portfolio is held through the drawdown. Real-world margin calls at
  `L=1.75+` would lock in losses below the modeled MDD.
- **SOFR rate path uncertain.** A reversion of SOFR to 2-3% would lower
  financing cost significantly and shift the leverage curves upward. A
  spike to 7%+ would do the opposite.
- **Tax drag of interest not modeled.** Adding ~2-3pp annual drag for
  non-deductible interest tax treatment in BR could move the prudent
  sweet spot downward to `L=1.15-1.30`.
- **Mandate §3 reactivation.** Activating leverage on Plano C blurs the line
  with Plano A (DORMANT). Document the override path in mandate §7 explicitly
  before deployment.

### Status

**Discovery-only and explicitly NOT recommended without further validation.**
The leverage analysis is a research scenario to inform future decisions, not
a deploy path. Before activating any leverage:

1. Stress test simulating GFC 2008 + COVID 2020 + 2022 with actual IBKR
   margin call rules engaged at `L=1.25, 1.50, 2.0`.
2. Document mandate §7 override with explicit risk acknowledgment.
3. Real-time PBO/DSR on the leveraged blend.
4. BR tax workflow confirmation for margin interest.
5. Currency hedging assessment (BRL/USD amplified vol).

## Important Caveats

This is **not** a formally validated strategy:

- Testfol.io series are simulated proxies for pre-inception history.
- `GDESIM`/`RSSTSIM` are capital-efficient/stacked products with embedded leverage;
  realized ETF tracking, financing, taxes and fund survival matter.
- BR investor implementation needs broker access, tax handling and product availability
  review.
- Monthly rebalance assumption needs sensitivity vs quarterly/yearly schedules.
- Fee/drag stress not yet applied at exact-core resolution.
- Formal validation gates (PBO/DSR/walk-forward/bootstrap) were not run because this
  study selects an internal benchmark, not a deployable trading strategy
  `[advances_fin_ml, p.208-211]`.

## Canonical Artifacts

- Full report: `studies/static_spy_beater_portfolio/FINAL_REPORT_35_40_25_CORE.md`.
- Pareto/regime (10 candidates, plots): `studies/static_spy_beater_portfolio/results/pareto_regime_report/REPORT.md`.
- Local search: `studies/static_spy_beater_portfolio/results/local_pareto_b4_no_margin/`.
- Factor/momentum GA: `studies/static_spy_beater_portfolio/results/ga_core_factor_momentum_beater/`.
- Stacked-ETF expansion triage: `studies/static_spy_beater_portfolio/results/ga_b4v2_stacked_triage/REPORT.md`.
- RSSX proportion test (grid + bias adjustment): `studies/static_spy_beater_portfolio/results/rssx_proportion_test/REPORT.md`.
- Proxy build (CTAPSIM, RSBTSIM, RSITSIM, HOLDSIM, MATESIM, ESBGSIM, GDTSIM, ALLWSIM, RSSXSIM): `scripts/build_stacked_sim_proxies.py`.
- Core-satellite size sweep + leverage analysis: `studies/static_spy_beater_portfolio/results/core_satellite_70_30/`.
- T3d-K2 satellite source study: `studies/letf_rotation_hunt/` (incumbent iter 022 `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`).
- Study memory: `studies/static_spy_beater_portfolio/MEMORY.md`.
- Next steps: `studies/static_spy_beater_portfolio/NEXT_STEPS.md`.

## Status & Mandate

- **Mandate**: 100% capital remains in **Plano C** passive factor-tilted (see
  `docs/investment-mandate.md` §1, `docs/CURRENT_STATE.md`).
- **Strategies A/B/D**: DORMANT (mandate §3, §4, §4b).
- **B4-v2**: discovery-only research benchmark inside the Plano C study line, not a
  deploy authorization.
- **Next research step**: implementation realism checks (drag, rebalance frequency,
  start-date sensitivity, remove-one-asset, BR product mapping). See
  `studies/static_spy_beater_portfolio/NEXT_STEPS.md`.
