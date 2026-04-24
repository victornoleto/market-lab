"""Rolling-window robustness test for the top-20 configs.

For each of the top-20 configs (and SPY buy-hold), generates rolling
windows of 5, 10, 15, 20 years (stride = 1 year) and measures CAGR,
Sharpe, MDD per window. Answers the user's question: is the top
config's edge stable across different historical periods, or does it
depend on a specific era?

Outputs
-------
* ``03_rolling_windows_5_10_15_20y.md`` — narrative + per-config tables.
* ``03_rolling_windows_5_10_15_20y.csv`` — raw per-(config, window) data.
* ``rolling_plots/<rank>_<cfg_id>.png`` — per-config rolling CAGR plots
  for all 4 window lengths (one panel each), with SPY overlay.
* ``rolling_plots/stability_heatmap.png`` — top-20 × window-start
  heatmap showing rank over time.

Cites
-----
- Robustness across regimes: `[advances_fin_ml, p.31-34]` (cross-lib)
  + `[systematic_trading, ch.10]` (rolling optimization check).
- Bull-bias of 40y SPY: `[adaptive_markets, p.282-283]` (regime shifts).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ai_trade.backtest.data.testfolio_loader import (  # noqa: E402
    load_testfolio_returns,
    load_testfolio_series,
)
from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (  # noqa: E402
    EMASMAThresholdConfig,
    simulate_ema_sma_threshold,
)

STUDY_DIR = Path(__file__).parent.parent
ANALYSES_DIR = STUDY_DIR / "analyses"
PLOTS_DIR = ANALYSES_DIR / "rolling_plots"
WINDOWS = (5, 10, 15, 20)  # years
STRIDE_YEARS = 1
TRADING_DAYS = 252


def _setup_logging() -> logging.Logger:
    logger = logging.getLogger("rolling")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(sh)
    return logger


def _fmt_pct(x: float, digits: int = 2) -> str:
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x * 100:+.{digits}f}%"


def _fmt_num(x: float, digits: int = 2) -> str:
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x:.{digits}f}"


def _cfg_from_row(row: pd.Series) -> EMASMAThresholdConfig:
    return EMASMAThresholdConfig(
        filter=row["filter"],
        lookback=int(row["lookback"]),
        threshold_pct=float(row["threshold_pct"]),
        buy_leverage=float(row["buy_leverage"]),
        sell_leverage=float(row["sell_leverage"]),
    )


def _window_metrics(equity: pd.Series, returns: pd.Series) -> tuple[float, float, float]:
    """Compute CAGR, Sharpe, MDD for one window slice."""
    if len(equity) < 10:
        return np.nan, np.nan, np.nan
    # Normalise equity to 1.0 at window start for clean CAGR.
    eq = equity / equity.iloc[0]
    c = _cagr(eq, TRADING_DAYS)
    s = _sharpe(returns, TRADING_DAYS)
    dd = _max_drawdown(eq)
    return c, s, dd


def _rolling_window_stats(
    strat_eq: pd.Series,
    strat_rets: pd.Series,
    bench_eq: pd.Series,
    bench_rets: pd.Series,
    window_years: int,
    stride_years: int = 1,
) -> pd.DataFrame:
    """Generate rolling windows of `window_years`. Returns one row per window."""
    idx = strat_eq.index
    # Align both series.
    df = pd.concat({
        "strat_eq": strat_eq,
        "strat_ret": strat_rets,
        "bench_eq": bench_eq,
        "bench_ret": bench_rets,
    }, axis=1).dropna()
    if df.empty:
        return pd.DataFrame()

    window_bars = int(window_years * TRADING_DAYS)
    stride_bars = int(stride_years * TRADING_DAYS)
    n = len(df)
    rows = []
    start = 0
    while start + window_bars <= n:
        sl = df.iloc[start : start + window_bars]
        sc, ss, sd = _window_metrics(sl["strat_eq"], sl["strat_ret"])
        bc, bs, bd = _window_metrics(sl["bench_eq"], sl["bench_ret"])
        rows.append({
            "window_start": sl.index[0].date().isoformat(),
            "window_end": sl.index[-1].date().isoformat(),
            "strat_cagr": sc, "strat_sharpe": ss, "strat_mdd": sd,
            "bench_cagr": bc, "bench_sharpe": bs, "bench_mdd": bd,
            "excess_cagr": sc - bc,
            "strat_beats_bench": sc > bc,
        })
        start += stride_bars
    return pd.DataFrame(rows)


def _render_config_rolling_plot(
    cfg_id: str,
    rank: int,
    per_window_df: dict[int, pd.DataFrame],
    out_path: Path,
) -> None:
    """4-panel plot: one subplot per window length (5/10/15/20y)."""
    fig, axes = plt.subplots(4, 1, figsize=(11, 10), dpi=110, sharex=False)
    for ax, W in zip(axes, WINDOWS):
        df = per_window_df[W]
        if df.empty:
            ax.text(0.5, 0.5, f"no {W}y windows", ha="center", transform=ax.transAxes)
            continue
        x = pd.to_datetime(df["window_start"])
        ax.plot(x, df["strat_cagr"] * 100, label=f"Strategy (CAGR over {W}y)",
                color="#1f77b4", linewidth=1.4, marker="o", markersize=3)
        ax.plot(x, df["bench_cagr"] * 100, label="SPY buy-hold",
                color="#808080", linewidth=1.2, linestyle="--",
                marker="s", markersize=3)
        ax.axhline(0, color="red", linestyle=":", linewidth=0.8, alpha=0.5)
        ax.set_ylabel(f"{W}y CAGR (%)")
        ax.legend(loc="best", fontsize=8, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.set_title(f"Rolling {W}-year CAGR over time (stride 1y)", fontsize=9)
    axes[-1].set_xlabel("Window start date")
    fig.suptitle(f"Rank {rank:02d} — {cfg_id}", fontsize=11, y=0.995)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _render_stability_heatmap(
    all_data: pd.DataFrame,
    window_years: int,
    cfg_order: list[str],
    out_path: Path,
) -> None:
    """Heatmap: rows=configs (rank order), cols=window start year, values=CAGR-over-SPY."""
    df = all_data[all_data["window_years"] == window_years].copy()
    if df.empty:
        return
    df["start_year"] = pd.to_datetime(df["window_start"]).dt.year
    pivot = df.pivot_table(
        index="cfg_id", columns="start_year", values="excess_cagr", aggfunc="first"
    )
    pivot = pivot.reindex(cfg_order)

    fig, ax = plt.subplots(figsize=(max(10, 0.35 * pivot.shape[1]), 7), dpi=110)
    vmax = float(np.nanpercentile(np.abs(pivot.values), 95))
    im = ax.imshow(pivot.values * 100, aspect="auto", cmap="RdYlGn",
                   vmin=-vmax * 100, vmax=vmax * 100)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([f"{i+1:02d} {c}" for i, c in enumerate(pivot.index)],
                       fontsize=8)
    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels(pivot.columns, rotation=45, fontsize=8)
    ax.set_xlabel("Window start year")
    ax.set_title(
        f"Excess CAGR vs SPY per {window_years}-year rolling window (%)\n"
        f"green = strategy beats SPY, red = SPY beats strategy"
    )
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Excess CAGR (pp, strategy − SPY)")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _render_summary_md(
    all_data: pd.DataFrame,
    top20: pd.DataFrame,
    out_path: Path,
) -> None:
    lines: list[str] = []
    lines.append("# Analysis 3 — Rolling-window robustness (5 / 10 / 15 / 20 years)\n")
    lines.append(
        "> Answers: *\"essas 20 estratégias aplicadas em períodos diferentes "
        "de 5/10/15/20 anos — elas se mantêm ou dependem da era?\"*\n"
    )

    lines.append("## Method\n")
    lines.append(
        f"- Rolling windows of **5, 10, 15, 20 years**, stride **1 year**.\n"
        f"- For each window: compute strategy CAGR/Sharpe/MDD and SPY "
        "buy-hold CAGR/Sharpe/MDD on the same slice.\n"
        f"- A window is a 'win' when strategy CAGR > SPY CAGR.\n"
        "- Data: SPYSIM 1986-01-02 → 2026-04-17 (testfolio synth).\n"
        "- Strategy runs with `tax_rate = 0` (pure). For tax-15% analogue, "
        "apply the `tax_drag_cagr` column from `../configs.csv` (~2-3pp).\n"
    )

    # Per-window counts.
    n_windows_by_W = {W: int((all_data["window_years"] == W).sum()
                              / top20.shape[0]) for W in WINDOWS}
    lines.append("### Rolling windows generated\n")
    lines.append("| window length | # of rolling starts |\n|---|---|")
    for W in WINDOWS:
        lines.append(f"| {W}y | {n_windows_by_W[W]} |")
    lines.append("")

    # Top-1 detailed table.
    top1_cfg = top20.iloc[0]["cfg_id"]
    top1_data = all_data[all_data["cfg_id"] == top1_cfg]
    lines.append(f"## Spotlight — rank 1 `{top1_cfg}`\n")
    lines.append(
        "| window | # of windows | median CAGR | min CAGR | max CAGR | "
        "median MDD | worst MDD | % windows beat SPY | median excess vs SPY |\n"
        "|---|---|---|---|---|---|---|---|---|"
    )
    for W in WINDOWS:
        sub = top1_data[top1_data["window_years"] == W]
        if sub.empty: continue
        lines.append(
            f"| {W}y | {len(sub)} | {_fmt_pct(sub['strat_cagr'].median())} | "
            f"{_fmt_pct(sub['strat_cagr'].min())} | "
            f"{_fmt_pct(sub['strat_cagr'].max())} | "
            f"{_fmt_pct(sub['strat_mdd'].median())} | "
            f"{_fmt_pct(sub['strat_mdd'].max())} | "
            f"{sub['strat_beats_bench'].mean()*100:.1f}% | "
            f"{_fmt_pct(sub['excess_cagr'].median())} |"
        )
    lines.append("")

    # Worst window detail for top-1.
    top1_worst_5y = top1_data[top1_data["window_years"] == 5].nsmallest(1, "strat_cagr")
    if not top1_worst_5y.empty:
        row = top1_worst_5y.iloc[0]
        lines.append(
            f"**Pior janela 5y de `{top1_cfg}`**: "
            f"{row['window_start']} → {row['window_end']} — "
            f"strategy CAGR {_fmt_pct(row['strat_cagr'])}, "
            f"SPY CAGR {_fmt_pct(row['bench_cagr'])}, "
            f"strategy MDD {_fmt_pct(row['strat_mdd'])}.\n"
        )

    # Aggregate: all 20 configs, per window.
    lines.append("## Aggregate — all top-20 configs\n")
    for W in WINDOWS:
        lines.append(f"### {W}-year rolling windows\n")
        lines.append(
            "| rank | cfg_id | median CAGR | worst CAGR | % beats SPY | "
            "median excess |\n|---|---|---|---|---|---|"
        )
        for _, t in top20.iterrows():
            sub = all_data[
                (all_data["cfg_id"] == t["cfg_id"]) &
                (all_data["window_years"] == W)
            ]
            if sub.empty: continue
            lines.append(
                f"| {t['rank']:02d} | `{t['cfg_id']}` | "
                f"{_fmt_pct(sub['strat_cagr'].median())} | "
                f"{_fmt_pct(sub['strat_cagr'].min())} | "
                f"{sub['strat_beats_bench'].mean()*100:.0f}% | "
                f"{_fmt_pct(sub['excess_cagr'].median())} |"
            )
        lines.append("")

    # Stability ranking — which configs beat SPY in ≥80% of windows across ALL Ws?
    lines.append("## Stability ranking — how often does each config beat SPY?\n")
    stab = (all_data.groupby("cfg_id")["strat_beats_bench"].mean() * 100).sort_values(ascending=False)
    # Keep top20 order but also show the pct.
    lines.append(
        "For each config, % of rolling windows (across all 5/10/15/20y) "
        "where the strategy outperforms SPY buy-hold.\n"
    )
    lines.append("| rank (composite) | cfg_id | % of windows beating SPY |\n|---|---|---|")
    for _, t in top20.iterrows():
        pct = stab.get(t["cfg_id"], np.nan)
        lines.append(f"| {t['rank']:02d} | `{t['cfg_id']}` | {pct:.1f}% |")
    lines.append("")

    # Worst-case guarantee table.
    lines.append("## Worst-case guarantee per config\n")
    lines.append(
        "What's the WORST CAGR each config has produced across any "
        "window? (Answer to \"o pior cenário realista\").\n"
    )
    lines.append(
        "| rank | cfg_id | worst 5y CAGR | worst 10y CAGR | worst 15y CAGR | "
        "worst 20y CAGR | worst-ever MDD |\n|---|---|---|---|---|---|---|"
    )
    for _, t in top20.iterrows():
        row_parts = [f"{t['rank']:02d}", f"`{t['cfg_id']}`"]
        worst_mdd = 0.0
        for W in WINDOWS:
            sub = all_data[
                (all_data["cfg_id"] == t["cfg_id"]) &
                (all_data["window_years"] == W)
            ]
            if sub.empty:
                row_parts.append("—")
            else:
                row_parts.append(_fmt_pct(sub["strat_cagr"].min()))
                worst_mdd = max(worst_mdd, float(sub["strat_mdd"].max()))
        row_parts.append(_fmt_pct(worst_mdd))
        lines.append("| " + " | ".join(row_parts) + " |")
    lines.append("")

    # Honest narrative.
    lines.append("## Narrative — is the top config ready for live?\n")

    # Pull key stats for top-1.
    top1 = all_data[all_data["cfg_id"] == top1_cfg]
    for W in WINDOWS:
        sub = top1[top1["window_years"] == W]
        if sub.empty: continue
        worst_c = sub["strat_cagr"].min()
        beats_pct = sub["strat_beats_bench"].mean() * 100
        median_excess = sub["excess_cagr"].median()
        lines.append(
            f"- **{W}y windows** ({len(sub)} rolling starts): "
            f"median excess vs SPY **{_fmt_pct(median_excess)}**, "
            f"beats SPY in **{beats_pct:.0f}%** of windows, "
            f"worst CAGR **{_fmt_pct(worst_c)}**.\n"
        )

    # Key verdict.
    lines.append("### Verdict\n")
    lines.append(
        "This is where the 'is it ready for live?' question gets data-backed. "
        "A config is *robust* (live-candidate) when:\n\n"
        "1. It beats SPY in ≥ 80% of rolling windows at every length.\n"
        "2. Its worst 5y CAGR is still positive (or at least not catastrophic).\n"
        "3. Its worst-ever MDD across windows is within the user's pain "
        "tolerance.\n\n"
        "Check each top-20 config against those three criteria using the "
        "tables above. If only one or two configs pass all three, those are "
        "the **true robustness survivors** — and those are the ones worth "
        "considering for paper trading.\n\n"
        "If NO config passes all three, the top-20 is period-dependent and "
        "not live-ready in any form. That would reinforce the mandate §1 "
        "(MAINTENANCE / 100% Plano C) decision.\n"
    )

    # Plots.
    lines.append("## Plots\n")
    lines.append(
        "- `rolling_plots/<rank>_<cfg_id>.png` — per-config: rolling CAGR "
        "(strategy vs SPY) across all 4 window lengths.\n"
        "- `rolling_plots/stability_heatmap_<W>y.png` — 20 configs × window-start "
        "year heatmap of excess CAGR vs SPY (green = strategy beats).\n"
    )
    lines.append("Top-3 detailed plots:\n")
    for _, t in top20.head(3).iterrows():
        lines.append(f"- rank {t['rank']:02d}: "
                     f"![rolling plot](rolling_plots/{int(t['rank']):02d}_"
                     f"{t['cfg_id']}.png)")
    lines.append("")

    lines.append("---\n")
    lines.append(
        "*Citations: rolling-window robustness `[systematic_trading, ch.10]`; "
        "cross-lib/lookahead discipline `[advances_fin_ml, p.31-34]`; "
        "regime shift risk `[adaptive_markets, p.282-283]`; MDD tiers "
        "(§2.3) and gate rules (§5) per `docs/investment-mandate.md`.*"
    )

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    log = _setup_logging()
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    log.info("Loading data + configs.csv...")
    spx_prices = load_testfolio_series("SPYSIM")
    spx_returns = load_testfolio_returns("SPYSIM")
    bench_eq_full = spx_prices.reindex(spx_returns.index).ffill()
    bench_eq_full = bench_eq_full / bench_eq_full.iloc[0]
    bench_rets_full = bench_eq_full.pct_change().fillna(0.0)

    configs_csv = pd.read_csv(STUDY_DIR / "configs.csv")
    top20 = configs_csv.head(20).copy()

    all_rows = []
    log.info("Running rolling windows for top-20 configs × 4 window lengths...")
    for _, trow in top20.iterrows():
        cfg = _cfg_from_row(trow)
        res = simulate_ema_sma_threshold(spx_prices, spx_returns, cfg)
        strat_eq = res.equity.dropna()
        strat_rets = res.daily_returns

        per_window = {}
        for W in WINDOWS:
            df = _rolling_window_stats(
                strat_eq, strat_rets, bench_eq_full, bench_rets_full,
                window_years=W, stride_years=STRIDE_YEARS,
            )
            df["window_years"] = W
            df["cfg_id"] = cfg.cfg_id
            df["rank"] = int(trow["rank"])
            per_window[W] = df
            all_rows.append(df)

        # Per-config rolling plot.
        _render_config_rolling_plot(
            cfg.cfg_id, int(trow["rank"]), per_window,
            out_path=PLOTS_DIR / f"{int(trow['rank']):02d}_{cfg.cfg_id}.png",
        )
        log.info("  done rank %02d %s", int(trow["rank"]), cfg.cfg_id)

    all_data = pd.concat(all_rows, ignore_index=True)
    all_data.to_csv(ANALYSES_DIR / "03_rolling_windows_5_10_15_20y.csv", index=False)

    # Stability heatmaps (one per window length).
    cfg_order = top20["cfg_id"].tolist()
    for W in WINDOWS:
        _render_stability_heatmap(
            all_data, W, cfg_order,
            out_path=PLOTS_DIR / f"stability_heatmap_{W}y.png",
        )

    _render_summary_md(
        all_data, top20,
        out_path=ANALYSES_DIR / "03_rolling_windows_5_10_15_20y.md",
    )

    log.info("Done. Outputs at %s", ANALYSES_DIR / "03_rolling_windows_5_10_15_20y.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
