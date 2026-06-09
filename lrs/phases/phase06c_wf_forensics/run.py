"""Phase 6C - walk-forward forensics on the Phase 4 bases (DIAGNOSTIC).

Research-only. Phase 4 closed the LRS family with the walk-forward gate (G3) as
the universal binding failure. This phase persists the per-window detail Phase 4
never wrote (one row per base x OOS window) and labels each window with
pre-registered regime tags, to answer: are the failing windows concentrated in
the `bull x low-vol` cell, where trend-timing structurally underperforms a
leveraged hold `[leverage_for_the_long_run, p.7-8]`, or scattered (regime-
incoherent edge)? Report-only: no new configs (+0 n_trials), no gate re-runs,
no reopening of the standalone line `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.211-216]`.
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

from lrs.lib.backtest import fmt_num, fmt_pct, fmt_pp, md_table  # noqa: E402
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402
from market_lab.backtest.validation import walk_forward_splits  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase06c_wf_forensics.csv"

# Pre-registered regime-vol cuts (annualized RV21), anchored on the reading
# that high realized vol degrades leveraged compounding
# `[leverage_for_the_long_run, p.4-7]`, `[volatility_trading, p.39, p.53-54]`.
RV_LOW_CUT = 0.15
RV_HIGH_CUT = 0.25
RV_WINDOW = 21
# Pre-registered headline question threshold: >=2/3 of failing windows in the
# `bull x low` cell.
HEADLINE_SHARE = 2.0 / 3.0

REGIME_CELLS = [
    "bull_low", "bull_mid", "bull_high",
    "bear_low", "bear_mid", "bear_high",
]


def total_return(returns: pd.Series) -> float:
    arr = returns.to_numpy(dtype=float)
    if len(arr) == 0:
        return 0.0
    return float(np.prod(1.0 + arr) - 1.0)


def segment_mdd(returns: pd.Series) -> float:
    """Positive-magnitude max drawdown of a return segment."""
    arr = returns.to_numpy(dtype=float)
    if len(arr) == 0:
        return 0.0
    equity = np.cumprod(1.0 + arr)
    peak = np.maximum.accumulate(equity)
    return float((1.0 - equity / peak).max())


def classify_trend(under_total_return: float) -> str:
    return "bull" if under_total_return > 0.0 else "bear"


def classify_vol(mean_rv: float, low_cut: float = RV_LOW_CUT, high_cut: float = RV_HIGH_CUT) -> str:
    if mean_rv < low_cut:
        return "low"
    if mean_rv < high_cut:
        return "mid"
    return "high"


def realized_vol_series(underlying_returns: pd.Series, window: int = RV_WINDOW) -> pd.Series:
    """Contemporaneous annualized RV for window labeling (descriptive, not a signal)."""
    return underlying_returns.rolling(window).std(ddof=0) * np.sqrt(252.0)


def window_rows(
    base_meta: dict[str, object],
    strategy: pd.Series,
    underlying: pd.Series,
    signal: pd.Series,
    realized_vol: pd.Series,
    *,
    is_size: int,
    oos_size: int,
    step: int,
) -> list[dict[str, object]]:
    """One forensic row per walk-forward OOS window (Phase 4 split geometry)."""
    aligned = pd.concat({"s": strategy, "b": underlying}, axis=1).dropna()
    s = aligned["s"]
    b = aligned["b"]
    signal = signal.reindex(aligned.index).fillna(False).astype(bool)
    realized_vol = realized_vol.reindex(aligned.index)
    rows: list[dict[str, object]] = []
    for window_idx, (_train, test) in enumerate(
        walk_forward_splits(len(aligned), is_size=is_size, oos_size=oos_size, step=step)
    ):
        seg = slice(test.start, test.stop)
        strat_ret = total_return(s.iloc[seg])
        under_ret = total_return(b.iloc[seg])
        rel = strat_ret - under_ret
        mean_rv = float(realized_vol.iloc[seg].mean())
        trend = classify_trend(under_ret)
        vol_label = classify_vol(mean_rv)
        rows.append(
            {
                **base_meta,
                "window_idx": window_idx,
                "oos_start": str(aligned.index[test.start].date()),
                "oos_end": str(aligned.index[test.stop - 1].date()),
                "strat_oos_ret": strat_ret,
                "under_oos_ret": under_ret,
                "rel_ret": rel,
                "beat": bool(rel > 0.0),
                "strat_oos_mdd": segment_mdd(s.iloc[seg]),
                "under_oos_mdd": segment_mdd(b.iloc[seg]),
                "mean_rv21": mean_rv,
                "pct_risk_on_days": float(signal.iloc[seg].mean()),
                "regime_trend": trend,
                "regime_vol": vol_label,
                "regime_cell": f"{trend}_{vol_label}",
            }
        )
    return rows


def failure_concentration(frame: pd.DataFrame) -> pd.DataFrame:
    """Beat-rate and window counts per regime cell (pooled and per branch)."""
    out: list[dict[str, object]] = []
    groups = [("ALL", frame)] + [(branch, g) for branch, g in frame.groupby("branch")]
    for label, group in groups:
        for cell in REGIME_CELLS:
            sub = group[group["regime_cell"] == cell]
            if sub.empty:
                continue
            out.append(
                {
                    "scope": label,
                    "regime_cell": cell,
                    "n_windows": int(len(sub)),
                    "n_beat": int(sub["beat"].sum()),
                    "n_fail": int((~sub["beat"]).sum()),
                    "beat_rate": float(sub["beat"].mean()),
                    "mean_rel_ret": float(sub["rel_ret"].mean()),
                }
            )
    return pd.DataFrame(out)


def headline_answer(frame: pd.DataFrame) -> dict[str, object]:
    """Pre-registered question: >=2/3 of failing windows in `bull_low`?"""
    fails = frame[~frame["beat"]]
    n_fail = int(len(fails))
    n_bull_low = int((fails["regime_cell"] == "bull_low").sum())
    n_bull = int((fails["regime_trend"] == "bull").sum())
    share_bull_low = n_bull_low / n_fail if n_fail else float("nan")
    share_bull = n_bull / n_fail if n_fail else float("nan")
    return {
        "n_fail": n_fail,
        "n_fail_bull_low": n_bull_low,
        "n_fail_bull": n_bull,
        "share_bull_low": share_bull_low,
        "share_bull": share_bull,
        "headline_yes": bool(n_fail > 0 and share_bull_low >= HEADLINE_SHARE),
    }


def build_rows() -> pd.DataFrame:
    contexts = {name: phase04.build_context(branch) for name, branch in phase04.BRANCHES.items()}
    all_rows: list[dict[str, object]] = []
    for base in phase04.BASE_SPECS:
        ctx = contexts[str(base["branch"])]
        risk_off = next(r for r in phase04.RISK_OFF_SPECS if r["name"] == base["risk_off"])
        vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == base["vol"])
        lag = phase04.best_lag_for_base(str(base["name"]))
        risk_off_weights = {k: float(v) for k, v in dict(risk_off["weights"]).items()}
        strategy = phase04.simulate_returns(
            ctx, float(base["target_leverage"]), risk_off_weights, vol_spec, lag
        )
        signal = ctx.sma_signal & phase04.vol_gate(ctx, vol_spec)
        rv = realized_vol_series(ctx.returns[ctx.branch["underlying"]])
        meta = {
            "branch": base["branch"],
            "base_name": base["name"],
            "target_leverage": float(base["target_leverage"]),
            "risk_off": base["risk_off"],
            "vol_filter": base["vol"],
            "lag_days": lag,
        }
        all_rows.extend(
            window_rows(
                meta,
                strategy,
                ctx.underlying_taxed,
                signal,
                rv,
                is_size=phase04.WF_IS_SIZE,
                oos_size=phase04.WF_OOS_SIZE,
                step=phase04.WF_STEP,
            )
        )
    return pd.DataFrame(all_rows)


# --------------------------------------------------------------------------- plots

CELL_COLORS = {
    "bull_low": "#9ecf6a",
    "bull_mid": "#4c9a6b",
    "bull_high": "#1b5e3a",
    "bear_low": "#f0b27a",
    "bear_mid": "#d65f5f",
    "bear_high": "#7d2e2e",
}


def plot_window_bars(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    bases = list(dict.fromkeys(frame["base_name"]))
    fig, axes = plt.subplots(3, 2, figsize=(15, 11), squeeze=False)
    for ax, base_name in zip(axes.ravel(), bases):
        sub = frame[frame["base_name"] == base_name].sort_values("window_idx")
        colors = [CELL_COLORS[c] for c in sub["regime_cell"]]
        edges = ["black" if not beat else "none" for beat in sub["beat"]]
        ax.bar(
            sub["window_idx"], sub["rel_ret"] * 100.0,
            color=colors, edgecolor=edges, linewidth=1.6,
        )
        ax.axhline(0, color="black", linewidth=0.8)
        beats = int(sub["beat"].sum())
        ax.set_title(f"{base_name} ({beats}/{len(sub)} beat)")
        ax.set_xlabel("OOS window")
        ax.set_ylabel("Strategy - underlying (% total)")
        ax.grid(True, alpha=0.3)
    handles = [Patch(facecolor=color, label=cell) for cell, color in CELL_COLORS.items()]
    handles.append(Patch(facecolor="white", edgecolor="black", linewidth=1.6, label="failing window"))
    fig.legend(handles=handles, loc="lower center", ncol=7, frameon=False)
    fig.suptitle("Phase 6C: per-window OOS relative return by regime cell", y=0.995)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = PLOTS / "phase06c_window_bars.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_rv_scatter(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), squeeze=False)
    for ax, (branch, sub) in zip(axes[0], frame.groupby("branch")):
        for beat, marker, color in ((True, "o", "#4c9a6b"), (False, "x", "#d65f5f")):
            pts = sub[sub["beat"] == beat]
            ax.scatter(
                pts["mean_rv21"] * 100.0, pts["rel_ret"] * 100.0,
                marker=marker, color=color, s=46, label="beat" if beat else "fail",
            )
        ax.axvline(RV_LOW_CUT * 100.0, color="gray", linestyle="--", linewidth=0.8)
        ax.axvline(RV_HIGH_CUT * 100.0, color="gray", linestyle="--", linewidth=0.8)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(f"{branch}: window mean RV21 vs OOS relative return")
        ax.set_xlabel("Mean RV21 (annualized, %)")
        ax.set_ylabel("Strategy - underlying (% total)")
        ax.grid(True, alpha=0.3)
        ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase06c_rv_scatter.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_beat_heatmap(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap

    bases = list(dict.fromkeys(frame["base_name"]))
    max_windows = int(frame["window_idx"].max()) + 1
    grid = np.full((len(bases), max_windows), np.nan)
    for i, base_name in enumerate(bases):
        sub = frame[frame["base_name"] == base_name]
        for _, row in sub.iterrows():
            grid[i, int(row["window_idx"])] = 1.0 if row["beat"] else 0.0
    starts = (
        frame[frame["base_name"] == bases[0]].sort_values("window_idx")["oos_start"].tolist()
    )
    fig, ax = plt.subplots(figsize=(13, 4.5))
    masked = np.ma.masked_invalid(grid)
    ax.imshow(masked, cmap=ListedColormap(["#d65f5f", "#4c9a6b"]), vmin=0, vmax=1, aspect="auto")
    ax.set_yticks(range(len(bases)))
    ax.set_yticklabels(bases)
    ax.set_xticks(range(max_windows))
    labels = [starts[j][:7] if j < len(starts) else "" for j in range(max_windows)]
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
    ax.set_title("Phase 6C: beat (green) / fail (red) per base x OOS window (SPY window starts)")
    fig.tight_layout()
    out = PLOTS / "phase06c_beat_heatmap.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def make_plots(frame: pd.DataFrame) -> list[dict[str, str]]:
    PLOTS.mkdir(parents=True, exist_ok=True)
    plots = [
        ("Per-window relative return by regime cell", plot_window_bars(frame)),
        ("Window mean RV21 vs relative return", plot_rv_scatter(frame)),
        ("Beat/fail heatmap", plot_beat_heatmap(frame)),
    ]
    return [{"Plot": label, "File": f"[plots/{path.name}](plots/{path.name})"} for label, path in plots]


# --------------------------------------------------------------------------- report


def concentration_table(conc: pd.DataFrame, scope: str) -> str:
    sub = conc[conc["scope"] == scope]
    rows = [
        {
            "Cell": r["regime_cell"],
            "Windows": int(r["n_windows"]),
            "Beat": int(r["n_beat"]),
            "Fail": int(r["n_fail"]),
            "Beat rate": fmt_pct(r["beat_rate"]),
            "Mean rel ret": fmt_pp(r["mean_rel_ret"]),
        }
        for _, r in sub.iterrows()
    ]
    return md_table(rows, ["Cell", "Windows", "Beat", "Fail", "Beat rate", "Mean rel ret"])


def failing_windows_table(frame: pd.DataFrame) -> str:
    fails = frame[~frame["beat"]].sort_values(["branch", "base_name", "window_idx"])
    rows = [
        {
            "Base": r["base_name"],
            "Window": f"{r['oos_start']} .. {r['oos_end']}",
            "Rel ret": fmt_pp(r["rel_ret"]),
            "Under ret": fmt_pct(r["under_oos_ret"]),
            "Mean RV21": fmt_pct(r["mean_rv21"]),
            "Risk-on days": fmt_pct(r["pct_risk_on_days"]),
            "Cell": r["regime_cell"],
        }
        for _, r in fails.iterrows()
    ]
    return md_table(rows, ["Base", "Window", "Rel ret", "Under ret", "Mean RV21", "Risk-on days", "Cell"])


def write_report(frame: pd.DataFrame, conc: pd.DataFrame, headline: dict[str, object], plot_rows: list[dict[str, str]]) -> None:
    yes = bool(headline["headline_yes"])
    sections = [
        "# Phase 6C - Walk-Forward Forensics (DIAGNOSTIC)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change. Phase 4's verdict (family closed, 0/6 gates) stands regardless of this forensic.\n\n"
        "Phase 4's binding gate was G3 walk-forward (>=75% of rolling ~3y OOS windows must beat the underlying after-tax). This phase persists the per-window detail (one row per base x window, the artifact Phase 4 never wrote) and labels each window with pre-registered regime tags, asking whether the failures concentrate where trend-timing structurally loses `[leverage_for_the_long_run, p.7-8]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.211-216]`.\n\n"
        f"Splits identical to Phase 4 (`is={phase04.WF_IS_SIZE}d / oos={phase04.WF_OOS_SIZE}d / step={phase04.WF_STEP}d`). Regime cuts pre-registered: trend = sign of underlying OOS return; vol = mean RV21 < {RV_LOW_CUT:.0%} low, {RV_LOW_CUT:.0%}-{RV_HIGH_CUT:.0%} mid, >= {RV_HIGH_CUT:.0%} high `[leverage_for_the_long_run, p.4-7]`, `[volatility_trading, p.39, p.53-54]`. No new configs: **+0 to the n_trials ledger** (lineage stays 3876).\n\n"
        "## Executive Conclusion\n\n"
        f"Failing windows: **{headline['n_fail']}** of {len(frame)} base-windows. In the `bull_low` cell: {headline['n_fail_bull_low']} ({fmt_pct(headline['share_bull_low'])}); in any `bull` cell: {headline['n_fail_bull']} ({fmt_pct(headline['share_bull'])}).\n\n"
        f"**Pre-registered headline question — do >=2/3 of failing windows fall in `bull x low-vol`? {'YES' if yes else 'NO'}.** "
        + (
            "The failure mode is the structurally expected one: the strategy pays its timing premium in calm bull windows where leveraged holding is unbeatable, and wins where downside regimes exist. This supports the satellite framing tested in Phase 6A (small sleeve, not standalone), without reversing Phase 4.\n\n"
            if yes
            else "Failures are not concentrated enough in the calm-bull cell to call the miss purely structural; the per-cell table below shows where they actually sit. The family stays closed with this additional evidence.\n\n"
        ),
    ]
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    sections.append("## Beat Rate By Regime Cell (pooled)\n\n" + concentration_table(conc, "ALL"))
    sections.append("## Beat Rate By Regime Cell (SPY)\n\n" + concentration_table(conc, "SPY"))
    sections.append("## Beat Rate By Regime Cell (QQQ)\n\n" + concentration_table(conc, "QQQ"))
    sections.append("## All Failing Windows\n\n" + failing_windows_table(frame))
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Failing windows concentrated in `bull_low` (>=2/3)? | {'Yes' if yes else 'No'} ({fmt_pct(headline['share_bull_low'])}). |\n"
        f"| Failing windows in any `bull` cell? | {fmt_pct(headline['share_bull'])}. |\n"
        "| New configs / trials added? | 0 — pure forensics on the Phase 4 bases. |\n"
        "| Did we promote anything? | No - diagnostic only. Phase 4 verdict unchanged. |\n"
        "| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    frame = build_rows()
    frame.to_csv(CSV, index=False)
    conc = failure_concentration(frame)
    headline = headline_answer(frame)
    plot_rows = make_plots(frame)
    write_report(frame, conc, headline, plot_rows)
    print(
        f"Phase 6C: {len(frame)} base-windows; {headline['n_fail']} fail; "
        f"bull_low share {headline['share_bull_low']:.1%}; bull share {headline['share_bull']:.1%}; "
        f"headline {'YES' if headline['headline_yes'] else 'NO'}"
    )
    for base_name, sub in frame.groupby("base_name"):
        print(f"  {base_name:14s} beat {int(sub['beat'].sum())}/{len(sub)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
