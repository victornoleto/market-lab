from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
REDDIT = ROOT / "b4v2_reddit"
GLOBAL = ROOT / "b4v2_global"

BS = {
    "benchmark": "#000",
    "primary": "#0d6efd",
    "secondary": "#dc3545",
    "green": "#198754",
    "yellow": "#ffc107",
    "teal": "#20c997",
    "cyan": "#0dcaf0",
    "indigo": "#6610f2",
    "purple": "#6f42c1",
    "pink": "#d63384",
    "orange": "#fd7e14",
}


def _read_equity(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    return df.set_index("date").sort_index()


def _drawdown(equity: pd.DataFrame) -> pd.DataFrame:
    return equity / equity.cummax() - 1.0


def _rolling_relative_wealth(equity: pd.DataFrame, benchmark: str, years: int) -> pd.DataFrame:
    periods = int(round(years * 252))
    rel = equity.div(equity[benchmark], axis=0)
    return rel / rel.shift(periods) - 1.0


def _rolling_cagr_spread(equity: pd.DataFrame, benchmark: str, years: int) -> pd.DataFrame:
    periods = int(round(years * 252))
    out = pd.DataFrame(index=equity.index)
    bench = (equity[benchmark] / equity[benchmark].shift(periods)) ** (1.0 / years) - 1.0
    for col in equity.columns:
        if col == benchmark:
            continue
        cagr = (equity[col] / equity[col].shift(periods)) ** (1.0 / years) - 1.0
        out[col] = cagr - bench
    return out


def _max_drawdown(paths: np.ndarray) -> np.ndarray:
    peaks = np.maximum.accumulate(paths, axis=1)
    drawdowns = paths / peaks - 1.0
    return drawdowns.min(axis=1)


def _block_bootstrap_paths(
    equity: pd.DataFrame,
    columns: list[str],
    years: int = 20,
    n_paths: int = 1000,
    block_size: int = 21,
    seed: int = 20260525,
) -> np.ndarray:
    returns = equity[columns].pct_change().dropna().to_numpy(dtype=np.float64)
    horizon = int(round(years * 252))
    rng = np.random.default_rng(seed)
    paths = np.empty((n_paths, horizon + 1, len(columns)), dtype=np.float32)
    paths[:, 0, :] = 1.0

    max_start = returns.shape[0] - block_size
    if max_start <= 0:
        raise ValueError("Not enough observations for block bootstrap")

    for i in range(n_paths):
        sampled_indices: list[int] = []
        while len(sampled_indices) < horizon:
            start = int(rng.integers(0, max_start + 1))
            sampled_indices.extend(range(start, start + block_size))
        sampled = returns[np.array(sampled_indices[:horizon])]
        paths[i, 1:, :] = np.cumprod(1.0 + sampled, axis=0, dtype=np.float64)
    return paths


def _monte_carlo_summary(
    paths: np.ndarray,
    columns: list[str],
    benchmark: str,
    years: int,
    n_paths: int,
    block_size: int,
    seed: int,
    output: Path,
) -> pd.DataFrame:
    terminals = paths[:, -1, :]
    cagrs = terminals ** (1.0 / years) - 1.0
    mdds = _max_drawdown(paths)
    benchmark_i = columns.index(benchmark)

    rows: list[dict[str, float | int | str]] = []
    for i, col in enumerate(columns):
        rows.append(
            {
                "portfolio": col,
                "years": years,
                "n_paths": n_paths,
                "block_size_days": block_size,
                "seed": seed,
                "terminal_p10": float(np.quantile(terminals[:, i], 0.10)),
                "terminal_median": float(np.quantile(terminals[:, i], 0.50)),
                "terminal_p90": float(np.quantile(terminals[:, i], 0.90)),
                "cagr_p10": float(np.quantile(cagrs[:, i], 0.10)),
                "cagr_median": float(np.quantile(cagrs[:, i], 0.50)),
                "cagr_p90": float(np.quantile(cagrs[:, i], 0.90)),
                "mdd_p10": float(np.quantile(mdds[:, i], 0.10)),
                "mdd_median": float(np.quantile(mdds[:, i], 0.50)),
                "mdd_p90": float(np.quantile(mdds[:, i], 0.90)),
                "prob_terminal_under_benchmark": float(np.mean(terminals[:, i] < terminals[:, benchmark_i])),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(output, index=False)
    return df


def _setup_ax(ax: plt.Axes, title: str, ylabel: str) -> None:
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.grid(True, which="major", alpha=0.22, linewidth=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _plot_lines(
    equity: pd.DataFrame,
    columns: list[str],
    colors: dict[str, str],
    path: Path,
    title: str,
    ylabel: str,
    logy: bool = False,
    styles: dict[str, str] | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(11, 6.2))
    for col in columns:
        ax.plot(
            equity.index,
            equity[col],
            label=col,
            color=colors[col],
            linewidth=2.3 if colors[col] != BS["benchmark"] else 2.6,
            linestyle=(styles or {}).get(col, "-"),
        )
    if logy:
        ax.set_yscale("log")
    _setup_ax(ax, title, ylabel)
    ax.legend(frameon=False, ncol=2, fontsize=9)
    _save(fig, path)


def _plot_drawdowns(
    equity: pd.DataFrame,
    columns: list[str],
    colors: dict[str, str],
    path: Path,
    title: str,
    styles: dict[str, str] | None = None,
) -> None:
    dd = _drawdown(equity[columns])
    fig, ax = plt.subplots(figsize=(11, 6.2))
    for col in columns:
        ax.plot(
            dd.index,
            dd[col] * 100.0,
            label=col,
            color=colors[col],
            linewidth=2.1 if colors[col] != BS["benchmark"] else 2.5,
            linestyle=(styles or {}).get(col, "-"),
        )
    _setup_ax(ax, title, "Drawdown (%)")
    ax.legend(frameon=False, ncol=2, fontsize=9)
    _save(fig, path)


def _plot_rolling_grid(
    equity: pd.DataFrame,
    benchmark: str,
    columns: list[str],
    colors: dict[str, str],
    path: Path,
    title: str,
    mode: str,
) -> None:
    horizons = [3, 5, 10, 15]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.2), sharex=False)
    for ax, years in zip(axes.ravel(), horizons):
        if mode == "relative_wealth":
            data = _rolling_relative_wealth(equity[[benchmark, *columns]], benchmark, years)[columns]
            ylabel = "Rel. wealth vs benchmark (%)"
            base = 0.0
        elif mode == "cagr_spread":
            data = _rolling_cagr_spread(equity[[benchmark, *columns]], benchmark, years)[columns]
            ylabel = "CAGR spread (pp)"
            base = 0.0
        else:
            raise ValueError(mode)

        ax.axhline(base, color=BS["benchmark"], linewidth=1.4, alpha=0.85)
        for col in columns:
            ax.plot(data.index, data[col] * 100.0, label=col, color=colors[col], linewidth=1.9)
        _setup_ax(ax, f"{years}y rolling", ylabel)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.suptitle(title, x=0.02, y=0.995, ha="left", fontsize=14, fontweight="bold")
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.55, 0.99), ncol=3, frameon=False, fontsize=9)
    _save(fig, path)


