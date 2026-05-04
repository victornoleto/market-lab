"""Sanity tests for `shared.adversarial_validator.adversarial_validate`.

Spec: studies/myfxbook_reverse_engineering/v4_redesign/tasks/005-adversarial-validator.md

5 sanity tests obrigatorios:
1. Copia exata: synthetic = real.copy() -> AUC em [0.45, 0.55].
2. Sub-amostra: synthetic = real.sample(0.5, seed) -> AUC em [0.45, 0.55].
3. Ruido puro: features sinteticos i.i.d. random -> AUC > 0.85.
4. Shift de hour: synthetic = real, hour += 6 -> AUC > 0.70.
5. Determinismo: mesma entrada + seed -> mesmo AUC `±0.01`.

Citacoes:
- `[advances_fin_ml, ch.5]` — adversarial validation real-vs-synthetic.
- `[testing_tuning, ch.7]` — overfit risks em ML CV.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

lgb = pytest.importorskip("lightgbm")

from studies.myfxbook_reverse_engineering.shared.adversarial_validator import (
    AdversarialResult,
    FEATURE_COLUMNS,
    _build_features,
    _paired_stratified_kfold_indices,
    adversarial_validate,
)


SEED = 20260503


def _make_real_trades(n: int = 200, *, base_hour: int = 10, seed: int = SEED) -> pd.DataFrame:
    """Synthetic 'real' trades com estrutura plausivel (hours concentrados).

    Features:
    - hour_utc concentrada em [base_hour - 2, base_hour + 2] (5 horas, sem cruzar dia).
    - 2 pares (EURUSD, GBPUSD).
    - Mistura Buy/Sell.
    - lots/duration/pips com distribuicoes realistas.
    """
    rng = np.random.default_rng(seed)
    base_ts = pd.Timestamp("2024-06-03 00:00:00", tz="UTC")  # Monday

    hours = rng.choice(
        np.arange(base_hour - 2, base_hour + 3), size=n, replace=True
    ).astype(int)
    days_offset = rng.integers(0, 90, size=n)
    minutes = rng.integers(0, 60, size=n)
    open_dts = base_ts + pd.to_timedelta(days_offset, unit="D")
    open_dts = open_dts + pd.to_timedelta(hours, unit="h")
    open_dts = open_dts + pd.to_timedelta(minutes, unit="m")

    symbols = rng.choice(["EURUSD", "GBPUSD"], size=n, replace=True)
    actions = rng.choice(["Buy", "Sell"], size=n, replace=True, p=[0.6, 0.4])
    lots = rng.uniform(0.01, 0.10, size=n)
    duration_sec = rng.uniform(120.0, 3600.0, size=n)
    pips = rng.normal(loc=2.0, scale=10.0, size=n)
    mfe_pips = pips + np.abs(rng.normal(loc=5.0, scale=3.0, size=n))
    mae_pips = pips - np.abs(rng.normal(loc=5.0, scale=3.0, size=n))
    open_price = np.where(symbols == "EURUSD", 1.08, 1.27) + rng.normal(0, 0.005, n)

    close_dts = open_dts + pd.to_timedelta(duration_sec, unit="s")

    df = pd.DataFrame(
        {
            "open_dt_utc": open_dts,
            "close_dt_utc": close_dts,
            "symbol": symbols,
            "action": actions,
            "lots": lots,
            "duration_sec": duration_sec,
            "pips": pips,
            "mfe_pips": mfe_pips,
            "mae_pips": mae_pips,
            "open_price": open_price,
            "is_trade": True,
            "is_deposit": False,
        }
    )
    return df


def _make_random_synth(n: int = 200, *, seed: int = SEED + 100) -> pd.DataFrame:
    """Synthetic 'fake' com features uniformemente aleatorias — i.i.d. ruido puro."""
    rng = np.random.default_rng(seed)
    base_ts = pd.Timestamp("2024-06-03 00:00:00", tz="UTC")
    hours = rng.integers(0, 24, size=n)
    days_offset = rng.integers(0, 90, size=n)
    minutes = rng.integers(0, 60, size=n)
    open_dts = (
        base_ts
        + pd.to_timedelta(days_offset, unit="D")
        + pd.to_timedelta(hours, unit="h")
        + pd.to_timedelta(minutes, unit="m")
    )
    symbols = rng.choice(
        ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"], size=n, replace=True
    )
    actions = rng.choice(["Buy", "Sell"], size=n, replace=True)
    lots = rng.uniform(0.001, 5.0, size=n)
    duration_sec = rng.uniform(1.0, 86400.0, size=n)
    pips = rng.uniform(-200.0, 200.0, size=n)
    mfe_pips = rng.uniform(-200.0, 500.0, size=n)
    mae_pips = rng.uniform(-500.0, 200.0, size=n)
    open_price = rng.uniform(0.5, 2500.0, size=n)
    return pd.DataFrame(
        {
            "open_dt_utc": open_dts,
            "close_dt_utc": open_dts + pd.to_timedelta(duration_sec, unit="s"),
            "symbol": symbols,
            "action": actions,
            "lots": lots,
            "duration_sec": duration_sec,
            "pips": pips,
            "mfe_pips": mfe_pips,
            "mae_pips": mae_pips,
            "open_price": open_price,
            "is_trade": True,
            "is_deposit": False,
        }
    )


# ---------------------------------------------------------------------------
# Sanity tests
# ---------------------------------------------------------------------------


def test_exact_copy_yields_auc_near_half():
    """Sanity 1: synthetic = real.copy() — features identicas entre classes.

    Esperado: AUC ~ 0.5 (modelo nao tem sinal). Margem `[0.45, 0.55]`.
    `[advances_fin_ml, ch.5]` — adversarial AUC ~ 0.5 = generation perfeita.
    """
    real = _make_real_trades(n=200, seed=SEED)
    synth = real.copy()

    result = adversarial_validate(real, synth, cv_folds=5, seed=SEED)

    assert isinstance(result, AdversarialResult)
    assert result.n_real == 200
    assert result.n_synthetic == 200
    assert result.n_features == len(FEATURE_COLUMNS)
    assert 0.45 <= result.auc <= 0.55, (
        f"Esperado AUC ~ 0.5 (copia exata), recebido {result.auc:.4f}. "
        f"Notes: {result.notes}"
    )


def test_subsample_yields_auc_near_half():
    """Sanity 3 (do spec): synthetic = real.sample(0.5) — mesma distribuicao."""
    real = _make_real_trades(n=300, seed=SEED)
    synth = real.sample(frac=0.5, random_state=SEED).reset_index(drop=True)

    result = adversarial_validate(real, synth, cv_folds=5, seed=SEED)

    assert 0.45 <= result.auc <= 0.55, (
        f"Esperado AUC ~ 0.5 (sub-amostra), recebido {result.auc:.4f}. "
        f"Notes: {result.notes}"
    )


def test_random_synth_yields_high_auc():
    """Sanity 2 (do spec): synthetic com features i.i.d. -> AUC > 0.85.

    Real concentrado em hour [8-12] e poucos pares; synthetic uniformemente
    aleatorio em todas dimensoes. Modelo separa facilmente.
    """
    real = _make_real_trades(n=200, seed=SEED)
    synth = _make_random_synth(n=200, seed=SEED + 999)

    result = adversarial_validate(real, synth, cv_folds=5, seed=SEED)

    assert result.auc > 0.85, (
        f"Esperado AUC > 0.85 (ruido puro), recebido {result.auc:.4f}. "
        f"Notes: {result.notes}"
    )


def test_hour_shift_yields_high_auc():
    """Sanity 4: synthetic = real, mas hour_utc deslocado +6h -> AUC > 0.70.

    Modelo deve isolar `hour_utc` como feature separadora.
    """
    real = _make_real_trades(n=200, base_hour=10, seed=SEED)
    synth = real.copy()
    # Shift de 6h em open_dt_utc (open hour passa de [8,12] para [14,18]).
    synth["open_dt_utc"] = synth["open_dt_utc"] + pd.Timedelta(hours=6)
    synth["close_dt_utc"] = synth["close_dt_utc"] + pd.Timedelta(hours=6)

    result = adversarial_validate(real, synth, cv_folds=5, seed=SEED)

    assert result.auc > 0.70, (
        f"Esperado AUC > 0.70 (hour shift), recebido {result.auc:.4f}. "
        f"Notes: {result.notes}"
    )
    # E hour_utc deve ser top-1 ou pelo menos top-3 em importance.
    top3 = list(result.feature_importance.keys())[:3]
    assert "hour_utc" in top3, (
        f"hour_utc deveria estar entre top-3 features; recebido top-3={top3}, "
        f"importance={result.feature_importance}"
    )


def test_determinism_same_seed_same_auc():
    """Sanity 5: mesma entrada + mesmo seed -> mesmo AUC `±0.01`."""
    real = _make_real_trades(n=200, seed=SEED)
    synth = _make_random_synth(n=200, seed=SEED + 1)

    r1 = adversarial_validate(real, synth, cv_folds=5, seed=SEED)
    r2 = adversarial_validate(real, synth, cv_folds=5, seed=SEED)

    assert abs(r1.auc - r2.auc) <= 0.01, (
        f"Determinismo violado: r1.auc={r1.auc:.6f}, r2.auc={r2.auc:.6f}, "
        f"delta={abs(r1.auc - r2.auc):.6f}"
    )
    assert list(r1.feature_importance.keys()) == list(r2.feature_importance.keys()), (
        "Ordem de feature_importance deve ser deterministica para mesmo seed."
    )


def test_paired_stratified_splitter_keeps_duplicates_together_and_balanced():
    """Duplicate feature rows stay grouped while validation folds remain balanced.

    Regression for GPT-5.5 blocking validation: duplicate-pair grouping is
    required for exact-copy AUC, but the splitter must still be stratified to
    avoid class-imbalance bias `[testing_tuning, ch.7]`.
    """
    real = _make_real_trades(n=120, seed=SEED)
    synth = real.copy()
    X, y = _build_features(real, synth)

    for _, val in _paired_stratified_kfold_indices(X, y, n_splits=5, seed=SEED):
        y_val = y.iloc[val]
        assert set(y_val.unique()) == {0, 1}
        assert int((y_val == 0).sum()) == int((y_val == 1).sum())

        val_hashes = pd.util.hash_pandas_object(X.iloc[val].fillna(-1.0e308), index=False)
        counts = val_hashes.value_counts()
        assert counts.min() == 2
        assert counts.max() == 2
