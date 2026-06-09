from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lrs.lib.backtest import (  # noqa: E402
    build_weekly_lagged_weights,
    clean_weights,
    equity_curve,
    fmt_num,
    fmt_pct,
    fmt_pp,
    fmt_x,
    md_table,
    metrics_from_returns,
    simulate_weight_frame,
    weights_label,
)
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from studies.return_stacked_core.export_sleeve_returns import build_sleeve_returns  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase05_rsc_overlay_proxy.csv"

RSC_SLEEVE_RETURNS = REPO_ROOT / "studies/return_stacked_core/us_core/series/return_stacked_core_sleeve_returns.parquet"
RSC_FULL_EQUITY = REPO_ROOT / "studies/return_stacked_core/us_core/series/full_equity_curves.csv"
RSC_CORE_COLUMN = "B4-v2 35/40/25"
RSC_SPY_COLUMN = "100% SPY"
RSC_WEIGHTS = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}
LETF_LAB_ROOT = REPO_ROOT.parent / "letf-lab"
LETF_LAB_PHASE12_EQUITY = LETF_LAB_ROOT / "studies/lrs/phases/phase_12_cross_study/results/equity_curves.csv"
T3D_COLUMN = "T3d-K2 (QLD/ZROZ)"

OVERLAY_WEIGHTS = [0.10, 0.20, 0.30]
STRICT_MDD_TOL = 1e-10


@dataclass(frozen=True)
class Satellite:
    name: str
    label: str
    source: str
    returns: pd.Series
    turnover_per_year: float
    trade_count: float
    notes: str


def read_equity_curve(path: Path, column: str) -> pd.Series:
    frame = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    if column not in frame.columns:
        raise KeyError(f"missing column {column!r} in {path}")
    series = frame[column].astype(float).dropna()
    if series.empty:
        raise ValueError(f"empty equity series for {column!r} in {path}")
    return (series / series.iloc[0]).rename(column)


def returns_from_equity(equity: pd.Series, name: str) -> pd.Series:
    clean = equity.dropna().astype(float)
    returns = clean.pct_change().dropna()
    returns.name = name
    return returns


def load_rsc_sleeve_returns() -> pd.DataFrame:
    """Load canonical RSC sleeve returns, rebuilding in memory if absent.

    The RSC baseline is evaluated from sleeves rather than from a saved top-level
    curve so overlay drawdown/turnover diagnostics stay tied to the actual
    `35/40/25` allocation geometry `[risk_parity, p.80-81]`,
    `[systematic_trading, p.185-188]`.
    """

    if RSC_SLEEVE_RETURNS.exists():
        frame = pd.read_parquet(RSC_SLEEVE_RETURNS).sort_index()
    else:
        frame = build_sleeve_returns().sort_index()
    missing = [column for column in RSC_WEIGHTS if column not in frame.columns]
    if missing:
        raise KeyError(f"missing RSC sleeve columns: {missing}")
    return frame[list(RSC_WEIGHTS)].dropna()


def rebuilt_rsc_core_returns() -> tuple[pd.Series, dict[str, float]]:
    sleeves = load_rsc_sleeve_returns()
    return monthly_rebalanced_returns(sleeves, RSC_WEIGHTS, name="rsc_core")


def saved_curve_audit(rebuilt: pd.Series, saved: pd.Series) -> dict[str, float]:
    aligned = pd.concat({"rebuilt": rebuilt, "saved": saved}, axis=1, sort=False).dropna()
    if aligned.empty:
        return {"terminal_ratio": math.nan, "cagr_diff": math.nan, "mdd_diff": math.nan, "max_abs_relative_deviation": math.nan}
    rebuilt_eq = equity_curve(aligned["rebuilt"])
    saved_eq = equity_curve(aligned["saved"])
    relative = rebuilt_eq / saved_eq
    rebuilt_m = metrics_from_returns(aligned["rebuilt"])
    saved_m = metrics_from_returns(aligned["saved"])
    return {
        "terminal_ratio": float(relative.iloc[-1]),
        "cagr_diff": float(rebuilt_m.cagr - saved_m.cagr),
        "mdd_diff": float(rebuilt_m.mdd - saved_m.mdd),
        "max_abs_relative_deviation": float((relative - 1.0).abs().max()),
    }


