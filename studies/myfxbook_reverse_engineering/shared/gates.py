"""Gates §2.4 (mandate) on observed PnL minus cost model — generalized.

Generalized from 06_gates_observed.py. Same DSR formula (Bailey & López de
Prado), same bootstrap implementation (np.random.default_rng(seed)), same
8-equal-time-block walk-forward. Smoke test must reproduce
`reports/06_gates_observed.md` numbers to 3 decimals.

Gates per `docs/investment-mandate.md §2.4`:
2. DSR p < 0.05  `[advances_fin_ml, p.196-202]`
3. Walk-forward ≥ 6/8 windows positive
4. Single-block OOS (last 12mo) Sharpe > 0 AND bootstrap 99.9% CI low > 0
6. Bootstrap 99.9% CI low > 0 (full sample)

Skipped here (out of scope for trade-history-only analysis):
1. PBO (no parameter grid)
5. FWD 3mo stress (subset of OOS)
7. Cross-lib (numpy reference only)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from . import config

DEFAULT_OOS_CUTOFF = "2020-06-01"
DEFAULT_N_BOOTSTRAP = 10_000
DEFAULT_BOOTSTRAP_SEED = 7
DEFAULT_CI = 0.999
DEFAULT_WF_WINDOWS = 8
DEFAULT_WF_MIN_POSITIVE = 6
TRADING_DAYS_PER_YEAR = 252
OPTIMISTIC_COST_FACTOR = 0.5


def sharpe_annualized(daily_returns: pd.Series, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
    if daily_returns.std() == 0 or daily_returns.empty:
        return 0.0
    return float(daily_returns.mean() / daily_returns.std() * np.sqrt(periods_per_year))


def bootstrap_sharpe_ci(
    daily_returns: pd.Series,
    n: int = DEFAULT_N_BOOTSTRAP,
    ci: float = DEFAULT_CI,
    seed: int = DEFAULT_BOOTSTRAP_SEED,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    arr = daily_returns.dropna().values
    if len(arr) < 30:
        return (float("nan"), float("nan"))
    sharpes = np.empty(n)
    for i in range(n):
        sample = rng.choice(arr, size=len(arr), replace=True)
        std = sample.std()
        sharpes[i] = sample.mean() / std * np.sqrt(TRADING_DAYS_PER_YEAR) if std > 0 else 0.0
    lo = float(np.quantile(sharpes, (1 - ci) / 2))
    hi = float(np.quantile(sharpes, 1 - (1 - ci) / 2))
    return lo, hi


def deflated_sharpe_p(observed_sharpe: float, n_returns: int, skew: float, kurt: float) -> float:
    """DSR p-value (n_trials=1) per Bailey & López de Prado `[advances_fin_ml, p.196-202]`."""
    if n_returns < 30:
        return 1.0
    se = np.sqrt((1 - skew * observed_sharpe + (kurt - 1) / 4 * observed_sharpe**2) / (n_returns - 1))
    z = observed_sharpe / se if se > 0 else 0
    return float(1 - norm.cdf(z))


@dataclass
class GateBlock:
    n_days: int
    n_trades: int
    daily_mean: float
    daily_std: float
    sharpe: float
    dsr_p: float
    boot_lo: float
    boot_hi: float


@dataclass
class GateStats:
    system_id: str
    cost_model_spread_pips: dict[str, float]
    cost_model_commission_pips: float
    full: GateBlock
    oos: GateBlock | None
    walkforward: pd.DataFrame  # window,start,end,n_days,sharpe,mean_net_pips
    n_wf_positive: int
    sharpe_optimistic: float
    gate2_pass: bool  # DSR p<0.05
    gate3_pass: bool  # WF ≥ 6/8
    gate4_pass: bool  # OOS Sharpe>0 AND boot CI low>0
    gate6_pass: bool  # full bootstrap CI low>0
    failed_gates: list[str] = field(default_factory=list)
    passed_gates: list[str] = field(default_factory=list)


def _block_stats(daily: pd.Series, n_trades: int, n_bootstrap: int, seed: int) -> GateBlock:
    sharpe = sharpe_annualized(daily)
    dsr = deflated_sharpe_p(sharpe, len(daily), daily.skew(), daily.kurt())
    lo, hi = bootstrap_sharpe_ci(daily, n=n_bootstrap, seed=seed)
    return GateBlock(
        n_days=len(daily),
        n_trades=n_trades,
        daily_mean=float(daily.mean()) if len(daily) else 0.0,
        daily_std=float(daily.std()) if len(daily) else 0.0,
        sharpe=sharpe,
        dsr_p=dsr,
        boot_lo=lo,
        boot_hi=hi,
    )


def compute_gates(
    trades_df: pd.DataFrame,
    system_id: int | str,
    cost_model: config.CostModel | None = None,
    oos_cutoff: str = DEFAULT_OOS_CUTOFF,
    n_bootstrap: int = DEFAULT_N_BOOTSTRAP,
    seed: int = DEFAULT_BOOTSTRAP_SEED,
    n_wf_windows: int = DEFAULT_WF_WINDOWS,
    min_wf_positive: int = DEFAULT_WF_MIN_POSITIVE,
) -> GateStats:
    cm = cost_model or config.pepperstone_razor_2025()
    df = trades_df
    trades = df[df["is_trade"]].copy().sort_values("close_dt_utc").reset_index(drop=True)
    trades["cost_pips"] = trades["symbol"].map(lambda s: cm.cost_for(s))
    trades["net_pips"] = trades["pips"] - trades["cost_pips"]
    trades["close_date"] = trades["close_dt_utc"].dt.date

    daily = trades.groupby("close_date")["net_pips"].sum()
    full_block = _block_stats(daily, len(trades), n_bootstrap, seed)

    cutoff = pd.Timestamp(oos_cutoff).date()
    oos_daily = daily[daily.index >= cutoff]
    oos_trades = int((trades["close_dt_utc"].dt.date >= cutoff).sum())
    oos_block = _block_stats(oos_daily, oos_trades, n_bootstrap, seed) if len(oos_daily) >= 30 else None

    daily_ts = daily.copy()
    daily_ts.index = pd.to_datetime(daily_ts.index)
    daily_ts = daily_ts.sort_index()
    splits = np.array_split(daily_ts.index, n_wf_windows)
    wf_rows = []
    for i, idxs in enumerate(splits):
        if len(idxs) == 0:
            continue
        window_data = daily_ts.loc[idxs.min():idxs.max()]
        if len(window_data) < 5:
            continue
        wf_rows.append({
            "window": i + 1,
            "start": str(idxs.min().date()),
            "end": str(idxs.max().date()),
            "n_days": len(window_data),
            "sharpe": round(sharpe_annualized(window_data), 3),
            "mean_net_pips": round(float(window_data.mean()), 3),
        })
    wf_df = pd.DataFrame(wf_rows)
    n_pos = int((wf_df["sharpe"] > 0).sum()) if len(wf_df) else 0

    trades["net_pips_optimistic"] = trades["pips"] - trades["cost_pips"] * OPTIMISTIC_COST_FACTOR
    daily_opt = trades.groupby("close_date")["net_pips_optimistic"].sum()
    sharpe_opt = sharpe_annualized(daily_opt)

    gate2 = full_block.dsr_p < 0.05
    gate3 = n_pos >= min_wf_positive
    gate4 = (oos_block is not None and oos_block.sharpe > 0 and oos_block.boot_lo > 0)
    gate6 = full_block.boot_lo > 0

    gates = {
        "Gate 2 (DSR)": gate2,
        "Gate 3 (WF)": gate3,
        "Gate 4 (OOS)": gate4,
        "Gate 6 (Bootstrap)": gate6,
    }
    failed = [g for g, p in gates.items() if not p]
    passed = [g for g, p in gates.items() if p]

    return GateStats(
        system_id=str(system_id),
        cost_model_spread_pips=dict(cm.spread_pips),
        cost_model_commission_pips=cm.commission_pips,
        full=full_block,
        oos=oos_block,
        walkforward=wf_df,
        n_wf_positive=n_pos,
        sharpe_optimistic=sharpe_opt,
        gate2_pass=gate2,
        gate3_pass=gate3,
        gate4_pass=gate4,
        gate6_pass=gate6,
        failed_gates=failed,
        passed_gates=passed,
    )


def format_gates_report(stats: GateStats, *, generated: str | None = None) -> str:
    lines: list[str] = []
    lines.append(f"# Gates §2.4 verdict — system {stats.system_id} (PnL minus cost model)")
    if generated:
        lines.append(f"\nGenerated: {generated}")
    spread = stats.cost_model_spread_pips
    lines.append(
        f"\n## Cost model (pips RT)\n"
        f"- Spreads: {spread}\n"
        f"- Commission: {stats.cost_model_commission_pips} pips RT\n"
        f"- Total cost per trade range: "
        f"{min(spread.values()) + stats.cost_model_commission_pips:.2f} – "
        f"{max(spread.values()) + stats.cost_model_commission_pips:.2f} pips"
    )
    lines.append("\n## Full-period")
    lines.append(f"- N trade days: {stats.full.n_days}")
    lines.append(f"- N trades: {stats.full.n_trades}")
    lines.append(f"- Daily net pips mean: {stats.full.daily_mean:.2f} | std: {stats.full.daily_std:.2f}")
    lines.append(f"- **Annualized Sharpe (full): {stats.full.sharpe:.3f}**")
    lines.append(f"- DSR p-value: {stats.full.dsr_p:.4f}")
    lines.append(f"- Bootstrap 99.9% CI: [{stats.full.boot_lo:.3f}, {stats.full.boot_hi:.3f}]")

    if stats.oos:
        lines.append(f"\n## Gate 4 — Single-block OOS")
        lines.append(f"- N days OOS: {stats.oos.n_days} | trades OOS: {stats.oos.n_trades}")
        lines.append(f"- OOS daily mean: {stats.oos.daily_mean:.2f} | std: {stats.oos.daily_std:.2f}")
        lines.append(f"- **OOS Sharpe: {stats.oos.sharpe:.3f}**")
        lines.append(f"- OOS DSR p-value: {stats.oos.dsr_p:.4f}")
        lines.append(f"- OOS bootstrap 99.9% CI: [{stats.oos.boot_lo:.3f}, {stats.oos.boot_hi:.3f}]")
        lines.append(f"- **Gate 4 verdict: {'✅ PASS' if stats.gate4_pass else '❌ FAIL'}**")
    else:
        lines.append("\n## Gate 4 — INSUFFICIENT OOS DATA (< 30 days)")

    lines.append("\n## Gate 6 — Bootstrap 99.9% CI low > 0 (full)")
    lines.append(f"- 99.9% CI low (full): {stats.full.boot_lo:.3f}")
    lines.append(f"- **Gate 6 verdict: {'✅ PASS' if stats.gate6_pass else '❌ FAIL'}**")

    lines.append("\n## Gate 3 — Walk-forward 8 windows (≥ 6/8 positive)")
    lines.append("```")
    lines.append(stats.walkforward.to_string(index=False))
    lines.append("```")
    lines.append(f"- Positive windows: {stats.n_wf_positive}/8")
    lines.append(f"- **Gate 3 verdict: {'✅ PASS' if stats.gate3_pass else '❌ FAIL'}**")

    lines.append("\n## Gate 2 — DSR p < 0.05")
    lines.append(f"- DSR p-value (full): {stats.full.dsr_p:.4f}")
    lines.append(f"- **Gate 2 verdict: {'✅ PASS' if stats.gate2_pass else '❌ FAIL'}**")

    lines.append("\n## Cost-model sensitivity (optimistic 50%)")
    lines.append(f"- Sharpe under optimistic costs: {stats.sharpe_optimistic:.3f}")

    lines.append("\n## Final verdict")
    lines.append(f"- Passed: {stats.passed_gates if stats.passed_gates else 'NONE'}")
    lines.append(f"- Failed: {stats.failed_gates if stats.failed_gates else 'NONE'}")
    if stats.failed_gates:
        lines.append("\n### ❌ K4 TRIGGERED — gates §2.4 FAIL on observed PnL minus cost model")
    else:
        lines.append("\n### ✅ Gates §2.4 PASS")
    return "\n".join(lines)


def write_gates_report(
    trades_df: pd.DataFrame,
    system_id: int | str,
    output_path: Path | None = None,
    cost_model: config.CostModel | None = None,
    *,
    generated: str | None = None,
    **compute_kwargs,
) -> tuple[GateStats, Path]:
    stats = compute_gates(trades_df, system_id, cost_model=cost_model, **compute_kwargs)
    path = output_path or config.gates_report_path(system_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_gates_report(stats, generated=generated))
    return stats, path
