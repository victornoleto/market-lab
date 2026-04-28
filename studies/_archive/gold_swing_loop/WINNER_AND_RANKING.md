# Winner conditions + ranking tiers (gold swing loop)

Two separate mechanisms:

1. **WINNER conditions (strict, binary)** — ALL 5 must hold for a
   strategy to be declared winner. This halts the shell loop.
2. **Ranking score (0-100) + tiers** — every strategy gets a score,
   so "semi-optimal" strategies are tracked, compared across
   iterations, and fed back into future research directions.

Implementation: `studies/gold_swing_loop/scoring.py`.

---

## Benchmarks (gold-complex buy-hold per dataset/cost-path)

Iter 001 already measured exact values for the original 3 datasets and
updated `scoring.py BENCHMARKS`. The new `gold_synth_40y` row (added
2026-04-26) is placeholder until first iter constructs the dataset from
FRED `PCU2122212122` or LBMA daily fix series.

| dataset | window | benchmark | Sharpe | CAGR | MDD | status |
|---|---|---|---|---|---|---|
| gld_long | 2004-11-18 → 2026-04-15 (21.4y) | GLD ETF b&h | ~0.50 | ~7.8% | ~45.6% | measured |
| xauusd_real | 2020-01-02 → 2026-04-17 (6.3y) | XAUUSD spot b&h | ~0.85 | ~13% | ~22% | measured |
| xauusd_intraday | 2020-01-02 → 2026-04-17 (6.3y, 1h bars) | XAUUSD spot b&h | ~0.85 | ~13% | ~22% | measured |
| **gold_synth_40y** (NEW) | 1986-01 → 2026-04 (~40y daily) | gold spot synth b&h | TBD | TBD | TBD | DEFERRED — first iter needing it builds it |

**Multi-asset benchmarks** (declared per iter when `universe=gold_complex`):
the iter computes its own benchmark = passive-rebalanced version of the
declared portfolio (e.g., 60% XAU + 30% GDX + 10% XAG = "passive_complex").
Edge is measured against this, not single-asset XAU.

**Cost-path adjustment**: every dataset's benchmark is run through the
declared cost path (zero for buy-hold; declared path for candidates).
For multi-cost-path strategies (`both_*`), benchmark is computed per
path independently.

---

## Part 1 — WINNER conditions (strict)

A strategy counts as **winner** if AND ONLY IF all 5 conditions hold
simultaneously. Near-misses (4/5) get ranked but do NOT set
`status: winner`.

### 1. Sharpe edge on real data (UPDATED 2026-04-26 — primary + corroborating)

- **Primary dataset**: `Sharpe_candidate ≥ Sharpe_benchmark + 0.10`
- **At least 1 corroborating dataset**: `Sharpe_candidate > 0` (positive
  Sharpe on the cost-net returns)

The strategy's hypothesis.md declares which dataset is primary and
which is corroborating. Primary is the strategy's natural fit (e.g.,
intraday strategy → primary `xauusd_intraday`).

Edge minimums per dataset when used as primary:

| dataset | minimum primary Sharpe |
|---|---|
| gld_long | 0.60 |
| xauusd_real | 0.95 |
| xauusd_intraday | 0.95 |
| gold_synth_40y | TBD (when built) |

### 2. Gate battery (UPDATED — primary + corroborating)

- **Primary dataset**: full gate count
  - gld_long primary → ≥ **5/7** gates
  - xauusd_real / xauusd_intraday primary → ≥ **4/7** gates
  - gold_synth_40y primary → ≥ **5/7** gates (when built)
- **Corroborating dataset(s)**: lighter check
  - G6 bootstrap 99% CI low > 0
  - G2 DSR p-value < 0.20 (relaxed from 0.05)
  - At minimum 1 corroborating dataset must be declared and pass these
    two relaxed gates.

Gates (same 7 as sister loop):