def _plot_monte_carlo_fan(
    paths: np.ndarray,
    columns: list[str],
    colors: dict[str, str],
    path: Path,
    title: str,
    years: int,
    band_columns: list[str],
    styles: dict[str, str] | None = None,
) -> None:
    x = np.linspace(0.0, years, paths.shape[1])
    fig, ax = plt.subplots(figsize=(11, 6.2))
    for col in band_columns:
        i = columns.index(col)
        p10 = np.quantile(paths[:, :, i], 0.10, axis=0)
        p90 = np.quantile(paths[:, :, i], 0.90, axis=0)
        ax.fill_between(x, p10, p90, color=colors[col], alpha=0.12, linewidth=0)

    for col in columns:
        i = columns.index(col)
        median = np.quantile(paths[:, :, i], 0.50, axis=0)
        ax.plot(
            x,
            median,
            label=f"{col} median",
            color=colors[col],
            linewidth=2.4 if colors[col] != BS["benchmark"] else 2.7,
            linestyle=(styles or {}).get(col, "-"),
        )

    ax.set_yscale("log")
    ax.set_xlabel("Simulated years")
    ax.set_ylabel("Growth of $1 (log scale)")
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold")
    ax.grid(True, which="major", alpha=0.22, linewidth=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, ncol=2, fontsize=9)
    _save(fig, path)


