"""Generate markdown report and Pareto plots for a static portfolio GA run."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def pareto_mask(df: pd.DataFrame, x: str, y: str, *, maximize_x: bool = True, maximize_y: bool = True) -> pd.Series:
    values = df[[x, y]].dropna()
    mask = pd.Series(False, index=df.index)
    for idx, row in values.iterrows():
        better_x = values[x] >= row[x] if maximize_x else values[x] <= row[x]
        better_y = values[y] >= row[y] if maximize_y else values[y] <= row[y]
        strictly = (values[x] > row[x] if maximize_x else values[x] < row[x]) | (
            values[y] > row[y] if maximize_y else values[y] < row[y]
        )
        dominated = (better_x & better_y & strictly).any()
        mask.loc[idx] = not dominated
    return mask


def plot_frontier(df: pd.DataFrame, x: str, y: str, out: Path, *, maximize_x: bool = True, maximize_y: bool = True) -> None:
    clean = df[[x, y, "rank"]].replace([math.inf, -math.inf], pd.NA).dropna()
    if clean.empty:
        return
    mask = pareto_mask(clean, x, y, maximize_x=maximize_x, maximize_y=maximize_y)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(clean[x], clean[y], s=24, alpha=0.45, label="evaluated top")
    ax.scatter(clean.loc[mask, x], clean.loc[mask, y], s=50, label="pareto")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f"Pareto: {x} vs {y}")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)


SHORT_HORIZONS = ("1y", "3y", "5y")
LONG_HORIZONS = ("10y", "15y", "20y")
SHORT_LONG_METRICS = ("cagr_spy_spread", "wealth_spy_ratio_minus1", "mdd_minus_spy_mdd")


def _horizon_score(horizon: dict[str, float], metrics: tuple[str, ...]) -> float:
    values = [horizon.get(m, math.nan) for m in metrics]
    valid = [v for v in values if not (v is None or (isinstance(v, float) and math.isnan(v)))]
    return sum(valid) / len(valid) if valid else math.nan


def _short_long_scores(rolling: dict[str, dict[str, float]]) -> tuple[float, float]:
    short = [
        _horizon_score(rolling[h], SHORT_LONG_METRICS) for h in SHORT_HORIZONS if h in rolling
    ]
    long = [
        _horizon_score(rolling[h], SHORT_LONG_METRICS) for h in LONG_HORIZONS if h in rolling
    ]
    short_valid = [v for v in short if not math.isnan(v)]
    long_valid = [v for v in long if not math.isnan(v)]
    return (
        sum(short_valid) / len(short_valid) if short_valid else math.nan,
        sum(long_valid) / len(long_valid) if long_valid else math.nan,
    )


def _exposure_summary(top_payload: list[dict], k: int = 5) -> pd.DataFrame:
    rows = []
    for i, row in enumerate(top_payload[:k], start=1):
        flat = {"rank": i, "fitness_value": row.get("fitness_value")}
        for family, value in row.get("exposure", {}).items():
            flat[family] = value
        rows.append(flat)
    return pd.DataFrame(rows).fillna(0.0)


def generate(run_dir: Path, report_dir: Path, plot_dir: Path) -> Path:
    payload = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    top = pd.read_csv(run_dir / "top.csv")
    plot_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    # SPEC §Outputs lists a long-window vs short-window Pareto. Build virtual columns
    # from per-candidate rolling metrics so the frontier plot can pick them up.
    if payload.get("top"):
        short_long = [_short_long_scores(row.get("rolling", {})) for row in payload["top"]]
        # `top.csv` rows are in the same rank order as `payload["top"]` per run_ga.flatten_top.
        if len(short_long) == len(top):
            top["fit_short_window"] = [s for s, _ in short_long]
            top["fit_long_window"] = [l for _, l in short_long]

    frontiers = [
        ("full_cagr", "full_mdd", True, True),
        ("full_cagr", "full_sharpe", True, True),
        ("full_cagr", "full_calmar", True, True),
        ("fit_relative_wealth_spy", "full_mdd", True, True),
        ("fit_relative_wealth_qqq", "full_mdd", True, True),
        ("fit_short_window", "fit_long_window", True, True),
    ]
    plot_lines = []
    for x, y, max_x, max_y in frontiers:
        if x in top.columns and y in top.columns:
            name = f"{x}_vs_{y}.png"
            plot_frontier(top, x, y, plot_dir / name, maximize_x=max_x, maximize_y=max_y)
            plot_lines.append(f"- `plots/{name}`")

    report_path = report_dir / "REPORT.md"
    best = payload["top"][0]
    bench_rows = []
    for name, score in payload.get("benchmarks", {}).items():
        metrics = score["full_metrics"]
        bench_rows.append(
            {
                "benchmark": name,
                "cagr": metrics.get("cagr"),
                "mdd": metrics.get("mdd"),
                "sharpe": metrics.get("sharpe"),
                "sortino": metrics.get("sortino"),
                "calmar": metrics.get("calmar"),
                "terminal_wealth": metrics.get("terminal_wealth"),
            }
        )
    bench_md = pd.DataFrame(bench_rows).to_markdown(index=False) if bench_rows else "No benchmark rows."
    top_md = top[
        [
            "rank",
            "fitness_value",
            "full_cagr",
            "full_mdd",
            "full_sharpe",
            "full_sortino",
            "full_calmar",
            "fit_relative_wealth_spy",
            "fit_min_regret",
            "weights",
        ]
    ].head(15).to_markdown(index=False)
    exposure_df = _exposure_summary(payload.get("top", []), k=5)
    exposure_md = exposure_df.to_markdown(index=False) if not exposure_df.empty else "No exposure rows."
    report = f"""# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `{payload['universe']}`
