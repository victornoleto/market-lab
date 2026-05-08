"""Rolling-windows + equity-vs-benchmark analyses for real-ETF studies.

Generic over the market (SPY or NDX). Called by each study's
``run_analyses.py`` wrapper.
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ai_trade.backtest.grid.real_etf_regime_runner import (
    RealETFMarket,
    build_data_bundle,
    simulate_config_with_real_legs,
)
from ai_trade.backtest.metrics.performance import (
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (
    EMASMAThresholdConfig,
)

TRADING_DAYS = 252


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


def _window_metrics(equity: pd.Series, returns: pd.Series):
    if len(equity) < 10:
        return np.nan, np.nan, np.nan
    eq = equity / equity.iloc[0]
    return (
        _cagr(eq, TRADING_DAYS),
        _sharpe(returns, TRADING_DAYS),
        _max_drawdown(eq),
    )


def _rolling_window_stats(
    strat_eq: pd.Series, strat_rets: pd.Series,
    bench_eq: pd.Series, bench_rets: pd.Series,
    window_years: int, stride_years: float,
) -> pd.DataFrame:
    df = pd.concat({
        "strat_eq": strat_eq, "strat_ret": strat_rets,
        "bench_eq": bench_eq, "bench_ret": bench_rets,
    }, axis=1).dropna()
    if df.empty:
        return pd.DataFrame()
    W = int(window_years * TRADING_DAYS)
    S = max(1, int(stride_years * TRADING_DAYS))
    n = len(df)
    rows = []
    start = 0
    while start + W <= n:
        sl = df.iloc[start : start + W]
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
        start += S
    return pd.DataFrame(rows)


def _render_rolling_plot(
    cfg_id: str, rank: int,
    per_window_df: dict[int, pd.DataFrame],
    windows: tuple[int, ...],
    out_path: Path,
) -> None:
    fig, axes = plt.subplots(len(windows), 1, figsize=(11, 2.5 * len(windows) + 0.5),
                              dpi=110, sharex=False)
    if len(windows) == 1:
        axes = [axes]
    for ax, W in zip(axes, windows):
        df = per_window_df[W]
        if df.empty:
            ax.text(0.5, 0.5, f"no {W}y windows", ha="center", transform=ax.transAxes)
            continue
        x = pd.to_datetime(df["window_start"])
        ax.plot(x, df["strat_cagr"] * 100, label=f"Strategy ({W}y CAGR)",
                color="#1f77b4", linewidth=1.4, marker="o", markersize=3)
        ax.plot(x, df["bench_cagr"] * 100, label="Benchmark",
                color="#808080", linewidth=1.2, linestyle="--",
                marker="s", markersize=3)
        ax.axhline(0, color="red", linestyle=":", linewidth=0.8, alpha=0.5)
        ax.set_ylabel(f"{W}y CAGR (%)")
        ax.legend(loc="best", fontsize=8, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.set_title(f"Rolling {W}-year CAGR (stride 0.5y)", fontsize=9)
    axes[-1].set_xlabel("Window start date")
    fig.suptitle(f"Rank {rank:02d} — {cfg_id}", fontsize=11, y=0.995)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def run_rolling_windows_analysis(
    study_dir: Path,
    market: RealETFMarket,
    windows: tuple[int, ...] = (3, 5, 7, 10),
    stride_years: float = 0.5,
    log: logging.Logger | None = None,
) -> None:
    log = log or logging.getLogger(__name__)
    analyses_dir = study_dir / "analyses"
    plots_dir = analyses_dir / "rolling_plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    configs_csv = pd.read_csv(study_dir / "configs.csv")
    top20 = configs_csv.head(20).copy()

    bundle = build_data_bundle(
        market, leverages_used=tuple(float(x) for x in top20["buy_leverage"].unique()),
    )
    signal_prices = bundle["signal_prices"]
    signal_returns = bundle["signal_returns"]
    bench_eq = signal_prices / signal_prices.iloc[0]
    bench_rets = bench_eq.pct_change().fillna(0.0)

    all_rows = []
    for _, trow in top20.iterrows():
        cfg = _cfg_from_row(trow)
        res = simulate_config_with_real_legs(cfg, bundle)
        strat_eq = res.equity.dropna()
        strat_rets = res.daily_returns

        per_window = {}
        for W in windows:
            df = _rolling_window_stats(
                strat_eq, strat_rets, bench_eq, bench_rets,
                window_years=W, stride_years=stride_years,
            )
            df["window_years"] = W
            df["cfg_id"] = cfg.cfg_id
            df["rank"] = int(trow["rank"])
            per_window[W] = df
            all_rows.append(df)

        _render_rolling_plot(
            cfg.cfg_id, int(trow["rank"]), per_window, windows,
            out_path=plots_dir / f"{int(trow['rank']):02d}_{cfg.cfg_id}.png",
        )
        log.info("  done rank %02d %s", int(trow["rank"]), cfg.cfg_id)

    all_data = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()
    all_data.to_csv(analyses_dir / "03_rolling_windows.csv", index=False)

    # MD.
    meta = bundle["_meta"]
    bench_tk = market.signal_ticker

    lines: list[str] = []
    lines.append(f"# Analysis 3 — Rolling-window robustness ({', '.join(str(w) for w in windows)} years)\n")
    lines.append(
        f"> Real-data window: **{meta['start'].date()} → {meta['end'].date()}** "
        f"({meta['n_bars']} bars ~ {meta['n_bars']/252:.1f}y).  \n"
        f"> Benchmark: {bench_tk} buy-hold over the same slice.  \n"
        f"> Stride: {stride_years}y between windows.\n"
    )

    lines.append("## Rolling windows generated\n")
    lines.append("| window length | # of rolling starts |\n|---|---|")
    for W in windows:
        n_sub = int((all_data["window_years"] == W).sum() / top20.shape[0]) if not all_data.empty else 0
        lines.append(f"| {W}y | {n_sub} |")
    lines.append("")

    if not all_data.empty:
        top1_cfg = top20.iloc[0]["cfg_id"]
        top1_data = all_data[all_data["cfg_id"] == top1_cfg]
        lines.append(f"## Spotlight — rank 1 `{top1_cfg}`\n")
        lines.append(
            "| window | # | median CAGR | min CAGR | max CAGR | median MDD | worst MDD | % beats bench | median excess |\n"
            "|---|---|---|---|---|---|---|---|---|"
        )
        for W in windows:
            sub = top1_data[top1_data["window_years"] == W]
            if sub.empty: continue
            lines.append(
                f"| {W}y | {len(sub)} | {_fmt_pct(sub['strat_cagr'].median())} | "
                f"{_fmt_pct(sub['strat_cagr'].min())} | {_fmt_pct(sub['strat_cagr'].max())} | "
                f"{_fmt_pct(sub['strat_mdd'].median())} | {_fmt_pct(sub['strat_mdd'].max())} | "
                f"{sub['strat_beats_bench'].mean()*100:.1f}% | "
                f"{_fmt_pct(sub['excess_cagr'].median())} |"
            )
        lines.append("")

        # Aggregate per W.
        for W in windows:
            lines.append(f"### {W}-year rolling windows — all top-20\n")
            lines.append(
                f"| rank | cfg_id | median CAGR | worst CAGR | % beats {bench_tk} | median excess |\n"
                "|---|---|---|---|---|---|"
            )
            for _, t in top20.iterrows():
                sub = all_data[(all_data["cfg_id"] == t["cfg_id"]) & (all_data["window_years"] == W)]
                if sub.empty: continue
                lines.append(
                    f"| {t['rank']:02d} | `{t['cfg_id']}` | "
                    f"{_fmt_pct(sub['strat_cagr'].median())} | "
                    f"{_fmt_pct(sub['strat_cagr'].min())} | "
                    f"{sub['strat_beats_bench'].mean()*100:.0f}% | "
                    f"{_fmt_pct(sub['excess_cagr'].median())} |"
                )
            lines.append("")

        # Stability ranking.
        stab = (all_data.groupby("cfg_id")["strat_beats_bench"].mean() * 100)
        lines.append(f"## Stability — % windows beating {bench_tk}\n")
        lines.append("| rank | cfg_id | % of windows beating benchmark |\n|---|---|---|")
        for _, t in top20.iterrows():
            pct = stab.get(t["cfg_id"], np.nan)
            lines.append(f"| {t['rank']:02d} | `{t['cfg_id']}` | {pct:.1f}% |")
        lines.append("")

        # Worst-case table.
        lines.append("## Worst-case CAGR per config, per window length\n")
        header_parts = ["| rank", "cfg_id"]
        for W in windows:
            header_parts.append(f"worst {W}y")
        header_parts.append("worst-ever MDD |")
        lines.append(" | ".join(header_parts))
        lines.append("|" + "---|" * (len(header_parts) - 1) + "---|" if False else
                     "|" + "|".join(["---"] * (len(header_parts))) + "|")
        for _, t in top20.iterrows():
            row_parts = [f"{t['rank']:02d}", f"`{t['cfg_id']}`"]
            worst_mdd = 0.0
            for W in windows:
                sub = all_data[(all_data["cfg_id"] == t["cfg_id"]) & (all_data["window_years"] == W)]
                if sub.empty:
                    row_parts.append("—")
                else:
                    row_parts.append(_fmt_pct(sub["strat_cagr"].min()))
                    worst_mdd = max(worst_mdd, float(sub["strat_mdd"].max()))
            row_parts.append(_fmt_pct(worst_mdd))
            lines.append("| " + " | ".join(row_parts) + " |")
        lines.append("")

    lines.append("## Top-3 detail plots\n")
    for _, t in top20.head(3).iterrows():
        lines.append(f"- rank {t['rank']:02d}: "
                     f"![rolling plot](rolling_plots/{int(t['rank']):02d}_{t['cfg_id']}.png)")
    lines.append("")

    lines.append("---\n")
    lines.append(
        "*Real data: Tiingo parquet cache. Citations: rolling-window "
        "robustness `[systematic_trading, ch.10]`; synth-vs-real LETF drag "
        "`[leverage_for_the_long_run, p.21, Table 12]`; honest alignment "
        "`[advances_fin_ml, p.31-34]`.*"
    )
    (analyses_dir / "03_rolling_windows.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    log.info("rolling analysis written: %s", analyses_dir / "03_rolling_windows.md")