def regenerate_reddit_plots() -> None:
    full = _read_equity(REDDIT / "series" / "full_equity_curves.csv")
    full_colors = {
        "100% SPY": BS["benchmark"],
        "B4-v2 35/40/25": BS["primary"],
        "B4 original 25/25/25/25": BS["secondary"],
    }
    full_cols = ["100% SPY", "B4-v2 35/40/25", "B4 original 25/25/25/25"]
    _plot_lines(
        full,
        full_cols,
        full_colors,
        REDDIT / "plots" / "01_full_equity_log.png",
        "1988+ equity curves",
        "Growth of $1 (log scale)",
        logy=True,
    )

    relative = pd.DataFrame(index=full.index)
    relative["B4-v2 35/40/25"] = full["B4-v2 35/40/25"] / full["100% SPY"]
    relative["B4 original 25/25/25/25"] = full["B4 original 25/25/25/25"] / full["100% SPY"]
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.axhline(1.0, color=BS["benchmark"], linewidth=1.5, alpha=0.9, label="SPY baseline")
    for col in ["B4-v2 35/40/25", "B4 original 25/25/25/25"]:
        ax.plot(relative.index, relative[col], color=full_colors[col], linewidth=2.3, label=col)
    _setup_ax(ax, "1988+ relative wealth vs SPY", "Wealth / SPY wealth")
    ax.legend(frameon=False, ncol=2, fontsize=9)
    _save(fig, REDDIT / "plots" / "02_full_equity_vs_spy.png")

    impl = _read_equity(REDDIT / "series" / "implementation_equity_curves.csv")
    impl_cols = [
        "100% SPY",
        "35/40/25 core",
        "35/20/20/25 MF split",
        "10% RSSX + MF split",
        "17.5% RSSX + MF split",
    ]
    impl_colors = {
        "100% SPY": BS["benchmark"],
        "35/40/25 core": BS["primary"],
        "35/20/20/25 MF split": BS["secondary"],
        "10% RSSX + MF split": BS["green"],
        "17.5% RSSX + MF split": BS["yellow"],
    }
    _plot_lines(
        impl,
        impl_cols,
        impl_colors,
        REDDIT / "plots" / "03_implementation_equity_log.png",
        "Post-2010 implementation variants",
        "Growth of $1 (log scale)",
        logy=True,
    )

    impl_rel = impl[impl_cols].div(impl["100% SPY"], axis=0)
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.axhline(1.0, color=BS["benchmark"], linewidth=1.5, alpha=0.9, label="SPY baseline")
    for col in impl_cols[1:]:
        ax.plot(impl_rel.index, impl_rel[col], color=impl_colors[col], linewidth=2.2, label=col)
    _setup_ax(ax, "Post-2010 relative wealth vs SPY", "Wealth / SPY wealth")
    ax.legend(frameon=False, ncol=2, fontsize=9)
    _save(fig, REDDIT / "plots" / "04_implementation_equity_vs_spy.png")

    _plot_drawdowns(
        impl,
        impl_cols,
        impl_colors,
        REDDIT / "plots" / "05_implementation_drawdowns.png",
        "Post-2010 implementation drawdowns",
    )

    rolling_cols = ["B4-v2 35/40/25", "B4 original 25/25/25/25"]
    _plot_rolling_grid(
        full,
        "100% SPY",
        rolling_cols,
        full_colors,
        REDDIT / "plots" / "06_rolling_relative_wealth_2x2.png",
        "Rolling relative wealth vs SPY",
        "relative_wealth",
    )
    _plot_rolling_grid(
        full,
        "100% SPY",
        rolling_cols,
        full_colors,
        REDDIT / "plots" / "07_rolling_cagr_spread_2x2.png",
        "Rolling CAGR spread vs SPY",
        "cagr_spread",
    )

    mc_years = 20
    mc_paths = _block_bootstrap_paths(full, full_cols, years=mc_years, seed=20260525)
    _monte_carlo_summary(
        mc_paths,
        full_cols,
        "100% SPY",
        years=mc_years,
        n_paths=mc_paths.shape[0],
        block_size=21,
        seed=20260525,
        output=REDDIT / "monte_carlo_sequence_risk.csv",
    )
    _plot_monte_carlo_fan(
        mc_paths,
        full_cols,
        full_colors,
        REDDIT / "plots" / "08_monte_carlo_20y_sequence_risk.png",
        "20-year Monte Carlo sequence-risk simulation",
        mc_years,
        band_columns=["100% SPY", "B4-v2 35/40/25", "B4 original 25/25/25/25"],
    )


