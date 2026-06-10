"""Phase 10 - drawdown-contingent leverage ladder, "buy the dip" (DIAGNOSTIC).

Research-only, user-directed (2026-06-10). Contrarian family: hold L_base most
of the time, escalate to L_dip when the underlying's drawdown crosses -d,
de-escalate on recovery (new ATH, or DD back to -d/2). Equity indices are
high-noise / countertrend-matching markets `[trading_systems_methods, p.13]`;
the deliberate bet AGAINST the repo's core thesis (dips = high-vol regimes
where leverage compounds worst `[leverage_for_the_long_run, p.7-9]`) is
recorded in the pre-registration. State hysteresis per
`[trading_systems_methods, p.383]`; honest lagging per `[testing_tuning,
p.327-335]`; caps per `[volatility_trading, p.139-140]`. Pre-registered grid:
144 rows (2 branches x 2 profiles x 3 triggers x 2 exits x 6 lags); +144 to
the n_trials ledger (4425 -> 4569). No deployment, no paper-trade label, no
mandate change.
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
    load_price_frame,
    md_table,
    metrics_from_returns,
    simulate_weight_frame,
)
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from lrs.phases.phase06b_vol_target_continuous.run import wf_beats  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase10_dip_leverage_ladder.csv"

PROFILES: list[dict[str, float]] = [
    {"l_base": 1.0, "l_dip": 2.0},
    {"l_base": 1.5, "l_dip": 3.0},
]
TRIGGERS = [0.10, 0.20, 0.30]
EXIT_RULES = ["ath", "half"]
LAGS = list(range(6))
N_TRIALS_ADDED = 2 * len(PROFILES) * len(TRIGGERS) * len(EXIT_RULES) * len(LAGS)  # 144
N_TRIALS_LEDGER_BEFORE = 4425
MDD_FLOOR = -0.50

BRANCH_SPECS: list[dict[str, object]] = [
    {"branch": "SPY", "headline_l": 2.00, "headline_off": "50 ZROZ / 25 GLD / 25 CASH", "headline_vol": "RV21 <= 30%", "headline_lag": 3},
    {"branch": "QQQ", "headline_l": 1.75, "headline_off": "40 ZROZ / 40 GLD / 20 IEF", "headline_vol": "RV63 <= 40%", "headline_lag": 0},
]


def dip_state(prices: pd.Series, trigger: float, exit_rule: str) -> pd.Series:
    """Boolean dip-state series (True = escalated), hysteresis + 1-bar lag.

    Enter `dip` when drawdown <= -trigger; leave per `ath` (new all-time high)
    or `half` (drawdown recovered to >= -trigger/2)
    `[trading_systems_methods, p.383]`. The raw state is computed on same-bar
    closes then `.shift(1)`-lagged `[testing_tuning, p.327-335]`.
    """
    if exit_rule not in EXIT_RULES:
        raise ValueError(f"unknown exit rule: {exit_rule}")
    px = prices.to_numpy(dtype=float)
    runmax = np.maximum.accumulate(px)
    dd = px / runmax - 1.0
    exit_level = 0.0 if exit_rule == "ath" else -trigger / 2.0
    state = np.zeros(len(px), dtype=bool)
    in_dip = False
    for i in range(len(px)):
        if in_dip:
            if dd[i] >= exit_level - 1e-12:
                in_dip = False
        elif dd[i] <= -trigger:
            in_dip = True
        state[i] = in_dip
    raw = pd.Series(state, index=prices.index)
    return raw.shift(1).fillna(False).astype(bool)


def leverage_weights(branch: dict[str, str], leverage: float) -> dict[str, float]:
    if leverage < 1.0:
        raise ValueError(f"leverage below 1.0 not in this phase's grid: {leverage}")
    return phase04.target_leverage_weights(branch, leverage)


def simulate_ladder(
    context: "phase04.BranchContext",
    state: pd.Series,
    l_base: float,
    l_dip: float,
    lag: int,
) -> tuple[pd.Series, dict[str, float], dict[str, float]]:
    """After-tax returns for the DD-state ladder (no SMA, no vol gate)."""
    base_w = leverage_weights(context.branch, l_base)
    dip_w = leverage_weights(context.branch, l_dip)
    assets = sorted(set(base_w) | set(dip_w) | {"CASHX"})
    index = context.returns.index
    s = state.reindex(index).fillna(False).to_numpy(dtype=bool)
    desired = pd.DataFrame(0.0, index=index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(s, dip_w.get(asset, 0.0), base_w.get(asset, 0.0))
    weights, weight_summary = build_weekly_lagged_weights(desired, lag_days=lag)
    taxed, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    return taxed, weight_summary, tax_summary


def constant_leverage_taxed(
    context: "phase04.BranchContext", leverage: float
) -> pd.Series:
    """Weekly-cadence constant-leverage benchmark on the same engine."""
    never = pd.Series(False, index=context.returns.index)
    taxed, _, _ = simulate_ladder(context, never, leverage, leverage, 0)
    return taxed


def branch_underlying_prices(context: "phase04.BranchContext") -> pd.Series:
    prices = load_price_frame(phase04.branch_assets(context.branch))
    return prices[context.branch["underlying"]].reindex(context.returns.index)


def evaluate_row(
    context: "phase04.BranchContext",
    branch_key: str,
    prices: pd.Series,
    profile: dict[str, float],
    trigger: float,
    exit_rule: str,
    lag: int,
) -> tuple[dict[str, object], pd.Series, pd.Series]:
    state = dip_state(prices, trigger, exit_rule)
    taxed, weight_summary, tax_summary = simulate_ladder(
        context, state, profile["l_base"], profile["l_dip"], lag
    )
    metrics = metrics_from_returns(taxed)
    beats, n_windows = wf_beats(taxed, context.underlying_taxed)
    episodes = int(((~state.shift(1).fillna(False)) & state).sum())
    row: dict[str, object] = {
        "config_type": "dip_ladder",
        "branch": branch_key,
        "l_base": profile["l_base"],
        "l_dip": profile["l_dip"],
        "trigger": trigger,
        "exit_rule": exit_rule,
        "lag_days": lag,
        "taxed_cagr": metrics.cagr,
        "taxed_mdd": metrics.mdd,
        "taxed_sharpe": metrics.sharpe,
        "taxed_sortino": metrics.sortino,
        "taxed_calmar": metrics.calmar,
        "taxed_terminal": metrics.terminal,
        "wf_beats": beats,
        "wf_windows": n_windows,
        "pct_days_escalated": float(state.mean()),
        "dip_episodes": episodes,
        "state_changes": weight_summary["state_changes"],
        "turnover_per_year": tax_summary["turnover_per_year"],
        "total_tax_paid_pct_initial": tax_summary["total_tax_paid_pct_initial"],
    }
    return row, taxed, state


def benchmark_row(branch_key: str, name: str, returns: pd.Series, benchmark: pd.Series) -> dict[str, object]:
    metrics = metrics_from_returns(returns)
    beats, n_windows = wf_beats(returns, benchmark)
    return {
        "config_type": name,
        "branch": branch_key,
        "l_base": float("nan"),
        "l_dip": float("nan"),
        "trigger": float("nan"),
        "exit_rule": "",
        "lag_days": -1,
        "taxed_cagr": metrics.cagr,
        "taxed_mdd": metrics.mdd,
        "taxed_sharpe": metrics.sharpe,
        "taxed_sortino": metrics.sortino,
        "taxed_calmar": metrics.calmar,
        "taxed_terminal": metrics.terminal,
        "wf_beats": beats,
        "wf_windows": n_windows,
        "pct_days_escalated": float("nan"),
        "dip_episodes": float("nan"),
        "state_changes": float("nan"),
        "turnover_per_year": float("nan"),
        "total_tax_paid_pct_initial": float("nan"),
    }


def sanity_never_triggers(
    context: "phase04.BranchContext", prices: pd.Series, profile: dict[str, float]
) -> float:
    """Trigger 100% never fires -> must equal the constant L_base simulation."""
    state = dip_state(prices, 1.00, "ath")
    taxed, _, _ = simulate_ladder(context, state, profile["l_base"], profile["l_dip"], 0)
    reference = constant_leverage_taxed(context, profile["l_base"])
    aligned = pd.concat({"a": taxed, "b": reference}, axis=1, sort=False).dropna()
    return float((aligned["a"] - aligned["b"]).abs().max())


def screen_branch(frame: pd.DataFrame, branch_key: str) -> dict[str, object]:
    """Return-first screen vs the row's own constant-leverage benchmarks."""
    trials = frame[(frame["config_type"] == "dip_ladder") & (frame["branch"] == branch_key)]
    eligible = trials[trials["taxed_mdd"] >= MDD_FLOOR]
    bench = frame[(frame["branch"] == branch_key) & (frame["config_type"].str.startswith("const_"))]
    if eligible.empty:
        return {"branch": branch_key, "best": None, "success": False}
    best = eligible.sort_values(["taxed_cagr", "taxed_calmar"], ascending=False).iloc[0]
    base_bh = bench[bench["config_type"] == f"const_{best['l_base']:.2f}"].iloc[0]
    dip_bh = bench[bench["config_type"] == f"const_{best['l_dip']:.2f}"].iloc[0]
    crit_cagr = bool(best["taxed_cagr"] > base_bh["taxed_cagr"])
    crit_mdd_floor = bool(best["taxed_mdd"] >= MDD_FLOOR)
    crit_mdd_vs_dip = bool(best["taxed_mdd"] > dip_bh["taxed_mdd"])
    return {
        "branch": branch_key,
        "best": best,
        "base_bh": base_bh,
        "dip_bh": dip_bh,
        "crit_cagr": crit_cagr,
        "crit_mdd_floor": crit_mdd_floor,
        "crit_mdd_vs_dip": crit_mdd_vs_dip,
        "success": bool(crit_cagr and crit_mdd_floor and crit_mdd_vs_dip),
    }


