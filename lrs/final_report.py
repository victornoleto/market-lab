"""LRS study final consolidation: lrs/REPORT.md + lrs/plots/* (DIAGNOSTIC).

Research-only. Recomputes the three study finalists on their committed
configs (+0 trials - every config was already counted in the 4569 ledger),
adds the money-weighted contribution lens (10k + 1k/month, precedent: Phase
6A Part 2), and renders the study-evolution and current-status plot pack.
Nothing here is a promotion; validation status is quoted verbatim from
Phase 8 `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.

Runner: `uv run python -m lrs.final_report`.
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lrs.lib.backtest import (  # noqa: E402
    clean_weights,
    equity_curve,
    fmt_num,
    fmt_pct,
    md_table,
    metrics_from_returns,
    relative_stats,
)
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from lrs.phases.phase06b_vol_target_continuous import run as phase06b  # noqa: E402
from lrs.phases.phase07a_ensemble_lookback import run as phase07a  # noqa: E402
from lrs.phases.phase07d_vol_target_quadratic.run import quadratic_leverage_series  # noqa: E402
from lrs.lib.backtest import build_weekly_lagged_weights, simulate_weight_frame  # noqa: E402


PLOTS = ROOT / "plots"
REPORT = ROOT / "REPORT.md"

INITIAL = 10_000.0
MONTHLY = 1_000.0
TRADING_DAYS = 252

# The committed study-evolution facts (from MEMORY.md / phase REPORTs).
# Trial column = the official DSR-lineage adds (Phase 4 convention: the
# lineage starts at Phase 2; P0/P1/P5 rows exist but sit outside the ledger).
PHASE_LEDGER = [
    ("P0 baseline", 0, "diagnostic (24 rows, fora do ledger DSR)"),
    ("P1 risk-off", 0, "driver (264 rows, fora do ledger DSR)"),
    ("P2 geometry", 2400, "driver"),
    ("P3A filters", 324, "FAIL"),
    ("P3A-2 forms", 216, "FAIL"),
    ("P3C lookback", 936, "FAIL"),
    ("P4 gates", 0, "FAIL 0/6"),
    ("P5 overlay", 0, "FAIL 0/9 (fora do ledger DSR)"),
    ("P6 round", 129, "decision table"),
    ("P7A ensemble", 72, "SPY SUCCESS"),
    ("P7B multi-asset", 72, "FAIL"),
    ("P7C macro GTT", 72, "FAIL (MDD)"),
    ("P7D vol^2", 72, "QQQ SUCCESS"),
    ("P7E MF risk-off", 60, "weak SPY"),
    ("P7F composition", 24, "FAIL"),
    ("P8 final gates", 0, "FAIL 0/2"),
    ("P9 3x ceiling", 48, "SPY lead"),
    ("P10 dip ladder", 144, "FAIL 0/2"),
]
WF_PROGRESS = {
    "SPY": [("P4 binary", 12, 17, "pass-floor 13"), ("7A ensemble", 13, 17, "G3 level"), ("7C macro (MDD fail)", 14, 17, "floor breach")],
    "QQQ": [("P4 binary", 7, 11, "pass-floor 9"), ("7D vol^2", 8, 11, "best honest"), ("7C macro (MDD fail)", 10, 11, "floor breach")],
}
PHASE8_GATES = {
    "spy_7a_ensemble": {"G1 PBO": (0.397, True), "G2 DSR p": (0.052, False), "G3 WF": ("13/17", True), "G4 OOS": ("", True), "G5 FWD": ("", True), "G6 Boot": ("", True), "G7 xlib": ("", True)},
    "qqq_7d_quadratic": {"G1 PBO": (0.651, False), "G2 DSR p": (0.138, False), "G3 WF": ("8/11", False), "G4 OOS": ("", True), "G5 FWD": ("", True), "G6 Boot": ("", True), "G7 xlib": ("", True)},
}


# --------------------------------------------------------------------------- finalists


def finalist_spy_7a() -> tuple[pd.Series, pd.Series, pd.Series, dict[str, float]]:
    """F1: 7A ensemble spy_alt_off / narrow / lag 2. Returns (taxed, underlying, exposure, summary)."""
    context = phase04.build_context(phase04.BRANCHES["SPY"])
    fbs = {n: phase07a.ensemble_fraction(context, w) for n, w in phase07a.WINDOW_SETS.items()}
    base = next(b for b in phase04.BASE_SPECS if b["name"] == "spy_alt_off")
    row, taxed = phase07a.evaluate_row(context, base, "narrow_150_225", 2, fbs)
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == base["vol"])
    gate = phase04.vol_gate(context, vol_spec).astype(float)
    exposure = (fbs["narrow_150_225"] * gate * 2.0).rename("exposure")  # f_t x L2.00
    summary = {"turnover_per_year": float(row["turnover_per_year"]), "tax_paid_x": float(row["total_tax_paid_pct_initial"])}
    return taxed, context.underlying_taxed, exposure, summary


def finalist_spy_p9() -> tuple[pd.Series, pd.Series, pd.Series, dict[str, float]]:
    """F2: Phase 9 SPY quadratic cap 2.5x, sigma 40 / RV21 / lag 3."""
    context = phase04.build_context(phase04.BRANCHES["SPY"])
    risk_off = clean_weights(
        next(r["weights"] for r in phase04.RISK_OFF_SPECS if r["name"] == "50 ZROZ / 25 GLD / 25 CASH")
    )
    leverage = quadratic_leverage_series(context.returns["SPYSIM"], 21, 0.40, 2.50)
    desired = phase06b.desired_targets_continuous(context, leverage, risk_off)
    weights, _ = build_weekly_lagged_weights(desired, lag_days=3)
    taxed, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    signal = context.sma_signal.reindex(context.returns.index).fillna(False)
    exposure = leverage.where(signal, 0.0).rename("exposure")
    summary = {"turnover_per_year": float(tax_summary["turnover_per_year"]), "tax_paid_x": float(tax_summary["total_tax_paid_pct_initial"])}
    return taxed, context.underlying_taxed, exposure, summary


def finalist_qqq_l2() -> tuple[pd.Series, pd.Series, pd.Series, dict[str, float]]:
    """F3: Phase 2 QQQ L2.00 / 50 ZROZ 50 GLD / RV63<=40% / lag 1 (best Calmar of the grid)."""
    context = phase04.build_context(phase04.BRANCHES["QQQ"])
    risk_off = clean_weights(
        next(r["weights"] for r in phase04.RISK_OFF_SPECS if r["name"] == "50 ZROZ / 50 GLD")
    )
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == "RV63 <= 40%")
    risk_on = phase04.target_leverage_weights(context.branch, 2.00)
    signal = context.sma_signal & phase04.vol_gate(context, vol_spec)
    assets = sorted(set(risk_on) | set(risk_off) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=context.returns.index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(signal, risk_on.get(asset, 0.0), risk_off.get(asset, 0.0))
    weights, _ = build_weekly_lagged_weights(desired, lag_days=1, risk_on_weights=risk_on)
    taxed, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    exposure = signal.astype(float).reindex(context.returns.index).fillna(0.0) * 2.0
    exposure = exposure.rename("exposure")
    summary = {"turnover_per_year": float(tax_summary["turnover_per_year"]), "tax_paid_x": float(tax_summary["total_tax_paid_pct_initial"])}
    return taxed, context.underlying_taxed, exposure, summary


def lrs_headline_spy() -> pd.Series:
    context = phase04.build_context(phase04.BRANCHES["SPY"])
    risk_off = clean_weights(
        next(r["weights"] for r in phase04.RISK_OFF_SPECS if r["name"] == "50 ZROZ / 25 GLD / 25 CASH")
    )
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == "RV21 <= 30%")
    return phase04.simulate_returns(context, 2.00, risk_off, vol_spec, 3)


# --------------------------------------------------------------------------- contribution lens


def contribution_sim(returns: pd.Series) -> dict[str, float]:
    """10k + 1k on the first trading day of each month into the after-tax series.

    Money-weighted lens (Phase 6A Part 2 precedent): the strategy series is
    already after-tax, so inflows simply buy more of the same curve. Path MDD
    is mechanically softened by inflows - disclosed, not hidden.
    """
    r = returns.dropna()
    idx = r.index
    months = idx.to_period("M")
    is_month_start = np.r_[True, months[1:] != months[:-1]]
    value = 0.0
    flows: list[tuple[pd.Timestamp, float]] = []
    values = np.empty(len(idx))
    contributed = 0.0
    for i, (date, ret) in enumerate(zip(idx, r.to_numpy(dtype=float))):
        if i == 0:
            value += INITIAL
            contributed += INITIAL
            flows.append((date, INITIAL))
        elif is_month_start[i]:
            value += MONTHLY
            contributed += MONTHLY
            flows.append((date, MONTHLY))
        value *= 1.0 + ret
        values[i] = value
    series = pd.Series(values, index=idx)
    dd = series / series.cummax() - 1.0
    end = idx[-1]
    years = np.array([(end - d).days / 365.25 for d, _ in flows])
    amounts = np.array([a for _, a in flows])

    def fv_gap(rate: float) -> float:
        return float((amounts * (1.0 + rate) ** years).sum() - value)

    lo, hi = -0.5, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if fv_gap(mid) > 0:
            hi = mid
        else:
            lo = mid
    return {
        "irr": 0.5 * (lo + hi),
        "terminal": value,
        "contributed": contributed,
        "path_mdd": float(dd.min()),
        "years": float(len(idx) / TRADING_DAYS),
    }


# --------------------------------------------------------------------------- plots


def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def plot_equity_dd(curves: dict[str, dict[str, pd.Series]]) -> list[Path]:
    plt = _plt()
    out_paths = []
    for branch, series_map in curves.items():
        pair = pd.concat(series_map, axis=1).dropna()
        eq = pair.apply(equity_curve)
        fig, axes = plt.subplots(2, 1, figsize=(13, 9), height_ratios=[2, 1])
        eq.plot(ax=axes[0], logy=True, linewidth=1.0)
        axes[0].set_title(f"{branch}: after-tax equity (log), finalists vs benchmarks")
        axes[0].grid(True, alpha=0.3)
        dd = eq / eq.cummax() - 1.0
        (dd * 100.0).plot(ax=axes[1], linewidth=0.8, legend=False)
        axes[1].set_title("drawdown (%)")
        axes[1].grid(True, alpha=0.3)
        fig.tight_layout()
        out = PLOTS / f"final_equity_dd_{branch.lower()}.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        out_paths.append(out)
    return out_paths


def plot_frontier_all_trials(finalists: dict[str, dict[str, float]]) -> Path:
    plt = _plt()
    fig, ax = plt.subplots(figsize=(11, 7))
    n_rows = 0
    for csv in sorted((ROOT / "results").glob("*.csv")):
        try:
            df = pd.read_csv(csv)
        except Exception:
            continue
        cagr_col = "taxed_cagr" if "taxed_cagr" in df.columns else ("cagr" if "cagr" in df.columns else None)
        mdd_col = "taxed_mdd" if "taxed_mdd" in df.columns else ("mdd" if "mdd" in df.columns else None)
        if cagr_col is None or mdd_col is None:
            continue
        sub = df[[cagr_col, mdd_col]].dropna()
        ax.scatter(sub[mdd_col] * 100.0, sub[cagr_col] * 100.0, s=8, alpha=0.25, color="#999999")
        n_rows += len(sub)
    for name, m in finalists.items():
        marker = "*" if m.get("kind") == "finalist" else "D"
        size = 260 if m.get("kind") == "finalist" else 110
        ax.scatter(m["mdd"] * 100.0, m["cagr"] * 100.0, s=size, marker=marker, label=name, zorder=5)
    ax.axvline(-50.0, color="red", linestyle="--", linewidth=1.0, label="MDD -50% floor")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.set_title(f"LRS study map: every recorded trial row ({n_rows} grey dots) + finalists/benchmarks")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    fig.tight_layout()
    out = PLOTS / "final_frontier_all_trials.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_wf_progress() -> Path:
    plt = _plt()
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    for ax, (branch, steps) in zip(axes, WF_PROGRESS.items()):
        labels = [s[0] for s in steps]
        ratios = [s[1] / s[2] * 100.0 for s in steps]
        colors = ["#4c9a6b" if "fail" not in s[0].lower() else "#d6a35f" for s in steps]
        colors = ["#d6a35f" if "MDD fail" in s[0] else "#4c72b0" for s in steps]
        bars = ax.bar(labels, ratios, color=colors)
        for bar, s in zip(bars, steps):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{s[1]}/{s[2]}", ha="center", fontsize=10)
        ax.axhline(75.0, color="red", linestyle="--", linewidth=1.0, label="G3 gate (75%)")
        ax.set_ylim(0, 105)
        ax.set_ylabel("% OOS windows beating underlying")
        ax.set_title(f"{branch}: walk-forward evolution (binding gate)")
        ax.legend()
        ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "final_wf_progress.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_trial_ledger() -> Path:
    plt = _plt()
    labels = [p[0] for p in PHASE_LEDGER]
    adds = [p[1] for p in PHASE_LEDGER]
    cum = np.cumsum(adds)
    color_map = {"FAIL": "#d65f5f", "SUCCESS": "#4c9a6b", "driver": "#4c72b0", "diagnostic": "#888888"}

    def color_for(v: str) -> str:
        if "SUCCESS" in v or "lead" in v or "weak" in v:
            return "#4c9a6b"
        if "FAIL" in v:
            return "#d65f5f"
        if "driver" in v:
            return "#4c72b0"
        return "#888888"

    fig, ax = plt.subplots(figsize=(13, 5.2))
    ax.plot(range(len(labels)), cum, color="black", linewidth=1.2, marker="o", markersize=4)
    for i, (label, add, verdict) in enumerate(PHASE_LEDGER):
        ax.annotate(
            f"{label}\n+{add} ({verdict})", (i, cum[i]), textcoords="offset points", xytext=(0, 10),
            ha="center", fontsize=7, color=color_for(verdict), rotation=45,
        )
    ax.set_ylabel("cumulative n_trials (honest ledger)")
    ax.set_xticks([])
    ax.set_ylim(0, cum[-1] * 1.35)
    ax.set_title(f"Search-intensity ledger: {cum[-1]} trials across 18 pre-registered steps (DSR deflates against ALL of it)")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "final_trial_ledger.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_phase8_gates() -> Path:
    plt = _plt()
    from matplotlib.colors import ListedColormap

    configs = list(PHASE8_GATES)
    gate_names = list(PHASE8_GATES[configs[0]])
    grid = np.array([[1.0 if PHASE8_GATES[c][g][1] else 0.0 for g in gate_names] for c in configs])
    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.imshow(grid, cmap=ListedColormap(["#d65f5f", "#4c9a6b"]), vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(gate_names)))
    ax.set_xticklabels(gate_names, rotation=30, ha="right")
    ax.set_yticks(range(len(configs)))
    ax.set_yticklabels(configs)
    for i, c in enumerate(configs):
        for j, g in enumerate(gate_names):
            val, ok = PHASE8_GATES[c][g]
            text = f"{val}" if val != "" else ("PASS" if ok else "FAIL")
            ax.text(j, i, text, ha="center", va="center", fontsize=8, color="white")
    ax.set_title("Current validation status: Phase 8 mandate gates (FAIL 0/2 - line closed)")
    fig.tight_layout()
    out = PLOTS / "final_phase8_gates.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_exposure(exposures: dict[str, pd.Series]) -> Path:
    plt = _plt()
    fig, axes = plt.subplots(len(exposures), 1, figsize=(13, 2.9 * len(exposures)), squeeze=False)
    for ax, (label, exp) in zip(axes.ravel(), exposures.items()):
        ax.plot(exp.index, exp.to_numpy(dtype=float), linewidth=0.5, color="tab:blue")
        ax.set_title(f"{label}: effective risk-on exposure over time")
        ax.set_ylabel("x leverage")
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "final_exposure_series.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_rolling_10y(curves: dict[str, dict[str, pd.Series]]) -> Path:
    plt = _plt()
    window = 10 * TRADING_DAYS
    fig, axes = plt.subplots(1, len(curves), figsize=(7.5 * len(curves), 5), squeeze=False)
    for ax, (branch, series_map) in zip(axes[0], curves.items()):
        bench_name = [k for k in series_map if "B&H" in k][0]
        pair = pd.concat(series_map, axis=1).dropna()
        eq = pair.apply(equity_curve)
        for name in series_map:
            if name == bench_name:
                continue
            rel = (eq[name] / eq[name].shift(window)) / (eq[bench_name] / eq[bench_name].shift(window))
            ann = rel ** (1.0 / 10.0) - 1.0
            ax.plot(ann.index, ann.to_numpy(dtype=float) * 100.0, linewidth=0.9, label=name)
        ax.axhline(0.0, color="black", linewidth=0.8)
        ax.set_title(f"{branch}: rolling 10y CAGR spread vs {bench_name}")
        ax.set_ylabel("pp/year")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    fig.tight_layout()
    out = PLOTS / "final_rolling_10y.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_decade_returns(curves: dict[str, dict[str, pd.Series]]) -> Path:
    plt = _plt()
    fig, axes = plt.subplots(1, len(curves), figsize=(8 * len(curves), 5), squeeze=False)
    for ax, (branch, series_map) in zip(axes[0], curves.items()):
        pair = pd.concat(series_map, axis=1).dropna()
        decades = (pair.index.year // 10) * 10
        rows = {}
        for name in pair.columns:
            by_decade = {}
            for dec, sub in pair[name].groupby(decades):
                growth = float((1.0 + sub).prod())
                yrs = len(sub) / TRADING_DAYS
                by_decade[f"{dec}s"] = (growth ** (1.0 / yrs) - 1.0) * 100.0 if yrs > 0.5 else np.nan
            rows[name] = by_decade
        table = pd.DataFrame(rows)
        table.plot.bar(ax=ax)
        ax.set_title(f"{branch}: CAGR by decade (after-tax)")
        ax.set_ylabel("%/year")
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend(fontsize=8)
        ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    out = PLOTS / "final_decade_returns.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_contribution(curve_values: dict[str, pd.Series]) -> Path:
    plt = _plt()
    fig, ax = plt.subplots(figsize=(13, 6))
    for name, series in curve_values.items():
        ax.plot(series.index, series.to_numpy(dtype=float), linewidth=1.0, label=name)
    ax.set_yscale("log")
    ax.set_ylabel("portfolio value (USD, log)")
    ax.set_title(f"Contribution lens: {INITIAL:,.0f} initial + {MONTHLY:,.0f}/month into each after-tax curve")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    fig.tight_layout()
    out = PLOTS / "final_contribution_sim.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def contribution_value_series(returns: pd.Series) -> pd.Series:
    r = returns.dropna()
    idx = r.index
    months = idx.to_period("M")
    is_month_start = np.r_[True, months[1:] != months[:-1]]
    value = 0.0
    values = np.empty(len(idx))
    for i, ret in enumerate(r.to_numpy(dtype=float)):
        if i == 0:
            value += INITIAL
        elif is_month_start[i]:
            value += MONTHLY
        value *= 1.0 + ret
        values[i] = value
    return pd.Series(values, index=idx)


# --------------------------------------------------------------------------- report


def main() -> int:
    PLOTS.mkdir(parents=True, exist_ok=True)
    print("  building finalists...")
    f1_taxed, spy_bh, f1_exp, f1_sum = finalist_spy_7a()
    f2_taxed, _, f2_exp, f2_sum = finalist_spy_p9()
    f3_taxed, qqq_bh, f3_exp, f3_sum = finalist_qqq_l2()
    headline = lrs_headline_spy()

    finalists = {
        "F1 spy_7a_ensemble": (f1_taxed, spy_bh, f1_sum),
        "F2 spy_p9_cap2.5x": (f2_taxed, spy_bh, f2_sum),
        "F3 qqq_l2_binary": (f3_taxed, qqq_bh, f3_sum),
    }

    print("  metrics + contribution lens...")
    rows = []
    contrib = {}
    for name, (taxed, bench, summary) in finalists.items():
        m = metrics_from_returns(taxed)
        rs = relative_stats(taxed, bench)
        c = contribution_sim(taxed)
        contrib[name] = c
        rows.append(
            {
                "Finalist": name,
                "Window": f"{m.start}..{m.end}",
                "CAGR": fmt_pct(m.cagr),
                "MDD": fmt_pct(m.mdd),
                "Sharpe": fmt_num(m.sharpe),
                "Calmar": fmt_num(m.calmar),
                "Terminal vs B&H": f"{rs['terminal_vs_benchmark']:.1f}x",
                "hit10y": fmt_pct(rs.get("hit_10y", float("nan")), 0),
                "Turnover/y": fmt_num(summary["turnover_per_year"], 1),
                "IRR (aportes)": fmt_pct(c["irr"]),
                "Path MDD (aportes)": fmt_pct(c["path_mdd"]),
                "Terminal (aportes)": f"${c['terminal'] / 1e6:.2f}M",
            }
        )
        print(f"    {name}: CAGR {m.cagr:.2%} MDD {m.mdd:.2%} IRR {c['irr']:.2%} path MDD {c['path_mdd']:.2%}")

    bench_rows = []
    for name, series in [("SPY B&H", spy_bh), ("QQQ B&H", qqq_bh), ("LRS SPY headline (binaria)", headline)]:
        m = metrics_from_returns(series)
        c = contribution_sim(series)
        bench_rows.append(
            {
                "Benchmark": name,
                "Window": f"{m.start}..{m.end}",
                "CAGR": fmt_pct(m.cagr),
                "MDD": fmt_pct(m.mdd),
                "Sharpe": fmt_num(m.sharpe),
                "Calmar": fmt_num(m.calmar),
                "IRR (aportes)": fmt_pct(c["irr"]),
                "Path MDD (aportes)": fmt_pct(c["path_mdd"]),
                "Terminal (aportes)": f"${c['terminal'] / 1e6:.2f}M",
            }
        )

    print("  plots...")
    curves = {
        "SPY": {
            "F1 spy_7a_ensemble": f1_taxed,
            "F2 spy_p9_cap2.5x": f2_taxed,
            "LRS headline": headline,
            "SPY B&H": spy_bh,
        },
        "QQQ": {"F3 qqq_l2_binary": f3_taxed, "QQQ B&H": qqq_bh},
    }
    plot_paths: list[Path] = []
    plot_paths += plot_equity_dd(curves)
    m1, m2, m3 = (metrics_from_returns(x) for x in (f1_taxed, f2_taxed, f3_taxed))
    mb, mq, mh = (metrics_from_returns(x) for x in (spy_bh, qqq_bh, headline))
    frontier_marks = {
        "F1 spy_7a_ensemble": {"cagr": m1.cagr, "mdd": m1.mdd, "kind": "finalist"},
        "F2 spy_p9_cap2.5x": {"cagr": m2.cagr, "mdd": m2.mdd, "kind": "finalist"},
        "F3 qqq_l2_binary": {"cagr": m3.cagr, "mdd": m3.mdd, "kind": "finalist"},
        "SPY B&H": {"cagr": mb.cagr, "mdd": mb.mdd, "kind": "bench"},
        "QQQ B&H": {"cagr": mq.cagr, "mdd": mq.mdd, "kind": "bench"},
        "LRS headline": {"cagr": mh.cagr, "mdd": mh.mdd, "kind": "bench"},
    }
    plot_paths.append(plot_frontier_all_trials(frontier_marks))
    plot_paths.append(plot_wf_progress())
    plot_paths.append(plot_trial_ledger())
    plot_paths.append(plot_phase8_gates())
    plot_paths.append(
        plot_exposure(
            {
                "F1 spy_7a_ensemble (f_t x 2.0)": f1_exp,
                "F2 spy_p9_cap2.5x (ladder L_t)": f2_exp,
                "F3 qqq_l2_binary (binary x 2.0)": f3_exp,
            }
        )
    )
    plot_paths.append(plot_rolling_10y(curves))
    plot_paths.append(plot_decade_returns(curves))
    contrib_curves = {
        name: contribution_value_series(taxed) for name, (taxed, _b, _s) in finalists.items()
    }
    contrib_curves["SPY B&H"] = contribution_value_series(spy_bh)
    plot_paths.append(plot_contribution(contrib_curves))

    print("  writing REPORT.md...")
    plot_index = md_table(
        [{"Plot": p.stem.replace("final_", "").replace("_", " "), "File": f"[plots/{p.name}](plots/{p.name})"} for p in plot_paths],
        ["Plot", "File"],
    )
    ledger_total = sum(p[1] for p in PHASE_LEDGER)
    report = f"""# LRS — Relatório Final do Estudo (Phases 0-10)

