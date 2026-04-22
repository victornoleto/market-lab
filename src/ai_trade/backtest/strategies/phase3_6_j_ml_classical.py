"""Phase 3.6 Family J — ML classical swing predictor (Track J1 Jansen-style).

Track choice: **J1 — Jansen-style feature engineering + gradient-boosted
classifier on a multi-asset ETF panel**. Single-model multi-ticker, 5-day
forward-sign binary classification, predicted probability gates a 50%-of-equity
long entry.

This is deliberately **not** a re-run of the rejected V2-L3 AFML triple-barrier
meta-labeling lead (`reports/phase_3_5f/honest_revalidation/v2_l3_afml/AGGREGATE.md`).
V2-L3 was: single-ticker EMA-50-cross primary + RandomForest precision
filter on triple-barrier meta-labels [advances_fin_ml, p.50-60].

Family J changes **every** layer:

* **Universe:** 7 liquid ETFs covering equities (SPY, QQQ, XLF, XLE),
  bonds (TLT), emerging markets (EEM), and commodities (GLD). Single
  panel-trained model. V2-L3 was single-ticker per model
  [ml_for_algo_trading, ch.4 p.82-93].
* **Label paradigm:** **Forward 5d sign classification** (2-class). Not
  a meta-label over a pre-existing primary signal. The classifier IS
  the edge generator. Cite [ml_for_asset_managers, p.21,§1.9 FAQ]:
  "failing to predict the sign is an actual loss" → prefer classifiers
  on sign over regression on size.
* **Model:** sklearn ``GradientBoostingClassifier`` (LightGBM/XGBoost
  absent from venv — fallback per Jansen ch.12 p.390-400 LightGBM
  recipe, translated to sklearn equivalent with depth=5 default).
* **Validation during IS:** Purged 5-fold with 5d embargo on IS only
  (2001-05-14 → 2017-12-31), for threshold selection. Then train
  ONCE on full IS, predict OOS (2018-2023) and FWD (2024-2026) with
  NO refitting [ml_for_asset_managers, p.8, §1.4.2]; no walk-forward
  retrain leakage [advances_fin_ml, p.31-34].
* **Sizing:** 50% of equity per qualifying ticker, capped at 100%
  across the basket — conservative for a noise-prone ML signal
  [ml_for_algo_trading, ch.5 p.124-135].
* **Friction model:** Banco Inter (plan §3.2) — 0 commission on US
  ETFs + 5 bps one-way spread + BR 15% CG tax on realized monthly
  gains.

Every hyperparameter choice, lookback, and gate threshold cites a book.
Architecture follows Jansen ML4T workflow [preface p.xiii; ch.1 p.13]:
source → features → model → portfolio → backtest. No look-ahead: all
features at bar ``t`` use close information from ``t`` and backward
rolling windows; the label at ``t`` uses close-to-close return over
``(t, t+H]`` and is ONLY used during IS training
[ml_for_algo_trading, ch.8 p.223-224].

Classes
-------
``MLClassicalConfig``
    Immutable hyperparameter bundle.
``MLClassicalResult``
    Contains daily_returns, weights_path, feature_importance_, threshold
    used, prediction path.

Functions
---------
``build_features``
    Per-ticker DataFrame → feature DataFrame with NaN-safe rolling windows.
``build_panel_dataset``
    Stack features across tickers → training panel (X, y, idx, ticker).
``simulate_ml_classical``
    End-to-end train-IS / predict-OOS+FWD / simulate daily return series
    with prev_weight × next_return honest alignment.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score

log = logging.getLogger(__name__)

__all__ = [
    "MLClassicalConfig",
    "MLClassicalResult",
    "build_features",
    "build_panel_dataset",
    "purged_kfold_splits",
    "simulate_ml_classical",
]


TRADING_DAYS = 252


@dataclass(frozen=True)
class MLClassicalConfig:
    """Immutable config for one Family-J ML-classical run.

    Parameters
    ----------
    label_horizon : int
        Forward return window in trading days for the binary label.
        Default 5 matches the swing-horizon brief (5-15d hold).
        Grid variants {5, 10} [ml_for_asset_managers, p.10 §1.5]
        — label horizon is a modeling choice, not a free parameter.
    threshold : float
        Probability threshold P(up) above which a long position is
        taken. Defaults to 0.55; grid {0.55, 0.60}. Swept via purged
        k-fold on IS [advances_fin_ml, p.208-211 CSCV].
    n_estimators : int
        Boosting rounds for the ``GradientBoostingClassifier``.
        Default 300; grid {100, 300} [ml_for_algo_trading, p.388,
        p.397-399]: low-LR + many estimators + early stopping beats
        high-LR + few.
    max_depth : int
        Maximum tree depth. Default 3; grid {3, 5} [ml_for_algo_trading,
        p.397-398]: ``num_leaves``/``max_depth`` is "the most sensitive
        hyperparameter" for tree ensembles on low-SNR finance data.
    learning_rate : float
        Gradient-boosting learning rate. Default 0.05. Not gridded —
        held constant to keep the parameter sweep honest. Cite
        [ml_for_algo_trading, p.388]: low LR with many trees is
        canonical practice.
    position_size : float
        Fraction of equity allocated per triggered signal. Default 0.5
        — conservative for a noise-prone ML signal
        [ml_for_algo_trading, ch.5 p.124-135 on IR = IC × √breadth;
        ml_for_asset_managers, p.19 on ML oracle risk].
    rebalance_days : int
        Portfolio rebalance cadence in trading days. Default 5 matches
        the label horizon — we do NOT re-signal more frequently than
        the prediction window (that would leak).
    spread_one_way_pct : float
        One-way spread cost as fraction. Default 0.0005 (5 bps). Plan
        §3.2: Banco Inter US ETFs + synthetic 0.05% slippage.
    commission_per_trade : float
        Zero — Banco Inter does not charge commission on US ETFs per
        plan §3.2.
    tax_rate : float
        Monthly realized-gains tax. Default 0.15 = BR 15% on capital
        gains, applied on the first trading day of each month to the
        prior month's realized positive net. Mandate §1.
    purged_embargo_days : int
        Days to embargo around each validation fold in purged K-fold.
        Default 5 matches the label horizon per
        [ml_for_asset_managers, p.8; advances_fin_ml, p.108-110 on
        purging and embargo widths].
    n_kfold_splits : int
        Purged K-fold splits used for threshold selection on IS only.
        Default 5 [advances_fin_ml, p.103-110 on purged CV].
    random_state : int
        Reproducibility seed for sklearn. Default 42.

    Citations
    ---------
    * Overall ML4T workflow: [ml_for_algo_trading, preface p.xiii, ch.1 p.13].
    * Prefer classifiers over regression for sign prediction:
      [ml_for_asset_managers, p.21, §1.9].
    * Purged k-fold + embargo: [ml_for_asset_managers, p.8, §1.4.2];
      [advances_fin_ml, p.103-110].
    """

    label_horizon: int = 5
    threshold: float = 0.55
    n_estimators: int = 300
    max_depth: int = 3
    learning_rate: float = 0.05
    position_size: float = 0.5
    rebalance_days: int = 5
    spread_one_way_pct: float = 0.0005
    commission_per_trade: float = 0.0
    tax_rate: float = 0.15
    purged_embargo_days: int = 5
    n_kfold_splits: int = 5
    random_state: int = 42

    def __post_init__(self) -> None:
        if self.label_horizon <= 0:
            raise ValueError(f"label_horizon must be > 0, got {self.label_horizon}")
        if not 0.5 <= self.threshold <= 0.95:
            raise ValueError(
                f"threshold must be in [0.5, 0.95], got {self.threshold}"
            )
        if self.n_estimators <= 0:
            raise ValueError("n_estimators must be > 0")
        if self.max_depth <= 0:
            raise ValueError("max_depth must be > 0")
        if not 0 < self.position_size <= 1.0:
            raise ValueError(
                f"position_size must be in (0, 1], got {self.position_size}"
            )
        if self.rebalance_days <= 0:
            raise ValueError("rebalance_days must be > 0")


@dataclass
class MLClassicalResult:
    """Output of one Family-J simulation."""

    daily_returns: pd.Series
    equity: pd.Series
    weights: pd.DataFrame  # index=dates, columns=tickers, values=weight
    predictions: pd.DataFrame  # index=dates, columns=tickers, values=P(up)
    feature_importance: pd.Series
    threshold: float
    is_purged_kfold_accuracy: float
    is_purged_kfold_std: float
    cum_cost_pct: float = 0.0
    cum_tax_pct: float = 0.0

    def sharpe(self, periods_per_year: int = TRADING_DAYS) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        if sd == 0:
            return 0.0
        return float(r.mean() / sd * np.sqrt(periods_per_year))

    def cagr(self, periods_per_year: int = TRADING_DAYS) -> float:
        eq = self.equity.dropna()
        if len(eq) < 2:
            return 0.0
        years = (len(eq) - 1) / periods_per_year
        if years <= 0:
            return 0.0
        total = float(eq.iloc[-1] / eq.iloc[0])
        if total <= 0:
            return -1.0
        return total ** (1 / years) - 1

    def max_drawdown(self) -> float:
        eq = self.equity.dropna()
        if eq.empty:
            return 0.0
        peak = eq.cummax()
        return float((eq / peak - 1).min())


def _rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """RSI-14 per [ml_for_algo_trading, p.86].

    Uses Wilder-like simple rolling mean of gains/losses. No look-ahead:
    value at bar ``t`` uses closes up to and including ``t``.
    """
    delta = prices.diff()
    up = delta.clip(lower=0.0)
    dn = (-delta).clip(lower=0.0)
    avg_up = up.rolling(window, min_periods=window).mean()
    avg_dn = dn.rolling(window, min_periods=window).mean()
    rs = avg_up / avg_dn.replace(0.0, np.nan)
    rsi = 100.0 - 100.0 / (1.0 + rs)
    return rsi.fillna(50.0)


def build_features(
    df: pd.DataFrame,
    spy_close: pd.Series,
    spy_sma200: pd.Series,
) -> pd.DataFrame:
    """Per-ticker feature DataFrame.

    All features are computed from close (``adj_close``) and aligned to the
    same DatetimeIndex as the input. No look-ahead: every rolling window
    uses observations on or before bar ``t``; all features at bar ``t`` are
    known by the close of ``t``. Signal generation is shifted one day
    downstream by the caller, so these features feed the bar-``t+1`` entry
    decision. Citation: [advances_fin_ml, p.31-34 on timing convention].

    Features engineered per [ml_for_algo_trading, ch.4 p.82-93]:

    * ``ret_1``, ``ret_5``, ``ret_20`` — simple return lags
      [ml_for_algo_trading, p.86, Jegadeesh 12-1 adapted to swing].
    * ``vol_20``, ``vol_60`` — rolling std of daily returns
      [ml_for_algo_trading, p.99 — Bollinger/vol as factor].
    * ``corr_spy_60`` — 60d rolling correlation vs SPY daily returns
      [ml_for_algo_trading, ch.7 p.188-191 — market-beta factor].
    * ``mom_zscore_60`` — 60d-lookback momentum z-score vs rolling mean/std
      [ml_for_algo_trading, p.86; stocks_on_the_move, p.81].
    * ``rsi_14`` — canonical RSI [ml_for_algo_trading, p.86].
    * ``dow`` — day-of-week integer (0=Mon) [ml_for_algo_trading, p.86-87].
    * ``regime_spy200`` — binary 1 if SPY close > SPY SMA200, else 0
      [stocks_on_the_move, p.66-67; shared regime feature across panel].
    """
    close = df["adj_close"].astype(float)
    ret = close.pct_change()

    feats = pd.DataFrame(index=close.index)
    feats["ret_1"] = ret
    feats["ret_5"] = close.pct_change(5)
    feats["ret_20"] = close.pct_change(20)
    feats["vol_20"] = ret.rolling(20, min_periods=20).std(ddof=0)
    feats["vol_60"] = ret.rolling(60, min_periods=60).std(ddof=0)

    spy_ret = spy_close.pct_change()
    common = ret.index.intersection(spy_ret.index)
    corr_series = (
        ret.loc[common].rolling(60, min_periods=60).corr(spy_ret.loc[common])
    )
    feats["corr_spy_60"] = corr_series.reindex(close.index)

    # Momentum z-score: (ret_60 - rolling_mean_60) / rolling_std_60
    ret_60 = close.pct_change(60)
    mu_60 = ret_60.rolling(60, min_periods=60).mean()
    sd_60 = ret_60.rolling(60, min_periods=60).std(ddof=0)
    feats["mom_zscore_60"] = (ret_60 - mu_60) / sd_60.replace(0.0, np.nan)

    feats["rsi_14"] = _rsi(close, window=14)
    feats["dow"] = close.index.dayofweek.astype(float)

    regime = (spy_close > spy_sma200).astype(float)
    feats["regime_spy200"] = regime.reindex(close.index).fillna(0.0)

    return feats


def build_panel_dataset(
    panel: dict[str, pd.DataFrame],
    spy_df: pd.DataFrame,
    label_horizon: int,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> tuple[pd.DataFrame, pd.Series, pd.DatetimeIndex, np.ndarray]:
    """Build stacked feature panel with binary forward-sign labels.

    Returns
    -------
    X : pd.DataFrame
        Rows = (date, ticker) pairs; columns = features.
    y : pd.Series
        Binary label: 1 if forward ``label_horizon``-day return > 0 else 0.
    idx : pd.DatetimeIndex
        Date of each row (aligned with ticker_ids below).
    ticker_ids : np.ndarray
        Per-row ticker id (string).
    """
    spy_close = spy_df["adj_close"].astype(float)
    spy_sma200 = spy_close.rolling(200, min_periods=200).mean()

    xs: list[pd.DataFrame] = []
    ys: list[pd.Series] = []
    dates: list[pd.DatetimeIndex] = []
    tickers: list[np.ndarray] = []

    for ticker, df in sorted(panel.items()):
        feats = build_features(df, spy_close, spy_sma200)
        close = df["adj_close"].astype(float)
        fwd_ret = close.pct_change(label_horizon).shift(-label_horizon)
        label = (fwd_ret > 0).astype(float)
        mask = feats.index.to_series().between(start, end) & feats.notna().all(axis=1) & fwd_ret.notna()
        mask = mask.reindex(feats.index, fill_value=False)

        xf = feats.loc[mask].copy()
        yf = label.loc[xf.index]
        xs.append(xf)
        ys.append(yf)
        dates.append(xf.index)
        tickers.append(np.full(len(xf), ticker, dtype=object))

    X = pd.concat(xs, axis=0)
    y = pd.concat(ys, axis=0)
    idx = pd.DatetimeIndex(np.concatenate([d.values for d in dates]))
    ticker_ids = np.concatenate(tickers)
    X = X.reset_index(drop=True)
    y = y.reset_index(drop=True)
    return X, y, idx, ticker_ids


def purged_kfold_splits(
    dates: pd.DatetimeIndex,
    n_splits: int = 5,
    embargo_days: int = 5,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Purged K-fold by calendar time.

    Splits the unique dates into ``n_splits`` chronologically contiguous
    blocks; for each block used as validation, training rows are all rows
    with a unique date OUTSIDE that block AND outside the embargo window
    on either side. Per [ml_for_asset_managers, p.8, §1.4.2] and
    [advances_fin_ml, p.103-110].

    Embargo is applied as ``± embargo_days`` trading days around the
    validation block bounds; this matches the label-horizon leakage
    window since labels span ``H`` days forward.
    """
    unique_dates = np.array(sorted(np.unique(dates)))
    n = len(unique_dates)
    if n == 0:
        return []
    fold_size = n // n_splits
    folds: list[tuple[np.ndarray, np.ndarray]] = []
    all_rows = np.arange(len(dates))
    for k in range(n_splits):
        vs = k * fold_size
        ve = (k + 1) * fold_size if k < n_splits - 1 else n
        val_dates = unique_dates[vs:ve]
        val_start, val_end = val_dates[0], val_dates[-1]
        val_mask = (dates >= val_start) & (dates <= val_end)
        # Embargo window: exclude rows within ± embargo_days of val block.
        embargo_before = val_start - pd.Timedelta(days=embargo_days * 2)
        embargo_after = val_end + pd.Timedelta(days=embargo_days * 2)
        train_mask = (~val_mask) & (
            (dates < embargo_before) | (dates > embargo_after)
        )
        train_idx = all_rows[train_mask]
        val_idx = all_rows[val_mask]
        if len(train_idx) > 0 and len(val_idx) > 0:
            folds.append((train_idx, val_idx))
    return folds