# --------------------------------------------------------------------------- plots


def plot_state_series(best_states: dict[str, tuple[pd.Series, pd.Series]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(best_states), 1, figsize=(13, 3.6 * len(best_states)), squeeze=False)
    for ax, (label, (prices, state)) in zip(axes.ravel(), best_states.items()):
        px = prices / prices.iloc[0]
        ax.plot(px.index, px.to_numpy(dtype=float), linewidth=0.8, color="black")
        ax.set_yscale("log")
        mask = state.reindex(px.index).fillna(False).to_numpy(dtype=bool)
        ax.fill_between(px.index, ax.get_ylim()[0], ax.get_ylim()[1], where=mask, color="tab:green", alpha=0.15, label="escalated (dip state)")
        ax.set_title(f"{label}: underlying (log) with escalation shading")
        ax.legend()
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase10_state_series.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_equity_dd(
    best_returns: dict[str, pd.Series],
    base_bh: dict[str, pd.Series],
    dip_bh: dict[str, pd.Series],
) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    branches = list(best_returns)
    fig, axes = plt.subplots(2, len(branches), figsize=(7.5 * len(branches), 8.5), squeeze=False)
    for col, branch in enumerate(branches):
        pair = pd.concat(
            {
                "dip ladder best": best_returns[branch],
                "const L_base B&H": base_bh[branch],
                "const L_dip B&H": dip_bh[branch],
            },
            axis=1,
        ).dropna()
        eq = pair.apply(equity_curve)
        eq.plot(ax=axes[0][col], logy=True, linewidth=1.0)
        axes[0][col].set_title(f"{branch}: after-tax equity")
        axes[0][col].grid(True, alpha=0.3)
        dd = eq / eq.cummax() - 1.0
        (dd * 100.0).plot(ax=axes[1][col], linewidth=0.9)
        axes[1][col].set_title(f"{branch}: drawdown (%)")
        axes[1][col].grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase10_equity_dd.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9.5, 6))
    trials = frame[frame["config_type"] == "dip_ladder"]
    for (profile, trigger), sub in trials.groupby(["l_dip", "trigger"]):
        ax.scatter(
            sub["taxed_mdd"] * 100.0, sub["taxed_cagr"] * 100.0, s=35, alpha=0.75,
            label=f"L_dip {float(profile):.1f} @ -{float(trigger):.0%}",
        )
    bench = frame[frame["config_type"].str.startswith("const_")]
    ax.scatter(bench["taxed_mdd"] * 100.0, bench["taxed_cagr"] * 100.0, s=110, marker="*", color="black", label="const-L benchmarks")
    ax.axvline(MDD_FLOOR * 100.0, color="red", linestyle="--", linewidth=0.9, label="MDD -50% floor")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.set_title("Phase 10 frontier: dip-ladder grid vs constant leverage")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = PLOTS / "phase10_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------- report


