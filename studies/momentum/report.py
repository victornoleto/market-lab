"""Markdown/JSON report helpers for the momentum study."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


def fmt_pct(value: float, digits: int = 2) -> str:
    if not math.isfinite(float(value)):
        return "n/a"
    return f"{100.0 * float(value):.{digits}f}%"


def fmt_num(value: float, digits: int = 3) -> str:
    if not math.isfinite(float(value)):
        return "n/a"
    return f"{float(value):.{digits}f}"


def md_value(value: object) -> str:
    if isinstance(value, np.integer):
        value = int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float) and not math.isfinite(value):
        return "n/a"
    return str(value)


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._\n"
    header = "| " + " | ".join(columns) + " |"
    sep = "|" + "|".join("---" for _ in columns) + "|"
    body = ["| " + " | ".join(md_value(row.get(col, "")) for col in columns) + " |" for row in rows]
    return "\n".join([header, sep, *body]) + "\n"


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(payload), indent=2, allow_nan=False), encoding="utf-8")


def write_data_audit(
    path: Path,
    *,
    db_summary: pd.DataFrame,
    universe_rows: list[dict[str, object]],
    database_label: str,
) -> None:
    db_rows = db_summary.to_dict(orient="records") if not db_summary.empty else []
    path.write_text(
        "# Momentum Data Audit\n\n"
        "Status: Postgres-backed yfinance cache audit for `studies/momentum/`.\n\n"
        f"Database: `{database_label}`\n\n"
        "## Database Coverage\n\n"
        + md_table(
            db_rows,
            [
                "country",
                "asset_class",
                "n_tickers",
                "first_date",
                "last_date",
                "n_active",
                "n_with_error",
            ],
        )
        + "\n## Universe Filter Coverage\n\n"
        + md_table(
            universe_rows,
            [
                "universe",
                "raw_symbols",
                "loaded_symbols",
                "passed_filter",
                "start",
                "end",
                "filter_keys",
            ],
        )
        + "\n## Caveat\n\n"
        "The local cache accelerates tests, but yfinance/current-universe data remain "
        "screen-only until point-in-time membership, delisted symbols and corporate "
        "actions are audited `[advances_fin_ml, p.208-211]`.\n",
        encoding="utf-8",
    )


def format_result_rows(frame: pd.DataFrame, n: int = 30) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for _, row in frame.head(n).iterrows():
        rows.append(
            {
                "Name": row["name"],
                "Universe": row["universe"],
                "Mechanism": row["mechanism"],
                "Top-N": int(row["top_n"]),
                "Reb": int(row["rebalance_months"]),
                "Off": int(row["rebalance_offset"]),
                "Stag": bool(row["staggered_offsets"]),
                "CAGR": fmt_pct(float(row["cagr"])),
                "Excess": fmt_pct(float(row["excess_cagr"])),
                "MDD": fmt_pct(float(row["mdd"])),
                "Sharpe": fmt_num(float(row["sharpe"])),
                "Calmar": fmt_num(float(row["calmar"])),
                "DSR p": fmt_num(float(row["dsr_p_value"])),
                "WF": f"{int(row['wf_positive'])}/{int(row['wf_windows'])}",
                "Turnover": fmt_num(float(row["annual_turnover"])),
            }
        )
    return rows


def write_report(
    path: Path,
    *,
    results: pd.DataFrame,
    pbo_rows: list[dict[str, object]],
    errors: list[str],
    n_trials: int,
    config_path: Path,
    phase: str = "broad",
    plot_paths: list[str] | None = None,
) -> None:
    if results.empty:
        verdict = "Data-blocked: no successful strategy rows."
        top_sharpe = results
        top_excess = results
    else:
        top_sharpe = results.sort_values(["sharpe", "excess_cagr"], ascending=False)
        top_excess = results.sort_values(["excess_cagr", "sharpe"], ascending=False)
        all_pbo = next((row for row in pbo_rows if row.get("group") == "all"), {})
        sample_suffix = ""
        if all_pbo.get("sampled"):
            sample_suffix = f" sampled `{all_pbo.get('n_configs')}/{all_pbo.get('n_configs_total')}`."
        verdict = (
            "Research-only screen: results use local yfinance/current-universe cache and "
            f"are not promotion-eligible. Overall PBO = `{float(all_pbo.get('pbo', float('nan'))):.3f}`{sample_suffix}."
        )
    error_text = "\n".join(f"- {error}" for error in errors) if errors else "_No run errors._"
    plot_text = "_No plots generated._"
    if plot_paths:
        plot_text = "\n".join(f"- [`{path}`]({path})" for path in plot_paths)
    path.write_text(
        "# Momentum Study Report\n\n"
        "Status: research-only. No deployment, paper-trade label or mandate change.\n\n"
        "## Verdict\n\n"
        f"{verdict}\n\n"
        "## Run\n\n"
        f"- Config: `{config_path}`\n"
        f"- Phase: `{phase}`\n"
        f"- Successful rows: `{len(results)}`\n"
        f"- Trial count used in DSR: `{n_trials}`\n"
        "- Data source: local Postgres `yf_tickers`/`yf_daily_prices`\n\n"
        "## Top 30 By Sharpe\n\n"
        + md_table(
            format_result_rows(top_sharpe),
            [
                "Name",
                "Universe",
                "Mechanism",
                "Top-N",
                "Reb",
                "Off",
                "Stag",
                "CAGR",
                "Excess",
                "MDD",
                "Sharpe",
                "Calmar",
                "DSR p",
                "WF",
                "Turnover",
            ],
        )
        + "\n## Top 30 By Excess CAGR\n\n"
        + md_table(
            format_result_rows(top_excess),
            [
                "Name",
                "Universe",
                "Mechanism",
                "Top-N",
                "Reb",
                "Off",
                "Stag",
                "CAGR",
                "Excess",
                "MDD",
                "Sharpe",
                "Calmar",
                "DSR p",
                "WF",
                "Turnover",
            ],
        )
        + "\n## PBO Summary\n\n"
        + md_table(
            pbo_rows,
            [
                "group",
                "pbo",
                "n_configs",
                "n_configs_total",
                "sampled",
                "n_obs",
                "n_combinations",
                "pass",
            ],
        )
        + "\n## Plots\n\n"
        + plot_text
        + "\n\n## Errors / Skips\n\n"
        + error_text
        + "\n\n## Caveats\n\n"
        "- yfinance/current-universe rows remain screen-only `[advances_fin_ml, p.208-211]`.\n"
        "- Broad grids must pay multiple-testing costs `[advances_fin_ml, p.273-275]`.\n"
        "- Results are gross of transaction costs and taxes in this scaffold.\n"
        "- CAGR/MDD are warning tiers under the mandate, not promotion gates.\n",
        encoding="utf-8",
    )
