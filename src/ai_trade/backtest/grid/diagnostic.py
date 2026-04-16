"""DiagnosticAnalyzer — structured breakdown when the gates fail.

Produces a :class:`DiagnosticReport` whose purpose is to answer "why did
this grid fail, and what's the next rational step?" without requiring
another run. The user reads the ``recommendation`` text + ``per_config_
metrics`` DataFrame and decides: iterate on universe? pivot strategy?
migrate to paid data as ablation study?

The analyzer never recommends a fork on its own — it only classifies the
failure mode and surfaces the numbers.
"""

from __future__ import annotations

import logging
from dataclasses import MISSING, dataclass, field, fields

import numpy as np
import pandas as pd

from ai_trade.backtest.grid.gates import GateVerdict
from ai_trade.backtest.grid.result import GridResult, TrialResult
from ai_trade.backtest.grid.walk_forward import WFResult


def _varied_field_names(config) -> tuple[str, ...]:
    """Field names of a grid-config dataclass that are swept (no default).

    Convention used across ``ai_trade.backtest.grid``: grid axes are
    declared as fields WITHOUT a default (so callers have to set them),
    and fixed literature constants are declared WITH defaults. This
    helper lets the diagnostic/report layer be strategy-agnostic.
    """
    return tuple(
        f.name
        for f in fields(config)
        if f.default is MISSING and f.default_factory is MISSING
    )


_log = logging.getLogger("ai_trade.grid.diagnostic")


@dataclass
class FailureMode:
    label: str
    description: str
    severity: str            # "critical" | "moderate"


@dataclass
class DiagnosticReport:
    failure_modes: list[FailureMode]
    best_config: TrialResult
    pbo_logit_distribution: str
    per_config_metrics: pd.DataFrame
    wf_window_breakdown: dict[int, WFResult]
    recommendation: str = ""


@dataclass
class DiagnosticAnalyzer:
    pbo_threshold: float = 0.5

    def analyze(
        self,
        *,
        grid: GridResult,
        verdict: GateVerdict,
        wf_results: dict[int, WFResult],
    ) -> DiagnosticReport:
        failure_modes = self._classify_failure(verdict)
        best_config = _best_config(grid)
        per_config_df = _per_config_metrics(grid, verdict, wf_results)
        pbo_desc = _pbo_logit_description(verdict)
        recommendation = _recommendation(failure_modes, best_config, verdict)

        return DiagnosticReport(
            failure_modes=failure_modes,
            best_config=best_config,
            pbo_logit_distribution=pbo_desc,
            per_config_metrics=per_config_df,
            wf_window_breakdown=dict(wf_results),
            recommendation=recommendation,
        )

    def _classify_failure(self, verdict: GateVerdict) -> list[FailureMode]:
        modes: list[FailureMode] = []

        # Check upstream fail FIRST — other gate verdicts are misleading
        # when no trial produced an equity curve.
        # We detect this via verdict signature: pbo_result is None AND
        # dsr_results is empty AND wf_verdicts is empty (no OK trials means
        # GateEvaluator couldn't compute any of these).
        upstream_fail = (
            verdict.pbo_result is None
            and not verdict.dsr_results
            and not verdict.wf_verdicts
        )
        if upstream_fail:
            modes.append(FailureMode(
                label="GATE_UPSTREAM_FAIL",
                description=(
                    "All trials errored upstream of the backtest (e.g. the "
                    "strategy's __post_init__ validator rejected the data — "
                    "no cointegration, half-life out of range, regime "
                    "filter, etc.). No equity curve was produced for any "
                    "config, so PBO/DSR/walk-forward could not be computed. "
                    "Inspect the per-trial error_msg in the report below "
                    "and check spec §7 for the next-step decision (typically "
                    "a strategy pivot rather than parameter tuning)."
                ),
                severity="critical",
            ))
            return modes

        pbo_fail = not verdict.pbo_pass
        dsr_fail = len(verdict.dsr_pass_ids) == 0
        wf_fail = len(verdict.wf_pass_ids) == 0

        if pbo_fail:
            pbo_val = verdict.pbo_result.pbo if verdict.pbo_result else float("nan")
            modes.append(FailureMode(
                label="PBO_HIGH",
                description=(
                    f"PBO = {pbo_val:.3f} ≥ {self.pbo_threshold}. Probability of "
                    "Backtest Overfitting too high — IS-best configs lose their "
                    "rank out-of-sample. Look for a smaller grid or fundamentally "
                    "different hypothesis, not more parameters."
                ),
                severity="critical",
            ))
        if dsr_fail:
            modes.append(FailureMode(
                label="DSR_ALL_FAIL",
                description=(
                    "No config cleared DSR p-value < 0.05. After deflating for "
                    f"N={len(verdict.dsr_results)} multiple tests, the observed "
                    "Sharpes are compatible with selection bias rather than skill. "
                    "Either the edge is small or noise dominates at this sample size."
                ),
                severity="critical",
            ))
        if wf_fail:
            modes.append(FailureMode(
                label="WF_INSUFFICIENT",
                description=(
                    "No config passes the walk-forward gate (≥6/8 profitable "
                    "windows, max DD ≤ 25%). OOS generalization is broken — "
                    "drill into the per-window breakdown to identify which "
                    "regimes killed the strategy."
                ),
                severity="critical",
            ))

        if sum([pbo_fail, dsr_fail, wf_fail]) >= 2:
            modes.append(FailureMode(
                label="COMBINED",
                description=(
                    "Multiple gates failed simultaneously. The grid does not "
                    "exhibit edge in any dimension — either the hypothesis is "
                    "wrong for this universe/timeframe, or the data source "
                    "(survivorship residual, data quality) is the limiting "
                    "factor."
                ),
                severity="critical",
            ))
        return modes