def trigger_answer_table(frame: pd.DataFrame, branch_key: str) -> str:
    """The user's question: per trigger level, the best row's economics."""
    trials = frame[(frame["config_type"] == "dip_ladder") & (frame["branch"] == branch_key)]
    rows = []
    for (trigger, l_dip), sub in trials.groupby(["trigger", "l_dip"]):
        best = sub.sort_values(["taxed_cagr", "taxed_calmar"], ascending=False).iloc[0]
        rows.append(
            {
                "Trigger": f"-{float(trigger):.0%}",
                "Profile": f"{best['l_base']:.1f} -> {best['l_dip']:.1f}",
                "Best exit/lag": f"{best['exit_rule']} / lag {int(best['lag_days'])}",
                "CAGR": fmt_pct(best["taxed_cagr"]),
                "MDD": fmt_pct(best["taxed_mdd"]),
                "Floor": "ok" if best["taxed_mdd"] >= MDD_FLOOR else "BREACH",
                "Calmar": fmt_num(best["taxed_calmar"]),
                "Escalated days": fmt_pct(best["pct_days_escalated"], 1),
                "Episodes": int(best["dip_episodes"]),
            }
        )
    rows.sort(key=lambda r: (r["Trigger"], r["Profile"]))
    return md_table(rows, ["Trigger", "Profile", "Best exit/lag", "CAGR", "MDD", "Floor", "Calmar", "Escalated days", "Episodes"])


