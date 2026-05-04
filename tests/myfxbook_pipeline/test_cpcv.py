"""Unit tests for shared.cpcv (task 003-cpcv-pbo).

Synthetic scenarios follow [advances_fin_ml, p.208-222] (Lopez de Prado, AFML
cap. 14). Three regimes:

  - constant edge -> PBO baixo (estrategia A consistentemente boa OOS)
  - pure noise   -> PBO ~ 0.5 (rank OOS aleatorio)
  - rotative overfit -> PBO alto (best-in-sample muda em cada sub-periodo)

Citations:
- CSCV/PBO algoritmo: `[advances_fin_ml, p.208-222]`
- PBO < 0.5 hard gate: `[advances_fin_ml, p.211]`
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
import pytest

from studies.myfxbook_reverse_engineering.shared import cpcv


def _constant_edge_matrix(S: int = 16, N: int = 10, seed: int = 7) -> pd.DataFrame:
    """Estrategia 0 com Sharpe ~2.0; demais com Sharpe ~0. PBO esperado: baixo."""
    rng = np.random.default_rng(seed)
    M = rng.normal(loc=0.0, scale=0.3, size=(S, N))
    M[:, 0] += 2.0  # estrategia 0 dominante e estavel
    return pd.DataFrame(M, columns=[f"strat_{i}" for i in range(N)])


def _noise_matrix(S: int = 16, N: int = 10, seed: int = 11) -> pd.DataFrame:
    """Todas estrategias iid N(0,1). PBO esperado: ~ 0.5."""
    rng = np.random.default_rng(seed)
    M = rng.normal(loc=0.0, scale=1.0, size=(S, N))
    return pd.DataFrame(M, columns=[f"strat_{i}" for i in range(N)])


def _rotative_overfit_matrix(S: int = 16, N: int = 16, seed: int = 13) -> pd.DataFrame:
    """A "best in-sample" muda a cada sub-periodo (rotacao N=S). PBO esperado: alto.

    Estrategia i tem Sharpe enorme APENAS no sub-periodo i; resto do tempo Sharpe ~0.
    Quem ganha in-sample sera escolhida porque tem 1 sub-periodo de pico, mas
    out-of-sample colapsa.
    """
    rng = np.random.default_rng(seed)
    M = rng.normal(loc=0.0, scale=0.3, size=(S, N))
    for i in range(min(S, N)):
        M[i, i] = 10.0  # spike forte no sub-periodo i para estrategia i
    return pd.DataFrame(M, columns=[f"strat_{i}" for i in range(N)])


def test_constant_edge_low_pbo() -> None:
    """Estrategia dominante consistente -> PBO < 0.2 [advances_fin_ml, p.208-222]."""
    M = _constant_edge_matrix()
    res = cpcv.cscv_pbo(M, n_groups=16)
    assert res.pbo < 0.2, f"esperava PBO<0.2 com edge constante; got {res.pbo:.4f}"
    # n_paths = C(16,8) = 12870. The complementary split is not a duplicate
    # because it can choose a different best-in-train strategy.
    assert res.n_paths == 12870
    assert res.n_groups == 16
    assert res.n_test == 8
    # mediana do rank OOS do best-in-sample alta (perto de N=10)
    assert res.median_oos_rank_of_best_is >= 8.0


def test_pure_noise_pbo_around_half() -> None:
    """Pure noise -> PBO ~ 0.5 (banda 0.30-0.70 para N=10, S=16)."""
    M = _noise_matrix()
    res = cpcv.cscv_pbo(M, n_groups=16)
    assert 0.30 <= res.pbo <= 0.70, f"PBO fora da banda noise: {res.pbo:.4f}"


def test_adversarial_overfit_high_pbo() -> None:
    """Rotative best -> PBO > 0.7."""
    M = _rotative_overfit_matrix()
    res = cpcv.cscv_pbo(M, n_groups=16)
    assert res.pbo > 0.7, f"esperava PBO>0.7 em rotative overfit; got {res.pbo:.4f}"


def test_npaths_too_small_raises() -> None:
    """S < MIN_GROUPS -> ValueError com mensagem clara."""
    M = pd.DataFrame(np.zeros((2, 5)))
    with pytest.raises(ValueError, match="CSCV exige T >="):
        cpcv.cscv_pbo(M, n_groups=2)


def test_purging_no_period_reuse() -> None:
    """CSCV nao reusa sub-periodos: train_set e test_set sao disjuntos.

    Verifica diretamente o enumerador de paths.
    """
    S = 8
    n_test = S // 2
    paths = cpcv._enumerate_paths(S, n_test)
    assert len(paths) > 0
    all_index = set(range(S))
    for J in paths:
        train = set(J)
        test = all_index - train
        assert not (train & test), f"train ∩ test != ∅ em path {J}"
        assert train | test == all_index, f"train U test != universo em path {J}"
        assert len(train) == n_test


def test_complementary_splits_are_kept() -> None:
    """J/J^c e J^c/J podem produzir logits diferentes; manter ambos.

    This prevents regressing to C(S,S/2)/2 canonical representatives.
    `[advances_fin_ml, p.208-222]`.
    """
    S = 4
    n_test = S // 2
    paths = cpcv._enumerate_paths(S, n_test)
    assert len(paths) == 6
    assert (0, 1) in paths
    assert (2, 3) in paths

    M = pd.DataFrame(
        [
            [10.0, 0.0, 0.0],
            [10.0, 0.0, 0.0],
            [0.0, 10.0, 0.0],
            [0.0, 10.0, 0.0],
        ],
        columns=["a", "b", "c"],
    )
    res = cpcv.cscv_pbo(M, n_groups=4)
    assert res.n_paths == 6


def test_determinism() -> None:
    """Mesma matrix + seed -> mesmo PBO e mesmo CI bootstrap."""
    M = _noise_matrix()
    r1 = cpcv.cscv_pbo(M, n_groups=16, bootstrap_seed=42)
    r2 = cpcv.cscv_pbo(M, n_groups=16, bootstrap_seed=42)
    assert r1.pbo == r2.pbo
    assert r1.pbo_ci_low_99 == r2.pbo_ci_low_99
    assert r1.pbo_ci_high_99 == r2.pbo_ci_high_99
    # seeds diferentes movem o CI mas nao o PBO ponto
    r3 = cpcv.cscv_pbo(M, n_groups=16, bootstrap_seed=43)
    assert r1.pbo == r3.pbo, "PBO ponto e deterministico (nao depende de bootstrap_seed)"


def test_build_metric_matrix_smoke() -> None:
    """Smoke test do helper: 3 candidates + ~80 trades + n_groups=4 -> shape (4, 3)."""
    n_trades = 80
    rng = np.random.default_rng(99)
    times = pd.date_range("2024-01-01", periods=n_trades, freq="3h", tz="UTC")
    trades = pd.DataFrame(
        {
            "is_trade": [True] * n_trades,
            "pips": rng.normal(loc=0.5, scale=2.0, size=n_trades),
            "open_dt_utc": times,
        }
    )

    # Tres candidates com masks distintos: take all / take half / take none
    cand_all = {"rank": 1, "extra": {"predicted_mask": np.ones(n_trades, dtype=bool)}}
    cand_half = {"rank": 2, "extra": {"predicted_mask": np.array([i % 2 == 0 for i in range(n_trades)])}}
    cand_none = {"rank": 3, "extra": {"predicted_mask": np.zeros(n_trades, dtype=bool)}}

    df = cpcv.build_metric_matrix_from_candidates(
        [cand_all, cand_half, cand_none],
        trades,
        ohlc=None,
        n_groups=4,
        metric="sharpe",
    )

    assert df.shape == (4, 3), f"esperava (4, 3); got {df.shape}"
    assert list(df.columns) == ["cand_1", "cand_2", "cand_3"]
    # cand_all deve produzir Sharpes finitos (tem retornos variaveis)
    assert df["cand_1"].notna().all()
    # cand_none zera tudo -> std=0 -> NaN
    assert df["cand_3"].isna().all()
