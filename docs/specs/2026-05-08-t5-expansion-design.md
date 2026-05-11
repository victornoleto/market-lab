# T5 Expansion — Design Spec (Carver vol-target sub-phases T5b/T5d + light grid)

**Date:** 2026-05-08
**Author:** Victor Noleto (via Claude Code brainstorm)
**Status:** Draft — pending user approval before plan phase
**Parent study:** `studies/letf_rotation_hunt/` (closed 2026-05-06; reopening as formal methodology amendment per §16-style of `STUDY_FINAL_REPORT.md`)
**Original parent spec:** `studies/letf_rotation_hunt/SPEC.md` §2.6 T5 sub-phases

---

## 0. TL;DR

Expand T5 (Carver vol-target tier) from the current 2 configs (T5a, T5c) to **~20 configs** across 4 new iters (022-025). Adds the two skipped sub-phases — **T5b (carry forecast, per-asset)** and **T5d (HRP/ERC weighting)** — plus a focused robustness grid on `sigma_target`, `IDM`, and pool variants. Treated as a **formal study reopening** with cumulative DSR re-computation across all 406 prior configs and methodology disclosure in `STUDY_FINAL_REPORT.md` §17.

**Operative metric:** Sortino (post-close reanalysis canonical), not Sharpe. KILL threshold = canonical Sortino 1.272 (Track A) `[advances_fin_ml, p.208-211]` anti-curve-fit margin.

**Expected outcome:** Verdict T5 (KILL FIRES — Carver does not generalize to small-pool LETF universe) likely to hold. Expansion produces stronger evidence, not a winner. This is documented honestly in §17 disclosure.

---

## 1. Motivation and scope

### 1.1 Why expand

Original T5 had only 2 configs while sibling tiers had T2=11, T3=7, T4=4 (sub-phases) — and T1d=360 (grid). The asymmetry was a result of:

1. **T5b (carry forecast) skipped** because original spec did not pre-arrange yield-curve / dividend data (`run_iter_t5.py:13-15`).
2. **T5d (HRP weighting) marked optional** in spec §2.6 and skipped to ship faster.

