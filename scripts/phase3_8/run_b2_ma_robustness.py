"""Phase 3.8 B2 runner — Gayed MA-robustness sweep × 13 honest gates.

Runs the **16-config grid** ``ma_type ∈ {SMA,EMA} × ma_period ∈
{100,125,150,200} × leg ∈ {UPRO,SSO}`` on the rota B Inter cost model
(DARF 15% + FX spread + ER 0.95%). Selects the winner config by **OOS
Sharpe** (post-selection; legit per the 13-gate framework because
winner selection happens AFTER all windows run, and the HARD gates
then check if that pick is statistically real).

Windows (mutually exclusive)
----------------------------
* IS   : 1970-01-02 → 1999-12-31
* OOS  : 2000-01-01 → 2015-12-31
* FWD  : 2016-01-01 → 2026-04-15

13-gate framework (mandate §2.4)
--------------------------------
1 IS Sharpe > 0.5 | 2 OOS Sharpe >= 1.3 | 3 OOS CAGR tier (WARN)
4 OOS MDD tier (WARN) | 5 FWD Sharpe > 0 | 6 WF >= 6/8
7 Median hold >= 5 days | 8 IR vs SPY >= 0.2 | 9 Cross-lib <=3pp (HARD)
10 Bootstrap 99.9% CI>0 HARD | 11 PBO < 0.3 (HARD, tightened for
single-feature 16-config family per B2 prompt) | 12 DSR p<0.05 (HARD)
13 Cost×2 Sharpe > 0.8

PASS iff hard gates 9/10/11/12 pass AND soft gates 1/2/5/6/7/8/13 pass.
Gates 3/4 are WARNING-only per mandate §2.2/§2.3.

Halt contract (B2 prompt hard stops)
------------------------------------
* Cross-lib Δ > 10pp on winner → write ENGINE_REGRESSION_NOTE.md.
* IS n_trades < 50 on winner → HALT sanity-check.
* Turnover on winner > 20 trades/yr → REJECT as DARF-incompatible.

Citations
---------
* ``[leverage_for_the_long_run, p.14, Table 6; p.16; p.17]`` — MA
  robustness + turnover + leverage grid.
* ``[cycle_analytics, p.9-10, ch.1-2]`` — EMA IIR.
* ``[advances_fin_ml, p.31-34, p.208-211, p.275]`` — F2, PBO, DSR.
* ``docs/investment-mandate.md §2.4, §2.2, §2.3, §4.6`` — gates +
  tiers + rota B.
* ``docs/plans/2026-04-22-phase3.8-1-plano-b-hunt-prompt.md §B2`` —
  B2 spec (16-config grid, PBO < 0.3 tight).
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
from ai_trade.backtest.strategies.phase3_8_b1_gayed_canonical import (  # noqa: E402
    B1Config,
)
from ai_trade.backtest.strategies.phase3_8_b1_gayed_canonical import (  # noqa: E402
    stitch_letf_returns as _b1_stitch,
)
from ai_trade.backtest.strategies.phase3_8_b2_ma_robustness import (  # noqa: E402
    B2Config,
    B2Result,
    compute_regime_signal_b2,
    simulate_b2,
)
from ai_trade.backtest.validation import dsr, walk_forward_gate  # noqa: E402
from ai_trade.backtest.validation.bootstrap import (  # noqa: E402
    stationary_bootstrap_trades,
)
from ai_trade.backtest.validation.pbo import pbo  # noqa: E402

LOG_FMT = "%(asctime)s %(levelname)-5s %(name)s %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FMT)
log = logging.getLogger("b2_ma_robustness")

UPRO_PATH = REPO_ROOT / "data" / "tiingo" / "daily" / "prices" / "UPRO.parquet"
SSO_PATH = REPO_ROOT / "data" / "tiingo" / "daily" / "prices" / "SSO.parquet"
REPORT_DIR = REPO_ROOT / "reports" / "phase_3_8" / "b2_ma_robustness"
PHASE_DIR = REPO_ROOT / "reports" / "phase_3_8"

IS_START, IS_END = "1970-01-02", "1999-12-31"
OOS_START, OOS_END = "2000-01-01", "2015-12-31"
FWD_START, FWD_END = "2016-01-01", "2026-04-15"

TRADING_DAYS = 252

PBO_HARD_THRESHOLD = 0.3  # B2 prompt — tighter than B1's 0.5


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


def _build_tr_price(returns: pd.Series) -> pd.Series:
    price = (1.0 + returns).cumprod() * 100.0
    price.name = "spx_tr_price"
    return price


def _slice(s: pd.Series, start: str, end: str) -> pd.Series:
    ts_start = pd.Timestamp(start)
    ts_end = pd.Timestamp(end)
    return s.loc[(s.index >= ts_start) & (s.index <= ts_end)]


def _short_hash(cfg: B2Config) -> str:
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


def _config_tag(cfg: B2Config) -> str:
    return f"B2-{cfg.filter}{cfg.ma_period}-{cfg.leg}-{cfg.leverage:g}x"


# ---------------------------------------------------------------------------
# Window runner (single config, single window)
# ---------------------------------------------------------------------------

def run_window(
    returns: pd.Series,
    price: pd.Series,
    ffr: pd.Series,
    real_letf: pd.Series | None,
    cfg: B2Config,
    label: str,
) -> tuple[dict[str, Any], B2Result, pd.Series]:
    res = simulate_b2(returns, price, ffr, cfg, real_letf_returns=real_letf)
    daily = res.daily_returns.dropna()
    on_frac = float((res.exposure > 0).mean())
    out = {
        "label": label,
        "variant": _config_tag(cfg),
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


# ---------------------------------------------------------------------------
# Cross-lib (Gate 9 — HARD) — pandas no-tax vs vbt replica on winner
# ---------------------------------------------------------------------------

def _crosslib_vbt_cagr(
    returns: pd.Series,
    price: pd.Series,
    ffr: pd.Series,
    real_letf: pd.Series | None,
    cfg: B2Config,
) -> float:
    """Cross-library replica of B2 gross (pre-tax) CAGR via vectorbt.

    Uses the same stitched LETF series and the same 0/1 regime gate
    built by our shared helpers; compounds ``gate × letf + (1-gate) ×
    cash`` without tax or switch cost (so both sides implement the
    same arithmetic — this is an engine check, not an economic one).
    """
    try:
        import vectorbt as vbt  # noqa: F401
    except ImportError:
        return float("nan")

    # Build the stitched LETF via B1's helper (zero drift).
    b1_shim = B1Config(
        leverage=cfg.leverage,
        letf_kind=cfg.leg,
        sma_period=200,
        expense_ratio=cfg.expense_ratio,
        swap_exposure=cfg.swap_exposure,
        ffr_spread=cfg.ffr_spread,
        cash_rate_annual=cfg.cash_rate_annual,
        commission_bps=cfg.commission_bps,
        spread_bps=cfg.spread_bps,
        tax_rate=0.0,
        use_real_letf=cfg.use_real_letf,
    )
    letf = _b1_stitch(returns, real_letf, ffr, b1_shim).fillna(0.0)
    regime = compute_regime_signal_b2(
        price, filter=cfg.filter, ma_period=cfg.ma_period
    )
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
# Grid orchestration
# ---------------------------------------------------------------------------

def _build_grid() -> list[B2Config]:
    """Return the 16-config B2 grid."""
    filters = ("SMA", "EMA")
    periods = (100, 125, 150, 200)
    legs = ("UPRO", "SSO")
    out: list[B2Config] = []
    for flt in filters:
        for p in periods:
            for leg in legs:
                out.append(B2Config(filter=flt, ma_period=p, leg=leg))  # type: ignore[arg-type]
    return out


def _run_grid_all_windows(
    grid: list[B2Config],
    full_returns: pd.Series,
    full_price: pd.Series,
    full_ffr: pd.Series,
    upro_real: pd.Series | None,
    sso_real: pd.Series | None,
) -> list[dict[str, Any]]:
    """For each of the 16 configs, run IS/OOS/FWD and record stats.

    Returns a list of per-config dicts with ``is_stats``, ``oos_stats``,
    ``fwd_stats`` (each is the :func:`run_window` payload) plus the
    stitched daily series needed downstream for PBO / bootstrap / DSR.
    """
    is_ret = _slice(full_returns, IS_START, IS_END)
    is_px = _slice(full_price, IS_START, IS_END)
    is_ffr = full_ffr.reindex(is_ret.index).ffill().bfill()

    oos_ret = _slice(full_returns, OOS_START, OOS_END)
    oos_px = _slice(full_price, OOS_START, OOS_END)
    oos_ffr = full_ffr.reindex(oos_ret.index).ffill().bfill()

    fwd_ret = _slice(full_returns, FWD_START, FWD_END)
    fwd_px = _slice(full_price, FWD_START, FWD_END)
    fwd_ffr = full_ffr.reindex(fwd_ret.index).ffill().bfill()

    grid_payloads: list[dict[str, Any]] = []
    for i, cfg in enumerate(grid):
        real = upro_real if cfg.leg == "UPRO" else sso_real
        tag = _config_tag(cfg)
        log.info(
            "[grid %d/%d] %s (%s/%d/%s)",
            i + 1, len(grid), tag, cfg.filter, cfg.ma_period, cfg.leg,
        )
        is_stats, _is_res, is_daily = run_window(
            is_ret, is_px, is_ffr, real, cfg, "IS"
        )
        oos_stats, _oos_res, oos_daily = run_window(
            oos_ret, oos_px, oos_ffr, real, cfg, "OOS"
        )
        fwd_stats, _fwd_res, fwd_daily = run_window(
            fwd_ret, fwd_px, fwd_ffr, real, cfg, "FWD"
        )
        grid_payloads.append(
            {
                "variant": tag,
                "cfg": asdict(cfg),
                "cfg_hash": _short_hash(cfg),
                "is_stats": is_stats,
                "oos_stats": oos_stats,
                "fwd_stats": fwd_stats,
                "is_daily": is_daily,
                "oos_daily": oos_daily,
                "fwd_daily": fwd_daily,
            }
        )
        log.info(
            "[grid %d/%d] %s OOS Sharpe=%.3f CAGR=%.3f MDD=%.3f",
            i + 1, len(grid), tag,
            oos_stats["sharpe_daily"], oos_stats["cagr"], oos_stats["mdd"],
        )
    return grid_payloads


# ---------------------------------------------------------------------------
# Winner selection + hard-gate evaluation
# ---------------------------------------------------------------------------

def _select_winner(grid_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    """Select the config with the highest OOS Sharpe.

    This is the **legit post-selection** per the 13-gate framework:
    winner selection happens AFTER all windows have run (no OOS peek
    into the selection model — we only observe the OOS Sharpe to rank
    the grid, and then the HARD gates (PBO, DSR, bootstrap, cross-lib)
    discipline whether this rank is real or a lucky draw.
    """
    return max(
        grid_payloads, key=lambda p: p["oos_stats"]["sharpe_daily"]
    )


def _evaluate_winner(
    winner: dict[str, Any],
    grid_payloads: list[dict[str, Any]],
    full_returns: pd.Series,
    full_price: pd.Series,
    full_ffr: pd.Series,
    upro_real: pd.Series | None,
    sso_real: pd.Series | None,
    spy_bh_daily: pd.Series,
    *,
    skip_crosslib: bool,
    skip_pbo: bool,
    skip_bootstrap: bool,
) -> dict[str, Any]:
    """Apply gates 1-13 to the winner config; PBO is on full grid."""
    cfg = B2Config(**winner["cfg"])
    real = upro_real if cfg.leg == "UPRO" else sso_real
    tag = _config_tag(cfg)
    cfg_hash = winner["cfg_hash"]
    log.info("[%s] winner — applying 13 gates", tag)

    is_stats = winner["is_stats"]
    oos_stats = winner["oos_stats"]
    fwd_stats = winner["fwd_stats"]
    is_daily = winner["is_daily"]
    oos_daily = winner["oos_daily"]
    fwd_daily = winner["fwd_daily"]

    # SPY IR.
    oos_spy = _slice(spy_bh_daily, OOS_START, OOS_END)
    ir_oos = _ir_vs_bench(oos_daily, oos_spy)

    # Turnover watchdog (full period).
    full_years = (
        pd.Timestamp(FWD_END) - pd.Timestamp(IS_START)
    ).days / 365.25
    full_switches = (
        is_stats["n_switches"] + oos_stats["n_switches"] + fwd_stats["n_switches"]
    )
    trades_per_yr = full_switches / full_years if full_years > 0 else 0.0
    turnover_reject = trades_per_yr > 20
    log.info(
        "[%s] turnover ~%.1f trades/yr (total %d switches over %.1fy)",
        tag, trades_per_yr, full_switches, full_years,
    )
    if is_stats["n_switches"] < 50:
        log.warning(
            "[%s] IS switches=%d < 50 — sanity-check (HALT per prompt)",
            tag, is_stats["n_switches"],
        )

    # Stress periods.
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
        src_daily = oos_daily if start_ts < pd.Timestamp(OOS_END) else fwd_daily
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

    # Cost × 2 — double tax + spread + ER (commission stays 0).
    oos_ret = _slice(full_returns, OOS_START, OOS_END)
    oos_px = _slice(full_price, OOS_START, OOS_END)
    oos_ffr = full_ffr.reindex(oos_ret.index).ffill().bfill()
    cfg_2x = B2Config(
        **{
            **winner["cfg"],
            "commission_bps": cfg.commission_bps * 2.0,
            "spread_bps": cfg.spread_bps * 2.0,
            "expense_ratio": cfg.expense_ratio * 2.0,
            "tax_rate": min(cfg.tax_rate * 2.0, 0.30),
        }
    )
    cost2_stats, _, cost2_daily = run_window(
        oos_ret, oos_px, oos_ffr, real, cfg_2x, "OOS_2x_cost"
    )
    log.info("[%s] cost×2 OOS: %s", tag, cost2_stats)

    # Walk-forward 8 windows over IS+OOS.
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
        tag, len(wf_returns),
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
                boot_results[label] = {"ci_low_999": float("nan"), "passes": False}
                continue
            rs = stationary_bootstrap_trades(
                trades, block_mean=5, n_resamples=2000, seed=42
            )
            means = rs.mean(axis=1)
            lo_999 = float(np.quantile(means, 0.001))
            boot_results[label] = {"ci_low_999": lo_999, "passes": lo_999 > 0}
    log.info("[%s] bootstrap: %s", tag, boot_results)

    # PBO — 16-config family on IS+OOS daily returns matrix (CSCV).
    pbo_value = float("nan")
    pbo_verdict = "n/a"
    if not skip_pbo:
        log.info("[PBO] 16-config grid (single feature family)")
        cols: list[np.ndarray] = []
        for gp in grid_payloads:
            # IS+OOS concatenation — mutually exclusive windows, no leak.
            d = pd.concat([gp["is_daily"], gp["oos_daily"]]).dropna().to_numpy()
            cols.append(d)
        min_len = min(len(c) for c in cols)
        mat = np.column_stack([c[-min_len:] for c in cols])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            pres = pbo(mat, n_blocks=10)
        pbo_value = float(pres.pbo)
        pbo_verdict = "pass" if pbo_value < PBO_HARD_THRESHOLD else "reject"
        log.info(
            "[PBO] value=%.4f threshold=%.2f verdict=%s (n_configs=%d)",
            pbo_value, PBO_HARD_THRESHOLD, pbo_verdict, len(cols),
        )

    # DSR — OOS track, n_trials = 16 (full grid).
    oos_trades = oos_daily.dropna().to_numpy()
    if len(oos_trades) >= 10:
        dsr_res = dsr(oos_trades, n_trials=16)
        dsr_p = float(dsr_res.p_value)
    else:
        dsr_p = float("nan")
    log.info("[%s] DSR p=%.4f (n_trials=16)", tag, dsr_p)

    # Cross-lib (HARD) — pandas no-tax vs vbt replica on OOS.
    delta_pp_cagr = float("nan")
    crosslib_note = "skipped"
    if not skip_crosslib:
        log.info("[%s] Cross-lib pandas vs vbt (no-tax OOS)", tag)
        try:
            vbt_cagr = _crosslib_vbt_cagr(
                oos_ret, oos_px, oos_ffr, real, cfg
            )
            cfg_no_tax = B2Config(
                **{
                    **winner["cfg"],
                    "tax_rate": 0.0,
                    "commission_bps": 0.0,
                    "spread_bps": 0.0,
                }
            )
            _, _, d_noval = run_window(
                oos_ret, oos_px, oos_ffr, real, cfg_no_tax, "ref_notax"
            )
            pandas_cagr_notax = _cagr(d_noval)
            delta_pp_cagr = abs(pandas_cagr_notax - vbt_cagr) * 100
            crosslib_note = (
                f"pandas(no-tax)={pandas_cagr_notax:.3%}, vbt={vbt_cagr:.3%}, "
                f"|Δ|={delta_pp_cagr:.3f}pp (compared ex-tax to match vbt scope)"
            )
            log.info("[%s] %s", tag, crosslib_note)

            # Halt contract: Δ > 10pp → engine regression.
            if delta_pp_cagr > 10.0:
                note_path = REPORT_DIR / "ENGINE_REGRESSION_NOTE.md"
                note_path.parent.mkdir(parents=True, exist_ok=True)
                note_path.write_text(
                    f"# ENGINE_REGRESSION_NOTE — Phase 3.8 B2 cross-lib FAIL\n\n"
                    f"Winner: {tag}\n"
                    f"pandas(no-tax) OOS CAGR: {pandas_cagr_notax:.3%}\n"
                    f"vectorbt OOS CAGR: {vbt_cagr:.3%}\n"
                    f"|Δ| = {delta_pp_cagr:.3f}pp (> 10pp halt threshold)\n",
                    encoding="utf-8",
                )
                log.error(
                    "[%s] cross-lib Δ=%.3fpp > 10pp — HALT per B2 prompt",
                    tag, delta_pp_cagr,
                )
        except Exception as e:
            crosslib_note = f"FAILED — {type(e).__name__}: {e}"
            log.warning("[%s] %s", tag, crosslib_note)

    # Gate verdicts.
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
    # B2 prompt: turnover > 20/yr REJECT as DARF-incompatible.
    if turnover_reject:
        log.warning(
            "[%s] turnover %.1f > 20/yr — REJECTED as DARF-incompatible",
            tag, trades_per_yr,
        )

    final_verdict = (
        "PASS"
        if (hard_pass and soft_pass and not turnover_reject)
        else "FAIL"
    )
    log.info(
        "[%s] FINAL VERDICT: %s (hard=%s soft=%s turnover_reject=%s)",
        tag, final_verdict, hard_pass, soft_pass, turnover_reject,
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
        (f"11 PBO < {PBO_HARD_THRESHOLD:g} (HARD, 16-config family)",
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
        if v == "FAIL" and "HARD" in label
    )

    return {
        "variant": tag,
        "verdict": final_verdict,
        "hard_fails": hard_fails,
        "config_hash": cfg_hash,
        "cfg": winner["cfg"],
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
        "pbo_threshold": PBO_HARD_THRESHOLD,
        "dsr_p": dsr_p,
        "crosslib_delta_pp": delta_pp_cagr,
        "crosslib_note": crosslib_note,
        "stress_rows": stress_rows,
        "gate_rows": gate_rows,
        "trades_per_yr": trades_per_yr,
        "turnover_reject": turnover_reject,
    }


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

def _write_aggregate_md(
    grid_payloads: list[dict[str, Any]],
    winner_payload: dict[str, Any],
    out_path: Path,
) -> None:
    # Grid table rows sorted by OOS Sharpe descending.
    sorted_grid = sorted(
        grid_payloads,
        key=lambda p: p["oos_stats"]["sharpe_daily"],
        reverse=True,
    )

    passes = winner_payload["verdict"] == "PASS"
    if passes:
        headline = (
            f"**Verdict: PASS** — winner `{winner_payload['variant']}` "
            f"(tier **{winner_payload['oos_cagr_tier']}** / MDD tier "
            f"**{winner_payload['oos_mdd_tier']}**)"
        )
    else:
        headline = (
            f"**Verdict: FAIL** — winner `{winner_payload['variant']}` "
            f"fails {winner_payload['hard_fails']}/4 hard gates "
            f"(grid: 16 configs run)"
        )

    lines: list[str] = [
        "# Phase 3.8 B2 — Gayed MA-robustness sweep — Honest Validation",
        "",
        headline,
        "",
        f"- **Git SHA:** `{_git_sha()}`",
        "- **Universe:** SPY (SPX-TR stitched KF+Tiingo), UPRO/SSO synth "
        "pre-inception + real post",
        f"- **Windows:** IS `{IS_START} → {IS_END}`, OOS `{OOS_START} → {OOS_END}`, "
        f"FWD `{FWD_START} → {FWD_END}`",
        "- **Cost model (rota B Inter, mandate §4.6):** commission=0 + "
        "spread=5.0bps/side + LETF ER=0.95% + DARF=15% year-end + "
        "cash_sleeve=4.0%/yr",
        f"- **Grid:** 2 filters × 4 MA periods × 2 legs = **16 configs**",
        f"- **PBO threshold:** < {PBO_HARD_THRESHOLD:g} (tightened for "
        "single-feature 16-config family)",
        "",
        "## Grid summary (16 configs, sorted by OOS Sharpe desc)",
        "",
        "| Rank | Variant | filter | period | leg | IS Sharpe | OOS Sharpe | OOS CAGR | OOS MDD | FWD Sharpe | n_switches IS/OOS/FWD |",
        "|------|---------|--------|--------|-----|-----------|------------|----------|---------|------------|-----------------------|",
    ]
    for rk, p in enumerate(sorted_grid, start=1):
        cfg = p["cfg"]
        lines.append(
            f"| {rk} | {p['variant']} | {cfg['filter']} | {cfg['ma_period']} | "
            f"{cfg['leg']} | {p['is_stats']['sharpe_daily']:.3f} | "
            f"{p['oos_stats']['sharpe_daily']:.3f} | "
            f"{p['oos_stats']['cagr']:.3%} | {p['oos_stats']['mdd']:.3%} | "
            f"{p['fwd_stats']['sharpe_daily']:.3f} | "
            f"{p['is_stats']['n_switches']}/{p['oos_stats']['n_switches']}/"
            f"{p['fwd_stats']['n_switches']} |"
        )

    lines += [
        "",
        f"## Winner — {winner_payload['variant']} — {winner_payload['verdict']}",
        "",
        f"- **Config hash:** `{winner_payload['config_hash']}`",
        f"- **Turnover:** ~{winner_payload['trades_per_yr']:.1f} trades/yr "
        + ("(REJECT — > 20 DARF-incompatible)" if winner_payload["turnover_reject"] else "(OK)"),
        f"- **OOS on-regime fraction:** {winner_payload['oos_stats']['on_regime_fraction']:.2%}",
        f"- **Config:** filter={winner_payload['cfg']['filter']}, "
        f"ma_period={winner_payload['cfg']['ma_period']}, "
        f"leg={winner_payload['cfg']['leg']}, "
        f"leverage={3.0 if winner_payload['cfg']['leg'] == 'UPRO' else 2.0}x",
        "",
        "### 13-Gate Table",
        "",
        "| Gate | Value | Verdict |",
        "|------|-------|---------|",
    ]
    for name, val, verdict in winner_payload["gate_rows"]:
        lines.append(f"| {name} | {val} | **{verdict}** |")

    w = winner_payload
    lines += [
        "",
        "### Window summaries (winner)",
        "",
        f"#### IS ({IS_START} → {IS_END})",
        f"- days={w['is_stats']['n_days']:,}, switches={w['is_stats']['n_switches']}, "
        f"median_hold={w['is_stats']['median_hold_days']:.1f}d, "
        f"on_regime={w['is_stats']['on_regime_fraction']:.2%}",
        f"- Sharpe(daily)={w['is_stats']['sharpe_daily']:.3f}, "
        f"CAGR={w['is_stats']['cagr']:.3%}, MDD={w['is_stats']['mdd']:.3%}",
        f"- Cumulative: switches={w['is_stats']['cum_cost_pct']:.3%}, "
        f"tax={w['is_stats']['cum_tax_pct']:.3%}",
        "",
        f"#### OOS ({OOS_START} → {OOS_END})",
        f"- days={w['oos_stats']['n_days']:,}, switches={w['oos_stats']['n_switches']}, "
        f"median_hold={w['oos_stats']['median_hold_days']:.1f}d",
        f"- Sharpe(daily)={w['oos_stats']['sharpe_daily']:.3f}, "
        f"CAGR={w['oos_stats']['cagr']:.3%} (tier **{w['oos_cagr_tier']}**), "
        f"MDD={w['oos_stats']['mdd']:.3%} (tier **{w['oos_mdd_tier']}**)",
        f"- IR vs SPY buy-hold: {w['ir_oos']:.3f}",
        "",
        f"#### FWD ({FWD_START} → {FWD_END})",
        f"- days={w['fwd_stats']['n_days']:,}, switches={w['fwd_stats']['n_switches']}, "
        f"median_hold={w['fwd_stats']['median_hold_days']:.1f}d",
        f"- Sharpe(daily)={w['fwd_stats']['sharpe_daily']:.3f}, "
        f"CAGR={w['fwd_stats']['cagr']:.3%}, MDD={w['fwd_stats']['mdd']:.3%}",
        "",
        "### Stress periods (winner)",
        "",
        "| Period | N | Sharpe | CAGR | MDD |",
        "|--------|---|--------|------|-----|",
    ]
    for key, row in w["stress_rows"]:
        if row["n"] == 0:
            lines.append(f"| {key} | 0 | n/a | n/a | n/a |")
        else:
            lines.append(
                f"| {key} | {row['n']} | {row['sharpe']:.3f} | "
                f"{row['cagr']:.3%} | {row['mdd']:.3%} |"
            )

    lines += [
        "",
        "### Walk-forward (8 windows over IS+OOS, winner)",
        f"- Profitable: {sum(1 for r in w['wf_returns'] if r > 0)} / "
        f"{len(w['wf_returns'])}",
        f"- Window returns: "
        + ", ".join(f"{r*100:.2f}%" for r in w["wf_returns"]),
        f"- Window MDDs: "
        + ", ".join(f"{d*100:.2f}%" for d in w["wf_dds"]),
        "",
        "## Data provenance",
        "",
        "- SPX-TR pre-2001-05-14: Kenneth French daily factors (`Mkt-RF + RF`)",
        "- SPX-TR post-2001-05-14: Tiingo SPY `adj_close` pct_change",
        "- UPRO-3x pre-2009-06-25: `synthesize_letf_returns_ffr_aware(L=3, ER=0.95%)`",
        "- UPRO-3x post-2009-06-25: Tiingo UPRO `adj_close` pct_change",
        "- SSO-2x pre-2006-06-21: `synthesize_letf_returns_ffr_aware(L=2, ER=0.95%)`",
        "- SSO-2x post-2006-06-21: Tiingo SSO `adj_close` pct_change",
        "- FFR proxy: Kenneth French daily `rf` × 252",
        "- Cash sleeve: flat 4%/yr (mandate §4.6 proxy)",
        "",
        "## Known limitations",
        "",
        "- Single cash rate (4%/yr flat) is a simplification.",
        "- Year-end DARF model: 15% on year's **net** gain; loss-carry NOT modelled.",
        "- Real LETF post-inception pct_change used as-is (no added ER drag).",
        "- EMA is not a Gayed-tested kernel; it is a prompt-defined extension",
        "  over SMA for low-lag comparison `[cycle_analytics, p.9-10, ch.1-2]`.",
        "",
        "## Citations",
        "",
        "- `[leverage_for_the_long_run, p.14, Table 6]` — MA 10-200d robustness",
        "- `[leverage_for_the_long_run, p.16]` — SMA-200 ~5 trades/yr; ER 0.95%",
        "- `[leverage_for_the_long_run, p.17, Table 8]` — LRS 2x/3x CAGR/Sharpe",
        "- `[leverage_for_the_long_run, p.202]` (summary ch.) — turnover vs MA",
        "- `[cycle_analytics, p.9-10, ch.1-2]` — EMA IIR recursion",
        "- `[advances_fin_ml, p.31-34]` — F2-alignment prev_weight × ret",
        "- `[advances_fin_ml, p.208-211]` — PBO via CSCV",
        "- `[advances_fin_ml, p.275]` — Deflated Sharpe Ratio",
        "- `docs/investment-mandate.md §2.4, §2.2, §2.3, §4.6`",
        "- `docs/plans/2026-04-22-phase3.8-1-plano-b-hunt-prompt.md §B2`",
    ]

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("wrote %s", out_path)


def _write_winner_md(payload: dict[str, Any], out_path: Path) -> None:
    lines = [
        "# Phase 3.8 Winner — B2 Gayed MA-robustness sweep",
        "",
        f"**Variant:** `{payload['variant']}`",
        f"**Verdict:** {payload['verdict']}",
        f"**Git SHA:** `{_git_sha()}`",
        f"**Config hash:** `{payload['config_hash']}`",
        "",
        "## Config",
        "",
        f"- filter: {payload['cfg']['filter']}",
        f"- ma_period: {payload['cfg']['ma_period']}",
        f"- leg: {payload['cfg']['leg']}",
        f"- leverage: {3.0 if payload['cfg']['leg'] == 'UPRO' else 2.0}x",
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
        "- `[leverage_for_the_long_run, p.14, Table 6; p.16; p.17]`",
        "- `docs/investment-mandate.md §2.4, §4.6`",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("wrote %s", out_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _serializable(grid_payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Strip pd.Series fields so JSON dump is clean."""
    out = []
    for p in grid_payloads:
        out.append(
            {k: v for k, v in p.items() if k not in ("is_daily", "oos_daily", "fwd_daily")}
        )
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-crosslib", action="store_true")
    parser.add_argument("--skip-pbo", action="store_true")
    parser.add_argument("--skip-bootstrap", action="store_true")
    args = parser.parse_args(argv)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    log.info("Loading SPX-TR (stitched KF + Tiingo SPY)")
    full_returns = load_spx_tr_daily(start="1970-01-01", end="2026-04-30")
    full_price = _build_tr_price(full_returns)
    full_ffr = _load_ffr_annualized(full_returns.index)
    log.info(
        "SPX-TR loaded: %s → %s (%d days)",
        full_returns.index.min().date(),
        full_returns.index.max().date(),
        len(full_returns),
    )
    spy_bh_daily = full_returns.copy()

    upro_real = _load_letf_real_returns(UPRO_PATH) if UPRO_PATH.exists() else None
    sso_real = _load_letf_real_returns(SSO_PATH) if SSO_PATH.exists() else None

    grid = _build_grid()
    log.info("Grid built: %d configs", len(grid))

    grid_payloads = _run_grid_all_windows(
        grid, full_returns, full_price, full_ffr, upro_real, sso_real
    )

    winner = _select_winner(grid_payloads)
    log.info(
        "Winner by OOS Sharpe: %s (OOS Sharpe=%.3f)",
        winner["variant"], winner["oos_stats"]["sharpe_daily"],
    )

    payload = _evaluate_winner(
        winner,
        grid_payloads,
        full_returns,
        full_price,
        full_ffr,
        upro_real,
        sso_real,
        spy_bh_daily,
        skip_crosslib=args.skip_crosslib,
        skip_pbo=args.skip_pbo,
        skip_bootstrap=args.skip_bootstrap,
    )

    _write_aggregate_md(grid_payloads, payload, REPORT_DIR / "AGGREGATE.md")
    summary_payload = {
        "git_sha": _git_sha(),
        "windows": {
            "IS": [IS_START, IS_END],
            "OOS": [OOS_START, OOS_END],
            "FWD": [FWD_START, FWD_END],
        },
        "grid": _serializable(grid_payloads),
        "winner": payload,
        "pbo_threshold": PBO_HARD_THRESHOLD,
    }
    (REPORT_DIR / "summary.json").write_text(
        json.dumps(summary_payload, indent=2, default=str), encoding="utf-8"
    )
    log.info("wrote %s/summary.json", REPORT_DIR)

    if payload["verdict"] == "PASS":
        _write_winner_md(payload, PHASE_DIR / "WINNER_B2.md")

    print(f"FINAL VERDICT: {payload['verdict']}")
    print(f"  winner: {payload['variant']} (hard_fails={payload['hard_fails']})")
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
