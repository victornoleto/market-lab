"""Pins our engine's numbers into baseline.json — the reference the libs
are compared against.

Runs ONCE when the harness is first built. Re-run only when `letf_rotation.py`
or `portfolio_3leg_ew` computation changes. Baseline is git-committed so
verdicts are reproducible.

SCHEMA NOTE — two distinct metric encodings in phase3_5b summaries:
  * Portfolio variants (variants_letf_execution, extended_window_1986_2026):
    metrics stored as PERCENT VALUES, e.g. cagr_pct=37.92 means 37.92%,
    max_drawdown_pct=16.91 means 16.91%.  No return_ann_pct/volatility_ann_pct.
  * Leg summaries (letf_rotation_ema100_2x, qqq_donchian_20_10,
    gld_donchian_40_20, portfolio_3leg_ew): metrics stored as DECIMAL RATIOS,
    e.g. cagr_pct=0.447 means 44.7%, max_drawdown_pct=0.205 means 20.5%.
    DO have return_ann_pct and volatility_ann_pct (also decimal ratios).

All values in baseline.json are normalised to PERCENT (e.g. 37.92, not 0.3792).
max_dd is stored as a negative percent (e.g. -16.91) so the verdict engine can
do simple sign-aware comparisons.  [leverage_for_the_long_run, ch.4]
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

BASELINE_JSON = Path(
    "reports/phase_3_5c/cross_lib/reference/baseline.json"
)


def git_commit_hash() -> str:
    return (
        subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    )


# ---------------------------------------------------------------------------
# Loaders — each returns a dict that _extract_metrics_* can consume
# ---------------------------------------------------------------------------


def _load_portfolio_3leg_ew_summary_canonical() -> dict:
    """V4_SSO_QLD_UGL variant from variants_letf_execution/summary.json.

    Top-level shape: {config, spy_buy_hold_SPYSIM, variants: [list-of-8], caveats}
    Each variant: {variant: str, legs, metrics: {cagr_pct, sharpe,
                   max_drawdown_pct (percent), final_equity}, ...}
    """
    path = Path("reports/phase3_5b/variants_letf_execution/summary.json")
    doc = json.loads(path.read_text())
    for item in doc["variants"]:
        if item["variant"] == "V4_SSO_QLD_UGL":
            return item  # has "metrics" key; values are percent
    raise KeyError(
        "V4_SSO_QLD_UGL not found in variants_letf_execution/summary.json"
    )


def _load_portfolio_3leg_ew_summary_extended() -> dict:
    """Extended window from extended_window_1986_2026/summary.json.

    Top-level shape: {config, strategy: {cagr_pct, sharpe, max_drawdown_pct
                      (percent), ...}, spy_buy_hold_SPYSIM, ...}
    No 'metrics' key — strategy sub-dict is wrapped here to match the
    convention expected by _extract_metrics_pct.
    """
    path = Path("reports/phase3_5b/extended_window_1986_2026/summary.json")
    doc = json.loads(path.read_text())
    # Wrap strategy under "metrics" so _extract_metrics_pct works uniformly
    return {"metrics": doc["strategy"]}


def _load_leg_summary(leg_name: str) -> dict:
    """Load a single-leg summary (decimal-ratio metrics).

    Shape: {strategy, params, window_start, window_end, initial_capital,
            tax_rate, metrics: {cagr_pct (decimal), sharpe,
            max_drawdown_pct (decimal), return_ann_pct, volatility_ann_pct,
            ...}, spy_benchmark, ...}
    """
    mapping = {
        "leg_sso_only": "letf_rotation_ema100_2x",
        "leg_qld_only": "qqq_donchian_20_10",
        "leg_ugl_only": "gld_donchian_40_20",
    }
    path = Path(f"reports/phase3_5b/{mapping[leg_name]}/summary.json")
    return json.loads(path.read_text())


def _load_v1_fallback() -> dict:
    """Legacy portfolio_3leg_ew summary (decimal-ratio metrics)."""
    return json.loads(
        Path("reports/phase3_5b/portfolio_3leg_ew/summary.json").read_text()
    )


# ---------------------------------------------------------------------------
# Metric extractors — separate functions for the two encodings
# ---------------------------------------------------------------------------


def _extract_metrics_pct(summary: dict) -> dict:
    """Extract from a summary whose metrics are already in PERCENT units.

    Used for: V4_SSO_QLD_UGL canonical + extended_window variants.
    max_dd is stored as a positive percent (e.g. 16.91); we negate it here so
    baseline always has max_dd <= 0 (consistent sign convention for verdicts).
    volatility_ann is not available in these summaries — stored as None.
    """
    m = summary.get("metrics", summary)
    raw_dd = float(m["max_drawdown_pct"])
    return {
        "cagr": float(m["cagr_pct"]),
        "sharpe": float(m["sharpe"]),
        # Negate so a larger drawdown is more negative (verdicts use abs diff)
        "max_dd": -abs(raw_dd),
        # return_ann and volatility_ann not present in portfolio summaries;
        # fall back to cagr and None respectively
        "return_ann": float(m.get("return_ann_pct", m["cagr_pct"])),
        "volatility_ann": None,  # not available for portfolio-level summaries
    }


def _extract_metrics_decimal(summary: dict) -> dict:
    """Extract from a summary whose metrics are DECIMAL RATIOS.

    Used for: single-leg summaries (letf_rotation_ema100_2x, etc.) and the
    legacy portfolio_3leg_ew summary.  All values are multiplied by 100 to
    convert to percent before storage, maintaining the same unit as _pct above.
    max_dd: stored as negative percent (e.g. 0.205 → -20.5).
    """
    m = summary.get("metrics", summary)
    raw_dd = float(m["max_drawdown_pct"])  # decimal, e.g. 0.205
    return {
        "cagr": float(m["cagr_pct"]) * 100,
        "sharpe": float(m["sharpe"]),
        "max_dd": -abs(raw_dd) * 100,
        "return_ann": float(m.get("return_ann_pct", m["cagr_pct"])) * 100,
        "volatility_ann": float(m["volatility_ann_pct"]) * 100
        if "volatility_ann_pct" in m
        else None,
    }


# ---------------------------------------------------------------------------
# Build + persist
# ---------------------------------------------------------------------------


def build_baseline() -> dict:
    baseline: dict = {
        "generated_at": pd.Timestamp.now("UTC").isoformat(),
        "git_commit": git_commit_hash(),
        "metric_units": {
            "cagr": "percent (e.g. 37.92 means 37.92%/yr)",
            "sharpe": "ratio (dimensionless)",
            "max_dd": "percent, negative (e.g. -16.91 means 16.91% drawdown)",
            "return_ann": "percent, same scale as cagr",
            "volatility_ann": "percent or null if unavailable",
        },
        "variants": {},
    }

    canonical = _load_portfolio_3leg_ew_summary_canonical()
    extended = _load_portfolio_3leg_ew_summary_extended()

    baseline["variants"]["plano_b_v4_threshold_10"] = {
        "canonical": _extract_metrics_pct(canonical),
        "extended": _extract_metrics_pct(extended),
    }

    for leg in ("leg_sso_only", "leg_qld_only", "leg_ugl_only"):
        baseline["variants"][leg] = {
            "canonical": _extract_metrics_decimal(_load_leg_summary(leg)),
        }

    v1 = _load_v1_fallback()
    baseline["variants"]["v1_fallback"] = {
        "canonical": _extract_metrics_decimal(v1),
    }

    baseline["integrity_hash"] = _hash_baseline(baseline)
    return baseline


def _hash_baseline(baseline: dict) -> str:
    body = {k: v for k, v in baseline.items() if k != "integrity_hash"}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True).encode()
    ).hexdigest()


def save_baseline(baseline: dict, path: Path = BASELINE_JSON) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(baseline, indent=2, sort_keys=True))


if __name__ == "__main__":
    bl = build_baseline()
    save_baseline(bl)
    print(
        f"Wrote baseline to {BASELINE_JSON} "
        f"(hash={bl['integrity_hash'][:12]})"
    )
    for vid, windows in bl["variants"].items():
        for window, metrics in windows.items():
            max_dd = metrics["max_dd"]
            print(
                f"  {vid}/{window}: CAGR={metrics['cagr']:.4f}% "
                f"Sharpe={metrics['sharpe']:.3f} "
                f"MaxDD={max_dd:.2f}%"
            )
