# Iteration 008 — XAU/XAG ratio mean-reversion pair (Chan stationary-spread framework)

## Hypothesis

Trade the **gold-silver ratio (XAU/XAG)** as a stationary spread. When
the rolling z-score of the ratio (60-day lookback) exceeds ±2σ, enter a
**dollar-neutral pair** that bets on reversion to the long-run mean:

- **z(ratio) > +2.0** → ratio is "high" (gold rich vs silver) → **SHORT XAU + LONG XAG** (1 USD notional each leg)
- **z(ratio) < −2.0** → ratio is "low" (gold cheap vs silver) → **LONG XAU + SHORT XAG**
- Exit when **|z| ≤ 0.5** (mean-reversion captured with hysteresis to
  avoid chop) OR after **10 trading bars** (timeout)

The strategy escapes the **GS-7 cost cliff** binding constraint that
closed the last 4 iters by replacing the small per-trade single-asset
edge with a stationary-spread reversion magnitude that — if the spread
is empirically cointegrated — can deliver per-trade gross moves >> cost
floor.

## Primary citation

`[algo_trading_chan, p.51-58, ch.2]` — Bollinger band z-score MR on
cointegrated pairs. Chan's worked GLD-USO example: APR 17.8%, Sharpe
0.96 net of costs over 2009-2011 with weekly z-score reset.

## Additional citations

- `[algo_trading_chan, p.71-73, ch.3]` — z-score grammar + entry/exit
  threshold construction (z>+2 entry, |z|≤0.5 exit hysteresis).
- `[algo_trading_chan, p.47, ch.2]` — half-life lookback rule (60d ≈
  Chan's typical pair half-life on weekly-to-monthly pairs; daily TF
  matches our resampling).
- `[algo_trading_chan, p.183-184, ch.8]` — time-based exit (timeout)
  preferred over backtest-fitted stop-loss for spread MR.
- `[advances_fin_ml, p.31-34]` — cost-realistic backtest discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials = 7+1=8`.
- Web (background, not basis): Engle-Granger 1987 *Econometrica* 55(2)
  for cointegration ADF foundation; commodity-pair literature
  (gold-silver ratio mean-reversion observed empirically since 1971
  abandonment of bimetallic standard).

## Edge source

XAUUSD buy-hold misses the **relative-value reversion** between gold
and silver. The two metals share macro drivers (real rates, USD
strength, inflation expectations) but trade with different industrial
exposure (silver ~50% industrial vs gold ~5%) — this drives short-term
divergences that the long-run cointegration reverts. Pair MR captures
the spread without taking a directional view on either metal alone.

## Datasets

- **gld_long** — GLD daily inner-join SLV daily → 2006-04-28 → 2026-04-15,
  ~5,000 bars / 19.97 y. SLV launched 2006-04-28 so this is the longest
  available silver counterpart; GLD's 2004-2006 stub is dropped.
  Multi-regime: 2008 GFC + 2011 silver-rally peak + 2015-2018 stagnation
  + 2019+ revival.
- **xauusd_real** — XAUUSD spot daily ∩ XAGUSD spot daily,
  2020-01-02 → 2026-04-17, 1,700 bars / 6.29 y. Direct instrument
  validation matching iter 001-007 short-window dataset.
- **xauusd_intraday** — XAUUSD 1h ∩ XAGUSD 1h, 2020-01-02 → 2026-04-17,
  ~32 k bars / 6.29 y, 5,119 bars/yr. Tests whether intraday-frequency
  spread MR clears costs at 1h reversion timescales (Chan p.71-73
  notes intraday spread MR has historically harvested faster cycles
  on more-liquid pairs).

## Timeframes used

`1d` and `1h` — both directly available from Tiingo cache. No 30m/15m/1m
requested → **no cTrader fetch iter prerequisite**.

## Broker tracks targeted

`broker_track: "pepperstone_cfd"` (Track A only).

**Track B (Inter ETF) is structurally non-viable**: spread MR requires
**SHORTING XAGUSD or SLV**, which Brazilian retail US accounts cannot
do on Inter Internacional (long-only restriction per
`INFRASTRUCTURE.md` §"Track B"). Reported per-track metrics will only
include Track A.

## Hold-time profile (HARD GATE)

- Expected mean hold: **~5-12 trading days** (Chan's typical pair MR
  half-life range; daily TF; |z|≤0.5 exit cuts hold below the natural
  z-cross-zero hold). Likely **swing-extended** on the upper end.
- Intraday-only: NO (daily TF; 1h variant tests intraday spread cycles).
- If mean hold > 5 days: tier capped at **STRONG**, not WINNER. Acceptable
  given the binding goal is to find the FIRST positive-Sharpe stream that
  beats buy-hold cross-dataset (which 7 prior iters all missed) — the
  hold-gate refinement is second-order and addressable in a follow-up
  iter via tighter exit thresholds.

## Pre-validation screen (mandatory per IC-6 + augmented per GS-7 corollary)

**Augmented cost-aware pre-val** (NEW per iter 007 Option C — adopted
here as the reference template for iter 008+):

```python
def cost_aware_pre_val(
    fwd_returns_bps: np.ndarray,        # forward N-bar log return on the spread position
    cost_floor_bps: float = 30.0,       # pair cost: 8 bps gold + ~20 bps silver + slip = 30 bps RT
    margin: float = 1.5,                # 1.5× cost floor as required edge
    min_t_stat: float = 1.0,            # tighter than legacy 0.5
    min_hit_rate: float = 0.50,         # tighter than legacy 0.45
    min_events: int = 30,               # pair signals are rarer; relax from 50
) -> dict:
    n = len(fwd_returns_bps)
    mean_bps = float(fwd_returns_bps.mean())
    std_bps = float(fwd_returns_bps.std(ddof=1))
    t_stat = mean_bps / (std_bps / np.sqrt(n)) if std_bps > 0 else 0.0
    hit_rate = float((fwd_returns_bps > 0).mean())
    required_edge = margin * cost_floor_bps  # 45 bps
    passed = (
        n >= min_events
        and mean_bps > required_edge
        and t_stat > min_t_stat
        and hit_rate > min_hit_rate
    )
    return {
        "n_events": n, "mean_fwd_bps": mean_bps, "t_stat": t_stat,
        "hit_rate": hit_rate, "required_edge_bps": required_edge,
        "cost_floor_bps": cost_floor_bps, "passed": passed,
    }