> **Status: research-only / ENCERRADO (2026-06-10).** Nada neste relatório
> autoriza deploy, paper-trade ou mudança de mandato. Mandate §1 (maintenance
> mode) inalterado. A suíte de validação foi executada (Phase 8): **0/2
> finalistas passam os 7 gates**; a linha está fechada salvo literatura ou
> regime genuinamente novos. Gerado por `lrs/final_report.py`.

## 1. O estudo em uma página

Pergunta original: *existe estratégia com ETFs alavancados que supere a LRS
200d SMA?* Resposta após {ledger_total} trials pré-registrados em 18 etapas:

- **Sim, em mecanismo:** o ensemble multi-lookback (7A) destravou o gate
  vinculante walk-forward no SPY pela primeira vez (13/17 = 76,5% ≥ 75%)
  `[systematic_trading, p.118-119, p.129-133]`, e o vol-targeting quadrático
  (7D) moveu o QQQ (8/11) `[volatility_trading, p.135, p.138-140]`.
- **Não, em validação:** na suíte completa (Phase 8, `n_trials = 4377` na
  época; ledger final {ledger_total}), o SPY ensemble fez 6/7 e morreu no DSR
  por p `0,052` vs `0,05` — com undercount honesto (letf-lab fora do ledger).
  "Quase lá" não passa `[advances_fin_ml, p.273-275]`.
