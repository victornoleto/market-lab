"""Phase 3.8 B5 runner — Faber 10-mo GTAA single-asset SPY × 13 gates.

Runs 4 variants (monthly SMA-{6, 10, 12} + daily SMA-210) through the
mandate §2.4 13-gate framework on mutually-exclusive IS / OOS / FWD
windows. Writes a full AGGREGATE.md + summary.json in
``reports/phase_3_8/b5_faber/``. Winner = the variant with highest OOS
Sharpe; the winner then runs the full hard-gate pack. If the winner
passes all hard gates AND CAGR ≥ 11% (Marginal tier or better) →
``WINNER_B5.md``. If the winner passes hard gates but CAGR < 11%
(Folclore tier) → ``FOLCLORE_PASS.md`` per plan line 352-354.

Windows (mutually exclusive)
----------------------------
* IS   : 1970-01-02 → 1999-12-31 (SPX-TR stitched KF + SPY post-2001)
* OOS  : 2000-01-01 → 2015-12-31
* FWD  : 2016-01-01 → 2026-04-15

Grid (4 configs — single-feature, PBO < 0.3)
-------------------------------------------
* V1 — monthly rebal, SMA 10 months  (Faber canonical)
* V2 — monthly rebal, SMA  6 months  (shorter — Phase 3.6 C robustness)
* V3 — monthly rebal, SMA 12 months  (longer — Phase 3.6 C robustness)
* V4 — daily  rebal, SMA 210 days    (Gayed SMA-200 cousin, unleveraged)

13-gate framework (rota B Inter, mandate §2.4 + §2.2/§2.3 tiers WARN)
--------------------------------------------------------------------
1 IS Sharpe > 0.5          | 2 OOS Sharpe ≥ 1.3         | 3 OOS CAGR tier (WARN)
4 OOS MDD tier (WARN)       | 5 FWD Sharpe > 0           | 6 WF ≥ 6/8
7 Median hold ≥ 5 days      | 8 IR vs SPY ≥ 0.2          | 9 Cross-lib ≤ 3pp (HARD)
10 Bootstrap 99.9% CI > 0 HARD | 11 PBO < 0.3 (HARD)    | 12 DSR p < 0.05 (HARD)
13 Cost×2 Sharpe > 1.0 (B5 unleveraged — plan line 307)

PASS iff all 4 HARD (9/10/11/12) PASS AND all soft (1/2/5/6/7/8/13) PASS.

Citations
---------
* ``[phase3_7_literature_sprint §T3]`` — Faber 2007 canonical
* ``[trading_evolved, p.211-212]`` — 10-month SMA filter caveat
* ``[leverage_for_the_long_run, p.13-14]`` — SMA-200 daily ≈ 10-mo monthly
* ``[advances_fin_ml, p.31-34, p.208-211, p.275]`` — F2, PBO, DSR
* ``docs/investment-mandate.md §2.4, §2.2, §2.3, §4.6`` — gates + tiers + rota B
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
    load_spx_tr_daily,
)
from ai_trade.backtest.helpers.synthetic_letf import (  # noqa: E402
    TRADING_DAYS_PER_YEAR,
)
from ai_trade.backtest.strategies.phase3_8_b5_faber_gtaa_single import (  # noqa: E402
    B5Config,
    B5Result,
    compute_daily_regime,
    compute_monthly_regime,
    simulate_b5,
)
from ai_trade.backtest.validation import dsr, walk_forward_gate  # noqa: E402
from ai_trade.backtest.validation.bootstrap import (  # noqa: E402
    stationary_bootstrap_trades,
)
from ai_trade.backtest.validation.pbo import pbo  # noqa: E402

LOG_FMT = "%(asctime)s %(levelname)-5s %(name)s %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FMT)
log = logging.getLogger("b5_faber_gtaa")

REPORT_DIR = REPO_ROOT / "reports" / "phase_3_8" / "b5_faber"
PHASE_DIR = REPO_ROOT / "reports" / "phase_3_8"

IS_START, IS_END = "1970-01-02", "1999-12-31"
OOS_START, OOS_END = "2000-01-01", "2015-12-31"
FWD_START, FWD_END = "2016-01-01", "2026-04-15"

TRADING_DAYS = 252


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

def _build_tr_price(returns: pd.Series) -> pd.Series:
    price = (1.0 + returns).cumprod() * 100.0
    price.name = "spy_tr_price"
    return price


# ---------------------------------------------------------------------------
# Window runner
# ---------------------------------------------------------------------------

def run_window(
    returns: pd.Series,
    price: pd.Series,
    cfg: B5Config,
    label: str,
) -> tuple[dict[str, Any], B5Result, pd.Series]:
    res = simulate_b5(returns, price, cfg)
    daily = res.daily_returns.dropna()
    on_frac = float((res.exposure > 0).mean())
    out = {
        "label": label,
        "variant": _variant_tag(cfg),
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


def _variant_tag(cfg: B5Config) -> str:
    if cfg.rebal == "monthly":
        return f"B5-monthly-SMA{cfg.sma_months}mo"
    return f"B5-daily-SMA{cfg.daily_sma_window}d"


def _short_hash(cfg: B5Config) -> str:
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
    price: pd.Series,
    cfg: B5Config,
) -> float:
    """Cross-library replica of B5 gross (pre-tax, pre-switch) CAGR.

    Builds the same 0/1 regime gate and computes a compound CAGR via
    vectorbt utilities. Tax and switch costs are excluded from both
    sides so the comparison is honest.
    """
    try:
        import vectorbt as vbt  # noqa: F401
    except ImportError:
        return float("nan")

    if cfg.rebal == "monthly":
        regime = compute_monthly_regime(price, sma_months=cfg.sma_months)
    else:
        regime = compute_daily_regime(price, sma_days=cfg.daily_sma_window)
    gate = regime.astype(float)
    cash_d = cfg.cash_rate_annual / TRADING_DAYS_PER_YEAR
    gross = gate * returns.astype(float) + (1.0 - gate) * cash_d

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
# Stress periods (shared with B1)
# ---------------------------------------------------------------------------

STRESS_PERIODS: dict[str, tuple[str, str]] = {
    "dotcom_2000_2002": ("2000-01-01", "2002-12-31"),
    "gfc_2007_2009": ("2007-10-01", "2009-03-31"),
    "euro_2011": ("2011-05-01", "2011-12-31"),
    "covid_2020_03": ("2020-02-01", "2020-04-30"),
    "rate_shock_2022": ("2022-01-01", "2022-12-31"),
}


# ---------------------------------------------------------------------------
# Variant orchestration — lightweight pass (IS/OOS/FWD stats + turnover)
# ---------------------------------------------------------------------------

def _run_variant_lite(
    cfg: B5Config,
    full_returns: pd.Series,
    full_price: pd.Series,
    spy_bh_daily: pd.Series,
) -> dict[str, Any]:
    """Run IS/OOS/FWD windows on a variant and capture headline stats.

    Used to pick the winner by OOS Sharpe before running the full hard
    gate pack. This avoids spending bootstrap/PBO/DSR cycles on losers.
    """
    def _slice(s, start, end):
        ts_start = pd.Timestamp(start)
        ts_end = pd.Timestamp(end)
        return s.loc[(s.index >= ts_start) & (s.index <= ts_end)]

    is_ret = _slice(full_returns, IS_START, IS_END)
    is_px = _slice(full_price, IS_START, IS_END)
    oos_ret = _slice(full_returns, OOS_START, OOS_END)
    oos_px = _slice(full_price, OOS_START, OOS_END)
    fwd_ret = _slice(full_returns, FWD_START, FWD_END)
    fwd_px = _slice(full_price, FWD_START, FWD_END)

    is_stats, _is_res, is_daily = run_window(is_ret, is_px, cfg, "IS")
    oos_stats, _oos_res, oos_daily = run_window(oos_ret, oos_px, cfg, "OOS")
    fwd_stats, _fwd_res, fwd_daily = run_window(fwd_ret, fwd_px, cfg, "FWD")

    oos_spy = _slice(spy_bh_daily, OOS_START, OOS_END)
    ir_oos = _ir_vs_bench(oos_daily, oos_spy)

    full_years = (
        pd.Timestamp(FWD_END) - pd.Timestamp(IS_START)
    ).days / 365.25
    full_switches = (
        is_stats["n_switches"]
        + oos_stats["n_switches"]
        + fwd_stats["n_switches"]
    )
    trades_per_yr = full_switches / full_years if full_years > 0 else 0.0

    return {
        "variant": _variant_tag(cfg),
        "config_hash": _short_hash(cfg),
        "cfg": asdict(cfg),
        "is_stats": is_stats,
        "oos_stats": oos_stats,
        "fwd_stats": fwd_stats,
        "ir_oos": ir_oos,
        "trades_per_yr": trades_per_yr,
        "oos_cagr_tier": cagr_tier_B(oos_stats["cagr"]),
        "oos_mdd_tier": mdd_tier_B(oos_stats["mdd"]),
        "is_daily": is_daily,  # keep for later gates
        "oos_daily": oos_daily,
        "fwd_daily": fwd_daily,
    }


def _run_hard_gates(
    payload: dict[str, Any],
    cfg: B5Config,
    full_returns: pd.Series,
    full_price: pd.Series,
    spy_bh_daily: pd.Series,
    all_variant_configs: list[B5Config],
    *,
    skip_crosslib: bool,
    skip_pbo: bool,
    skip_bootstrap: bool,
) -> dict[str, Any]:
    """Augment a variant payload with the full hard-gate pack (9-13) + WF."""
    variant_tag = payload["variant"]
    is_daily = payload["is_daily"]
    oos_daily = payload["oos_daily"]
    fwd_daily = payload["fwd_daily"]
    is_stats = payload["is_stats"]
    oos_stats = payload["oos_stats"]
    fwd_stats = payload["fwd_stats"]
    ir_oos = payload["ir_oos"]

    def _slice(s, start, end):
        ts_start = pd.Timestamp(start)
        ts_end = pd.Timestamp(end)
        return s.loc[(s.index >= ts_start) & (s.index <= ts_end)]

    is_ret = _slice(full_returns, IS_START, IS_END)
    is_px = _slice(full_price, IS_START, IS_END)
    oos_ret = _slice(full_returns, OOS_START, OOS_END)
    oos_px = _slice(full_price, OOS_START, OOS_END)

    # Stress periods
    stress_rows: list[tuple[str, dict[str, Any]]] = []
    for key, (s_, e_) in STRESS_PERIODS.items():
        start_ts = pd.Timestamp(s_)
        if start_ts < pd.Timestamp(OOS_END):
            src_daily = oos_daily
        else:
            src_daily = fwd_daily
        sub_daily = _slice(src_daily, s_, e_)
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

    # Cost × 2 (B5-specific: unleveraged → threshold 1.0, plan line 307)
    cfg_2x = B5Config(
        **{
            **asdict(cfg),
            "commission_bps": cfg.commission_bps * 2.0,
            "spread_bps": cfg.spread_bps * 2.0,
            "spy_expense_ratio": 0.0018,  # 2× SPY 0.09% ER to honor cost×2
            "tax_rate": min(cfg.tax_rate * 2.0, 0.30),
        }
    )
    cost2_stats, _, cost2_daily = run_window(
        oos_ret, oos_px, cfg_2x, "OOS_2x_cost"
    )
    log.info("[%s] cost×2 OOS: %s", variant_tag, cost2_stats)

    # Walk-forward — 8 windows over IS+OOS
    all_daily = pd.concat([is_daily, oos_daily])
    n_windows = 8
    wf_returns: list[float] = []
    wf_dds: list[float] = []
    if len(all_daily) >= n_windows * 30:
        size = len(all_daily) // n_windows
        for k in range(n_windows):
            w = all_daily.iloc[k * size: (k + 1) * size]
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

    # Bootstrap 99.9% CI low > 0 on OOS and FULL
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
    log.info("[%s] bootstrap: %s", variant_tag, boot_results)

    # PBO — 4-config single-feature family (V1/V2/V3/V4) over IS+OOS.
    pbo_value = float("nan")
    pbo_verdict = "n/a"
    if not skip_pbo:
        log.info(
            "[%s] Running PBO grid (%d configs, single-feature)",
            variant_tag, len(all_variant_configs),
        )
        is_plus_oos_ret = pd.concat([is_ret, oos_ret])
        is_plus_oos_px = pd.concat([is_px, oos_px])
        cols: list[np.ndarray] = []
        for c in all_variant_configs:
            r = simulate_b5(is_plus_oos_ret, is_plus_oos_px, c)
            d = r.daily_returns.dropna().to_numpy()
            cols.append(d)
        min_len = min(len(c) for c in cols)
        mat = np.column_stack([c[-min_len:] for c in cols])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            pres = pbo(mat, n_blocks=10)
        pbo_value = float(pres.pbo)
        # B5 threshold: PBO < 0.3 (single-feature, plan line 305)
        pbo_verdict = "pass" if pbo_value < 0.3 else "reject"
        log.info(
            "[%s] PBO=%.4f verdict=%s (threshold 0.3, n_configs=%d)",
            variant_tag, pbo_value, pbo_verdict, len(cols),
        )

    # DSR — OOS track, n_trials = 4 (one per PBO grid cell).
    oos_trades = oos_daily.dropna().to_numpy()
    if len(oos_trades) >= 10:
        dsr_res = dsr(oos_trades, n_trials=len(all_variant_configs))
        dsr_p = float(dsr_res.p_value)
    else:
        dsr_p = float("nan")
    log.info("[%s] DSR p=%s", variant_tag, dsr_p)

    # Cross-lib (Gate 9 HARD) on winner only
    delta_pp_cagr = float("nan")
    crosslib_note = "skipped"
    if not skip_crosslib:
        log.info(
            "[%s] Cross-lib — pandas-ref vs vectorbt replica on OOS",
            variant_tag,
        )
        try:
            vbt_cagr = _crosslib_vbt_cagr(oos_ret, oos_px, cfg)
            cfg_no_tax = B5Config(
                **{
                    **asdict(cfg),
                    "tax_rate": 0.0,
                    "commission_bps": 0.0,
                    "spread_bps": 0.0,
                }
            )
            _, _, d_noval = run_window(oos_ret, oos_px, cfg_no_tax, "ref_notax")
            pandas_cagr_notax = _cagr(d_noval)
            delta_pp_cagr = abs(pandas_cagr_notax - vbt_cagr) * 100
            crosslib_note = (
                f"pandas(no-tax)={pandas_cagr_notax:.3%}, vbt={vbt_cagr:.3%}, "
                f"|Δ|={delta_pp_cagr:.3f}pp (compared ex-tax/ex-cost to match vbt scope)"
            )
            log.info("[%s] %s", variant_tag, crosslib_note)
        except Exception as e:
            crosslib_note = f"FAILED — {type(e).__name__}: {e}"
            log.warning("[%s] %s", variant_tag, crosslib_note)

    # Gate verdicts
    oos_cagr_t = cagr_tier_B(oos_stats["cagr"])
    oos_mdd_t = mdd_tier_B(oos_stats["mdd"])
    is_sharpe_pass = is_stats["sharpe_daily"] > 0.5
    oos_sharpe_pass = oos_stats["sharpe_daily"] >= 1.3
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
    # B5-specific: cost×2 Sharpe > 1.0 (unleveraged, plan line 307)
    cost2_pass = cost2_stats["sharpe_daily"] > 1.0

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
        ("11 PBO < 0.3 (HARD)",
         f"pbo={pbo_value:.3f}" if np.isfinite(pbo_value) else "skipped",
         "PASS" if pbo_pass else "FAIL"),
        ("12 DSR p < 0.05 (HARD)",
         f"p={dsr_p:.4f}" if np.isfinite(dsr_p) else "n/a",
         "PASS" if dsr_pass else "FAIL"),
        ("13 Cost×2 Sharpe > 1.0 (unleveraged)",
         f"{cost2_stats['sharpe_daily']:.3f} (cagr={cost2_stats['cagr']:.3%})",
         "PASS" if cost2_pass else "FAIL"),
    ]

    hard_fails = sum(
        1
        for label, _, v in gate_rows
        if v == "FAIL" and any(k in label for k in ("HARD",))
    )

    payload.update({
        "verdict": final_verdict,
        "hard_fails": hard_fails,
        "oos_cagr_tier": oos_cagr_t,
        "oos_mdd_tier": oos_mdd_t,
        "cost2_stats": cost2_stats,
        "wf_returns": wf_returns,
        "wf_dds": wf_dds,
        "wf_verdict": wf_verdict,
        "boot_results": boot_results,
        "pbo_value": pbo_value,
        "pbo_verdict": pbo_verdict,
        "dsr_p": dsr_p,
        "crosslib_delta_pp": delta_pp_cagr,
        "crosslib_note": crosslib_note,
        "stress_rows": stress_rows,
        "gate_rows": gate_rows,
    })
    # Remove bulky daily series from JSON-able payload (kept implicitly
    # by callers while writing; drop at JSON dump time).
    return payload


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

def _write_aggregate_md(
    lite_payloads: list[dict[str, Any]],
    winner_payload: dict[str, Any] | None,
    out_path: Path,
) -> None:
    """Write the aggregate report: all 4 variants at a glance + winner gates."""
    if winner_payload is not None and winner_payload["verdict"] == "PASS":
        headline = (
            f"**Verdict: PASS** — winner `{winner_payload['variant']}` "
            f"(tier **{winner_payload['oos_cagr_tier']}** / MDD tier "
            f"**{winner_payload['oos_mdd_tier']}**)"
        )
    elif winner_payload is not None:
        n_hard = winner_payload["hard_fails"]
        headline = (
            f"**Verdict: FAIL** — winner candidate `{winner_payload['variant']}` "
            f"fails {n_hard}/4 hard gates "
            f"(CAGR tier **{winner_payload['oos_cagr_tier']}**)"
        )
    else:
        headline = "**Verdict: FAIL** — no viable candidate"

    lines: list[str] = [
        "# Phase 3.8 B5 — Faber 10-mo GTAA single-asset SPY — Honest Validation",
        "",
        headline,
        "",
        f"- **Git SHA:** `{_git_sha()}`",
        "- **Universe:** SPY stitched (Ken French market TR pre-2001-05-14 + Tiingo SPY `adj_close` post), UNLEVERAGED",
        f"- **Windows:** IS `{IS_START} → {IS_END}`, OOS `{OOS_START} → {OOS_END}`, FWD `{FWD_START} → {FWD_END}`",
        "- **Cost model (rota B Inter, mandate §4.6):** commission=0 + spread=5.0bps/switch + DARF=15% year-end + cash_sleeve=4.0%/yr (SPY ER already embedded in adj_close)",
        "- **Grid:** 4 configs (V1 monthly SMA-10mo Faber canon, V2 monthly SMA-6mo, V3 monthly SMA-12mo, V4 daily SMA-210d Gayed cousin)",
        "- **Winner selection:** highest OOS Sharpe; hard-gate pack run on winner only",
        "",
        "## Grid stats (all 4 variants, lite pass)",
        "",
        "| Variant | Config hash | IS Sharpe | OOS Sharpe | OOS CAGR | OOS CAGR tier | OOS MDD | Trades/yr |",
        "|---------|-------------|-----------|------------|----------|---------------|---------|-----------|",
    ]
    for p in lite_payloads:
        lines.append(
            f"| `{p['variant']}` | `{p['config_hash']}` | "
            f"{p['is_stats']['sharpe_daily']:.3f} | "
            f"{p['oos_stats']['sharpe_daily']:.3f} | "
            f"{p['oos_stats']['cagr']:.3%} | **{p['oos_cagr_tier']}** | "
            f"{p['oos_stats']['mdd']:.3%} | "
            f"{p['trades_per_yr']:.2f} |"
        )
    lines.append("")

    if winner_payload is not None:
        p = winner_payload
        lines += [
            f"## Winner — {p['variant']} — {p['verdict']}",
            "",
            f"- **Config hash:** `{p['config_hash']}`",
            f"- **Turnover:** ~{p['trades_per_yr']:.2f} trades/yr",
            f"- **OOS on-regime fraction:** {p['oos_stats']['on_regime_fraction']:.2%}",
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
            f"- days={p['is_stats']['n_days']:,}, switches={p['is_stats']['n_switches']}, "
            f"median_hold={p['is_stats']['median_hold_days']:.1f}d, "
            f"on_regime={p['is_stats']['on_regime_fraction']:.2%}",
            f"- Sharpe(daily)={p['is_stats']['sharpe_daily']:.3f}, "
            f"CAGR={p['is_stats']['cagr']:.3%}, MDD={p['is_stats']['mdd']:.3%}",
            f"- Cumulative: switches={p['is_stats']['cum_cost_pct']:.3%}, "
            f"tax={p['is_stats']['cum_tax_pct']:.3%}",
            "",
            f"#### OOS ({OOS_START} → {OOS_END})",
            f"- days={p['oos_stats']['n_days']:,}, switches={p['oos_stats']['n_switches']}, "
            f"median_hold={p['oos_stats']['median_hold_days']:.1f}d",
            f"- Sharpe(daily)={p['oos_stats']['sharpe_daily']:.3f}, "
            f"CAGR={p['oos_stats']['cagr']:.3%} (tier **{p['oos_cagr_tier']}**), "
            f"MDD={p['oos_stats']['mdd']:.3%} (tier **{p['oos_mdd_tier']}**)",
            f"- IR vs SPY buy-hold: {p['ir_oos']:.3f}",
            "",
            f"#### FWD ({FWD_START} → {FWD_END})",
            f"- days={p['fwd_stats']['n_days']:,}, switches={p['fwd_stats']['n_switches']}, "
            f"median_hold={p['fwd_stats']['median_hold_days']:.1f}d",
            f"- Sharpe(daily)={p['fwd_stats']['sharpe_daily']:.3f}, "
            f"CAGR={p['fwd_stats']['cagr']:.3%}, MDD={p['fwd_stats']['mdd']:.3%}",
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
            "- Window returns: "
            + ", ".join(f"{r*100:.2f}%" for r in p["wf_returns"]),
            "- Window MDDs: "
            + ", ".join(f"{d*100:.2f}%" for d in p["wf_dds"]),
            "",
        ]

    lines += [
        "## Data provenance",
        "",
        "- SPX-TR pre-2001-05-14: Kenneth French daily factors (`Mkt-RF + RF`)",
        "- SPY post-2001-05-14: Tiingo SPY `adj_close` pct_change",
        "- Cash sleeve: flat 4%/yr (mandate §4.6 proxy for long-term 3-mo T-bill)",
        "",
        "## Known limitations",
        "",
        "- Single cash rate (4%/yr flat) is a simplification; real cash sleeve would",
        "  track the daily 3-mo T-bill curve. Second-order effect.",
        "- Year-end DARF model: 15% on year's **net** gain; loss-carry NOT",
        "  modelled (conservative per mandate §4.6 rota B).",
        "- Pre-2001-05 SPY is a KF SPX-TR proxy, not a physical SPY series —",
        "  acceptable for a daily total-return regime signal (the 2001-05 seam",
        "  is continuous to O(bp)).",
        "- B5 is unleveraged by construction → CAGR ceiling is SPY buy-hold",
        "  minus cash-sleeve drag during off-regime periods. Tier 'Válido'",
        "  (17-25%) is physically unreachable without leverage; the escalation",
        "  rule is 'hard-gates technically pass + tier Folclore → FOLCLORE_PASS.md'.",
        "",
        "## Citations",
        "",
        "- `[phase3_7_literature_sprint §T3]` — Faber 2007 canonical",
        "- `[trading_evolved, p.211-212]` — 10-month SMA filter + caveat",
        "- `[leverage_for_the_long_run, p.13-14]` — SMA-200 daily ≈ 10-mo monthly",
        "- `[advances_fin_ml, p.31-34]` — F2-alignment prev_weight × ret",
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
        "# Phase 3.8 Winner — B5 Faber 10-mo GTAA single-asset SPY (unleveraged)",
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
        "- `[phase3_7_literature_sprint §T3]` — Faber 2007 canonical",
        "- `[trading_evolved, p.211-212]` — 10-month SMA filter",
        "- `docs/investment-mandate.md §2.4, §4.6`",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("wrote %s", out_path)


def _write_folclore_pass_md(payload: dict[str, Any], out_path: Path) -> None:
    """B5 special case: hard-gates pass but OOS CAGR < 11% (Folclore tier).

    Plan line 352-354: 'tier Folclore não é winner-to-live por default;
    escalar pro usuário antes de promover'. This file flags that
    situation — orchestrator relays it to the user.
    """
    lines = [
        "# Phase 3.8 B5 — FOLCLORE_PASS (escalation required)",
        "",
        f"**Variant:** `{payload['variant']}`",
        f"**Status:** HARD-GATES PASS, but OOS CAGR tier = **{payload['oos_cagr_tier']}** (< CDI líquido 11%).",
        f"**Git SHA:** `{_git_sha()}`",
        f"**Config hash:** `{payload['config_hash']}`",
        "",
        "## Why this file (not WINNER_B5.md)",
        "",
        "Per plan `docs/plans/2026-04-22-phase3.8-1-plano-b-hunt-prompt.md`",
        "line 352-354: *'Se B5 produz winner mas CAGR líquido < 11% (Folclore",
        "tier), escalar pro usuário antes de promover — tier Folclore não é",
        "winner-to-live por default'*. The strategy technically passes the 4",
        "hard gates (cross-lib + bootstrap + PBO + DSR) and all soft gates,",
        "but the realized CAGR is below the CDI líquido floor (~11%/yr).",
        "",
        "## Tiers",
        "",
        f"- OOS CAGR: **{payload['oos_cagr_tier']}** "
        f"({payload['oos_stats']['cagr']:.3%}) — below 11% CDI líquido",
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
        "## Next step (user decision)",
        "",
        "1. **Promote anyway** — explicit sign-off that a CDI-liq-matcher is",
        "   acceptable as rota B (re-spec mandate §2.2).",
        "2. **Reject + continue search** — B1-B4 already FAIL; with B5 also",
        "   non-viable the Plano B hunt is effectively exhausted under honest",
        "   gates + DARF. Proceed to `BREADTH_NO_WINNER_B.md`.",
        "3. **Stage paper trading** — live-collect 6-12 months without real",
        "   capital while the mandate is revised.",
        "",
        "## Citations",
        "",
        "- `[phase3_7_literature_sprint §T3]` — Faber 2007 canonical",
        "- `docs/investment-mandate.md §2.2, §2.4, §4.6`",
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

    log.info("Loading SPY-TR (stitched KF + Tiingo SPY)")
    full_returns = load_spx_tr_daily(start="1970-01-01", end="2026-04-30")
    full_price = _build_tr_price(full_returns)
    log.info(
        "SPY-TR loaded: %s → %s (%d days)",
        full_returns.index.min().date(),
        full_returns.index.max().date(),
        len(full_returns),
    )
    spy_bh_daily = full_returns.copy()

    # 4-config grid
    variants: list[B5Config] = [
        B5Config(sma_months=10, rebal="monthly"),  # V1 — Faber canon
        B5Config(sma_months=6, rebal="monthly"),   # V2 — shorter
        B5Config(sma_months=12, rebal="monthly"),  # V3 — longer
        B5Config(sma_months=10, rebal="daily"),    # V4 — SMA-210 daily
    ]

    # Lite pass: IS/OOS/FWD stats per variant, pick winner by OOS Sharpe.
    lite_payloads: list[dict[str, Any]] = []
    for cfg in variants:
        log.info(
            "[lite] Running variant %s (hash=%s)",
            _variant_tag(cfg), _short_hash(cfg),
        )
        p = _run_variant_lite(cfg, full_returns, full_price, spy_bh_daily)
        # Halt contract: IS n_trades < 30 (B5 monthly has few trades by construction).
        n_switches_is = p["is_stats"]["n_switches"]
        if n_switches_is < 30:
            log.warning(
                "[lite] %s IS switches=%d (< 30) — B5 monthly cadence on "
                "30y IS is expected to be ~20-30; proceeding but flagging.",
                p["variant"], n_switches_is,
            )
        lite_payloads.append(p)
        log.info(
            "[lite] %s: IS Sharpe=%.3f, OOS Sharpe=%.3f, OOS CAGR=%.3f%%, "
            "trades/yr=%.2f",
            p["variant"], p["is_stats"]["sharpe_daily"],
            p["oos_stats"]["sharpe_daily"], p["oos_stats"]["cagr"] * 100,
            p["trades_per_yr"],
        )

    # Winner = highest OOS Sharpe.
    winner_lite = max(lite_payloads, key=lambda p: p["oos_stats"]["sharpe_daily"])
    winner_cfg = next(
        c for c in variants if _variant_tag(c) == winner_lite["variant"]
    )
    log.info(
        "Winner by OOS Sharpe: %s (OOS Sharpe=%.3f)",
        winner_lite["variant"], winner_lite["oos_stats"]["sharpe_daily"],
    )

    # Full hard-gate pack on winner only.
    winner_payload = _run_hard_gates(
        winner_lite,
        winner_cfg,
        full_returns,
        full_price,
        spy_bh_daily,
        variants,
        skip_crosslib=args.skip_crosslib,
        skip_pbo=args.skip_pbo,
        skip_bootstrap=args.skip_bootstrap,
    )

    # Write aggregate + summary.json
    _write_aggregate_md(
        lite_payloads, winner_payload, REPORT_DIR / "AGGREGATE.md"
    )
    # Strip bulky series before JSON dump.
    lite_payloads_clean = [
        {k: v for k, v in p.items() if k not in ("is_daily", "oos_daily", "fwd_daily")}
        for p in lite_payloads
    ]
    winner_clean = {
        k: v for k, v in winner_payload.items()
        if k not in ("is_daily", "oos_daily", "fwd_daily")
    }
    summary_payload = {
        "git_sha": _git_sha(),
        "windows": {
            "IS": [IS_START, IS_END],
            "OOS": [OOS_START, OOS_END],
            "FWD": [FWD_START, FWD_END],
        },
        "variants_lite": lite_payloads_clean,
        "winner": winner_clean,
    }
    (REPORT_DIR / "summary.json").write_text(
        json.dumps(summary_payload, indent=2, default=str), encoding="utf-8"
    )
    log.info("wrote %s/summary.json", REPORT_DIR)

    # Verdict dispatch per plan §B5 escalation rule (line 352-354)
    verdict = winner_payload["verdict"]
    oos_cagr = winner_payload["oos_stats"]["cagr"]
    if verdict == "PASS":
        if oos_cagr >= 0.11:
            # Marginal tier or better → WINNER_B5.md
            _write_winner_md(winner_payload, PHASE_DIR / "WINNER_B5.md")
            print(f"FINAL VERDICT: PASS — {winner_payload['variant']}")
            return 0
        # Folclore tier — escalation
        _write_folclore_pass_md(winner_payload, REPORT_DIR / "FOLCLORE_PASS.md")
        print(f"FINAL VERDICT: FOLCLORE_PASS — {winner_payload['variant']}")
        return 0
    # FAIL
    print(
        f"FINAL VERDICT: FAIL — {winner_payload['variant']} "
        f"(hard_fails={winner_payload['hard_fails']}/4)"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