- G1 PBO grid-level < 0.5 `[advances_fin_ml, p.208-211]`
- G2 DSR p-value < 0.05 with n_trials cumulative `[p.222-223]`
- G3 Walk-Forward 6/8 windows, MDD < 25% per window `[ch.12]`
- G4 OOS 70/30 Sharpe > 0
- G5 FWD stress post-2022 Sharpe > 0 (gold's recent regime)
- G6 Bootstrap 99.9% CI low > 0 `[p.196-202]`
- G7 Cross-lib ±3 pp CAGR (numpy-pure reference) `[p.31-34]`

### 3. DSR with cumulative n_trials

Primary dataset DSR p-value < 0.05, using `cumulative_n_trials` from
`BASE_MEMORY.md` frontmatter. Corroborating datasets relaxed to p < 0.20.

### 4. CAGR floor (UPDATED — primary only)

`CAGR_candidate ≥ 0.8 × CAGR_benchmark` on the **primary dataset**
(NET of declared cost path). Corroborating datasets just need
`CAGR > 0` (positive — strategy isn't bleeding).

### 5. MDD ceiling (UPDATED — primary only)

`MDD_candidate ≤ MDD_benchmark + 5 pp` on the **primary dataset**.
Corroborating datasets: `MDD < 60%` (safety bound — not a comparative
measure since regime varies).

### 6. Hold-time bucket match (UPDATED 2026-04-26 — was "≤5d hard gate")

Declared `hold_time_track` must match observed `mean_hold_days`:

| track | observed mean hold bound |
|---|---|
| `intraday` | ≤ 1.0 trading day |
| `short_swing` | 2.0 ≤ mean ≤ 10.0 |
| `medium_swing` | 10.0 ≤ mean ≤ 30.0 |

- Mismatch (e.g., declared `intraday` but observed 4d) → tier downgraded
  to NEAR_FAIL regardless of score (declaration is wrong, not strategy).
- Match → no penalty; the bucket determines which broker/cost path is
  realistic (intraday on Pepperstone/futures; medium_swing on Inter ETF).
- The legacy `≤5d hard gate` is REMOVED. Medium-swing winners are
  legitimate winners — they just deploy via Track B (Inter ETF) rather
  than Track A (Pepperstone CFD intraday).

---

## Per-broker-track scoring (NEW vs sister loop)

The score above is computed against the **strategy's net-of-cost
returns** for the broker track declared in `hypothesis.md`. A single
strategy may be applicable to:

- **Track A (Pepperstone CFD)** — 8 bps spread round-trip + swap;
  long+short OK; no tax
- **Track B (Inter ETF)** — ~100 bps FX RT + ETF EER + **DARF 15%
  on monthly net profits**; LONG-ONLY; T+1 settlement (no intraday)
- **Both** — strategy works under A's full flexibility AND under B's
  long-only daily constraints

### When `broker_track = "both"`

Score is computed **separately per track** and the iter's verdict.json
includes both. Top-K ranks the **better-of-the-two** for that strategy.
Track B (Inter) typically scores 5-15 points lower than Track A on the
same strategy due to:
- DARF 15% drag on positive months (eats ~10-15% of CAGR)
- Long-only restriction (drops short-side profits)
- Higher FX cost (100 bps RT vs 8 bps spread)

A "WINNER" declaration requires the **specified primary track** to
clear all 6 conditions. If `broker_track = "both"`, both tracks must
clear independently.

### DARF model (Track B only)

```python
def apply_darf(monthly_net_returns_brl: pd.Series, rate: float = 0.15) -> pd.Series:
    """Apply 15% DARF on positive monthly net profits.
    Brazilian rule: tax accrues on monthly net profit basis;
    losing months reduce taxable base for the year (carry-forward
    not modeled here for backtest conservatism)."""
    monthly_after_tax = monthly_net_returns_brl - rate * monthly_net_returns_brl.clip(lower=0)
    return monthly_after_tax
```

R$20k/month exemption on US-equity sales is **not modeled** (assume
all sales taxable for backtest conservatism). Real-world deployment
may benefit from this exemption, increasing post-tax returns.

---

## Part 2 — Ranking score (0-100 + 5 bonus)

Every strategy gets a score. Tiers:

- 🏆 **WINNER** — score ≥ 90 AND all 5 strict conditions hold
- 🥇 **STRONG** — score 75-89
- 🥈 **PROMISING** — score 60-74
- 🥉 **MARGINAL** — score 40-59
- 📉 **NEAR_FAIL** — score 20-39
- ❌ **FAIL** — score < 20

### Scoring rubric (max 100 + 5 bonus)

| criterion | max | how it's awarded |
|---|---:|---|
| 1. Sharpe edge | 25 | datasets_beat_sharpe: 1→10, 2→20, 3→25 |
| 2. Gates per dataset + cross-bonus | 25 | per-dataset bucket + +4 if all 3 meet §0 minimums |
| 3. DSR significance (worst-p across 3 ds) | 15 | <0.05→15, <0.10→10, <0.20→5 |
| 4. CAGR floor (≥ 0.8 × bench, per ds) | 15 | 5 pts each ds passing |
| 5. MDD ceiling (≤ bench + 5pp, per ds) | 15 | 5 pts each ds passing |
| 6. Robustness bonus | 5 | non-overlapping sub-windows positivity |

**Hold-time gate (winner condition 6) is a HARD GATE** — strategy with
mean hold > 5 days CANNOT score WINNER even at 90+ rubric. Marks as
🥇 STRONG with "swing-extended" tag, surfaced in top-K but not auto-deploy.

---

## Implementation notes

`scoring.py` exposes `score_strategy(metrics, gates, cumulative_n_trials)`
matching sister loop's API. The only changes vs sister are:

- `BENCHMARKS` dict keys: `gld_long / xauusd_real / xauusd_intraday`
- `BENCHMARKS` values: gold buy-hold metrics (placeholder, iter 001 must measure)
- `GATE_THRESHOLDS`: `gld_long: 5, xauusd_real: 4, xauusd_intraday: 4`

The 5-condition strict winner check + tier mapping is identical.
