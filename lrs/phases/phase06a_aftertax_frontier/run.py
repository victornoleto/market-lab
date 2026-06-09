"""Phase 6A - after-tax frontier of static-core x LRS-satellite mixes (DIAGNOSTIC).

Research-only. REVISED 2026-06-09 after the user corrected the tax premise:
static portfolios rebalance with new contributions (aportes), not with sells,
so the core realizes no gains until final liquidation and pays no intermediate
DARF. Tax model per leg: core = gross monthly rebalancing + 15% DARF at final
liquidation only; satellites = full `AnnualDarfEngine` (the weekly rotation
genuinely sells); B&H benchmarks = final-liquidation DARF only; mixes =
two-account convention with contribution-funded (tax-free) re-truing,
leg-level final tax approximation disclosed in `tax_method`
`[testing_tuning, p.327-335]`.

Part 2 adds the user's real-world setup: 10k start + 1k/month contributions,
each month buying ONLY the single most-underweight component (minimal-trades
policy), no sells, final-liquidation tax on gross components
`[systematic_trading, p.185-188]`. Benchmarks: RSC-US 35/40/25, SSOSIM B&H,
SPYSIM B&H on the common 2000+ window. The screen is utility-based (ranked
decision table), NOT strict dominance, and promotes nothing
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.
+21 to the n_trials ledger -> cumulative lineage 4005 (Part 2 adds 0).
"""
from __future__ import annotations

from pathlib import Path
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
    load_price_frame,
    md_table,
    metrics_from_returns,
    simulate_weight_frame,
)
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from lrs.phases.phase05_rsc_overlay_proxy.run import (  # noqa: E402
    first_monthly_bar_mask,
    load_rsc_sleeve_returns,
    monthly_rebalanced_returns,
    read_equity_curve,
    returns_from_equity,
    underwater_stats,
)
from lrs.phases.phase05_rsc_overlay_proxy import run as phase05  # noqa: E402
from lrs.phases.phase06b_vol_target_continuous.run import (  # noqa: E402
    continuous_leverage_series,
    desired_targets_continuous,
)
from lrs.phases.phase06d_inverse_sleeve.run import crisis_window_stats  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase06a_aftertax_frontier.csv"
CSV_CONTRIB = RESULTS / "phase06a_contribution_sim.csv"

RSC_WEIGHTS = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}
MIX_WEIGHTS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
MDD_FLOOR = -0.50
N_TRIALS_ADDED = 21  # 18 mixes + 3 standalone satellite references on this window

DARF_RATE = 0.15  # Lei 14.754/2023, realized net gains
START_EQUITY = 10_000.0
MONTHLY_CONTRIBUTION = 1_000.0


# --------------------------------------------------------------------------- tax


def final_liquidation_tax(returns: pd.Series, rate: float = DARF_RATE) -> pd.Series:
    """Apply DARF once at final liquidation (contribution-rebalanced leg / B&H).

    A static leg rebalanced with new contributions realizes no gains along the
    way; the only taxable event is the final sale. The last daily return is
    adjusted so the terminal equity is net of 15% on the cumulative gain
    (losses pay nothing).
    """
    clean = returns.dropna().astype(float)
    if clean.empty:
        return clean
    equity = (1.0 + clean).cumprod()
    terminal = float(equity.iloc[-1])
    net_terminal = terminal - rate * max(0.0, terminal - 1.0)
    adjusted = clean.copy()
    prev = float(equity.iloc[-2]) if len(equity) > 1 else 1.0
    adjusted.iloc[-1] = net_terminal / prev - 1.0 if prev > 0 else 0.0
    return adjusted


# --------------------------------------------------------------------------- satellites