def _best_config(grid: GridResult) -> TrialResult:
    """The trial with the highest cached Sharpe.

    NaN Sharpes (error trials) are excluded from ranking. When no trial
    succeeded, returns a degenerate TrialResult derived from the first
    trial — the result/sharpe/cagr/max_drawdown fields are NaN-ish and
    callers (report layer) must check ``best.result is None``.
    """
    ok = grid.ok_trials
    if ok:
        return max(
            ok, key=lambda t: t.sharpe if np.isfinite(t.sharpe) else -np.inf,
        )
    if not grid.trials:
        raise ValueError("grid has no trials at all — cannot diagnose")
    first = grid.trials[0]
    return TrialResult(
        config_id=first.config_id,
        config=first.config,
        result=None,
        sharpe=float("nan"),
        cagr=float("nan"),
        max_drawdown=float("nan"),
        status="error",
        error_msg=first.error_msg,
    )


def _per_config_metrics(
    grid: GridResult,
    verdict: GateVerdict,
    wf_results: dict[int, WFResult],
) -> pd.DataFrame:
    rows = []
    for trial in grid.trials:
        dsr_p = (
            verdict.dsr_results[trial.config_id].p_value
            if trial.config_id in verdict.dsr_results
            else float("nan")
        )
        row = {"config_id": trial.config_id}
        for name in _varied_field_names(trial.config):
            row[name] = getattr(trial.config, name)
        row.update({
            "sharpe": trial.sharpe if trial.status == "ok" else float("nan"),
            "cagr": trial.cagr if trial.status == "ok" else float("nan"),
            "max_drawdown": trial.max_drawdown if trial.status == "ok" else float("nan"),
            "dsr_pvalue": dsr_p,
            "dsr_pass": trial.config_id in verdict.dsr_pass_ids,
            "wf_verdict": wf_results.get(
                trial.config_id,
                None,
            ).verdict if trial.config_id in wf_results else "n/a",
            "status": trial.status,
        })
        rows.append(row)
    return pd.DataFrame(rows)


def _pbo_logit_description(verdict: GateVerdict) -> str:
    if verdict.pbo_result is None:
        return "PBO not computed (matrix too small)."
    logits = verdict.pbo_result.logits
    return (
        f"PBO logits over {len(logits)} splits: "
        f"mean={np.mean(logits):.3f}, std={np.std(logits):.3f}, "
        f"min={np.min(logits):.3f}, max={np.max(logits):.3f}. "
        f"PBO = {verdict.pbo_result.pbo:.3f}."
    )


def _recommendation(
    failure_modes: list[FailureMode],
    best_config: TrialResult,
    verdict: GateVerdict,
) -> str:
    if not failure_modes:
        return "All gates passed. No diagnostic necessary."
    labels = {mode.label for mode in failure_modes}

    # Special case: all trials errored upstream — best_config is degenerate.
    if "GATE_UPSTREAM_FAIL" in labels:
        err = best_config.error_msg or "(no error_msg captured)"
        return (
            "Grid did not pass gates. Failure mode: GATE_UPSTREAM_FAIL.\n\n"
            f"All trials failed at construction. Sample error from "
            f"config_id={best_config.config_id}: {err}\n\n"
            "Next step: per spec §7, treat this as a strategy-level "
            "rejection — the hypothesis (this pair / this universe / this "
            "regime) does not satisfy the construction gate. Pivot to the "
            "next catálogo intraday entry rather than tuning parameters."
        )

    lines = [
        "Grid did not pass gates. Failure modes: "
        + ", ".join(sorted(labels))
        + ".",
    ]
    lines.append(
        f"Best config by Sharpe (ignoring gates): config_id="
        f"{best_config.config_id}, Sharpe={best_config.sharpe:.3f}, "
        f"CAGR={best_config.cagr:.3f}, max_dd={best_config.max_drawdown:.3f}."
    )
    if "PBO_HIGH" in labels:
        lines.append(
            "PBO_HIGH: grid is overfit — don't expand the grid. Consider a "
            "different hypothesis family (Ehlers DSP, AFML meta-label, mean "
            "reversion) or a universe shift (Nasdaq100, liquidity filter)."
        )
    if "DSR_ALL_FAIL" in labels and "PBO_HIGH" not in labels:
        lines.append(
            "DSR_ALL_FAIL with PBO in range: edge is real but small relative "
            "to trial count. Option A: paid-data ablation (survivorship-free) "
            "— if edge appears there, grid was being killed by data noise. "
            "Option B: pivot to a stronger hypothesis."
        )
    if "WF_INSUFFICIENT" in labels:
        lines.append(
            "WF_INSUFFICIENT: drill into the per-window breakdown above — if "
            "failures cluster on specific regimes (2020 H1, 2022 bear), a "
            "regime filter or position sizing change might save the edge. "
            "If failures scatter, the edge isn't durable."
        )
    lines.append(
        "Next step: bring this diagnostic report back and we'll choose between "
        "paid-data ablation, universe shift, and strategy pivot together."
    )
    return "\n\n".join(lines)