- **Drivers reais** (na ordem em que foram descobertos): geometria de
  exposição (alavancagem-alvo 1.75-2x + risk-off diversificado ZROZ/GLD/IEF +
  throttle de vol) `[leverage_for_the_long_run, p.4-7]`; suavização entre
  janelas (7A); sizing por inverso da variância (7D).
- **O que NÃO funciona** (tudo FAIL honesto): filtros AND (3A), formas de
  regime alternativas (3A-2), janelas/adaptativo (3C), sleeve inversa (6D),
  portfólio EW de rotações (7B), gate macro como switch binário (7C — conserta
  o WF mas explode o MDD), composição de mecanismos (7F), teto 3x cheio (P9) e
  **buy-the-dip alavancado (P10 — zero rows entre 144 seguram MDD ≥ −50%;
  a tese Gayed sobrevive à própria inversão** `[leverage_for_the_long_run,
  p.7-9]`, `[trading_systems_methods, p.13]`).

## 2. Status atual — validação

| Config | G1 PBO | G2 DSR p | G3 WF | G4-G7 | Geral |
|---|---|---|---|---|---|
| `spy_7a_ensemble` | 0,397 ✅ | **0,052 ❌** | 13/17 ✅ | ✅✅✅✅ | **FAIL 6/7** |
| `qqq_7d_quadratic` | 0,651 ❌ | 0,138 ❌ | 8/11 ❌ | ✅✅✅✅ | **FAIL 4/7** |