def lrs_weight_frame_binary(
    branch_key: str, target_leverage: float, risk_off_name: str, vol_name: str, lag: int
) -> pd.DataFrame:
    """Daily executable weights of a committed binary headline base (Phase 2/4)."""
    context = phase04.build_context(phase04.BRANCHES[branch_key])
    risk_off = next(r for r in phase04.RISK_OFF_SPECS if r["name"] == risk_off_name)
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == vol_name)
    risk_off_weights = clean_weights(dict(risk_off["weights"]))  # type: ignore[arg-type]
    risk_on = phase04.target_leverage_weights(context.branch, target_leverage)
    signal = context.sma_signal & phase04.vol_gate(context, vol_spec)
    assets = sorted(set(risk_on) | set(risk_off_weights) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=context.returns.index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(signal, risk_on.get(asset, 0.0), risk_off_weights.get(asset, 0.0))
    weights, _ = build_weekly_lagged_weights(desired, lag_days=lag, risk_on_weights=risk_on)
    return weights


def lrs_weight_frame_voltarget(
    branch_key: str, sigma_target: float, rv_window: int, l_max: float, risk_off_name: str, lag: int
) -> pd.DataFrame:
    """Daily executable weights of the Phase 6B continuous vol-target winner."""
    context = phase04.build_context(phase04.BRANCHES[branch_key])
    risk_off = next(r for r in phase04.RISK_OFF_SPECS if r["name"] == risk_off_name)
    risk_off_weights = clean_weights(dict(risk_off["weights"]))  # type: ignore[arg-type]
    leverage = continuous_leverage_series(
        context.returns[context.branch["underlying"]], rv_window, sigma_target, l_max
    )
    desired = desired_targets_continuous(context, leverage, risk_off_weights)
    weights, _ = build_weekly_lagged_weights(desired, lag_days=lag)
    return weights


SATELLITE_SPECS: list[dict[str, object]] = [
    {
        "name": "lrs_spy_headline",
        "label": "SPY L2.00 binary (Phase 2/4 headline, lag 3)",
        "builder": lambda: lrs_weight_frame_binary("SPY", 2.00, "50 ZROZ / 25 GLD / 25 CASH", "RV21 <= 30%", 3),
    },
    {
        "name": "lrs_qqq_voltarget",
        "label": "QQQ vol-target sigma40/RV21/lag1 (Phase 6B winner)",
        "builder": lambda: lrs_weight_frame_voltarget("QQQ", 0.40, 21, 1.75, "40 ZROZ / 40 GLD / 20 IEF", 1),
    },
]


def build_components_frame() -> pd.DataFrame:
    """Core sleeves from the RSC parquet + everything else from the cache.

    ZROZSIM is identical across the two sources (verified max abs diff 0), so a
    single column serves both the core and the satellite risk-off sleeves.
    """
    sleeves = load_rsc_sleeve_returns()  # GDESIM / RSSTSIM / ZROZSIM, 2000+
    cache_assets = [
        "CASHX", "GLDSIM", "IEFSIM", "ZROZSIM",
        "SPYSIM", "SSOSIM", "UPROSIM", "QQQSIM", "QLDSIM", "TQQQSIM",
    ]
    cache_returns = load_price_frame(cache_assets).pct_change().dropna()
    combined = pd.concat(
        [sleeves[["GDESIM", "RSSTSIM"]], cache_returns], axis=1, sort=False
    ).dropna()
    return combined


# --------------------------------------------------------------------------- part 1


def evaluate_row(
    *,
    candidate_id: str,
    candidate_type: str,
    satellite: str,
    satellite_share: float,
    tax_method: str,
    returns: pd.Series,
    summary: dict[str, float],
) -> dict[str, object]:
    metrics = metrics_from_returns(returns)
    underwater = underwater_stats(returns)
    return {
        "candidate_id": candidate_id,
        "candidate_type": candidate_type,
        "satellite": satellite,
        "satellite_share": satellite_share,
        "tax_method": tax_method,
        "start": metrics.start,
        "end": metrics.end,
        "years": metrics.years,
        "cagr": metrics.cagr,
        "mdd": metrics.mdd,
        "sharpe": metrics.sharpe,
        "sortino": metrics.sortino,
        "calmar": metrics.calmar,
        "terminal": metrics.terminal,
        "constraint_ok": bool(metrics.mdd >= MDD_FLOOR),
        "time_underwater_pct": underwater["time_underwater_pct"],
        "max_recovery_days": underwater["max_recovery_days"],
        "turnover_per_year": float(summary.get("turnover_per_year", float("nan"))),
        "total_tax_paid_pct_initial": float(summary.get("total_tax_paid_pct_initial", float("nan"))),
        **crisis_window_stats(returns),
    }


def add_benchmark_spreads(frame: pd.DataFrame) -> pd.DataFrame:
    for bench_id, prefix in (("bench_rsc", "rsc"), ("bench_sso", "sso"), ("bench_spy", "spy")):
        bench = frame[frame["candidate_id"] == bench_id].iloc[0]
        frame[f"cagr_spread_vs_{prefix}"] = frame["cagr"] - bench["cagr"]
        frame[f"mdd_spread_vs_{prefix}"] = frame["mdd"] - bench["mdd"]
        frame[f"calmar_spread_vs_{prefix}"] = frame["calmar"] - bench["calmar"]
    return frame


def build_all(components: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.Series], dict[str, pd.Series]]:
    index = pd.DatetimeIndex(components.index)
    rows: list[dict[str, object]] = []
    return_map: dict[str, pd.Series] = {}
    satellite_series: dict[str, pd.Series] = {}

    # Benchmark 1: RSC core - gross monthly rebalance (contribution-funded),
    # DARF only at final liquidation.
    core_gross, core_summary = monthly_rebalanced_returns(
        components[list(RSC_WEIGHTS)], RSC_WEIGHTS, name="rsc_core_gross"
    )
    core_leg = final_liquidation_tax(core_gross)
    return_map["bench_rsc"] = core_leg
    rows.append(
        evaluate_row(
            candidate_id="bench_rsc",
            candidate_type="benchmark",
            satellite="none",
            satellite_share=0.0,
            tax_method="final_darf_only",
            returns=core_leg,
            summary={"turnover_per_year": core_summary.get("rebalance_turnover_per_year", float("nan"))},
        )
    )

    # Benchmarks 2 and 3: taxed buy-and-hold (final liquidation only).
    for bench_id, asset in (("bench_sso", "SSOSIM"), ("bench_spy", "SPYSIM")):
        taxed = final_liquidation_tax(components[asset])
        return_map[bench_id] = taxed
        rows.append(
            evaluate_row(
                candidate_id=bench_id,
                candidate_type="benchmark",
                satellite="none",
                satellite_share=0.0,
                tax_method="final_darf_only",
                returns=taxed,
                summary={},
            )
        )

    # Local satellites: weekly rotation genuinely sells -> full annual engine.
    for spec in SATELLITE_SPECS:
        weights = spec["builder"]()  # type: ignore[operator]
        sat_name = str(spec["name"])
        sat_returns, sat_summary = simulate_weight_frame(
            components, weights.reindex(index).fillna(0.0), taxable=True
        )
        satellite_series[sat_name] = sat_returns
        return_map[sat_name] = sat_returns
        rows.append(
            evaluate_row(
                candidate_id=sat_name,
                candidate_type="satellite_reference",
                satellite=sat_name,
                satellite_share=1.0,
                tax_method="annual_darf_engine",
                returns=sat_returns,
                summary=sat_summary,
            )
        )

    # T3d-K2 saved curve (already after-tax br_lei).
    if phase05.LETF_LAB_PHASE12_EQUITY.exists():
        t3d_equity = read_equity_curve(phase05.LETF_LAB_PHASE12_EQUITY, phase05.T3D_COLUMN)
        t3d_returns = returns_from_equity(t3d_equity, "t3d_k2_saved").reindex(index).dropna()
        satellite_series["t3d_k2_saved"] = t3d_returns
        return_map["t3d_k2_saved"] = t3d_returns
        rows.append(
            evaluate_row(
                candidate_id="t3d_k2_saved",
                candidate_type="satellite_reference",
                satellite="t3d_k2_saved",
                satellite_share=1.0,
                tax_method="saved_after_tax_curve",
                returns=t3d_returns,
                summary={},
            )
        )

    # Mixes: two-account convention, contribution-funded re-truing (tax-free).
    for sat_name, sat_returns in satellite_series.items():
        aligned = pd.concat({"core": core_leg, "sat": sat_returns}, axis=1, sort=False).dropna()
        for share in MIX_WEIGHTS:
            candidate_id = f"mix_{sat_name}_{int(share * 100):02d}"
            combined, summary = monthly_rebalanced_returns(
                aligned, {"core": 1.0 - share, "sat": share}, name=candidate_id
            )
            return_map[candidate_id] = combined
            rows.append(
                evaluate_row(
                    candidate_id=candidate_id,
                    candidate_type="mix",
                    satellite=sat_name,
                    satellite_share=share,
                    tax_method="two_account_contrib",
                    returns=combined,
                    summary={"turnover_per_year": summary.get("rebalance_turnover_per_year", float("nan"))},
                )
            )

    frame = add_benchmark_spreads(pd.DataFrame(rows))
    return frame, return_map, satellite_series