def regenerate_global_plots() -> None:
    equity = _read_equity(GLOBAL / "series" / "global_selected_equity.csv")
    cols = [
        "66/34 VTI/VEA",
        "100% VT",
        "Global simple NTSD/RSIT",
        "Global 66/34 lead",
        "Global 60/40 lead",
        "US B4-v2 35/40/25",
    ]
    colors = {
        "66/34 VTI/VEA": BS["benchmark"],
        "100% VT": BS["benchmark"],
        "Global simple NTSD/RSIT": BS["primary"],
        "Global 66/34 lead": BS["secondary"],
        "Global 60/40 lead": BS["green"],
        "US B4-v2 35/40/25": BS["yellow"],
    }
    styles = {"100% VT": "--"}
    _plot_lines(
        equity,
        cols,
        colors,
        GLOBAL / "plots" / "01_global_equity_log.png",
        "Global B4-v2 candidates vs benchmarks",
        "Growth of $1 (log scale)",
        logy=True,
        styles=styles,
    )

    for benchmark, file_name, title in [
        ("66/34 VTI/VEA", "02_global_equity_vs_66_34.png", "Relative wealth vs 66/34 VTI/VEA"),
        ("100% VT", "03_global_equity_vs_vt.png", "Relative wealth vs 100% VT"),
    ]:
        rel_cols = [c for c in cols if c != benchmark]
        if benchmark == "66/34 VTI/VEA":
            rel_cols = [c for c in rel_cols if c != "100% VT"]
        fig, ax = plt.subplots(figsize=(11, 6.2))
        ax.axhline(1.0, color=BS["benchmark"], linewidth=1.5, alpha=0.9, label=f"{benchmark} baseline")
        for col in rel_cols:
            ax.plot(equity.index, equity[col] / equity[benchmark], color=colors[col], linewidth=2.2, linestyle=styles.get(col, "-"), label=col)
        _setup_ax(ax, title, "Wealth / benchmark wealth")
        ax.legend(frameon=False, ncol=2, fontsize=9)
        _save(fig, GLOBAL / "plots" / file_name)

    _plot_drawdowns(
        equity,
        cols,
        colors,
        GLOBAL / "plots" / "04_global_drawdowns.png",
        "Global B4-v2 candidate drawdowns",
        styles=styles,
    )
    _plot_rolling_grid(
        equity,
        "66/34 VTI/VEA",
        ["Global simple NTSD/RSIT", "Global 66/34 lead", "Global 60/40 lead", "US B4-v2 35/40/25"],
        colors,
        GLOBAL / "plots" / "05_global_rolling_relative_wealth_2x2.png",
        "Rolling relative wealth vs 66/34 VTI/VEA",
        "relative_wealth",
    )

    mc_years = 20
    mc_cols = ["66/34 VTI/VEA", "Global simple NTSD/RSIT", "Global 66/34 lead", "Global 60/40 lead", "US B4-v2 35/40/25"]
    mc_paths = _block_bootstrap_paths(equity, mc_cols, years=mc_years, seed=20260526)
    _monte_carlo_summary(
        mc_paths,
        mc_cols,
        "66/34 VTI/VEA",
        years=mc_years,
        n_paths=mc_paths.shape[0],
        block_size=21,
        seed=20260526,
        output=GLOBAL / "global_monte_carlo_sequence_risk.csv",
    )
    _plot_monte_carlo_fan(
        mc_paths,
        mc_cols,
        colors,
        GLOBAL / "plots" / "06_global_monte_carlo_20y_sequence_risk.png",
        "20-year Monte Carlo sequence-risk simulation",
        mc_years,
        band_columns=["66/34 VTI/VEA", "Global simple NTSD/RSIT", "Global 66/34 lead"],
    )


def main() -> None:
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "legend.fontsize": 9,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )
    regenerate_reddit_plots()
    regenerate_global_plots()


if __name__ == "__main__":
    main()