def top_rows_table(frame: pd.DataFrame, branch_key: str, limit: int = 10) -> str:
    sub = frame[(frame["config_type"] == "dip_ladder") & (frame["branch"] == branch_key)]
    sub = sub.sort_values(["taxed_cagr", "taxed_calmar"], ascending=False).head(limit)
    rows = [
        {
            "Profile": f"{r['l_base']:.1f}->{r['l_dip']:.1f}",
            "Trigger": f"-{float(r['trigger']):.0%}",
            "Exit": r["exit_rule"],
            "Lag": int(r["lag_days"]),
            "CAGR": fmt_pct(r["taxed_cagr"]),
            "MDD": fmt_pct(r["taxed_mdd"]),
            "Floor": "ok" if r["taxed_mdd"] >= MDD_FLOOR else "BREACH",
            "WF": f"{int(r['wf_beats'])}/{int(r['wf_windows'])}",
            "Calmar": fmt_num(r["taxed_calmar"]),
            "Turnover/y": fmt_num(r["turnover_per_year"], 2),
        }
        for _, r in sub.iterrows()
    ]
    return md_table(rows, ["Profile", "Trigger", "Exit", "Lag", "CAGR", "MDD", "Floor", "WF", "Calmar", "Turnover/y"])


def benchmarks_table(frame: pd.DataFrame, branch_key: str) -> str:
    bench = frame[(frame["branch"] == branch_key) & (frame["config_type"] != "dip_ladder")]
    rows = [
        {
            "Benchmark": r["config_type"],
            "CAGR": fmt_pct(r["taxed_cagr"]),
            "MDD": fmt_pct(r["taxed_mdd"]),
            "Sharpe": fmt_num(r["taxed_sharpe"]),
            "Calmar": fmt_num(r["taxed_calmar"]),
        }
        for _, r in bench.iterrows()
    ]
    return md_table(rows, ["Benchmark", "CAGR", "MDD", "Sharpe", "Calmar"])


