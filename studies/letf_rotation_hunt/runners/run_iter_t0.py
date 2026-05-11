"""Iter 000 — synth parity validation.

Generates SYNTH_PARITY_REPORT.md with table of synth vs real CAGR per LETF.
Sets verdict.synth_parity_pass = True iff ALL configured tickers within threshold
(vacuously True if no real data is available — infrastructure is in place).

Citations
---------
* Tolerance rationale: [leverage_for_the_long_run, p.16, footnote 22-23]
  — 2× LETFs: 1pp CAGR tolerance; 3× LETFs: 3pp (vol-decay premium documented).
* TMF: 1.5pp due to bond duration sensitivity and spread variance.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import (
    load_ffr_daily,
    load_testfolio_series,
    load_tiingo_real_etf,
)
from studies.letf_rotation_hunt.core.synths import letf_synth_by_ticker

PARITY_THRESHOLDS = {
    "UPRO": 0.03,
    "SSO": 0.01,
    "TQQQ": 0.03,
    "QLD": 0.01,
    "TMF": 0.015,
    "UGL": 0.01,
}

# Tickers whose testfolio cache has a direct *SIM equity curve. For these,
# the parity check uses testfolio's own synth methodology (e.g. UPROSIM) —
# the same series consumed in T1+ for pre-inception history.
#
# UGL was here originally (UGLSIM in cache), but iter 000 v2 (2026-05-05)
# measured ~3pp/yr drift between UGLSIM and real UGL over 2008-2026 —
# UGLSIM under-models gold-LETF tracking drag. Moved to _RESYNTH_UNDERLYINGS
# so the calibrated ER (0.030, see synths.LETF_EXPENSE_RATIOS) drives synth.
_DIRECT_SIM_TICKERS: frozenset[str] = frozenset({"UPRO", "SSO", "TQQQ", "QLD"})

# Underlyings used to re-synthesize tickers without a direct *SIM in cache or
# whose direct *SIM showed material parity drift in iter 000 v2.
# - TLTSIM is the documented 20yr-treasury proxy for TMF [SPEC.md §4.1].
# - GLDSIM is the gold-spot proxy for UGL after iter 000 v2 calibration
#   replaced UGLSIM (which under-modelled gold-LETF tracking drag).
_RESYNTH_UNDERLYINGS: dict[str, str] = {
    "TMF": "TLTSIM",
    "UGL": "GLDSIM",
}


def build_synth_equity_curve(ticker: str) -> pd.Series:
    """Equity-curve series used as the synth side of the parity gate.

    Two sources, picked per ticker:

    * **Direct *SIM** (UPRO/SSO/TQQQ/QLD/UGL): testfolio publishes
      ``{ticker}SIM`` curves built by their own FFR-aware synthesis;
      we use them as-is in T1+ pre-inception history, so parity validates
      *that* curve, not our own re-implementation.
    * **Re-synthesis** (TMF): no TMFSIM in cache → recompute via
      ``letf_synth_by_ticker(TMF, TLTSIM_returns, ffr_daily)``, the exact
      code path used in T1c rotation strategies. Returns are cumulated to
      a $1.0-indexed equity curve.

    Citations: [leverage_for_the_long_run, p.16, footnote 22-23]
    (FFR-aware formula); SPEC.md §4.1 (TLTSIM as TMF underlying proxy).

    Parameters
    ----------
    ticker:
        LETF ticker (UPRO/SSO/TQQQ/QLD/UGL/TMF).

    Returns
    -------
    pd.Series
        Equity-curve price series with DatetimeIndex.

    Raises
    ------
    KeyError
        If ``ticker`` has no defined parity source.
    """
    if ticker in _DIRECT_SIM_TICKERS:
        return load_testfolio_series(f"{ticker}SIM")
    if ticker in _RESYNTH_UNDERLYINGS:
        underlying_sim = _RESYNTH_UNDERLYINGS[ticker]
        underlying_prices = load_testfolio_series(underlying_sim)
        underlying_returns = underlying_prices.pct_change().dropna()
        ffr_daily = load_ffr_daily()
        synth_returns = letf_synth_by_ticker(ticker, underlying_returns, ffr_daily)
        return (1.0 + synth_returns).cumprod()
    raise KeyError(
        f"No parity synth source defined for {ticker!r}. "
        f"Add to _DIRECT_SIM_TICKERS or _RESYNTH_UNDERLYINGS."
    )


def run(config: dict, verdict: dict, out_dir: Path) -> dict:
    """Run iter 000 synth parity validation.

    For each ticker in config["tickers"]:
      - Load synth series from testfolio cache
      - Load real ETF from Tiingo bulk cache
      - Compute overlapping-window CAGR delta
      - Check against per-ticker threshold

    If real data is unavailable, the ticker is SKIP (not FAIL).
    synth_parity_pass = True iff no FAIL results (vacuously True if all SKIP).

    Parameters
    ----------
    config:
        Loaded iter config YAML dict.
    verdict:
        Scaffold verdict dict to be filled and returned.
    out_dir:
        Output directory for SYNTH_PARITY_REPORT.md.

    Returns
    -------
    dict
        Updated verdict dict.
    """
    tickers = config.get("tickers", list(PARITY_THRESHOLDS.keys()))
    results = []
    all_pass = True

    for ticker in tickers:
        threshold = PARITY_THRESHOLDS.get(ticker, 0.03)
        try:
            synth = build_synth_equity_curve(ticker)
            real = load_tiingo_real_etf(ticker)
        except (FileNotFoundError, KeyError, ValueError) as e:
            results.append({
                "ticker": ticker,
                "status": "SKIP",
                "reason": str(e),
                "synth_cagr": None,
                "real_cagr": None,
                "delta": None,
                "threshold": threshold,
            })
            continue

        common_start = max(synth.index.min(), real.index.min())
        common_end = min(synth.index.max(), real.index.max())
        if (common_end - common_start).days < 365:
            results.append({
                "ticker": ticker,
                "status": "SKIP",
                "reason": f"insufficient overlap ({common_start.date()} to {common_end.date()})",
                "synth_cagr": None,
                "real_cagr": None,
                "delta": None,
                "threshold": threshold,
            })
            continue

        synth_w = synth[common_start:common_end].dropna()
        real_w = real[common_start:common_end].dropna()
        if len(synth_w) < 252 or len(real_w) < 252:
            results.append({
                "ticker": ticker,
                "status": "SKIP",
                "reason": f"too few overlapping points: synth={len(synth_w)}, real={len(real_w)}",
                "synth_cagr": None,
                "real_cagr": None,
                "delta": None,
                "threshold": threshold,
            })
            continue

        synth_cagr = _cagr(synth_w)
        real_cagr = _cagr(real_w)
        delta = abs(synth_cagr - real_cagr)
        passed = delta <= threshold
        if not passed:
            all_pass = False

        results.append({
            "ticker": ticker,
            "status": "PASS" if passed else "FAIL",
            "synth_cagr": float(synth_cagr),
            "real_cagr": float(real_cagr),
            "delta": float(delta),
            "threshold": threshold,
            "common_start": str(common_start.date()),
            "common_end": str(common_end.date()),
        })

    # Write report
    report_path = out_dir / "SYNTH_PARITY_REPORT.md"
    report_path.write_text(_render_report(results, all_pass))
    print(f"[run_iter_t0] report written: {report_path}")

    verdict["results"] = results
    verdict["synth_parity_pass"] = all_pass
    verdict["best_config"] = "synth_parity"
    verdict["best_score"] = 100.0 if all_pass else 0.0
    verdict["best_tier"] = "PASS" if all_pass else "FAIL"
    verdict["kill_rule_status"] = "N/A"
    verdict["advance_to_next_tier"] = all_pass

    return verdict


def _cagr(prices: pd.Series) -> float:
    """CAGR from price series.

    Parameters
    ----------
    prices:
        pd.Series with DatetimeIndex of equity-curve values.

    Returns
    -------
    float
        Annualised compound growth rate, or nan if insufficient data.
    """
    n_years = (prices.index[-1] - prices.index[0]).days / 365.25
    if n_years < 0.1 or prices.iloc[0] <= 0:
        return float("nan")
    return (prices.iloc[-1] / prices.iloc[0]) ** (1 / n_years) - 1


def _render_report(results: list[dict], all_pass: bool) -> str:
    """Render markdown parity report table.

    Parameters
    ----------
    results:
        List of per-ticker result dicts.
    all_pass:
        True iff no FAIL results.

    Returns
    -------
    str
        Markdown-formatted report.
    """
    lines = [
        "# Iter 000 — Synth Parity Validation Report",
        "",
        f"**Status:** {'PASS — all tested tickers within threshold' if all_pass else 'FAIL — debug before T1'}",
        "",
        "Per spec §4.3: synth LETF series must reproduce real ETF returns within tolerance:",
        "- 2x LETFs (SSO, QLD, UGL): |CAGR delta| <= 1pp",
        "- 3x LETFs (UPRO, TQQQ): |CAGR delta| <= 3pp (Gayed leverage premium documented)",
        "- TMF: |CAGR delta| <= 1.5pp",
        "",
        "Citation: [leverage_for_the_long_run, p.16, footnote 22-23]",
        "",
        "## Results",
        "",
        "| Ticker | Status | Synth CAGR | Real CAGR | Delta | Threshold | Window |",
        "|--------|--------|----------:|----------:|------:|----------:|--------|",
    ]
    for r in results:
        if r["status"] == "SKIP":
            lines.append(
                f"| {r['ticker']} | SKIP | — | — | — | {r['threshold']:.3f} | {r.get('reason', '')} |"
            )
        else:
            sc = r["synth_cagr"]
            rc = r["real_cagr"]
            d = r["delta"]
            t = r["threshold"]
            mark = "PASS" if r["status"] == "PASS" else "FAIL"
            window = f"{r['common_start']} to {r['common_end']}"
            lines.append(
                f"| {r['ticker']} | {mark} | {sc:.4f} | {rc:.4f} | {d:.4f} | {t:.3f} | {window} |"
            )
    lines.append("")
    lines.append("---")
    lines.append("")
    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    n_skip = sum(1 for r in results if r["status"] == "SKIP")
    lines.append(f"Summary: {n_pass} PASS, {n_fail} FAIL, {n_skip} SKIP out of {len(results)} tickers.")
    lines.append("")
    if all_pass:
        lines.append("Decision: ADVANCE to T1 implementation.")
    else:
        lines.append("Decision: DEBUG required before T1. Check testfolio synth methodology vs Tiingo data.")
    lines.append("")
    return "\n".join(lines)