Veredito da linha: **a geometria de timing alavancado é real — o gate
vinculante foi destravado — mas o edge é pequeno demais para sobreviver ao
accounting honesto de múltiplos testes.** O RSC-US 35/40/25 estático segue
como âncora limpa do repo; a tabela de mix da 6A continua disponível para a
decisão static×satélite `[risk_parity, p.80-81]`, `[advances_fin_ml,
p.208-211]`.

## 3. Finalistas — lente time-weighted e lente de aportes

Time-weighted (after-tax, DARF anual) e money-weighted (aportes de
${INITIAL:,.0f} + ${MONTHLY:,.0f}/mês na própria curva after-tax; path MDD é
mecanicamente suavizado por inflows — divulgado, precedente 6A Part 2):

{md_table(rows, list(rows[0].keys()))}

Benchmarks (mesmas lentes):

{md_table(bench_rows, list(bench_rows[0].keys()))}

**Status de cada finalista:** F1 reprovou a suíte (6/7, DSR); F2 e F3 nunca
rodaram a suíte e enfrentariam ledger ≥ {ledger_total} (odds registradas como
baixas — o DSR matou candidato com risco-ajustado melhor). Uso com capital é
decisão pessoal fora do mandate (§7); nenhum é candidato a deploy do repo.

## 4. Fichas operacionais