def screen_table(screens: list[dict[str, object]]) -> str:
    rows = []
    for screen in screens:
        best = screen["best"]
        if best is None:
            rows.append(
                {
                    "Branch": screen["branch"],
                    "Best eligible row": "none (all rows breach the -50% floor)",
                    "CAGR > const L_base": "F",
                    "MDD >= -50%": "F",
                    "MDD better than const L_dip": "F",
                    "Screen": "FAIL",
                }
            )
            continue
        rows.append(
            {
                "Branch": screen["branch"],
                "Best eligible row": f"{best['l_base']:.1f}->{best['l_dip']:.1f} @ -{float(best['trigger']):.0%} / {best['exit_rule']} / lag {int(best['lag_days'])}",
                "CAGR > const L_base": f"{fmt_pct(best['taxed_cagr'])} vs {fmt_pct(screen['base_bh']['taxed_cagr'])} {'P' if screen['crit_cagr'] else 'F'}",
                "MDD >= -50%": f"{fmt_pct(best['taxed_mdd'])} {'P' if screen['crit_mdd_floor'] else 'F'}",
                "MDD better than const L_dip": f"vs {fmt_pct(screen['dip_bh']['taxed_mdd'])} {'P' if screen['crit_mdd_vs_dip'] else 'F'}",
                "Screen": "SUCCESS" if screen["success"] else "FAIL",
            }
        )
    return md_table(rows, ["Branch", "Best eligible row", "CAGR > const L_base", "MDD >= -50%", "MDD better than const L_dip", "Screen"])


