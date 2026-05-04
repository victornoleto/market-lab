"""Build the v4 Fase 3b offline copyability scoreboard.

The gates and weights are intentionally duplicated from the pre-registered
`FILTER_COPY_PLAN.md`; changing them after observing the ranking would be a
data-mining error [evidence_based_ta, p.247-260]. Track-record evidence keeps
MCPT [evidence_based_ta, p.325-328] and PSR for a single EA return series
[advances_fin_ml, p.260-263]. Selecting top systems from 21 alternatives is
reported as ranking/multiple-testing risk [advances_fin_ml, p.273-275]. A fixed
2.0-pip round-trip overlay models copy friction for short strategies
[systematic_trading, p.182-197].
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
STUDY_ROOT = ROOT / "studies" / "myfxbook_reverse_engineering"
SYSTEMS_ROOT = STUDY_ROOT / "systems"
TRADES_ROOT = STUDY_ROOT / "data" / "trades"
DIAGNOSTICS_ROOT = STUDY_ROOT / "_diagnostics"
RESULTS_007 = STUDY_ROOT / "v4_redesign" / "iterations" / "007-fase1-batch-run" / "RESULTS.json"

AUDIT_ONLY_SYSTEM_IDS = [
    "10062918",
    "10067081",
    "10249298",
    "10281851",
    "10563761",
    "10734338",
    "11155858",
    "11206045",
    "11207608",
    "1152318",
    "11628637",
    "1407880",
    "1612420",
    "2421356",
    "6541963",
    "8577442",
    "8647517",
    "9375654",
    "9830783",
    "9841939",
    "9912554",
]

RANKING_SELECTION_WARNING = (
    "Top-N selection across 21 EAs is multiple testing / data-mining risk; "
    "shortlist is diagnostic only [advances_fin_ml, p.273-275] "
    "[evidence_based_ta, p.247-260]."
)


@dataclass(frozen=True)
class OperationalMetrics:
    n_trades: int
    first_close: str | None
    last_close: str | None
    positive_month_ratio: float
    max_no_trade_gap_days: float
    recent_90d_drawdown: float
    historical_max_drawdown: float
    recent_dd_ratio: float
    median_monthly_trades: float
    total_gross_pips: float
    total_cost_pips: float
    total_net_pips: float
    avg_net_pips_per_trade: float
    cost_drag_ratio: float
    n_symbols: int
    n_symbols_with_positive_pnl: int
    top_symbol_pnl_share: float
    top_symbol: str | None


def clamp01(value: float) -> float:
    if math.isnan(value) or math.isinf(value):
        return 0.0
    return max(0.0, min(1.0, value))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_pre_screen(system_id: str) -> dict[str, Any]:
    path = SYSTEMS_ROOT / system_id / "decoding_v4_fase1" / "pre_decode_screen.json"
    if not path.exists():
        raise FileNotFoundError(f"pre_decode_screen.json missing for {system_id}: {path}")
    return read_json(path)


def load_trades(system_id: str) -> pd.DataFrame:
    path = TRADES_ROOT / system_id / "trades.parquet"
    if not path.exists():
        raise FileNotFoundError(f"trades.parquet missing for {system_id}: {path}")
    trades = pd.read_parquet(path)
    required = {"is_trade", "close_dt_utc", "symbol", "pips"}
    missing = sorted(required.difference(trades.columns))
    if missing:
        raise ValueError(f"trades.parquet for {system_id} missing columns: {missing}")
    trades = trades[trades["is_trade"].astype(bool)].copy()
    trades["close_dt_utc"] = pd.to_datetime(trades["close_dt_utc"], utc=True)
    trades["pips"] = pd.to_numeric(trades["pips"], errors="coerce")
    trades = trades.dropna(subset=["close_dt_utc", "pips"]).sort_values("close_dt_utc")
    trades["symbol"] = trades["symbol"].astype(str)
    return trades


def max_drawdown(values: pd.Series) -> float:
    if values.empty:
        return 0.0
    equity = values.cumsum()
    drawdown = equity.cummax() - equity
    return float(drawdown.max()) if not drawdown.empty else 0.0


def operational_metrics(trades: pd.DataFrame, round_trip_cost_pips: float = 2.0) -> OperationalMetrics:
    if trades.empty:
        return OperationalMetrics(
            n_trades=0,
            first_close=None,
            last_close=None,
            positive_month_ratio=0.0,
            max_no_trade_gap_days=math.inf,
            recent_90d_drawdown=math.inf,
            historical_max_drawdown=0.0,
            recent_dd_ratio=math.inf,
            median_monthly_trades=0.0,
            total_gross_pips=0.0,
            total_cost_pips=0.0,
            total_net_pips=0.0,
            avg_net_pips_per_trade=0.0,
            cost_drag_ratio=math.inf,
            n_symbols=0,
            n_symbols_with_positive_pnl=0,
            top_symbol_pnl_share=0.0,
            top_symbol=None,
        )

    trades = trades.copy()
    trades["net_pips"] = trades["pips"].astype(float) - round_trip_cost_pips
    first_close = trades["close_dt_utc"].iloc[0]
    last_close = trades["close_dt_utc"].iloc[-1]

    monthly_net = trades.set_index("close_dt_utc")["net_pips"].resample("ME").sum()
    monthly_counts = trades.set_index("close_dt_utc")["pips"].resample("ME").count()
    positive_month_ratio = float((monthly_net > 0).mean()) if len(monthly_net) else 0.0
    median_monthly_trades = float(monthly_counts.median()) if len(monthly_counts) else 0.0

    close_gaps = trades["close_dt_utc"].diff().dropna().dt.total_seconds() / 86400.0
    max_no_trade_gap_days = float(close_gaps.max()) if not close_gaps.empty else 0.0

    historical_max_drawdown = max_drawdown(trades["net_pips"])
    recent_start = last_close - pd.Timedelta(days=90)
    recent_90d_drawdown = max_drawdown(trades.loc[trades["close_dt_utc"] >= recent_start, "net_pips"])
    if historical_max_drawdown <= 0:
        recent_dd_ratio = math.inf if recent_90d_drawdown > 0 else 0.0
    else:
        recent_dd_ratio = recent_90d_drawdown / historical_max_drawdown

    total_gross_pips = float(trades["pips"].sum())
    total_cost_pips = float(round_trip_cost_pips * len(trades))
    total_net_pips = float(trades["net_pips"].sum())
    avg_net_pips_per_trade = total_net_pips / len(trades)
    gross_positive_pips = float(trades.loc[trades["pips"] > 0, "pips"].sum())
    cost_drag_ratio = math.inf if gross_positive_pips <= 0 else total_cost_pips / gross_positive_pips

    by_symbol = trades.groupby("symbol")["net_pips"].sum().sort_values(ascending=False)
    positive_by_symbol = by_symbol[by_symbol > 0]
    n_symbols_with_positive_pnl = int(len(positive_by_symbol))
    positive_total = float(positive_by_symbol.sum())
    if positive_total > 0:
        top_symbol = str(positive_by_symbol.index[0])
        top_symbol_pnl_share = float(positive_by_symbol.iloc[0] / positive_total)
    else:
        top_symbol = str(by_symbol.index[0]) if len(by_symbol) else None
        top_symbol_pnl_share = 0.0

    return OperationalMetrics(
        n_trades=int(len(trades)),
        first_close=first_close.isoformat(),
        last_close=last_close.isoformat(),
        positive_month_ratio=positive_month_ratio,
        max_no_trade_gap_days=max_no_trade_gap_days,
        recent_90d_drawdown=recent_90d_drawdown,
        historical_max_drawdown=historical_max_drawdown,
        recent_dd_ratio=float(recent_dd_ratio),
        median_monthly_trades=median_monthly_trades,
        total_gross_pips=total_gross_pips,
        total_cost_pips=total_cost_pips,
        total_net_pips=total_net_pips,
        avg_net_pips_per_trade=avg_net_pips_per_trade,
        cost_drag_ratio=float(cost_drag_ratio),
        n_symbols=int(trades["symbol"].nunique()),
        n_symbols_with_positive_pnl=n_symbols_with_positive_pnl,
        top_symbol_pnl_share=top_symbol_pnl_share,
        top_symbol=top_symbol,
    )


def score_components(pre: dict[str, Any], metrics: OperationalMetrics) -> dict[str, float]:
    psr_p = float(pre["psr_p"])
    mcpt_p = float(pre["mcpt_p"])
    concentration_top5 = float(pre["concentration_top5"])
    frequency = metrics.median_monthly_trades
    if 20 <= frequency <= 120:
        frequency_component = 1.0
    elif 5 <= frequency < 20 or 120 < frequency <= 300:
        frequency_component = 0.5
    else:
        frequency_component = 0.0

    return {
        "psr_component": clamp01(1 - psr_p / 0.05),
        "mcpt_component": clamp01(1 - mcpt_p / 0.05),
        "concentration_component": clamp01((0.50 - concentration_top5) / 0.50),
        "stability_component": clamp01(metrics.positive_month_ratio),
        "drawdown_component": clamp01(1 - metrics.recent_dd_ratio / 1.25),
        "frequency_component": frequency_component,
        "cost_component": clamp01(1 - metrics.cost_drag_ratio / 0.50),
        "live_component": 1.0 if bool(pre.get("is_live")) else 0.5,
        "multi_asset_component": clamp01((metrics.n_symbols_with_positive_pnl - 1) / 4),
    }


def weighted_score(components: dict[str, float]) -> float:
    weights = {
        "psr_component": 0.18,
        "mcpt_component": 0.12,
        "concentration_component": 0.10,
        "stability_component": 0.15,
        "drawdown_component": 0.12,
        "frequency_component": 0.10,
        "cost_component": 0.15,
        "live_component": 0.08,
        "multi_asset_component": 0.10,
    }
    return sum(weights[key] * components[key] for key in weights)


def failed_gates(system_id: str, pre: dict[str, Any], metrics: OperationalMetrics) -> list[str]:
    failed: list[str] = []
    if system_id not in AUDIT_ONLY_SYSTEM_IDS:
        failed.append("universe_not_audit_only")
    if pre.get("decision") != "GO" or not bool(pre.get("k1_sanity_pass")):
        failed.append("k1_or_pre_screen_not_go")
    if float(pre.get("mcpt_p", math.inf)) >= 0.05:
        failed.append("mcpt_p_high")
    if float(pre.get("psr_p", math.inf)) >= 0.05:
        failed.append("psr_p_high")
    if float(pre.get("concentration_top5", math.inf)) >= 0.50:
        failed.append("concentration_top5_high")
    if metrics.positive_month_ratio < 0.60:
        failed.append("monthly_stability_low")
    if metrics.max_no_trade_gap_days > 90:
        failed.append("operational_gap_gt_90d")
    if metrics.recent_dd_ratio > 1.25:
        failed.append("recent_drawdown_gt_1_25x_historical")
    if metrics.median_monthly_trades < 5 or metrics.median_monthly_trades > 300:
        failed.append("trade_frequency_outside_5_300")
    if metrics.cost_drag_ratio >= 0.50:
        failed.append("cost_drag_ratio_gte_50pct")
    if metrics.avg_net_pips_per_trade <= 0:
        failed.append("net_expectancy_non_positive_after_2pip_cost")
    if metrics.top_symbol_pnl_share > 0.80:
        failed.append("single_asset_pnl_share_gt_80pct")
    return failed


def build_system_row(system_id: str, survivor_metrics: dict[str, Any]) -> dict[str, Any]:
    pre = load_pre_screen(system_id)
    metrics = operational_metrics(load_trades(system_id))
    components = score_components(pre, metrics)
    failed = failed_gates(system_id, pre, metrics)
    status = "PASS" if not failed else "STOP"
    copyability_score = round(weighted_score(components), 6) if status == "PASS" else None
    batch_metrics = survivor_metrics.get(system_id, {})
    return {
        "system_id": system_id,
        "copyability_status": status,
        "failed_copyability_gates": failed,
        "copyability_score": copyability_score,
        "ranking_selection_warning": RANKING_SELECTION_WARNING,
        "components": {key: round(value, 6) for key, value in components.items()},
        "pre_screen": {
            "decision": pre.get("decision"),
            "k1_sanity_pass": pre.get("k1_sanity_pass"),
            "mcpt_p": pre.get("mcpt_p"),
            "psr_p": pre.get("psr_p"),
            "concentration_top5": pre.get("concentration_top5"),
            "is_live": pre.get("is_live"),
            "notes": pre.get("notes", []),
        },
        "operational_metrics": {
            key: (round(value, 6) if isinstance(value, float) and math.isfinite(value) else value)
            for key, value in metrics.__dict__.items()
        },
        "fase1_diagnostics": {
            "adversarial_auc": batch_metrics.get("adversarial_auc"),
            "mandate_24_pass": batch_metrics.get("mandate_24_pass"),
            "mandate_24_failed": batch_metrics.get("mandate_24_failed", []),
            "fidelity_score": batch_metrics.get("fidelity_score"),
        },
    }


def markdown(scoreboard: dict[str, Any]) -> str:
    rows = sorted(
        scoreboard["systems"],
        key=lambda row: (
            1 if row["copyability_score"] is None else 0,
            0.0 if row["copyability_score"] is None else -row["copyability_score"],
            row["system_id"],
        ),
    )
    lines = [
        "# COPYABILITY_SCOREBOARD — MyFxBook v4 Fase 3b",
        "",
        "Diagnostic offline scoring only. No paper/live, no AutoTrade real, no capital allocation, and no threshold changes after ranking.",
        "",
        "## Summary",
        "",
        f"- Universe: `{scoreboard['summary']['n_systems']}` audit-only pre-screen GO systems.",
        f"- PASS: `{scoreboard['summary']['n_pass']}`.",
        f"- STOP: `{scoreboard['summary']['n_stop']}`.",
        f"- Verdict: `{scoreboard['summary']['verdict']}`.",
        "- Ranking warning: selection across systems is multiple testing / data-mining risk [advances_fin_ml, p.273-275] [evidence_based_ta, p.247-260].",
        "",
        "## Table",
        "",
        "| system_id | status | score | failed gates | pos months | med trades/mo | cost drag | net pips/trade | top symbol share | live |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        metrics = row["operational_metrics"]
        pre = row["pre_screen"]
        score = "" if row["copyability_score"] is None else f"{row['copyability_score']:.6f}"
        failed = ", ".join(row["failed_copyability_gates"]) or "-"
        lines.append(
            "| {system_id} | {status} | {score} | {failed} | {pos:.3f} | {freq:.1f} | {cost:.3f} | {avg:.3f} | {share:.3f} | {live} |".format(
                system_id=row["system_id"],
                status=row["copyability_status"],
                score=score,
                failed=failed,
                pos=metrics["positive_month_ratio"],
                freq=metrics["median_monthly_trades"],
                cost=metrics["cost_drag_ratio"],
                avg=metrics["avg_net_pips_per_trade"],
                share=metrics["top_symbol_pnl_share"],
                live=pre["is_live"],
            )
        )
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            scoreboard["summary"]["conclusion"],
            "",
            "Citations: MCPT [evidence_based_ta, p.325-328]; PSR [advances_fin_ml, p.260-263]; ranking/multiple-testing [advances_fin_ml, p.273-275]; copy cost/slippage [systematic_trading, p.182-197]; data-mining risk [evidence_based_ta, p.247-260].",
        ]
    )
    return "\n".join(lines) + "\n"


def build_scoreboard() -> dict[str, Any]:
    results_007 = read_json(RESULTS_007)
    ids_from_results = results_007["pre_screen_go_systems"]
    if ids_from_results != AUDIT_ONLY_SYSTEM_IDS:
        raise RuntimeError("007 pre_screen_go_systems does not match the FILTER_COPY_PLAN fixed universe")
    survivor_metrics = results_007.get("survivor_metrics", {})
    systems = [build_system_row(system_id, survivor_metrics) for system_id in AUDIT_ONLY_SYSTEM_IDS]
    pass_systems = [row for row in systems if row["copyability_status"] == "PASS"]
    stop_systems = [row for row in systems if row["copyability_status"] == "STOP"]
    failed_gate_counts: dict[str, int] = {}
    for row in stop_systems:
        for gate in row["failed_copyability_gates"]:
            failed_gate_counts[gate] = failed_gate_counts.get(gate, 0) + 1
    if not pass_systems:
        verdict = "STOP_ALL_FAILED_COPYABILITY_GATES"
        conclusion = (
            "All 21 audit-only systems failed at least one pre-registered copyability gate. "
            "The result is a clean diagnostic STOP; thresholds and weights were not relaxed."
        )
    elif len(pass_systems) <= 3:
        verdict = "DIAGNOSTIC_SHORTLIST_ONLY"
        conclusion = (
            f"{len(pass_systems)} systems passed the offline copyability gates. "
            "This is only a diagnostic shortlist and does not authorize paper/live, AutoTrade real, or Plano A reactivation."
        )
    else:
        verdict = "TOO_MANY_PASS_REQUIRES_REPORT_REVIEW"
        conclusion = (
            f"{len(pass_systems)} systems passed the gates, above the planned 1-3 shortlist. "
            "A report task must review concentration/multiple-testing risk without changing thresholds."
        )

    ranked = sorted(pass_systems, key=lambda row: row["copyability_score"] or 0.0, reverse=True)
    return {
        "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "contract": "FILTER_COPY_PLAN.md gates and weights, unchanged after ranking",
        "summary": {
            "n_systems": len(systems),
            "n_pass": len(pass_systems),
            "n_stop": len(stop_systems),
            "verdict": verdict,
            "conclusion": conclusion,
            "failed_gate_counts": dict(sorted(failed_gate_counts.items())),
            "top_pass_system_ids": [row["system_id"] for row in ranked[:3]],
            "ranking_selection_warning": RANKING_SELECTION_WARNING,
        },
        "systems": systems,
    }


def main() -> None:
    DIAGNOSTICS_ROOT.mkdir(parents=True, exist_ok=True)
    scoreboard = build_scoreboard()
    json_path = DIAGNOSTICS_ROOT / "COPYABILITY_SCOREBOARD.json"
    md_path = DIAGNOSTICS_ROOT / "COPYABILITY_SCOREBOARD.md"
    json_path.write_text(json.dumps(scoreboard, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown(scoreboard))
    print(json.dumps(scoreboard["summary"], indent=2, sort_keys=True))
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()
