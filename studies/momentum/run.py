#!/usr/bin/env python3
"""Run Postgres-backed long-horizon momentum screens."""

from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import sys
import time
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from studies.momentum.config import (  # noqa: E402
    DEFAULT_CONFIG,
    database_url,
    load_config,
    load_env_file,
    masked_database_url,
    merged_filter_config,
    price_column,
    schema_name,
)
from studies.momentum.data import (  # noqa: E402
    PricePanel,
    audit_database,
    connect,
    load_price_panel,
    load_symbols_price_frame,
)
from studies.momentum.features import precompute_features  # noqa: E402
from studies.momentum.features import canonicalize_prices  # noqa: E402
from studies.momentum.filters import FilterConfig, FilterResult, apply_filters  # noqa: E402
from studies.momentum.grid import build_strategy_grid  # noqa: E402
from studies.momentum.plots import (  # noqa: E402
    plot_strategy_panel,
    select_finalists,
    write_aggregate_plots,
)
from studies.momentum.report import write_data_audit, write_json, write_report  # noqa: E402
from studies.momentum.strategies import (  # noqa: E402
    holdings_loop_returns,
    simulate_strategy,
)
from studies.momentum.validation import (  # noqa: E402
    metrics_from_returns,
    pbo_summary,
    result_row,
)


STUDY_DIR = Path(__file__).resolve().parent
RESULTS_DIR = STUDY_DIR / "results"
DATA_AUDIT = STUDY_DIR / "DATA_AUDIT.md"
REPORT = STUDY_DIR / "REPORT.md"
PLOTS_DIR = STUDY_DIR / "plots"
CACHE_DIR = STUDY_DIR / "cache"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Postgres-backed momentum grid")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--phase", choices=["broad", "validate"], default="broad")
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--limit-configs", type=int, default=None)
    parser.add_argument("--max-symbols", type=int, default=None)
    parser.add_argument("--no-plots", action="store_true", help="Skip PNG plot generation")
    parser.add_argument("--max-plots", type=int, default=30, help="Maximum individual finalist plots")
    parser.add_argument(
        "--cache-panels",
        action="store_true",
        help="Cache filtered price panels locally under studies/momentum/cache/",
    )
    parser.add_argument("--refresh-cache", action="store_true", help="Rebuild local panel cache")
    parser.add_argument(
        "--cross-check",
        choices=["auto", "always", "never"],
        default="auto",
        help="Run independent holdings-loop cross-check; auto means validate phase only",
    )
    parser.add_argument(
        "--pbo-max-configs",
        type=int,
        default=None,
        help="Deterministically sample at most N configs for PBO; default is phase-dependent",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=50,
        help="Print progress every N simulated configs; use 0 for milestones only",
    )
    return parser.parse_args(argv)


def progress(message: str) -> None:
    """Print immediately so long terminal runs show live progress."""
    print(message, flush=True)


def fmt_elapsed(start: float) -> str:
    elapsed = max(time.perf_counter() - start, 0.0)
    minutes, seconds = divmod(int(elapsed), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}h{minutes:02d}m{seconds:02d}s"
    if minutes:
        return f"{minutes:d}m{seconds:02d}s"
    return f"{seconds:d}s"


def fmt_duration(seconds: float) -> str:
    seconds = max(float(seconds), 0.0)
    if seconds >= 3600:
        hours, rem = divmod(seconds, 3600)
        minutes, sec = divmod(rem, 60)
        return f"{int(hours)}h{int(minutes):02d}m{sec:04.1f}s"
    if seconds >= 60:
        minutes, sec = divmod(seconds, 60)
        return f"{int(minutes)}m{sec:04.1f}s"
    return f"{seconds:.2f}s"


def add_timing(stage_times: MutableMapping[str, float], stage: str, started_at: float) -> None:
    stage_times[stage] = stage_times.get(stage, 0.0) + max(time.perf_counter() - started_at, 0.0)