### F1 `spy_7a_ensemble` — o mais robusto (6/7 gates)

- **Regra semanal (1º pregão):** fração risk-on `f = (nº de SMAs de
  {{150,175,200,225}} com SPY acima) / 4`, zerada se RV21 > 30% a.a.;
  carteira-alvo = `f` × [25% SPY + 75% SSO] + `(1-f)` × [40% ZROZ + 40% GLD +
  20% IEF]; executar com 2 dias de lag via caixa.
- Posições: SPY/SSO/ZROZ/GLD/IEF + caixa. Turnover ~{f1_sum["turnover_per_year"]:.0f}/ano.
- Caveat: MDD −43% e ~1pp de CAGR abaixo da headline binária; a vantagem é
  consistência entre janelas (13/17).

### F2 `spy_p9_cap2.5x` — o de maior ganho dentro do teto

- **Regra semanal:** acima da SMA200 do SPY, alavancagem-alvo
  `L = clip((40% / RV21)², 0, 2.5)` quantizada em degraus de 0,25 (inércia:
  só muda se o alvo desviar ≥ 0,25); expressa por mix SPY/SSO/UPRO (a 2,5x =
  50% SSO + 50% UPRO). Abaixo da SMA200: 50% ZROZ + 25% GLD + 25% caixa.
  Lag 3 dias.
