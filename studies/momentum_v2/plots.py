"""Plot helpers: per-strategy equity-vs-benchmark panels and aggregate maps.

All paths returned are relative to the universe directory (e.g.
``plots/broad/heatmap_sharpe.png``) so the markdown reports under ``reports/``
can link them with a ``../`` prefix.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from studies.momentum_v2.core import benchmark_returns_for
from studies.momentum_v2.util import safe_filename


def _rel(path: Path, universe_dir: Path) -> str:
    return str(path.relative_to(universe_dir))


def plot_strategy_vs_benchmark(
    name: str,
    returns: pd.Series,
    benchmark_prices: pd.DataFrame,
    out_dir: Path,
    universe_dir: Path,
    benchmark_symbol: str = "SPY",
) -> str | None:
    """3-panel after-tax equity / drawdown / relative-equity chart vs benchmark."""
    strategy_returns, bench_returns = benchmark_returns_for(returns, benchmark_prices, benchmark_symbol)
    if strategy_returns.empty or bench_returns.empty:
        return None
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    strategy_eq = (1.0 + strategy_returns).cumprod()
    bench_eq = (1.0 + bench_returns).cumprod()
    aligned = pd.concat({"Strategy": strategy_eq, benchmark_symbol: bench_eq}, axis=1).dropna()
    dd = aligned / aligned.cummax() - 1.0
    ratio = aligned["Strategy"] / aligned[benchmark_symbol]

    # Three panels side-by-side (equity | drawdown | relative-equity) in one figure.
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharex=True)
    aligned.plot(ax=axes[0], linewidth=1.2)
    axes[0].set_title(f"{name}: after-tax equity vs {benchmark_symbol}")
    axes[0].set_ylabel("Growth of $1")
    axes[0].grid(True, alpha=0.3)
    # Drawdown DIFFERENCE (strategy − benchmark) as a signed area: below 0 (strategy fell
    # more than the benchmark = worse) filled red; above 0 (fell less = better) filled blue.
    dd_diff = (dd["Strategy"] - dd[benchmark_symbol]).to_numpy(dtype=float)
    x = dd.index
    axes[1].fill_between(x, dd_diff, 0.0, where=dd_diff <= 0, color="#d62728", alpha=0.35,
                         interpolate=True, label="pior (caiu mais)")
    axes[1].fill_between(x, dd_diff, 0.0, where=dd_diff >= 0, color="#1f77b4", alpha=0.35,
                         interpolate=True, label="melhor (caiu menos)")
    axes[1].axhline(0.0, color="gray", linewidth=0.8)
    axes[1].set_title(f"Drawdown Δ vs {benchmark_symbol} (azul=melhor · vermelho=pior)")
    axes[1].set_ylabel("DD estratégia − DD benchmark")
    axes[1].legend(fontsize=7, loc="lower left")
    axes[1].grid(True, alpha=0.3)
    ratio.plot(ax=axes[2], color="black", linewidth=1.1)
    axes[2].axhline(1.0, color="gray", linestyle="--", linewidth=1.0)
    axes[2].set_title(f"Strategy / {benchmark_symbol} relative equity")
    axes[2].set_ylabel("Ratio")
    axes[2].grid(True, alpha=0.3)
    fig.tight_layout()
    path = out_dir / f"{safe_filename(name)}_vs_{benchmark_symbol}.png"
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return _rel(path, universe_dir)


def select_finalists(results: pd.DataFrame, max_finalists: int = 12) -> pd.DataFrame:
    """Diverse finalist selection: rolling dominance first, then Sharpe/Calmar/crisis."""
    if results.empty:
        return results
    selected = [
        results.nlargest(max_finalists, "rolling_rel_score"),
        results.nlargest(4, "after_tax_sharpe"),
        results.nlargest(4, "after_tax_calmar"),
        results.nlargest(4, "excess_cagr"),
        results.nlargest(3, "gfc_mdd"),
    ]
    out = pd.concat(selected).drop_duplicates("name")
    out = out.sort_values(["rolling_rel_score", "after_tax_sharpe"], ascending=False)
    return out.head(max_finalists).copy()


def write_aggregate_plots(results: pd.DataFrame, plots_dir: Path, universe_dir: Path) -> list[str]:
    """CAGR-vs-MDD scatter plus mechanism/rebalance heatmaps for one universe."""
    if results.empty:
        return []
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plots_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []

    fig, ax = plt.subplots(figsize=(10, 6))
    for mechanism, sub in results.groupby("mechanism"):
        ax.scatter(
            sub["after_tax_mdd"] * 100.0,
            sub["after_tax_cagr"] * 100.0,
            s=16 + sub["top_n"].to_numpy(dtype=float),
            alpha=0.6,
            label=mechanism,
        )
    ax.set_title("All configs: after-tax CAGR vs MDD (size = top-N)")
    ax.set_xlabel("MDD (%)")
    ax.set_ylabel("CAGR (%)")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=7, loc="best")
    fig.tight_layout()
    scatter = plots_dir / "all_configs_cagr_vs_mdd.png"
    fig.savefig(scatter, dpi=140)
    plt.close(fig)
    paths.append(_rel(scatter, universe_dir))

    paths.append(_heatmap(results, "after_tax_sharpe", "max", "heatmap_sharpe.png", plots_dir, universe_dir, "viridis"))
    paths.append(_heatmap(results, "after_tax_mdd", "median", "heatmap_mdd.png", plots_dir, universe_dir, "magma_r"))
    paths.append(_heatmap(results, "rolling_rel_score", "max", "heatmap_rolling_rel.png", plots_dir, universe_dir, "viridis"))
    return [p for p in paths if p]


def _heatmap(
    results: pd.DataFrame, value: str, agg: str, filename: str, plots_dir: Path, universe_dir: Path, cmap: str
) -> str:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pivot = results.pivot_table(index="mechanism", columns="rebalance_months", values=value, aggfunc=agg).sort_index()
    fig, ax = plt.subplots(figsize=(8, 6))
    data = pivot.to_numpy(dtype=float)
    im = ax.imshow(data, aspect="auto", cmap=cmap)
    ax.set_title(f"{agg} {value}")
    ax.set_xticks(range(len(pivot.columns)), [str(col) for col in pivot.columns])
    ax.set_yticks(range(len(pivot.index)), list(pivot.index), fontsize=7)
    ax.set_xlabel("Rebalance months")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if math.isfinite(float(data[i, j])):
                ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center", fontsize=6)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    path = plots_dir / filename
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return _rel(path, universe_dir)