def print_timing_breakdown(
    stage_times: dict[str, float], *, total_seconds: float, n_trials: int, n_success: int
) -> None:
    accounted = sum(stage_times.values())
    unaccounted = max(total_seconds - accounted, 0.0)
    if unaccounted > 1e-6:
        stage_times = {**stage_times, "unaccounted": unaccounted}
    progress("[timing] breakdown:")
    for stage, seconds in sorted(stage_times.items(), key=lambda item: item[1], reverse=True):
        pct = 100.0 * seconds / total_seconds if total_seconds > 0 else 0.0
        per_config = ""
        if stage in {"simulate_strategy", "metrics_validation", "cross_check"} and n_success:
            per_config = f" ({1000.0 * seconds / n_success:.1f} ms/success)"
        progress(f"[timing] {stage}: {fmt_duration(seconds)} {pct:.1f}%{per_config}")
    if n_trials:
        progress(
            f"[timing] total={fmt_duration(total_seconds)} success={n_success}/{n_trials} "
            f"throughput={n_trials / max(total_seconds, 1e-9):.2f} configs/s"
        )


def effective_validation_config(raw: dict[str, Any], phase: str) -> dict[str, Any]:
    """Return phase-specific validation settings.

    Broad screens are discovery runs, so expensive bootstrap/rolling diagnostics
    are deferred to `validate` `[advances_fin_ml, p.208-211]`,
    `[advances_fin_ml, p.273-275]`.
    """
    out = dict(raw)
    if phase == "broad":
        out["bootstrap_resamples"] = int(out.get("broad_bootstrap_resamples", 0))
        out["rolling_years"] = [int(x) for x in out.get("broad_rolling_years", [])]
    return out


def pbo_max_configs_for(args: argparse.Namespace, validation_config: dict[str, Any]) -> int | None:
    if args.pbo_max_configs is not None:
        return None if args.pbo_max_configs <= 0 else int(args.pbo_max_configs)
    if args.phase == "broad":
        value = int(validation_config.get("broad_pbo_max_configs", 1000))
        return None if value <= 0 else value
    value = int(validation_config.get("pbo_max_configs", 0))
    return None if value <= 0 else value


def should_cross_check(args: argparse.Namespace) -> bool:
    if args.cross_check == "always":
        return True
    if args.cross_check == "never":
        return False
    return args.phase == "validate"


def panel_cache_path(
    config: dict[str, Any], args: argparse.Namespace, universe: str, max_symbols: int | None
) -> Path:
    run_cfg = config.get("run", {})
    payload = {
        "universe": universe,
        "schema": schema_name(config),
        "price_column": price_column(config),
        "start": str(run_cfg.get("start")),
        "end": str(run_cfg.get("end")),
        "max_symbols": max_symbols,
        "filters": config.get("filters", {}),
    }
    raw = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    digest = hashlib.sha1(raw).hexdigest()[:12]
    return CACHE_DIR / f"{universe}_{digest}.pkl"


def load_filtered_panel_with_cache(
    conn,
    config: dict[str, Any],
    args: argparse.Namespace,
    universe: str,
    max_symbols: int | None,
) -> tuple[FilterResult, dict[str, object], bool]:
    cache_path = panel_cache_path(config, args, universe, max_symbols)
    if args.cache_panels and cache_path.exists() and not args.refresh_cache:
        with cache_path.open("rb") as fh:
            payload = pickle.load(fh)  # noqa: S301 - local cache controlled by this CLI.
        return payload["filtered"], payload["row"], True

    run_cfg = config.get("run", {})
    panel = load_price_panel(
        conn,
        schema=schema_name(config),
        universe=str(universe),
        price_column=price_column(config),
        start=run_cfg.get("start"),
        end=run_cfg.get("end"),
        max_symbols=max_symbols,
    )
    filtered, filter_keys = filter_panel_by_metadata(panel, config)
    row = {
        "universe": universe,
        "raw_symbols": len(panel.metadata),
        "loaded_symbols": len(panel.prices.columns),
        "passed_filter": len(filtered.prices.columns),
        "start": str(filtered.prices.index.min().date()) if not filtered.prices.empty else "n/a",
        "end": str(filtered.prices.index.max().date()) if not filtered.prices.empty else "n/a",
        "filter_keys": ",".join(filter_keys),
    }
    if args.cache_panels:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with cache_path.open("wb") as fh:
            pickle.dump({"filtered": filtered, "row": row}, fh, protocol=pickle.HIGHEST_PROTOCOL)
    return filtered, row, False