- Na prática fica ~99% do tempo risk-on no teto 2,5x (σ40 quase nunca binda):
  comporta-se como "2,5x constante + saída em pânico". Turnover ~{f2_sum["turnover_per_year"]:.0f}/ano.
- Caveat: nunca validado; o ganho vem da alavancagem, não do sizing.

### F3 `qqq_l2_binary` — melhor Calmar do grid, branch frágil

- **Regra semanal:** QQQ acima da SMA200 E RV63 ≤ 40% → 100% QLD (2x);
  senão → 50% ZROZ + 50% GLD. Lag 1 dia.
- Turnover ~{f3_sum["turnover_per_year"]:.0f}/ano. Caveat sério: a branch QQQ reprovou PBO
  (0,64) e DSR na Phase 4 — 40 anos dominados pela era tech; o risco de
  overfit é o maior dos três.

## 5. Linha do tempo do estudo (ledger {ledger_total})

{md_table([{"Etapa": p[0], "Trials": f"+{p[1]}", "Veredito": p[2]} for p in PHASE_LEDGER], ["Etapa", "Trials", "Veredito"])}

## 6. Plots

{plot_index}

## 7. Referências

Fases e memórias: `lrs/phases/phase00_*..phase10_*`, `lrs/MEMORY.md`,
`lrs/CONCLUSION.md` (comparação com RSC), `lrs/NEXT_STEPS.md`. Citações-chave:
`[leverage_for_the_long_run, p.4-9, p.13-16]`, `[systematic_trading,
p.118-133, p.137-148]`, `[volatility_trading, p.135-140]`,
`[trading_systems_methods, p.13, p.383, p.939]`, `[testing_tuning,
p.318-335]`, `[advances_fin_ml, p.208-216, p.273-275]`.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(f"Final report written: {REPORT} ({len(plot_paths)} plot files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