def write_report(
    frame: pd.DataFrame,
    screens: list[dict[str, object]],
    plot_rows: list[dict[str, str]],
    sanity: dict[str, float],
) -> None:
    n_success = sum(1 for s in screens if s["success"])
    sanity_text = "; ".join(f"{k}: max abs diff {v:.3g}" for k, v in sanity.items())
    sections = [
        "# Phase 10 - Drawdown-Contingent Leverage Ladder, \"Buy the Dip\" (DIAGNOSTIC, RETURN-FIRST)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.\n\n"
        "User-directed contrarian family: L_base most of the time, escalate to L_dip when the underlying's drawdown crosses -d, de-escalate on recovery (`ath` = new high; `half` = DD back to -d/2), hysteresis per `[trading_systems_methods, p.383]`. Equity indices are high-noise/countertrend-matching markets `[trading_systems_methods, p.13]`; the recorded counter-thesis is that dips are high-vol regimes where leveraged compounding is worst `[leverage_for_the_long_run, p.7-9]`. No SMA gate, no vol gate (clean isolation). Weekly cadence, lag 0..5, `AnnualDarfEngine`.\n\n"
        f"Pre-registered grid: 2 branches x 2 profiles x 3 triggers x 2 exits x 6 lags = {N_TRIALS_ADDED} rows. **n_trials ledger: {N_TRIALS_LEDGER_BEFORE} + {N_TRIALS_ADDED} = {N_TRIALS_LEDGER_BEFORE + N_TRIALS_ADDED}.** Constant-leverage B&H rows, underlying B&H and the LRS headline are comparisons, not trials.\n\n"
        f"**Built-in sanity (trigger 100% never fires vs constant L_base):** {sanity_text}.\n\n"
        "## Executive Conclusion\n\n"
        f"Return-first pre-registered screen (best CAGR among MDD>=-50% rows, vs the row's own constant-leverage benchmarks): **{n_success}/{len(screens)} branches SUCCESS**. Criteria: CAGR strictly above constant L_base B&H AND MDD >= -50% AND MDD strictly better than constant L_dip B&H. NOT a gate pass either way `[advances_fin_ml, p.208-211]`.\n\n",
    ]
    sections.append("## Screen Result\n\n" + screen_table(screens))
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    for screen in screens:
        branch_key = str(screen["branch"])
        sections.append(
            f"## {branch_key}: \"what dip level is interesting?\" (best row per trigger x profile)\n\n"
            + trigger_answer_table(frame, branch_key)
        )
        sections.append(f"## Top {branch_key} Rows (by CAGR)\n\n" + top_rows_table(frame, branch_key))
        sections.append(f"## {branch_key} Benchmarks (non-trial)\n\n" + benchmarks_table(frame, branch_key))
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        + "".join(
            (
                f"| {s['branch']}: does dip-escalation beat its own constant-leverage benchmarks within the floor? | "
                + ("Yes" if s["success"] else "No")
                + (
                    f" ({fmt_pct(float(s['best']['taxed_cagr']))} @ {fmt_pct(float(s['best']['taxed_mdd']))}). |\n"
                    if s["best"] is not None
                    else " (no row inside the floor). |\n"
                )
            )
            for s in screens
        )
        + f"| Screen successes? | {n_success}/{len(screens)}. |\n"
        "| Did we promote anything? | No - return-first diagnostic only. |\n"
        "| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    best_returns: dict[str, pd.Series] = {}
    best_states: dict[str, tuple[pd.Series, pd.Series]] = {}
    base_bh_returns: dict[str, pd.Series] = {}
    dip_bh_returns: dict[str, pd.Series] = {}
    sanity: dict[str, float] = {}

    for spec in BRANCH_SPECS:
        branch_key = str(spec["branch"])
        context = phase04.build_context(phase04.BRANCHES[branch_key])
        prices = branch_underlying_prices(context)
        sanity[branch_key] = sanity_never_triggers(context, prices, PROFILES[0])

        # Non-trial benchmarks: underlying B&H, constant-L B&H per unique level, LRS headline.
        rows.append(benchmark_row(branch_key, "underlying_bh", context.underlying_taxed, context.underlying_taxed))
        const_taxed: dict[float, pd.Series] = {}
        for level in sorted({p["l_base"] for p in PROFILES} | {p["l_dip"] for p in PROFILES}):
            const_taxed[level] = constant_leverage_taxed(context, level)
            rows.append(benchmark_row(branch_key, f"const_{level:.2f}", const_taxed[level], context.underlying_taxed))
        risk_off_weights = clean_weights(
            next(r["weights"] for r in phase04.RISK_OFF_SPECS if r["name"] == spec["headline_off"])
        )
        vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == spec["headline_vol"])
        headline = phase04.simulate_returns(
            context, float(spec["headline_l"]), risk_off_weights, vol_spec, int(spec["headline_lag"])
        )
        rows.append(benchmark_row(branch_key, "lrs_headline", headline, context.underlying_taxed))

        best_key: tuple[float, float] | None = None
        for profile in PROFILES:
            for trigger in TRIGGERS:
                for exit_rule in EXIT_RULES:
                    for lag in LAGS:
                        row, taxed, state = evaluate_row(
                            context, branch_key, prices, profile, trigger, exit_rule, lag
                        )
                        rows.append(row)
                        if row["taxed_mdd"] >= MDD_FLOOR:
                            key = (float(row["taxed_cagr"]), float(row["taxed_calmar"]))
                            if best_key is None or key > best_key:
                                best_key = key
                                best_returns[branch_key] = taxed
                                best_states[
                                    f"{branch_key} {profile['l_base']:.1f}->{profile['l_dip']:.1f} @ -{trigger:.0%} {exit_rule} lag {lag}"
                                ] = (prices, state)
                                base_bh_returns[branch_key] = const_taxed[profile["l_base"]]
                                dip_bh_returns[branch_key] = const_taxed[profile["l_dip"]]
        print(f"  {branch_key}: grid done (sanity max abs diff {sanity[branch_key]:.3g})")

    frame = pd.DataFrame(rows)
    frame.to_csv(CSV, index=False)
    screens = [screen_branch(frame, str(spec["branch"])) for spec in BRANCH_SPECS]
    plot_rows = []
    if best_states:
        state_plot = plot_state_series(best_states)
        plot_rows.append({"Plot": "Underlying with escalation shading (best rows)", "File": f"[plots/{state_plot.name}](plots/{state_plot.name})"})
    if best_returns:
        eq = plot_equity_dd(best_returns, base_bh_returns, dip_bh_returns)
        plot_rows.append({"Plot": "Equity/drawdown vs constant-leverage benchmarks", "File": f"[plots/{eq.name}](plots/{eq.name})"})
    frontier = plot_frontier(frame)
    plot_rows.append({"Plot": "CAGR x MDD frontier", "File": f"[plots/{frontier.name}](plots/{frontier.name})"})
    write_report(frame, screens, plot_rows, sanity)

    for screen in screens:
        best = screen["best"]
        if best is None:
            print(f"Phase 10 {screen['branch']}: no row inside the -50% floor -> FAIL")
            continue
        print(
            f"Phase 10 {screen['branch']}: best {best['l_base']:.1f}->{best['l_dip']:.1f} @ -{float(best['trigger']):.0%} "
            f"{best['exit_rule']} lag {int(best['lag_days'])} CAGR {best['taxed_cagr']:.2%} "
            f"(const base {screen['base_bh']['taxed_cagr']:.2%}) MDD {best['taxed_mdd']:.2%} "
            f"(const dip {screen['dip_bh']['taxed_mdd']:.2%}) "
            f"screen={'SUCCESS' if screen['success'] else 'FAIL'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
