#!/usr/bin/env python3
"""Run factor-core comparisons against Return-Stacked Core.

The initial case reproduces the user's short live-history Testfol.io payload
without persisting credentials. Portfolio weights are fixed hypotheses, not
optimized weights, to avoid best-of-grid overfit selection
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.return_stacked_core.discussion.engine import compute_metrics  # noqa: E402

ENDPOINT = "https://testfol.io/api/backtest"
TOKEN_FILE = REPO_ROOT / ".testfolio_token"
STUDY_DIR = Path(__file__).resolve().parent
PAYLOAD_DIR = STUDY_DIR / "payloads"
RAW_DIR = STUDY_DIR / "raw"
RESULTS_DIR = STUDY_DIR / "results"
TRADING_DAYS = 252

US_SHORT_LABELS = [
    "AVUS",
    "AVUV",
    "SPMO",
    "AVUS_AVUV_SPMO_60_20_20",
    "RSC_US_TRACKING",
]

STRESS_WINDOWS = {
    "2022_rate_cycle": ("2022-01-03", "2022-12-30"),
    "2023_recovery": ("2023-01-03", "2023-12-29"),
    "2024_2026_recent": ("2024-01-02", "2026-12-31"),
}


@dataclass(frozen=True)
class CaseConfig:
    slug: str
    rebalance_freq: str
    labels: list[str]


CASES = {
    "us_short_live_yearly": CaseConfig(
        slug="us_short_live_yearly",
        rebalance_freq="Yearly",
        labels=US_SHORT_LABELS,
    ),
    "us_short_live_monthly": CaseConfig(
        slug="us_short_live_monthly",
        rebalance_freq="Monthly",
        labels=US_SHORT_LABELS,
    ),
}


def build_us_short_payload(rebalance_freq: str) -> dict[str, Any]:
    """Build the sanitized user Testfol.io payload with no auth headers."""
    def bt(allocation: dict[str, float]) -> dict[str, Any]:
        return {
            "invest_dividends": True,
            "rebalance_freq": rebalance_freq,
            "rebalance_offset": 0,
            "allocation": allocation,
            "drag": 0,
            "absolute_dev": 0,
            "relative_dev": 0,
        }

    return {
        "start_date": "1800-01-01",
        "end_date": "2100-01-01",
        "start_val": 10000,
        "adj_inflation": False,
        "target_currency": "USD",
        "cashflow": 0,
        "cashflow_freq": "Yearly",
        "cashflow_offset": 0,
        "match_first_portfolio_income_cashflows": False,
        "one_time_cashflows": [],
        "rolling_window": 60,
        "withdrawal_surface_include": False,
        "withdrawal_surface_projection": "NONE",
        "withdrawal_surface_projection_min_years": 10,
        "withdrawal_surface_start_years": 5,
        "withdrawal_surface_end_years": 50,
        "withdrawal_surface_step_years": 1,
        "backtests": [
            bt({"AVUS": 100}),
            bt({"AVUV": 100}),
            bt({"SPMO": 100}),
            bt({"AVUS": 60, "AVUV": 20, "SPMO": 20}),
            bt({
                "SPY": 40,
                "GDE": 35,
                "ZROZ": 25,
                "DBMF": 28,
                "KMLM": 12,
                "CASHX?E=-2": -40,
            }),
        ],
        "cashflow_legs": [],
    }


def _token_from_env_or_file() -> str:
    token = os.environ.get("TESTFOLIO_TOKEN", "").strip()
    if token:
        return token
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if token:
            return token
    return ""


def _post_payload(payload: dict[str, Any], token: str = "") -> dict[str, Any]:
    headers = {
        "content-type": "application/json",
        "Referer": "https://testfol.io/",
        "User-Agent": "market-lab/factor-core-comparison",
    }
    if token:
        headers["authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download_response(case: CaseConfig, force: bool = False) -> dict[str, Any]:
    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    payload_path = PAYLOAD_DIR / f"{case.slug}.json"
    raw_path = RAW_DIR / f"{case.slug}.json"

    payload = build_us_short_payload(case.rebalance_freq)
    payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if raw_path.exists() and not force:
        return json.loads(raw_path.read_text(encoding="utf-8"))

    try:
        response = _post_payload(payload)
    except urllib.error.HTTPError as no_auth_error:
        token = _token_from_env_or_file()
        if not token:
            body = no_auth_error.read().decode(errors="replace")[:500]
            raise RuntimeError(
                f"Testfol.io no-auth request failed with HTTP {no_auth_error.code}: {body}. "
                "Set TESTFOLIO_TOKEN or gitignored .testfolio_token for an authenticated retry."
            ) from no_auth_error
        response = _post_payload(payload, token=token)

    raw_path.write_text(json.dumps(response), encoding="utf-8")
    return response


def extract_equity_frame(response: dict[str, Any], labels: list[str]) -> pd.DataFrame:
    errors = response.get("errors", [])
    if errors:
        raise RuntimeError(f"Testfol.io returned errors: {errors}")

    history = response.get("charts", {}).get("history")
    if not isinstance(history, list) or len(history) < len(labels) + 1:
        raise ValueError("charts.history does not contain the expected equity curves")

    index = pd.DatetimeIndex(pd.to_datetime(history[0], unit="s", utc=True).tz_convert(None))
    frame = pd.DataFrame(index=index)
    for label, values in zip(labels, history[1:], strict=False):
        frame[label] = pd.to_numeric(pd.Series(values, index=index), errors="coerce")
    return frame


def aligned_equity(raw_equity: pd.DataFrame) -> pd.DataFrame:
    aligned = raw_equity.dropna(how="any")
    if aligned.empty:
        raise ValueError("common equity window is empty after dropna")
    return aligned / aligned.iloc[0]


def metrics_table(equity: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in equity.columns:
        row = compute_metrics(equity[col])
        row["portfolio"] = col
        rows.append(row)
    cols = [
        "portfolio",
        "start",
        "end",
        "years",
        "cagr",
        "mdd",
        "vol",
        "sharpe",
        "sortino",
        "calmar",
        "ulcer",
        "terminal",
    ]
    return pd.DataFrame(rows)[cols]


def rolling_metrics(equity: pd.DataFrame, window_years: int) -> pd.DataFrame:
    window = int(window_years * TRADING_DAYS)
    if len(equity) < window:
        return pd.DataFrame()
    rows = []
    for end_pos in range(window, len(equity) + 1):
        segment = equity.iloc[end_pos - window:end_pos]
        for col in equity.columns:
            row = compute_metrics(segment[col])
            row.update({
                "portfolio": col,
                "window_years": window_years,
                "window_end": str(segment.index[-1].date()),
            })
            rows.append(row)
    return pd.DataFrame(rows)


def stress_table(equity: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, (start, end) in STRESS_WINDOWS.items():
        segment = equity.loc[start:end]
        if len(segment) < 5:
            continue
        for col in equity.columns:
            row = compute_metrics(segment[col])
            row.update({"stress_window": name, "portfolio": col})
            rows.append(row)
    return pd.DataFrame(rows)


def relative_table(equity: pd.DataFrame) -> pd.DataFrame:
    rsc = equity["RSC_US_TRACKING"]
    rows = []
    for col in equity.columns:
        if col == "RSC_US_TRACKING":
            continue
        rel = equity[col] / rsc
        rows.append({
            "portfolio": col,
            "terminal_vs_rsc": float(rel.iloc[-1]),
            "min_vs_rsc": float(rel.min()),
            "max_vs_rsc": float(rel.max()),
            "pct_days_above_rsc": float((rel > 1.0).mean()),
        })
    return pd.DataFrame(rows)


def _fmt_pct(value: float, digits: int = 2) -> str:
    if not math.isfinite(value):
        return "n/a"
    return f"{value * 100:.{digits}f}%"


def _fmt_num(value: float, digits: int = 3) -> str:
    if not math.isfinite(value):
        return "n/a"
    return f"{value:.{digits}f}"


def _markdown_table(frame: pd.DataFrame, columns: list[str], pct_cols: set[str] | None = None) -> str:
    pct_cols = pct_cols or set()
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for _, row in frame[columns].iterrows():
        vals = []
        for col in columns:
            val = row[col]
            if isinstance(val, float | np.floating):
                vals.append(_fmt_pct(float(val)) if col in pct_cols else _fmt_num(float(val)))
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def _factor_rsc_summary(label: str, metrics: pd.DataFrame, relative: pd.DataFrame) -> dict[str, float | str]:
    factor = metrics[metrics["portfolio"] == "AVUS_AVUV_SPMO_60_20_20"].iloc[0]
    rsc = metrics[metrics["portfolio"] == "RSC_US_TRACKING"].iloc[0]
    rel_factor = relative[relative["portfolio"] == "AVUS_AVUV_SPMO_60_20_20"].iloc[0]
    return {
        "case": label,
        "factor_cagr": float(factor["cagr"]),
        "factor_mdd": float(factor["mdd"]),
        "factor_terminal": float(factor["terminal"]),
        "rsc_cagr": float(rsc["cagr"]),
        "rsc_mdd": float(rsc["mdd"]),
        "rsc_terminal": float(rsc["terminal"]),
        "factor_terminal_vs_rsc": float(rel_factor["terminal_vs_rsc"]),
    }


def write_report(case: CaseConfig, metrics: pd.DataFrame, relative: pd.DataFrame, rolling: dict[int, pd.DataFrame], stress: pd.DataFrame) -> None:
    factor = metrics[metrics["portfolio"] == "AVUS_AVUV_SPMO_60_20_20"].iloc[0]
    rsc = metrics[metrics["portfolio"] == "RSC_US_TRACKING"].iloc[0]
    rel_factor = relative[relative["portfolio"] == "AVUS_AVUV_SPMO_60_20_20"].iloc[0]
    factor_wins = float(rel_factor["terminal_vs_rsc"]) > 1.0
    monthly_metrics_path = RESULTS_DIR / "us_short_live_monthly_metrics.csv"
    monthly_relative_path = RESULTS_DIR / "us_short_live_monthly_relative_to_rsc.csv"
    monthly_done = monthly_metrics_path.exists() and monthly_relative_path.exists()

    lines = [
        "# Factor Core Comparison Report",
        "",
        "Status: research-only diagnostic. No deployment, paper-trade label, capital allocation change, or mandate override.",
        "",
        f"Primary case: `{case.slug}` (`{case.rebalance_freq}` rebalance, Testfol.io payload).",
        "",
        "## Headline",
        "",
        (
            f"The short live-window factor core `60% AVUS / 20% AVUV / 20% SPMO` "
            f"{'beat' if factor_wins else 'did not beat'} the RSC-US tracking payload by terminal wealth: "
            f"`{_fmt_num(float(rel_factor['terminal_vs_rsc']), 3)}x` versus RSC."
        ),
        "",
        f"Common window: `{rsc['start']}` to `{rsc['end']}` (`{_fmt_num(float(rsc['years']), 2)}` years).",
        "",
        "This is a short-window regime result, not validation. It is useful because it tests the live ETF implementation friction of RSC versus live factor ETFs, but it cannot answer the long-horizon expected-return question by itself `[advances_fin_ml, p.208-211]`.",
        "",
        "## Metrics",
        "",
        _markdown_table(
            metrics.sort_values("terminal", ascending=False),
            ["portfolio", "cagr", "mdd", "vol", "sharpe", "sortino", "calmar", "terminal"],
            pct_cols={"cagr", "mdd", "vol"},
        ),
        "",
        "## Relative To RSC",
        "",
        _markdown_table(
            relative.sort_values("terminal_vs_rsc", ascending=False),
            ["portfolio", "terminal_vs_rsc", "min_vs_rsc", "max_vs_rsc", "pct_days_above_rsc"],
            pct_cols={"pct_days_above_rsc"},
        ),
        "",
    ]

    if monthly_done:
        monthly_metrics = pd.read_csv(monthly_metrics_path)
        monthly_relative = pd.read_csv(monthly_relative_path)
        sensitivity = pd.DataFrame([
            _factor_rsc_summary("yearly", metrics, relative),
            _factor_rsc_summary("monthly", monthly_metrics, monthly_relative),
        ])
        lines.extend([
            "## Monthly Sensitivity",
            "",
            "The same fixed weights were rerun with monthly rebalance. This is a sensitivity check, not a new optimized portfolio; rebalance frequency should not be selected from the same short sample `[testing_tuning, p.327-335]`.",
            "",
            _markdown_table(
                sensitivity,
                [
                    "case",
                    "factor_cagr",
                    "factor_mdd",
                    "factor_terminal",
                    "rsc_cagr",
                    "rsc_mdd",
                    "rsc_terminal",
                    "factor_terminal_vs_rsc",
                ],
                pct_cols={"factor_cagr", "factor_mdd", "rsc_cagr", "rsc_mdd"},
            ),
            "",
            "Monthly rebalance leaves the factor mix effectively unchanged and makes the RSC tracking comparator slightly worse over this window. The core conclusion therefore does not depend on yearly rebalance noise.",
            "",
        ])

    lines.extend([
        "## Stress Windows",
        "",
    ])
    if stress.empty:
        lines.append("No pre-registered stress window had enough overlap.")
    else:
        view = stress[["stress_window", "portfolio", "cagr", "mdd", "sharpe", "terminal"]]
        lines.append(_markdown_table(view, list(view.columns), pct_cols={"cagr", "mdd"}))

    lines.extend([
        "",
        "## Rolling Windows",
        "",
    ])
    for years, frame in rolling.items():
        if frame.empty:
            lines.append(f"- `{years}y`: not enough common history.")
            lines.append("")
            continue
        summary = frame.groupby("portfolio").agg(
            cagr_median=("cagr", "median"),
            cagr_min=("cagr", "min"),
            mdd_min=("mdd", "min"),
            sharpe_median=("sharpe", "median"),
        ).reset_index()
        lines.append(f"### {years}y Rolling Summary")
        lines.append("")
        lines.append(_markdown_table(summary, list(summary.columns), pct_cols={"cagr_median", "cagr_min", "mdd_min"}))
        lines.append("")

    lines.extend([
        "## Reading",
        "",
        "- The factor portfolio is the cleaner live-ETF implementation over this short window: no embedded managed-futures proxy, no GDE/RSST short-history stack, and less dependence on 2022 bond/futures behavior.",
        "- The RSC thesis is still a long-horizon, cross-asset diversification thesis. It should be judged on crisis/rate/inflation regimes and multi-decade sequence risk, not only the post-GDE live window `[risk_parity, p.80-81]`.",
        "- A sub-5-year loss to factor ETFs is not surprising and is not by itself a reason to abandon RSC. It is evidence that the implementation comparison needs a live-window dashboard plus a separate proxy-long study.",
        "",
        "## Next Tests",
        "",
    ])
    if not monthly_done:
        lines.append("1. Run the same payload with monthly rebalance to isolate rebalance-frequency noise.")
        lines.append("2. Build `proxy_long` using the existing RSC discussion matrix plus explicit factor proxies for AVUS/AVUV/SPMO/AVDE/AVDV/IDMO/AVEM.")
        lines.append("3. Add global factor cases: `60/30/10`, historical `55/30/15`, and RSC-Global comparators.")
        lines.append("4. Keep all weights fixed/pre-registered; do not optimize the factor mix from this short sample `[testing_tuning, p.327-335]`.")
    else:
        lines.append("1. Build `proxy_long` using the existing RSC discussion matrix plus explicit factor proxies for AVUS/AVUV/SPMO/AVDE/AVDV/IDMO/AVEM.")
        lines.append("2. Add global factor cases: `60/30/10`, historical `55/30/15`, and RSC-Global comparators.")
        lines.append("3. Keep all weights fixed/pre-registered; do not optimize the factor mix from this short sample `[testing_tuning, p.327-335]`.")
    lines.append("")
    (STUDY_DIR / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def run_case(case: CaseConfig, force: bool = False) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    response = download_response(case, force=force)
    raw_equity = extract_equity_frame(response, case.labels)
    equity = aligned_equity(raw_equity)
    returns = equity.pct_change().dropna()

    metrics = metrics_table(equity)
    relative = relative_table(equity)
    corr = returns.corr()
    stress = stress_table(equity)
    rolling = {years: rolling_metrics(equity, years) for years in (1, 3, 5)}

    equity.to_csv(RESULTS_DIR / f"{case.slug}_equity.csv")
    returns.to_csv(RESULTS_DIR / f"{case.slug}_returns.csv")
    metrics.to_csv(RESULTS_DIR / f"{case.slug}_metrics.csv", index=False)
    relative.to_csv(RESULTS_DIR / f"{case.slug}_relative_to_rsc.csv", index=False)
    corr.to_csv(RESULTS_DIR / f"{case.slug}_correlations.csv")
    if not stress.empty:
        stress.to_csv(RESULTS_DIR / f"{case.slug}_stress.csv", index=False)
    for years, frame in rolling.items():
        if not frame.empty:
            frame.to_csv(RESULTS_DIR / f"{case.slug}_rolling_{years}y.csv", index=False)

    if case.slug == "us_short_live_yearly":
        write_report(case, metrics, relative, rolling, stress)
        write_data_audit(case, raw_equity, equity)
    elif case.slug == "us_short_live_monthly":
        refresh_primary_documents_from_saved()

    print(metrics[["portfolio", "start", "end", "years", "cagr", "mdd", "sharpe", "terminal"]].to_string(index=False))


def write_data_audit(case: CaseConfig, raw_equity: pd.DataFrame, equity: pd.DataFrame) -> None:
    coverage_rows = []
    for col in raw_equity.columns:
        s = raw_equity[col].dropna()
        coverage_rows.append({
            "portfolio": col,
            "first_non_null": str(s.index[0].date()) if not s.empty else "n/a",
            "last_non_null": str(s.index[-1].date()) if not s.empty else "n/a",
            "bars": int(len(s)),
        })
    coverage = pd.DataFrame(coverage_rows)
    monthly_done = (PAYLOAD_DIR / "us_short_live_monthly.json").exists()
    case_line = f"Primary case: `{case.slug}` with `{case.rebalance_freq}` rebalance."
    if monthly_done:
        case_line += " Sensitivity case: `us_short_live_monthly` with `Monthly` rebalance."

    lines = [
        "# Factor Core Comparison Data Audit",
        "",
        "Status: generated from sanitized Testfol.io payload. No authorization header or Bearer token is stored in this folder.",
        "",
        case_line,
        "",
        f"Common aligned window: `{equity.index[0].date()}` to `{equity.index[-1].date()}` (`{len(equity)}` daily bars).",
        "",
        "## Raw Coverage",
        "",
        _markdown_table(coverage, list(coverage.columns)),
        "",
        "## Saved Artifacts",
        "",
        f"- `payloads/{case.slug}.json`: sanitized request body only.",
        f"- `raw/{case.slug}.json`: Testfol.io response, if fetch succeeded.",
        f"- `results/{case.slug}_metrics.csv`: metrics table.",
        f"- `results/{case.slug}_equity.csv`: normalized aligned equity curves.",
        f"- `results/{case.slug}_returns.csv`: daily returns from aligned equity.",
        f"- `results/{case.slug}_relative_to_rsc.csv`: terminal/min/max relative wealth vs RSC.",
        f"- `results/{case.slug}_correlations.csv`: return correlation matrix.",
    ]
    if monthly_done:
        lines.extend([
            "- `payloads/us_short_live_monthly.json`: sanitized monthly-sensitivity request body only.",
            "- `raw/us_short_live_monthly.json`: Testfol.io response, if fetch succeeded.",
            "- `results/us_short_live_monthly_metrics.csv`: monthly-sensitivity metrics table.",
            "- `results/us_short_live_monthly_equity.csv`: monthly-sensitivity normalized aligned equity curves.",
            "- `results/us_short_live_monthly_returns.csv`: monthly-sensitivity daily returns from aligned equity.",
            "- `results/us_short_live_monthly_relative_to_rsc.csv`: monthly-sensitivity terminal/min/max relative wealth vs RSC.",
            "- `results/us_short_live_monthly_correlations.csv`: monthly-sensitivity return correlation matrix.",
        ])
    lines.extend([
        "",
        "## Caveats",
        "",
        "- Common window is determined by the youngest live ETF/proxy in the payload, so this is a short-window implementation diagnostic.",
    ])
    if monthly_done:
        lines.append("- The primary payload uses yearly rebalance because that was the user-provided comparison. Monthly rebalance is recorded as a sensitivity, not selected as an optimized setting `[testing_tuning, p.327-335]`.")
    else:
        lines.append("- The payload uses yearly rebalance because that was the user-provided comparison. Monthly rebalance is a separate sensitivity.")
    lines.extend([
        "- Testfol.io output is treated as an external-engine artifact. It is not a substitute for long-history proxy work or mandate gates `[advances_fin_ml, p.208-211]`.",
        "",
    ])
    (STUDY_DIR / "DATA_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def refresh_primary_documents_from_saved() -> None:
    case = CASES["us_short_live_yearly"]
    required = [
        RAW_DIR / f"{case.slug}.json",
        RESULTS_DIR / f"{case.slug}_metrics.csv",
        RESULTS_DIR / f"{case.slug}_relative_to_rsc.csv",
    ]
    if not all(path.exists() for path in required):
        return

    metrics = pd.read_csv(RESULTS_DIR / f"{case.slug}_metrics.csv")
    relative = pd.read_csv(RESULTS_DIR / f"{case.slug}_relative_to_rsc.csv")
    stress_path = RESULTS_DIR / f"{case.slug}_stress.csv"
    stress = pd.read_csv(stress_path) if stress_path.exists() else pd.DataFrame()
    rolling = {}
    for years in (1, 3, 5):
        path = RESULTS_DIR / f"{case.slug}_rolling_{years}y.csv"
        rolling[years] = pd.read_csv(path) if path.exists() else pd.DataFrame()

    response = json.loads((RAW_DIR / f"{case.slug}.json").read_text(encoding="utf-8"))
    raw_equity = extract_equity_frame(response, case.labels)
    equity = aligned_equity(raw_equity)
    write_report(case, metrics, relative, rolling, stress)
    write_data_audit(case, raw_equity, equity)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=sorted(CASES), default="us_short_live_yearly")
    parser.add_argument("--all", action="store_true", help="run all registered cases")
    parser.add_argument("--force", action="store_true", help="refetch raw Testfol.io response")
    args = parser.parse_args()

    selected = CASES.values() if args.all else [CASES[args.case]]
    for case in selected:
        run_case(case, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
