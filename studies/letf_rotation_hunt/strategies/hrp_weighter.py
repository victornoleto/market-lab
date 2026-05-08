"""HRP and ERC weighting schemes for T5d (multi-asset Carver vol-target).

Citations
---------
* HRP: López de Prado [advances_fin_ml, ch.16 p.221-228]
* ERC: Maillard, Roncalli, Teïletche (2010), 'Properties of Equally
  Weighted Risk Contribution Portfolios'
* spec §3.3 (docs/specs/2026-05-08-t5-expansion-design.md)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform


def compute_hrp_weights(
    returns: pd.DataFrame, lookback: int = 252, min_periods: int = 126,
) -> pd.DataFrame:
    out = pd.DataFrame(index=returns.index, columns=returns.columns, dtype=float)
    for i, date in enumerate(returns.index):
        if i + 1 < min_periods:
            continue
        window = returns.iloc[max(0, i + 1 - lookback): i + 1]
        if len(window) < min_periods:
            continue
        out.loc[date] = _hrp_single(window)
    return out


def _hrp_single(returns: pd.DataFrame) -> pd.Series:
    cov = returns.cov().values.copy()
    corr = returns.corr().values.copy()
    np.fill_diagonal(corr, 1.0)
    dist = np.sqrt(0.5 * (1.0 - np.clip(corr, -1.0, 1.0)))
    np.fill_diagonal(dist, 0.0)
    link = linkage(squareform(dist, checks=False), method="single")
    sort_ix = _quasi_diag(link, n=len(returns.columns))
    weights = _recursive_bisection(cov, sort_ix)
    return pd.Series(weights, index=[returns.columns[i] for i in sort_ix]).reindex(returns.columns)


def _quasi_diag(link: np.ndarray, n: int) -> list[int]:
    link = link.astype(int)
    sort_ix = pd.Series([link[-1, 0], link[-1, 1]])
    while sort_ix.max() >= n:
        sort_ix.index = range(0, sort_ix.size * 2, 2)
        df0 = sort_ix[sort_ix >= n]
        i = df0.index
        j = df0.values - n
        sort_ix[i] = link[j, 0]
        df0 = pd.Series(link[j, 1], index=i + 1)
        sort_ix = pd.concat([sort_ix, df0]).sort_index()
        sort_ix.index = range(sort_ix.size)
    return sort_ix.tolist()


def _recursive_bisection(cov: np.ndarray, sort_ix: list[int]) -> np.ndarray:
    weights = np.ones(len(sort_ix))
    clusters = [sort_ix]
    while clusters:
        new_clusters = []
        for c in clusters:
            if len(c) <= 1:
                continue
            half = len(c) // 2
            left, right = c[:half], c[half:]
            var_l = _cluster_var(cov, left)
            var_r = _cluster_var(cov, right)
            alpha = 1.0 - var_l / (var_l + var_r)
            for idx in left:
                weights[sort_ix.index(idx)] *= alpha
            for idx in right:
                weights[sort_ix.index(idx)] *= (1.0 - alpha)
            new_clusters.extend([left, right])
        clusters = new_clusters
    return weights


def _cluster_var(cov: np.ndarray, indices: list[int]) -> float:
    sub = cov[np.ix_(indices, indices)]
    inv_diag = 1.0 / np.diag(sub)
    w = inv_diag / inv_diag.sum()
    return float(w @ sub @ w)