def filter_panel_by_metadata(panel: PricePanel, config: dict[str, Any]) -> tuple[FilterResult, list[str]]:
    """Apply per-country/asset-class filters, including mixed universes."""
    if panel.prices.empty or panel.metadata.empty:
        return FilterResult(panel.prices, panel.volumes, panel.metadata, pd.DataFrame()), []
    diagnostics: list[pd.DataFrame] = []
    passed_prices: list[pd.DataFrame] = []
    passed_volumes: list[pd.DataFrame] = []
    passed_metadata: list[pd.DataFrame] = []
    filter_keys: list[str] = []
    for (country, asset_class), meta in panel.metadata.groupby(["country", "asset_class"]):
        symbols = meta["yf_symbol"].astype(str).str.upper().tolist()
        raw_filter = merged_filter_config(config, str(country), str(asset_class))
        filter_cfg = FilterConfig.from_dict(raw_filter)
        result = apply_filters(
            panel.prices.reindex(columns=symbols),
            panel.volumes.reindex(columns=symbols),
            meta,
            filter_cfg,
        )
        key = "crypto" if asset_class == "crypto" else f"{country}_{asset_class}"
        filter_keys.append(key)
        if not result.diagnostics.empty:
            diag = result.diagnostics.copy()
            diag["filter_key"] = key
            diagnostics.append(diag)
        if not result.prices.empty:
            passed_prices.append(result.prices)
            passed_volumes.append(result.volumes)
            passed_metadata.append(result.metadata)
    prices = pd.concat(passed_prices, axis=1).sort_index() if passed_prices else pd.DataFrame()
    volumes = pd.concat(passed_volumes, axis=1).sort_index() if passed_volumes else pd.DataFrame()
    metadata = pd.concat(passed_metadata, axis=0).drop_duplicates("yf_symbol") if passed_metadata else pd.DataFrame()
    diag = pd.concat(diagnostics, axis=0).sort_values("yf_symbol") if diagnostics else pd.DataFrame()
    return FilterResult(prices, volumes, metadata, diag), sorted(set(filter_keys))


def write_audit_only(conn, config: dict[str, Any], args: argparse.Namespace, db_url: str) -> None:
    progress(f"[audit] database={masked_database_url(db_url)}")
    db_summary = audit_database(conn, schema=schema_name(config))
    universe_rows = audit_universes(conn, config, args)
    write_data_audit(
        DATA_AUDIT,
        db_summary=db_summary,
        universe_rows=universe_rows,
        database_label=masked_database_url(db_url),
    )