def simulate_ml_classical(
    panel: dict[str, pd.DataFrame],
    spy_df: pd.DataFrame,
    config: MLClassicalConfig,
    is_start: pd.Timestamp,
    is_end: pd.Timestamp,
    oos_start: pd.Timestamp,
    oos_end: pd.Timestamp,
    fwd_end: pd.Timestamp,
) -> MLClassicalResult:
    """End-to-end Family-J simulation.

    Pipeline:

    1. Build features + labels on IS (for training) and IS+OOS+FWD (for
       prediction / evaluation).
    2. Purged K-fold CV on IS ONLY to record baseline accuracy
       [ml_for_asset_managers, p.8, §1.4.2]. Threshold is fixed by
       config (outer grid selects it via CSCV/PBO).
    3. Train a single ``GradientBoostingClassifier`` on the FULL IS
       panel (no refit).
    4. Predict P(up) for each (date, ticker) pair across IS+OOS+FWD.
    5. Simulate daily returns via ``prev_weight × next_return`` alignment
       [advances_fin_ml, p.31-34 honest timing]. Rebalance every
       ``rebalance_days`` trading days; target weight = position_size
       per ticker whose P(up) > threshold on the rebalance bar, else 0.
       Cap total weight at 1.0.
    6. Apply spread cost on absolute weight changes and BR 15% tax on
       monthly realized positive net return.

    No walk-forward retraining: the IS-trained model is frozen before
    OOS/FWD and evaluated without peeking. This is the V2-L3-safe
    research protocol per [ml_for_asset_managers, p.3-8].
    """
    # ---- Step 1: feature panel for prediction span (IS+OOS+FWD) ----
    predict_start = is_start
    predict_end = fwd_end
    spy_close = spy_df["adj_close"].astype(float)
    spy_sma200 = spy_close.rolling(200, min_periods=200).mean()

    per_ticker_feats: dict[str, pd.DataFrame] = {}
    per_ticker_close: dict[str, pd.Series] = {}
    all_dates = pd.DatetimeIndex([])
    for ticker, df in sorted(panel.items()):
        f = build_features(df, spy_close, spy_sma200)
        c = df["adj_close"].astype(float)
        per_ticker_feats[ticker] = f
        per_ticker_close[ticker] = c
        all_dates = all_dates.union(f.index)

    all_dates = pd.DatetimeIndex(sorted(all_dates))
    all_dates = all_dates[(all_dates >= predict_start) & (all_dates <= predict_end)]

    # ---- Step 2: build IS training panel with labels ----
    X_is, y_is, dates_is, tickers_is = build_panel_dataset(
        panel, spy_df, config.label_horizon, is_start, is_end
    )
    log.info(
        "IS panel: rows=%d tickers=%d date_range=%s→%s up_rate=%.3f",
        len(X_is),
        len(np.unique(tickers_is)),
        dates_is.min().date(),
        dates_is.max().date(),
        y_is.mean(),
    )

    # ---- Step 3: Purged K-fold CV on IS for diagnostic ----
    folds = purged_kfold_splits(
        dates_is,
        n_splits=config.n_kfold_splits,
        embargo_days=config.purged_embargo_days * max(1, config.label_horizon),
    )
    fold_accs: list[float] = []
    X_is_np = X_is.to_numpy(dtype=float)
    y_is_np = y_is.to_numpy(dtype=int)
    for k, (tr, va) in enumerate(folds):
        clf = GradientBoostingClassifier(
            n_estimators=config.n_estimators,
            max_depth=config.max_depth,
            learning_rate=config.learning_rate,
            random_state=config.random_state,
        )
        clf.fit(X_is_np[tr], y_is_np[tr])
        preds = (clf.predict_proba(X_is_np[va])[:, 1] > config.threshold).astype(int)
        fold_accs.append(float(accuracy_score(y_is_np[va], preds)))
    cv_acc_mean = float(np.mean(fold_accs)) if fold_accs else float("nan")
    cv_acc_std = float(np.std(fold_accs, ddof=1)) if len(fold_accs) > 1 else 0.0
    log.info("Purged K-fold CV accuracy: %.4f ± %.4f", cv_acc_mean, cv_acc_std)

    # ---- Step 4: train on full IS ----
    model = GradientBoostingClassifier(
        n_estimators=config.n_estimators,
        max_depth=config.max_depth,
        learning_rate=config.learning_rate,
        random_state=config.random_state,
    )
    model.fit(X_is_np, y_is_np)
    feat_importance = pd.Series(
        model.feature_importances_,
        index=X_is.columns,
        name="importance",
    ).sort_values(ascending=False)

    # ---- Step 5: predict for each (date, ticker) across the full span ----
    # We need features at each bar for each ticker, but only where feature
    # row is non-NaN. We do NOT require labels here (we are predicting,
    # not training).
    predictions_df = pd.DataFrame(index=all_dates, columns=sorted(panel.keys()), dtype=float)
    for ticker in sorted(panel.keys()):
        f = per_ticker_feats[ticker]
        f_in = f.reindex(all_dates)
        valid_mask = f_in.notna().all(axis=1)
        if not valid_mask.any():
            continue
        X_p = f_in.loc[valid_mask].to_numpy(dtype=float)
        prob_up = model.predict_proba(X_p)[:, 1]
        predictions_df.loc[valid_mask.index[valid_mask], ticker] = prob_up

    # ---- Step 6: build weight path ----
    tickers = sorted(panel.keys())
    weights = pd.DataFrame(0.0, index=all_dates, columns=tickers)
    last_weights = pd.Series(0.0, index=tickers)
    # Rebalance at the SIGNAL bar (t), for EXECUTION at t+1 (via shift
    # downstream in prev_weight × next_return).
    bar_idx = 0
    for ts in all_dates:
        if bar_idx % config.rebalance_days == 0:
            # Read predictions_df at ts (predictions computed on features
            # up to AND including close of t, which is the convention for
            # prev_weight × ret alignment).
            row = predictions_df.loc[ts]
            signals = (row > config.threshold).fillna(False)
            n_on = int(signals.sum())
            if n_on == 0:
                w = pd.Series(0.0, index=tickers)
            else:
                # Per-signal position_size, capped at 1.0 total.
                per = config.position_size
                total = per * n_on
                scale = min(1.0, 1.0 / total) if total > 0 else 0.0
                w = pd.Series(0.0, index=tickers)
                # scale=1 if total≤1; else shrink to sum to 1.
                w[signals.index[signals]] = per * scale if total > 1.0 else per
            last_weights = w
        weights.loc[ts] = last_weights.values
        bar_idx += 1

    # ---- Step 7: compute daily returns with prev_weight × next_return ----
    # Stack per-ticker returns on all_dates.
    ret_matrix = pd.DataFrame(0.0, index=all_dates, columns=tickers)
    for ticker in tickers:
        close = per_ticker_close[ticker]
        r = close.pct_change().reindex(all_dates).fillna(0.0)
        ret_matrix[ticker] = r

    # prev_weight × ret alignment: shift weights by 1 day.
    weights_shift = weights.shift(1).fillna(0.0)
    gross_daily = (weights_shift * ret_matrix).sum(axis=1)

    # ---- Step 8: spread cost on absolute weight changes ----
    weight_change = (weights - weights.shift(1).fillna(0.0)).abs().sum(axis=1)
    # Cost = spread × |Δw| (round-trip one-way on each side).
    spread_cost = weight_change * config.spread_one_way_pct
    net_pre_tax = gross_daily - spread_cost
    cum_cost = float(spread_cost.sum())

    # ---- Step 9: monthly BR 15% tax on realized positive returns ----
    # Approximation: at the first bar of each month, apply tax to the
    # prior month's net-positive cumulative return (and reset counter).
    # This is a conservative realized-gains proxy; actual BR rule only
    # taxes exits, but in a daily-rebalanced strategy most gains ARE
    # realized on the rebalance bar. Mandate §1 + plan §3.2.
    net_series = net_pre_tax.copy()
    cum_tax = 0.0
    month_starts = all_dates.to_series().groupby(
        [all_dates.year, all_dates.month]
    ).transform("first")
    prev_month = None
    month_ret_accum = 0.0
    taxed = pd.Series(0.0, index=all_dates)
    for ts in all_dates:
        m = (ts.year, ts.month)
        if prev_month is not None and m != prev_month:
            if month_ret_accum > 0:
                tax = month_ret_accum * config.tax_rate
                taxed.loc[ts] = tax  # charge at first day of new month
                cum_tax += tax
            month_ret_accum = 0.0
        month_ret_accum += float(net_pre_tax.loc[ts])
        prev_month = m
    net = net_pre_tax - taxed

    # ---- Step 10: equity curve ----
    equity = (1.0 + net).cumprod()

    return MLClassicalResult(
        daily_returns=net,
        equity=equity,
        weights=weights,
        predictions=predictions_df,
        feature_importance=feat_importance,
        threshold=config.threshold,
        is_purged_kfold_accuracy=cv_acc_mean,
        is_purged_kfold_std=cv_acc_std,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
    )
