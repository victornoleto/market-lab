"""Phase 3.6 Family H — Adaptive-Markets regime-switching swing strategy.

Clean return-series simulator that (a) fits a Gaussian Hidden Markov
Model (HMM) on realized market statistics computed from SPY/TLT total
returns (volatility, return, optional correlation, optional skewness);
(b) labels the IS-derived states by regime semantics (low-vol / high-vol
/ crisis) using IS averages only; (c) maps each regime to a fixed 3-asset
allocation among SPY/TLT/GLD; (d) rebalances every N trading days with
the regime decoded at the most recent close, applied on a one-day lag
(`prev_weight × ret` alignment).

**Differentiator from V2-L2 Gayed EMA regime (rejected 2026-04-22):**
Gayed uses a simple SMA/EMA cross on *price* of a single index (SPY) as
the regime classifier `[leverage_for_the_long_run, p.8, p.13]`. Family H
deliberately does NOT use a price-cross signal. Instead, Family H fits a
probabilistic state-space model (HMM / Markov-switching) on a feature
set of **realized moments** (vol, cross-asset correlation, optionally
skew) — the Adaptive Markets Hypothesis framing of regimes as
distributional states over which investors adapt
`[adaptive_markets, p.282-283, RULE 1A]`,
`[adaptive_markets, p.287-288, ch.8]` (risk/reward only holds inside
normal regime). The classifier returns a *posterior probability* per
state; the allocation then maps regime → multi-asset mix rather than
binary ON/OFF on a single index.

Scientific anchors
------------------

* **Adaptive Markets Hypothesis (AMH):** markets are ecologies of
  heuristics whose efficiency is regime-dependent — risk/reward trade-off
  only holds in "normal" regimes; extreme regimes punish (not reward)
  risk exposure `[adaptive_markets, p.282-283, ch.8 RULE 1A-5A]`.
  Implication for strategy design: an honest regime classifier on
  statistical moments (not trend crosses) gates when to take risk vs
  when to step aside into defensive assets.

* **Hidden Markov Model (MSA) for regime detection:** Hamilton (1989)
  Markov-switching model with transition probabilities
  `P(s_t=j | s_{t-1}=i) = a_{ij}` and Gaussian emissions per state. MLE
  via the Baum-Welch EM algorithm. Expected duration in state *i*
  equals `1/(1 - a_{ii})` trading days `[fin_time_series_tsay, p.186-187,
  §4.1.4, eq.4.18]`.

* **Regime-change practical reference:** Chen & Tsang (2021) use 2-state
  HMM with Gaussian emissions on log(R) derived from Directional Change
  indicators to detect normal vs abnormal volatility regimes, confirming
  that higher-TMV/lower-T states cluster as abnormal
  `[regime_change, p.14-17, ch.2]`, `[regime_change, p.44-46, ch.4]`.
  We use realized vol directly (no DC transformation) to stay close to
  Lo's AMH distributional framing.

* **Universe rationale (broad-market SPY / long-bond TLT / gold GLD):**
  the Adaptive Markets rule 4A observes that asset-class correlations
  become non-stationary under distress, which we model by having the
  regime classifier read cross-asset signals (SPY + TLT realized vol
  and correlation) and map crisis states to GLD (defensive)
  `[adaptive_markets, p.282-283, RULE 4A]`. The 3-asset choice
  deliberately parallels canonical "risk-on / balanced / defensive"
  ecology.

* **Look-ahead bias audit + timing convention:**
  `[advances_fin_ml, p.31-34]`. We use `prev_weight × ret` alignment
  throughout, same as `letf_rotation.py` / `phase3_6_c_gtaa_faber_10mo.py`.

Algorithm summary
-----------------

1. **Feature extraction (daily):** from SPY & TLT log-returns compute:
   * 20-day realized volatility of SPY (annualized)
   * 20-day realized volatility of TLT (annualized)
   * 20-day realized correlation between SPY and TLT returns
   * 20-day realized skewness of SPY returns
   * Feature set variant switches which of these are used for HMM input.
2. **HMM training (IS only):** fit N-state Gaussian HMM via Baum-Welch
   EM on the 20d feature vector stream over the IS window
   (2001-05-14 → 2017-12-31, trimmed to TLT 2002-07 / GLD 2004-11
   inception). Save transition matrix A and emission params (mean μ_i,
   covariance Σ_i per state). No peeking at OOS/FWD.
3. **State labelling (IS only):** rank states by average SPY realized
   vol under each state. With N=2 → {low_vol, high_vol}; with N=3 →
   {low_vol, medium_vol, crisis}; with N=4 → {low_vol, medium_vol,
   high_vol, crisis}.
4. **Regime decoding (all splits):** Viterbi decode the most-likely
   state sequence given the fitted A, μ, Σ. Produces a per-day state
   label ∈ {0..N-1}.
5. **Regime → allocation mapping (fixed post-IS):**
   * **low_vol** → 100% SPY
   * **medium_vol** → 50% SPY + 50% TLT (balanced)
   * **high_vol** → 100% TLT (bonds defensive, still with carry)
   * **crisis** → 100% GLD (gold as AMH-rule-1A defensive asset)
   Collapse table for lower state counts:
   * N=2 → {low_vol → 100% SPY, high_vol → 100% GLD}
   * N=3 → {low_vol → 100% SPY, medium → 50/50 SPY/TLT, high → 100% GLD}
   * N=4 → as above
6. **Rebalance cadence:** every N trading days (10 or 21). Between
   rebalances, hold whatever allocation was decided at the last
   rebalance (no mid-cadence regime flips — minimises whipsaw).
7. **P&L:** `prev_weight × ret` alignment. Frictions per Inter broker
   model (plan §3.2): 0 commission, 2bps spread, 1bps slippage on
   traded notional per rebalance switch, 15% BR CG tax on positive
   monthly net return.

Grid for CPCV/PBO (12 configs)
------------------------------

* N states ∈ {2, 3, 4}              — capacity for classifier detail
* Feature set ∈ {σ_only, σ+ρ, σ+ρ+skew}  — richness of input
* Rebalance cadence ∈ {10d, 21d}    — swing-horizon per plan §0

Actually 3 × 3 × 2 = **18 configs**. We retain all 18 for PBO/DSR.

Hard constraints honoured
-------------------------

* HMM trained on **IS only**. State parameters never re-fitted on
  OOS/FWD; Viterbi decoding uses fixed post-IS parameters.
* State-label assignment uses IS-only statistics (mean SPY realized vol
  per state during the IS window) — OOS state distribution not
  inspected.
* No price-cross regime signal anywhere (the differentiator vs
  V2-L2 Gayed).
* 1× leverage; no synthesized LETFs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

__all__ = [
    "HMMParams",
    "AMHRegimeConfig",
    "AMHRegimeResult",
    "compute_features",
    "fit_gaussian_hmm",
    "viterbi_decode",
    "label_states_by_spy_vol",
    "simulate_amh_regime",
]


FeatureSet = Literal["sigma", "sigma_rho", "sigma_rho_skew"]


# ---------------------------------------------------------------------------
# HMM implementation (pure numpy, Baum-Welch EM + Viterbi)
# ---------------------------------------------------------------------------


@dataclass
class HMMParams:
    """Fitted parameters of a Gaussian HMM with diagonal-covariance emissions.

    Notes
    -----
    We use diagonal covariances per state (no cross-feature covariance)
    for numerical stability on small samples and to mirror Chen & Tsang
    2021's single-variable Gaussian emissions generalized to the
    multivariate case. `[regime_change, p.14-17, ch.2]`.
    """

    n_states: int
    n_features: int
    init_probs: np.ndarray  # shape (n_states,)
    trans: np.ndarray       # shape (n_states, n_states)
    means: np.ndarray       # shape (n_states, n_features)
    variances: np.ndarray   # shape (n_states, n_features), strictly positive

    def logemit(self, x: np.ndarray) -> np.ndarray:
        """Log emission probability of ``x`` (n_features,) under each state.

        Diagonal-covariance Gaussian:
            log p(x|s) = -0.5 * sum_j [ log(2π σ²_{s,j}) + (x_j-μ_{s,j})² / σ²_{s,j} ]
        """
        diff = x[None, :] - self.means                # (n_states, n_features)
        inv = 1.0 / self.variances
        log_norm = -0.5 * np.log(2.0 * np.pi * self.variances).sum(axis=1)
        quad = -0.5 * (diff * diff * inv).sum(axis=1)
        return log_norm + quad


def _logsumexp_axis(a: np.ndarray, axis: int) -> np.ndarray:
    m = np.max(a, axis=axis, keepdims=True)
    return (m + np.log(np.exp(a - m).sum(axis=axis, keepdims=True))).squeeze(axis=axis)


def fit_gaussian_hmm(
    features: np.ndarray,
    n_states: int,
    n_iter: int = 100,
    tol: float = 1e-4,
    seed: int = 42,
    min_var: float = 1e-6,
) -> HMMParams:
    """Fit a Gaussian HMM by Baum-Welch EM.

    Parameters
    ----------
    features
        Array shape (T, F) of real-valued feature rows.
    n_states
        Number of hidden states (2, 3, or 4).
    n_iter
        Max EM iterations.
    tol
        Convergence tolerance on log-likelihood improvement.
    seed
        RNG seed for initial k-means-style seeding.
    min_var
        Variance floor to avoid singular emissions
        `[fin_time_series_tsay, ch.4 §4.1.4 caveats on MSA numerics]`.

    Returns
    -------
    HMMParams

    Citations
    ---------
    * Baum-Welch EM for MSA / HMM: Hamilton (1989) and
      `[fin_time_series_tsay, p.186-187, §4.1.4]`.
    * Diagonal Gaussian emissions: `[regime_change, p.14-17, ch.2]`
      (extended to multivariate).
    """
    if features.ndim != 2:
        raise ValueError(f"features must be 2D, got shape {features.shape}")
    T, F = features.shape
    if T < 2 * n_states:
        raise ValueError(
            f"need at least 2*n_states rows, got {T} for n_states={n_states}"
        )
    rng = np.random.default_rng(seed)

    # --- init via simple k-means-style quantile seeding on feature 0 -----
    # Sort by first feature (vol by convention) and split into n_states
    # equal-count buckets to initialize means + vars.
    order = np.argsort(features[:, 0])
    buckets = np.array_split(order, n_states)
    means = np.vstack([features[b].mean(axis=0) for b in buckets])
    variances = np.vstack(
        [np.clip(features[b].var(axis=0, ddof=0), min_var, None) for b in buckets]
    )
    trans = np.full((n_states, n_states), 0.1 / max(n_states - 1, 1))
    np.fill_diagonal(trans, 0.9)  # sticky states
    init = np.full(n_states, 1.0 / n_states)

    params = HMMParams(
        n_states=n_states, n_features=F,
        init_probs=init, trans=trans,
        means=means, variances=variances,
    )

    prev_ll = -np.inf
    for it in range(n_iter):
        # --- forward (alpha) in log space ---
        logA = np.log(params.trans + 1e-300)
        logpi = np.log(params.init_probs + 1e-300)
        logB = np.zeros((T, n_states))
        for t in range(T):
            logB[t] = params.logemit(features[t])

        logalpha = np.full((T, n_states), -np.inf)
        logalpha[0] = logpi + logB[0]
        for t in range(1, T):
            # logalpha[t, j] = logsumexp_i(logalpha[t-1, i] + logA[i, j]) + logB[t, j]
            mat = logalpha[t - 1][:, None] + logA   # (n_states, n_states)
            logalpha[t] = _logsumexp_axis(mat, axis=0) + logB[t]
        ll = _logsumexp_axis(logalpha[-1], axis=0)
        ll = float(ll) if np.ndim(ll) == 0 else float(ll.flatten()[0])

        # --- backward (beta) in log space ---
        logbeta = np.full((T, n_states), -np.inf)
        logbeta[-1] = 0.0
        for t in range(T - 2, -1, -1):
            mat = logA + logB[t + 1][None, :] + logbeta[t + 1][None, :]
            logbeta[t] = _logsumexp_axis(mat, axis=1)

        # --- gamma = alpha*beta ---
        loggamma = logalpha + logbeta
        loggamma -= _logsumexp_axis(loggamma, axis=1)[:, None]
        gamma = np.exp(loggamma)

        # --- xi[t, i, j] = alpha[t,i] * A[i,j] * B[t+1,j] * beta[t+1,j] ---
        # We only need sum over t of xi for the transition update.
        xi_sum = np.zeros((n_states, n_states))
        for t in range(T - 1):
            logxi_t = (
                logalpha[t][:, None]
                + logA
                + logB[t + 1][None, :]
                + logbeta[t + 1][None, :]
            )
            logxi_t -= _logsumexp_axis(logxi_t.reshape(-1), axis=0)
            xi_sum += np.exp(logxi_t)

        # --- M-step ---
        # initial probs
        init_new = gamma[0] / gamma[0].sum()
        # transitions
        denom = gamma[:-1].sum(axis=0) + 1e-300
        trans_new = xi_sum / denom[:, None]
        # renormalize rows to deal with floating errors
        trans_new = trans_new / trans_new.sum(axis=1, keepdims=True)
        # emissions (diagonal Gaussian)
        weight = gamma.sum(axis=0) + 1e-300       # (n_states,)
        means_new = (gamma[:, :, None] * features[:, None, :]).sum(axis=0) / weight[:, None]
        diff = features[:, None, :] - means_new[None, :, :]
        var_new = (gamma[:, :, None] * diff * diff).sum(axis=0) / weight[:, None]
        var_new = np.clip(var_new, min_var, None)

        params = HMMParams(
            n_states=n_states, n_features=F,
            init_probs=init_new, trans=trans_new,
            means=means_new, variances=var_new,
        )

        if abs(ll - prev_ll) < tol:
            break
        prev_ll = ll

    return params


def viterbi_decode(features: np.ndarray, params: HMMParams) -> np.ndarray:
    """Most-likely state sequence given fitted HMM.

    Returns array shape (T,) with state indices in {0, .., n_states-1}.
    """
    T = features.shape[0]
    n = params.n_states
    logA = np.log(params.trans + 1e-300)
    logpi = np.log(params.init_probs + 1e-300)
    logB = np.zeros((T, n))
    for t in range(T):
        logB[t] = params.logemit(features[t])

    delta = np.full((T, n), -np.inf)
    psi = np.zeros((T, n), dtype=np.int64)
    delta[0] = logpi + logB[0]
    for t in range(1, T):
        mat = delta[t - 1][:, None] + logA  # (n, n)
        psi[t] = np.argmax(mat, axis=0)
        delta[t] = np.max(mat, axis=0) + logB[t]

    path = np.zeros(T, dtype=np.int64)
    path[-1] = int(np.argmax(delta[-1]))
    for t in range(T - 2, -1, -1):
        path[t] = psi[t + 1, path[t + 1]]
    return path


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------


def compute_features(
    spy_ret: pd.Series,
    tlt_ret: pd.Series,
    feature_set: FeatureSet,
    lookback: int = 20,
) -> pd.DataFrame:
    """Build the feature panel for HMM input.

    Features
    --------
    * ``spy_vol``: 20-day realized stdev of SPY returns (annualized by
      ``sqrt(252)``).
    * ``tlt_vol``: 20-day realized stdev of TLT returns.
    * ``sr_corr``: 20-day Pearson correlation between SPY and TLT.
    * ``spy_skew``: 20-day skewness of SPY returns (sample skew).

    Parameters
    ----------
    feature_set
        * ``sigma``         → [spy_vol, tlt_vol]
        * ``sigma_rho``     → [spy_vol, tlt_vol, sr_corr]
        * ``sigma_rho_skew``→ [spy_vol, tlt_vol, sr_corr, spy_skew]

    Citations
    ---------
    * Realized volatility as regime-discriminator:
      `[fin_time_series_tsay, §3.15.1, eq.RV]` + `[regime_change,
      p.27, ch.3 eq.3.2]`.
    * Cross-asset correlation non-stationarity in distress regimes:
      `[adaptive_markets, p.282-283, RULE 4A]`.
    * Sample skewness as higher-moment regime feature:
      `[fin_time_series_tsay, p.109-110, ch.3.1]`.
    """
    aligned = pd.concat(
        {"spy": spy_ret.astype(float), "tlt": tlt_ret.astype(float)},
        axis=1,
    ).dropna()
    r_spy = aligned["spy"]
    r_tlt = aligned["tlt"]
    sqrt252 = np.sqrt(252.0)
    spy_vol = r_spy.rolling(lookback, min_periods=lookback).std(ddof=1) * sqrt252
    tlt_vol = r_tlt.rolling(lookback, min_periods=lookback).std(ddof=1) * sqrt252
    sr_corr = r_spy.rolling(lookback, min_periods=lookback).corr(r_tlt)
    spy_skew = r_spy.rolling(lookback, min_periods=lookback).skew()

    if feature_set == "sigma":
        df = pd.concat({"spy_vol": spy_vol, "tlt_vol": tlt_vol}, axis=1)
    elif feature_set == "sigma_rho":
        df = pd.concat(
            {"spy_vol": spy_vol, "tlt_vol": tlt_vol, "sr_corr": sr_corr},
            axis=1,
        )
    elif feature_set == "sigma_rho_skew":
        df = pd.concat(
            {
                "spy_vol": spy_vol, "tlt_vol": tlt_vol,
                "sr_corr": sr_corr, "spy_skew": spy_skew,
            },
            axis=1,
        )
    else:
        raise ValueError(f"unknown feature_set {feature_set!r}")

    return df.dropna()


def label_states_by_spy_vol(
    states_is: np.ndarray, features_is: np.ndarray, n_states: int
) -> dict[int, str]:
    """Map fitted state ids to regime semantic labels using IS averages.

    Ranks states by their mean value of feature 0 (SPY realized vol).
    Lowest → 'low_vol'. Highest → 'crisis' (for n≥3) or 'high_vol' (n=2).

    IMPORTANT: the state ids from HMM fitting are arbitrary; this
    function assigns them semantic labels using **IS statistics only**
    so the mapping is invariant across splits.
    """
    per_state_mean: dict[int, float] = {}
    for s in range(n_states):
        mask = states_is == s
        if mask.sum() == 0:
            per_state_mean[s] = np.inf  # unused; sort to end
        else:
            per_state_mean[s] = float(features_is[mask, 0].mean())
    ordered = sorted(per_state_mean.items(), key=lambda kv: kv[1])

    mapping: dict[int, str] = {}
    if n_states == 2:
        mapping[ordered[0][0]] = "low_vol"
        mapping[ordered[1][0]] = "crisis"
    elif n_states == 3:
        mapping[ordered[0][0]] = "low_vol"
        mapping[ordered[1][0]] = "medium_vol"
        mapping[ordered[2][0]] = "crisis"
    elif n_states == 4:
        mapping[ordered[0][0]] = "low_vol"
        mapping[ordered[1][0]] = "medium_vol"
        mapping[ordered[2][0]] = "high_vol"
        mapping[ordered[3][0]] = "crisis"
    else:
        raise ValueError(f"unsupported n_states={n_states}")
    return mapping


# Canonical regime → allocation map. Keys are semantic labels.
REGIME_ALLOCATION: dict[str, dict[str, float]] = {
    "low_vol":    {"SPY": 1.0, "TLT": 0.0, "GLD": 0.0},
    "medium_vol": {"SPY": 0.5, "TLT": 0.5, "GLD": 0.0},
    "high_vol":   {"SPY": 0.0, "TLT": 1.0, "GLD": 0.0},
    "crisis":     {"SPY": 0.0, "TLT": 0.0, "GLD": 1.0},
}


# ---------------------------------------------------------------------------
# Strategy dataclasses + simulator
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AMHRegimeConfig:
    """Immutable configuration for one grid cell.

    Parameters
    ----------
    n_states
        HMM state count ∈ {2, 3, 4}.
    feature_set
        One of ``"sigma"``, ``"sigma_rho"``, ``"sigma_rho_skew"``.
    rebalance_cadence_days
        Trading-day cadence for rebalance decisions. 10 and 21 are the
        swing-horizon tests per plan §0.
    feature_lookback
        Realized-moment rolling window (trading days). 20 per
        `[regime_change, p.27, ch.3]`.
    commission_bps
        Inter = 0 (plan §3.2).
    spread_bps
        2 bps retail default.
    slippage_bps
        1 bps retail default.
    tax_rate
        0.15 BR (mandate §1).
    hmm_seed
        RNG seed for HMM fit reproducibility.
    """

    n_states: int = 3
    feature_set: FeatureSet = "sigma_rho"
    rebalance_cadence_days: int = 21
    feature_lookback: int = 20
    commission_bps: float = 0.0
    spread_bps: float = 2.0
    slippage_bps: float = 1.0
    tax_rate: float = 0.15
    hmm_seed: int = 42

    def __post_init__(self) -> None:
        if self.n_states not in (2, 3, 4):
            raise ValueError(f"n_states must be 2/3/4, got {self.n_states}")
        if self.feature_set not in ("sigma", "sigma_rho", "sigma_rho_skew"):
            raise ValueError(f"unknown feature_set {self.feature_set!r}")
        if self.rebalance_cadence_days <= 0:
            raise ValueError(
                f"rebalance_cadence_days must be > 0, got {self.rebalance_cadence_days}"
            )
        if self.feature_lookback <= 1:
            raise ValueError(
                f"feature_lookback must be > 1, got {self.feature_lookback}"
            )

    @property
    def switch_cost_pct(self) -> float:
        return (self.commission_bps + self.spread_bps + self.slippage_bps) / 10_000.0


@dataclass
class AMHRegimeResult:
    """Output of an AMH regime-switching simulation."""

    equity: pd.Series
    daily_returns: pd.Series
    regime_labels: pd.Series
    state_ids: pd.Series
    weights: pd.DataFrame
    rebal_dates: pd.DatetimeIndex
    state_label_map: dict[int, str]
    hmm_params: HMMParams
    is_state_stats: pd.DataFrame
    cum_cost_pct: float = 0.0
    cum_tax_pct: float = 0.0

    def sharpe(self, periods_per_year: int = 252) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        std = float(r.std(ddof=1))
        if std == 0.0:
            return 0.0
        return float(r.mean() / std * np.sqrt(periods_per_year))

    def cagr(self, periods_per_year: int = 252) -> float:
        eq = self.equity.dropna()
        if len(eq) < 2:
            return 0.0
        years = (len(eq) - 1) / periods_per_year
        if years <= 0:
            return 0.0
        total = float(eq.iloc[-1] / eq.iloc[0])
        if total <= 0:
            return -1.0
        return total ** (1.0 / years) - 1.0

    def max_drawdown(self) -> float:
        eq = self.equity.dropna()
        if eq.empty:
            return 0.0
        peak = eq.cummax()
        dd = eq / peak - 1.0
        return float(dd.min())


def simulate_amh_regime(
    spy_ret: pd.Series,
    tlt_ret: pd.Series,
    gld_ret: pd.Series,
    config: AMHRegimeConfig,
    is_start: pd.Timestamp,
    is_end: pd.Timestamp,
) -> AMHRegimeResult:
    """Run the full AMH regime pipeline end-to-end.

    Parameters
    ----------
    spy_ret, tlt_ret, gld_ret
        Daily total-returns, aligned on common index. Must include the
        IS window in full.
    config
        Grid cell settings.
    is_start, is_end
        IS window bounds. HMM fitting and state labelling use ONLY the
        slice ``[is_start, is_end]`` of the feature panel — OOS/FWD
        never touches fit parameters, per plan hard constraint.

    Returns
    -------
    AMHRegimeResult
        With weights/returns spanning the intersection of the three
        assets' index (minus feature-warmup NaNs).
    """
    # --- 1. Align ---
    df = pd.concat(
        {"SPY": spy_ret.astype(float), "TLT": tlt_ret.astype(float),
         "GLD": gld_ret.astype(float)},
        axis=1,
    ).dropna()
    if df.empty:
        raise ValueError("SPY/TLT/GLD return panel is empty after align")

    # --- 2. Features (use SPY + TLT only, GLD is allocation-only) ---
    features_df = compute_features(
        df["SPY"], df["TLT"], config.feature_set, lookback=config.feature_lookback
    )
    # Reindex features to the aligned panel's index, drop warmup NaNs.
    features_df = features_df.reindex(df.index).dropna()

    # --- 3. Fit HMM on IS slice only ---
    is_mask = (features_df.index >= is_start) & (features_df.index <= is_end)
    feats_is = features_df.loc[is_mask].to_numpy()
    if feats_is.shape[0] < max(60, 3 * config.n_states):
        raise ValueError(
            f"IS feature count {feats_is.shape[0]} too low for n_states={config.n_states}"
        )
    params = fit_gaussian_hmm(
        feats_is, n_states=config.n_states, seed=config.hmm_seed,
    )

    # --- 4. Viterbi decode on IS to label states ---
    states_is = viterbi_decode(feats_is, params)
    label_map = label_states_by_spy_vol(states_is, feats_is, config.n_states)

    # --- 5. Viterbi decode full series (IS+OOS+FWD) ---
    feats_all = features_df.to_numpy()
    states_all = viterbi_decode(feats_all, params)
    state_series = pd.Series(
        states_all, index=features_df.index, name="state_id"
    )
    regime_label_series = state_series.map(label_map)

    # --- 6. IS state stats (for reproducibility CSV) ---
    is_stats_rows = []
    for s in range(config.n_states):
        m = states_is == s
        if m.sum() == 0:
            continue
        feat_mean = feats_is[m].mean(axis=0)
        # mean SPY return per state on IS (for diagnostics)
        is_state_idx = features_df.loc[is_mask].index[m]
        spy_ret_in = df["SPY"].loc[is_state_idx].dropna()
        row = {
            "state_id": s,
            "label": label_map[s],
            "prob_in_state": float(m.sum() / len(states_is)),
            "feat0_mean_spy_vol_ann": float(feat_mean[0]),
            "feat1_mean_tlt_vol_ann": float(feat_mean[1]) if feats_is.shape[1] >= 2 else np.nan,
            "mean_spy_daily_ret": float(spy_ret_in.mean()) if len(spy_ret_in) else 0.0,
            "std_spy_daily_ret": float(spy_ret_in.std(ddof=1)) if len(spy_ret_in) > 1 else 0.0,
        }
        is_stats_rows.append(row)
    is_state_stats = pd.DataFrame(is_stats_rows)

    # --- 7. Build daily weights via cadence rebalance ---
    # At each rebalance date t, read state_series.loc[t] and set target
    # weights = REGIME_ALLOCATION[label_map[state]]. Those weights apply
    # from next trading day (one-day lag) until next rebalance.
    full_idx = df.index
    # Restrict weights to dates where features_df has non-nan value
    # (otherwise regime is undefined) → start from first feature date.
    start_idx = features_df.index[0]
    weights = pd.DataFrame(0.0, index=full_idx, columns=["SPY", "TLT", "GLD"])

    # Rebalance every N trading days starting at first valid feature date.
    first_pos = full_idx.get_loc(start_idx)
    rebal_positions = list(range(first_pos, len(full_idx), config.rebalance_cadence_days))
    rebal_dates = [full_idx[p] for p in rebal_positions]

    for rd in rebal_dates:
        # Read regime at rebalance date (using decoded state on that bar).
        if rd not in regime_label_series.index:
            continue
        label = regime_label_series.loc[rd]
        if not isinstance(label, str):
            continue
        alloc = REGIME_ALLOCATION.get(label)
        if alloc is None:
            continue
        # Apply from rd onward until next rebal event (will be overwritten).
        for asset, w in alloc.items():
            weights.loc[rd:, asset] = w

    # --- 8. P&L with prev_weight × ret + per-switch cost ---
    prev_w = weights.shift(1).fillna(0.0)
    ret_panel = df.fillna(0.0)
    # Align weights panel to df index (full_idx == df.index). Same frame.
    daily_ret_gross = (prev_w[["SPY", "TLT", "GLD"]] * ret_panel[["SPY", "TLT", "GLD"]]).sum(axis=1)

    # Cost: turnover in weights, 0.5 × sum(|Δw|) per rebalance day
    turnover = weights.diff().abs().sum(axis=1)
    traded_notional = turnover / 2.0
    cost_series = traded_notional * config.switch_cost_pct
    daily_net_before_tax = daily_ret_gross - cost_series

    # --- 9. Monthly BR tax on positive cumulative monthly returns ---
    equity = 1.0
    equity_curve: list[float] = []
    cum_cost = 0.0
    cum_tax = 0.0
    month_start_equity = equity
    prev_month = None
    for ts, r_net in daily_net_before_tax.items():
        r_net = 0.0 if np.isnan(r_net) else float(r_net)
        month = (ts.year, ts.month)
        # Apply day's return first.
        eq_after_ret = equity * (1.0 + r_net)
        cum_cost += float(cost_series.loc[ts]) * equity
        equity = eq_after_ret
        # On last trading day of the month (detected by month change on
        # the NEXT bar — i.e. apply at end of current month detection):
        # we'll detect via checking if the next index value (if any) has
        # a different month. Here we use a simpler rule — apply tax at
        # month-switch boundary on *this* bar when the NEXT bar is in a
        # new month. We'll handle at end of loop with a one-step
        # lookahead on the index itself (no data lookahead — just knowing
        # the calendar).
        equity_curve.append(equity)
        prev_month = month

    # Apply tax retrospectively at each month-end boundary.
    dates = list(daily_net_before_tax.index)
    month_ids: list[tuple[int, int]] = [(d.year, d.month) for d in dates]
    # Track indices where the month changes vs next bar (i.e. last bar
    # of each month).
    month_end_mask = np.zeros(len(dates), dtype=bool)
    for i in range(len(dates) - 1):
        if month_ids[i] != month_ids[i + 1]:
            month_end_mask[i] = True
    month_end_mask[-1] = True  # last bar counts as month-end

    equity = 1.0
    adjusted_equity = []
    month_start = 1.0
    for i, r_net in enumerate(daily_net_before_tax.values):
        r = 0.0 if np.isnan(r_net) else float(r_net)
        equity *= 1.0 + r
        if month_end_mask[i] and config.tax_rate > 0:
            gain = max(0.0, equity - month_start)
            tax = gain * config.tax_rate
            equity -= tax
            cum_tax += tax
            month_start = equity
        adjusted_equity.append(equity)

    equity_series = pd.Series(
        adjusted_equity, index=daily_net_before_tax.index, name="equity"
    )
    daily_net = equity_series.pct_change().fillna(0.0)

    return AMHRegimeResult(
        equity=equity_series,
        daily_returns=daily_net,
        regime_labels=regime_label_series.reindex(full_idx),
        state_ids=state_series.reindex(full_idx),
        weights=weights,
        rebal_dates=pd.DatetimeIndex(rebal_dates),
        state_label_map=label_map,
        hmm_params=params,
        is_state_stats=is_state_stats,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
    )
