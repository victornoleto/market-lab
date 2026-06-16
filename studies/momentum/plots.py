"""Plot helpers for Postgres-backed momentum runs."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from studies.momentum.validation import equity_from_returns


def safe_filename(value: str) -> str:
    """Return a conservative filename stem for generated plot artifacts."""
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)


def select_finalists(results: pd.DataFrame, max_finalists: int = 30) -> pd.DataFrame:
    """Pick diagnostic rows for individual strategy plots."""
    if results.empty:
        return results.copy()
    selected: list[pd.DataFrame] = []
    selected.append(results.nlargest(min(8, len(results)), "sharpe"))
    selected.append(results.nlargest(min(8, len(results)), "calmar"))
    selected.append(results.nlargest(min(8, len(results)), "excess_cagr"))
    selected.append(results.nlargest(min(6, len(results)), "terminal"))
    for _, sub in results.groupby("universe"):
        selected.append(sub.nlargest(min(3, len(sub)), "sharpe"))
    out = pd.concat(selected, axis=0).drop_duplicates("name")
    out = out.sort_values(["sharpe", "excess_cagr"], ascending=False)
    return out.head(max_finalists).copy()


def write_aggregate_plots(results: pd.DataFrame, output_dir: Path, study_dir: Path) -> list[str]:
    """Write aggregate grid plots and return paths relative to the study dir."""
    if results.empty:
        return []
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    universes = sorted(results["universe"].dropna().unique())
    colors = dict(zip(universes, plt.cm.tab10.colors, strict=False))

    fig, ax = plt.subplots(figsize=(11, 7))
    for universe, sub in results.groupby("universe"):
        ax.scatter(
            sub["mdd"].astype(float) * 100.0,
            sub["cagr"].astype(float) * 100.0,
            s=18 + sub["top_n"].astype(float).clip(upper=50),
            alpha=0.65,
            label=str(universe),
            color=colors.get(str(universe)),
        )
    ax.set_title("All configs: CAGR vs Max Drawdown")
    ax.set_xlabel("Max Drawdown (%)")
    ax.set_ylabel("CAGR (%)")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    paths.append(_save(fig, output_dir / "all_configs_cagr_vs_mdd.png", study_dir))

    fig, ax = plt.subplots(figsize=(12, 5))
    labels = [str(value) for value in sorted(results["universe"].unique())]
    values = [results.loc[results["universe"] == label, "sharpe"].astype(float) for label in labels]
    try:
        ax.boxplot(values, tick_labels=labels, showfliers=False)
    except TypeError:
        ax.boxplot(values, labels=labels, showfliers=False)
    ax.axhline(0.0, color="gray", linestyle="--", linewidth=1.0)
    ax.set_title("Sharpe distribution by universe")
    ax.set_ylabel("Sharpe")
    ax.grid(True, axis="y", alpha=0.25)
    paths.append(_save(fig, output_dir / "boxplot_sharpe_by_universe.png", study_dir))

    if {"top_n", "rebalance_months", "mdd"}.issubset(results.columns):
        pivot = results.pivot_table(
            index="top_n", columns="rebalance_months", values="mdd", aggfunc="median"
        ).sort_index()
        if not pivot.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            data = pivot.to_numpy(dtype=float) * 100.0
            im = ax.imshow(data, aspect="auto", cmap="magma_r")
            ax.set_title("Median MDD by Top-N and Rebalance Frequency")
            ax.set_xlabel("Rebalance months")
            ax.set_ylabel("Top-N")
            ax.set_xticks(range(len(pivot.columns)), [str(col) for col in pivot.columns])
            ax.set_yticks(range(len(pivot.index)), [str(idx) for idx in pivot.index])
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    if math.isfinite(float(data[i, j])):
                        ax.text(j, i, f"{data[i, j]:.0f}%", ha="center", va="center", fontsize=8)
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            paths.append(_save(fig, output_dir / "median_mdd_by_topn_rebalance.png", study_dir))
    return paths


def plot_strategy_panel(
    name: str,
    returns: pd.Series,
    benchmark_prices: pd.DataFrame,
    benchmark_symbol: str,
    output_dir: Path,
    study_dir: Path,
) -> str | None:
    """Write an individual equity/drawdown/relative plot for one strategy."""
    clean = returns.dropna().astype(float)
    if clean.empty:
        return None
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    strategy_equity = equity_from_returns(clean, start_value=1.0)
    strategy_drawdown = strategy_equity / strategy_equity.cummax() - 1.0
    bench_equity = _benchmark_equity(clean, benchmark_prices)

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    strategy_equity.plot(ax=axes[0], linewidth=1.2, label="Strategy")
    if bench_equity is not None and not bench_equity.empty:
        bench_equity.plot(ax=axes[0], linewidth=1.1, label=benchmark_symbol)
    axes[0].set_title(f"{name}: equity")
    axes[0].set_ylabel("Growth of $1")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.25)

    strategy_drawdown.plot(ax=axes[1], linewidth=1.1, label="Strategy")
    if bench_equity is not None and not bench_equity.empty:
        bench_dd = bench_equity / bench_equity.cummax() - 1.0
        bench_dd.plot(ax=axes[1], linewidth=1.0, label=benchmark_symbol)
    axes[1].set_title("Drawdown")
    axes[1].set_ylabel("Drawdown")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.25)

    if bench_equity is not None and not bench_equity.empty:
        aligned = pd.concat({"strategy": strategy_equity, "benchmark": bench_equity}, axis=1).dropna()
        ratio = aligned["strategy"] / aligned["benchmark"]
        ratio.plot(ax=axes[2], color="black", linewidth=1.1)
        axes[2].axhline(1.0, color="gray", linestyle="--", linewidth=1.0)
        axes[2].set_title(f"Strategy / {benchmark_symbol} relative equity")
        axes[2].set_ylabel("Ratio")
    else:
        rolling = (1.0 + clean).rolling(252).apply(lambda x: float(x.prod()), raw=True) - 1.0
        rolling.plot(ax=axes[2], color="black", linewidth=1.1)
        axes[2].axhline(0.0, color="gray", linestyle="--", linewidth=1.0)
        axes[2].set_title("Rolling 252d return (benchmark unavailable)")
        axes[2].set_ylabel("Return")
    axes[2].grid(True, alpha=0.25)
    fig.tight_layout()
    return _save(fig, output_dir / f"{safe_filename(name)}.png", study_dir)


def _benchmark_equity(strategy_returns: pd.Series, benchmark_prices: pd.DataFrame) -> pd.Series | None:
    if benchmark_prices.empty:
        return None
    prices = benchmark_prices.iloc[:, 0].astype(float).sort_index()
    prices.index = pd.DatetimeIndex(prices.index).tz_localize(None)
    prices = prices.reindex(strategy_returns.index, method="ffill").dropna()
    if prices.empty:
        return None
    returns = prices.pct_change(fill_method=None).fillna(0.0)
    return equity_from_returns(returns, start_value=1.0)


def _save(fig, path: Path, study_dir: Path) -> str:
    import matplotlib.pyplot as plt

    fig.savefig(path, dpi=140)
    plt.close(fig)
    return str(path.relative_to(study_dir))
