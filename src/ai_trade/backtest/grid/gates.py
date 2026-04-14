"""GateEvaluator — apply the 3 anti-overfit rules to a GridResult.

Consumes:

* :class:`GridResult` (trials with cached scalar metrics + aligned returns
  matrix for PBO)
* ``wf_verdicts: dict[config_id, "pass"|"reject"]`` — per-config walk-forward
  verdicts from the :mod:`grid.walk_forward` module

Produces a :class:`GateVerdict` exposing the raw outputs of each gate plus
the aggregate ``overall_pass`` flag and (when possible) the ``best_config_id``.

Rules (``knowledge/SKILL.md``):

* #3 PBO < 0.5
* #4 DSR p-value < 0.05
* #5 Walk-forward verdict == ``"pass"``

``overall_pass`` is ``True`` iff at least one config passes all three gates.
``best_config_id`` is the passing config with the largest cached Sharpe.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np

from ai_trade.backtest.grid.result import GridResult, TrialResult
from ai_trade.backtest.validation.dsr import DSRResult, dsr
from ai_trade.backtest.validation.pbo import PBOResult, pbo, pbo_gate


_log = logging.getLogger("ai_trade.grid.gates")


@dataclass
class GateVerdict:
    pbo_result: PBOResult | None
    pbo_pass: bool
    dsr_results: dict[int, DSRResult] = field(default_factory=dict)
    dsr_pass_ids: list[int] = field(default_factory=list)
    wf_verdicts: dict[int, str] = field(default_factory=dict)
    wf_pass_ids: list[int] = field(default_factory=list)
    overall_pass: bool = False
    best_config_id: int | None = None


@dataclass
class GateEvaluator:
    pbo_threshold: float = 0.5
    dsr_alpha: float = 0.05
    n_blocks_pbo: int = 10

    def evaluate(
        self,
        *,
        grid: GridResult,
        wf_verdicts: dict[int, str],
    ) -> GateVerdict:
        ok_trials = grid.ok_trials
        if not ok_trials:
            return GateVerdict(pbo_result=None, pbo_pass=False)

        pbo_result, pbo_pass = self._pbo_gate(grid)
        dsr_results, dsr_pass_ids = self._dsr_gate(ok_trials, n_trials=len(ok_trials))
        wf_pass_ids = sorted(cid for cid, v in wf_verdicts.items() if v == "pass")

        overall_pass, best_config_id = self._aggregate(
            ok_trials, pbo_pass, dsr_pass_ids, wf_pass_ids,
        )

        return GateVerdict(
            pbo_result=pbo_result,
            pbo_pass=pbo_pass,
            dsr_results=dsr_results,
            dsr_pass_ids=dsr_pass_ids,
            wf_verdicts=dict(wf_verdicts),
            wf_pass_ids=wf_pass_ids,
            overall_pass=overall_pass,
            best_config_id=best_config_id,
        )

    def _pbo_gate(self, grid: GridResult) -> tuple[PBOResult | None, bool]:
        matrix = grid.returns_matrix
        if matrix.shape[1] < 2 or matrix.shape[0] < self.n_blocks_pbo:
            _log.warning(
                "PBO skipped: matrix shape %s insufficient for %d blocks",
                matrix.shape, self.n_blocks_pbo,
            )
            return None, False
        result = pbo(matrix, n_blocks=self.n_blocks_pbo)
        passed = pbo_gate(float(result.pbo), threshold=self.pbo_threshold) == "pass"
        return result, passed

    def _dsr_gate(
        self,
        ok_trials: list[TrialResult],
        n_trials: int,
    ) -> tuple[dict[int, DSRResult], list[int]]:
        results: dict[int, DSRResult] = {}
        pass_ids: list[int] = []
        for trial in ok_trials:
            if trial.result is None:
                continue
            eq = trial.result.equity_curve
            rets = eq.pct_change().dropna().to_numpy(dtype=float)
            if len(rets) < 2:
                continue
            try:
                dsr_res = dsr(rets, n_trials=n_trials)
            except ValueError as exc:
                _log.warning(
                    "DSR failed for config %d: %s", trial.config_id, exc,
                )
                continue
            results[trial.config_id] = dsr_res
            if dsr_res.p_value < self.dsr_alpha:
                pass_ids.append(trial.config_id)
        pass_ids.sort()
        return results, pass_ids

    def _aggregate(
        self,
        ok_trials: list[TrialResult],
        pbo_pass: bool,
        dsr_pass_ids: list[int],
        wf_pass_ids: list[int],
    ) -> tuple[bool, int | None]:
        if not pbo_pass:
            return False, None
        passers = set(dsr_pass_ids) & set(wf_pass_ids)
        if not passers:
            return False, None
        # Select the config with the highest cached Sharpe among passers.
        candidates = [t for t in ok_trials if t.config_id in passers]
        best = max(
            candidates,
            key=lambda t: t.sharpe if np.isfinite(t.sharpe) else -np.inf,
        )
        return True, best.config_id