User requested coherence with peer tiers. This expansion delivers ~20 configs (between T2/T3/T4 sizing and T1d's robustness grid) — sufficient to defend the T5 verdict statistically without explosive cross-product cost.

### 1.2 Scope (what is in)

- New sub-phase **T5b**: per-asset carry forecast (Carver `[systematic_trading, ch.9 p.180-190]`).
- New sub-phase **T5d**: HRP weighting (López de Prado `[advances_fin_ml, ch.16 p.221-228]`) and ERC weighting (Maillard et al. via standard ERC formulation, cited via `[risk_parity_fundamentals, ch.4]`).
- **T5a-grid**: `sigma_target` sweep on QLD single-asset (5 configs).
- **T5c-grid**: focused subset of `IDM × pool variants` (7 configs, not full cross-product).
- **DSR cumulative re-computation** for all 406 prior configs.
- Reports amendment: `TIER_5_REPORT.md` post-close note + `STUDY_FINAL_REPORT.md` §17.

### 1.3 Out of scope

- T1/T2/T3/T4 expansion. Only T5.
- New canonical winner replacement. Verdict T3d K=2 stands unless T5-expansion-best clears Sortino 1.272 (extremely unlikely per the §3 diagnosis in `TIER_5_REPORT.md`).
- Mandate §1 changes. Capital remains 100% Plano C; Strategy B DORMANT regardless of expansion outcome.
- Live deployment. Pure post-mortem methodology work.

### 1.4 Mandate alignment

Per `CLAUDE.md` mandate §1, Strategy B is in MAINTENANCE MODE. This expansion is **post-mortem methodology completeness work**, not capital allocation. No conflict with §1. Disclosure in §17 will state this explicitly.

---

## 2. Architecture

### 2.1 Module map

**New modules** (in `studies/letf_rotation_hunt/`):

| File | Purpose |
|------|---------|
| `signals_carry.py` | Per-asset carry forecast (Carver ch.9). Composes EWMAC+carry. |
| `data_loader_yields.py` | Dividend yield (yfinance), constant-maturity yields (^IRX/^TNX/^TYX), with parquet cache in `data/external/yields/`. |
| `strategies/hrp_weighter.py` | HRP and ERC weighting schemes (rolling). |
| `run_iter_t5_extended.py` | Extended dispatcher accepting `forecast_type` and `weighting_scheme` config keys. |

**New configs** (in `studies/letf_rotation_hunt/configs/`):

| File | Sub-phase | # configs |
|------|-----------|-----------|
| `iter_022_t5a_sigma_sweep.yaml` | T5a-grid | 5 |
| `iter_023_t5b_carry.yaml` | T5b | 4 |
| `iter_024_t5c_grid.yaml` | T5c-grid | 7 |
| `iter_025_t5d_hrp_erc.yaml` | T5d | 4 |
| **Total** | | **20** |

**New scripts**:

| File | Purpose |
|------|---------|
| `scripts/dsr_recompute_cumulative.py` | Re-runs `g2_dsr_p_value` cumulative for all 406 prior configs with `n_trials = 426` (or final post-expansion count). Updates verdict.json files in place; preserves history via git. |

**Modified files** (read-only or additive only):

| File | Change |
|------|--------|
| `studies/letf_rotation_hunt/runners/run_iter_t5.py` | Untouched. Existing iters 020-021 keep current behavior. |
| `studies/letf_rotation_hunt/core/gates.py` | Untouched. Re-execution uses existing `g2_dsr_p_value`. |
| `studies/letf_rotation_hunt/core/scoring.py` | Untouched. |
| `studies/letf_rotation_hunt/reports/TIER_5_REPORT.md` | Add post-`> ⚠️ Post-close` note and new §-N for expansion results. |
| `studies/letf_rotation_hunt/reports/STUDY_FINAL_REPORT.md` | Add §17 "Methodology change disclosure (T5 expansion, 2026-05-08)". |
| `docs/CURRENT_STATE.md` | Add T5-expansion to active work, then move to history when complete. |

### 2.2 Why a separate `_extended` dispatcher

`run_iter_t5.py` is referenced by closed-study artifacts (iter_020/021 verdicts cite its module path). Adding optional kwargs there would not break behavior, but creating `run_iter_t5_extended.py` makes the methodology-change boundary explicit: anything new uses the extended dispatcher; anything already-shipped uses the original. This matches the project's existing pattern of segregating post-close work (`sortino_reanalysis/` directory).

The dispatcher router in `run_iter.py` (or wherever iter dispatch lives) gets a single new branch: if `tier in {"T5a", "T5b", "T5c", "T5d"}` AND config has `forecast_type` or `weighting_scheme` keys → use `run_iter_t5_extended`; else → original `run_iter_t5`.

---

## 3. Components — detailed design

### 3.1 `signals_carry.py`

**Public API:**

```python
def compute_carry_forecast(
    asset: str,
    asset_prices: pd.Series,
    ffr_daily: pd.Series,
    fdm: float = 1.0,
) -> pd.Series:
    """Per-asset carry forecast, Carver [systematic_trading, ch.9 p.180-190].

    carry_raw[t] = expected_yield[t] - leverage * FFR[t]
    carry_norm[t] = (carry_raw / rolling_std(carry_raw, 252)) * scalar * fdm
    forecast = carry_norm.clip(-20, 20)

    Args:
        asset: ticker (e.g., "UPRO", "QLD", "TMF", "ZROZ", "UGL")
        asset_prices: daily close prices (for index alignment only)
        ffr_daily: federal funds rate daily series, decimal annual
        fdm: forecast diversification multiplier (default 1.0 standalone;
             1.41 if composed with EWMAC composite per Carver Table 49)

    Returns:
        pd.Series indexed like asset_prices, NaN where yield data unavailable.
    """
```

**Asset → (yield_source, leverage) mapping** (single source of truth in module):

| Asset | Yield source | Leverage | Notes |
|-------|--------------|----------|-------|
| UPRO  | SPY trailing 12m div yield | 3 | S&P 500 3x |
| QLD   | QQQ trailing 12m div yield | 2 | NDX 2x |
| TQQQ  | QQQ trailing 12m div yield | 3 | NDX 3x (if pool extends) |
| TMF   | ^TYX (30y CMT) | 3 | 20y+ Treasury 3x |
| ZROZ  | ^TYX (30y CMT) | 1 | STRIPS 25y+, unleveraged off-asset |
| UGL   | 0 (gold has no yield) | 2 | Gold 2x |

`scalar` calibrated per Carver `[ch.9 p.183]`: target carry forecast SD = 10 (Carver convention) → scalar set so that `(carry_raw / rolling_std(carry_raw, 252)) * scalar` has SD ≈ 10 over the calibration window. Per-asset-class scalars are **calibrated empirically during the implementation plan phase** by running the carry computation on lh_56y data and measuring SD. Initial placeholders: `_CARRY_SCALAR_BY_CLASS_INITIAL = {"equity": 10.0, "bond": 10.0, "gold": 0.0}` (gold short-circuits to zero forecast — no carry semantics for non-yielding asset).

**Composition with EWMAC** (used by T5b configs):

```python
def compose_ewmac_carry(
    ewmac: pd.Series, carry: pd.Series, fdm: float = 1.41,
) -> pd.Series:
    """50/50 blend per Carver [ch.9 p.185]. Assumes both inputs already
    individually scaled to SD~10. FDM 1.41 = 2-forecast diversification."""
    return ((ewmac + carry) / 2.0 * fdm).clip(-20, 20)
```

### 3.2 `data_loader_yields.py`

**Public API:**

```python
def load_dividend_yield(underlying: str) -> pd.Series:
    """Trailing 12m dividend yield for SPY/QQQ/etc.

    Cache: data/external/yields/{underlying}_divyield.parquet
    Source: yfinance Ticker.dividends + Ticker.history (Adj Close).
    Computation: rolling 365d sum of dividends / current adj close.
    Pre-1993 (SPY inception): constant = historical mean (warning logged).

    Returns daily series, decimal (e.g., 0.018 = 1.8%).
    """

def load_constant_maturity_yield(tenor: str) -> pd.Series:
    """Tenor in {"3m", "10y", "30y"} → ^IRX, ^TNX, ^TYX.

    Cache: data/external/yields/cmt_{tenor}.parquet
    Source: yfinance primary; FRED fallback (DGS3MO, DGS10, DGS30).
    Pre-^TYX-inception (1977): constant = historical mean.

    Returns daily series, decimal (e.g., 0.044 = 4.4%).
    """
```

**Caching policy**: write parquet on first fetch. Tests mock both functions to avoid network.

**Pre-data fallback**: if asked for a date before data start, use class-level historical mean and emit `logger.warning("yield data pre-{start_date} fallback to mean for {asset}")`. Document this clearly in the §17 disclosure as a known limitation for the `lh_56y` window (1970-1993 portion).

### 3.3 `strategies/hrp_weighter.py`

**Public API:**

```python
def compute_hrp_weights(
    returns: pd.DataFrame, lookback: int = 252, min_periods: int = 126,
) -> pd.DataFrame:
    """Hierarchical Risk Parity weights, López de Prado
    [advances_fin_ml, ch.16 p.221-228].

    Steps:
      1. corr matrix from rolling returns (last `lookback` rows)
      2. distance d[i,j] = sqrt(0.5 * (1 - corr[i,j]))
      3. linkage (single)
      4. quasi-diagonalization (sort cluster order)
      5. recursive bisection: split assets into two halves per quasi-diag
         order, allocate inversely to each half's cluster variance.

    Returns DataFrame indexed like returns, columns = returns.columns,
    rows sum to 1. NaN for first `min_periods` rows.
    """

def compute_erc_weights(
    returns: pd.DataFrame, lookback: int = 252, min_periods: int = 126,
    max_iter: int = 50, tol: float = 1e-6,
) -> pd.DataFrame:
    """Equal Risk Contribution weights via Newton iteration on
    risk-budget constraint. Each asset contributes equal marginal risk
    to portfolio variance."""
```

**Integration with `build_positions`**: new optional parameter `external_weights: pd.DataFrame | None = None`. If provided, replaces the IDM-uniform allocation step.

The current `build_positions` (T5 baseline) computes per-asset position as:
```
position[asset, t] = (forecast[asset, t] / 10) * (sigma_target / vol[asset, t]) * idm * (1 / N_assets)
```
where the implicit `(1 / N_assets) * idm` is the equal-weight × diversification multiplier.

With `external_weights` provided, this becomes:
```
position[asset, t] = (forecast[asset, t] / 10) * (sigma_target / vol[asset, t]) * external_weights[asset, t]
```
where `external_weights` rows sum to 1 and absorb the diversification structure directly (HRP allocates to clusters; ERC equalizes risk contributions). No additional IDM multiplier is applied — that would double-count the diversification benefit.

**Note:** when `weighting_scheme ∈ {"hrp", "erc"}`, configs explicitly set `idm: 1.0` to make this routing unambiguous. The diversification factor is encoded in `external_weights`, not `idm`.

### 3.4 `run_iter_t5_extended.py`

Wraps `_run_single_voltarget_config` from `run_iter_t5.py` with two additional config dimensions:

- `forecast_type ∈ {"ewmac", "ewmac_carry", "carry_only"}` (default `"ewmac"`)
- `weighting_scheme ∈ {"idm", "hrp", "erc"}` (default `"idm"`)

Logic:

```python
if forecast_type == "ewmac":
    forecast = _compute_ewmac_composite_forecast(prices, fdm)
elif forecast_type == "carry_only":
    forecast = signals_carry.compute_carry_forecast(asset, prices, ffr_daily, fdm=1.0)
elif forecast_type == "ewmac_carry":
    ewmac = _compute_ewmac_composite_forecast(prices, fdm=1.0)
    carry = signals_carry.compute_carry_forecast(asset, prices, ffr_daily, fdm=1.0)
    forecast = signals_carry.compose_ewmac_carry(ewmac, carry, fdm=1.41)

if weighting_scheme == "idm":
    positions = build_positions(forecasts, vols, sigma_target, idm, ...)
elif weighting_scheme in {"hrp", "erc"}:
    weights = compute_hrp_weights(returns) if scheme == "hrp" else compute_erc_weights(returns)
    positions = build_positions(forecasts, vols, sigma_target, idm=1.0,
                                external_weights=weights, ...)
```

Everything else (gates, metrics, scoring, artifact writing) reuses `run_iter_t5._run_single_voltarget_config`'s downstream code unchanged.

---

## 4. Configs — exact contents

### 4.1 `iter_022_t5a_sigma_sweep.yaml` — T5a sigma_target sweep (5 configs)

```yaml
iter: 022-2026-05-08-T5a-sigma-sweep
tier: T5a
hypothesis: |
  Sweep sigma_target over {0.15, 0.20, 0.25, 0.30, 0.35} on T5a single-asset
  QLD vol-target. 0.25 = Half-Kelly Carver baseline [systematic_trading, ch.10 p.198].
  Tests if T5a Sharpe 0.587 was driven by sigma choice or by structural
  under-allocation (per TIER_5_REPORT §3).
primary_citation: "[systematic_trading, ch.10 p.198]; spec §2.6 T5a; T5-expansion §3.1"
configs_tested:
  - {name: voltarget_qld_sigma015, pool: [QLD], off_asset: ZROZ,
     sigma_target: 0.15, idm: 1.0, position_inertia: 0.10}
  - {name: voltarget_qld_sigma020, pool: [QLD], off_asset: ZROZ,
     sigma_target: 0.20, idm: 1.0, position_inertia: 0.10}
  - {name: voltarget_qld_sigma025, pool: [QLD], off_asset: ZROZ,
     sigma_target: 0.25, idm: 1.0, position_inertia: 0.10}  # = iter_020 baseline
  - {name: voltarget_qld_sigma030, pool: [QLD], off_asset: ZROZ,
     sigma_target: 0.30, idm: 1.0, position_inertia: 0.10}
  - {name: voltarget_qld_sigma035, pool: [QLD], off_asset: ZROZ,
     sigma_target: 0.35, idm: 1.0, position_inertia: 0.10}
cumulative_n_trials_at_iter: 406  # set by orchestrator before run
datasets: [lh_56y, modern_1990, spy_real, ndx_real]
windows_used: # same as iter_020
random_seed: 42
```

### 4.2 `iter_023_t5b_carry.yaml` — T5b carry forecast (4 configs)

```yaml
iter: 023-2026-05-08-T5b-carry
tier: T5b
hypothesis: |
  Per-asset carry forecast (Carver ch.9). Tests if (a) carry_only delivers
  signal independent of EWMAC and (b) ewmac_carry composite (FDM=1.41)
  outperforms EWMAC alone via diversified forecasts.
primary_citation: "[systematic_trading, ch.9 p.180-190]; spec §2.6 T5b; T5-expansion §3.1"
configs_tested:
  - {name: carry_only_qld_sigma025, pool: [QLD], off_asset: ZROZ,
     sigma_target: 0.25, idm: 1.0, position_inertia: 0.10,
     forecast_type: carry_only}
  - {name: ewmac_carry_qld_sigma025, pool: [QLD], off_asset: ZROZ,
     sigma_target: 0.25, idm: 1.0, position_inertia: 0.10,
     forecast_type: ewmac_carry}
  - {name: carry_only_multi4_sigma025, pool: [UPRO, QLD, UGL, TMF],
     off_asset: ZROZ, sigma_target: 0.25, idm: 2.5, position_inertia: 0.10,
     forecast_type: carry_only}
  - {name: ewmac_carry_multi4_sigma025, pool: [UPRO, QLD, UGL, TMF],
     off_asset: ZROZ, sigma_target: 0.25, idm: 2.5, position_inertia: 0.10,
     forecast_type: ewmac_carry}
cumulative_n_trials_at_iter: 411
datasets: [lh_56y, modern_1990, spy_real, ndx_real]
random_seed: 42
```

### 4.3 `iter_024_t5c_grid.yaml` — T5c IDM × pool grid (7 configs)

```yaml
iter: 024-2026-05-08-T5c-grid
tier: T5c
hypothesis: |
  Focused IDM × pool sweep on multi-asset T5c. Tests robustness of the
  Carver IDM=2.5 cap [p.170-171] and pool composition sensitivity. Ablations:
  no-gold, no-bond, HFEA-Trinity {UPRO, TMF, UGL}.
primary_citation: "[systematic_trading, ch.10 p.170-171, ch.11]; spec §2.6 T5c"
configs_tested:
  - {name: voltarget_multi4_idm15, pool: [UPRO, QLD, UGL, TMF],
     off_asset: ZROZ, sigma_target: 0.25, idm: 1.5, position_inertia: 0.10}
  - {name: voltarget_multi4_idm20, pool: [UPRO, QLD, UGL, TMF],
     off_asset: ZROZ, sigma_target: 0.25, idm: 2.0, position_inertia: 0.10}
  - {name: voltarget_multi4_idm25, pool: [UPRO, QLD, UGL, TMF],
     off_asset: ZROZ, sigma_target: 0.25, idm: 2.5, position_inertia: 0.10}  # = iter_021 baseline
  - {name: voltarget_no_gold_idm22, pool: [UPRO, QLD, TMF],
     off_asset: ZROZ, sigma_target: 0.25, idm: 2.2, position_inertia: 0.10}
  - {name: voltarget_no_bond_idm22, pool: [UPRO, QLD, UGL],
     off_asset: ZROZ, sigma_target: 0.25, idm: 2.2, position_inertia: 0.10}
  - {name: voltarget_hfea_trinity_idm22, pool: [UPRO, TMF, UGL],
     off_asset: ZROZ, sigma_target: 0.25, idm: 2.2, position_inertia: 0.10}
  - {name: voltarget_hfea_trinity_idm25, pool: [UPRO, TMF, UGL],
     off_asset: ZROZ, sigma_target: 0.25, idm: 2.5, position_inertia: 0.10}
cumulative_n_trials_at_iter: 415
datasets: [lh_56y, modern_1990, spy_real, ndx_real]
random_seed: 42
```

### 4.4 `iter_025_t5d_hrp_erc.yaml` — T5d HRP/ERC weighting (4 configs)

```yaml
iter: 025-2026-05-08-T5d-hrp-erc
tier: T5d
hypothesis: |
  HRP and ERC replace IDM uniform. Tests if cluster-aware weighting
  (López de Prado [ch.16]) or Equal Risk Contribution improves over IDM=2.5
  on the 4-LETF pool. 2x sigma_target levels (0.25, 0.30) per scheme.
primary_citation: "[advances_fin_ml, ch.16 p.221-228]; spec §2.6 T5d (optional)"
configs_tested:
  - {name: hrp_multi4_sigma025, pool: [UPRO, QLD, UGL, TMF],
     off_asset: ZROZ, sigma_target: 0.25, idm: 1.0, position_inertia: 0.10,
     weighting_scheme: hrp}
  - {name: hrp_multi4_sigma030, pool: [UPRO, QLD, UGL, TMF],
     off_asset: ZROZ, sigma_target: 0.30, idm: 1.0, position_inertia: 0.10,
     weighting_scheme: hrp}
  - {name: erc_multi4_sigma025, pool: [UPRO, QLD, UGL, TMF],
     off_asset: ZROZ, sigma_target: 0.25, idm: 1.0, position_inertia: 0.10,
     weighting_scheme: erc}
  - {name: erc_multi4_sigma030, pool: [UPRO, QLD, UGL, TMF],
     off_asset: ZROZ, sigma_target: 0.30, idm: 1.0, position_inertia: 0.10,
     weighting_scheme: erc}
cumulative_n_trials_at_iter: 422
datasets: [lh_56y, modern_1990, spy_real, ndx_real]
random_seed: 42
```

**Total new configs:** 5 + 4 + 7 + 4 = **20**. Final cumulative `n_trials = 426`.

---

## 5. Methodology, gates, metric

### 5.1 Operative metric

**Sortino as primary** (per post-close reanalysis canonical, `SORTINO_REANALYSIS_REPORT.md`). Sharpe reported as secondary for backward comparison with iter 020/021.

**KILL T5-expansion threshold:** canonical Sortino 1.272 (Track A: T3d K=2 sma250/100 winner Sortino + 0.05 anti-curve-fit `[advances_fin_ml, p.208-211]`). T5-expansion-best Sortino must exceed 1.272 to displace winner; otherwise verdict T5 (KILL FIRES) is reinforced.

### 5.2 Gates (no changes to gate logic)

All 7 gates from `gates.py` unchanged:
- G1 PBO (computed within each iter's configs)
- G2 DSR p-value (local within iter, AND cumulative across full study)
- G3 walk-forward
- G4 OOS 70/30
- G5 fwd post-2020
- G6 bootstrap 99% CI low
- G7 cross-lib CAGR delta

### 5.3 DSR cumulative re-computation

**Trigger:** after iter_025 completes, `n_trials_cumulative` becomes 426.

**Action:** `scripts/dsr_recompute_cumulative.py` walks all 21 prior iter directories (iters 000-021 in `runs/original/` plus 022, 023 = T3d sortino-era) and recomputes `g2_dsr_p_cumulative` for every config using `n_trials = 426`. Writes back to each config's verdict.json under a new key `g2_dsr_p_cumulative_v2_post_t5_expansion`. Original keys preserved for historical fidelity.

**Acceptance:** any prior config whose `g2_dsr_p_cumulative_v2` flips from PASS (<0.05) to FAIL (≥0.05) is flagged in §17 disclosure. **Track A winner `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` MUST remain PASS after re-correction** — if it does not, the expansion is documented as having invalidated the canonical winner and the user is asked to re-evaluate before any further work.

**Why use cumulative N=426 not 406:** DSR (Bailey & López de Prado 2014) requires the multiple-testing N at which the maximum Sharpe across all tested strategies is observed. Reopening the study extends N to 426. Anything else is statistically misleading `[advances_fin_ml, p.208]`.

### 5.4 Reports amendment

**`reports/TIER_5_REPORT.md`**: insert new note between current `> ⚠️ Post-close Sortino re-analysis update (2026-05-07)` and `**Status:**` heading:

```
> ## ⚠️ Post-close T5 expansion (2026-05-08)
>
> The original T5 tier ran 2 configs (T5a, T5c). T5b/T5d were skipped per
> scope. After post-close review, T5 was reopened to add the 2 skipped
> sub-phases plus a focused robustness grid (~20 new configs in iters
> 022-025). See §17 of STUDY_FINAL_REPORT.md for full disclosure.
>
> **Verdict update:** [filled in after iter_025 completes; cite T5-expansion-best Sortino vs threshold 1.272 and whether KILL stays FIRES]
> **Body of report below preserved as-is for historical fidelity.**
```

**`reports/STUDY_FINAL_REPORT.md`**: add §17 following the same structure as §14, §15, §16 (post-close methodology disclosures already present).

§17 must cover: (a) what was added, (b) why (coherence with peer tiers), (c) cumulative DSR impact on prior 406 configs, (d) whether any prior verdict flipped, (e) updated cross-tier comparison table, (f) explicit statement of mandate §1 unchanged.

### 5.5 `docs/CURRENT_STATE.md`

Add bullet under "Active work" while in progress; move to "History" section when expansion completes. Note the date and link to this spec.

---

## 6. Data flow

```
Yields (yfinance/FRED) ──> data_loader_yields ──> cache (parquet)
                                  │
                                  ▼
                          signals_carry ────────┐
                                                ▼
prices ──> signals (EWMAC) ──> compose ──> forecast ──┐
                                                       ▼
returns ──> hrp_weighter ──> external_weights ──> build_positions ──> positions
                                                       ▼
positions × shifted_returns ──> strategy_returns ──> equity ──> metrics + gates
                                                       ▼
                                            score_strategy ──> verdict.json
                                                       ▼
                              dsr_recompute_cumulative ──> verdict_v2 (after expansion done)
```

---

## 7. Error handling

Trust internal interfaces (per CLAUDE.md "Don't add error handling for scenarios that can't happen"). Validate at boundaries only:

- **`data_loader_yields`**: validate ticker known; on missing data, fall back to historical mean with `logger.warning` (not exception). Raise `RuntimeError` only if both yfinance AND FRED fail (genuine network/data outage).
- **`signals_carry.compute_carry_forecast`**: raise `ValueError` if asset unknown to `_ASSET_YIELD_MAP`. Do not silently return zeros — that would be a silent failure (per `superpowers:silent-failure-hunter` discipline implicit in CLAUDE.md).
- **`hrp_weighter`**: raise `ValueError` if returns has <2 cols (HRP needs ≥2 assets). NaN-tolerant via `min_periods` parameter; return NaN-rows for warmup, not exceptions.
- **`run_iter_t5_extended`**: same try/except per-config pattern as `run_iter_t5.run()` — preserves study runs even if one config errors.

---

## 8. Testing strategy

Baseline: project has 813 tests; CLAUDE.md requires no breakage. New tests live in `studies/letf_rotation_hunt/tests/`.

### 8.1 Unit tests (new files)

| Test file | Coverage |
|-----------|----------|
| `tests/test_signals_carry.py` | (a) carry forecast for each asset class returns expected sign in known regimes (e.g., bond carry > 0 when 30y > 3×FFR); (b) clipping at ±20; (c) FDM composition with EWMAC; (d) NaN handling pre-data-start. |
| `tests/test_data_loader_yields.py` | Mock yfinance/FRED. Verify cache write/read, fallback to historical mean pre-inception, parquet roundtrip. |
| `tests/test_hrp_weighter.py` | (a) HRP weights sum to 1, all positive; (b) on uncorrelated assets HRP ≈ inverse-vol; (c) on perfectly correlated assets HRP ≈ equal-weight; (d) ERC convergence within max_iter; (e) reference numerical example from López de Prado `[ch.16 p.230]`. |
| `tests/test_run_iter_t5_extended.py` | (a) backward-compat: config without `forecast_type/weighting_scheme` produces identical output to `run_iter_t5.run`; (b) `forecast_type="carry_only"` produces zero-equity for gold-only universe (carry=0 → no positions); (c) `weighting_scheme="hrp"` produces non-uniform positions on a 4-LETF pool. |

### 8.2 Integration smoke

Add to `scripts/smoke_fanout_protocol.py` (or a dedicated `scripts/smoke_t5_expansion.py`): run each of the 4 new configs against a 3-year synthetic mini-universe, verify verdict.json shape and gate outputs, in <30s total.

### 8.3 DSR re-computation regression test

`tests/test_dsr_recompute_cumulative.py`: with N=2 cached prior configs and a known-Sharpe synthetic, verify recomputed `g2_dsr_p_cumulative_v2` matches expected formula output and is monotonically larger than the original (N=406) value when N grows to 426.

### 8.4 Acceptance gate before merge

- All new unit tests pass.
- 813-test baseline still passes.
- After running iter_022..025 end-to-end on real data: Track A canonical winner `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` retains G2 cumulative PASS (p<0.05 with N=426).

---

## 9. Citations bibliography

| Slug | Pages used | Use |
|------|-----------|-----|
| `systematic_trading` | ch.7-12 (98-202), ch.9 (180-190), ch.10 (170-171, 198), ch.11, Table 49 (285) | Carver vol-target framework, carry forecast, IDM, FDM, sigma_target Half-Kelly |
| `advances_fin_ml` | ch.16 (221-228), p.208-211 | HRP, DSR threshold, anti-curve-fit margin |
| `risk_parity_fundamentals` | ch.4 | ERC formulation (if available; else cite Maillard 2010 directly) |
| `leverage_for_the_long_run` | (existing citations in study) | LETF universe choice, pool composition rationale (HFEA Trinity) |

---

## 10. Open items / risks

1. **`risk_parity_fundamentals` book may not be in the project's 33-book set.** If absent, cite ERC directly via "Maillard, Roncalli & Teïletche (2010), 'The Properties of Equally Weighted Risk Contribution Portfolios'" — verify in `books/MAPPING.md` during plan phase; fall back to direct paper citation if needed.
2. **yfinance dividend data quality for SPY pre-1993 / QQQ pre-1999.** Spec calls for fallback to historical mean — this is documented in §3.2 but should be flagged in §17 disclosure as a known limitation for the `lh_56y` window.
3. **DSR re-computation could invalidate Track A winner.** §5.3 names the explicit failure mode and asks the user to re-evaluate if it triggers. Probability is low (T3d K=2 has Sharpe 0.853 with comfortable margin) but non-zero.
4. **Run time.** 20 configs × 4 datasets × ~57y of daily data is non-trivial. Estimate: ~30-60 min on the existing infrastructure (per-iter timings in iter_020/021 verdicts as benchmark). Plan phase should confirm and parallelize via `run_loop.sh` if needed.

---

## 11. Out-of-scope reminders (so we don't drift)

- No T1/T2/T3/T4 expansion.
- No new live-deployment work. Mandate §1 unchanged.
- No new metrics beyond Sortino (already canonical post-close).
- No threshold relaxation. KILL T5-expansion = canonical Sortino 1.272.
- No code in `run_iter_t5.py` modified — all new behavior in `run_iter_t5_extended.py`.

---

## 12. Approval

This spec is the **single source of truth** for the T5 expansion. Implementation plan (next phase) decomposes §3 + §4 into ordered tasks and decides parallelization. Any deviation from this spec during implementation requires updating this doc and re-getting user approval.

**Status:** Draft awaiting user review.
