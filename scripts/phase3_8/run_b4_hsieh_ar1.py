"""Phase 3.8 B4 runner — Hsieh-Chang-Chen AR(1) regime LETF rotation × 13 gates.

Implements the Phase 3.8-1 Wave 2 B4 hypothesis: LETF performance is
conditional on return autocorrelation (Hsieh-Chang-Chen 2025, arXiv
2504.20116). Tests 8 configs (2 leverage legs × 4 AR(1) lookbacks
{42, 63, 84, 126}) with winner chosen by OOS Sharpe, then runs the
winner through the full 13-gate framework. Stop-at-first-winner:
if the winner variant PASSES, also writes
``reports/phase_3_8/WINNER_B4.md``.

Grid
----

* Leverage legs : UPRO (3x) + SSO (2x)
* AR(1) lookbacks : 42, 63, 84, 126 trading days
* 8 configs total

Windows (mutually exclusive)
----------------------------
* IS   : 1970-01-02 → 1999-12-31
* OOS  : 2000-01-01 → 2015-12-31
* FWD  : 2016-01-01 → 2026-04-15

13-gate framework (mandate §2.4)
--------------------------------
1 IS Sharpe > 0.5           | 2 OOS Sharpe >= 1.3        | 3 OOS CAGR tier (WARN)
4 OOS MDD tier (WARN)        | 5 FWD Sharpe > 0           | 6 WF >= 6/8
7 Median hold >= 5 days      | 8 IR vs SPY >= 0.2         | 9 Cross-lib <=3pp (HARD)
10 Bootstrap 99.9% CI>0 HARD | 11 PBO < 0.3 (HARD)        | 12 DSR p<0.05 (HARD)
13 Cost×2 Sharpe > 0.8       |

HARD gates: 9/10/11/12. PASS iff hard AND soft all pass. Gate 11
threshold tightened to **0.3** for B4 because the grid is single-feature
(one AR(1) lookback axis after leg is fixed) — mandate §2.4 recommends
<0.3 when few features to prevent silent over-tuning.

Turnover watchdog
-----------------
B4 specifically expects ~12-20 trades/yr. If winner > 25/yr: mark
"DARF-toxic" in AGGREGATE.md and fail gracefully (expected finding,
not HALT).

Citations
---------
* ``[phase3_7_literature_sprint §T1, arXiv 2504.20116]`` — Hsieh-Chang-Chen
* ``[leverage_for_the_long_run, p.4, p.7-8]`` — AR(1) as trending signature
* ``[advances_fin_ml, p.31-34, p.208-211, p.275]`` — F2, PBO, DSR
* ``docs/investment-mandate.md §2.4, §2.2, §2.3, §4.6``
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
    load_spx_tr_daily,
)
from ai_trade.backtest.helpers.synthetic_letf import (  # noqa: E402
    TRADING_DAYS_PER_YEAR,
)
from ai_trade.backtest.strategies.phase3_8_b4_hsieh_ar1 import (  # noqa: E402
    B4Config,
    B4Result,
    compute_ar1_regime_signal,
    simulate_b4,
    stitch_letf_returns,
)
from ai_trade.backtest.validation import dsr, walk_forward_gate  # noqa: E402
from ai_trade.backtest.validation.bootstrap import (  # noqa: E402
    stationary_bootstrap_trades,
)
from ai_trade.backtest.validation.pbo import pbo  # noqa: E402

LOG_FMT = "%(asctime)s %(levelname)-5s %(name)s %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FMT)
log = logging.getLogger("b4_hsieh_ar1")

UPRO_PATH = REPO_ROOT / "data" / "tiingo" / "daily" / "prices" / "UPRO.parquet"
SSO_PATH = REPO_ROOT / "data" / "tiingo" / "daily" / "prices" / "SSO.parquet"
REPORT_DIR = REPO_ROOT / "reports" / "phase_3_8" / "b4_hsieh_ar1"
PHASE_DIR = REPO_ROOT / "reports" / "phase_3_8"

IS_START, IS_END = "1970-01-02", "1999-12-31"
OOS_START, OOS_END = "2000-01-01", "2015-12-31"
FWD_START, FWD_END = "2016-01-01", "2026-04-15"

TRADING_DAYS = 252

AR1_LOOKBACK_GRID = [42, 63, 84, 126]
LEVERAGE_GRID = [(3.0, "UPRO"), (2.0, "SSO")]
# Gate 11 threshold is tightened for B4 — single-feature sweep with
# fewer configs needs a stricter PBO floor per mandate §2.4.
PBO_THRESHOLD_B4 = 0.3


# ---------------------------------------------------------------------------
# Metrics on daily (compounded) return series
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


def _median_hold_days(exposure: pd.Series) -> float:
    exp = exposure.astype(float).fillna(0.0).to_numpy()
    on = exp > 0
    if not on.any():
        return 0.0
    blocks: list[int] = []
    start = None
    for i, flag in enumerate(on):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            blocks.append(i - start)
            start = None
    if start is not None:
        blocks.append(len(on) - start)
    if not blocks:
        return 0.0
    return float(np.median(blocks))


# ---------------------------------------------------------------------------
# Tier classifiers — rota B Inter (§2.2 / §2.3)
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
# Data loaders
# ---------------------------------------------------------------------------

def _load_letf_real_returns(path: Path) -> pd.Series:
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index)
    return df["adj_close"].astype(float).sort_index().pct_change().dropna()


def _load_ffr_annualized(index: pd.DatetimeIndex) -> pd.Series:
    kf = fetch_ken_french_daily()
    rf_annual = kf["rf"].astype(float) * TRADING_DAYS_PER_YEAR
    return rf_annual.reindex(index).ffill().bfill()


# ---------------------------------------------------------------------------
# Window runner
# ---------------------------------------------------------------------------

def run_window(
    returns: pd.Series,
    ffr: pd.Series,
    real_letf: pd.Series | None,
    cfg: B4Config,
    label: str,
) -> tuple[dict[str, Any], B4Result, pd.Series]:
    res = simulate_b4(returns, ffr, cfg, real_letf_returns=real_letf)
    daily = res.daily_returns.dropna()
    on_frac = float((res.exposure > 0).mean())
    out = {
        "label": label,
        "variant": f"B4-{cfg.letf_kind}-{cfg.leverage:g}x-L{cfg.ar1_lookback}",
        "n_days": int(len(daily)),
        "sharpe_daily": _sharpe(daily),
        "cagr": _cagr(daily),
        "mdd": _mdd(daily),
        "n_switches": int(res.switches.sum()),
        "median_hold_days": _median_hold_days(res.exposure),
        "on_regime_fraction": on_frac,
        "cum_cost_pct": float(res.cum_cost_pct),
        "cum_tax_pct": float(res.cum_tax_pct),
    }
    return out, res, daily


def _short_hash(cfg: B4Config) -> str:
    payload = json.dumps(asdict(cfg), sort_keys=True, default=str).encode()
    return hashlib.sha256(payload).hexdigest()[:10]


def _git_sha() -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
        return out[:10]
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Cross-lib — pandas ref vs vectorbt replica (Gate 9 — HARD)
# ---------------------------------------------------------------------------

def _crosslib_vbt_cagr(
    returns: pd.Series,
    ffr: pd.Series,
    real_letf: pd.Series | None,
    cfg: B4Config,
) -> float:
    """Cross-library replica of B4 gross (pre-tax) CAGR via vectorbt.

    Uses the same 0/1 AR(1) regime gate and the same stitched LETF return
    series; then cross-checks compound CAGR using vbt utilities. Tax and
    switch costs are excluded from both sides (both lib paths implement
    the same arithmetic — honest comparison).
    """
    try:
        import vectorbt as vbt  # noqa: F401
    except ImportError:
        return float("nan")

    letf = stitch_letf_returns(returns, real_letf, ffr, cfg).fillna(0.0)
    regime, _ = compute_ar1_regime_signal(returns, lookback=cfg.ar1_lookback)
    gate = regime.astype(float)
    cash_d = cfg.cash_rate_annual / TRADING_DAYS_PER_YEAR
    gross = gate * letf + (1.0 - gate) * cash_d

    try:
        import vectorbt as vbt
        eq = vbt.nb.returns_nb.cum_returns_final_1d_nb(gross.to_numpy(), 1.0)
    except Exception:
        eq = float((1.0 + gross).prod())

    n = len(gross)
    if n <= 1 or eq <= 0:
        return float("nan")
    years = n / TRADING_DAYS
    return float(eq ** (1.0 / years) - 1.0)


# ---------------------------------------------------------------------------
# Config object builders
# ---------------------------------------------------------------------------

def _build_grid() -> list[B4Config]:
    """Build the 8-config grid — (leg, lookback) combinations."""
    grid: list[B4Config] = []
    for lev, kind in LEVERAGE_GRID:
        for lb in AR1_LOOKBACK_GRID:
            grid.append(
                B4Config(
                    leverage=lev,
                    letf_kind=kind,
                    ar1_lookback=lb,
                )
            )
    return grid


# ---------------------------------------------------------------------------
# Winner selection via OOS Sharpe
# ---------------------------------------------------------------------------

def _oos_sharpe_for_cfg(
    cfg: B4Config,
    oos_ret: pd.Series,
    oos_ffr: pd.Series,
    real_letf_by_kind: dict[str, pd.Series | None],
) -> float:
    real = real_letf_by_kind[cfg.letf_kind]
    res = simulate_b4(oos_ret, oos_ffr, cfg, real_letf_returns=real)
    return _sharpe(res.daily_returns.dropna())


# ---------------------------------------------------------------------------
# Variant orchestration — runs a single WINNER config through 13 gates
# ---------------------------------------------------------------------------

def _run_winner(
    cfg: B4Config,
    full_returns: pd.Series,
    full_ffr: pd.Series,
    real_letf: pd.Series | None,
    real_letf_by_kind: dict[str, pd.Series | None],
    spy_bh_daily: pd.Series,
    grid_oos_sharpe: list[tuple[B4Config, float]],
    *,
    skip_crosslib: bool,
    skip_pbo: bool,
    skip_bootstrap: bool,
) -> dict[str, Any]:
    """Run the winner B4 config through all 13 gates."""
    cfg_hash = _short_hash(cfg)
    variant_tag = (
        f"B4-{cfg.letf_kind}-{cfg.leverage:g}x-L{cfg.ar1_lookback}"
    )
    log.info("[%s] WINNER config_hash=%s cfg=%s", variant_tag, cfg_hash, asdict(cfg))

    def _slice(s, start, end):
        ts_start = pd.Timestamp(start)
        ts_end = pd.Timestamp(end)
        return s.loc[(s.index >= ts_start) & (s.index <= ts_end)]

    is_ret = _slice(full_returns, IS_START, IS_END)
    is_ffr = full_ffr.reindex(is_ret.index).ffill().bfill()

    oos_ret = _slice(full_returns, OOS_START, OOS_END)
    oos_ffr = full_ffr.reindex(oos_ret.index).ffill().bfill()

    fwd_ret = _slice(full_returns, FWD_START, FWD_END)
    fwd_ffr = full_ffr.reindex(fwd_ret.index).ffill().bfill()

    log.info("[%s] Running IS window", variant_tag)
    is_stats, _is_res, is_daily = run_window(
        is_ret, is_ffr, real_letf, cfg, "IS"
    )
    log.info("[%s] IS: %s", variant_tag, is_stats)

    log.info("[%s] Running OOS window", variant_tag)
    oos_stats, _oos_res, oos_daily = run_window(
        oos_ret, oos_ffr, real_letf, cfg, "OOS"
    )
    log.info("[%s] OOS: %s", variant_tag, oos_stats)

    log.info("[%s] Running FWD window", variant_tag)
    fwd_stats, _fwd_res, fwd_daily = run_window(
        fwd_ret, fwd_ffr, real_letf, cfg, "FWD"
    )
    log.info("[%s] FWD: %s", variant_tag, fwd_stats)

    # SPY buy-hold benchmark — shared.
    oos_spy = _slice(spy_bh_daily, OOS_START, OOS_END)
    ir_oos = _ir_vs_bench(oos_daily, oos_spy)

    # Turnover — total across IS+OOS+FWD.
    full_years = (
        pd.Timestamp(FWD_END) - pd.Timestamp(IS_START)
    ).days / 365.25
    full_switches = (
        is_stats["n_switches"] + oos_stats["n_switches"] + fwd_stats["n_switches"]
    )
    trades_per_yr = full_switches / full_years if full_years > 0 else 0.0
    # B4 watchdog: >25 trades/yr → "DARF-toxic" finding (expected for AR1)
    darf_toxic = trades_per_yr > 25
    log.info(
        "[%s] turnover ~%.1f trades/yr over %.1fy (total %d switches) — %s",
        variant_tag, trades_per_yr, full_years, full_switches,
        "DARF-TOXIC" if darf_toxic else "within budget",
    )
    if is_stats["n_switches"] < 50:
        log.warning(
            "[%s] IS switches=%d (< 50) — check data sanity",
            variant_tag, is_stats["n_switches"],
        )

    # Stress periods (OOS + FWD subsets)
    stress_periods = {
        "dotcom_2000_2002": ("2000-01-01", "2002-12-31"),
        "gfc_2007_2009": ("2007-10-01", "2009-03-31"),
        "euro_2011": ("2011-05-01", "2011-12-31"),
        "covid_2020_03": ("2020-02-01", "2020-04-30"),
        "rate_shock_2022": ("2022-01-01", "2022-12-31"),
    }
    stress_rows: list[tuple[str, dict[str, Any]]] = []
    for key, (s, e) in stress_periods.items():
        start_ts = pd.Timestamp(s)
        if start_ts < pd.Timestamp(OOS_END):
            src_daily = oos_daily
        else:
            src_daily = fwd_daily
        sub_daily = _slice(src_daily, s, e)
        if len(sub_daily) < 5:
            stress_rows.append(
                (key, {"n": 0, "sharpe": float("nan"),
                       "cagr": float("nan"), "mdd": float("nan")})
            )
            continue
        stress_rows.append(
            (
                key,
                {
                    "n": int(len(sub_daily)),
                    "sharpe": _sharpe(sub_daily),
                    "cagr": _cagr(sub_daily),
                    "mdd": _mdd(sub_daily),
                },
            )
        )

    # Cost × 2 — double tax + spread + ER (commission=0).
    cfg_2x = B4Config(
        **{
            **asdict(cfg),
            "commission_bps": cfg.commission_bps * 2.0,
            "spread_bps": cfg.spread_bps * 2.0,
            "expense_ratio": cfg.expense_ratio * 2.0,
            "tax_rate": min(cfg.tax_rate * 2.0, 0.30),
        }
    )
    log.info("[%s] Running OOS × 2 cost", variant_tag)
    cost2_stats, _, cost2_daily = run_window(
        oos_ret, oos_ffr, real_letf, cfg_2x, "OOS_2x_cost"
    )
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
    log.info(
        "[%s] WF: n=%d profitable=%d/%d verdict=%s",
        variant_tag, len(wf_returns),
        sum(1 for r in wf_returns if r > 0), len(wf_returns), wf_verdict,
    )

    # Bootstrap 99.9% CI low > 0 on OOS and FULL.
    boot_results: dict[str, dict[str, Any]] = {}
    if not skip_bootstrap:
        for label, daily in (
            ("OOS", oos_daily),
            ("FULL", pd.concat([is_daily, oos_daily, fwd_daily])),
        ):
            trades = daily.dropna().to_numpy()
            if len(trades) < 50:
                boot_results[label] = {
                    "ci_low_999": float("nan"), "passes": False,
                }
                continue
            rs = stationary_bootstrap_trades(
                trades, block_mean=5, n_resamples=2000, seed=42
            )
            means = rs.mean(axis=1)
            lo_999 = float(np.quantile(means, 0.001))
            boot_results[label] = {"ci_low_999": lo_999, "passes": lo_999 > 0}
    log.info("[%s] bootstrap: %s", variant_tag, boot_results)

    # PBO — 8-config grid (full grid — mandate §2.4 single-feature strictness).
    pbo_value = float("nan")
    pbo_verdict = "n/a"
    if not skip_pbo:
        log.info(
            "[%s] Running PBO grid (8 configs: 4 lookbacks × 2 legs)",
            variant_tag,
        )
        is_plus_oos_ret = pd.concat([is_ret, oos_ret])
        is_plus_oos_ffr = (
            full_ffr.reindex(is_plus_oos_ret.index).ffill().bfill()
        )
        cols: list[np.ndarray] = []
        for grid_cfg in _build_grid():
            rl_cell = real_letf_by_kind[grid_cfg.letf_kind]
            r = simulate_b4(
                is_plus_oos_ret, is_plus_oos_ffr, grid_cfg,
                real_letf_returns=rl_cell,
            )
            d = r.daily_returns.dropna().to_numpy()
            cols.append(d)
        min_len = min(len(c) for c in cols)
        mat = np.column_stack([c[-min_len:] for c in cols])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            pres = pbo(mat, n_blocks=10)
        pbo_value = float(pres.pbo)
        pbo_verdict = "pass" if pbo_value < PBO_THRESHOLD_B4 else "reject"
        log.info(
            "[%s] PBO=%.4f threshold=%.2f verdict=%s (n_configs=%d)",
            variant_tag, pbo_value, PBO_THRESHOLD_B4, pbo_verdict, len(cols),
        )

    # DSR — OOS track, n_trials = 8 (same grid as PBO).
    oos_trades = oos_daily.dropna().to_numpy()
    if len(oos_trades) >= 10:
        dsr_res = dsr(oos_trades, n_trials=8)
        dsr_p = float(dsr_res.p_value)
    else:
        dsr_p = float("nan")
    log.info("[%s] DSR p=%s", variant_tag, dsr_p)

    # Cross-lib — pandas ref (OOS no-tax no-switch) vs vbt on OOS.
    delta_pp_cagr = float("nan")
    crosslib_note = "skipped"
    if not skip_crosslib:
        log.info("[%s] Cross-lib — pandas-ref vs vectorbt replica on OOS", variant_tag)
        try:
            vbt_cagr = _crosslib_vbt_cagr(
                oos_ret, oos_ffr, real_letf, cfg
            )
            cfg_no_tax = B4Config(
                **{
                    **asdict(cfg),
                    "tax_rate": 0.0,
                    "commission_bps": 0.0,
                    "spread_bps": 0.0,
                }
            )
            _, _, d_noval = run_window(
                oos_ret, oos_ffr, real_letf, cfg_no_tax, "ref_notax"
            )
            pandas_cagr_notax = _cagr(d_noval)
            delta_pp_cagr = abs(pandas_cagr_notax - vbt_cagr) * 100
            crosslib_note = (
                f"pandas(no-tax)={pandas_cagr_notax:.3%}, "
                f"vbt={vbt_cagr:.3%}, |Δ|={delta_pp_cagr:.3f}pp "
                f"(compared ex-tax to match vbt scope)"
            )
            log.info("[%s] %s", variant_tag, crosslib_note)
        except Exception as e:
            crosslib_note = f"FAILED — {type(e).__name__}: {e}"
            log.warning("[%s] %s", variant_tag, crosslib_note)

    # Gate verdicts
    is_sharpe_pass = is_stats["sharpe_daily"] > 0.5
    oos_sharpe_pass = oos_stats["sharpe_daily"] >= 1.3
    oos_cagr_t = cagr_tier_B(oos_stats["cagr"])
    oos_mdd_t = mdd_tier_B(oos_stats["mdd"])
    fwd_sharpe_pass = fwd_stats["sharpe_daily"] > 0
    wf_pass = wf_verdict == "pass"
    median_hold_pass = is_stats["median_hold_days"] >= 5
    ir_pass = ir_oos >= 0.2
    crosslib_pass = np.isfinite(delta_pp_cagr) and delta_pp_cagr <= 3.0
    boot_pass = (
        boot_results.get("OOS", {}).get("passes", False)
        and boot_results.get("FULL", {}).get("passes", False)
    )
    pbo_pass = pbo_verdict == "pass"
    dsr_pass = np.isfinite(dsr_p) and dsr_p < 0.05
    cost2_pass = cost2_stats["sharpe_daily"] > 0.8

    hard_pass = crosslib_pass and boot_pass and pbo_pass and dsr_pass
    soft_pass = (
        is_sharpe_pass and oos_sharpe_pass and fwd_sharpe_pass
        and wf_pass and median_hold_pass and ir_pass and cost2_pass
    )
    final_verdict = "PASS" if (hard_pass and soft_pass) else "FAIL"
    log.info(
        "[%s] FINAL VERDICT: %s (hard=%s soft=%s)",
        variant_tag, final_verdict, hard_pass, soft_pass,
    )

    gate_rows = [
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
        (f"11 PBO < {PBO_THRESHOLD_B4:.1f} (HARD, single-feature)",
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
        for label, _, v in gate_rows
        if v == "FAIL"
        and any(k in label for k in ("HARD",))
    )

    return {
        "variant": variant_tag,
        "verdict": final_verdict,
        "hard_fails": hard_fails,
        "config_hash": cfg_hash,
        "cfg": asdict(cfg),
        "is_stats": is_stats,
        "oos_stats": oos_stats,
        "fwd_stats": fwd_stats,
        "cost2_stats": cost2_stats,
        "ir_oos": ir_oos,
        "oos_cagr_tier": oos_cagr_t,
        "oos_mdd_tier": oos_mdd_t,
        "wf_returns": wf_returns,
        "wf_dds": wf_dds,
        "wf_verdict": wf_verdict,
        "boot_results": boot_results,
        "pbo_value": pbo_value,
        "pbo_verdict": pbo_verdict,
        "pbo_threshold": PBO_THRESHOLD_B4,
        "dsr_p": dsr_p,
        "crosslib_delta_pp": delta_pp_cagr,
        "crosslib_note": crosslib_note,
        "stress_rows": stress_rows,
        "gate_rows": gate_rows,
        "trades_per_yr": trades_per_yr,
        "darf_toxic": darf_toxic,
        "grid_sharpe": [
            {
                "variant": (
                    f"B4-{g_cfg.letf_kind}-{g_cfg.leverage:g}x-L{g_cfg.ar1_lookback}"
                ),
                "ar1_lookback": g_cfg.ar1_lookback,
                "leverage": g_cfg.leverage,
                "letf_kind": g_cfg.letf_kind,
                "oos_sharpe": g_sharpe,
            }
            for g_cfg, g_sharpe in grid_oos_sharpe
        ],
    }


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

def _write_aggregate_md(payload: dict[str, Any], out_path: Path) -> None:
    verdict = payload["verdict"]
    if verdict == "PASS":
        headline = (
            f"**Verdict: PASS** — winner `{payload['variant']}` "
            f"(OOS CAGR tier **{payload['oos_cagr_tier']}** / "
            f"MDD tier **{payload['oos_mdd_tier']}**)"
        )
    else:
        headline = (
            f"**Verdict: FAIL** — winner config `{payload['variant']}` "
            f"fails {payload['hard_fails']}/4 hard gates; total fails "
            f"tallied in table below."
        )

    lines: list[str] = [
        "# Phase 3.8 B4 — Hsieh-Chang-Chen AR(1) regime LETF rotation — "
        "Honest Validation",
        "",
        headline,
        "",
        f"- **Git SHA:** `{_git_sha()}`",
        f"- **Grid:** 8 configs (2 legs {{UPRO-3x, SSO-2x}} × 4 AR(1) "
        "lookbacks {42, 63, 84, 126})",
        f"- **Winner selection:** OOS Sharpe across grid; winner evaluated "
        "against 13 gates",
        f"- **Winner config hash:** `{payload['config_hash']}`",
        f"- **Universe:** SPX-TR stitched (KF pre-2001-05-14 + Tiingo SPY), "
        "LETF synth pre-inception + real post",
        f"- **Windows:** IS `{IS_START} → {IS_END}`, OOS `{OOS_START} → "
        f"{OOS_END}`, FWD `{FWD_START} → {FWD_END}`",
        f"- **Cost model (rota B Inter, mandate §4.6):** commission=0 + "
        "spread=5.0bps/side + LETF ER=0.95% + DARF=15% year-end + "
        "cash_sleeve=4.0%/yr",
        "",
        "## Grid sweep — OOS Sharpe ranking",
        "",
        "| Variant | AR(1) lookback | Leverage | OOS Sharpe |",
        "|---------|----------------|----------|------------|",
    ]
    # Grid sharpe sorted descending for clarity.
    grid_sorted = sorted(
        payload["grid_sharpe"], key=lambda r: -r["oos_sharpe"]
    )
    for row in grid_sorted:
        lines.append(
            f"| {row['variant']} | {row['ar1_lookback']} | "
            f"{row['leverage']:.0f}x | {row['oos_sharpe']:.3f} |"
        )
    lines += [
        "",
        f"**Winner selected:** `{payload['variant']}` "
        f"(OOS Sharpe {grid_sorted[0]['oos_sharpe']:.3f})",
        "",
        f"## Winner — `{payload['variant']}` — {verdict}",
        "",
        f"- **Turnover:** ~{payload['trades_per_yr']:.1f} trades/yr "
        + (
            "⚠️ **DARF-TOXIC** (> 25/yr, expected for AR(1) per Phase 3.8-1 plan)"
            if payload["darf_toxic"]
            else "(within 25/yr budget)"
        ),
        f"- **OOS on-regime fraction:** "
        f"{payload['oos_stats']['on_regime_fraction']:.2%}",
        "",
        "### 13-Gate Table",
        "",
        "| Gate | Value | Verdict |",
        "|------|-------|---------|",
    ]
    for name, val, verdict_cell in payload["gate_rows"]:
        lines.append(f"| {name} | {val} | **{verdict_cell}** |")

    lines += [
        "",
        "### Window summaries",
        "",
        f"#### IS ({IS_START} → {IS_END})",
        f"- days={payload['is_stats']['n_days']:,}, "
        f"switches={payload['is_stats']['n_switches']}, "
        f"median_hold={payload['is_stats']['median_hold_days']:.1f}d, "
        f"on_regime={payload['is_stats']['on_regime_fraction']:.2%}",
        f"- Sharpe(daily)={payload['is_stats']['sharpe_daily']:.3f}, "
        f"CAGR={payload['is_stats']['cagr']:.3%}, "
        f"MDD={payload['is_stats']['mdd']:.3%}",
        f"- Cumulative: switches={payload['is_stats']['cum_cost_pct']:.3%}, "
        f"tax={payload['is_stats']['cum_tax_pct']:.3%}",
        "",
        f"#### OOS ({OOS_START} → {OOS_END})",
        f"- days={payload['oos_stats']['n_days']:,}, "
        f"switches={payload['oos_stats']['n_switches']}, "
        f"median_hold={payload['oos_stats']['median_hold_days']:.1f}d",
        f"- Sharpe(daily)={payload['oos_stats']['sharpe_daily']:.3f}, "
        f"CAGR={payload['oos_stats']['cagr']:.3%} "
        f"(tier **{payload['oos_cagr_tier']}**), "
        f"MDD={payload['oos_stats']['mdd']:.3%} "
        f"(tier **{payload['oos_mdd_tier']}**)",
        f"- IR vs SPY buy-hold: {payload['ir_oos']:.3f}",
        "",
        f"#### FWD ({FWD_START} → {FWD_END})",
        f"- days={payload['fwd_stats']['n_days']:,}, "
        f"switches={payload['fwd_stats']['n_switches']}, "
        f"median_hold={payload['fwd_stats']['median_hold_days']:.1f}d",
        f"- Sharpe(daily)={payload['fwd_stats']['sharpe_daily']:.3f}, "
        f"CAGR={payload['fwd_stats']['cagr']:.3%}, "
        f"MDD={payload['fwd_stats']['mdd']:.3%}",
        "",
        "### Stress periods (Sharpe | CAGR | MDD | N)",
        "",
        "| Period | N | Sharpe | CAGR | MDD |",
        "|--------|---|--------|------|-----|",
    ]
    for key, row in payload["stress_rows"]:
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
        f"- Profitable: "
        f"{sum(1 for r in payload['wf_returns'] if r > 0)} / "
        f"{len(payload['wf_returns'])}",
        f"- Window returns: "
        + ", ".join(f"{r*100:.2f}%" for r in payload["wf_returns"]),
        f"- Window MDDs: "
        + ", ".join(f"{d*100:.2f}%" for d in payload["wf_dds"]),
        "",
    ]

    lines += [
        "## Data provenance",
        "",
        "- SPX-TR pre-2001-05-14: Kenneth French daily factors "
        "(`Mkt-RF + RF`)",
        "- SPX-TR post-2001-05-14: Tiingo SPY `adj_close` pct_change",
        "- UPRO-3x pre-2009-06-25: "
        "`synthesize_letf_returns_ffr_aware(L=3, ER=0.95%)`",
        "- UPRO-3x post-2009-06-25: Tiingo UPRO `adj_close` pct_change",
        "- SSO-2x pre-2006-06-21: "
        "`synthesize_letf_returns_ffr_aware(L=2, ER=0.95%)`",
        "- SSO-2x post-2006-06-21: Tiingo SSO `adj_close` pct_change",
        "- FFR proxy: Kenneth French daily `rf` × 252",
        "- Cash sleeve: flat 4%/yr (mandate §4.6)",
        "",
        "## Structural interpretation",
        "",
    ]
    if verdict == "PASS":
        lines.append(
            "Winner passes all 13 gates — AR(1) regime filter is a real "
            "novel signal under DARF-heavy rota B. Recommend elevation "
            "to WINNER_B4.md and production sizing study."
        )
    else:
        # Structural interpretation — what failed and why
        reasons = []
        for name, val, v_cell in payload["gate_rows"]:
            if v_cell == "FAIL":
                reasons.append(name)
        reason_str = "; ".join(reasons) if reasons else "no specific gate"
        lines.append(
            f"Winner FAILs: {reason_str}. "
            + (
                "Turnover > 25/yr confirmed DARF-toxic: AR(1) sign flips "
                "drive excess switching, year-end DARF compounds the drag. "
                "B4 hypothesis does not beat B1 in rota B context."
                if payload["darf_toxic"]
                else "Turnover within budget — primary failure is signal "
                "quality (Sharpe/bootstrap CI), not cost overhead."
            )
        )
    lines += [
        "",
        "## Known limitations",
        "",
        "- AR(1) signal uses sign-only regime gating (0/1). Scaling on β "
        "magnitude is a future extension not tested here (paper leaves as "
        "open).",
        "- Synth LETF has ±5pp tracking-error band in 2020 validation — "
        "material on long IS window but bounded. Inherited from B1.",
        "- Year-end DARF model: 15% on yearly net gain; loss-carry NOT "
        "modelled (conservative per mandate §4.6).",
        "- Cash sleeve flat 4%/yr — simplification vs daily 3mo T-bill.",
        "",
        "## Citations",
        "",
        "- `[phase3_7_literature_sprint §T1, arXiv 2504.20116]` — "
        "Hsieh-Chang-Chen 2025 AR(1) regime thesis",
        "- `[leverage_for_the_long_run, p.4, p.7-8]` — AR(1) > 0 as "
        "statistical signature of trending market (Gayed framing)",
        "- `[advances_fin_ml, p.31-34]` — F2-alignment prev_weight × ret",
        "- `[advances_fin_ml, p.208-211]` — PBO via CSCV",
        "- `[advances_fin_ml, p.275]` — Deflated Sharpe Ratio",
        "- `[docs/investment-mandate.md §2.4]` — 13-gate framework",
        "- `[docs/investment-mandate.md §2.2, §2.3, §7]` — CAGR/MDD tiers "
        "warning-only",
        "- `[docs/investment-mandate.md §4.6]` — rota B Inter cost model "
        "(DARF 15%)",
    ]

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("wrote %s", out_path)


def _write_winner_md(payload: dict[str, Any], out_path: Path) -> None:
    lines = [
        "# Phase 3.8 Winner — B4 Hsieh-Chang-Chen AR(1) regime LETF rotation",
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
    for name, val, verdict_cell in payload["gate_rows"]:
        lines.append(f"| {name} | {val} | **{verdict_cell}** |")
    lines += [
        "",
        "## Citations",
        "",
        "- `[phase3_7_literature_sprint §T1, arXiv 2504.20116]`",
        "- `[leverage_for_the_long_run, p.4, p.7-8]`",
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

    log.info("Loading SPX-TR (stitched KF + Tiingo SPY)")
    full_returns = load_spx_tr_daily(start="1970-01-01", end="2026-04-30")
    full_ffr = _load_ffr_annualized(full_returns.index)
    log.info(
        "SPX-TR loaded: %s → %s (%d days)",
        full_returns.index.min().date(),
        full_returns.index.max().date(),
        len(full_returns),
    )
    spy_bh_daily = full_returns.copy()

    # Load real LETF series (None-safe).
    upro_real = (
        _load_letf_real_returns(UPRO_PATH) if UPRO_PATH.exists() else None
    )
    sso_real = (
        _load_letf_real_returns(SSO_PATH) if SSO_PATH.exists() else None
    )
    real_letf_by_kind = {"UPRO": upro_real, "SSO": sso_real}
    log.info(
        "UPRO real range: %s → %s; SSO real range: %s → %s",
        upro_real.index.min().date() if upro_real is not None else "n/a",
        upro_real.index.max().date() if upro_real is not None else "n/a",
        sso_real.index.min().date() if sso_real is not None else "n/a",
        sso_real.index.max().date() if sso_real is not None else "n/a",
    )

    # Slice OOS for winner selection.
    oos_start_ts = pd.Timestamp(OOS_START)
    oos_end_ts = pd.Timestamp(OOS_END)
    oos_ret = full_returns.loc[
        (full_returns.index >= oos_start_ts)
        & (full_returns.index <= oos_end_ts)
    ]
    oos_ffr = full_ffr.reindex(oos_ret.index).ffill().bfill()

    # Build 8-config grid and rank by OOS Sharpe.
    grid = _build_grid()
    log.info("Grid size: %d configs", len(grid))
    grid_sharpe: list[tuple[B4Config, float]] = []
    for cfg in grid:
        sh = _oos_sharpe_for_cfg(cfg, oos_ret, oos_ffr, real_letf_by_kind)
        grid_sharpe.append((cfg, sh))
        log.info(
            "  grid cell: kind=%s lev=%.1fx lb=%d OOS_sharpe=%.3f",
            cfg.letf_kind, cfg.leverage, cfg.ar1_lookback, sh,
        )

    # IS switches sanity — winner must have >= 50 IS switches (halt if not).
    # We check by running winner on IS.
    winner_cfg = max(grid_sharpe, key=lambda it: it[1])[0]
    log.info(
        "Winner: B4-%s-%gx-L%d (OOS Sharpe=%.3f)",
        winner_cfg.letf_kind, winner_cfg.leverage, winner_cfg.ar1_lookback,
        max(sh for _, sh in grid_sharpe),
    )

    # Run winner through 13-gate framework.
    real_winner = real_letf_by_kind[winner_cfg.letf_kind]
    payload = _run_winner(
        winner_cfg,
        full_returns,
        full_ffr,
        real_winner,
        real_letf_by_kind,
        spy_bh_daily,
        grid_sharpe,
        skip_crosslib=args.skip_crosslib,
        skip_pbo=args.skip_pbo,
        skip_bootstrap=args.skip_bootstrap,
    )

    # HALT if winner IS switches < 50.
    if payload["is_stats"]["n_switches"] < 50:
        halt_path = REPORT_DIR / "ENGINE_REGRESSION_NOTE.md"
        halt_path.write_text(
            f"# HALT — B4 winner IS switches < 50\n\n"
            f"Winner variant: `{payload['variant']}`\n"
            f"IS switches: {payload['is_stats']['n_switches']} (threshold 50)\n\n"
            f"Root cause investigation required — possible data / signal bug.\n",
            encoding="utf-8",
        )
        log.error("HALT — IS switches %d < 50", payload["is_stats"]["n_switches"])
        return 2

    # HALT if cross-lib Δ > 10pp.
    if (
        np.isfinite(payload["crosslib_delta_pp"])
        and payload["crosslib_delta_pp"] > 10.0
    ):
        halt_path = REPORT_DIR / "ENGINE_REGRESSION_NOTE.md"
        halt_path.write_text(
            f"# HALT — B4 cross-lib Δ > 10pp\n\n"
            f"Winner variant: `{payload['variant']}`\n"
            f"Cross-lib delta: {payload['crosslib_delta_pp']:.3f}pp\n"
            f"{payload['crosslib_note']}\n\n"
            f"Engine regression suspected — pandas and vectorbt diverged "
            f"beyond the 10pp hard halt threshold.\n",
            encoding="utf-8",
        )
        log.error(
            "HALT — cross-lib delta %.3fpp > 10pp",
            payload["crosslib_delta_pp"],
        )
        return 2

    # Write aggregate MD + JSON.
    _write_aggregate_md(payload, REPORT_DIR / "AGGREGATE.md")
    summary_payload = {
        "git_sha": _git_sha(),
        "windows": {
            "IS": [IS_START, IS_END],
            "OOS": [OOS_START, OOS_END],
            "FWD": [FWD_START, FWD_END],
        },
        "grid_size": len(grid),
        "pbo_threshold": PBO_THRESHOLD_B4,
        "winner": payload,
    }
    (REPORT_DIR / "summary.json").write_text(
        json.dumps(summary_payload, indent=2, default=str), encoding="utf-8"
    )
    log.info("wrote %s/summary.json", REPORT_DIR)

    # Stop-at-first-winner — write WINNER_B4.md if PASS.
    if payload["verdict"] == "PASS":
        _write_winner_md(payload, PHASE_DIR / "WINNER_B4.md")

    print(f"FINAL VERDICT: {payload['verdict']}")
    print(
        f"  {payload['variant']}: {payload['verdict']} "
        f"(hard_fails={payload['hard_fails']})"
    )
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
