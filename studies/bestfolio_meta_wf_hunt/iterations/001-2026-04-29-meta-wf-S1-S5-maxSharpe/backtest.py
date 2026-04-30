"""Iter 001 — meta walk-forward, max-Sharpe over S1-S5 universe.

Loads daily gross_returns from 5 pre-validated sleeves in
``studies/long_term_portfolio/iterations/`` and runs ``walk_forward_solve``
per dataset (lh_56y / vt_real / ndx_real). Reports Sharpe/CAGR/MDD,
Sharpe edge vs S1 (F1+SPLIT incumbent), DSR with cumulative n_trials,
walk-forward 8-fold, bootstrap 99.9% CI.

PBO and cross-lib gates are DEFERRED (PBO requires K≥2 configs, scheduled
for iter 003; cross-lib scheduled for iter 004).

Citations:
- bestfolio.app/blog/walk-forward-portfolios — methodology
- ``[advances_fin_ml, p.105-108]`` embargoed CV; ``p.196-202`` bootstrap;
  ``p.208-211`` PBO; ``p.222-223`` DSR n_trials cumulative
- ``[risk_parity, ch.5]`` sleeve thesis
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "studies"))

from _shared.wf_solver import walk_forward_solve  # noqa: E402
from src.ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr,
    max_drawdown,
    sharpe,
)
from src.ai_trade.backtest.validation.dsr import dsr as compute_dsr  # noqa: E402
from src.ai_trade.backtest.validation.walk_forward import (  # noqa: E402
    walk_forward_splits,
)

ITER_DIR = Path(__file__).resolve().parent
LTP_ITERS = REPO_ROOT / "studies" / "long_term_portfolio" / "iterations"

DATASETS = ["lh_56y", "vt_real", "ndx_real"]

SLEEVES = {
    "S1_F1_SPLIT": ("043-2026-04-30-F1-TLT-variation", "f1_split_baseline"),
    "S2_TLT_static": (
        "023-2026-04-29-0150-iter011-plus-TLT-sleeve",
        "tlt_mod_25_25_35_15",
    ),
    "S3_AllWeather": ("020-2026-04-28-2340-C3-all-weather", "aw_browne_25252525"),
    "S4_SPMO_hybrid": ("040-2026-04-30-F3-US-Hybrid-SPMO", "f3_spmo_5_subKMLM"),
    "S5_RSST_heavy": ("041-2026-04-30-F7-US-Stacked-MF", "f7_lite"),
}

LOOKBACK_MONTHS = 36
MAX_WEIGHT = 0.40
EMBARGO_DAYS = 21
BOOTSTRAP_N = 2000
WF_N_WINDOWS = 8
CUMULATIVE_N_TRIALS_PRIOR = 156  # long_term_portfolio cumulative through iter 043


def _load_sleeve_returns(iter_dirname: str, config_slug: str) -> dict[str, pd.Series]:
    path = LTP_ITERS / iter_dirname / "results.json"
    with path.open() as f:
        data = json.load(f)
    rs = data.get("returns_series", {})
    out: dict[str, pd.Series] = {}
    for ds in DATASETS:
        cfg = rs.get(ds, {}).get(config_slug, {})
        idx = cfg.get("index")
        ret = cfg.get("gross_returns")
        if idx is None or ret is None:
            raise ValueError(
                f"missing returns for {iter_dirname}/{config_slug}/{ds}"
            )
        out[ds] = pd.Series(ret, index=pd.to_datetime(idx))
    return out


def _aligned_panel(dataset: str) -> pd.DataFrame:
    series_by_sleeve = {
        sleeve_id: _load_sleeve_returns(dirname, slug)[dataset]
        for sleeve_id, (dirname, slug) in SLEEVES.items()
    }
    df = pd.concat(series_by_sleeve, axis=1).dropna()
    df.columns = list(SLEEVES.keys())
    return df


def _equity_from_returns(rets: pd.Series, start: float = 1.0) -> pd.Series:
    return start * (1.0 + rets).cumprod()


def _bootstrap_cagr_ci(
    returns: pd.Series, n: int = BOOTSTRAP_N, ci_level: float = 0.999
) -> tuple[float, float]:
    rng = np.random.default_rng(seed=42)
    arr = returns.to_numpy()
    cagrs = np.empty(n, dtype=float)
    L = len(arr)
    for i in range(n):
        sample = rng.choice(arr, size=L, replace=True)
        eq = (1.0 + sample).cumprod()
        years = L / 252.0
        cagrs[i] = eq[-1] ** (1.0 / years) - 1.0
    alpha = (1.0 - ci_level) / 2.0
    return float(np.quantile(cagrs, alpha)), float(np.quantile(cagrs, 1.0 - alpha))


def _wf_8fold(returns: pd.Series, k: int = WF_N_WINDOWS) -> dict:
    n = len(returns)
    is_size = max(int(n * 0.6 / k), 252)
    oos_size = max(int(n * 0.4 / k), 63)
    step = oos_size  # non-overlapping rolling windows
    sharpes_oos: list[float] = []
    for _train, test in walk_forward_splits(n, is_size, oos_size, step):
        oos = returns.iloc[list(test)]
        if len(oos) < 5:
            continue
        sharpes_oos.append(sharpe(oos))
    sharpes_oos = sharpes_oos[:k]
    n_winners = sum(1 for s in sharpes_oos if s > 0)
    return {
        "k": len(sharpes_oos),
        "winners": n_winners,
        "oos_sharpes": sharpes_oos,
        "ratio": (n_winners / len(sharpes_oos)) if sharpes_oos else 0.0,
    }


def _summarize_dataset(
    dataset: str, panel: pd.DataFrame
) -> dict:
    res = walk_forward_solve(
        panel,
        lookback_months=LOOKBACK_MONTHS,
        max_weight=MAX_WEIGHT,
        embargo_days=EMBARGO_DAYS,
        objective="sharpe",
        strict_lookback=True,
    )
    meta_returns = res.portfolio_returns
    meta_eq = _equity_from_returns(meta_returns)

    s1_returns = panel["S1_F1_SPLIT"].loc[meta_returns.index]
    s1_eq = _equity_from_returns(s1_returns)

    wfres = _wf_8fold(meta_returns)
    boot_low, boot_high = _bootstrap_cagr_ci(meta_returns)

    dsr_result = compute_dsr(
        meta_returns.to_numpy(), n_trials=CUMULATIVE_N_TRIALS_PRIOR + 1
    )

    weights_df = res.weights
    weight_concentration = float(
        (weights_df > 0.80).any(axis=1).mean() if len(weights_df) > 0 else 0.0
    )
    annual_turnover = float(
        weights_df.diff().abs().sum(axis=1).sum() / max((len(weights_df) / 12.0), 1.0)
    ) if len(weights_df) > 1 else 0.0

    return {
        "dataset": dataset,
        "n_obs": int(len(meta_returns)),
        "first_rebal": str(res.rebal_dates[0].date()) if len(res.rebal_dates) else None,
        "last_rebal": str(res.rebal_dates[-1].date()) if len(res.rebal_dates) else None,
        "meta": {
            "sharpe": float(sharpe(meta_returns)),
            "cagr": float(cagr(meta_eq)),
            "mdd": float(max_drawdown(meta_eq)),
        },
        "s1_incumbent": {
            "sharpe": float(sharpe(s1_returns)),
            "cagr": float(cagr(s1_eq)),
            "mdd": float(max_drawdown(s1_eq)),
        },
        "edge": {
            "sharpe": float(sharpe(meta_returns) - sharpe(s1_returns)),
            "mdd_delta_pp": float(
                (max_drawdown(meta_eq) - max_drawdown(s1_eq)) * 100.0
            ),
        },
        "wf_8fold": wfres,
        "bootstrap_999_ci": {"low": boot_low, "high": boot_high},
        "dsr": {
            "dsr": float(dsr_result.dsr),
            "p_value": float(dsr_result.p_value),
            "observed_sharpe": float(dsr_result.observed_sharpe),
            "n_trials": CUMULATIVE_N_TRIALS_PRIOR + 1,
        },
        "weight_concentration_high_share": weight_concentration,
        "annual_turnover": annual_turnover,
        "weights_returns_series": {
            "rebal_dates": [str(d.date()) for d in res.rebal_dates],
            "weights": weights_df.values.tolist() if len(weights_df) else [],
            "weight_columns": list(weights_df.columns),
            "meta_index": [str(d.date()) for d in meta_returns.index],
            "meta_returns": meta_returns.tolist(),
        },
    }


def _gate_decisions(by_dataset: dict[str, dict]) -> dict:
    sharpe_edges = [v["edge"]["sharpe"] for v in by_dataset.values()]
    mdd_deltas = [v["edge"]["mdd_delta_pp"] for v in by_dataset.values()]
    n_sharpe_pass = sum(1 for e in sharpe_edges if e >= 0.05)
    n_mdd_pass = sum(1 for d in mdd_deltas if d <= 3.0)

    wf_ratios = [v["wf_8fold"]["winners"] for v in by_dataset.values()]
    wf_min = min(wf_ratios) if wf_ratios else 0
    wf_pass = wf_min >= 6

    boot_lows = [v["bootstrap_999_ci"]["low"] for v in by_dataset.values()]
    boot_pass = all(low > 0 for low in boot_lows)

    dsr_ps = [v["dsr"]["p_value"] for v in by_dataset.values()]
    dsr_pass = all(p < 0.05 for p in dsr_ps)

    weight_conc = max(v["weight_concentration_high_share"] for v in by_dataset.values())
    turnover = max(v["annual_turnover"] for v in by_dataset.values())
    max_mdd_delta = max(mdd_deltas)
    max_sharpe_edge = max(sharpe_edges)

    kill_K2 = weight_conc > 0.80
    kill_K3 = turnover > 1.0 and max_sharpe_edge < 0.10
    kill_K4 = max_mdd_delta > 5.0
    any_kill = kill_K2 or kill_K3 or kill_K4

    return {
        "sharpe_edge_pass": n_sharpe_pass >= 2,
        "sharpe_edge_count": n_sharpe_pass,
        "mdd_delta_pass": n_mdd_pass >= 2,
        "mdd_delta_count": n_mdd_pass,
        "wf_pass": wf_pass,
        "wf_min_winners": int(wf_min),
        "bootstrap_pass": boot_pass,
        "dsr_pass": dsr_pass,
        "kill_K2_concentration": kill_K2,
        "kill_K3_turnover_no_edge": kill_K3,
        "kill_K4_mdd_blow": kill_K4,
        "any_kill_triggered": any_kill,
        "verdict": (
            "DEAD_END"
            if any_kill or n_sharpe_pass < 2
            else (
                "WINNER_CANDIDATE"
                if (n_sharpe_pass >= 2 and n_mdd_pass >= 2 and wf_pass and boot_pass and dsr_pass)
                else "PROMISING"
            )
        ),
    }


def main() -> None:
    by_dataset: dict[str, dict] = {}
    for ds in DATASETS:
        panel = _aligned_panel(ds)
        if len(panel) < 252 * 3:
            print(f"⚠️  {ds}: only {len(panel)} obs after intersection, skipping")
            continue
        by_dataset[ds] = _summarize_dataset(ds, panel)
        print(
            f"{ds}: meta Sharpe {by_dataset[ds]['meta']['sharpe']:.3f} | "
            f"S1 Sharpe {by_dataset[ds]['s1_incumbent']['sharpe']:.3f} | "
            f"edge {by_dataset[ds]['edge']['sharpe']:+.3f} | "
            f"WF {by_dataset[ds]['wf_8fold']['winners']}/{by_dataset[ds]['wf_8fold']['k']}"
        )

    gates = _gate_decisions(by_dataset)
    out = {
        "iter": 1,
        "iter_slug": "meta-wf-S1-S5-maxSharpe",
        "objective": "sharpe",
        "lookback_months": LOOKBACK_MONTHS,
        "max_weight": MAX_WEIGHT,
        "embargo_days": EMBARGO_DAYS,
        "sleeves": list(SLEEVES.keys()),
        "datasets_evaluated": list(by_dataset.keys()),
        "by_dataset": by_dataset,
        "gates": gates,
    }

    results_path = ITER_DIR / "results.json"
    with results_path.open("w") as f:
        json.dump(out, f, indent=2, default=str)

    verdict_path = ITER_DIR / "verdict.json"
    with verdict_path.open("w") as f:
        json.dump(
            {
                "iter": 1,
                "verdict": gates["verdict"],
                "gates": gates,
                "summary": {
                    ds: {
                        "meta_sharpe": v["meta"]["sharpe"],
                        "meta_cagr": v["meta"]["cagr"],
                        "meta_mdd": v["meta"]["mdd"],
                        "edge_sharpe": v["edge"]["sharpe"],
                        "edge_mdd_pp": v["edge"]["mdd_delta_pp"],
                    }
                    for ds, v in by_dataset.items()
                },
            },
            f,
            indent=2,
        )
    print(f"\nVERDICT: {gates['verdict']}")
    print(f"Sharpe edge ≥+0.05: {gates['sharpe_edge_count']}/3")
    print(f"MDD ≤ +3pp: {gates['mdd_delta_count']}/3")
    print(f"WF ≥6/8 min: {gates['wf_min_winners']}/8")
    print(f"Bootstrap 99.9% CI low > 0: {gates['bootstrap_pass']}")
    print(f"DSR p<0.05: {gates['dsr_pass']}")
    print(f"Any kill: {gates['any_kill_triggered']}")


if __name__ == "__main__":
    main()
