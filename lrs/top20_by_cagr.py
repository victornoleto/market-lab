from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lrs.lib.backtest import fmt_num, fmt_pct, fmt_x, md_table  # noqa: E402


RESULTS = ROOT / "results"
OUT_CSV = RESULTS / "top20_by_cagr.csv"
OUT_REPORT = ROOT / "TOP20_BY_CAGR.md"
EXCLUDE = {"phase03c_theory_anchor.csv"}


def _candidate_label(source: str, row: pd.Series) -> str:
    if "candidate_id" in row:
        return str(row["candidate_id"])
    branch = str(row.get("branch", ""))
    parts = [branch]
    if pd.notna(row.get("target_leverage", pd.NA)):
        parts.append(f"L{float(row['target_leverage']):.2f}")
    elif pd.notna(row.get("risk_on", pd.NA)):
        parts.append(str(row["risk_on"]))
    risk_off = row.get("risk_off_name", row.get("risk_off", ""))
    if pd.notna(risk_off) and str(risk_off):
        parts.append(f"off {risk_off}")
    vol_filter = row.get("vol_filter", "")
    if pd.notna(vol_filter) and str(vol_filter):
        parts.append(str(vol_filter))
    lag = row.get("lag_days", "")
    if pd.notna(lag) and str(lag) != "":
        parts.append(f"lag {int(lag)}")
    for key in ("regime_form", "filter_name", "window", "base_name"):
        value = row.get(key, "")
        if pd.notna(value) and str(value):
            parts.append(f"{key}={value}")
    return " | ".join(parts)


def collect_candidates() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for path in sorted(RESULTS.glob("*.csv")):
        if path.name in EXCLUDE or path.name == OUT_CSV.name:
            continue
        frame = pd.read_csv(path)
        if "taxed_cagr" in frame.columns:
            cagr_col = "taxed_cagr"
            mdd_col = "taxed_mdd"
            sharpe_col = "taxed_sharpe"
            calmar_col = "taxed_calmar"
            terminal_col = "taxed_terminal"
            metric_basis = "after_tax"
        elif "cagr" in frame.columns:
            cagr_col = "cagr"
            mdd_col = "mdd"
            sharpe_col = "sharpe"
            calmar_col = "calmar"
            terminal_col = "terminal"
            metric_basis = "as_reported"
        else:
            continue
        for i, row in frame.iterrows():
            rows.append(
                {
                    "rank_basis": "cagr_desc_no_drawdown_filter",
                    "source_file": str(path.relative_to(REPO_ROOT)),
                    "source_row": int(i),
                    "phase": path.stem,
                    "candidate_id": row.get("candidate_id", f"{path.stem}_{i:05d}"),
                    "candidate_type": row.get("candidate_type", "lrs_candidate"),
                    "branch": row.get("branch", ""),
                    "label": row.get("component_label", "") or _candidate_label(path.stem, row),
                    "metric_basis": metric_basis,
                    "start": row.get("start", ""),
                    "end": row.get("end", ""),
                    "years": row.get("years", pd.NA),
                    "cagr": row[cagr_col],
                    "mdd": row.get(mdd_col, pd.NA),
                    "sharpe": row.get(sharpe_col, pd.NA),
                    "calmar": row.get(calmar_col, pd.NA),
                    "terminal": row.get(terminal_col, pd.NA),
                    "turnover_per_year": row.get("turnover_per_year", row.get("estimated_total_turnover_per_year", pd.NA)),
                    "drawdown_tier": row.get("drawdown_tier", ""),
                    "strict_overlay_pass": row.get("strict_overlay_pass", ""),
                    "overall_pass": row.get("overall_pass", ""),
                    "notes": row.get("notes", ""),
                }
            )
    if not rows:
        raise ValueError("no CAGR-capable result rows found")
    return pd.DataFrame(rows).sort_values(["cagr", "calmar"], ascending=[False, False]).reset_index(drop=True)


def report_rows(frame: pd.DataFrame, limit: int = 20) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for rank, (_, row) in enumerate(frame.head(limit).iterrows(), start=1):
        rows.append(
            {
                "Rank": rank,
                "Candidate": str(row["label"]).replace("|", "/"),
                "Phase": row["phase"],
                "CAGR": fmt_pct(row["cagr"]),
                "MDD": fmt_pct(row["mdd"]),
                "Sharpe": fmt_num(row["sharpe"]),
                "Calmar": fmt_num(row["calmar"]),
                "Terminal": fmt_x(row["terminal"]),
                "Basis": row["metric_basis"],
                "Years": fmt_num(row["years"], 1),
            }
        )
    return rows


def write_outputs(frame: pd.DataFrame) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    top20 = frame.head(20).copy()
    top20.insert(0, "rank", range(1, len(top20) + 1))
    top20.to_csv(OUT_CSV, index=False)
    body = [
        "# LRS Top-20 By CAGR\n\n"
        "Status: research-only diagnostic. This ranking deliberately ignores drawdown filters so the user can inspect the highest-return rows before choosing any follow-up. It is **not** a validation result, winner label, paper-trade label or mandate change `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.\n\n"
        f"Source rows scanned: `{len(frame)}` from `lrs/results/*.csv`. Ranking metric: CAGR descending, with no MDD/Calmar/underwater gate. `after_tax` rows use `taxed_cagr`; Phase 5 rows use the phase's reported `cagr`.\n\n"
        "## Top 20\n\n"
        + md_table(report_rows(frame), ["Rank", "Candidate", "Phase", "CAGR", "MDD", "Sharpe", "Calmar", "Terminal", "Basis", "Years"])
        + "\n\n## Reading\n\n"
        "The table is intentionally return-first. Large MDD rows are not excluded; they are shown so the trade-off is explicit. Any selected follow-up still needs a fresh pre-registration, account-level frictions/tax where applicable, and the mandate gates before any promotion claim `[advances_fin_ml, p.273-275]`.\n"
    ]
    OUT_REPORT.write_text("".join(body), encoding="utf-8")


def main() -> int:
    frame = collect_candidates()
    write_outputs(frame)
    best = frame.iloc[0]
    print(f"wrote {OUT_CSV.relative_to(REPO_ROOT)} and {OUT_REPORT.relative_to(REPO_ROOT)}")
    print(f"top CAGR: {best['cagr']:.4f} {best['label']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