# --------------------------------------------------------------------------- part 2


def pick_most_underweight(targets: dict[str, float], values: dict[str, float]) -> str:
    """The single component whose current weight lags its target the most (pp)."""
    total = sum(values.values())
    if total <= 0:
        return max(targets, key=lambda c: targets[c])
    return max(targets, key=lambda c: targets[c] - values[c] / total)


def annualized_irr(
    flow_days: list[float], flow_amounts: list[float], terminal_day: float, terminal_value: float
) -> float:
    """Money-weighted annual return via bisection on the XNPV equation."""

    def npv(rate: float) -> float:
        acc = 0.0
        for day, amount in zip(flow_days, flow_amounts):
            acc += amount / (1.0 + rate) ** (day / 365.25)
        return acc - terminal_value / (1.0 + rate) ** (terminal_day / 365.25)

    low, high = -0.95, 10.0
    f_low, f_high = npv(low), npv(high)
    if f_low * f_high > 0:
        return float("nan")
    for _ in range(200):
        mid = 0.5 * (low + high)
        f_mid = npv(mid)
        if abs(f_mid) < 1e-9:
            return mid
        if f_low * f_mid <= 0:
            high, f_high = mid, f_mid
        else:
            low, f_low = mid, f_mid
    return 0.5 * (low + high)


