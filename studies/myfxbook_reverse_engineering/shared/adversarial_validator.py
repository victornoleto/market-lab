"""Adversarial validator (real-vs-synthetic) — Pipeline v4 Redesign Fase 1.

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task: 005-adversarial-validator (TASKS.md / tasks/005-adversarial-validator.md)
Pre-reg: v4_redesign/iterations/005-adversarial-validator/PRE_REG.md

## What this measures

Treina um classificador binario LightGBM cuja unica tarefa e distinguir trades
*reais* (label=0) de trades *sinteticos* (label=1, gerados pelo replicator).
A AUC out-of-fold mede **identificabilidade** do decode:

* AUC ~ 0.5  → sintetico indistinguivel do real (decode capturou a distrib).
* AUC > 0.65 → modelo de geracao errado (overfire, taxonomia incorreta, etc).

Citacoes:
* `[advances_fin_ml, ch.5]` — feature importance + clustered MDA + LightGBM;
  uso de classificador adversarial para validar geracao sintetica.
* `[testing_tuning, ch.7]` — risco de overfitting em ML; capacity baixa em
  sample pequeno justifica hyperparams conservadores e CV estratificado.
* `[advances_fin_ml, p.196-211]` — bootstrap CI sobre AUCs dos folds.

## Interface (frozen)

```python
@dataclass(frozen=True)
class AdversarialResult:
    auc: float
    auc_ci_low_95: float
    auc_ci_high_95: float
    n_real: int
    n_synthetic: int
    n_features: int
    feature_importance: dict[str, float]  # top-10 ordenado decrescente
    notes: list[str]

def adversarial_validate(
    real_trades: pd.DataFrame,
    synthetic_trades: pd.DataFrame,
    *,
    cv_folds: int = 5,
    seed: int = 20260503,
) -> AdversarialResult: ...
```

## Sanity contract

| Cenario | Expectativa |
|---|---|
| `synthetic = real.copy()` | `0.45 ≤ AUC ≤ 0.55` |
| `synthetic = real.sample(0.5)` | `0.45 ≤ AUC ≤ 0.55` |
| Features sinteticas i.i.d. | `AUC > 0.85` |
| `synthetic = real`, `hour += 6` | `AUC > 0.70` |
| Mesma entrada + seed | mesmo AUC `±0.01` |
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold


# ---------------------------------------------------------------------------
# Constants — frozen by SPEC.md task 005.
# ---------------------------------------------------------------------------

#: Trade-level features computadas para real e synthetic. Window-level entra
#: na Fase 2A apos features ricas (news, cross-asset, tick volume).
FEATURE_COLUMNS: tuple[str, ...] = (
    "hour_utc",
    "dow",
    "pair_idx",
    "direction_idx",
    "lots",
    "duration_sec",
    "pips",
    "mfe_pips",
    "mae_pips",
    "entry_price_normalized",
)

#: Hyperparams LightGBM conservadores (anti-overfit em sample pequeno).
#: `[testing_tuning, ch.7]` — capacity baixa em sample pequeno.
LGBM_PARAMS: dict[str, object] = {
    "objective": "binary",
    "metric": "auc",
    "n_estimators": 200,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "min_child_samples": 10,
    "feature_fraction": 0.9,
    "bagging_fraction": 0.9,
    "bagging_freq": 5,
    "verbosity": -1,
    "deterministic": True,
    "force_row_wise": True,
}

#: Numero de reamostragens bootstrap para CI 95% sobre AUCs dos folds.
BOOTSTRAP_N: int = 1000

#: Tamanho minimo combinado abaixo do qual emitimos warning.
LOW_SAMPLE_THRESHOLD: int = 60


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AdversarialResult:
    """Resultado do classificador adversarial real-vs-synthetic.

    Attributes:
        auc: AUC media nos folds (out-of-fold), valor em [0, 1].
        auc_ci_low_95: percentil 2.5% do bootstrap nao-parametrico sobre os
            AUCs dos folds.
        auc_ci_high_95: percentil 97.5% do bootstrap.
        n_real: linhas de `real_trades` apos limpeza.
        n_synthetic: linhas de `synthetic_trades` apos limpeza.
        n_features: numero efetivo de features apos `_build_features`.
        feature_importance: top-10 features por gain, ordenado decrescente.
        notes: warnings nao-fatais (sample pequeno, classe degenerada, etc).
    """

    auc: float
    auc_ci_low_95: float
    auc_ci_high_95: float
    n_real: int
    n_synthetic: int
    n_features: int
    feature_importance: dict[str, float]
    notes: list[str]


# ---------------------------------------------------------------------------
# Feature builder
# ---------------------------------------------------------------------------


def _coerce_dt_utc(series: pd.Series) -> pd.Series:
    """Garante datetime UTC; aceita naive ou tz-aware."""
    s = pd.to_datetime(series, utc=True, errors="coerce")
    return s


def _build_pair_index(symbols: Iterable[str]) -> dict[str, int]:
    """Mapeia symbols -> int IDs estaveis por ordem alfabetica do conjunto pooled.

    Pool = real ∪ synthetic; mesma chave produz mesmo id em ambos. Ordem
    alfabetica garante determinismo (independent de qual DF foi processado
    primeiro). `[advances_fin_ml, ch.5]`.
    """
    seen = sorted({str(s) for s in symbols if pd.notna(s)})
    return {sym: idx for idx, sym in enumerate(seen)}


def _normalize_entry_price(df: pd.DataFrame, medians: dict[str, float]) -> pd.Series:
    """`open_price / median_open_price[pair]` — adimensional por pair."""
    px = pd.to_numeric(df.get("open_price"), errors="coerce")
    sym = df.get("symbol")
    if sym is None:
        return pd.Series([np.nan] * len(df), index=df.index, dtype="float64")
    med = sym.astype(str).map(medians).astype("float64")
    out = px / med
    return out


def _build_features(
    real: pd.DataFrame, synthetic: pd.DataFrame
) -> tuple[pd.DataFrame, pd.Series]:
    """Compute trade-level features para ambos DFs e empilha (real=0, synth=1).

    Mapeamentos sao computados sobre o pool (real ∪ synthetic) para que features
    derivadas (`pair_idx`, `entry_price_normalized`) sejam consistentes em
    ambos os lados.

    Returns:
        (X, y) — DataFrame de features (n_real+n_synth, n_features) e Series
        de labels (0 para real, 1 para synthetic).
    """
    if real.empty or synthetic.empty:
        raise ValueError(
            "real_trades e synthetic_trades nao podem estar vazios "
            f"(n_real={len(real)}, n_synthetic={len(synthetic)})."
        )

    pool_symbols = list(real.get("symbol", pd.Series(dtype=str))) + list(
        synthetic.get("symbol", pd.Series(dtype=str))
    )
    pair_map = _build_pair_index(pool_symbols)

    pool_prices = pd.concat(
        [
            pd.DataFrame(
                {
                    "symbol": real.get("symbol", pd.Series(dtype=str)).astype(str),
                    "open_price": pd.to_numeric(
                        real.get("open_price"), errors="coerce"
                    ),
                }
            ),
            pd.DataFrame(
                {
                    "symbol": synthetic.get("symbol", pd.Series(dtype=str)).astype(str),
                    "open_price": pd.to_numeric(
                        synthetic.get("open_price"), errors="coerce"
                    ),
                }
            ),
        ],
        ignore_index=True,
    )
    medians = (
        pool_prices.dropna(subset=["open_price"]).groupby("symbol")["open_price"].median()
    )
    medians_map = {k: float(v) for k, v in medians.items() if v and v != 0.0}

    def _one(df: pd.DataFrame) -> pd.DataFrame:
        dt = _coerce_dt_utc(df.get("open_dt_utc", pd.Series(dtype="datetime64[ns, UTC]")))
        sym = df.get("symbol", pd.Series(dtype=str)).astype(str)
        action = df.get("action", pd.Series(dtype=str)).astype(str)
        feats = pd.DataFrame(index=df.index)
        feats["hour_utc"] = dt.dt.hour.astype("float64")
        feats["dow"] = dt.dt.dayofweek.astype("float64")
        feats["pair_idx"] = sym.map(pair_map).astype("float64")
        # Buy=0, Sell=1; outros valores -> NaN (LightGBM trata missing).
        feats["direction_idx"] = action.where(action.isin(["Buy", "Sell"])).map(
            {"Buy": 0.0, "Sell": 1.0}
        )
        for col in ("lots", "duration_sec", "pips", "mfe_pips", "mae_pips"):
            feats[col] = pd.to_numeric(df.get(col), errors="coerce").astype("float64")
        feats["entry_price_normalized"] = _normalize_entry_price(df, medians_map)
        return feats[list(FEATURE_COLUMNS)]

    x_real = _one(real)
    x_synth = _one(synthetic)
    X = pd.concat([x_real, x_synth], axis=0, ignore_index=True)
    y = pd.Series(
        [0] * len(x_real) + [1] * len(x_synth), name="label", dtype="int64"
    )
    return X, y


# ---------------------------------------------------------------------------
# CV + scoring
# ---------------------------------------------------------------------------


def _paired_stratified_kfold_indices(
    X: pd.DataFrame, y: pd.Series, *, n_splits: int, seed: int
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    """K-fold pareado e estratificado por hash de features.

    Adversarial validation com `synthetic = real` byte-a-byte sofre data leakage
    em CV padrao: a permutacao independente das classes coloca a copia "real" no
    train e a "sintetica" no val (ou vice-versa), e o LightGBM memoriza features
    ID-like (lots, pips, duracao) → AUC ≈ 0 (sinal invertido), nao 0.5.

    Solucao: agrupar linhas por hash de feature row; cada hash recebe um fold
    via `StratifiedGroupKFold`, preservando duas invariantes simultaneas:
    (1) duplicatas real/synthetic viajam juntas, eliminando leakage;
    (2) cada fold mantem balanceamento aproximado de classes, evitando imbalance
    bias no AUC. Quando nao ha duplicatas, cada linha e seu proprio grupo e o
    comportamento se aproxima de StratifiedKFold randomizado seeded.

    `[advances_fin_ml, ch.5]` — leakage control em adversarial CV.
    `[testing_tuning, ch.7]` — purga e embargo evitam memorizacao de IDs.
    """
    Xh = X.fillna(-1.0e308)
    hashes = pd.util.hash_pandas_object(Xh, index=False).to_numpy()
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    yield from splitter.split(X, y, groups=hashes)


def _fold_auc(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    n_splits: int,
    seed: int,
) -> tuple[list[float], pd.Series]:
    """Roda paired-stratified-kfold; retorna AUCs por fold + feature importance media.

    `[testing_tuning, ch.7]` — paired stratified group k-fold purga rows
    duplicadas evitando memorizacao spuria de IDs entre classes sem abrir mao
    de balanceamento de labels no validation fold.
    """
    import lightgbm as lgb

    aucs: list[float] = []
    importances = pd.Series(0.0, index=X.columns, dtype="float64")
    n_models = 0

    for fold_idx, (tr, vl) in enumerate(
        _paired_stratified_kfold_indices(X, y, n_splits=n_splits, seed=seed)
    ):
        X_tr, X_vl = X.iloc[tr], X.iloc[vl]
        y_tr, y_vl = y.iloc[tr], y.iloc[vl]

        # Edge case: validation fold tem so 1 classe → AUC indefinido. Pula
        # com NaN; sera ignorado em np.nanmean. Garantir reproducibilidade
        # passando seed dependente de fold para cada modelo.
        if y_vl.nunique() < 2:
            aucs.append(float("nan"))
            continue

        model = lgb.LGBMClassifier(
            random_state=seed + fold_idx,
            **LGBM_PARAMS,
        )
        model.fit(X_tr, y_tr)
        proba = model.predict_proba(X_vl)[:, 1]
        auc = float(roc_auc_score(y_vl, proba))
        aucs.append(auc)

        booster = model.booster_
        gains = pd.Series(
            booster.feature_importance(importance_type="gain"),
            index=X.columns,
            dtype="float64",
        )
        importances = importances + gains
        n_models += 1

    if n_models > 0:
        importances = importances / n_models
    return aucs, importances


def _bootstrap_ci(values: list[float], *, seed: int) -> tuple[float, float]:
    """Bootstrap nao-parametrico 95% sobre os AUCs dos folds.

    `[advances_fin_ml, p.196-211]` — bootstrap CI sobre estatisticas de fold.
    Quando n_folds < 2, retorna (auc, auc) (CI degenerado).
    """
    arr = np.asarray([v for v in values if not np.isnan(v)], dtype="float64")
    if arr.size == 0:
        return float("nan"), float("nan")
    if arr.size == 1:
        return float(arr[0]), float(arr[0])
    rng = np.random.default_rng(seed + 1)
    samples = rng.choice(arr, size=(BOOTSTRAP_N, arr.size), replace=True)
    means = samples.mean(axis=1)
    lo = float(np.percentile(means, 2.5))
    hi = float(np.percentile(means, 97.5))
    return lo, hi


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def adversarial_validate(
    real_trades: pd.DataFrame,
    synthetic_trades: pd.DataFrame,
    *,
    cv_folds: int = 5,
    seed: int = 20260503,
) -> AdversarialResult:
    """Treina classificador real-vs-synthetic e retorna AUC out-of-fold.

    Args:
        real_trades: DataFrame de trades reais (do `parser.parse_history_html`
            ou equivalente). Esperado conter `open_dt_utc`, `symbol`, `action`,
            `lots`, `duration_sec`, `pips`, `open_price`. Opcionais:
            `mfe_pips`, `mae_pips`.
        synthetic_trades: DataFrame de trades gerados pelo replicator.
            Mesmo schema.
        cv_folds: numero de folds StratifiedKFold (default 5).
        seed: random_state para LightGBM, fold split e bootstrap.

    Returns:
        `AdversarialResult` com AUC media, CI 95% bootstrap, feature importance
        top-10 e notes.

    Raises:
        ValueError: se algum DF estiver vazio.
    """
    notes: list[str] = []

    # Filtrar so trades (defensivo — alguns DFs reais carregam deposit/withdrawal).
    real = real_trades.copy()
    synthetic = synthetic_trades.copy()
    if "is_trade" in real.columns:
        real = real[real["is_trade"].astype("boolean").fillna(True)].copy()
    if "is_trade" in synthetic.columns:
        synthetic = synthetic[
            synthetic["is_trade"].astype("boolean").fillna(True)
        ].copy()

    n_real = len(real)
    n_synth = len(synthetic)
    n_total = n_real + n_synth

    if n_total < LOW_SAMPLE_THRESHOLD:
        notes.append(
            f"low_sample_warning: n_total={n_total} < {LOW_SAMPLE_THRESHOLD}; "
            "AUC tem variancia alta. `[testing_tuning, ch.7]`"
        )

    X, y = _build_features(real, synthetic)
    n_features = X.shape[1]

    # Numero efetivo de folds: cada fold precisa de ao menos 1 amostra de cada
    # classe na validacao. StratifiedKFold ja garante isso, mas se a classe
    # menor for menor que cv_folds, reduzimos.
    min_class = int(min((y == 0).sum(), (y == 1).sum()))
    n_splits = max(2, min(cv_folds, min_class))
    if n_splits != cv_folds:
        notes.append(
            f"cv_folds_reduced: solicitado {cv_folds}, usado {n_splits} "
            f"(min_class={min_class})."
        )

    fold_aucs, importances = _fold_auc(X, y, n_splits=n_splits, seed=seed)
    valid_aucs = [a for a in fold_aucs if not np.isnan(a)]
    if not valid_aucs:
        notes.append("all_folds_degenerate: validacao com classe unica em todos os folds.")
        auc = float("nan")
    else:
        auc = float(np.mean(valid_aucs))

    ci_lo, ci_hi = _bootstrap_ci(fold_aucs, seed=seed)

    # Top-10 importance ordenada decrescente; keys preservam ordem (Python 3.7+).
    top = importances.sort_values(ascending=False).head(10)
    feature_importance = {str(k): float(v) for k, v in top.items()}

    return AdversarialResult(
        auc=auc,
        auc_ci_low_95=ci_lo,
        auc_ci_high_95=ci_hi,
        n_real=n_real,
        n_synthetic=n_synth,
        n_features=n_features,
        feature_importance=feature_importance,
        notes=notes,
    )


__all__ = [
    "AdversarialResult",
    "adversarial_validate",
    "FEATURE_COLUMNS",
    "LGBM_PARAMS",
    "BOOTSTRAP_N",
    "LOW_SAMPLE_THRESHOLD",
]
