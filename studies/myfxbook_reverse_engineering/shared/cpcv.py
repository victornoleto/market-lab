"""CSCV / PBO — Pipeline v4 Redesign module (task 003).

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task spec: studies/myfxbook_reverse_engineering/v4_redesign/tasks/003-cpcv-pbo.md

Combinatorial Symmetric Cross-Validation (CSCV) and Probability of Backtest
Overfitting (PBO).

`[advances_fin_ml, p.208-222]` (Lopez de Prado, AFML cap. 14, baseado em Bailey
& Lopez de Prado 2014). PBO mede a probabilidade de que a estrategia escolhida
como "melhor in-sample" entre N candidatos seja ranqueada abaixo da mediana
out-of-sample. PBO >= 0.5 = mais provavel que ter sido sorte do que edge real
`[advances_fin_ml, p.211]`.

PBO **complementa** WF, nao substitui. PBO mede sorte na selecao entre N
candidates; WF mede generalizacao temporal de UMA regra. Mandate §2.4 exige
ambos como hard gates. Veja `DEAD_ENDS.md` -> "PBO substituindo WF8 (rejeitado)".

Algoritmo (sintese de Bailey/Lopez 2014 §2.2):

  1. Particionar matriz `M` (T x N) em S sub-matrizes contiguas (T = S aqui).
  2. Para cada combinacao c de S/2 indices em {0,...,S-1} — total
     `phi[S, S/2] = C(S, S/2)` paths:
       - train_set = c, test_set = complement
       - rank do "best-in-train" no test (rank 1 = pior, N = melhor)
       - w_c = rank / (N+1)
       - lambda_c = log(w_c / (1 - w_c))
  3. PBO = fracao de paths com `lambda_c <= 0` (i.e., w_c <= 0.5).
  4. CI 99% via bootstrap dos indicadores.

Output: `CPCVResult` com PBO + diagnosticos.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from itertools import combinations
from math import comb
from typing import Any, Sequence

import numpy as np
import pandas as pd
import scipy.stats

PBO_THRESHOLD = 0.50  # mandate §2.4 hard gate; >= 0.5 rejeita
DEFAULT_N_GROUPS = 16
MIN_GROUPS = 4  # S < 4 -> n_paths < 2 ou trivial
DEFAULT_BOOTSTRAP_SEED = 20260504
DEFAULT_N_BOOT = 1000


@dataclass(frozen=True)
class CPCVResult:
    """Resultado de uma rodada CSCV/PBO.

    `pbo`: fracao de paths em que o "best-in-train" ranqueou abaixo da mediana
    OOS. PBO < 0.5 = generaliza; PBO >= 0.5 = mais provavel sorte que edge real
    `[advances_fin_ml, p.211]`.

    `pbo_ci_low_99 / pbo_ci_high_99`: bootstrap quantile CI dos indicadores
    `(lambda_c <= 0)` — diagnostico de incerteza amostral, nao gate.

    `median_oos_rank_of_best_is`: mediana do rank OOS do melhor IS (1 = pior,
    N = melhor). Edge real -> > (N+1)/2; sorte -> ~ (N+1)/2.
    """

    n_groups: int
    n_test: int
    n_paths: int
    pbo: float
    pbo_ci_low_99: float
    pbo_ci_high_99: float
    median_oos_rank_of_best_is: float
    n_strategies: int
    n_periods: int


def _validate_matrix(M: np.ndarray) -> tuple[int, int]:
    if M.ndim != 2:
        raise ValueError(f"metric_matrix deve ser 2D; got shape={M.shape}")
    T, N = M.shape
    if N < 2:
        raise ValueError(f"CSCV exige N>=2 estrategias; got N={N}")
    if not np.all(np.isfinite(M)):
        raise ValueError("metric_matrix contem NaN/Inf; limpar antes de chamar")
    return T, N


def _enumerate_paths(S: int, n_test: int) -> list[tuple[int, ...]]:
    """Enumera todos os splits train/test de tamanho S/2.

    Para PBO, `J train / J^c test` e `J^c train / J test` nao sao duplicatas:
    cada lado pode escolher uma estrategia diferente in-sample, gerando ranks
    OOS diferentes. Portanto usamos `C(S, S/2)` paths, nao metade.
    `[advances_fin_ml, p.208-222]`.
    """
    return list(combinations(range(S), n_test))


def _logit(w: float, eps: float = 1e-12) -> float:
    w_c = float(np.clip(w, eps, 1.0 - eps))
    return float(np.log(w_c / (1.0 - w_c)))


def cscv_pbo(
    metric_matrix: pd.DataFrame,
    n_groups: int = DEFAULT_N_GROUPS,
    metric: str = "sharpe",
    *,
    bootstrap_seed: int = DEFAULT_BOOTSTRAP_SEED,
    n_bootstrap: int = DEFAULT_N_BOOT,
) -> CPCVResult:
    """Roda CSCV e retorna PBO. `[advances_fin_ml, p.208-222]`.

    Args:
      metric_matrix: shape (T, N). T sub-periodos contiguos, N candidate
        rules. `metric_matrix.iloc[t, n]` = metrica (Sharpe / total_pnl /
        Calmar) da rule n no sub-periodo t. Index pode ser DatetimeIndex ou
        RangeIndex contiguo. Columns sao IDs (string) das rules.
      n_groups: S = numero de sub-periodos. S = T (sem rebinning v1). Se
        T != n_groups, usa T como S e ignora o argumento (com warning).
        Se T impar, dropa ultima linha (S = T - 1) com warning.
      metric: tag informacional (nao muda o algoritmo). `"sharpe" | "total_pnl"
        | "calmar"`.
      bootstrap_seed: seed para CI bootstrap (determinismo).
      n_bootstrap: numero de resamples para CI 99%.

    Returns:
      CPCVResult com PBO + diagnosticos.

    Raises:
      ValueError: se T < MIN_GROUPS, N < 2, ou matrix tem NaN/Inf.
    """
    if metric not in {"sharpe", "total_pnl", "calmar"}:
        raise ValueError(f"metric deve ser sharpe|total_pnl|calmar; got {metric!r}")

    M = np.asarray(metric_matrix.to_numpy() if isinstance(metric_matrix, pd.DataFrame) else metric_matrix, dtype=float)
    T, N = _validate_matrix(M)

    if T < MIN_GROUPS:
        raise ValueError(
            f"CSCV exige T >= {MIN_GROUPS}; got T={T}. "
            f"n_paths < 2 -> PBO trivial / sem variancia amostral."
        )

    S = T
    if S % 2 != 0:
        warnings.warn(
            f"T={T} e impar; dropando ultima linha, S={T - 1}",
            UserWarning,
            stacklevel=2,
        )
        M = M[: S - 1]
        S = S - 1

    if S != n_groups:
        warnings.warn(
            f"n_groups={n_groups} != T={S}; usando S=T (sem rebinning v1).",
            UserWarning,
            stacklevel=2,
        )

    n_test = S // 2
    paths = _enumerate_paths(S, n_test)
    n_paths = len(paths)
    if n_paths < 2:
        raise ValueError(
            f"n_paths={n_paths} < 2. S={S} muito pequeno para CSCV. "
            f"Aumente sub-periodos."
        )
    # invariante: PBO avalia os dois sentidos do split, pois o best-in-train
    # pode diferir entre J e J^c.
    assert n_paths == comb(S, n_test)

    logits = np.empty(n_paths, dtype=float)
    oos_ranks_of_best = np.empty(n_paths, dtype=float)
    all_index = np.arange(S)

    for k, train_idx_t in enumerate(paths):
        train_idx = np.array(train_idx_t, dtype=int)
        test_mask = np.ones(S, dtype=bool)
        test_mask[train_idx] = False
        test_idx = all_index[test_mask]

        # in-sample / out-of-sample performance per estrategia (mean over groups)
        in_perf = M[train_idx].mean(axis=0)  # (N,)
        oos_perf = M[test_idx].mean(axis=0)  # (N,)

        # best-in-sample (argmax). Em caso de empate, np.argmax retorna primeiro indice.
        n_star = int(np.argmax(in_perf))

        # rank OOS: rank 1 = pior, N = melhor (method="average" lida com empates)
        ranks = scipy.stats.rankdata(oos_perf, method="average")
        rank_n_star = float(ranks[n_star])
        oos_ranks_of_best[k] = rank_n_star

        # w = rank / (N+1) ∈ (0, 1); usa N+1 para nunca atingir 0 ou 1
        w = rank_n_star / (N + 1)
        logits[k] = _logit(w)

    indicators = (logits <= 0.0).astype(float)
    pbo = float(indicators.mean())

    # bootstrap 99% CI dos indicadores
    rng = np.random.default_rng(bootstrap_seed)
    boot = rng.choice(indicators, size=(n_bootstrap, n_paths), replace=True).mean(axis=1)
    pbo_ci_low_99 = float(np.quantile(boot, 0.005))
    pbo_ci_high_99 = float(np.quantile(boot, 0.995))

    median_oos_rank = float(np.median(oos_ranks_of_best))

    return CPCVResult(
        n_groups=int(S),
        n_test=int(n_test),
        n_paths=int(n_paths),
        pbo=pbo,
        pbo_ci_low_99=pbo_ci_low_99,
        pbo_ci_high_99=pbo_ci_high_99,
        median_oos_rank_of_best_is=median_oos_rank,
        n_strategies=int(N),
        n_periods=int(S),
    )


def _per_group_sharpe(returns: np.ndarray) -> float:
    """Sharpe per-trade (sem anualizacao). NaN se < 2 obs ou std == 0."""
    if returns.size < 2:
        return float("nan")
    sd = float(np.std(returns, ddof=1))
    if sd == 0.0:
        return float("nan")
    return float(np.mean(returns) / sd)


def _per_group_total_pnl(returns: np.ndarray) -> float:
    if returns.size == 0:
        return float("nan")
    return float(np.sum(returns))


def _per_group_calmar(returns: np.ndarray) -> float:
    """Calmar per-period: mean / max_drawdown_abs. Per-trade fragil; NaN se DD=0."""
    if returns.size < 2:
        return float("nan")
    eq = np.cumsum(returns)
    peak = np.maximum.accumulate(eq)
    dd = peak - eq
    max_dd = float(dd.max())
    if max_dd == 0.0:
        return float("nan")
    return float(np.mean(returns) / max_dd)


_METRIC_FNS = {
    "sharpe": _per_group_sharpe,
    "total_pnl": _per_group_total_pnl,
    "calmar": _per_group_calmar,
}


def build_metric_matrix_from_candidates(
    candidates: Sequence[dict[str, Any]],
    trades: pd.DataFrame,
    ohlc: dict[str, pd.DataFrame] | None = None,
    n_groups: int = DEFAULT_N_GROUPS,
    metric: str = "sharpe",
) -> pd.DataFrame:
    """Adapter myfxbook: produz matriz (n_groups, N) de metrica per-rule per-sub-periodo.

    Para cada candidate, espera-se `extra["predicted_mask"]` (bool array de
    `len(trades)` indicando quais trades a regra "tomaria"). Nas trades onde
    mask=True, contribuem com `pips`; mask=False contribuem com 0 (skip).
    Sub-periodos sao bins temporais iguais por `open_dt_utc`.

    Citacoes:
    - Sharpe per-trade nas sub-janelas: `[evidence_based_ta, p.325-328]`
      (sample-level signal/noise como insumo do PBO).

    Args:
      candidates: list de dicts (schema `Candidate.to_dict()`). Cada dict
        precisa de `rank` (int) e idealmente `extra["predicted_mask"]` para
        avaliacao. Se ausente, a coluna fica NaN.
      trades: DataFrame com colunas `pips` (float), `is_trade` (bool),
        `open_dt_utc` (datetime UTC). Apenas rows com `is_trade=True`
        contam. Outros campos sao ignorados.
      ohlc: dict por simbolo (reservado para v2; nao usado nesta versao).
      n_groups: numero de sub-periodos. Cada bin temporal contiguo agrupa
        ~len(trades)/n_groups trades.
      metric: `"sharpe" | "total_pnl" | "calmar"`.

    Returns:
      DataFrame shape `(n_groups, len(candidates))`. Index = bin number 0..S-1.
      Columns = `f"cand_{rank}"` ou `extra["id"]` se presente. NaN onde
      sub-periodo tem < 2 trades validos.
    """
    if metric not in _METRIC_FNS:
        raise ValueError(f"metric deve ser sharpe|total_pnl|calmar; got {metric!r}")
    if n_groups < MIN_GROUPS:
        raise ValueError(f"n_groups >= {MIN_GROUPS} obrigatorio; got {n_groups}")

    metric_fn = _METRIC_FNS[metric]

    valid = trades[trades["is_trade"]].copy() if "is_trade" in trades.columns else trades.copy()
    valid = valid.sort_values("open_dt_utc").reset_index(drop=True)
    n_trades = len(valid)
    n_cand = len(candidates)

    columns = [c.get("extra", {}).get("id") or f"cand_{c.get('rank', i + 1)}" for i, c in enumerate(candidates)]

    # bins temporais iguais — pd.cut com n_groups bins iguais sobre [t_min, t_max]
    if n_trades < n_groups * 2:
        # Sub-periodos com < 2 trades retornam NaN; ainda devolvemos shape correto.
        result = np.full((n_groups, n_cand), np.nan, dtype=float)
        return pd.DataFrame(result, columns=columns)

    t_min = valid["open_dt_utc"].min()
    t_max = valid["open_dt_utc"].max()
    if pd.isna(t_min) or pd.isna(t_max) or t_min == t_max:
        result = np.full((n_groups, n_cand), np.nan, dtype=float)
        return pd.DataFrame(result, columns=columns)

    bin_edges = pd.date_range(t_min, t_max, periods=n_groups + 1)
    bin_idx = pd.cut(valid["open_dt_utc"], bin_edges, labels=False, include_lowest=True).to_numpy()

    pips = valid["pips"].astype(float).fillna(0.0).to_numpy()

    matrix = np.full((n_groups, n_cand), np.nan, dtype=float)

    for j, cand in enumerate(candidates):
        mask = cand.get("extra", {}).get("predicted_mask")
        if mask is None:
            # Sem predicted_mask: rule nao e avaliavel; coluna inteira NaN.
            continue
        mask_arr = np.asarray(mask, dtype=bool)
        if mask_arr.shape[0] != n_trades:
            raise ValueError(
                f"candidate[{j}].extra.predicted_mask len={mask_arr.shape[0]} != "
                f"len(trades)={n_trades}"
            )
        rule_returns = np.where(mask_arr, pips, 0.0)
        for g in range(n_groups):
            in_bin = bin_idx == g
            if in_bin.sum() < 2:
                continue
            matrix[g, j] = metric_fn(rule_returns[in_bin])

    return pd.DataFrame(matrix, columns=columns)