def contribution_simulation(
    component_returns: pd.DataFrame,
    targets: dict[str, float],
    taxable_components: set[str],
    *,
    start_equity: float = START_EQUITY,
    contribution: float = MONTHLY_CONTRIBUTION,
    rate: float = DARF_RATE,
) -> dict[str, float]:
    """10k start + 1k/month, each month buying ONLY the most-underweight
    component; no sells; final-liquidation DARF on gross components only
    `[systematic_trading, p.185-188]`."""
    clean = component_returns[list(targets)].dropna().astype(float)
    index = pd.DatetimeIndex(clean.index)
    monthly = first_monthly_bar_mask(index).to_numpy(dtype=bool)
    returns_arr = clean.to_numpy(dtype=float)
    names = list(targets)

    values = {c: start_equity * targets[c] for c in names}
    basis = dict(values)
    contributed = start_equity
    t0 = index[0]
    flow_days = [0.0]
    flow_amounts = [start_equity]
    equity_path = np.empty(len(index))
    weight_dev_acc = 0.0

    for i in range(len(index)):
        if i > 0 and monthly[i]:
            pick = pick_most_underweight(targets, values)
            values[pick] += contribution
            basis[pick] += contribution
            contributed += contribution
            flow_days.append(float((index[i] - t0).days))
            flow_amounts.append(contribution)
        for j, name in enumerate(names):
            values[name] *= 1.0 + returns_arr[i, j]
        total = sum(values.values())
        equity_path[i] = total
        weight_dev_acc += sum(abs(values[c] / total - targets[c]) for c in names) / len(names)

    terminal_gross = float(sum(values.values()))
    tax = sum(rate * max(0.0, values[c] - basis[c]) for c in names if c in taxable_components)
    terminal_net = terminal_gross - tax
    path = pd.Series(equity_path, index=index)
    drawdown = path / path.cummax() - 1.0
    terminal_day = float((index[-1] - t0).days)
    return {
        "terminal_net": terminal_net,
        "terminal_gross": terminal_gross,
        "final_tax": float(tax),
        "contributed": float(contributed),
        "wealth_ratio": terminal_net / contributed if contributed > 0 else float("nan"),
        "irr_annual": annualized_irr(flow_days, flow_amounts, terminal_day, terminal_net),
        "path_mdd": float(drawdown.min()),
        "mean_abs_weight_dev": float(weight_dev_acc / len(index)),
        "n_contributions": float(len(flow_amounts) - 1),
    }


