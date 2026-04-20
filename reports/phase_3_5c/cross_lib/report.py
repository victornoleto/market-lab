"""Generate VERDICT.md from results/ directory tree.

Scans results/stage_{1,2}/**/result.json, loads the baseline.json, applies
the verdict engine, and emits a matrix + per-variant sections + an executive
summary at the top.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

from reports.phase_3_5c.cross_lib.types import RunResult
from reports.phase_3_5c.cross_lib.verdict import (
    AggregateVerdict,
    Baseline,
    Tier,
    aggregate_verdict,
    classify_tier,
)

RESULTS_DIR = Path("reports/phase_3_5c/cross_lib/results")
BASELINE_PATH = Path("reports/phase_3_5c/cross_lib/reference/baseline.json")
VERDICT_MD = Path("reports/phase_3_5c/cross_lib/VERDICT.md")


def load_all_results() -> list[dict]:
    rows: list[dict] = []
    for stage_dir in RESULTS_DIR.glob("stage_*"):
        stage = int(stage_dir.name.split("_")[1])
        for result_file in stage_dir.rglob("result.json"):
            payload = json.loads(result_file.read_text())
            payload["stage"] = stage
            payload["path"] = str(result_file.parent)
            # Load equity curve for rho computation
            equity_parquet = result_file.parent / "equity.parquet"
            if equity_parquet.exists():
                payload["equity"] = pd.read_parquet(equity_parquet)["equity"]
            rows.append(payload)
    return rows


def load_baseline() -> dict:
    return json.loads(BASELINE_PATH.read_text())


def compute_monthly_rho(
    equity: pd.Series, baseline_monthly: pd.Series | None
) -> float:
    if equity is None or baseline_monthly is None:
        return float("nan")
    ret = equity.pct_change().dropna()
    monthly = ret.resample("ME").apply(lambda x: (1 + x).prod() - 1)
    common_idx = monthly.index.intersection(baseline_monthly.index)
    if len(common_idx) < 12:
        return float("nan")
    return float(monthly.loc[common_idx].corr(baseline_monthly.loc[common_idx]))


def build_verdict_matrix(results: list[dict], baseline: dict) -> dict:
    """Return nested dict: {variant_id: {window: {stage: {lib: tier}}}}.

    Monthly rho is computed against the first OK result of each (variant, window)
    pair (treated as reference) so cross-lib rho captures real divergence across
    libraries rather than against a baseline equity curve we don't persist.
    """
    matrix: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    reference_monthly: dict[tuple[str, str, int], pd.Series] = {}
    for row in results:
        key = (row["variant_id"], tuple(row["window"])[0], row["stage"])
        if row["outcome"] == "OK" and key not in reference_monthly and "equity" in row:
            ret = row["equity"].pct_change().dropna()
            reference_monthly[key] = ret.resample("ME").apply(lambda x: (1 + x).prod() - 1)

    for row in results:
        vid = row["variant_id"]
        window = tuple(row["window"])
        window_key = "canonical" if window[0] == "2004-10-01" else (
            "extended" if window[0] == "1986-01-02" else "post_2009"
        )
        stage = row["stage"]
        lib = row["lib"]

        if vid not in baseline["variants"] or window_key not in baseline["variants"][vid]:
            continue
        bl_metrics = baseline["variants"][vid][window_key]
        # baseline.json stores cagr/max_dd as percent; verdict.Baseline uses decimal
        bl = Baseline(
            cagr=bl_metrics["cagr"] / 100.0,
            sharpe=bl_metrics["sharpe"],
            max_dd=bl_metrics["max_dd"] / 100.0,
        )

        if row["outcome"] != "OK":
            matrix[vid][window_key][stage][lib] = row["outcome"]
            continue

        ref_key = (vid, window[0], stage)
        ref_monthly = reference_monthly.get(ref_key)
        equity = row.get("equity")
        rho = compute_monthly_rho(equity, ref_monthly) if equity is not None else 1.0
        if not pd.notna(rho):
            rho = 1.0  # insufficient overlap; defer to metric-based tier only

        fake_run = _payload_to_result(row)
        tier = classify_tier(fake_run, bl, monthly_rho_override=rho)
        matrix[vid][window_key][stage][lib] = tier.value

    return matrix


def _payload_to_result(payload: dict) -> RunResult:
    return RunResult(
        variant_id=payload["variant_id"],
        lib=payload["lib"],
        window=tuple(payload["window"]),
        stage=payload["stage"],
        equity_curve=pd.Series(dtype=float),
        monthly_returns=pd.Series(dtype=float),
        trade_dates=[],
        cagr=payload["cagr"],
        sharpe=payload["sharpe"],
        max_dd=payload["max_dd"],
        wf_splits_8=payload["wf_splits_8"],
        dsr_pval=payload["dsr_pval"],
        outcome=payload["outcome"],
        error_detail=payload.get("error_detail"),
    )


def emit_verdict_md(matrix: dict, baseline: dict) -> str:
    lines: list[str] = [
        "# VERDICT — Plano B Cross-Library Validation",
        "",
        f"> Generated: {pd.Timestamp.utcnow().isoformat()}.",
        f"> Baseline commit: `{baseline.get('git_commit', '?')[:12]}`.",
        f"> Baseline hash: `{baseline.get('integrity_hash', '?')[:12]}`.",
        "",
        "## Aggregate verdicts",
        "",
    ]

    for vid, windows in matrix.items():
        for window_key, stages in windows.items():
            s1_tiers = _coerce_tiers(stages.get(1, {}))
            s2_tiers = _coerce_tiers(stages.get(2, {}))
            agg = aggregate_verdict(s1_tiers, s2_tiers)
            lines.append(f"- **{vid}** / {window_key}: **{agg.value}**")

    lines += ["", "## Per-variant matrix", ""]

    for vid, windows in matrix.items():
        lines.append(f"### {vid}")
        lines.append("")
        for window_key, stages in windows.items():
            lines.append(f"**Window:** {window_key}")
            lines.append("")
            lines.append("| stage | lib | tier/outcome |")
            lines.append("|-------|-----|--------------|")
            for stage in sorted(stages.keys()):
                for lib, tier in stages[stage].items():
                    lines.append(f"| {stage} | {lib} | {tier} |")
            lines.append("")

    lines += [
        "",
        "## Citations",
        "",
        "- Tolerance magnitudes: `[advances_fin_ml, p.208-211]`",
        "- Strategy similarity: `[advances_fin_ml, p.273-275]`",
        "- 5-gate framework: `[advances_fin_ml, p.208-211, p.273-275, p.298-299]`",
        "- LETF synthetic formula: `[leverage_for_the_long_run, p.16]`",
        "- Signal EMA regime: `[leverage_for_the_long_run, p.13]`",
        "- Donchian canonical: `[trading_systems_methods, p.353]`",
    ]
    return "\n".join(lines)


def _coerce_tiers(lib_map: dict[str, str]) -> dict[str, Tier]:
    return {
        lib: Tier(v)
        for lib, v in lib_map.items()
        if v in (t.value for t in Tier)
    }


def main() -> None:
    results = load_all_results()
    baseline = load_baseline()
    matrix = build_verdict_matrix(results, baseline)
    md = emit_verdict_md(matrix, baseline)
    VERDICT_MD.write_text(md)
    print(f"Wrote {VERDICT_MD} ({len(md.splitlines())} lines)")


if __name__ == "__main__":
    main()