- Fitness: `{payload['fitness']}`
- Seed: `{payload['seed']}`
- Common window: `{payload['common_start']}` to `{payload['common_end']}`
- Unique evaluated portfolios: `{payload['unique_evaluated']}`
- GA rolling step: `{payload['rolling_step']}` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `{payload.get('finalist_exact', 0)}` portfolios
- Benchmark rolling step: `{payload.get('benchmark_rolling_step', payload['rolling_step'])}`
- Generations completed: `{payload.get('generations_completed', payload['generations'])}` / `{payload['generations']}`
- Early stop: `{payload.get('stopped_early', False)}` (`{payload.get('stop_reason', 'completed_generations')}`)
- Patience: `{payload.get('patience', 'n/a')}`, min_delta: `{payload.get('min_delta', 'n/a')}`
- Log every: `{payload.get('log_every', 'n/a')}` generations
- Eval log every: `{payload.get('eval_log_every', 'n/a')}` unique portfolios
- Fast discovery: `{payload.get('fast_discovery', False)}`
- Jobs: `{payload.get('jobs', 1)}`

This is discovery output only. It is not a validated winner or a mandate change.
GA search breadth must be carried into later DSR/PBO accounting
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Best Portfolio

- Fitness value: `{best['fitness_value']:.6f}`
- Weights: `{json.dumps(best['weights'], sort_keys=True)}`
- Effective exposure: `{json.dumps(best['exposure'], sort_keys=True)}`

## Top 15

{top_md}

## Effective Exposure Summary (Top 5)

{exposure_md}

## Benchmark Portfolios

{bench_md}

## Pareto Plots

{chr(10).join(plot_lines) if plot_lines else 'No plots generated.'}

## Notes

- `full_mdd` is less negative when better, so Pareto plots maximize it.
- If `finalist_exact > 0`, `top.csv` and this report use the exact re-rank with all possible rolling windows.
- `top_sampled.csv` preserves the faster GA discovery ranking.
- If fast discovery was enabled, sampled GA rankings skipped rolling MDD/Calmar (set to NaN, not zero, so the weighted fitness ignores them honestly) and should only be used as search traces.
- Relative wealth scores are rolling-window aggregate ratios minus 1 versus the named benchmark.
- The rolling score combines mean, median and p10 to penalize bad-regime fragility.
- Only `balanced_spy_beater`, `balanced_dual_beater`, `relative_wealth_*` and `min_regret` are CASHX-proof. The simple `*_robust` families are raw clipped spreads and can be maximized by defensive/cash-like portfolios `[testing_tuning, p.327-335]`.
"""
    report_path.write_text(report, encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path)
    parser.add_argument("--plot-dir", type=Path)
    args = parser.parse_args()
    report_dir = args.report_dir or args.run_dir
    plot_dir = args.plot_dir or (args.run_dir / "plots")
    report_path = generate(args.run_dir, report_dir, plot_dir)
    print(f"wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
