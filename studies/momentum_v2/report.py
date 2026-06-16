"""Markdown / JSON report writers for the momentum_v2 funnel.

Every report opens with the research-only / survivorship disclaimer and marks
results ``promotion_eligible=false`` `[advances_fin_ml, p.208-211]`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from studies.momentum_v2.util import fmt_num, fmt_pct, json_safe, md_table

DISCLAIMER = (
    "Status: **research-only**, `promotion_eligible=false`. The Postgres universe "
    "plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance "
    "feed never captured most fully delisted names, so historical screens stay "
    "inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual "
    "15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.\n"
)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(payload), indent=2, allow_nan=False), encoding="utf-8")


def write_results(results: pd.DataFrame, results_dir: Path, stem: str) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(results_dir / f"{stem}.csv", index=False)
    write_json(results_dir / f"{stem}.json", results.to_dict(orient="records"))


def _plot_links(plot_paths: list[str]) -> str:
    return "\n".join(f"- [{Path(p).name}](../{p})" for p in plot_paths if p) or "_No plots._"


def write_data_audit(
    path: Path, *, universe: str, start: str, audit: pd.DataFrame, diagnostics: pd.DataFrame, kept: int, total: int
) -> None:
    reasons = ""
    if not diagnostics.empty and "reason" in diagnostics.columns:
        counts = diagnostics.loc[~diagnostics["pass_filter"], "reason"].value_counts().head(12)
        reasons = md_table(
            [{"reason": idx, "n": int(val)} for idx, val in counts.items()], ["reason", "n"]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Data Audit — `{universe}`\n\n"
        + DISCLAIMER
        + "\n## Database coverage\n\n"
        + md_table(audit.to_dict(orient="records"), list(audit.columns))
        + "\n## Filter attrition\n\n"
        f"- Start: `{start}`\n"
        f"- Tickers loaded: `{total}` -> passed filters: `{kept}` "
        f"({100.0 * kept / max(total, 1):.1f}%).\n"
        "- Expanding-universe caveat: filters (min history) plus sparse early coverage "
        "mean the tradable set in early years is much smaller than today; cross-era "
        "CAGR comparisons are affected.\n\n"
        "### Top rejection reasons\n\n"
        + (reasons or "_No rejections recorded._\n"),
        encoding="utf-8",
    )


def _broad_table(frame: pd.DataFrame) -> str:
    rows = [
        {
            "Name": r["name"],
            "Mechanism": r["mechanism"],
            "LB": r["lookback_label"],
            "Top-N": int(r["top_n"]),
            "Reb": int(r["rebalance_months"]),
            "CAGR": fmt_pct(float(r["after_tax_cagr"])),
            "MDD": fmt_pct(float(r["after_tax_mdd"])),
            "Sharpe": fmt_num(float(r["after_tax_sharpe"])),
            "RollRel": fmt_pct(float(r["rolling_rel_score"])),
            "GFC MDD": fmt_pct(float(r["gfc_mdd"])),
            "Turnover": fmt_num(float(r["annual_turnover"])),
        }
        for _, r in frame.iterrows()
    ]
    return md_table(
        rows, ["Name", "Mechanism", "LB", "Top-N", "Reb", "CAGR", "MDD", "Sharpe", "RollRel", "GFC MDD", "Turnover"]
    )


def write_broad_report(
    path: Path, *, universe: str, start: str, results: pd.DataFrame, pbo_rows: list[dict[str, Any]], plot_paths: list[str]
) -> None:
    overall = next((row for row in pbo_rows if row["group"] == "all"), {})
    best_roll = results.nlargest(1, "rolling_rel_score").iloc[0]
    best_sharpe = results.nlargest(1, "after_tax_sharpe").iloc[0]
    best_calmar = results.nlargest(1, "after_tax_calmar").iloc[0]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Broad Momentum Screen — `{universe}`\n\n"
        + DISCLAIMER
        + "\nThe broad phase is a **diagnostic map**, not a promotion claim. Honest gates "
        "run only on the small validate-phase finalist set.\n\n"
        "## Scope\n\n"
        f"- Start: `{start}`\n"
        f"- Configs: `{len(results)}`\n"
        f"- Sampled PBO (all): `{float(overall.get('pbo', float('nan'))):.3f}` "
        f"over `{overall.get('n_configs', 0)}`/`{overall.get('n_configs_total', 0)}` configs.\n\n"
        "## Key readings\n\n"
        f"- Best rolling dominance: `{best_roll['name']}` — score "
        f"`{fmt_pct(float(best_roll['rolling_rel_score']))}`, CAGR "
        f"`{fmt_pct(float(best_roll['after_tax_cagr']))}`, MDD `{fmt_pct(float(best_roll['after_tax_mdd']))}`.\n"
        f"- Best after-tax Sharpe: `{best_sharpe['name']}` — CAGR "
        f"`{fmt_pct(float(best_sharpe['after_tax_cagr']))}`, Sharpe "
        f"`{fmt_num(float(best_sharpe['after_tax_sharpe']))}`, MDD `{fmt_pct(float(best_sharpe['after_tax_mdd']))}`.\n"
        f"- Best after-tax Calmar: `{best_calmar['name']}` — Calmar "
        f"`{fmt_num(float(best_calmar['after_tax_calmar']))}`, CAGR "
        f"`{fmt_pct(float(best_calmar['after_tax_cagr']))}`, MDD `{fmt_pct(float(best_calmar['after_tax_mdd']))}`.\n\n"
        "## Plots\n\n" + _plot_links(plot_paths) + "\n\n"
        "## Top 20 by rolling dominance\n\n" + _broad_table(results.nlargest(20, "rolling_rel_score"))
        + "\n## Top 20 by after-tax Sharpe\n\n" + _broad_table(results.nlargest(20, "after_tax_sharpe"))
        + "\n## PBO summary\n\n"
        + md_table(pbo_rows, ["group", "pbo", "n_configs", "n_configs_total", "sampled", "pass"]),
        encoding="utf-8",
    )


def _evo_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {
            "Name": r["name"],
            "Overlay": r.get("overlay", "none"),
            "Offsets": r.get("offset_mode", "fixed"),
            "CAGR": fmt_pct(float(r["after_tax_cagr"])),
            "MDD": fmt_pct(float(r["after_tax_mdd"])),
            "Sharpe": fmt_num(float(r["after_tax_sharpe"])),
            "Calmar": fmt_num(float(r["after_tax_calmar"])),
            "RollRel": fmt_pct(float(r["rolling_rel_score"])),
            "GFC MDD": fmt_pct(float(r["gfc_mdd"])),
        }
        for _, r in frame.iterrows()
    ]


def write_evolution_report(
    path: Path, *, universe: str, start: str, results: pd.DataFrame, pbo_rows: list[dict[str, Any]], plot_paths: list[str]
) -> None:
    cols = ["Name", "Overlay", "Offsets", "CAGR", "MDD", "Sharpe", "Calmar", "RollRel", "GFC MDD"]
    best_sharpe = results.nlargest(1, "after_tax_sharpe").iloc[0]
    best_calmar = results.nlargest(1, "after_tax_calmar").iloc[0]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Finalist Evolution — `{universe}`\n\n"
        + DISCLAIMER
        + "\nFinalists are selected by after-tax Sharpe and Calmar (return/risk-adjusted "
        "lens). Evolutions add MA overlays (SPY SMA200 monthly/daily, stock SMA100, combos) "
        "and fixed/staggered offsets; these are literature-grounded stress diagnostics tested "
        "after the broad map, so the effective trial count exceeds this file "
        "`[advances_fin_ml, p.273-275]`.\n\n"
        "## Scope\n\n"
        f"- Start: `{start}`\n- Rows: `{len(results)}`\n\n"
        "## Key readings\n\n"
        f"- Best after-tax Sharpe: `{best_sharpe['name']}` — Sharpe "
        f"`{fmt_num(float(best_sharpe['after_tax_sharpe']))}`, CAGR "
        f"`{fmt_pct(float(best_sharpe['after_tax_cagr']))}`, MDD "
        f"`{fmt_pct(float(best_sharpe['after_tax_mdd']))}`, overlay `{best_sharpe.get('overlay', 'none')}`.\n"
        f"- Best after-tax Calmar: `{best_calmar['name']}` — Calmar "
        f"`{fmt_num(float(best_calmar['after_tax_calmar']))}`, CAGR "
        f"`{fmt_pct(float(best_calmar['after_tax_cagr']))}`, MDD "
        f"`{fmt_pct(float(best_calmar['after_tax_mdd']))}`, overlay `{best_calmar.get('overlay', 'none')}`.\n\n"
        "## Plots\n\n" + _plot_links(plot_paths) + "\n\n"
        "## Top 25 by after-tax Sharpe\n\n"
        + md_table(_evo_rows(results.nlargest(25, "after_tax_sharpe")), cols)
        + "\n## Top 25 by after-tax Calmar\n\n"
        + md_table(_evo_rows(results.nlargest(25, "after_tax_calmar")), cols)
        + "\n## PBO summary\n\n"
        + md_table(pbo_rows, ["group", "pbo", "n_configs", "n_configs_total", "sampled", "pass"]),
        encoding="utf-8",
    )


def write_validate_report(path: Path, *, universe: str, start: str, verdict: dict[str, Any]) -> None:
    per = verdict.get("per_config", [])
    rows = [
        {
            "Name": v["name"],
            "DSR p": fmt_num(float(v.get("dsr_p_value", float("nan"))), 4),
            "DSR": "pass" if v.get("dsr_pass") else "FAIL",
            "WF": f"{v.get('wf_profitable', 0)}/{v.get('wf_windows', 0)} {v.get('wf_verdict', '')}",
            "Boot CI low": fmt_num(float(v.get("bootstrap_ci_low_sharpe", float("nan")))),
            "xlib Δpp": fmt_num(float(v.get("xlib_cagr_delta_pp", float("nan")))),
            "All gates": "PASS" if v.get("all_pass") else "FAIL",
        }
        for v in per
    ]
    pbo = verdict.get("pbo", {})
    overall = "PASS" if verdict.get("overall_pass") else "FAIL"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Validate Gates — `{universe}`\n\n"
        + DISCLAIMER
        + "\nHard gates (zero bypass) `[advances_fin_ml, p.208-211, p.273-275]`: PBO<0.5, "
        "DSR p<0.05, WF>=6/8 profitable windows, bootstrap CI-low Sharpe>0, cross-library CAGR "
        "within +/-3pp. MDD is a warning-only tier (mandate §5), so it does **not** block the WF "
        "gate here. A FAIL is still the honest, expected outcome for survivorship-biased screens.\n\n"
        "## Verdict\n\n"
        f"- Honest trial count: `{verdict.get('n_trials', 0)}`\n"
        f"- Set PBO: `{float(pbo.get('pbo', float('nan'))):.3f}` "
        f"(pass={verdict.get('pbo_pass')})\n"
        f"- **Overall: {overall}**\n\n"
        "## Per-config gates\n\n"
        + md_table(rows, ["Name", "DSR p", "DSR", "WF", "Boot CI low", "xlib Δpp", "All gates"]),
        encoding="utf-8",
    )
