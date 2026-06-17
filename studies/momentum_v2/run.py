#!/usr/bin/env python3
"""momentum_v2 funnel runner: broad -> evolution -> validate, per universe.

Usage::

    uv run python studies/momentum_v2/run.py --universe us_stocks --audit-only
    uv run python studies/momentum_v2/run.py --universe us_stocks --phase broad --start 1990-01-01
    uv run python studies/momentum_v2/run.py --universe us_stocks --phase evolution
    uv run python studies/momentum_v2/run.py --universe us_stocks --phase validate

Outputs land under ``studies/momentum_v2/universes/<universe>/{results,plots,reports}``
with an identical schema across universes. Phases are sequential: evolution reads
the broad results, validate reads the evolution results.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from market_lab.backtest.data.postgres_source import PostgresSource  # noqa: E402
from studies.momentum_v2 import config as cfg  # noqa: E402
from studies.momentum_v2 import plots as plotlib  # noqa: E402
from studies.momentum_v2 import report as reportlib  # noqa: E402
from studies.momentum_v2.core import (  # noqa: E402
    LookbackProfile,
    StrategyConfig,
    apply_br_foreign_annual_tax,
    build_panel_cache,
    canonicalize_columns,
    metrics_from_returns,
    precompute_scores,
    simulate_config,
    simulate_config_holdings_loop,
)
from studies.momentum_v2.filters import FilterConfig, FilterResult, apply_filters  # noqa: E402
from studies.momentum_v2.grid import build_strategy_grid, lookback_profiles  # noqa: E402
from studies.momentum_v2.overlays import (  # noqa: E402
    OFFSET_MODES,
    OVERLAYS,
    market_regime,
    simulate_evolved,
    stock_trend_ok,
)
from studies.momentum_v2.validation import (  # noqa: E402
    pbo_summary,
    result_row,
    validate_gates,
)

STUDY_DIR = Path(__file__).resolve().parent


def window_tag(start: str | None, membership: str = "none") -> str:
    """Output namespace for one start window, e.g. ``from_1990`` (``from_2000_sp500``
    when a point-in-time membership mask is active, so masked runs never overwrite
    the unmasked baseline)."""
    year = str(start)[:4] if start else "all"
    tag = f"from_{year}"
    return tag if membership == "none" else f"{tag}_{membership}"


def load_membership(args: argparse.Namespace, prices: pd.DataFrame):
    """Build the point-in-time eligibility mask for ``--membership`` (None when off)."""
    if args.membership == "none":
        return None
    from studies.momentum_v2 import membership as memb  # local: optional dependency path
    data_dir = STUDY_DIR / "data"
    if args.membership == "sp500":
        csv = data_dir / "sp500_ticker_start_end.csv"
        if not csv.exists():
            raise SystemExit(
                f"[membership] sp500 needs {csv} -- fetch (free, MIT):\n"
                "  curl -sL https://raw.githubusercontent.com/fja05680/sp500/master/"
                f"sp500_ticker_start_end.csv -o {csv}"
            )
        eligible = memb.build_sp500_eligibility(csv, prices.index)
    else:  # ipo_delist
        av_csv = data_dir / "listing_status_active.csv"
        if not av_csv.exists():
            raise SystemExit(
                "[membership] ipo_delist needs studies/momentum_v2/data/listing_status_active.csv "
                "-- fetch it with your free ALPHAVANTAGE_API_KEY (see README)."
            )
        eligible = memb.build_ipo_delist_eligibility(av_csv, tuple(prices.columns), prices.index)
    sample = next(iter(eligible.values())) if eligible else set()
    priced = {str(c).upper() for c in prices.columns}
    overlap = len(sample & priced)  # the universe actually rankable = members ∩ our prices
    print(f"[membership] {args.membership}: {len(eligible)} months, ~{overlap}/{len(priced)} priced "
          f"tickers rankable/month (sample set={len(sample)})", flush=True)
    return eligible


def universe_dirs(universe: str, window: str) -> tuple[Path, Path, Path, Path]:
    base = STUDY_DIR / "universes" / universe / window
    return base, base / "results", base / "plots", base / "reports"


def effective_start(config: dict, args: argparse.Namespace) -> str:
    return args.start or str(config["run"].get("start"))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the momentum_v2 funnel for one universe")
    parser.add_argument("--universe", default="us_stocks")
    parser.add_argument("--phase", choices=["broad", "evolution", "validate"], default="broad")
    parser.add_argument("--start", default=None, help="Override config start (e.g. 2000-01-01)")
    parser.add_argument("--end", default=None)
    parser.add_argument(
        "--membership", choices=["none", "sp500", "ipo_delist"], default="none",
        help="Point-in-time eligibility mask (survivorship diagnostic). none = current behaviour.",
    )
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--max-symbols", type=int, default=None)
    parser.add_argument("--limit-configs", type=int, default=None, help="Cap broad grid (fast iteration)")
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument("--max-plots", type=int, default=12)
    parser.add_argument("--progress-every", type=int, default=200)
    parser.add_argument(
        "--jobs", type=int, default=None,
        help="Parallel workers for the broad/evolution config loops "
             "(default min(16, cpus); 1 = serial). Results are identical regardless.",
    )
    parser.add_argument(
        "--cache-panels", action="store_true",
        help="Cache the filtered price panel per window so phases reuse one Postgres load",
    )
    parser.add_argument("--refresh-cache", action="store_true", help="Rebuild the panel cache")
    return parser.parse_args(argv)


# --- data loading -----------------------------------------------------------

_CACHE_FILES = ("prices", "volumes", "metadata", "diagnostics", "benchmark")


def _write_panel_cache(cache_dir: Path, result: FilterResult, benchmark: pd.DataFrame, total: int) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    result.prices.to_parquet(cache_dir / "prices.parquet")
    result.volumes.to_parquet(cache_dir / "volumes.parquet")
    result.metadata.to_parquet(cache_dir / "metadata.parquet")
    result.diagnostics.to_parquet(cache_dir / "diagnostics.parquet")
    benchmark.to_parquet(cache_dir / "benchmark.parquet")
    (cache_dir / "meta.json").write_text(json.dumps({"total": int(total)}), encoding="utf-8")


def _read_panel_cache(cache_dir: Path) -> tuple[FilterResult, pd.DataFrame, int]:
    result = FilterResult(
        pd.read_parquet(cache_dir / "prices.parquet"),
        pd.read_parquet(cache_dir / "volumes.parquet"),
        pd.read_parquet(cache_dir / "metadata.parquet"),
        pd.read_parquet(cache_dir / "diagnostics.parquet"),
    )
    benchmark = pd.read_parquet(cache_dir / "benchmark.parquet")
    total = int(json.loads((cache_dir / "meta.json").read_text(encoding="utf-8"))["total"])
    return result, benchmark, total


def _cache_ready(cache_dir: Path) -> bool:
    return (cache_dir / "meta.json").exists() and all(
        (cache_dir / f"{name}.parquet").exists() for name in _CACHE_FILES
    )


def _load_panel(config: dict, universe: str, args: argparse.Namespace):
    """Load (and optionally cache) the filtered price panel for one window.

    Returns (source, total_tickers, filter_result, benchmark, benchmark_symbol,
    start, window). Caching is keyed by the per-window cache directory and is
    skipped when --max-symbols is set (a bounded slice must never serve as the
    canonical panel).
    """
    cfg.load_env_file()
    start = effective_start(config, args)
    end = args.end or config["run"].get("end")
    window = window_tag(start, args.membership)
    base, _results, _plots, _reports = universe_dirs(universe, window)
    cache_dir = base / "cache"
    benchmark_symbol = cfg.benchmark_symbol(config)
    source = PostgresSource(
        database_url=cfg.database_url(config),
        schema=cfg.schema_name(config),
        price_column=cfg.price_column(config),
    )
    cacheable = args.cache_panels and not args.max_symbols
    if cacheable and not args.refresh_cache and _cache_ready(cache_dir):
        result, benchmark, total = _read_panel_cache(cache_dir)
        print(f"[panel] reused cache {cache_dir}", flush=True)
        return source, total, result, benchmark, benchmark_symbol, start, window

    max_symbols = args.max_symbols or config["run"].get("max_symbols_per_universe")
    panel = source.fetch_panel(universe, start=start, end=end, max_symbols=max_symbols)
    filt = FilterConfig.from_dict(cfg.merged_filter_config(config, universe))
    result = apply_filters(panel.prices, panel.volumes, panel.metadata, filt)
    benchmark = source.fetch_symbols((benchmark_symbol,), start=start, end=end)
    total = len(panel.metadata)
    if cacheable:
        _write_panel_cache(cache_dir, result, benchmark, total)
    return source, total, result, benchmark, benchmark_symbol, start, window


def _build_bundles(prices: pd.DataFrame, assets: tuple[str, ...], profiles, features: dict) -> dict:
    return {
        profile.label: precompute_scores(
            prices,
            assets,
            vol_window_days=int(features.get("vol_window_days", 126)),
            trend_window_days=int(features.get("trend_window_days", 126)),
            lookback_months=profile.months,
        )
        for profile in profiles
    }


def _select_finalists(df: pd.DataFrame, metrics: list[str], n: int) -> pd.DataFrame:
    """Union of the top-n rows by each metric (deduped by name).

    With ``metrics=[after_tax_sharpe, after_tax_calmar]`` this takes the best n by
    Sharpe and the best n by Calmar so both lenses are evolved/validated; falls
    back to rolling dominance if a metric column is missing.
    """
    available = [m for m in metrics if m in df.columns] or ["rolling_rel_score"]
    picked = pd.concat([df.nlargest(n, m) for m in available]).drop_duplicates("name")
    return picked.sort_values(available[0], ascending=False)


def _config_from_row(row: pd.Series, assets: tuple[str, ...], features: dict) -> StrategyConfig:
    months = tuple(int(p) for p in str(row["lookback_months"]).split("/") if p)
    profile = LookbackProfile(label=str(row["lookback_label"]), months=months)
    return StrategyConfig(
        name=str(row["name"]),
        universe=str(row["universe"]),
        assets=assets,
        top_n=int(row["top_n"]),
        rebalance_months=int(row["rebalance_months"]),
        rebalance_offset=int(row["rebalance_offset"]),
        score_mode=str(row["score_mode"]),  # type: ignore[arg-type]
        lookback=profile,
        weight_mode=str(row["weight_mode"]),  # type: ignore[arg-type]
        absolute_filter=bool(row["absolute_filter"]),
        vol_window_days=int(features.get("vol_window_days", 126)),
        trend_window_days=int(features.get("trend_window_days", 126)),
    )


# --- parallel config-loop execution -----------------------------------------
# The broad/evolution config loops are the dominant cost (~99% of broad) and are
# embarrassingly parallel. Workers run in fork()ed processes so the ~120MB price
# panel is shared copy-on-write (measured peak ~+1MB/worker) instead of pickled
# per task. ``Pool.map`` preserves submission order, so rows/returns_by_name keep
# the exact config insertion order -> results are bit-identical to the serial loop
# and to each other regardless of worker count. PBO `[advances_fin_ml, p.208-211]`
# only order-depends on exact Sharpe ties (none in practice), and the bootstrap RNG
# is call-local (seed 42 in validation.py), so determinism is unaffected.

_SHARED: dict = {}


def _resolve_jobs(args: argparse.Namespace) -> int:
    """Worker count: explicit --jobs, else min(16, cpus) (measured speedup plateau)."""
    if args.jobs is not None:
        return max(1, int(args.jobs))
    return min(16, os.cpu_count() or 1)


def _map_configs(worker, n: int, jobs: int) -> list:
    """Run ``worker(i)`` for i in range(n), order-preserving: fork Pool or serial."""
    if jobs <= 1 or n <= 1:
        return [worker(i) for i in range(n)]
    import multiprocessing as mp

    try:
        ctx = mp.get_context("fork")  # fork -> panel shared COW; spawn would pickle it per task
    except ValueError:  # non-fork platform (e.g. Windows): stay correct, lose the speedup
        return [worker(i) for i in range(n)]
    with ctx.Pool(jobs) as pool:
        return pool.map(worker, range(n), chunksize=1)  # chunksize=1 balances heavy reb=1 configs


def _collect(results: list) -> tuple[list[dict], dict[str, pd.Series]]:
    """Rebuild (rows, returns_by_name) in config order, skipping empty simulations."""
    rows: list[dict] = []
    returns_by_name: dict[str, pd.Series] = {}
    for res in results:
        if res is None:
            continue
        name, row, ranked_returns = res
        rows.append(row)
        returns_by_name[name] = ranked_returns
    return rows, returns_by_name


def _broad_worker(i: int):
    s = _SHARED
    config_i = s["configs"][i]
    simulation = simulate_config(
        s["prices"], s["bundles"][config_i.lookback.label], config_i,
        eligible_by_date=s["eligible"], panel=s["panel"],
    )
    if simulation.returns.empty:
        return None
    tax = apply_br_foreign_annual_tax(simulation.returns, simulation.daily_weights)
    row = result_row(
        config_i, simulation, s["benchmark"], n_trials=s["n_trials"],
        benchmark_symbol=s["benchmark_symbol"], ranked_returns=tax.returns, tax_summary=tax.summary,
    )
    return (config_i.name, row, tax.returns)


def _evolution_worker(i: int):
    s = _SHARED
    base_cfg, overlay, offset_mode = s["planned"][i]
    evolved_name = f"evo_{base_cfg.name}_{offset_mode}_{overlay}"
    evolved_cfg = StrategyConfig(
        name=evolved_name, universe=s["universe"], assets=s["assets"], top_n=base_cfg.top_n,
        rebalance_months=base_cfg.rebalance_months, rebalance_offset=base_cfg.rebalance_offset,
        score_mode=base_cfg.score_mode, lookback=base_cfg.lookback, weight_mode=base_cfg.weight_mode,
        absolute_filter=base_cfg.absolute_filter, vol_window_days=base_cfg.vol_window_days,
        trend_window_days=base_cfg.trend_window_days,
    )
    simulation = simulate_evolved(
        s["prices"], s["bundles"][base_cfg.lookback.label], evolved_cfg, overlay, offset_mode,
        s["daily_market_ok"], s["monthly_market_ok"], s["monthly_stock_ok"],
        eligible_by_date=s["eligible"], panel=s["panel"],
    )
    if simulation.returns.empty:
        return None
    tax = apply_br_foreign_annual_tax(simulation.returns, simulation.daily_weights)
    row = result_row(
        evolved_cfg, simulation, s["benchmark"], n_trials=s["n_trials"], benchmark_symbol=s["benchmark_symbol"],
        ranked_returns=tax.returns, tax_summary=tax.summary,
        extra={"base_name": base_cfg.name, "overlay": overlay, "offset_mode": offset_mode},
    )
    return (evolved_name, row, tax.returns)


# --- phases -----------------------------------------------------------------

def run_audit(config: dict, universe: str, args: argparse.Namespace) -> int:
    source, total, result, _bench, _sym, start, window = _load_panel(config, universe, args)
    _base, _results, _plots, reports = universe_dirs(universe, window)
    kept = result.prices.shape[1]
    _results.mkdir(parents=True, exist_ok=True)
    if not result.diagnostics.empty:
        result.diagnostics.to_csv(_results / "filter_diagnostics.csv", index=False)
    reportlib.write_data_audit(
        reports / "DATA_AUDIT.md",
        universe=universe, start=start, audit=source.audit(),
        diagnostics=result.diagnostics, kept=kept, total=total,
    )
    print(f"[audit] {universe}: {kept}/{total} tickers pass filters. Wrote DATA_AUDIT.md")
    return 0


def run_broad(config: dict, universe: str, args: argparse.Namespace) -> int:
    source, total, result, benchmark, benchmark_symbol, start, window = _load_panel(config, universe, args)
    base, results_dir, plots_dir, reports = universe_dirs(universe, window)
    if result.prices.shape[1] < int(config["run"].get("min_assets_after_filter", 5)):
        print(f"[broad] too few assets after filter ({result.prices.shape[1]}); aborting.")
        return 1
    assets = tuple(result.prices.columns)
    eligible = load_membership(args, result.prices)
    features = config.get("features", {})
    profiles = lookback_profiles(config["grid"])
    bundles = _build_bundles(result.prices, assets, profiles, features)
    configs = build_strategy_grid(
        config["grid"], universe=universe, assets=assets,
        vol_window_days=int(features.get("vol_window_days", 126)),
        trend_window_days=int(features.get("trend_window_days", 126)),
    )
    if args.limit_configs:
        configs = configs[: args.limit_configs]
    n_trials = len(configs)
    print(f"[broad] {universe}: {len(assets)} assets, {n_trials} configs from {start}")

    _SHARED.update(
        prices=result.prices, bundles=bundles, benchmark=benchmark, n_trials=n_trials,
        benchmark_symbol=benchmark_symbol, eligible=eligible, configs=configs,
        panel=build_panel_cache(result.prices),
    )
    jobs = _resolve_jobs(args)
    print(f"[broad] simulating {n_trials} configs (jobs={jobs})", flush=True)
    rows, returns_by_name = _collect(_map_configs(_broad_worker, len(configs), jobs))

    results = pd.DataFrame(rows)
    reportlib.write_results(results, results_dir, "broad_results")
    if not result.diagnostics.empty:
        result.diagnostics.to_csv(results_dir / "filter_diagnostics.csv", index=False)
    pbo = pbo_summary(
        returns_by_name, results, int(config["validation"]["pbo_blocks"]),
        max_configs=int(config["validation"].get("broad_pbo_max_configs", 1000)),
    )
    reportlib.write_json(results_dir / "broad_pbo.json", pbo)

    plot_paths: list[str] = []
    if not args.no_plots and not results.empty:
        plot_paths = plotlib.write_aggregate_plots(results, plots_dir / "broad", base)
        finalists = plotlib.select_finalists(results, max_finalists=args.max_plots)
        for name in finalists["name"]:
            path = plotlib.plot_strategy_vs_benchmark(
                name, returns_by_name[name], benchmark, plots_dir / "broad" / "finalists", base, benchmark_symbol
            )
            if path:
                plot_paths.append(path)

    reportlib.write_data_audit(
        reports / "DATA_AUDIT.md", universe=universe, start=start, audit=source.audit(),
        diagnostics=result.diagnostics, kept=len(assets), total=total,
    )
    reportlib.write_broad_report(
        reports / "BROAD_REPORT.md", universe=universe, start=start,
        results=results, pbo_rows=pbo["rows"], plot_paths=plot_paths,
    )
    print(f"[broad] wrote {len(results)} rows -> {reports / 'BROAD_REPORT.md'}")
    return 0


def run_evolution(config: dict, universe: str, args: argparse.Namespace) -> int:
    window = window_tag(effective_start(config, args), args.membership)
    base, results_dir, plots_dir, reports = universe_dirs(universe, window)
    broad_path = results_dir / "broad_results.csv"
    if not broad_path.exists():
        print(f"[evolution] missing {broad_path}; run --phase broad first.")
        return 1
    broad = pd.read_csv(broad_path)
    source, _total, result, benchmark, benchmark_symbol, start, window = _load_panel(config, universe, args)
    assets = tuple(result.prices.columns)
    features = config.get("features", {})

    evo_cfg = config.get("evolution", {})
    max_finalists = int(evo_cfg.get("max_finalists", 6))
    metrics = list(evo_cfg.get("selection_metrics", ["rolling_rel_score"]))
    finalists = _select_finalists(broad, metrics, max_finalists)
    finalist_configs = [_config_from_row(row, assets, features) for _, row in finalists.iterrows()]
    print(f"[evolution] selected {len(finalist_configs)} broad finalists by {metrics}")

    daily = canonicalize_columns(result.prices).sort_index()
    daily_market_ok, monthly_market_ok = market_regime(benchmark, pd.DatetimeIndex(daily.index))
    monthly_stock_ok = stock_trend_ok(result.prices)
    bundles = {
        c.lookback.label: precompute_scores(
            result.prices, assets,
            vol_window_days=c.vol_window_days, trend_window_days=c.trend_window_days,
            lookback_months=c.lookback.months,
        )
        for c in finalist_configs
    }

    eligible = load_membership(args, result.prices)
    planned = [(c, overlay, offset_mode) for c in finalist_configs for overlay in OVERLAYS for offset_mode in OFFSET_MODES]
    n_trials = len(planned)
    print(f"[evolution] {universe}: {len(finalist_configs)} finalists x {len(OVERLAYS)} overlays x {len(OFFSET_MODES)} offsets = {n_trials}")
    _SHARED.update(
        prices=result.prices, bundles=bundles, benchmark=benchmark, n_trials=n_trials,
        benchmark_symbol=benchmark_symbol, eligible=eligible, planned=planned,
        universe=universe, assets=assets, daily_market_ok=daily_market_ok,
        monthly_market_ok=monthly_market_ok, monthly_stock_ok=monthly_stock_ok,
        panel=build_panel_cache(result.prices),
    )
    jobs = _resolve_jobs(args)
    print(f"[evolution] simulating {n_trials} trials (jobs={jobs})", flush=True)
    rows, returns_by_name = _collect(_map_configs(_evolution_worker, len(planned), jobs))

    results = pd.DataFrame(rows)
    reportlib.write_results(results, results_dir, "evolution_results")
    pbo = pbo_summary(returns_by_name, results, int(config["validation"]["pbo_blocks"]))
    reportlib.write_json(results_dir / "evolution_pbo.json", pbo)

    plot_paths: list[str] = []
    if not args.no_plots and not results.empty:
        top = results.nlargest(args.max_plots, "after_tax_sharpe")
        for name in top["name"]:
            path = plotlib.plot_strategy_vs_benchmark(
                name, returns_by_name[name], benchmark, plots_dir / "evolution" / "finalists", base, benchmark_symbol
            )
            if path:
                plot_paths.append(path)

    reportlib.write_evolution_report(
        reports / "EVOLUTION_REPORT.md", universe=universe, start=start,
        results=results, pbo_rows=pbo["rows"], plot_paths=plot_paths,
    )
    print(f"[evolution] wrote {len(results)} rows -> {reports / 'EVOLUTION_REPORT.md'}")
    return 0


def run_validate(config: dict, universe: str, args: argparse.Namespace) -> int:
    window = window_tag(effective_start(config, args), args.membership)
    base, results_dir, _plots, reports = universe_dirs(universe, window)
    evo_path = results_dir / "evolution_results.csv"
    broad_path = results_dir / "broad_results.csv"
    if not evo_path.exists():
        print(f"[validate] missing {evo_path}; run --phase evolution first.")
        return 1
    evo = pd.read_csv(evo_path)
    n_broad = len(pd.read_csv(broad_path)) if broad_path.exists() else 0
    source, _total, result, benchmark, benchmark_symbol, start, window = _load_panel(config, universe, args)
    assets = tuple(result.prices.columns)
    features = config.get("features", {})

    evo_cfg = config.get("evolution", {})
    n_finalists = int(evo_cfg.get("max_finalists", 6))
    metrics = list(evo_cfg.get("selection_metrics", ["rolling_rel_score"]))
    finalists = _select_finalists(evo, metrics, n_finalists)
    daily = canonicalize_columns(result.prices).sort_index()
    daily_market_ok, monthly_market_ok = market_regime(benchmark, pd.DatetimeIndex(daily.index))
    monthly_stock_ok = stock_trend_ok(result.prices)

    val = config["validation"]
    eligible = load_membership(args, result.prices)
    n_trials = n_broad + len(evo)  # honest count across the whole funnel
    returns_by_name: dict[str, pd.Series] = {}
    xlib_delta: dict[str, float] = {}
    for _, row in finalists.iterrows():
        base_cfg = _config_from_row(
            pd.Series({**row.to_dict(), "name": str(row["base_name"])}), assets, features
        )
        bundle = precompute_scores(
            result.prices, assets, vol_window_days=base_cfg.vol_window_days,
            trend_window_days=base_cfg.trend_window_days, lookback_months=base_cfg.lookback.months,
        )
        overlay = str(row.get("overlay", "none"))
        offset_mode = str(row.get("offset_mode", "fixed"))
        evolved_cfg = StrategyConfig(
            name=str(row["name"]), universe=universe, assets=assets, top_n=base_cfg.top_n,
            rebalance_months=base_cfg.rebalance_months, rebalance_offset=base_cfg.rebalance_offset,
            score_mode=base_cfg.score_mode, lookback=base_cfg.lookback, weight_mode=base_cfg.weight_mode,
            absolute_filter=base_cfg.absolute_filter, vol_window_days=base_cfg.vol_window_days,
            trend_window_days=base_cfg.trend_window_days,
        )
        simulation = simulate_evolved(
            result.prices, bundle, evolved_cfg, overlay, offset_mode,
            daily_market_ok, monthly_market_ok, monthly_stock_ok,
            eligible_by_date=eligible,
        )
        if simulation.returns.empty:
            continue
        returns_by_name[str(row["name"])] = simulation.returns
        # cross-library CAGR check validates the *engine*: the same base strategy
        # computed two independent ways (vectorized vs holdings loop) must agree.
        # Overlay/stagger reuse these primitives, so the base check covers them; we
        # must NOT compare the overlay'd curve against the base loop (different
        # strategies) `[advances_fin_ml, p.31-34]`.
        base_vec = simulate_config(result.prices, bundle, base_cfg).returns
        base_loop = simulate_config_holdings_loop(result.prices, bundle, base_cfg)
        vec_cagr = float(metrics_from_returns(base_vec)["cagr"]) if not base_vec.empty else float("nan")
        loop_cagr = float(metrics_from_returns(base_loop)["cagr"]) if not base_loop.empty else float("nan")
        xlib_delta[str(row["name"])] = abs(vec_cagr - loop_cagr) * 100.0

    verdict = validate_gates(
        returns_by_name, n_trials=n_trials,
        pbo_blocks=int(val["pbo_blocks"]), dsr_alpha=float(val["dsr_alpha"]),
        wf_min_windows=int(val["wf_min_windows"]), wf_max_drawdown=float(val["wf_max_drawdown"]),
        bootstrap_resamples=int(val["bootstrap_resamples"]), bootstrap_block_days=int(val["bootstrap_block_days"]),
        xlib_delta_by_name=xlib_delta,
    )
    reportlib.write_json(results_dir / "validate_verdict.json", verdict)
    reportlib.write_validate_report(
        reports / "VALIDATE_REPORT.md", universe=universe, start=start, verdict=verdict
    )
    print(f"[validate] overall_pass={verdict['overall_pass']} -> {reports / 'VALIDATE_REPORT.md'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = cfg.load_config(args.universe)
    if args.audit_only:
        return run_audit(config, args.universe, args)
    if args.phase == "broad":
        return run_broad(config, args.universe, args)
    if args.phase == "evolution":
        return run_evolution(config, args.universe, args)
    return run_validate(config, args.universe, args)


if __name__ == "__main__":
    raise SystemExit(main())