def first_monthly_bar_mask(index: pd.DatetimeIndex) -> pd.Series:
    periods = index.to_period("M")
    values = np.r_[True, periods[1:].to_numpy() != periods[:-1].to_numpy()]
    return pd.Series(values, index=index)


def monthly_rebalanced_returns(
    component_returns: pd.DataFrame,
    weights: dict[str, float],
    *,
    name: str = "monthly_rebalanced",
) -> tuple[pd.Series, dict[str, float]]:
    """Return daily portfolio returns with monthly fixed-weight rebalancing.

    Monthly rebalancing is a diagnostic allocation-control convention for this
    rebuilt-sleeve overlay check. It prevents satellite drift from dominating the question and
    keeps implementation-cost realism visible as turnover, rather than assuming a
    free continuous mix `[testing_tuning, p.327-335]`, `[systematic_trading,
    p.185-188]`.
    """

    clean = component_returns.dropna().astype(float)
    if clean.empty:
        raise ValueError("component_returns is empty after dropna")
    target = pd.Series(weights, dtype=float)
    if (target < -1e-12).any():
        raise ValueError("weights must be non-negative")
    if target.sum() <= 0:
        raise ValueError("weights must sum to a positive value")
    target = target / target.sum()
    missing = [column for column in target.index if column not in clean.columns]
    if missing:
        raise KeyError(f"missing component return columns: {missing}")
    clean = clean[list(target.index)]

    values = target.to_numpy(dtype=float).copy()
    target_arr = target.to_numpy(dtype=float)
    month_mask = first_monthly_bar_mask(pd.DatetimeIndex(clean.index))
    out: list[float] = []
    total_turnover = 0.0
    trade_count = 0

    for i, date in enumerate(clean.index):
        total = float(values.sum())
        if total <= 0:
            raise ValueError("portfolio value became non-positive")
        current_weights = values / total
        if i == 0 or bool(month_mask.loc[date]):
            turnover = 0.5 * float(np.abs(target_arr - current_weights).sum())
            if turnover > 1e-10:
                total_turnover += turnover
                trade_count += 1
            values = total * target_arr

        before = float(values.sum())
        values *= 1.0 + clean.loc[date].to_numpy(dtype=float)
        after = float(values.sum())
        out.append(after / before - 1.0 if before > 0 else 0.0)

    years = len(clean) / 252.0
    summary = {
        "rebalance_turnover_per_year": float(total_turnover / years) if years > 0 else math.nan,
        "rebalance_trade_count": float(trade_count),
    }
    return pd.Series(out, index=clean.index, name=name), summary


def underwater_stats(returns: pd.Series) -> dict[str, float]:
    clean = returns.dropna().astype(float)
    if clean.empty:
        return {
            "time_underwater_pct": math.nan,
            "max_recovery_days": math.nan,
            "current_underwater_days": math.nan,
        }
    equity = equity_curve(clean)
    peak_values = np.maximum.accumulate(np.r_[1.0, equity.to_numpy(dtype=float)])[1:]
    peak = pd.Series(peak_values, index=equity.index)
    underwater = equity < peak * (1.0 - 1e-10)
    longest = 0
    current = 0
    for flag in underwater.to_numpy(dtype=bool):
        if flag:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return {
        "time_underwater_pct": float(underwater.mean()),
        "max_recovery_days": float(longest),
        "current_underwater_days": float(current),
    }


def relative_to_core_stats(candidate: pd.Series, core: pd.Series) -> dict[str, float]:
    aligned = pd.concat({"candidate": candidate, "core": core}, axis=1, sort=False).dropna()
    if aligned.empty:
        return {
            "terminal_vs_rsc": math.nan,
            "pct_days_below_rsc": math.nan,
            "longest_below_rsc_days": math.nan,
            "max_deficit_vs_rsc": math.nan,
            "max_relative_drawdown_vs_rsc": math.nan,
        }
    candidate_eq = equity_curve(aligned["candidate"])
    core_eq = equity_curve(aligned["core"])
    relative = candidate_eq / core_eq
    below = relative < 1.0 - 1e-10
    longest = 0
    current = 0
    for flag in below.to_numpy(dtype=bool):
        if flag:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    rel_dd = relative / relative.cummax() - 1.0
    return {
        "terminal_vs_rsc": float(relative.iloc[-1]),
        "pct_days_below_rsc": float(below.mean()),
        "longest_below_rsc_days": float(longest),
        "max_deficit_vs_rsc": float(relative.min() - 1.0),
        "max_relative_drawdown_vs_rsc": float(rel_dd.min()),
    }