```

**Plus stationarity check** (Chan p.51-58 cointegration prerequisite):

- ADF test on `log(XAU/XAG)` series → **null hypothesis (unit root) must
  reject at p < 0.05** for the spread to qualify as "stationary enough"
  for pair MR. If ADF p ≥ 0.05 on a dataset, that dataset's pair-MR
  result is reported but with a STATIONARITY-FAIL caveat, and the
  candidate cannot be a WINNER on that dataset.

**Pre-val screens** (run before Stage 3 backtest):

| dataset | ADF target | cost-aware fwd-edge target |
|---|---|---|
| gld_long (1d, 60d lookback, fwd 10d) | p < 0.05 | mean fwd-10d spread move > 45 bps |
| xauusd_real (1d, 60d lookback, fwd 10d) | p < 0.05 | mean fwd-10d spread move > 45 bps |
| xauusd_intraday (1h, 60-bar lookback, fwd 24-bar) | p < 0.05 | mean fwd-24h spread move > 45 bps |

If ALL 3 datasets fail BOTH gates → hard abort the iter at Stage 3 entry
(saves DSR trial; iter recorded as "pre-val auto-aborted, GS-8 candidate
closure"). If at least 1 dataset passes both gates → proceed to full
backtest on all 3 (need cross-dataset evidence per WINNER condition).

## Cost model (Track A only)

**Per-pair round-trip on Pepperstone**:

| component | per-pair-RT (bps) | rationale |
|---|---:|---|
| Gold leg spread (XAUUSD) | 8.0 | iter 001+ baseline (Pepperstone Razor avg + slip) |
| Silver leg spread (XAGUSD) | 20.0 | XAGUSD spreads ~2.5× gold's at PEP (silver less liquid in spot) — conservative; verify via cTrader live spec in future iter |
| Slippage (pair execution) | 2.0 | Pair execution introduces tracking error vs single-asset; conservative |
| **Total spread RT** | **30.0** | Combined entry+exit costs |
| Net swap (long+short ≈ wash) | ~0 | Long+short legs cancel approximately; conservative net 0 bps/night |
| Weekend hold | ~0 | Net swap ≈ 0 → weekend mult negligible |

**Why pair swap ≈ 0**: on Pepperstone XAUUSD, long pays −1 bps/night,
short pays +0.3 bps/night; on XAGUSD assume similar asymmetry (long
−0.6, short +0.2 bps/night). Net pair swap = −1.0 + 0.2 = −0.8 bps OR
+0.3 − 0.6 = −0.3 bps depending on direction → ≤ 1 bps/night magnitude.
Over a 10-day hold this is < 10 bps cumulative, well under spread cost.
**Conservatively model as 0 net swap; if backtest is borderline,
re-run with −0.5 bps/night to verify robustness.**

## Kill criteria (pre-committed before backtest)

The hypothesis is **falsified** (FAIL/NEAR_FAIL tier) at end of Stage 3
if ANY of:

1. **Pair gross-negative on ≥ 2 of 3 datasets** (i.e., the spread does
   not mean-revert in the direction the z-score predicts on the test
   window). Same closure pattern as GS-4/5/6 cross-dataset failure.
2. **Per-trade gross < 30 bps on ≥ 2 of 3 datasets** (≤ 1× cost floor;
   no margin → cost-cliff replay even though signal exists).
3. **ADF stationarity rejected (p ≥ 0.05) on ≥ 2 of 3 datasets** AND
   the gross-Sharpe on those same datasets is also < 0 (spread is not
   stationary AND not directionally usable → no escape mechanism).
4. **Net Sharpe < buy-hold − 0.50 on ≥ 2 of 3 datasets** AFTER costs
   (analogue of the iter 003 "rescued but still trails by 0.38-0.86"
   scenario; large negative gap implies even an IC-7 secondary role
   wouldn't help).

If kill criterion fires → close the family in DEAD_ENDS as **GS-8**
("XAU/XAG ratio MR cost-or-stationarity dominated"). If it does NOT
fire AND any condition meets winner thresholds → declare per
WINNER_AND_RANKING.md.

## Why this is structurally NEW (vs all 7 prior iters + IC-1..IC-8)

| dimension | priors (001-007) | iter 008 |
|---|---|---|
| Universe | single-asset XAU(USD)/GLD | **two-asset (XAU+XAG)** |
| Direction | long-only or bidirectional single | **dollar-neutral pair (long-short simultaneously)** |
| Edge thesis | timing of single-asset price moves | **stationary-spread reversion (cointegration)** |
| Cost cliff exposure | 8 bps RT spread vs ~1-15 bps gross edge → 1:5 to 1:1 | 30 bps RT pair cost vs hopefully ~50-500 bps spread reversion → 1.5:1 to 16:1 |
| GS-1..GS-7 closure | applies to single-asset MR/trend/macro/calendar/z-score | **does NOT apply** (spread is a different family entirely) |
| IC-1..IC-8 closure | none vol-target wraps a pair signal here; no double regime gate; not 50/50; not modulation; not cross-section ranking; pre-val ✓ planned; not yet IC-7 candidate; pre-commit single cfg ✓ | **all clear** |

This is the FIRST iter testing a **two-asset spread** mechanism on this
loop, opening a structurally orthogonal family.

## Expected budget

- **Configs to test**: 1 pre-committed (lookback=60, z_entry=2.0,
  z_exit=0.5, timeout=10) per IC-8.
- **Wall-time**: ~30-45 min (pair construction + ADF + pre-val + 3
  full backtests with 7-gate battery).
- **Files to create**:
  - `iterations/008-*/hypothesis.md` (this file)
  - `iterations/008-*/test_pair_mr_signal.py` (TDD, signal correctness)
  - `iterations/008-*/run_backtest.py` (end-to-end engine)
  - `iterations/008-*/results.json` (raw metrics)
  - `iterations/008-*/pre_val.json` (ADF + cost-aware fwd-edge)
  - `iterations/008-*/verdict.json` (score result)
  - `iterations/008-*/final_report.md`

## Implementation plan

1. **Pair constructor** — for each dataset, inner-join gold leg + silver
   leg on timestamp index. Compute `log_ratio = log(close_gold / close_silver)`.
   Drop NaNs.
2. **Stationarity test (ADF)** — `statsmodels.tsa.stattools.adfuller`
   on the full log-ratio series per dataset. Record p-value.
3. **Signal generator** — rolling z-score of `log_ratio` over `lookback`
   (60 d on daily, 60 bar on 1h). State machine:
   - `pos = 0` (flat); enter `pos = -1` (short ratio = short XAU + long XAG)
     when `z > +2`; enter `pos = +1` when `z < −2`.
   - Hold until `|z| ≤ 0.5` OR `bars_held ≥ timeout` → exit to flat.
   - One position at a time (no pyramiding).
4. **Cost-aware pre-val** — for each entry signal, compute the
   forward-N-bar log return of the dollar-neutral pair position. Apply
   cost-aware gate (45 bps required edge, t≥1.0, hit≥0.5).
5. **Full backtest** — daily/hourly P&L = `pos × (gold_log_ret −
   silver_log_ret)`. Apply spread cost on entry+exit. Apply zero swap
   (verify in sensitivity check).
6. **TDD** — `test_pair_mr_signal.py` covers (a) ratio computation
   correctness on a 5-bar fixture, (b) z-score windowing, (c) entry/exit
   transitions, (d) timeout behavior, (e) cost arithmetic, (f) gross
   vs net P&L parity with a numpy-pure reference (this satisfies G7
   cross-lib gate by construction).
7. **Metrics** — Sharpe (annualized), CAGR, MDD per dataset; PBO
   (sub-window comparison: 4 non-overlapping splits per dataset, each
   yielding a Sharpe estimate; rank-based PBO via small grid permuted
   on lookback ∈ {30,60,90} as the only param-axis in the small grid);
   DSR with cumulative_n_trials=8; WF (8 windows, MDD<25%); OOS 70/30;
   FWD post-2022; Bootstrap 99.9% CI; G7 cross-lib parity (numpy ref
   built in).
8. **Score + report** — call `scoring.score_strategy(...)` + check
   hold-time gate (mean trading-day hold).
