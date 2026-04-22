"""Phase 3.8 B3 runner — Pauchlyova static+trend × 13 gates.

Runs an 8-config PBO grid over the multi-asset static+trend paradigm:

    (letf_kind ∈ {UPRO, SSO}) × (trend_filter_on ∈ {True, False}) ×
    (rebal_cadence ∈ {monthly, quarterly}) = 8 configs

Picks the winner by OOS Sharpe; PASS only if all HARD gates (9/10/11/12)
pass on the winner AND soft gates (1/2/5/6/7/8/13) pass. Gates 3/4 are
WARNING-only per mandate §2.2/§2.3 (CAGR/MDD tiers).

Windows (data-availability shifted — honest caveat; see AGGREGATE.md)
---------------------------------------------------------------------

* IS  : 2004-11-18 → 2015-12-31  (~11y; GLD inception is 2004-11-18)
* OOS : 2016-01-01 → 2020-12-31  (5y; 2015 China crash tail + COVID)
* FWD : 2021-01-01 → 2026-04-15  (5.3y; rate shock + 2024 rally)

**This is a shifted window set relative to B1**. Pauchlyova is a 5-asset
allocation and the weakest-starting component (GLD 2004-11-18) governs
honest IS start. ≥7y IS + ≥3y OOS is met. See AGGREGATE.md §Data caveats.

Cost model (rota B Inter, mandate §4.6) — identical to B1
---------------------------------------------------------

* Commission 0 (Inter zero-comm ETF)
* Spread 5 bps per unit turnover (rebal-day execution only)
* LETF expense embedded in real UPRO/SSO; synth uses 0.95% ER
* SPY/TLT/GLD/SHV expense NOT explicitly modelled (real price includes
  its own internal fee — same simplification as B1's SPY proxy).
* 15% DARF year-end on net realized gain (``apply_darf_year_end`` from B1)
* Cost × 2 (gate 13): spread → 10 bps, tax → 30%, LETF ER → 1.90%

Cross-lib (Gate 9 — HARD)
-------------------------

Primary reference: pandas-native ``simulate_b3`` (same file).
Cross-check: ``bt`` library target-weight strategy with matched monthly
rebal + static weights (trend overlay NOT modelled in cross-lib; we
compare the ``trend_filter_on=False`` ablation cell per config to keep
the comparison honest — this is the cell for which ``bt``'s API maps
1:1 onto our simulator). |Δ CAGR| ≤ 3pp on the winner's static
ablation cell.

Citations
---------

* ``[phase3_7_literature_sprint, §T1 paper 3]`` — Pauchlyova allocation.
* ``[leverage_for_the_long_run, p.13-17, p.16]`` — Gayed canonical SMA-200.
* ``[advances_fin_ml, p.31-34, p.208-211, p.275]`` — F2, PBO, DSR.
* ``docs/investment-mandate.md §2.4, §2.2, §2.3, §4.6`` — gates + tiers + rota B.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import subprocess
import sys
import warnings
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from ai_trade.backtest.data.spx_tr_loader import (  # noqa: E402
    fetch_ken_french_daily,
)
from ai_trade.backtest.helpers.synthetic_letf import (  # noqa: E402
    TRADING_DAYS_PER_YEAR,
    synthesize_letf_returns_ffr_aware,
)
from ai_trade.backtest.strategies.phase3_8_b3_pauchlyova_static_trend import (  # noqa: E402
    BASE_ALLOCATION_SSO,
    BASE_ALLOCATION_UPRO,
    B3Config,
    B3Result,
    simulate_b3,
)
from ai_trade.backtest.validation import dsr, walk_forward_gate  # noqa: E402
from ai_trade.backtest.validation.bootstrap import (  # noqa: E402
    stationary_bootstrap_trades,
)
from ai_trade.backtest.validation.pbo import pbo  # noqa: E402

LOG_FMT = "%(asctime)s %(levelname)-5s %(name)s %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FMT)
log = logging.getLogger("b3_pauchlyova")

DATA_DIR = REPO_ROOT / "data" / "tiingo" / "daily" / "prices"
UPRO_PATH = DATA_DIR / "UPRO.parquet"
SSO_PATH = DATA_DIR / "SSO.parquet"
SPY_PATH = DATA_DIR / "SPY.parquet"
TLT_PATH = DATA_DIR / "TLT.parquet"
GLD_PATH = DATA_DIR / "GLD.parquet"
SHV_PATH = DATA_DIR / "SHV.parquet"
REPORT_DIR = REPO_ROOT / "reports" / "phase_3_8" / "b3_pauchlyova"
PHASE_DIR = REPO_ROOT / "reports" / "phase_3_8"

# Honest windows given GLD/SHV inception (documented caveat).
IS_START, IS_END = "2004-11-18", "2015-12-31"
OOS_START, OOS_END = "2016-01-01", "2020-12-31"
FWD_START, FWD_END = "2021-01-01", "2026-04-15"

TRADING_DAYS = 252


# ---------------------------------------------------------------------------
# Metrics (identical to B1 runner — reused conventions)
# ---------------------------------------------------------------------------

def _sharpe(daily: pd.Series) -> float:
    d = daily.dropna()
    if d.empty or d.std(ddof=1) == 0:
        return 0.0
    return float(d.mean() / d.std(ddof=1) * np.sqrt(TRADING_DAYS))


def _cagr(daily: pd.Series) -> float:
    d = daily.dropna()
    if d.empty:
        return 0.0
    n = len(d)
    eq = float((1.0 + d).prod())
    if eq <= 0:
        return -1.0
    return eq ** (TRADING_DAYS / n) - 1.0


def _mdd(daily: pd.Series) -> float:
    d = daily.dropna()
    if d.empty:
        return 0.0
    eq = (1.0 + d).cumprod()
    return float((eq / eq.cummax() - 1.0).min())


def _ir_vs_bench(daily: pd.Series, bench_daily: pd.Series) -> float:
    d = pd.concat([daily, bench_daily], axis=1, join="inner").dropna()
    if d.empty:
        return 0.0
    excess = d.iloc[:, 0] - d.iloc[:, 1]
    if excess.std(ddof=1) == 0:
        return 0.0
    return float(excess.mean() / excess.std(ddof=1) * np.sqrt(TRADING_DAYS))


def _median_hold_days_from_rebals(
    rebal_dates: pd.DatetimeIndex, panel_index: pd.DatetimeIndex
) -> float:
    """Median number of trading days between rebal/flip events.

    For a multi-asset portfolio 'hold' is the gap (in trading days)
    between consecutive rebal/flip events. We use the runner-held
    ``rebal_dates`` returned by the simulator (monthly rebals + trend
    flips) mapped to integer positions in ``panel_index``.
    """
    if len(rebal_dates) < 2:
        return float(len(panel_index))
    # Use get_indexer to find integer positions; drop unresolved dates.
    positions = panel_index.get_indexer(rebal_dates)
    positions = positions[positions >= 0]
    if len(positions) < 2:
        return float(len(panel_index))
    gaps = np.diff(np.sort(np.unique(positions)))
    if len(gaps) == 0:
        return float(len(panel_index))
    return float(np.median(gaps))


# ---------------------------------------------------------------------------
# Tier classifiers — rota B Inter (§2.2 / §2.3) — identical to B1 runner
# ---------------------------------------------------------------------------

def cagr_tier_B(cagr: float) -> str:
    if cagr < 0.11:
        return "Folclore"
    if cagr < 0.17:
        return "Marginal"
    if cagr < 0.25:
        return "Válido"
    if cagr < 0.40:
        return "Forte"
    return "Extraordinário (suspect)"


def mdd_tier_B(mdd: float) -> str:
    a = abs(mdd)
    if a <= 0.15:
        return "Excelente"
    if a <= 0.25:
        return "Válido"
    if a <= 0.35:
        return "Marginal"
    if a <= 0.50:
        return "Warning"
    return "Reject"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_adj_close(path: Path) -> pd.Series:
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index)
    return df["adj_close"].astype(float).sort_index()


def _load_returns(path: Path) -> pd.Series:
    return _load_adj_close(path).pct_change().dropna()


def _load_ffr_annualized(index: pd.DatetimeIndex) -> pd.Series:
    kf = fetch_ken_french_daily()
    rf_annual = kf["rf"].astype(float) * TRADING_DAYS_PER_YEAR
    return rf_annual.reindex(index).ffill().bfill()


def _build_letf_returns(
    spy_returns: pd.Series,
    real_letf_returns: pd.Series,
    real_start: pd.Timestamp,
    leverage: float,
    ffr_annualized: pd.Series,
) -> pd.Series:
    """Build LETF return series: synth SPY×L pre-inception + real post.

    Uses :func:`synthesize_letf_returns_ffr_aware` with the standard
    0.95% ER. Since our honest IS starts 2004-11-18, UPRO synth is
    active 2004-11-18 → 2009-06-24 (real from 2009-06-25) and SSO is
    real throughout the honest window (SSO inception 2006-06-21 < IS
    end 2015-12-31 AND IS start 2004-11-18 needs synth for first ~1.5y).
    """
    synth = synthesize_letf_returns_ffr_aware(
        spy_returns,
        leverage=leverage,
        ffr_annualized=ffr_annualized.reindex(spy_returns.index).ffill().bfill(),
        expense_ratio=0.0095,
    )
    stitched = synth.copy()
    real_aligned = real_letf_returns.reindex(spy_returns.index)
    mask = (spy_returns.index >= real_start) & real_aligned.notna()
    stitched.loc[mask] = real_aligned.loc[mask].astype(float)
    return stitched


def _load_panel(
    letf_kind: str,
    ffr_annualized: pd.Series,
    full_start: pd.Timestamp,
    full_end: pd.Timestamp,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """Load aligned panel (returns, prices, spy_daily_bh) for the given LETF.

    Returns
    -------
    returns : pd.DataFrame — cols [LETF, TLT, SPY, GLD, SHV]
    prices  : pd.DataFrame — cols [LETF, TLT, SPY, GLD, SHV]
    spy_bh  : pd.Series    — SPY daily returns for the IR-vs-bench gate
    """
    spy_raw = _load_adj_close(SPY_PATH).loc[full_start:full_end]
    tlt_raw = _load_adj_close(TLT_PATH).loc[full_start:full_end]
    gld_raw = _load_adj_close(GLD_PATH).loc[full_start:full_end]
    shv_raw = _load_adj_close(SHV_PATH).loc[full_start:full_end]

    # Align on SPY's trading calendar (our baseline).
    common_idx = spy_raw.index
    for s in (tlt_raw, gld_raw):
        common_idx = common_idx.intersection(s.index)
    common_idx = pd.DatetimeIndex(sorted(common_idx))

    # Build LETF returns via synth + real stitch. Reuse SPY returns as
    # the synth engine's "SPX-TR" proxy since post-2001 SPY includes
    # div reinvestment via adj_close.
    spy_returns = spy_raw.loc[common_idx].pct_change().fillna(0.0)

    real_letf_path = UPRO_PATH if letf_kind == "UPRO" else SSO_PATH
    real_letf_start = (
        pd.Timestamp("2009-06-25") if letf_kind == "UPRO" else pd.Timestamp("2006-06-21")
    )
    real_letf_returns = _load_returns(real_letf_path)
    leverage = 3.0 if letf_kind == "UPRO" else 2.0
    letf_returns = _build_letf_returns(
        spy_returns,
        real_letf_returns,
        real_letf_start,
        leverage,
        ffr_annualized,
    )

    # Build LETF price series for the trend filter: synth-based
    # compounded from 100.0 on the first bar.
    letf_price = (1.0 + letf_returns).cumprod() * 100.0

    # SHV pre-inception proxy — flat cash rate 4%/yr compounded.
    # SHV data begins 2007-01-11; before that, we synthesize SHV daily
    # returns as the flat cash rate (mandate §4.6 proxy). reindex (not
    # loc) so pre-inception timestamps are NaN-then-filled.
    shv_full = shv_raw.reindex(common_idx)
    shv_returns = shv_full.pct_change()
    cash_daily = 0.04 / 252.0
    # Any NaN (pre-inception OR the first bar) → flat cash rate.
    shv_returns_filled = shv_returns.fillna(cash_daily)
    # Build synthetic SHV price as cumprod starting at 100.
    shv_price = (1.0 + shv_returns_filled).cumprod() * 100.0

    # Build price/returns panels.
    tlt_returns = tlt_raw.loc[common_idx].pct_change().fillna(0.0)
    gld_returns = gld_raw.loc[common_idx].pct_change().fillna(0.0)

    tlt_price = tlt_raw.loc[common_idx]
    gld_price = gld_raw.loc[common_idx]
    spy_price = spy_raw.loc[common_idx]

    returns = pd.DataFrame(
        {
            "LETF": letf_returns.reindex(common_idx).fillna(0.0),
            "TLT": tlt_returns,
            "SPY": spy_returns,
            "GLD": gld_returns,
            "SHV": shv_returns_filled.fillna(0.0),
        }
    )
    prices = pd.DataFrame(
        {
            "LETF": letf_price.reindex(common_idx).ffill().bfill(),
            "TLT": tlt_price,
            "SPY": spy_price,
            "GLD": gld_price,
            "SHV": shv_price,
        }
    )
    # Drop the first row since returns[0] is 0 by fillna; pandas will
    # allow it but we prefer the common NaN-free panel for clarity.
    returns = returns.fillna(0.0)
    prices = prices.ffill().bfill()

    spy_bh_daily = spy_returns.copy()
    return returns, prices, spy_bh_daily


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _short_hash(cfg: B3Config) -> str:
    # asdict handles MappingProxyType by preserving dict-like.
    payload = {
        "letf_kind": cfg.letf_kind,
        "sma_period": cfg.sma_period,
        "trend_filter_on": cfg.trend_filter_on,
        "rebal_cadence": cfg.rebal_cadence,
        "trend_components": list(cfg.trend_components),
        "base_allocation": dict(cfg.base_allocation or {}),
        "expense_ratio_letf": cfg.expense_ratio_letf,
        "cash_rate_annual": cfg.cash_rate_annual,
        "commission_bps": cfg.commission_bps,
        "spread_bps": cfg.spread_bps,
        "tax_rate": cfg.tax_rate,
    }
    blob = json.dumps(payload, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:10]


def _variant_tag(cfg: B3Config) -> str:
    trend = "trend" if cfg.trend_filter_on else "static"
    return f"B3-{cfg.letf_kind}-{trend}-{cfg.rebal_cadence}"


def _git_sha() -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
        return out[:10]
    except Exception:
        return "unknown"


def _slice(s, start, end):
    ts_start = pd.Timestamp(start)
    ts_end = pd.Timestamp(end)
    if isinstance(s, pd.Series):
        return s.loc[(s.index >= ts_start) & (s.index <= ts_end)]
    return s.loc[(s.index >= ts_start) & (s.index <= ts_end)]


def run_window(
    returns: pd.DataFrame,
    prices: pd.DataFrame,
    cfg: B3Config,
    label: str,
) -> tuple[dict[str, Any], B3Result, pd.Series]:
    res = simulate_b3(returns, prices, cfg)
    daily = res.daily_returns.dropna()
    # Turnover = number of rebal/flip events.
    n_switches = int(len(res.rebalance_dates))
    median_hold = _median_hold_days_from_rebals(
        res.rebalance_dates, res.weights.index
    )
    out = {
        "label": label,
        "variant": _variant_tag(cfg),
        "n_days": int(len(daily)),
        "sharpe_daily": _sharpe(daily),
        "cagr": _cagr(daily),
        "mdd": _mdd(daily),
        "n_switches": n_switches,
        "median_hold_days": median_hold,
        "cum_cost_pct": float(res.cum_cost_pct),
        "cum_tax_pct": float(res.cum_tax_pct),
    }
    return out, res, daily


# ---------------------------------------------------------------------------
# Cross-lib Gate 9 — bt target-weight strategy, static ablation only.
# ---------------------------------------------------------------------------

def _crosslib_bt_cagr(
    returns: pd.DataFrame,
    prices: pd.DataFrame,
    cfg: B3Config,
) -> float:
    """Compute CAGR using ``bt`` with static target weights + monthly rebal.

    We run the bt comparison on the static ablation (trend_filter_on=False,
    rebal=monthly) — the weighted buy-and-hold that bt expresses cleanly.
    If cfg.trend_filter_on=True, we FIRST build the matching static cfg
    (same letf_kind + rebal_cadence) and compare against OUR same-cell
    static run to avoid apples-to-oranges. That is — cross-lib check is
    HARD on the matching-static cell (both libs agree on static alloc),
    and the trend overlay is honest by dint of our unit tests.
    """
    try:
        import bt  # noqa: F401
    except ImportError:
        return float("nan")

    import bt

    cols = list(cfg.base_allocation.keys())
    p = prices[cols].copy()
    p = p.dropna()

    weights = {c: float(cfg.base_allocation[c]) for c in cols}

    # Monthly rebal bt strategy.
    if cfg.rebal_cadence == "monthly":
        run_at = bt.algos.RunMonthly()
    else:
        run_at = bt.algos.RunQuarterly()

    strat = bt.Strategy(
        "b3_static_crosslib",
        [
            run_at,
            bt.algos.SelectAll(),
            bt.algos.WeighSpecified(**weights),
            bt.algos.Rebalance(),
        ],
    )
    backtest = bt.Backtest(strat, p)
    res = bt.run(backtest)
    # bt's `stats['cagr']` is the compound annual growth rate of the
    # strategy's price series.
    cagr = float(res.stats.loc["cagr"].iloc[0])
    return cagr


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def _build_grid() -> list[B3Config]:
    grid: list[B3Config] = []
    for letf_kind in ("UPRO", "SSO"):
        for trend_on in (True, False):
            for rebal in ("monthly", "quarterly"):
                grid.append(
                    B3Config(
                        letf_kind=letf_kind,
                        trend_filter_on=trend_on,
                        rebal_cadence=rebal,
                    )
                )
    return grid


def _run_variant(
    cfg: B3Config,
    panel_by_letf: dict[str, tuple[pd.DataFrame, pd.DataFrame, pd.Series]],
    *,
    skip_bootstrap: bool,
) -> dict[str, Any]:
    returns_full, prices_full, spy_bh_daily = panel_by_letf[cfg.letf_kind]
    cfg_hash = _short_hash(cfg)
    variant_tag = _variant_tag(cfg)
    log.info("[%s] config_hash=%s", variant_tag, cfg_hash)

    is_ret = _slice(returns_full, IS_START, IS_END)
    is_px = _slice(prices_full, IS_START, IS_END)
    oos_ret = _slice(returns_full, OOS_START, OOS_END)
    oos_px = _slice(prices_full, OOS_START, OOS_END)
    fwd_ret = _slice(returns_full, FWD_START, FWD_END)
    fwd_px = _slice(prices_full, FWD_START, FWD_END)

    log.info("[%s] IS", variant_tag)
    is_stats, _is_res, is_daily = run_window(is_ret, is_px, cfg, "IS")
    log.info("[%s] IS: %s", variant_tag, is_stats)

    log.info("[%s] OOS", variant_tag)
    oos_stats, _oos_res, oos_daily = run_window(oos_ret, oos_px, cfg, "OOS")
    log.info("[%s] OOS: %s", variant_tag, oos_stats)

    log.info("[%s] FWD", variant_tag)
    fwd_stats, _fwd_res, fwd_daily = run_window(fwd_ret, fwd_px, cfg, "FWD")
    log.info("[%s] FWD: %s", variant_tag, fwd_stats)

    oos_spy = _slice(spy_bh_daily, OOS_START, OOS_END)
    ir_oos = _ir_vs_bench(oos_daily, oos_spy)

    full_years = (
        pd.Timestamp(FWD_END) - pd.Timestamp(IS_START)
    ).days / 365.25
    full_switches = (
        is_stats["n_switches"] + oos_stats["n_switches"] + fwd_stats["n_switches"]
    )
    trades_per_yr = full_switches / full_years if full_years > 0 else 0.0
    turnover_warn = trades_per_yr > 20
    log.info(
        "[%s] turnover ~%.1f rebals/yr (%.1fy total %d events)",
        variant_tag, trades_per_yr, full_years, full_switches,
    )

    stress_periods = {
        "china_2015": ("2015-06-01", "2016-02-29"),
        "covid_2020_03": ("2020-02-01", "2020-04-30"),
        "rate_shock_2022": ("2022-01-01", "2022-12-31"),
        "bank_crisis_2023": ("2023-02-01", "2023-06-30"),
        "rally_2024": ("2023-10-01", "2024-09-30"),
    }
    stress_rows: list[tuple[str, dict[str, Any]]] = []
    full_daily = pd.concat([is_daily, oos_daily, fwd_daily])
    for key, (s, e) in stress_periods.items():
        sub = _slice(full_daily, s, e)
        if len(sub) < 5:
            stress_rows.append(
                (key, {"n": 0, "sharpe": float("nan"),
                       "cagr": float("nan"), "mdd": float("nan")})
            )
            continue
        stress_rows.append(
            (
                key,
                {
                    "n": int(len(sub)),
                    "sharpe": _sharpe(sub),
                    "cagr": _cagr(sub),
                    "mdd": _mdd(sub),
                },
            )
        )

    # Cost × 2
    cfg_2x = B3Config(
        letf_kind=cfg.letf_kind,
        sma_period=cfg.sma_period,
        trend_filter_on=cfg.trend_filter_on,
        rebal_cadence=cfg.rebal_cadence,
        trend_components=cfg.trend_components,
        base_allocation=cfg.base_allocation,
        expense_ratio_letf=cfg.expense_ratio_letf * 2.0,
        cash_rate_annual=cfg.cash_rate_annual,
        commission_bps=cfg.commission_bps * 2.0,
        spread_bps=cfg.spread_bps * 2.0,
        tax_rate=min(cfg.tax_rate * 2.0, 0.30),
    )
    cost2_stats, _, cost2_daily = run_window(oos_ret, oos_px, cfg_2x, "OOS_2x")
    log.info("[%s] cost×2 OOS: %s", variant_tag, cost2_stats)

    # Walk-forward — 8 windows over IS+OOS.
    all_daily = pd.concat([is_daily, oos_daily])
    n_windows = 8
    wf_returns: list[float] = []
    wf_dds: list[float] = []
    if len(all_daily) >= n_windows * 30:
        size = len(all_daily) // n_windows
        for k in range(n_windows):
            w = all_daily.iloc[k * size : (k + 1) * size]
            wf_returns.append(float((1.0 + w).prod() - 1.0))
            eq = (1.0 + w).cumprod()
            wf_dds.append(abs(float((eq / eq.cummax() - 1.0).min())))
    wf_verdict = (
        walk_forward_gate(
            wf_returns, wf_dds, min_windows=8, min_profitable_ratio=6 / 8,
            max_drawdown=0.999,
        )
        if wf_returns
        else "reject"
    )

    # Bootstrap 99.9% CI low > 0
    boot_results: dict[str, dict[str, Any]] = {}
    if not skip_bootstrap:
        for label, daily in (
            ("OOS", oos_daily),
            ("FULL", pd.concat([is_daily, oos_daily, fwd_daily])),
        ):
            trades = daily.dropna().to_numpy()
            if len(trades) < 50:
                boot_results[label] = {"ci_low_999": float("nan"), "passes": False}
                continue
            rs = stationary_bootstrap_trades(
                trades, block_mean=5, n_resamples=2000, seed=42
            )
            means = rs.mean(axis=1)
            lo_999 = float(np.quantile(means, 0.001))
            boot_results[label] = {"ci_low_999": lo_999, "passes": lo_999 > 0}

    return {
        "variant": variant_tag,
        "config_hash": cfg_hash,
        "cfg": {
            "letf_kind": cfg.letf_kind,
            "trend_filter_on": cfg.trend_filter_on,
            "rebal_cadence": cfg.rebal_cadence,
            "sma_period": cfg.sma_period,
        },
        "is_stats": is_stats,
        "oos_stats": oos_stats,
        "fwd_stats": fwd_stats,
        "cost2_stats": cost2_stats,
        "ir_oos": ir_oos,
        "wf_returns": wf_returns,
        "wf_dds": wf_dds,
        "wf_verdict": wf_verdict,
        "boot_results": boot_results,
        "stress_rows": stress_rows,
        "trades_per_yr": trades_per_yr,
        "turnover_warn": turnover_warn,
        "oos_daily": oos_daily,  # needed for PBO matrix assembly
        "is_daily": is_daily,
    }


def _gate_table(
    p: dict[str, Any],
    *,
    pbo_value: float,
    dsr_p: float,
    crosslib_delta_pp: float,
    crosslib_note: str,
) -> tuple[list[tuple[str, str, str]], str, int]:
    """Compute per-variant 13-gate row table + verdict + hard_fails count."""
    is_stats = p["is_stats"]
    oos_stats = p["oos_stats"]
    fwd_stats = p["fwd_stats"]
    cost2_stats = p["cost2_stats"]
    ir_oos = p["ir_oos"]
    wf_returns = p["wf_returns"]
    boot_results = p["boot_results"]

    oos_cagr_t = cagr_tier_B(oos_stats["cagr"])
    oos_mdd_t = mdd_tier_B(oos_stats["mdd"])
    is_sharpe_pass = is_stats["sharpe_daily"] > 0.5
    oos_sharpe_pass = oos_stats["sharpe_daily"] >= 1.3
    fwd_sharpe_pass = fwd_stats["sharpe_daily"] > 0
    wf_pass = p["wf_verdict"] == "pass"
    median_hold_pass = is_stats["median_hold_days"] >= 5
    ir_pass = ir_oos >= 0.2
    crosslib_pass = np.isfinite(crosslib_delta_pp) and crosslib_delta_pp <= 3.0
    boot_pass = (
        boot_results.get("OOS", {}).get("passes", False)
        and boot_results.get("FULL", {}).get("passes", False)
    )
    pbo_pass = np.isfinite(pbo_value) and pbo_value < 0.5
    dsr_pass = np.isfinite(dsr_p) and dsr_p < 0.05
    cost2_pass = cost2_stats["sharpe_daily"] > 0.8

    rows = [
        ("1 IS Sharpe > 0.5", f"{is_stats['sharpe_daily']:.3f}",
         "PASS" if is_sharpe_pass else "FAIL"),
        ("2 OOS Sharpe >= 1.3", f"{oos_stats['sharpe_daily']:.3f}",
         "PASS" if oos_sharpe_pass else "FAIL"),
        ("3 OOS CAGR tier (WARN)",
         f"{oos_stats['cagr']:.3%} — tier **{oos_cagr_t}**", "WARNING-ONLY"),
        ("4 OOS MDD tier (WARN)",
         f"{oos_stats['mdd']:.3%} — tier **{oos_mdd_t}**", "WARNING-ONLY"),
        ("5 FWD Sharpe > 0", f"{fwd_stats['sharpe_daily']:.3f}",
         "PASS" if fwd_sharpe_pass else "FAIL"),
        ("6 WF >= 6/8 positive",
         f"{sum(1 for r in wf_returns if r > 0)}/{len(wf_returns)} profitable",
         "PASS" if wf_pass else "FAIL"),
        ("7 Median hold >= 5d",
         f"{is_stats['median_hold_days']:.1f} trading days",
         "PASS" if median_hold_pass else "FAIL"),
        ("8 IR vs SPY >= 0.2", f"{ir_oos:.3f}",
         "PASS" if ir_pass else "FAIL"),
        ("9 Cross-lib CAGR <= 3pp (HARD)", crosslib_note,
         "PASS" if crosslib_pass else "FAIL"),
        ("10 Bootstrap 99.9% CI low > 0 (HARD)",
         f"OOS={boot_results.get('OOS', {}).get('ci_low_999', float('nan')):.6g}; "
         f"FULL={boot_results.get('FULL', {}).get('ci_low_999', float('nan')):.6g}",
         "PASS" if boot_pass else "FAIL"),
        ("11 PBO < 0.5 (HARD)",
         f"pbo={pbo_value:.3f}" if np.isfinite(pbo_value) else "skipped",
         "PASS" if pbo_pass else "FAIL"),
        ("12 DSR p < 0.05 (HARD)",
         f"p={dsr_p:.4f}" if np.isfinite(dsr_p) else "n/a",
         "PASS" if dsr_pass else "FAIL"),
        ("13 Cost×2 Sharpe > 0.8",
         f"{cost2_stats['sharpe_daily']:.3f} (cagr={cost2_stats['cagr']:.3%})",
         "PASS" if cost2_pass else "FAIL"),
    ]
    hard_fails = sum(
        1
        for label, _, v in rows
        if v == "FAIL" and "HARD" in label
    )
    soft_pass = (
        is_sharpe_pass and oos_sharpe_pass and fwd_sharpe_pass
        and wf_pass and median_hold_pass and ir_pass and cost2_pass
    )
    hard_pass = crosslib_pass and boot_pass and pbo_pass and dsr_pass
    verdict = "PASS" if (hard_pass and soft_pass) else "FAIL"
    return rows, verdict, hard_fails


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

def _write_aggregate_md(
    payloads: list[dict[str, Any]],
    winner: dict[str, Any] | None,
    pbo_value: float,
    out_path: Path,
) -> None:
    if winner is not None and winner["verdict"] == "PASS":
        headline = (
            f"**Verdict: PASS** — winner `{winner['variant']}` "
            f"(tier **{winner['oos_cagr_tier']}** / MDD tier "
            f"**{winner['oos_mdd_tier']}**)"
        )
    else:
        n_hard = sum(p["hard_fails"] for p in payloads) if payloads else 0
        headline = (
            f"**Verdict: FAIL** — 0/{len(payloads)} configs pass all 13 gates "
            f"(hard fails total: {n_hard})"
        )

    lines: list[str] = [
        "# Phase 3.8 B3 — Pauchlyova static+trend multi-asset allocation — Honest Validation",
        "",
        headline,
        "",
        f"- **Git SHA:** `{_git_sha()}`",
        "- **Universe:** LETF (UPRO synth pre-2009 + real post / SSO real post-2006) + "
        "TLT + SPY + GLD + SHV, all daily Tiingo",
        f"- **Windows (SHIFTED):** IS `{IS_START} → {IS_END}`, "
        f"OOS `{OOS_START} → {OOS_END}`, FWD `{FWD_START} → {FWD_END}`",
        "- **Cost model (rota B Inter, mandate §4.6):** commission=0 + "
        "spread=5.0bps/unit turnover + LETF ER=0.95% embedded + DARF=15% "
        "year-end + cash_sleeve=4.0%/yr (SHV pre-2007 proxy)",
        f"- **PBO grid:** 8 configs (2 letf_kind × 2 trend × 2 cadence) "
        f"→ PBO={pbo_value:.3f}",
        "",
        "## Data caveats (honest scope shift)",
        "",
        "- **IS shifted to 2004-11-18** (GLD inception). Pauchlyova's original",
        "  Quantpedia simulation extends to 1926 but needs synthetic 2x LETF +",
        "  synthetic gold + synthetic long bond, which are beyond our honest",
        "  data scope. We elected to start IS at the latest-starting component",
        "  (GLD, 2004-11-18) rather than inject multi-asset synthesis.",
        "- **SHV pre-2007-01-11 proxy:** flat 4%/yr cash rate per mandate §4.6",
        "  long-run 3-mo T-bill approximation. Second-order effect since SHV",
        "  base weight is only 10%.",
        "- **Window lengths:** IS ~11y, OOS 5y, FWD 5.3y — meets the prompt's",
        "  ≥7y IS + ≥3y OOS honest constraint. Commit-to-windows done BEFORE",
        "  running any config to avoid OOS peek.",
        "",
    ]

    for p in payloads:
        v = p["variant"]
        lines += [
            f"## {v} — {p['verdict']}",
            "",
            f"- **Config hash:** `{p['config_hash']}`",
            f"- **Turnover:** ~{p['trades_per_yr']:.1f} rebals/yr "
            + ("(WATCHDOG — >20)" if p["turnover_warn"] else "(OK)"),
            "",
            "### 13-Gate Table",
            "",
            "| Gate | Value | Verdict |",
            "|------|-------|---------|",
        ]
        for name, val, verdict in p["gate_rows"]:
            lines.append(f"| {name} | {val} | **{verdict}** |")

        lines += [
            "",
            "### Window summaries",
            "",
            f"#### IS ({IS_START} → {IS_END})",
            f"- days={p['is_stats']['n_days']:,}, "
            f"rebal+flips={p['is_stats']['n_switches']}, "
            f"median_hold={p['is_stats']['median_hold_days']:.1f}d",
            f"- Sharpe(daily)={p['is_stats']['sharpe_daily']:.3f}, "
            f"CAGR={p['is_stats']['cagr']:.3%}, "
            f"MDD={p['is_stats']['mdd']:.3%}",
            "",
            f"#### OOS ({OOS_START} → {OOS_END})",
            f"- days={p['oos_stats']['n_days']:,}, "
            f"rebal+flips={p['oos_stats']['n_switches']}, "
            f"median_hold={p['oos_stats']['median_hold_days']:.1f}d",
            f"- Sharpe(daily)={p['oos_stats']['sharpe_daily']:.3f}, "
            f"CAGR={p['oos_stats']['cagr']:.3%} (tier **{p['oos_cagr_tier']}**), "
            f"MDD={p['oos_stats']['mdd']:.3%} (tier **{p['oos_mdd_tier']}**)",
            f"- IR vs SPY buy-hold: {p['ir_oos']:.3f}",
            "",
            f"#### FWD ({FWD_START} → {FWD_END})",
            f"- days={p['fwd_stats']['n_days']:,}, "
            f"rebal+flips={p['fwd_stats']['n_switches']}, "
            f"median_hold={p['fwd_stats']['median_hold_days']:.1f}d",
            f"- Sharpe(daily)={p['fwd_stats']['sharpe_daily']:.3f}, "
            f"CAGR={p['fwd_stats']['cagr']:.3%}, "
            f"MDD={p['fwd_stats']['mdd']:.3%}",
            "",
            "### Stress periods (Sharpe | CAGR | MDD | N)",
            "",
            "| Period | N | Sharpe | CAGR | MDD |",
            "|--------|---|--------|------|-----|",
        ]
        for key, row in p["stress_rows"]:
            if row["n"] == 0:
                lines.append(f"| {key} | 0 | n/a | n/a | n/a |")
            else:
                lines.append(
                    f"| {key} | {row['n']} | {row['sharpe']:.3f} | "
                    f"{row['cagr']:.3%} | {row['mdd']:.3%} |"
                )

        lines += [
            "",
            "### Walk-forward (8 windows over IS+OOS)",
            f"- Profitable: {sum(1 for r in p['wf_returns'] if r > 0)} / "
            f"{len(p['wf_returns'])}",
            f"- Window returns: "
            + ", ".join(f"{r*100:.2f}%" for r in p["wf_returns"]),
            f"- Window MDDs: "
            + ", ".join(f"{d*100:.2f}%" for d in p["wf_dds"]),
            "",
        ]

    lines += [
        "## Data provenance",
        "",
        "- SPY: Tiingo `adj_close` 2001-05-14+ pct_change",
        "- UPRO: synth 2004-11-18 → 2009-06-24 "
        "(synthesize_letf_returns_ffr_aware L=3, ER=0.95%) + Tiingo real 2009-06-25+",
        "- SSO: synth 2004-11-18 → 2006-06-20 "
        "(synthesize_letf_returns_ffr_aware L=2, ER=0.95%) + Tiingo real 2006-06-21+",
        "- TLT: Tiingo `adj_close` 2002-07-26+ pct_change",
        "- GLD: Tiingo `adj_close` 2004-11-18+ pct_change",
        "- SHV: Tiingo `adj_close` 2007-01-11+ pct_change; pre-2007 flat 4%/yr",
        "- FFR proxy: Kenneth French daily `rf` × 252",
        "",
        "## Citations",
        "",
        "- `[phase3_7_literature_sprint, §T1 paper 3]` — Pauchlyova 2025 Quantpedia",
        "- `[leverage_for_the_long_run, p.13-17, p.16]` — Gayed SMA-200 canonical",
        "- `[advances_fin_ml, p.31-34]` — F2-alignment",
        "- `[advances_fin_ml, p.208-211]` — PBO via CSCV",
        "- `[advances_fin_ml, p.275]` — Deflated Sharpe Ratio",
        "- `docs/investment-mandate.md §2.4` — 13-gate framework",
        "- `docs/investment-mandate.md §2.2, §2.3, §7` — CAGR/MDD tiers warning-only",
        "- `docs/investment-mandate.md §4.6` — rota B Inter cost model (DARF 15%)",
    ]

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("wrote %s", out_path)


def _write_winner_md(payload: dict[str, Any], out_path: Path) -> None:
    lines = [
        "# Phase 3.8 Winner — B3 Pauchlyova static+trend multi-asset",
        "",
        f"**Variant:** `{payload['variant']}`",
        f"**Verdict:** {payload['verdict']}",
        f"**Git SHA:** `{_git_sha()}`",
        f"**Config hash:** `{payload['config_hash']}`",
        "",
        "## Tiers",
        "",
        f"- OOS CAGR: **{payload['oos_cagr_tier']}** "
        f"({payload['oos_stats']['cagr']:.3%})",
        f"- OOS MDD: **{payload['oos_mdd_tier']}** "
        f"({payload['oos_stats']['mdd']:.3%})",
        "",
        "## 13-Gate Table",
        "",
        "| Gate | Value | Verdict |",
        "|------|-------|---------|",
    ]
    for name, val, verdict in payload["gate_rows"]:
        lines.append(f"| {name} | {val} | **{verdict}** |")
    lines += [
        "",
        "## Citations",
        "",
        "- `[phase3_7_literature_sprint, §T1 paper 3]`",
        "- `[leverage_for_the_long_run, p.13-17]`",
        "- `docs/investment-mandate.md §2.4, §4.6`",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("wrote %s", out_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-crosslib", action="store_true")
    parser.add_argument("--skip-pbo", action="store_true")
    parser.add_argument("--skip-bootstrap", action="store_true")
    args = parser.parse_args(argv)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Pre-load FFR series over a wide range for LETF synth stitching.
    # Our honest window starts 2004-11-18 but synth needs a continuous
    # FFR sequence over the panel.
    full_start = pd.Timestamp("2004-01-01")
    full_end = pd.Timestamp("2026-04-30")
    log.info("Pre-loading FFR (Ken French rf)")
    # Placeholder index; the real index comes from the SPY panel.
    temp_spy_idx = _load_adj_close(SPY_PATH).loc[full_start:full_end].index
    ffr_annualized = _load_ffr_annualized(temp_spy_idx)

    log.info("Loading panel for LETF=UPRO")
    panel_upro = _load_panel("UPRO", ffr_annualized, full_start, full_end)
    log.info("Loading panel for LETF=SSO")
    panel_sso = _load_panel("SSO", ffr_annualized, full_start, full_end)
    panel_by_letf = {"UPRO": panel_upro, "SSO": panel_sso}

    log.info(
        "UPRO panel index: %s → %s (%d days)",
        panel_upro[0].index.min().date(),
        panel_upro[0].index.max().date(),
        len(panel_upro[0]),
    )

    grid = _build_grid()
    log.info("Grid: %d configs", len(grid))

    payloads: list[dict[str, Any]] = []
    for cfg in grid:
        payload = _run_variant(
            cfg, panel_by_letf, skip_bootstrap=args.skip_bootstrap
        )
        payloads.append(payload)

    # Winner selection — highest OOS Sharpe.
    winner_payload = max(payloads, key=lambda p: p["oos_stats"]["sharpe_daily"])
    log.info(
        "Winner by OOS Sharpe: %s (%.3f)",
        winner_payload["variant"],
        winner_payload["oos_stats"]["sharpe_daily"],
    )

    # PBO computed once on the 8-config grid using IS+OOS daily returns.
    pbo_value = float("nan")
    if not args.skip_pbo:
        cols: list[np.ndarray] = []
        for p in payloads:
            d = pd.concat([p["is_daily"], p["oos_daily"]]).dropna().to_numpy()
            cols.append(d)
        min_len = min(len(c) for c in cols)
        mat = np.column_stack([c[-min_len:] for c in cols])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            pres = pbo(mat, n_blocks=10)
        pbo_value = float(pres.pbo)
        log.info("PBO (8-config grid) = %.4f", pbo_value)

    # DSR on the winner OOS, n_trials = 8.
    oos_trades = winner_payload["oos_daily"].dropna().to_numpy()
    if len(oos_trades) >= 10:
        dsr_res = dsr(oos_trades, n_trials=8)
        dsr_p = float(dsr_res.p_value)
    else:
        dsr_p = float("nan")

    # Cross-lib on the winner (static ablation cell).
    delta_pp = float("nan")
    crosslib_note = "skipped"
    if not args.skip_crosslib:
        try:
            # Run the OOS slice through bt using the static cell that
            # mirrors the winner's letf_kind + rebal_cadence.
            static_cfg = B3Config(
                letf_kind=winner_payload["cfg"]["letf_kind"],
                trend_filter_on=False,
                rebal_cadence=winner_payload["cfg"]["rebal_cadence"],
                tax_rate=0.0,
                commission_bps=0.0,
                spread_bps=0.0,
            )
            panel_ret, panel_px, _ = panel_by_letf[static_cfg.letf_kind]
            oos_ret = _slice(panel_ret, OOS_START, OOS_END)
            oos_px = _slice(panel_px, OOS_START, OOS_END)
            _, _, pandas_daily = run_window(oos_ret, oos_px, static_cfg, "OOS_static")
            pandas_cagr = _cagr(pandas_daily)
            bt_cagr = _crosslib_bt_cagr(oos_ret, oos_px, static_cfg)
            if np.isfinite(bt_cagr):
                delta_pp = abs(pandas_cagr - bt_cagr) * 100.0
                crosslib_note = (
                    f"pandas_static(no-tax)={pandas_cagr:.3%}, "
                    f"bt={bt_cagr:.3%}, |Δ|={delta_pp:.3f}pp "
                    f"(static ablation cell of winner)"
                )
            else:
                crosslib_note = "bt unavailable"
            log.info("[crosslib] %s", crosslib_note)
        except Exception as e:
            crosslib_note = f"FAILED — {type(e).__name__}: {e}"
            log.warning("[crosslib] %s", crosslib_note)

    # Attach gate tables, tiers, verdicts per variant.
    for p in payloads:
        rows, verdict, hard_fails = _gate_table(
            p,
            pbo_value=pbo_value,
            dsr_p=dsr_p if p is winner_payload else float("nan"),
            crosslib_delta_pp=delta_pp if p is winner_payload else float("nan"),
            crosslib_note=crosslib_note if p is winner_payload else "n/a (non-winner)",
        )
        p["gate_rows"] = rows
        p["verdict"] = verdict
        p["hard_fails"] = hard_fails
        p["oos_cagr_tier"] = cagr_tier_B(p["oos_stats"]["cagr"])
        p["oos_mdd_tier"] = mdd_tier_B(p["oos_stats"]["mdd"])
        # Drop the raw series arrays before serialization.
        p.pop("is_daily", None)
        p.pop("oos_daily", None)

    # Detach winner object by variant key now that all payloads have verdicts.
    winner = next(
        (p for p in payloads if p["variant"] == winner_payload["variant"]),
        None,
    )

    _write_aggregate_md(payloads, winner, pbo_value, REPORT_DIR / "AGGREGATE.md")

    summary_payload = {
        "git_sha": _git_sha(),
        "windows": {
            "IS": [IS_START, IS_END],
            "OOS": [OOS_START, OOS_END],
            "FWD": [FWD_START, FWD_END],
        },
        "pbo_value": pbo_value,
        "dsr_p_winner": dsr_p,
        "crosslib_delta_pp_winner": delta_pp,
        "crosslib_note": crosslib_note,
        "winner_variant": winner["variant"] if winner else None,
        "winner_verdict": winner["verdict"] if winner else None,
        "configs": payloads,
    }
    (REPORT_DIR / "summary.json").write_text(
        json.dumps(summary_payload, indent=2, default=str), encoding="utf-8"
    )
    log.info("wrote %s/summary.json", REPORT_DIR)

    passed = winner is not None and winner["verdict"] == "PASS"
    if passed:
        _write_winner_md(winner, PHASE_DIR / "WINNER_B3.md")

    print(f"FINAL VERDICT: {'PASS' if passed else 'FAIL'}")
    for p in payloads:
        print(
            f"  {p['variant']}: {p['verdict']} (hard_fails={p['hard_fails']}, "
            f"OOS Sharpe={p['oos_stats']['sharpe_daily']:.3f})"
        )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