def simulate_local_lrs_satellite(spec: dict[str, object]) -> Satellite:
    branch = phase04.BRANCHES[str(spec["branch"])]
    context = phase04.build_context(branch)
    risk_off = next(r for r in phase04.RISK_OFF_SPECS if r["name"] == spec["risk_off"])
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == spec["vol_filter"])
    risk_off_weights = clean_weights(risk_off["weights"])  # type: ignore[arg-type]
    risk_on_weights = phase04.target_leverage_weights(branch, float(spec["target_leverage"]))
    signal = context.sma_signal & phase04.vol_gate(context, vol_spec)
    assets = sorted(set(risk_on_weights) | set(risk_off_weights) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=context.returns.index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(signal, risk_on_weights.get(asset, 0.0), risk_off_weights.get(asset, 0.0))
    weights, _ = build_weekly_lagged_weights(
        desired,
        lag_days=int(spec["lag_days"]),
        risk_on_weights=risk_on_weights,
    )
    returns, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    label = (
        f"{spec['branch']} L{float(spec['target_leverage']):.2f} "
        f"off {spec['risk_off']} {spec['vol_filter']} lag {int(spec['lag_days'])}"
    )
    return Satellite(
        name=str(spec["name"]),
        label=label,
        source="local_lrs_phase04_geometry",
        returns=returns.rename(str(spec["name"])),
        turnover_per_year=float(tax_summary["turnover_per_year"]),
        trade_count=float(tax_summary["trade_count"]),
        notes=f"risk_on={weights_label(risk_on_weights)}; risk_off={weights_label(risk_off_weights)}",
    )


def load_t3d_satellite() -> Satellite:
    equity = read_equity_curve(LETF_LAB_PHASE12_EQUITY, T3D_COLUMN)
    returns = returns_from_equity(equity, "t3d_k2_saved_br_lei")
    comparison = pd.read_csv(LETF_LAB_PHASE12_EQUITY.parent / "comparison_matrix.csv")
    row = comparison[
        (comparison["strategy"] == T3D_COLUMN) & (comparison["tax_scenario"] == "br_lei_14754")
    ].iloc[0]
    return Satellite(
        name="t3d_k2_saved",
        label="T3d-K2 saved br_lei curve (QLD/ZROZ)",
        source="letf_lab_phase12_saved_equity",
        returns=returns,
        turnover_per_year=float(row["switches_per_year"]),
        trade_count=float(row["n_switches"]),
        notes="Saved Phase 12 equity curve; T3d-K2 not recomputed inside market-lab.",
    )


def build_satellites() -> list[Satellite]:
    specs: list[dict[str, object]] = [
        {
            "name": "lrs_spy_headline",
            "branch": "SPY",
            "target_leverage": 2.00,
            "risk_off": "50 ZROZ / 25 GLD / 25 CASH",
            "vol_filter": "RV21 <= 30%",
            "lag_days": 3,
        },
        {
            "name": "lrs_qqq_headline",
            "branch": "QQQ",
            "target_leverage": 1.75,
            "risk_off": "40 ZROZ / 40 GLD / 20 IEF",
            "vol_filter": "RV63 <= 40%",
            "lag_days": 0,
        },
    ]
    satellites = [simulate_local_lrs_satellite(spec) for spec in specs]
    if LETF_LAB_PHASE12_EQUITY.exists():
        satellites.append(load_t3d_satellite())
    return satellites


def evaluate_candidate(
    *,
    candidate_id: str,
    candidate_type: str,
    component_label: str,
    satellite_weight: float,
    returns: pd.Series,
    core_returns: pd.Series,
    overlay_summary: dict[str, float],
    satellite: Satellite | None,
) -> dict[str, object]:
    aligned = pd.concat({"candidate": returns, "rsc": core_returns}, axis=1, sort=False).dropna()
    candidate_returns = aligned["candidate"]
    aligned_core = aligned["rsc"]
    metrics = metrics_from_returns(candidate_returns)
    core_metrics = metrics_from_returns(aligned_core)
    underwater = underwater_stats(candidate_returns)
    core_underwater = underwater_stats(aligned_core)
    rel = relative_to_core_stats(candidate_returns, aligned_core)
    cagr_spread = metrics.cagr - core_metrics.cagr
    mdd_spread = metrics.mdd - core_metrics.mdd
    calmar_spread = metrics.calmar - core_metrics.calmar
    strict_pass = bool(
        candidate_type == "overlay"
        and cagr_spread > 0.0
        and mdd_spread >= -STRICT_MDD_TOL
        and calmar_spread >= -STRICT_MDD_TOL
        and underwater["time_underwater_pct"] <= core_underwater["time_underwater_pct"] + STRICT_MDD_TOL
        and underwater["max_recovery_days"] <= core_underwater["max_recovery_days"] + STRICT_MDD_TOL
    )
    satellite_turnover = satellite.turnover_per_year if satellite else 0.0
    satellite_trades = satellite.trade_count if satellite else 0.0
    overlay_turnover = float(overlay_summary.get("rebalance_turnover_per_year", 0.0))
    return {
        "candidate_id": candidate_id,
        "candidate_type": candidate_type,
        "component_label": component_label,
        "satellite_weight": satellite_weight,
        "start": metrics.start,
        "end": metrics.end,
        "years": metrics.years,
        "cagr": metrics.cagr,
        "mdd": metrics.mdd,
        "sharpe": metrics.sharpe,
        "sortino": metrics.sortino,
        "calmar": metrics.calmar,
        "terminal": metrics.terminal,
        "rsc_cagr_same_window": core_metrics.cagr,
        "rsc_mdd_same_window": core_metrics.mdd,
        "rsc_calmar_same_window": core_metrics.calmar,
        "cagr_spread_vs_rsc": cagr_spread,
        "mdd_spread_vs_rsc": mdd_spread,
        "calmar_spread_vs_rsc": calmar_spread,
        "time_underwater_pct": underwater["time_underwater_pct"],
        "max_recovery_days": underwater["max_recovery_days"],
        "current_underwater_days": underwater["current_underwater_days"],
        "rsc_time_underwater_pct_same_window": core_underwater["time_underwater_pct"],
        "rsc_max_recovery_days_same_window": core_underwater["max_recovery_days"],
        "terminal_vs_rsc": rel["terminal_vs_rsc"],
        "pct_days_below_rsc": rel["pct_days_below_rsc"],
        "longest_below_rsc_days": rel["longest_below_rsc_days"],
        "max_deficit_vs_rsc": rel["max_deficit_vs_rsc"],
        "max_relative_drawdown_vs_rsc": rel["max_relative_drawdown_vs_rsc"],
        "overlay_rebalance_turnover_per_year": overlay_turnover,
        "overlay_rebalance_trade_count": float(overlay_summary.get("rebalance_trade_count", 0.0)),
        "satellite_turnover_per_year": satellite_turnover,
        "satellite_trade_count": satellite_trades,
        "weighted_satellite_turnover_per_year": satellite_weight * satellite_turnover,
        "estimated_total_turnover_per_year": overlay_turnover + satellite_weight * satellite_turnover,
        "strict_overlay_pass": strict_pass,
        "satellite_source": satellite.source if satellite else "rsc_sleeve_returns",
        "notes": satellite.notes if satellite else "RSC rebuilt from GDESIM/RSSTSIM/ZROZSIM sleeve returns.",
    }


def build_candidates() -> tuple[pd.DataFrame, dict[str, pd.Series], list[Satellite], dict[str, float]]:
    core_returns, core_rebalance = rebuilt_rsc_core_returns()
    saved_core_returns = returns_from_equity(read_equity_curve(RSC_FULL_EQUITY, RSC_CORE_COLUMN), "rsc_saved_reference")
    audit = saved_curve_audit(core_returns, saved_core_returns)
    spy_equity = read_equity_curve(RSC_FULL_EQUITY, RSC_SPY_COLUMN)
    spy_returns = returns_from_equity(spy_equity, "spy_saved")
    satellites = build_satellites()

    rows: list[dict[str, object]] = []
    return_map: dict[str, pd.Series] = {"rsc_core": core_returns, "rsc_saved_reference": saved_core_returns, "spy_saved": spy_returns}
    rows.append(
        evaluate_candidate(
            candidate_id="rsc_core",
            candidate_type="core",
            component_label="100% RSC-US 35/40/25",
            satellite_weight=0.0,
            returns=core_returns,
            core_returns=core_returns,
            overlay_summary=core_rebalance,
            satellite=None,
        )
    )

    for satellite in satellites:
        return_map[satellite.name] = satellite.returns
        rows.append(
            evaluate_candidate(
                candidate_id=satellite.name,
                candidate_type="satellite_reference",
                component_label=f"100% {satellite.label}",
                satellite_weight=1.0,
                returns=satellite.returns,
                core_returns=core_returns,
                overlay_summary={"rebalance_turnover_per_year": 0.0, "rebalance_trade_count": 0.0},
                satellite=satellite,
            )
        )
        for weight in OVERLAY_WEIGHTS:
            candidate_id = f"rsc_{int((1.0 - weight) * 100):02d}_{satellite.name}_{int(weight * 100):02d}"
            aligned = pd.concat({"rsc": core_returns, satellite.name: satellite.returns}, axis=1, sort=False).dropna()
            combined, overlay_summary = monthly_rebalanced_returns(
                aligned,
                {"rsc": 1.0 - weight, satellite.name: weight},
                name=candidate_id,
            )
            return_map[candidate_id] = combined
            rows.append(
                evaluate_candidate(
                    candidate_id=candidate_id,
                    candidate_type="overlay",
                    component_label=f"{(1.0 - weight) * 100:.0f}% RSC / {weight * 100:.0f}% {satellite.label}",
                    satellite_weight=weight,
                    returns=combined,
                    core_returns=core_returns,
                    overlay_summary=overlay_summary,
                    satellite=satellite,
                )
            )

    results = pd.DataFrame(rows).sort_values(
        ["candidate_type", "strict_overlay_pass", "cagr_spread_vs_rsc", "calmar_spread_vs_rsc"],
        ascending=[True, False, False, False],
    )
    return results, return_map, satellites, audit


def drawdown(returns: pd.Series) -> pd.Series:
    eq = equity_curve(returns)
    return eq / eq.cummax() - 1.0


def plot_equity(return_map: dict[str, pd.Series], results: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    overlay = results[results["candidate_type"] == "overlay"].sort_values("cagr_spread_vs_rsc", ascending=False).head(3)
    ids = ["rsc_core", *[str(x) for x in overlay["candidate_id"]]]
    aligned = pd.concat({candidate_id: equity_curve(return_map[candidate_id]) for candidate_id in ids}, axis=1, sort=False).dropna()
    fig, ax = plt.subplots(figsize=(11, 6))
    aligned.plot(ax=ax, logy=True, linewidth=1.2)
    ax.set_title("Phase 5 rebuilt sleeves: RSC vs top CAGR overlays")
    ax.set_ylabel("Growth of $1")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase05_equity_top_overlays.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_drawdowns(return_map: dict[str, pd.Series], results: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    overlay = results[results["candidate_type"] == "overlay"].sort_values("cagr_spread_vs_rsc", ascending=False).head(3)
    ids = ["rsc_core", *[str(x) for x in overlay["candidate_id"]]]
    aligned = pd.concat({candidate_id: drawdown(return_map[candidate_id]) for candidate_id in ids}, axis=1, sort=False).dropna()
    fig, ax = plt.subplots(figsize=(11, 5))
    (aligned * 100.0).plot(ax=ax, linewidth=1.1)
    ax.set_title("Phase 5 rebuilt sleeves: drawdowns")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase05_drawdowns_top_overlays.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_relative(return_map: dict[str, pd.Series], results: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    overlay = results[results["candidate_type"] == "overlay"].sort_values("cagr_spread_vs_rsc", ascending=False).head(5)
    core = equity_curve(return_map["rsc_core"])
    data = {}
    for candidate_id in overlay["candidate_id"]:
        candidate_id = str(candidate_id)
        aligned = pd.concat({"candidate": equity_curve(return_map[candidate_id]), "core": core}, axis=1, sort=False).dropna()
        data[candidate_id] = aligned["candidate"] / aligned["core"]
    frame = pd.DataFrame(data).dropna()
    fig, ax = plt.subplots(figsize=(11, 5))
    frame.plot(ax=ax, linewidth=1.1)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=0.8)
    ax.set_title("Phase 5 rebuilt sleeves: overlay relative wealth vs RSC")
    ax.set_ylabel("Relative wealth")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase05_relative_vs_rsc.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(results: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6))
    colors = {"core": "black", "satellite_reference": "tab:red", "overlay": "tab:blue"}
    for kind, subset in results.groupby("candidate_type", sort=True):
        ax.scatter(
            subset["mdd"] * 100.0,
            subset["cagr"] * 100.0,
            label=kind,
            s=52 if kind == "core" else 36,
            alpha=0.75,
            color=colors.get(str(kind), None),
        )
    core = results[results["candidate_id"] == "rsc_core"].iloc[0]
    ax.axhline(float(core["cagr"]) * 100.0, color="black", linestyle="--", linewidth=0.8)
    ax.axvline(float(core["mdd"]) * 100.0, color="black", linestyle="--", linewidth=0.8)
    ax.set_title("Phase 5 rebuilt-sleeve frontier")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("CAGR (%)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase05_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def make_plots(return_map: dict[str, pd.Series], results: pd.DataFrame) -> list[dict[str, str]]:
    PLOTS.mkdir(parents=True, exist_ok=True)
    plots = [
        ("Equity top overlays", plot_equity(return_map, results)),
        ("Drawdowns top overlays", plot_drawdowns(return_map, results)),
        ("Relative wealth vs RSC", plot_relative(return_map, results)),
        ("Risk/return frontier", plot_frontier(results)),
    ]
    return [{"Plot": label, "File": f"[plots/{path.name}](plots/{path.name})"} for label, path in plots]


def candidate_rows(frame: pd.DataFrame, *, kind: str | None = None, limit: int = 20) -> list[dict[str, object]]:
    subset = frame if kind is None else frame[frame["candidate_type"] == kind]
    subset = subset.sort_values(["strict_overlay_pass", "cagr_spread_vs_rsc", "calmar_spread_vs_rsc"], ascending=False).head(limit)
    rows: list[dict[str, object]] = []
    for _, row in subset.iterrows():
        rows.append(
            {
                "Candidate": row["candidate_id"],
                "Type": row["candidate_type"],
                "CAGR": fmt_pct(row["cagr"]),
                "MDD": fmt_pct(row["mdd"]),
                "Sharpe": fmt_num(row["sharpe"]),
                "Calmar": fmt_num(row["calmar"]),
                "CAGR vs RSC": fmt_pp(row["cagr_spread_vs_rsc"]),
                "MDD vs RSC": fmt_pp(row["mdd_spread_vs_rsc"]),
                "Terminal/RSC": fmt_x(row["terminal_vs_rsc"]),
                "Rel DD": fmt_pct(row["max_relative_drawdown_vs_rsc"]),
                "Strict": "yes" if row["strict_overlay_pass"] else "no",
            }
        )
    return rows


def underwater_rows(frame: pd.DataFrame, *, kind: str | None = None, limit: int = 20) -> list[dict[str, object]]:
    subset = frame if kind is None else frame[frame["candidate_type"] == kind]
    subset = subset.sort_values("cagr_spread_vs_rsc", ascending=False).head(limit)
    rows: list[dict[str, object]] = []
    for _, row in subset.iterrows():
        rows.append(
            {
                "Candidate": row["candidate_id"],
                "UW days": fmt_pct(row["time_underwater_pct"]),
                "Max recovery": int(row["max_recovery_days"]),
                "RSC max recovery": int(row["rsc_max_recovery_days_same_window"]),
                "Days below RSC": fmt_pct(row["pct_days_below_rsc"]),
                "Longest below RSC": int(row["longest_below_rsc_days"]),
                "Max deficit": fmt_pct(row["max_deficit_vs_rsc"]),
                "Est turnover/y": fmt_num(row["estimated_total_turnover_per_year"], 2),
            }
        )
    return rows


def source_rows(satellites: list[Satellite]) -> list[dict[str, object]]:
    rows = [
        {
            "Series": "RSC core",
            "Source": str(RSC_SLEEVE_RETURNS.relative_to(REPO_ROOT)),
            "Use": "core baseline",
            "Note": "Monthly `35/40/25` rebuild from `GDESIM/RSSTSIM/ZROZSIM` sleeve returns.",
        },
        {
            "Series": "Saved RSC curve",
            "Source": str(RSC_FULL_EQUITY.relative_to(REPO_ROOT)),
            "Use": "audit only",
            "Note": f"Column `{RSC_CORE_COLUMN}` checks rebuilt core drift against the prior saved curve.",
        }
    ]
    for sat in satellites:
        rows.append({"Series": sat.name, "Source": sat.source, "Use": "satellite", "Note": sat.notes})
    return rows


def write_report(
    results: pd.DataFrame,
    plot_rows: list[dict[str, str]],
    satellites: list[Satellite],
    audit: dict[str, float],
) -> None:
    overlays = results[results["candidate_type"] == "overlay"]
    strict = overlays[overlays["strict_overlay_pass"]]
    top_cagr = overlays.sort_values("cagr_spread_vs_rsc", ascending=False).iloc[0]
    top_strict = strict.sort_values("cagr_spread_vs_rsc", ascending=False).iloc[0] if not strict.empty else None
    core = results[results["candidate_id"] == "rsc_core"].iloc[0]
    sections = [
        "# Phase 5 - RSC + LRS/T3d Overlay Rebuilt-Sleeve Diagnostic\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change.\n\n"
        "This phase answers whether the failed standalone LRS line deserves a smaller role as a satellite around the RSC-US `35/40/25` core. The RSC core is now rebuilt from `GDESIM`, `ZROZSIM`, and an `RSSTSIM` tracking proxy in `studies/return_stacked_core/us_core/series/return_stacked_core_sleeve_returns.parquet`. The current `RSSTSIM` follows the user-provided Testfol.io payload: `SPYSIM + 70% DBMFSIM + 30% KMLMSIM - (CASHX + 200 bps/year)`, equivalent to `100% SPY + 70% DBMF + 30% KMLM - 100% CASHX?E=-2` `[testing_tuning, p.327-335]`, `[risk_parity, p.80-81]`, `[systematic_trading, p.185-188]`.\n\n"
        "Monthly fixed-weight rebalancing is used for both the RSC sleeve mix and the core/satellite allocation control, with turnover reported separately; it is not a deployable account-level tax simulation `[systematic_trading, p.185-188]`. Local LRS satellites are after-tax under the annual DARF model; the RSC core remains a gross/static portfolio diagnostic.\n\n"
        "## Executive Conclusion\n\n"
        f"Rebuilt-sleeve overlays passing the strict RSC-improvement screen: **{len(strict)}/{len(overlays)}**. Strict means higher CAGR than same-window RSC, no worse MDD, no worse Calmar, no worse time underwater and no worse max recovery time. "
        + (
            f"The best strict overlay is `{top_strict['candidate_id']}` with CAGR {fmt_pct(top_strict['cagr'])} vs same-window RSC {fmt_pct(top_strict['rsc_cagr_same_window'])}, MDD {fmt_pct(top_strict['mdd'])} vs RSC {fmt_pct(top_strict['rsc_mdd_same_window'])}, and Calmar {fmt_num(top_strict['calmar'])} vs RSC {fmt_num(top_strict['rsc_calmar_same_window'])}. "
            if top_strict is not None
            else "No overlay cleared the strict screen. "
        )
        + f"The highest-CAGR overlay overall is `{top_cagr['candidate_id']}` with CAGR {fmt_pct(top_cagr['cagr'])} but MDD {fmt_pct(top_cagr['mdd'])}, so it is a growth-for-drawdown trade-off rather than a strict improvement. "
        f"Baseline RSC in this diagnostic window is CAGR {fmt_pct(core['cagr'])}, MDD {fmt_pct(core['mdd'])}, Sharpe {fmt_num(core['sharpe'])}, Calmar {fmt_num(core['calmar'])}.\n\n"
        "Interpretation rule: strict rebuilt-sleeve passes are diagnostic leads only. They do not reverse the Phase 4 LRS gate failure and would need account-level tax/friction plus mandate gates with honest accumulated trial accounting before any promotion claim `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.\n\n"
        "## Source And Rules\n\n"
        "| Item | Value |\n|---|---|\n"
        f"| RSC core | `{RSC_SLEEVE_RETURNS.relative_to(REPO_ROOT)}` with weights `35% GDESIM / 40% RSSTSIM / 25% ZROZSIM` |\n"
        "| RSSTSIM formula | `SPYSIM + 0.70*DBMFSIM + 0.30*KMLMSIM - (CASHX + 0.0200/252)`; local proxy for `CASHX?E=-2` financing. |\n"
        f"| Saved RSC audit | terminal ratio `{audit['terminal_ratio']:.6f}`, CAGR diff `{audit['cagr_diff'] * 100:.3f}pp`, MDD diff `{audit['mdd_diff'] * 100:.3f}pp`, max relative deviation `{audit['max_abs_relative_deviation'] * 100:.3f}%` vs `{RSC_FULL_EQUITY.relative_to(REPO_ROOT)}` column `{RSC_CORE_COLUMN}` |\n"
        f"| T3d-K2 source | `{LETF_LAB_PHASE12_EQUITY}` column `{T3D_COLUMN}` if present |\n"
        "| Local LRS satellites | Rebuilt from Phase 4 headline geometries in `lrs/` |\n"
        "| Overlay weights | `90/10`, `80/20`, `70/30` RSC/satellite |\n"
        "| Overlay rebalance | Monthly fixed-weight diagnostic |\n"
        "| Strict screen | CAGR up; MDD, Calmar, underwater and recovery no worse than same-window RSC |\n"
        "| Promotion status | None; diagnostic only, no gates, no mandate change |\n\n"
    ]
    sections.append("## Series Sources\n\n" + md_table(source_rows(satellites), ["Series", "Source", "Use", "Note"]))
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    sections.append(
        "## Overlay Ranking\n\n"
        + md_table(
            candidate_rows(results, kind="overlay", limit=20),
            ["Candidate", "Type", "CAGR", "MDD", "Sharpe", "Calmar", "CAGR vs RSC", "MDD vs RSC", "Terminal/RSC", "Rel DD", "Strict"],
        )
    )
    sections.append(
        "## Underwater And Relative Pain\n\n"
        + md_table(
            underwater_rows(results, kind="overlay", limit=20),
            ["Candidate", "UW days", "Max recovery", "RSC max recovery", "Days below RSC", "Longest below RSC", "Max deficit", "Est turnover/y"],
        )
    )
    sections.append(
        "## References And Standalone Satellites\n\n"
        + md_table(
            candidate_rows(results[results["candidate_type"].isin(["core", "satellite_reference"])], limit=10),
            ["Candidate", "Type", "CAGR", "MDD", "Sharpe", "Calmar", "CAGR vs RSC", "MDD vs RSC", "Terminal/RSC", "Rel DD", "Strict"],
        )
    )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Did any rebuilt-sleeve overlay strictly improve RSC? | {'Yes' if len(strict) else 'No'} ({len(strict)}/{len(overlays)}). |\n"
        "| Did this reconstruct RSC sleeves? | Yes, inside repo provenance: `GDESIM/RSSTSIM/ZROZSIM` monthly `35/40/25`. `RSSTSIM` is a documented RSST tracking proxy, not a live ETF backfill. |\n"
        "| Did this run mandate gates? | No. This is a small diagnostic overlay screen only. |\n"
        "| Is anything deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |\n\n"
        "Next engineering step, if further precision is desired: add account-level tax/friction handling and then run the mandate validation gates with honest accumulated trial accounting.\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    results, return_map, satellites, audit = build_candidates()
    results.to_csv(CSV, index=False)
    plot_rows = make_plots(return_map, results)
    write_report(results, plot_rows, satellites, audit)
    overlays = results[results["candidate_type"] == "overlay"]
    n_strict = int(overlays["strict_overlay_pass"].sum())
    top = overlays.sort_values("cagr_spread_vs_rsc", ascending=False).iloc[0]
    print(f"Phase 5 rebuilt-sleeve diagnostic: {len(overlays)} overlays; strict pass {n_strict}/{len(overlays)}")
    print(
        f"  top CAGR overlay {top['candidate_id']}: CAGR {top['cagr']:.4f}, "
        f"MDD {top['mdd']:.4f}, strict={bool(top['strict_overlay_pass'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