def build_contribution_table(
    components: pd.DataFrame, satellite_series: dict[str, pd.Series]
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    def run_candidate(candidate_id: str, satellite: str, share: float,
                      frame: pd.DataFrame, targets: dict[str, float], taxable: set[str]) -> None:
        stats = contribution_simulation(frame, targets, taxable)
        rows.append({"candidate_id": candidate_id, "satellite": satellite, "satellite_share": share, **stats})

    sleeves = components[list(RSC_WEIGHTS)]
    run_candidate("bench_rsc", "none", 0.0, sleeves, dict(RSC_WEIGHTS), set(RSC_WEIGHTS))
    for bench_id, asset in (("bench_sso", "SSOSIM"), ("bench_spy", "SPYSIM")):
        run_candidate(bench_id, "none", 0.0, components[[asset]], {asset: 1.0}, {asset})

    for sat_name, sat_returns in satellite_series.items():
        frame = pd.concat([sleeves, sat_returns.rename(sat_name)], axis=1, sort=False).dropna()
        for share in MIX_WEIGHTS:
            targets = {c: (1.0 - share) * w for c, w in RSC_WEIGHTS.items()}
            targets[sat_name] = share
            run_candidate(
                f"mix_{sat_name}_{int(share * 100):02d}", sat_name, share,
                frame, targets, set(RSC_WEIGHTS),
            )
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- plots


def plot_frontier(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6.5))
    colors = {"lrs_spy_headline": "tab:blue", "lrs_qqq_voltarget": "tab:orange", "t3d_k2_saved": "tab:purple"}
    mixes = frame[frame["candidate_type"] == "mix"]
    for sat, sub in mixes.groupby("satellite"):
        ax.scatter(
            sub["mdd"] * 100.0, sub["cagr"] * 100.0,
            s=20 + 200 * sub["satellite_share"], alpha=0.75,
            color=colors.get(str(sat)), label=f"mix {sat}",
        )
    marks = {"bench_rsc": ("*", "black", "RSC-US 35/40/25"), "bench_sso": ("^", "darkred", "SSO B&H"), "bench_spy": ("s", "gray", "SPY B&H")}
    for bench_id, (marker, color, label) in marks.items():
        b = frame[frame["candidate_id"] == bench_id].iloc[0]
        ax.scatter([b["mdd"] * 100.0], [b["cagr"] * 100.0], marker=marker, s=170, color=color, label=label, zorder=5)
    ax.axvline(MDD_FLOOR * 100.0, color="red", linestyle="--", linewidth=1.0, label="MDD -50% constraint")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.set_title("Phase 6A (revised tax): after-tax frontier, mixes vs benchmarks (2000+)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = PLOTS / "phase06a_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _best_mix_ids(frame: pd.DataFrame) -> list[str]:
    mixes = frame[(frame["candidate_type"] == "mix") & frame["constraint_ok"]]
    out: list[str] = []
    for _sat, sub in mixes.groupby("satellite"):
        out.append(str(sub.sort_values(["calmar", "cagr"], ascending=False).iloc[0]["candidate_id"]))
    return out


def plot_equity(frame: pd.DataFrame, return_map: dict[str, pd.Series]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ids = ["bench_rsc", "bench_sso", "bench_spy", *_best_mix_ids(frame)]
    aligned = pd.concat({i: equity_curve(return_map[i]) for i in ids}, axis=1, sort=False).dropna()
    fig, ax = plt.subplots(figsize=(11.5, 6))
    aligned.plot(ax=ax, logy=True, linewidth=1.1)
    ax.set_title("Phase 6A: after-tax equity, benchmarks vs best constraint-passing mixes")
    ax.set_ylabel("Growth of $1 (after-tax)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase06a_equity.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_underwater(frame: pd.DataFrame, return_map: dict[str, pd.Series]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ids = ["bench_rsc", "bench_sso", *_best_mix_ids(frame)]
    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    for i in ids:
        eq = equity_curve(return_map[i])
        dd = (eq / eq.cummax() - 1.0) * 100.0
        ax.plot(dd.index, dd.to_numpy(dtype=float), linewidth=0.9, label=i)
    ax.axhline(MDD_FLOOR * 100.0, color="red", linestyle="--", linewidth=1.0)
    ax.set_title("Phase 6A: underwater chart")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = PLOTS / "phase06a_underwater.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_crisis_bars(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ids = ["bench_rsc", "bench_sso", "bench_spy", *_best_mix_ids(frame)]
    crisis_cols = [c for c in frame.columns if c.startswith("crisis_") and c.endswith("_ret")]
    labels = [c.replace("crisis_", "").replace("_ret", "") for c in crisis_cols]
    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(len(crisis_cols))
    width = 0.8 / len(ids)
    for k, candidate_id in enumerate(ids):
        row = frame[frame["candidate_id"] == candidate_id].iloc[0]
        vals = [float(row[c]) * 100.0 for c in crisis_cols]
        ax.bar(x + (k - len(ids) / 2 + 0.5) * width, vals, width=width, label=candidate_id)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Total return in window (%)")
    ax.set_title("Phase 6A: pre-registered crisis windows")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = PLOTS / "phase06a_crisis_bars.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_contribution_terminal(contrib: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sub = contrib.sort_values("irr_annual", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 0.42 * len(sub) + 1.8))
    colors = ["black" if str(c).startswith("bench") else "tab:blue" for c in sub["candidate_id"]]
    ax.barh(sub["candidate_id"], sub["irr_annual"] * 100.0, color=colors)
    ax.set_xlabel("Money-weighted annual return / IRR (%) - net of final DARF")
    ax.set_title("Phase 6A part 2: 10k start + 1k/month, buy-most-underweight, no sells")
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase06a_contribution_irr.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------- report


def ranked_table(frame: pd.DataFrame, *, constraint_only: bool) -> str:
    rows_src = frame[frame["candidate_type"].isin(["mix", "benchmark"])]
    if constraint_only:
        rows_src = rows_src[rows_src["constraint_ok"]]
    rows_src = rows_src.sort_values(["calmar", "cagr"], ascending=False)
    rows = [
        {
            "Candidate": r["candidate_id"],
            "w": fmt_pct(r["satellite_share"], 0),
            "CAGR": fmt_pct(r["cagr"]),
            "MDD": fmt_pct(r["mdd"]),
            "Sharpe": fmt_num(r["sharpe"]),
            "Calmar": fmt_num(r["calmar"]),
            "UW": fmt_pct(r["time_underwater_pct"], 0),
            "Recovery": int(r["max_recovery_days"]),
            "vs RSC CAGR": fmt_pp(r["cagr_spread_vs_rsc"]),
            "vs RSC MDD": fmt_pp(r["mdd_spread_vs_rsc"]),
            "vs SSO CAGR": fmt_pp(r["cagr_spread_vs_sso"]),
            "vs SPY CAGR": fmt_pp(r["cagr_spread_vs_spy"]),
            "Tax": r["tax_method"],
            "OK": "yes" if r["constraint_ok"] else "NO",
        }
        for _, r in rows_src.iterrows()
    ]
    return md_table(
        rows,
        ["Candidate", "w", "CAGR", "MDD", "Sharpe", "Calmar", "UW", "Recovery",
         "vs RSC CAGR", "vs RSC MDD", "vs SSO CAGR", "vs SPY CAGR", "Tax", "OK"],
    )


def contribution_table(contrib: pd.DataFrame) -> str:
    sub = contrib.sort_values("irr_annual", ascending=False)
    rows = [
        {
            "Candidate": r["candidate_id"],
            "w": fmt_pct(r["satellite_share"], 0),
            "Terminal net": f"${r['terminal_net']:,.0f}",
            "Contributed": f"${r['contributed']:,.0f}",
            "Wealth ratio": fmt_x(r["wealth_ratio"]),
            "IRR (annual)": fmt_pct(r["irr_annual"]),
            "Final tax": f"${r['final_tax']:,.0f}",
            "Path MDD*": fmt_pct(r["path_mdd"]),
            "Weight dev": fmt_pct(r["mean_abs_weight_dev"]),
        }
        for _, r in sub.iterrows()
    ]
    return md_table(
        rows,
        ["Candidate", "w", "Terminal net", "Contributed", "Wealth ratio", "IRR (annual)",
         "Final tax", "Path MDD*", "Weight dev"],
    )


def crisis_table(frame: pd.DataFrame) -> str:
    ids = ["bench_rsc", "bench_sso", "bench_spy", *_best_mix_ids(frame)]
    rows = []
    for candidate_id in ids:
        r = frame[frame["candidate_id"] == candidate_id].iloc[0]
        rows.append(
            {
                "Candidate": candidate_id,
                "Dotcom ret/MDD": f"{fmt_pct(r['crisis_dotcom_ret'])} / {fmt_pct(r['crisis_dotcom_mdd'])}",
                "GFC ret/MDD": f"{fmt_pct(r['crisis_gfc_ret'])} / {fmt_pct(r['crisis_gfc_mdd'])}",
                "COVID ret/MDD": f"{fmt_pct(r['crisis_covid_ret'])} / {fmt_pct(r['crisis_covid_mdd'])}",
                "2022 ret/MDD": f"{fmt_pct(r['crisis_2022_ret'])} / {fmt_pct(r['crisis_2022_mdd'])}",
            }
        )
    return md_table(rows, ["Candidate", "Dotcom ret/MDD", "GFC ret/MDD", "COVID ret/MDD", "2022 ret/MDD"])


def write_report(frame: pd.DataFrame, contrib: pd.DataFrame, plot_rows: list[dict[str, str]]) -> None:
    bench_rsc = frame[frame["candidate_id"] == "bench_rsc"].iloc[0]
    bench_sso = frame[frame["candidate_id"] == "bench_sso"].iloc[0]
    bench_spy = frame[frame["candidate_id"] == "bench_spy"].iloc[0]
    mixes_ok = frame[(frame["candidate_type"] == "mix") & frame["constraint_ok"]]
    better_than_rsc = mixes_ok[
        (mixes_ok["cagr_spread_vs_rsc"] > 0) & (mixes_ok["calmar_spread_vs_rsc"] > 0)
    ]
    top = mixes_ok.sort_values(["calmar", "cagr"], ascending=False).iloc[0] if not mixes_ok.empty else None
    contrib_sorted = contrib.sort_values("irr_annual", ascending=False)
    contrib_top = contrib_sorted.iloc[0]
    contrib_rsc = contrib[contrib["candidate_id"] == "bench_rsc"].iloc[0]
    sections = [
        "# Phase 6A - After-Tax Frontier vs 3 Benchmarks (DIAGNOSTIC, REVISED)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.\n\n"
        "REVISION (2026-06-09, user correction): static portfolios rebalance with new contributions (aportes), not with sells - so the core pays NO intermediate DARF; only final liquidation is taxed. Tax model per leg: core = gross monthly rebalance + final 15% DARF; LRS satellites = full `AnnualDarfEngine` (the weekly rotation genuinely sells); B&H benchmarks = final DARF only; mixes = two-account convention with contribution-funded re-truing (`tax_method` column) `[testing_tuning, p.327-335]`. Part 2 simulates the user's real-world setup: 10k start + 1k/month, each month buying ONLY the most-underweight component (minimal trades), no sells, final DARF on gross components `[systematic_trading, p.185-188]`.\n\n"
        f"n_trials ledger: +{N_TRIALS_ADDED} (Part 2 re-prices the same mixes: +0) -> cumulative LRS lineage **4005** `[advances_fin_ml, p.273-275]`.\n\n"
        "## Executive Conclusion\n\n"
        f"Part 1 benchmarks (after-tax, {bench_rsc['start']}..{bench_rsc['end']}): RSC-US 35/40/25 CAGR {fmt_pct(bench_rsc['cagr'])} / MDD {fmt_pct(bench_rsc['mdd'])} / Calmar {fmt_num(bench_rsc['calmar'])}; SSO B&H {fmt_pct(bench_sso['cagr'])} / {fmt_pct(bench_sso['mdd'])} / {fmt_num(bench_sso['calmar'])}; SPY B&H {fmt_pct(bench_spy['cagr'])} / {fmt_pct(bench_spy['mdd'])} / {fmt_num(bench_spy['calmar'])}.\n\n"
        f"Constraint-passing mixes (MDD >= -50%): **{len(mixes_ok)}/{int((frame['candidate_type'] == 'mix').sum())}**. Mixes beating the RSC core on BOTH CAGR and Calmar: **{len(better_than_rsc)}**.\n\n"
        + (
            f"Part 1 top-ranked mix (Calmar, then CAGR): `{top['candidate_id']}` - CAGR {fmt_pct(top['cagr'])} ({fmt_pp(top['cagr_spread_vs_rsc'])} vs RSC), MDD {fmt_pct(top['mdd'])} ({fmt_pp(top['mdd_spread_vs_rsc'])} vs RSC), Calmar {fmt_num(top['calmar'])} (RSC {fmt_num(bench_rsc['calmar'])}).\n\n"
            if top is not None
            else "No mix passes the constraint.\n\n"
        )
        + f"Part 2 (contribution sim): top IRR `{contrib_top['candidate_id']}` at {fmt_pct(contrib_top['irr_annual'])} vs RSC {fmt_pct(contrib_rsc['irr_annual'])}; terminal net ${contrib_top['terminal_net']:,.0f} vs ${contrib_rsc['terminal_net']:,.0f} on ${contrib_rsc['contributed']:,.0f} contributed.\n\n"
        "This is a decision input for the user. Nothing here is promoted: every LRS satellite failed (or never ran) the mandate gate suite, and any promotion claim requires the full SS5 suite with honest n_trials >= 4005.\n\n",
    ]
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    sections.append("## Part 1 - Ranked Table (constraint-passing mixes + benchmarks)\n\n" + ranked_table(frame, constraint_only=True))
    sections.append("## Part 1 - Full Table (including constraint violators)\n\n" + ranked_table(frame, constraint_only=False))
    sections.append("## Part 1 - Crisis Windows (pre-registered dates)\n\n" + crisis_table(frame))
    sections.append(
        "## Part 2 - Contribution Simulation (10k + 1k/month, buy-most-underweight, no sells)\n\n"
        "*Path MDD is mechanically softened by monthly inflows - compare candidates against each other, not against Part 1 MDDs. Weight dev = mean absolute deviation from target weights (quality of buy-only rebalancing).\n\n"
        + contribution_table(contrib)
    )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Any mix with MDD >= -50% beating RSC on CAGR AND Calmar (Part 1)? | {'Yes' if len(better_than_rsc) else 'No'} ({len(better_than_rsc)}). |\n"
        f"| Best risk-adjusted candidate (Part 1)? | {top['candidate_id'] if top is not None else 'none'}. |\n"
        f"| Best money-weighted candidate (Part 2)? | {contrib_top['candidate_id']} ({fmt_pct(contrib_top['irr_annual'])} IRR). |\n"
        "| Did we promote anything? | No - decision table only; user chooses, gates still mandatory. |\n"
        "| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    components = build_components_frame()
    frame, return_map, satellite_series = build_all(components)
    frame.to_csv(CSV, index=False)
    contrib = build_contribution_table(components, satellite_series)
    contrib.to_csv(CSV_CONTRIB, index=False)
    plots = [
        ("Frontier (CAGR x MDD)", plot_frontier(frame)),
        ("After-tax equity", plot_equity(frame, return_map)),
        ("Underwater chart", plot_underwater(frame, return_map)),
        ("Crisis windows", plot_crisis_bars(frame)),
        ("Contribution sim IRR", plot_contribution_terminal(contrib)),
    ]
    plot_rows = [{"Plot": label, "File": f"[plots/{path.name}](plots/{path.name})"} for label, path in plots]
    write_report(frame, contrib, plot_rows)

    bench = frame[frame["candidate_id"] == "bench_rsc"].iloc[0]
    print(f"Phase 6A (revised): RSC after-tax CAGR {bench['cagr']:.2%} MDD {bench['mdd']:.2%} Calmar {bench['calmar']:.3f}")
    mixes_ok = frame[(frame["candidate_type"] == "mix") & frame["constraint_ok"]]
    for _, r in mixes_ok.sort_values(["calmar", "cagr"], ascending=False).head(5).iterrows():
        print(
            f"  P1 {r['candidate_id']:32s} CAGR {r['cagr']:.2%} MDD {r['mdd']:.2%} "
            f"Calmar {r['calmar']:.3f} (vs RSC CAGR {r['cagr_spread_vs_rsc']:+.2%})"
        )
    for _, r in contrib.sort_values("irr_annual", ascending=False).head(5).iterrows():
        print(
            f"  P2 {r['candidate_id']:32s} IRR {r['irr_annual']:.2%} terminal ${r['terminal_net']:,.0f} "
            f"(contributed ${r['contributed']:,.0f})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
