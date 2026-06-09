"""Phase 6D - capped inverse sleeve inside risk-off (DIAGNOSTIC).

Research-only. Unblocks the deferred bear-sleeve idea by synthesizing inverse
daily returns locally (`r_inv = -r_underlying - 0.0095/252`, the repo's
negative-leverage synthesis convention with daily reset and fee drag
`[leverage_for_the_long_run, p.16, fn.22-23]`) and blending a capped fraction
`f` into the headline risk-off sleeves: `risk_off' = (1-f)*risk_off + f*{INV}`.
The short side of a trend rule is citable and a known underperformer, hence the
small cap `[trading_systems_methods, p.354]`, `[systematic_trading,
p.137-148]`. Pre-registered grid: 36 rows (2 branches x f in {10,15,25%} x lag
0..5); +36 to the n_trials ledger (3948 -> 3984 including Phase 6B). Screen read
at the committed headline lag. No deployment, no paper-trade label, no mandate
change.
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
    clean_weights,
    equity_curve,
    fmt_num,
    fmt_pct,
    fmt_pp,
    md_table,
    metrics_from_returns,
)
from lrs.phases.phase04_validation_gates import run as phase04  # noqa: E402


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase06d_inverse_sleeve.csv"

INVERSE_FEE_ANNUAL = 0.0095  # `[leverage_for_the_long_run, p.16, fn.23]`
INVERSE_FRACTIONS = [0.10, 0.15, 0.25]
MAX_INVERSE_FRACTION = 0.25
LAGS = list(range(6))
N_TRIALS_ADDED = len(INVERSE_FRACTIONS) * len(LAGS) * 2  # 36

# Pre-registered crisis windows (shared with Phase 6A).
CRISIS_WINDOWS: list[tuple[str, str, str]] = [
    ("dotcom", "2000-03-24", "2002-10-09"),
    ("gfc", "2007-10-09", "2009-03-09"),
    ("covid", "2020-02-19", "2020-03-23"),
    ("2022", "2022-01-03", "2022-10-12"),
]

BRANCH_SPECS: list[dict[str, object]] = [
    {
        "branch": "SPY",
        "target_leverage": 2.00,
        "risk_off": "50 ZROZ / 25 GLD / 25 CASH",
        "vol": "RV21 <= 30%",
        "headline_lag": 3,
        "inverse_asset": "SPYINVSIM",
    },
    {
        "branch": "QQQ",
        "target_leverage": 1.75,
        "risk_off": "40 ZROZ / 40 GLD / 20 IEF",
        "vol": "RV63 <= 40%",
        "headline_lag": 0,
        "inverse_asset": "QQQINVSIM",
    },
]


def synthesize_inverse_returns(underlying_returns: pd.Series, fee: float = INVERSE_FEE_ANNUAL) -> pd.Series:
    """Daily-reset -1x returns with annual fee drag (in-memory; cache untouched).

    Mirrors the repo's `_synth_leveraged_returns` convention for negative
    leverage `[leverage_for_the_long_run, p.16, fn.22-23]`.
    """
    return (-1.0 * underlying_returns - fee / 252.0).rename("inverse")


def blend_risk_off(base_weights: dict[str, float], inverse_asset: str, fraction: float) -> dict[str, float]:
    """`risk_off' = (1-f)*risk_off + f*{INV}`, with the pre-registered cap."""
    if fraction < 0.0 or fraction > MAX_INVERSE_FRACTION:
        raise ValueError(f"inverse fraction out of range [0, {MAX_INVERSE_FRACTION}]: {fraction}")
    blended = {asset: weight * (1.0 - fraction) for asset, weight in base_weights.items()}
    if fraction > 0.0:
        blended[inverse_asset] = fraction
    return clean_weights(blended)


def crisis_window_stats(returns: pd.Series, windows: list[tuple[str, str, str]] = CRISIS_WINDOWS) -> dict[str, float]:
    """Total return and segment MDD inside each pre-registered crisis window."""
    out: dict[str, float] = {}
    for name, start, end in windows:
        seg = returns.loc[(returns.index >= pd.Timestamp(start)) & (returns.index <= pd.Timestamp(end))]
        arr = seg.to_numpy(dtype=float)
        if len(arr) == 0:
            out[f"crisis_{name}_ret"] = float("nan")
            out[f"crisis_{name}_mdd"] = float("nan")
            continue
        equity = np.cumprod(1.0 + arr)
        peak = np.maximum.accumulate(equity)
        out[f"crisis_{name}_ret"] = float(equity[-1] - 1.0)
        out[f"crisis_{name}_mdd"] = float(-(1.0 - equity / peak).max())
    return out


def build_context_with_inverse(spec: dict[str, object]) -> "phase04.BranchContext":
    branch = phase04.BRANCHES[str(spec["branch"])]
    context = phase04.build_context(branch)
    inverse = synthesize_inverse_returns(context.returns[branch["underlying"]])
    context.returns[str(spec["inverse_asset"])] = inverse
    return context


def evaluate_grid(spec: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, pd.Series]]:
    context = build_context_with_inverse(spec)
    risk_off = next(r for r in phase04.RISK_OFF_SPECS if r["name"] == spec["risk_off"])
    vol_spec = next(v for v in phase04.VOL_SPECS if v["name"] == spec["vol"])
    base_weights = clean_weights(dict(risk_off["weights"]))  # type: ignore[arg-type]

    rows: list[dict[str, object]] = []
    return_map: dict[str, pd.Series] = {}
    headline_by_lag: dict[int, dict[str, float]] = {}

    for fraction in [0.0, *INVERSE_FRACTIONS]:
        blended = blend_risk_off(base_weights, str(spec["inverse_asset"]), fraction)
        for lag in LAGS:
            taxed = phase04.simulate_returns(
                context, float(spec["target_leverage"]), blended, vol_spec, lag
            )
            metrics = metrics_from_returns(taxed)
            key = f"{spec['branch']}_f{int(fraction * 100):02d}_lag{lag}"
            return_map[key] = taxed
            row: dict[str, object] = {
                "config_type": "headline_f0" if fraction == 0.0 else "inverse",
                "branch": spec["branch"],
                "inverse_fraction": fraction,
                "lag_days": lag,
                "is_headline_lag": bool(lag == int(spec["headline_lag"])),
                "target_leverage": float(spec["target_leverage"]),
                "risk_off": spec["risk_off"],
                "vol_filter": spec["vol"],
                "taxed_cagr": metrics.cagr,
                "taxed_mdd": metrics.mdd,
                "taxed_sharpe": metrics.sharpe,
                "taxed_sortino": metrics.sortino,
                "taxed_calmar": metrics.calmar,
                "taxed_terminal": metrics.terminal,
                **crisis_window_stats(taxed),
            }
            if fraction == 0.0:
                headline_by_lag[lag] = {"cagr": metrics.cagr, "mdd": metrics.mdd}
            rows.append(row)

    for row in rows:
        headline = headline_by_lag[int(row["lag_days"])]
        row["headline_cagr_same_lag"] = headline["cagr"]
        row["headline_mdd_same_lag"] = headline["mdd"]
        row["pass_vs_headline"] = bool(
            row["config_type"] == "inverse"
            and float(row["taxed_cagr"]) >= headline["cagr"]
            and float(row["taxed_mdd"]) > headline["mdd"]
        )
    return rows, return_map


def sanity_f0_matches_phase04(rows: list[dict[str, object]]) -> dict[str, float]:
    """f=0 rows must reproduce the Phase 4 headline metrics byte-for-byte."""
    phase04_csv = pd.read_csv(RESULTS / "phase04_validation_gates.csv")
    deltas: dict[str, float] = {}
    for base_name, branch, lag in (("spy_top", "SPY", 3), ("qqq_top", "QQQ", 0)):
        saved = phase04_csv[phase04_csv["base_name"] == base_name].iloc[0]
        local = next(
            r for r in rows
            if r["branch"] == branch and r["config_type"] == "headline_f0" and int(r["lag_days"]) == lag
        )
        deltas[base_name] = max(
            abs(float(local["taxed_cagr"]) - float(saved["taxed_cagr"])),
            abs(float(local["taxed_mdd"]) - float(saved["taxed_mdd"])),
        )
    return deltas


def branch_screen(frame: pd.DataFrame, branch: str, headline_lag: int) -> dict[str, object]:
    """Pre-registered: verdict read at the committed headline lag only."""
    at_lag = frame[
        (frame["branch"] == branch)
        & (frame["config_type"] == "inverse")
        & (frame["lag_days"] == headline_lag)
    ]
    passing = at_lag[at_lag["pass_vs_headline"]]
    best = at_lag.sort_values("taxed_calmar", ascending=False).iloc[0]
    headline = frame[
        (frame["branch"] == branch)
        & (frame["config_type"] == "headline_f0")
        & (frame["lag_days"] == headline_lag)
    ].iloc[0]
    return {
        "branch": branch,
        "headline_lag": headline_lag,
        "n_passing_at_lag": int(len(passing)),
        "best": best,
        "headline": headline,
        "success": bool(len(passing) > 0),
    }


# --------------------------------------------------------------------------- plots


def plot_equity_dd(return_map: dict[str, pd.Series], screens: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, len(screens), figsize=(7.5 * len(screens), 8.5), squeeze=False)
    for col, screen in enumerate(screens):
        branch = str(screen["branch"])
        lag = int(screen["headline_lag"])
        best_f = float(screen["best"]["inverse_fraction"])
        pair = pd.concat(
            {
                f"f={best_f:.0%}": return_map[f"{branch}_f{int(best_f * 100):02d}_lag{lag}"],
                "f=0 (headline)": return_map[f"{branch}_f00_lag{lag}"],
            },
            axis=1,
        ).dropna()
        eq = pair.apply(equity_curve)
        eq.plot(ax=axes[0][col], logy=True, linewidth=1.1)
        axes[0][col].set_title(f"{branch} lag {lag}: after-tax equity")
        axes[0][col].grid(True, alpha=0.3)
        dd = eq / eq.cummax() - 1.0
        (dd * 100.0).plot(ax=axes[1][col], linewidth=1.0)
        axes[1][col].set_title(f"{branch}: drawdown (%)")
        axes[1][col].grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase06d_equity_dd.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_crisis_zoom(return_map: dict[str, pd.Series], screens: list[dict[str, object]]) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(screens), len(CRISIS_WINDOWS), figsize=(4.2 * len(CRISIS_WINDOWS), 3.6 * len(screens)), squeeze=False)
    for row_i, screen in enumerate(screens):
        branch = str(screen["branch"])
        lag = int(screen["headline_lag"])
        best_f = float(screen["best"]["inverse_fraction"])
        series = {
            f"f={best_f:.0%}": return_map[f"{branch}_f{int(best_f * 100):02d}_lag{lag}"],
            "f=0": return_map[f"{branch}_f00_lag{lag}"],
        }
        for col_i, (name, start, end) in enumerate(CRISIS_WINDOWS):
            ax = axes[row_i][col_i]
            for label, returns in series.items():
                seg = returns.loc[(returns.index >= pd.Timestamp(start)) & (returns.index <= pd.Timestamp(end))]
                if seg.empty:
                    continue
                ax.plot(seg.index, equity_curve(seg).to_numpy(dtype=float), linewidth=1.0, label=label)
            ax.set_title(f"{branch} {name}", fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis="x", labelsize=6, rotation=30)
            if col_i == 0:
                ax.legend(fontsize=7)
    fig.suptitle("Phase 6D: crisis-window equity (normalized at window start)")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out = PLOTS / "phase06d_crisis_zoom.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_f_sensitivity(frame: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), squeeze=False)
    for ax, branch in zip(axes[0], ["SPY", "QQQ"]):
        sub = frame[(frame["branch"] == branch) & frame["is_headline_lag"]].sort_values("inverse_fraction")
        ax2 = ax.twinx()
        ax.plot(sub["inverse_fraction"] * 100.0, sub["taxed_cagr"] * 100.0, "o-", color="tab:blue", label="CAGR")
        ax2.plot(sub["inverse_fraction"] * 100.0, sub["taxed_mdd"] * 100.0, "s--", color="tab:red", label="MDD")
        ax.set_title(f"{branch} (headline lag): CAGR / MDD vs inverse fraction")
        ax.set_xlabel("Inverse fraction of risk-off (%)")
        ax.set_ylabel("After-tax CAGR (%)", color="tab:blue")
        ax2.set_ylabel("MDD (%)", color="tab:red")
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase06d_f_sensitivity.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------- report


def grid_table(frame: pd.DataFrame, branch: str) -> str:
    sub = frame[(frame["branch"] == branch) & frame["is_headline_lag"]].sort_values("inverse_fraction")
    rows = [
        {
            "f": fmt_pct(r["inverse_fraction"], 0),
            "CAGR": fmt_pct(r["taxed_cagr"]),
            "MDD": fmt_pct(r["taxed_mdd"]),
            "Sharpe": fmt_num(r["taxed_sharpe"]),
            "Calmar": fmt_num(r["taxed_calmar"]),
            "GFC ret": fmt_pct(r["crisis_gfc_ret"]),
            "COVID ret": fmt_pct(r["crisis_covid_ret"]),
            "2022 ret": fmt_pct(r["crisis_2022_ret"]),
            "Pass": "yes" if r.get("pass_vs_headline") else ("-" if r["config_type"] == "headline_f0" else "no"),
        }
        for _, r in sub.iterrows()
    ]
    return md_table(rows, ["f", "CAGR", "MDD", "Sharpe", "Calmar", "GFC ret", "COVID ret", "2022 ret", "Pass"])


def lag_sensitivity_table(frame: pd.DataFrame, branch: str) -> str:
    sub = frame[(frame["branch"] == branch) & (frame["config_type"] == "inverse")]
    rows = []
    for fraction, group in sub.groupby("inverse_fraction"):
        n_pass = int(group["pass_vs_headline"].sum())
        rows.append(
            {
                "f": fmt_pct(float(fraction), 0),
                "Lags passing": f"{n_pass}/{len(group)}",
                "Best lag CAGR": fmt_pct(group["taxed_cagr"].max()),
                "Worst lag MDD": fmt_pct(group["taxed_mdd"].min()),
            }
        )
    return md_table(rows, ["f", "Lags passing", "Best lag CAGR", "Worst lag MDD"])


def write_report(frame: pd.DataFrame, screens: list[dict[str, object]], sanity: dict[str, float], plot_rows: list[dict[str, str]]) -> None:
    n_success = sum(1 for s in screens if s["success"])
    sections = [
        "# Phase 6D - Inverse Sleeve In Risk-Off (DIAGNOSTIC)\n\n"
        "Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.\n\n"
        "Blends a capped synthetic inverse position (`r_inv = -r_underlying - 0.0095/252`, daily reset, in-memory only `[leverage_for_the_long_run, p.16, fn.22-23]`) into the headline risk-off sleeves: `risk_off' = (1-f)*risk_off + f*{INV}` `[trading_systems_methods, p.354]`, `[systematic_trading, p.137-148]`. Headline geometry and binary vol gate unchanged - the risk-off composition is the single mechanism family under test.\n\n"
        f"Pre-registered grid: 2 branches x f in {{10%, 15%, 25%}} x lag 0..5 = {N_TRIALS_ADDED} rows (+{N_TRIALS_ADDED} to the n_trials ledger -> 3984 cumulative with Phase 6B). Screen read at the committed headline lag (SPY 3, QQQ 0); other lags are sensitivity only.\n\n"
        "## Executive Conclusion\n\n"
        f"Branches passing the pre-registered screen (CAGR >= headline AND MDD strictly better, at the headline lag): **{n_success}/{len(screens)}**.\n\n"
        f"Sanity check: f=0 rows reproduce the Phase 4 headline metrics; max abs deviation spy_top `{sanity.get('spy_top', float('nan')):.2e}`, qqq_top `{sanity.get('qqq_top', float('nan')):.2e}`.\n\n",
    ]
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    for screen in screens:
        branch = str(screen["branch"])
        sections.append(f"## {branch} At Headline Lag {int(screen['headline_lag'])}\n\n" + grid_table(frame, branch))
        sections.append(f"### {branch} Lag Sensitivity\n\n" + lag_sensitivity_table(frame, branch))
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        + "".join(
            f"| {s['branch']}: does a capped inverse sleeve improve the headline? | {'Yes' if s['success'] else 'No'} ({int(s['n_passing_at_lag'])}/{len(INVERSE_FRACTIONS)} fractions pass at lag {int(s['headline_lag'])}). |\n"
            for s in screens
        )
        + f"| Screen successes? | {n_success}/{len(screens)}. |\n"
        "| Did we promote anything? | No - diagnostic only. |\n"
        "| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, object]] = []
    return_map: dict[str, pd.Series] = {}
    for spec in BRANCH_SPECS:
        rows, branch_map = evaluate_grid(spec)
        all_rows.extend(rows)
        return_map.update(branch_map)
        print(f"  {spec['branch']}: grid done")

    sanity = sanity_f0_matches_phase04(all_rows)
    frame = pd.DataFrame(all_rows)
    frame.to_csv(CSV, index=False)
    screens = [
        branch_screen(frame, str(spec["branch"]), int(spec["headline_lag"])) for spec in BRANCH_SPECS
    ]
    plots = [
        ("Equity/drawdown best-f vs f=0", plot_equity_dd(return_map, screens)),
        ("Crisis-window zoom", plot_crisis_zoom(return_map, screens)),
        ("CAGR/MDD vs inverse fraction", plot_f_sensitivity(frame)),
    ]
    plot_rows = [{"Plot": label, "File": f"[plots/{path.name}](plots/{path.name})"} for label, path in plots]
    write_report(frame, screens, sanity, plot_rows)

    for screen in screens:
        best = screen["best"]
        print(
            f"Phase 6D {screen['branch']}: best f {best['inverse_fraction']:.0%} at lag {int(screen['headline_lag'])} "
            f"CAGR {best['taxed_cagr']:.2%} (headline {screen['headline']['taxed_cagr']:.2%}) "
            f"MDD {best['taxed_mdd']:.2%} (headline {screen['headline']['taxed_mdd']:.2%}) "
            f"screen={'SUCCESS' if screen['success'] else 'FAIL'}"
        )
    print(f"  sanity f=0 vs phase04: {sanity}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