def audit_universes(conn, config: dict[str, Any], args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    run_cfg = config.get("run", {})
    max_symbols = args.max_symbols or run_cfg.get("max_symbols_per_universe")
    for universe in config.get("grid", {}).get("universes", []):
        progress(f"[audit] loading universe={universe} max_symbols={max_symbols or 'all'}")
        panel = load_price_panel(
            conn,
            schema=schema_name(config),
            universe=str(universe),
            price_column=price_column(config),
            start=run_cfg.get("start"),
            end=run_cfg.get("end"),
            max_symbols=max_symbols,
        )
        filtered, filter_keys = filter_panel_by_metadata(panel, config)
        progress(
            f"[audit] universe={universe} raw={len(panel.metadata)} "
            f"loaded={len(panel.prices.columns)} passed={len(filtered.prices.columns)}"
        )
        rows.append(
            {
                "universe": universe,
                "raw_symbols": len(panel.metadata),
                "loaded_symbols": len(panel.prices.columns),
                "passed_filter": len(filtered.prices.columns),
                "start": str(filtered.prices.index.min().date()) if not filtered.prices.empty else "n/a",
                "end": str(filtered.prices.index.max().date()) if not filtered.prices.empty else "n/a",
                "filter_keys": ",".join(filter_keys),
            }
        )
    return rows


def run_grid(conn, config: dict[str, Any], args: argparse.Namespace) -> int:
    started = time.perf_counter()
    stage_times: dict[str, float] = {}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    run_cfg = config.get("run", {})
    feature_cfg = config.get("features", {})
    validation_cfg = effective_validation_config(config.get("validation", {}), args.phase)
    pbo_max_configs = pbo_max_configs_for(args, validation_cfg)
    run_cross_check = should_cross_check(args)
    max_symbols = args.max_symbols or run_cfg.get("max_symbols_per_universe")
    filtered_panels: dict[str, FilterResult] = {}
    universe_assets: dict[str, tuple[str, ...]] = {}
    universe_rows: list[dict[str, object]] = []
    errors: list[str] = []
    progress(
        f"[run] config={args.config} phase={args.phase} max_symbols={max_symbols or 'all'} "
        f"limit_configs={args.limit_configs or 'all'} plots={'off' if args.no_plots else 'on'} "
        f"cross_check={'on' if run_cross_check else 'off'} "
        f"bootstrap_resamples={validation_cfg.get('bootstrap_resamples', 0)} "
        f"pbo_max_configs={pbo_max_configs or 'all'} cache_panels={'on' if args.cache_panels else 'off'}"
    )

    for universe in config.get("grid", {}).get("universes", []):
        try:
            progress(f"[data] loading universe={universe}")
            stage_started = time.perf_counter()
            filtered, universe_row, cache_hit = load_filtered_panel_with_cache(
                conn, config, args, str(universe), max_symbols
            )
            add_timing(stage_times, "data_load_filter", stage_started)
            cache_label = " cache=hit" if cache_hit else " cache=miss"
            progress(
                f"[data] universe={universe} raw={universe_row['raw_symbols']} "
                f"loaded={universe_row['loaded_symbols']} passed={universe_row['passed_filter']} "
                f"elapsed={fmt_elapsed(started)}{cache_label}"
            )
            filtered_panels[str(universe)] = filtered
            universe_assets[str(universe)] = tuple(str(col).upper() for col in filtered.prices.columns)
            if not filtered.diagnostics.empty:
                filtered.diagnostics.to_csv(
                    RESULTS_DIR / f"filter_diagnostics_{universe}.csv",
                    index=False,
                )
            universe_rows.append(universe_row)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{universe}: {exc}")
            progress(f"[data] universe={universe} error={exc}")

    stage_started = time.perf_counter()
    configs = build_strategy_grid(config, universe_assets)
    if args.limit_configs is not None:
        configs = configs[: args.limit_configs]
    n_trials = len(configs)
    grouped: dict[str, list] = {}
    for strategy_config in configs:
        grouped.setdefault(strategy_config.universe, []).append(strategy_config)
    add_timing(stage_times, "grid_build", stage_started)
    progress(f"[grid] configs={n_trials} universes={len(grouped)}")
    for universe, strategy_configs in grouped.items():
        progress(f"[grid] universe={universe} configs={len(strategy_configs)}")

    benchmark_cache: dict[str, pd.DataFrame] = {}
    rows: list[dict[str, Any]] = []
    returns_by_name: dict[str, pd.Series] = {}
    processed = 0
    progress_every = max(int(args.progress_every), 0)
    for universe, strategy_configs in grouped.items():
        filtered = filtered_panels.get(universe)
        if filtered is None or filtered.prices.empty:
            errors.append(f"{universe}: no prices after filters")
            progress(f"[skip] universe={universe} no prices after filters")
            continue
        score_modes = sorted({cfg.score_mode for cfg in strategy_configs})
        stage_started = time.perf_counter()
        daily_prices = canonicalize_prices(filtered.prices)
        daily_returns = daily_prices.pct_change(fill_method=None).fillna(0.0)
        add_timing(stage_times, "daily_returns", stage_started)
        progress(
            f"[features] universe={universe} assets={len(filtered.prices.columns)} "
            f"score_modes={','.join(score_modes)}"
        )
        stage_started = time.perf_counter()
        bundle = precompute_features(
            daily_prices,
            score_modes=score_modes,
            raw_lookbacks=feature_cfg.get("lookbacks", {}).get("raw_13612", [1, 3, 6, 12]),
            mom_3_6_12_lookbacks=feature_cfg.get("lookbacks", {}).get("mom_3_6_12", [3, 6, 12]),
            vol_window_days=int(feature_cfg.get("vol_window_days", 126)),
            trend_window_days=int(feature_cfg.get("trend_window_days", 126)),
        )
        add_timing(stage_times, "feature_precompute", stage_started)
        benchmark_symbol = str(run_cfg.get("benchmark_by_universe", {}).get(universe, "SPY")).upper()
        if benchmark_symbol not in benchmark_cache:
            stage_started = time.perf_counter()
            benchmark_cache[benchmark_symbol] = load_symbols_price_frame(
                conn,
                schema=schema_name(config),
                symbols=(benchmark_symbol,),
                price_column=price_column(config),
                start=run_cfg.get("start"),
                end=run_cfg.get("end"),
            )
            add_timing(stage_times, "benchmark_load", stage_started)
        benchmark_prices = benchmark_cache[benchmark_symbol]
        if benchmark_prices.empty:
            errors.append(f"{universe}: benchmark {benchmark_symbol} not available in Postgres yet")
            progress(f"[benchmark] universe={universe} symbol={benchmark_symbol} missing")
        else:
            progress(
                f"[benchmark] universe={universe} symbol={benchmark_symbol} "
                f"rows={len(benchmark_prices)}"
            )
        for strategy_config in strategy_configs:
            processed += 1
            try:
                stage_started = time.perf_counter()
                simulation = simulate_strategy(
                    filtered.prices,
                    bundle,
                    strategy_config,
                    daily_prices=daily_prices,
                    daily_returns=daily_returns,
                )
                add_timing(stage_times, "simulate_strategy", stage_started)
                if simulation.returns.empty:
                    continue
                xlib_delta_pp = float("nan")
                if run_cross_check:
                    stage_started = time.perf_counter()
                    loop = holdings_loop_returns(
                        filtered.prices,
                        simulation.rebalance_weights,
                        strategy_config.name,
                        daily_prices=daily_prices,
                        daily_returns=daily_returns,
                    )
                    aligned = pd.concat({"vectorized": simulation.returns, "loop": loop}, axis=1).dropna()
                    if not aligned.empty:
                        vec = metrics_from_returns(aligned["vectorized"])
                        ref = metrics_from_returns(aligned["loop"])
                        xlib_delta_pp = abs(float(vec["cagr"]) - float(ref["cagr"])) * 100.0
                    add_timing(stage_times, "cross_check", stage_started)
                stage_started = time.perf_counter()
                row = result_row(
                    strategy_config,
                    simulation,
                    benchmark_prices,
                    n_trials=n_trials,
                    validation_config=validation_cfg,
                    xlib_cagr_delta_pp=xlib_delta_pp,
                )
                add_timing(stage_times, "metrics_validation", stage_started)
                row["benchmark_symbol"] = benchmark_symbol
                row["source"] = "postgres_yfinance_cache"
                rows.append(row)
                returns_by_name[strategy_config.name] = simulation.returns
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{strategy_config.name}: {exc}")
            if progress_every and (processed == 1 or processed % progress_every == 0 or processed == n_trials):
                progress(
                    f"[simulate] {processed}/{n_trials} ok={len(rows)} "
                    f"errors={len(errors)} elapsed={fmt_elapsed(started)}"
                )

    stage_started = time.perf_counter()
    results = pd.DataFrame(rows)
    if not results.empty:
        results.to_csv(RESULTS_DIR / "broad_results.csv", index=False)
    write_json(RESULTS_DIR / "broad_results.json", rows)
    add_timing(stage_times, "write_results", stage_started)
    stage_started = time.perf_counter()
    pbo_data = pbo_summary(
        returns_by_name,
        results[["name", "universe", "mechanism"]] if not results.empty else pd.DataFrame(),
        int(validation_cfg.get("pbo_blocks", 10)),
        max_configs=pbo_max_configs,
    )
    write_json(RESULTS_DIR / "broad_pbo.json", pbo_data)
    add_timing(stage_times, "pbo_summary", stage_started)
    plot_paths: list[str] = []
    if not args.no_plots and not results.empty:
        progress(f"[plots] writing aggregate/finalist plots max_plots={args.max_plots}")
        stage_started = time.perf_counter()
        try:
            plot_paths.extend(write_aggregate_plots(results, PLOTS_DIR, STUDY_DIR))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"plots aggregate: {exc}")
        finalists = select_finalists(results, max_finalists=max(int(args.max_plots), 0))
        for _, row in finalists.iterrows():
            name = str(row["name"])
            benchmark_symbol = str(row.get("benchmark_symbol", "SPY")).upper()
            try:
                path = plot_strategy_panel(
                    name,
                    returns_by_name.get(name, pd.Series(dtype=float)),
                    benchmark_cache.get(benchmark_symbol, pd.DataFrame()),
                    benchmark_symbol,
                    PLOTS_DIR / "finalists",
                    STUDY_DIR,
                )
                if path is not None:
                    plot_paths.append(path)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"plot {name}: {exc}")
        add_timing(stage_times, "plots", stage_started)
    write_json(RESULTS_DIR / "plot_manifest.json", {"plots": plot_paths})
    progress("[reports] writing DATA_AUDIT.md and REPORT.md")
    stage_started = time.perf_counter()
    db_summary = audit_database(conn, schema=schema_name(config))
    write_data_audit(
        DATA_AUDIT,
        db_summary=db_summary,
        universe_rows=universe_rows,
        database_label="local Postgres yfinance cache",
    )
    write_report(
        REPORT,
        results=results,
        pbo_rows=pbo_data["rows"],
        errors=errors,
        n_trials=n_trials,
        config_path=args.config,
        phase=args.phase,
        plot_paths=plot_paths,
    )
    add_timing(stage_times, "reports", stage_started)
    print(f"wrote {REPORT.relative_to(REPO_ROOT)}")
    print(f"wrote {(RESULTS_DIR / 'broad_results.json').relative_to(REPO_ROOT)}")
    if plot_paths:
        print(f"wrote {len(plot_paths)} plot(s) under {PLOTS_DIR.relative_to(REPO_ROOT)}")
    print(f"simulated {len(results)}/{n_trials} configs")
    print(f"elapsed {fmt_elapsed(started)}")
    if errors:
        print("errors/skips:")
        for error in errors[:25]:
            print(f"- {error}")
    print_timing_breakdown(
        stage_times,
        total_seconds=time.perf_counter() - started,
        n_trials=n_trials,
        n_success=len(results),
    )
    return 0 if len(results) else 2


def main(argv: list[str] | None = None) -> int:
    load_env_file()
    args = parse_args(argv)
    config = load_config(args.config)
    db_url = database_url(config)
    with connect(db_url) as conn:
        if args.audit_only:
            write_audit_only(conn, config, args, db_url)
            print(f"wrote {DATA_AUDIT.relative_to(REPO_ROOT)}")
            return 0
        return run_grid(conn, config, args)


if __name__ == "__main__":
    raise SystemExit(main())
