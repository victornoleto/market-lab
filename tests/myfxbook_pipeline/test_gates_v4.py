"""Unit tests for shared.gates v4 refactor (task 004-gates-dsr-hard).

Cobertura:
- DSR p < 0.05 -> passes (`[advances_fin_ml, p.273-275]`)
- DSR p >= 0.05 -> fails com 'dsr_p' em failed_gate_names
- PBO < 0.50 -> passes (`[advances_fin_ml, p.208-222]`)
- PBO >= 0.50 -> fails
- Combinacao parcial (Sharpe ok + DSR fail -> fail total)
- CAGR / MDD altos NAO bloqueiam (warning-only `[mandate §2.2/§2.3]`)
- WF purgado None NAO bloqueia (opcional)
- WF purgado < 6 -> fails (`[testing_tuning, p.148-162]`)
- compute_gates() backward-compat: chamada sem novos kwargs preserva
  comportamento pre-refactor

Citacoes:
- DSR: `[advances_fin_ml, p.273-275]`
- Bootstrap CI Sharpe: `[advances_fin_ml, p.196-211]`
- PBO via CSCV: `[advances_fin_ml, p.208-222]`
- WF purgado: `[testing_tuning, p.148-162]`
- CAGR/MDD warning-only: `[docs/investment-mandate.md §2.2/§2.3]`
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from studies.myfxbook_reverse_engineering.shared import gates as gates_mod
from studies.myfxbook_reverse_engineering.shared.cpcv import CPCVResult
from studies.myfxbook_reverse_engineering.shared.gates import (
    DSR_HARD_THRESHOLD,
    GateBlock,
    GateStats,
    PBO_THRESHOLD,
    WF_PURGED_MIN_POSITIVE,
    compute_gates,
)


def _make_block(*, sharpe: float = 1.5, dsr_p: float = 0.01,
                boot_lo: float = 0.8, boot_hi: float = 2.5,
                n_days: int = 600, n_trades: int = 1500) -> GateBlock:
    return GateBlock(
        n_days=n_days,
        n_trades=n_trades,
        daily_mean=0.5,
        daily_std=2.0,
        sharpe=sharpe,
        dsr_p=dsr_p,
        boot_lo=boot_lo,
        boot_hi=boot_hi,
    )


def _make_stats(
    *,
    full: GateBlock | None = None,
    oos: GateBlock | None | object = ...,
    pbo: float | None = None,
    wf_purged_n_positive: int | None = None,
    wf_purged_total: int | None = None,
    cagr: float | None = None,
    max_drawdown: float | None = None,
) -> GateStats:
    """Constroi GateStats minimo com defaults que fazem mandate §2.4 PASS."""
    full_block = full if full is not None else _make_block()
    if oos is ...:
        oos_block: GateBlock | None = _make_block(sharpe=1.0, boot_lo=0.5, n_days=180)
    else:
        oos_block = oos  # type: ignore[assignment]
    pbo_pass = None if pbo is None else (pbo < PBO_THRESHOLD)
    wf_pass = (
        None
        if wf_purged_n_positive is None
        else (wf_purged_n_positive >= WF_PURGED_MIN_POSITIVE)
    )
    return GateStats(
        system_id="TEST",
        cost_model_spread_pips={"EURUSD": 1.0},
        cost_model_commission_pips=0.7,
        full=full_block,
        oos=oos_block,
        walkforward=pd.DataFrame(),
        n_wf_positive=7,
        sharpe_optimistic=1.6,
        gate2_pass=full_block.dsr_p < DSR_HARD_THRESHOLD,
        gate3_pass=True,
        gate4_pass=oos_block is not None and oos_block.sharpe > 0 and oos_block.boot_lo > 0,
        gate6_pass=full_block.boot_lo > 0,
        pbo=pbo,
        pbo_pass=pbo_pass,
        wf_purged_n_positive=wf_purged_n_positive,
        wf_purged_total=wf_purged_total,
        wf_purged_pass=wf_pass,
        cagr=cagr,
        max_drawdown=max_drawdown,
    )


def test_dsr_below_threshold_passes() -> None:
    stats = _make_stats(full=_make_block(dsr_p=0.001))
    passes, failed = stats.passes_mandate_24()
    assert passes is True
    assert "dsr_p" not in failed


def test_dsr_above_threshold_fails_with_dsr_p_in_failed_names() -> None:
    """DSR p=0.10 (>=0.05) bloqueia; outros gates passam.
    `[advances_fin_ml, p.273-275]`"""
    stats = _make_stats(full=_make_block(dsr_p=0.10))
    passes, failed = stats.passes_mandate_24()
    assert passes is False
    assert "dsr_p" in failed


def test_pbo_below_threshold_passes() -> None:
    stats = _make_stats(pbo=0.30)
    passes, failed = stats.passes_mandate_24()
    assert passes is True
    assert "pbo" not in failed


def test_pbo_above_threshold_fails_with_pbo_in_failed_names() -> None:
    """PBO=0.60 (>=0.50) bloqueia. `[advances_fin_ml, p.208-222]`"""
    stats = _make_stats(pbo=0.60)
    passes, failed = stats.passes_mandate_24()
    assert passes is False
    assert "pbo" in failed


def test_partial_pass_sharpe_ok_dsr_fail_means_total_fail() -> None:
    """Sharpe bootstrap CI ok + OOS ok + WF ok, mas DSR alto -> falha agregada."""
    stats = _make_stats(full=_make_block(boot_lo=0.9, dsr_p=0.20))
    passes, failed = stats.passes_mandate_24()
    assert passes is False
    assert "dsr_p" in failed
    assert "sharpe_bootstrap_ci_low_999" not in failed


def test_cagr_and_mdd_high_do_not_block_warning_only() -> None:
    """CAGR e MDD nunca aparecem em failed_gate_names mandate §2.2/§2.3."""
    stats = _make_stats(cagr=10.0, max_drawdown=-0.95)  # absurdamente altos
    passes, failed = stats.passes_mandate_24()
    assert passes is True
    assert "cagr" not in failed
    assert "max_drawdown" not in failed


def test_wf_purged_none_does_not_block() -> None:
    """WF purgado opcional: None nao bloqueia (sem ohlc embargado disponivel)."""
    stats = _make_stats(wf_purged_n_positive=None, wf_purged_total=None)
    passes, failed = stats.passes_mandate_24()
    assert passes is True
    assert "wf_purged_positive" not in failed


def test_wf_purged_below_6_fails() -> None:
    """WF purgado 4/8 < 6 -> falha. `[testing_tuning, p.148-162]`"""
    stats = _make_stats(wf_purged_n_positive=4, wf_purged_total=8)
    passes, failed = stats.passes_mandate_24()
    assert passes is False
    assert "wf_purged_positive" in failed


def test_oos_missing_blocks_oos_gate() -> None:
    stats = _make_stats(oos=None)
    passes, failed = stats.passes_mandate_24()
    assert passes is False
    assert "oos_bootstrap_ci_low_999" in failed


def test_sharpe_bootstrap_ci_low_zero_blocks() -> None:
    stats = _make_stats(full=_make_block(boot_lo=0.0))
    passes, failed = stats.passes_mandate_24()
    assert passes is False
    assert "sharpe_bootstrap_ci_low_999" in failed


def test_compute_gates_backward_compat_no_new_kwargs() -> None:
    """Chamada sem `cpcv_result` / `wf_purged` preserva comportamento pre-task-004.

    Insumos: trades sinteticos minimos. Saida: GateStats com `pbo`,
    `wf_purged_*`, `cagr`, `max_drawdown` todos None.
    """
    rng = np.random.default_rng(42)
    n_trades = 800
    open_dt = pd.date_range("2018-01-01", periods=n_trades, freq="6h", tz="UTC")
    close_dt = open_dt + pd.Timedelta("1h")
    pips = rng.normal(loc=2.0, scale=10.0, size=n_trades)
    trades = pd.DataFrame(
        {
            "is_trade": True,
            "open_dt_utc": open_dt,
            "close_dt_utc": close_dt,
            "symbol": "EURUSD",
            "pips": pips,
        }
    )
    stats = compute_gates(trades, system_id="SMOKE", n_bootstrap=200)
    assert stats.pbo is None
    assert stats.pbo_pass is None
    assert stats.wf_purged_n_positive is None
    assert stats.wf_purged_total is None
    assert stats.wf_purged_pass is None
    assert stats.cagr is None
    assert stats.max_drawdown is None
    # Propriedades novas devem refletir blocos legados
    assert stats.dsr_p == stats.full.dsr_p
    assert stats.sharpe_bootstrap_ci_low_999 == stats.full.boot_lo
    assert stats.wf_simple_positive == stats.n_wf_positive


def test_compute_gates_with_cpcv_result_populates_pbo() -> None:
    rng = np.random.default_rng(7)
    n_trades = 600
    open_dt = pd.date_range("2018-01-01", periods=n_trades, freq="8h", tz="UTC")
    trades = pd.DataFrame(
        {
            "is_trade": True,
            "open_dt_utc": open_dt,
            "close_dt_utc": open_dt + pd.Timedelta("1h"),
            "symbol": "EURUSD",
            "pips": rng.normal(loc=1.5, scale=8.0, size=n_trades),
        }
    )
    cpcv = CPCVResult(
        n_groups=16,
        n_test=8,
        n_paths=12870,
        pbo=0.35,
        pbo_ci_low_99=0.30,
        pbo_ci_high_99=0.42,
        median_oos_rank_of_best_is=8.5,
        n_strategies=10,
        n_periods=16,
    )
    stats = compute_gates(
        trades,
        system_id="WITH_CPCV",
        n_bootstrap=200,
        cpcv_result=cpcv,
        wf_purged=(7, 8),
        cagr=0.18,
        max_drawdown=-0.22,
    )
    assert stats.pbo == pytest.approx(0.35)
    assert stats.pbo_pass is True
    assert stats.wf_purged_n_positive == 7
    assert stats.wf_purged_total == 8
    assert stats.wf_purged_pass is True
    assert stats.cagr == pytest.approx(0.18)
    assert stats.max_drawdown == pytest.approx(-0.22)


def test_passes_mandate_24_returns_tuple_bool_list() -> None:
    """Contrato de assinatura: `passes_mandate_24() -> tuple[bool, list[str]]`."""
    stats = _make_stats()
    result = stats.passes_mandate_24()
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], bool)
    assert isinstance(result[1], list)
    for name in result[1]:
        assert isinstance(name, str)


def test_module_exposes_thresholds() -> None:
    """Thresholds importaveis do modulo (auditoria)."""
    assert gates_mod.DSR_HARD_THRESHOLD == 0.05
    assert gates_mod.PBO_THRESHOLD == 0.50
    assert gates_mod.WF_PURGED_MIN_POSITIVE == 6
