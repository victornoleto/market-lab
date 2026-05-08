"""Iter 025 — B.3: VXX real diagnostic on iter 011 (no-free-lunch quantification).

Replaces iter 022's synthetic tail-hedge model with REAL VXX (iPath VIX
Short-Term Futures ETN, BlackRock, 2009-01-30+) loaded from Tiingo cache.
Quantifies the gap between modeled (+5pp Sharpe artifact) and deployable
(-X Sharpe expected) under honest no-free-lunch constraints.

Pre-run sanity check: VXX standalone Sharpe = -0.738, CAGR = -51%/yr,
MDD = -100%. Asset is legitimate destroyer of capital — any portfolio
+signal must come from negative-correlation tail-hedge benefit (2009-Q1,
2020-Q1, 2022 corrections).

KILL #1 (no-free-lunch monotonic): Sharpe should decrease monotonically
as VXX % rises 2.5% → 10%. If Sharpe RISES with VXX %, there's a bug.
KILL #2 (decay): edge ≤ 0 vs iter 011 expected on ≥2/3 datasets.

Hypothesis: see ./hypothesis.md.
Mission NEW: gross-of-tax Sharpe edge ≥0.05 vs SPY on ≥2/3 — UNLIKELY here.

Citations:
- Capital-efficient stacking: [risk_parity, ch.5, p.10]
- Tail-hedge convex thesis: Spitznagel _Safe Haven_ (2021); Universa real
  implementation reports +1-2pp CAGR over 60/40 — not Sharpe miracle.
- No-free-lunch / monotonic check: [advances_fin_ml, p.208-211]
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).parents[4]
sys.path.insert(0, str(REPO_ROOT))

from ai_trade.backtest.metrics.performance import cagr, max_drawdown, sharpe
from ai_trade.backtest.validation.dsr import dsr as compute_dsr
from ai_trade.backtest.validation.dsr import psr as compute_psr
from ai_trade.backtest.validation.pbo import pbo
from ai_trade.backtest.validation.walk_forward import walk_forward_splits


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SHARED = REPO_ROOT / "studies" / "_shared"
LOOP = REPO_ROOT / "studies" / "long_term_portfolio"
AnnualDarfEngine = _load_module("iter025_tax_engine", SHARED / "tax_engine.py").AnnualDarfEngine
_scoring = _load_module("iter025_scoring", LOOP / "scoring.py")
_datasets_mod = _load_module("iter025_datasets", LOOP / "datasets.py")
_proxies = _load_module("iter025_proxies", LOOP / "proxies.py")
DatasetMetrics = _scoring.DatasetMetrics
Gates = _scoring.Gates
BENCHMARKS = _scoring.BENCHMARKS
spy_benchmark = _scoring.spy_benchmark
avg_benchmark = _scoring.avg_benchmark
legacy_benchmarks = _scoring.legacy_benchmarks
score_strategy = _scoring.score_strategy
load_prices_base = _datasets_mod.load_prices
DATASETS_META = _datasets_mod.DATASETS
expand_capital_efficient = _proxies.expand_capital_efficient
PROXY_LEGS = _proxies.PROXY_LEGS

ITER_DIR = Path(__file__).parent
N_CONFIGS = 4
BOOTSTRAP_N = 2000
WF_N_WINDOWS = 8
CUMULATIVE_N_TRIALS_PRIOR = 90  # iter 024's cumulative

DATASETS = ["lh_56y", "vt_real", "ndx_real"]


def _load_vxx_curve() -> pd.Series:
    """Load VXX adj_close as 'VXX_REAL' Tiingo ETF.

    VXX inception 2009-01-30 (iPath Series B S&P 500 VIX Short-Term Futures ETN,
    BlackRock). Pre-2009 rows are NaN — loose convention treats those as 0-weight
    when summing.
    """
    path = REPO_ROOT / "data" / "tiingo" / "daily" / "prices" / "VXX.parquet"
    df = pd.read_parquet(path)
    s = df["adj_close"].rename("VXX_REAL")
    return s


_VXX_CURVE = _load_vxx_curve()


def load_prices(name: str) -> pd.DataFrame:
    df = load_prices_base(name).copy()
    vxx = _VXX_CURVE.reindex(df.index).ffill()  # ffill within data range; NaN pre-inception
    df["VXX_REAL"] = vxx
    return df


# 4 configs: VXX 2.5% / 5% / 7.5% / 10%, substituted from KMLM. Iter 011 base.
CONFIGS: dict[str, dict[str, float]] = {
    "vxx_lite_3525_375_25":     {"NTSX_PROXY": 0.35, "GDESIM": 0.25, "KMLMSIM": 0.375, "VXX_REAL": 0.025},
    "vxx_mod_3525_35_5":        {"NTSX_PROXY": 0.35, "GDESIM": 0.25, "KMLMSIM": 0.35,  "VXX_REAL": 0.05},
    "vxx_balanced_3525_325_75": {"NTSX_PROXY": 0.35, "GDESIM": 0.25, "KMLMSIM": 0.325, "VXX_REAL": 0.075},
    "vxx_heavy_3525_30_10":     {"NTSX_PROXY": 0.35, "GDESIM": 0.25, "KMLMSIM": 0.30,  "VXX_REAL": 0.10},
}

CONFIG_TYPE = {cfg: f"VXX_{w['VXX_REAL']*100:.1f}pct" for cfg, w in CONFIGS.items()}

EFF_CONFIGS = {cfg: expand_capital_efficient(weights) for cfg, weights in CONFIGS.items()}


def compute_equity(returns: pd.Series, start: float = 10_000.0) -> pd.Series:
    return (1.0 + returns).cumprod() * start


def gross_returns(prices: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    tickers = [t for t in weights if t in prices.columns]
    px = prices[tickers].ffill().dropna(how="all")
    rets = px.pct_change()
    w = pd.Series({t: weights[t] for t in tickers}, dtype=float)
    return (rets * w).sum(axis=1).dropna().iloc[1:]


def gross_returns_strict(prices: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    tickers = [t for t in weights if t in prices.columns]
    px = prices[tickers].dropna(how="any")
    rets = px.pct_change().dropna()
    w = pd.Series({t: weights[t] for t in tickers}, dtype=float)
    return (rets * w).sum(axis=1)


def net_returns_annual_darf(gross: pd.Series, weights: dict[str, float]) -> tuple[pd.Series, dict]:
    engine = AnnualDarfEngine(initial_investment=10_000.0)
    prev_value = engine.port_value
    prev_weights = {k: 0.0 for k in weights}
    curr_weights = dict(weights)
    net: list[float] = []
    last_year: int | None = None

    for i, (date, ret) in enumerate(gross.items()):
        if i == 0:
            engine.record_trade(date, prev_weights, curr_weights)
            prev_weights = curr_weights
        if last_year is not None and date.year != last_year:
            engine.year_end_settlement(last_year)
        last_year = date.year
        engine.apply_return(float(ret))
        net.append(engine.port_value / prev_value - 1.0)
        prev_value = engine.port_value

    if last_year is not None:
        engine.year_end_settlement(last_year, force=True)
        if net:
            final_value = engine.port_value
            net[-1] = (1.0 + net[-1]) * (final_value / prev_value) - 1.0
    return pd.Series(net, index=gross.index, name="net_returns"), engine.summary() | {"events": engine.events}


def metrics_from_returns(returns: pd.Series) -> dict[str, float]:
    eq = compute_equity(returns)
    return {
        "sharpe": float(sharpe(returns, periods_per_year=252)),
        "cagr":   float(cagr(eq, periods_per_year=252)),
        "mdd":    float(max_drawdown(eq)),
    }


def numpy_returns(prices: pd.DataFrame, weights: dict[str, float]) -> np.ndarray:
    tickers = [t for t in weights if t in prices.columns]
    px_df = prices[tickers].ffill()
    px_df = px_df.dropna(how="any")
    px = px_df.to_numpy(dtype=float)
    if len(px) < 2:
        return np.array([], dtype=float)
    w = np.array([weights[t] for t in tickers], dtype=float)
    daily = np.diff(px, axis=0) / px[:-1]
    return (daily * w).sum(axis=1)


def gate_dsr(returns: pd.Series) -> tuple[bool, float]:
    if N_CONFIGS < 2:
        p_value = 1.0 - compute_psr(returns.values, benchmark=0.0)
    else:
        p_value = compute_dsr(returns.values, n_trials=N_CONFIGS).p_value
    return p_value < 0.05, float(p_value)


def gate_walk_forward(returns: pd.Series) -> tuple[bool, list[float], list[float]]:
    n = len(returns)
    window = n // (WF_N_WINDOWS + 1)
    if window < 63:
        return False, [], []
    oos_returns: list[float] = []
    oos_mdds: list[float] = []
    for _, test_range in walk_forward_splits(n, window, window, window):
        idx = list(test_range)
        r = returns.iloc[idx]
        oos_returns.append(float((1.0 + r).prod() - 1.0))
        oos_mdds.append(float(max_drawdown(compute_equity(r))))
        if len(oos_returns) >= WF_N_WINDOWS:
            break
    passed = (
        len(oos_returns) == WF_N_WINDOWS
        and sum(x > 0 for x in oos_returns) >= 6
        and all(x <= 0.25 for x in oos_mdds)
    )
    return passed, oos_returns, oos_mdds


def gate_oos_70_30(returns: pd.Series) -> tuple[bool, float]:
    oos = returns.iloc[int(len(returns) * 0.70):]
    s = float(sharpe(oos, periods_per_year=252)) if len(oos) >= 63 else 0.0
    return s > 0, s


def gate_fwd(returns: pd.Series) -> tuple[bool, float]:
    fwd = returns[returns.index >= "2020-01-01"]
    s = float(sharpe(fwd, periods_per_year=252)) if len(fwd) >= 63 else 0.0
    return s > 0, s


def gate_bootstrap(returns: pd.Series) -> tuple[bool, float]:
    arr = returns.to_numpy(dtype=float)
    if len(arr) < 252:
        return False, 0.0
    rng = np.random.default_rng(42)
    block = 21
    n_blocks = len(arr) // block
    sharpes: list[float] = []
    for _ in range(BOOTSTRAP_N):
        starts = rng.integers(0, len(arr) - block + 1, size=n_blocks)
        sample = np.concatenate([arr[s:s + block] for s in starts])[:len(arr)]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            sharpes.append(float(sample.mean() / sigma * np.sqrt(252)))
    ci_low = float(np.percentile(sharpes, 0.1)) if sharpes else 0.0
    return ci_low > 0, ci_low


def rolling_robustness(returns: pd.Series) -> tuple[int, float, int, list[float]]:
    sharpes: list[float] = []
    window = 252 * 5
    for start in range(0, len(returns) - window + 1, 252):
        sample = returns.iloc[start:start + window]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            sharpes.append(float(sample.mean() / sigma * np.sqrt(252)))
    pct_pos = sum(s > 0 for s in sharpes) / len(sharpes) if sharpes else 0.0
    pts = 5 if pct_pos >= 0.90 else 3 if pct_pos >= 0.75 else 1 if pct_pos >= 0.60 else 0
    return pts, pct_pos, len(sharpes), sharpes


def run_dataset(ds: str) -> dict:
    prices_full = load_prices(ds)
    needed_legs = sorted(set().union(*[set(w) for w in EFF_CONFIGS.values()]))
    needed = sorted(set(needed_legs + ["VTSIM", "QQQSIM", "SPYSIM"]).intersection(prices_full.columns))
    prices = prices_full[needed].dropna(how="all").ffill()

    configs: dict[str, dict] = {}
    aligned_gross: list[pd.Series] = []
    for cfg_id, weights in EFF_CONFIGS.items():
        gross = gross_returns(prices, weights)
        gross_strict = gross_returns_strict(prices_full[needed].dropna(how="all"), weights)
        net, tax = net_returns_annual_darf(gross, weights)
        configs[cfg_id] = {
            "gross_metrics":         metrics_from_returns(gross),
            "gross_metrics_strict":  metrics_from_returns(gross_strict) if len(gross_strict) > 0 else None,
            "strict_window": {
                "start": str(gross_strict.index[0].date()) if len(gross_strict) > 0 else None,
                "end":   str(gross_strict.index[-1].date()) if len(gross_strict) > 0 else None,
                "n":     int(len(gross_strict)),
            },
            "loose_window": {
                "start": str(gross.index[0].date()) if len(gross) > 0 else None,
                "end":   str(gross.index[-1].date()) if len(gross) > 0 else None,
                "n":     int(len(gross)),
            },
            "net_metrics":   metrics_from_returns(net),
            "tax": tax,
            "gross_returns": gross,
            "net_returns":   net,
        }
        aligned_gross.append(gross.rename(cfg_id))

    matrix_df = pd.concat(aligned_gross, axis=1).dropna()
    pbo_result = pbo(matrix_df.to_numpy(dtype=float), n_blocks=10)
    g1_pass = pbo_result.pbo < 0.5
    return {
        "dataset": ds,
        "prices":  prices,
        "configs": configs,
        "pbo": {"pbo": float(pbo_result.pbo), "n_combinations": pbo_result.n_combinations, "pass": g1_pass},
    }


def gate_selected(ds_result: dict, cfg_id: str) -> dict:
    prices = ds_result["prices"]
    weights = EFF_CONFIGS[cfg_id]
    gross = ds_result["configs"][cfg_id]["gross_returns"]
    metrics = ds_result["configs"][cfg_id]["gross_metrics"]

    g2, pval = gate_dsr(gross)
    g3, wf_returns, wf_mdds = gate_walk_forward(gross)
    g4, oos_s = gate_oos_70_30(gross)
    g5, fwd_s = gate_fwd(gross)
    g6, ci_low = gate_bootstrap(gross)
    np_rets = numpy_returns(prices, weights)
    np_eq = (1.0 + np_rets).cumprod() * 10_000.0
    np_cagr = (
        float((np_eq[-1] / np_eq[0]) ** (252 / (len(np_rets) - 1)) - 1.0)
        if len(np_rets) > 252
        else 0.0
    )
    g7 = abs(np_cagr - metrics["cagr"]) * 100 <= 3.0
    gates = {
        "g1_pbo":       ds_result["pbo"]["pass"],
        "g2_dsr":       g2,
        "g3_wf":        g3,
        "g4_oos":       g4,
        "g5_fwd":       g5,
        "g6_bootstrap": g6,
        "g7_crosslib":  g7,
    }
    return {
        "gates": gates | {"n_passed": sum(gates.values())},
        "gate_details": {
            "g1_pbo":         ds_result["pbo"]["pbo"],
            "g2_dsr_p":       pval,
            "g3_wf_returns":  wf_returns,
            "g3_wf_mdds":     wf_mdds,
            "g3_max_wf_mdd":  max(wf_mdds) if wf_mdds else 0.0,
            "g4_oos_sharpe":  oos_s,
            "g5_fwd_sharpe":  fwd_s,
            "g6_ci_low":      ci_low,
            "g7_np_cagr":     np_cagr,
        },
    }


def main() -> None:
    print(f"VXX inception: {_VXX_CURVE.dropna().index[0].date()}")
    print(f"VXX standalone metrics (no-free-lunch sanity check):")
    vxx_rets = _VXX_CURVE.dropna().pct_change().dropna()
    vxx_sharpe_alone = float(vxx_rets.mean() / vxx_rets.std() * np.sqrt(252))
    vxx_cagr_alone = float((_VXX_CURVE.dropna().iloc[-1] / _VXX_CURVE.dropna().iloc[0])
                           ** (252 / len(vxx_rets)) - 1)
    vxx_eq = (_VXX_CURVE.dropna() / _VXX_CURVE.dropna().cummax())
    vxx_mdd_alone = float((vxx_eq - 1).min())
    print(f"  Sharpe = {vxx_sharpe_alone:.3f}, CAGR = {vxx_cagr_alone:.2%}, MDD = {vxx_mdd_alone:.2%}")
    if vxx_sharpe_alone >= 0:
        raise RuntimeError(f"NO-FREE-LUNCH VIOLATION: VXX standalone Sharpe {vxx_sharpe_alone:.3f} >= 0; expected negative.")

    all_results = {ds: run_dataset(ds) for ds in DATASETS}
    spy_bms = {ds: spy_benchmark(BENCHMARKS[ds]) for ds in DATASETS}
    avg_bms = {ds: avg_benchmark(BENCHMARKS[ds]) for ds in DATASETS}

    selection_scores: dict[str, float] = {}
    for cfg_id in CONFIGS:
        vals = [
            all_results[ds]["configs"][cfg_id]["gross_metrics"]["sharpe"] / spy_bms[ds].sharpe
            for ds in DATASETS
        ]
        selection_scores[cfg_id] = float(np.mean(vals))
    selected_cfg = max(selection_scores, key=selection_scores.get)

    metrics_map: dict[str, DatasetMetrics] = {}
    gates_map: dict[str, Gates] = {}
    datasets_out: dict[str, dict] = {}
    returns_series: dict[str, dict] = {}
    for ds in DATASETS:
        gated = gate_selected(all_results[ds], selected_cfg)
        gm = all_results[ds]["configs"][selected_cfg]["gross_metrics"]
        nm = all_results[ds]["configs"][selected_cfg]["net_metrics"]
        gd = gated["gate_details"]
        g = gated["gates"]
        metrics_map[ds] = DatasetMetrics(
            sharpe=gm["sharpe"], cagr=gm["cagr"], mdd=gm["mdd"],
            dsr_p_value=gd["g2_dsr_p"],
            net_sharpe=nm["sharpe"], net_cagr=nm["cagr"], net_mdd=nm["mdd"],
        )
        gates_map[ds] = Gates(g["g1_pbo"], g["g2_dsr"], g["g3_wf"], g["g4_oos"], g["g5_fwd"], g["g6_bootstrap"], g["g7_crosslib"])
        top_cfgs = sorted(
            all_results[ds]["configs"],
            key=lambda c: all_results[ds]["configs"][c]["gross_metrics"]["sharpe"],
            reverse=True,
        )[:5]
        datasets_out[ds] = {
            "selected_config": selected_cfg,
            "selection_scores": selection_scores,
            "configs": {
                c: {
                    "gross_metrics":        all_results[ds]["configs"][c]["gross_metrics"],
                    "gross_metrics_strict": all_results[ds]["configs"][c]["gross_metrics_strict"],
                    "strict_window":        all_results[ds]["configs"][c]["strict_window"],
                    "loose_window":         all_results[ds]["configs"][c]["loose_window"],
                    "net_metrics":          all_results[ds]["configs"][c]["net_metrics"],
                    "config_type":          CONFIG_TYPE[c],
                }
                for c in CONFIGS
            },
            "top5_by_sharpe": top_cfgs,
            "selected": {
                "gross_metrics": gm,
                "net_metrics":   nm,
                **gated,
                "tax": all_results[ds]["configs"][selected_cfg]["tax"],
            },
            "pbo": all_results[ds]["pbo"],
        }
        returns_series[ds] = {}
        for c in set([selected_cfg, top_cfgs[0]]):
            gr = all_results[ds]["configs"][c]["gross_returns"]
            nr = all_results[ds]["configs"][c]["net_returns"]
            returns_series[ds][c] = {
                "index":         [str(d.date()) for d in gr.index],
                "gross_returns": gr.tolist(),
                "net_returns":   nr.tolist(),
            }

    rob_pts, pct_pos, n_roll, roll_sharpes = rolling_robustness(
        all_results["lh_56y"]["configs"][selected_cfg]["gross_returns"]
    )
    score = score_strategy(
        metrics_map, gates_map,
        cumulative_n_trials=CUMULATIVE_N_TRIALS_PRIOR + N_CONFIGS,
        robustness_bonus=rob_pts,
    )
    score_legacy = score_strategy(
        metrics_map, gates_map,
        cumulative_n_trials=CUMULATIVE_N_TRIALS_PRIOR + N_CONFIGS,
        benchmarks=legacy_benchmarks(),
        robustness_bonus=rob_pts,
    )

    verdict = score.to_dict()
    verdict.update({
        "status":           score.tier.value.lower(),
        "configs_tested":   N_CONFIGS,
        "primary_citation": "Spitznagel Safe Haven (2021)",
        "hypothesis_slug":  "iter011-VXX-real-diagnostic",
        "selected_config":  selected_cfg,
        "selected_config_type": CONFIG_TYPE[selected_cfg],
        "selection_rule":   "NEW (2026-04-29 reframing): max mean(gross_Sharpe / SPY_Sharpe) across 3 datasets",
        "scoring_basis":    "NEW SPY-only +0.05 (mandate reframing 2026-04-29)",
        "score_legacy":     score_legacy.to_dict(),
        "vxx_standalone": {
            "sharpe": vxx_sharpe_alone,
            "cagr":   vxx_cagr_alone,
            "mdd":    vxx_mdd_alone,
            "inception": str(_VXX_CURVE.dropna().index[0].date()),
        },
        "net_metrics": {
            ds: {
                "sharpe": all_results[ds]["configs"][selected_cfg]["net_metrics"]["sharpe"],
                "cagr":   all_results[ds]["configs"][selected_cfg]["net_metrics"]["cagr"],
                "mdd":    all_results[ds]["configs"][selected_cfg]["net_metrics"]["mdd"],
            }
            for ds in DATASETS
        },
        "robustness": {
            "bonus_pts":            rob_pts,
            "pct_positive_sharpe":  pct_pos,
            "n_windows":            n_roll,
            "min_rolling_sharpe":   float(min(roll_sharpes)) if roll_sharpes else None,
            "max_rolling_sharpe":   float(max(roll_sharpes)) if roll_sharpes else None,
        },
    })

    def default(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return str(obj)

    (ITER_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2, default=default) + "\n")
    runs = {
        ds: {
            cfg_id: {
                "sharpe":        all_results[ds]["configs"][cfg_id]["gross_metrics"]["sharpe"],
                "cagr":          all_results[ds]["configs"][cfg_id]["gross_metrics"]["cagr"],
                "mdd":           all_results[ds]["configs"][cfg_id]["gross_metrics"]["mdd"],
                "sharpe_strict": (
                    all_results[ds]["configs"][cfg_id]["gross_metrics_strict"]["sharpe"]
                    if all_results[ds]["configs"][cfg_id]["gross_metrics_strict"]
                    else None
                ),
                "net_sharpe":    all_results[ds]["configs"][cfg_id]["net_metrics"]["sharpe"],
                "net_cagr":      all_results[ds]["configs"][cfg_id]["net_metrics"]["cagr"],
                "net_mdd":       all_results[ds]["configs"][cfg_id]["net_metrics"]["mdd"],
                "config_type":   CONFIG_TYPE[cfg_id],
            }
            for cfg_id in CONFIGS
        }
        for ds in DATASETS
    }

    (ITER_DIR / "results.json").write_text(json.dumps({
        "hypothesis_slug": "iter011-VXX-real-diagnostic",
        "selected_config": selected_cfg,
        "configs_tested":  N_CONFIGS,
        "configs":         CONFIGS,
        "config_type":     CONFIG_TYPE,
        "eff_configs":     EFF_CONFIGS,
        "proxy_legs":      PROXY_LEGS,
        "runs":            runs,
        "datasets":        datasets_out,
        "returns_series":  returns_series,
    }, indent=2, default=default) + "\n")

    print(f"\nSelected: {selected_cfg} ({CONFIG_TYPE[selected_cfg]})")
    print("--- Per-dataset metrics (under NEW SPY-only baseline) ---")
    for ds in DATASETS:
        m = metrics_map[ds]
        spy_b = spy_bms[ds]
        avg_b = avg_bms[ds]
        spy_edge = m.sharpe - spy_b.sharpe
        avg_edge = m.sharpe - avg_b.sharpe
        cfg_data = all_results[ds]["configs"][selected_cfg]
        strict_s = cfg_data["gross_metrics_strict"]["sharpe"] if cfg_data["gross_metrics_strict"] else None
        strict_str = f" [strict={strict_s:.3f}]" if strict_s is not None else ""
        print(
            f"{ds}: gross S={m.sharpe:.3f}{strict_str} "
            f"(SPY={spy_b.sharpe:.3f} edge={spy_edge:+.3f}) "
            f"(avg={avg_b.sharpe:.3f} edge={avg_edge:+.3f}) "
            f"CAGR={m.cagr:.2%} MDD={m.mdd:.2%} gates={gates_map[ds].n_passed}/7 "
            f"DSRp={m.dsr_p_value:.2e} | net S={m.net_sharpe:.3f}"
        )
    print(f"NEW    Tier={score.tier.value} Score={score.total_score}/100 Winner={score.winner_conditions_met}")
    print(f"LEGACY Tier={score_legacy.tier.value} Score={score_legacy.total_score}/100 Winner={score_legacy.winner_conditions_met}")

    print("\n--- Full grid (gross Sharpe per config × dataset) — KILL #1 monotonic check ---")
    print(f"{'config':<32} {'VXX%':<6} {'lh_56y':>8} {'vt_real':>8} {'ndx_real':>9}")
    for cfg in CONFIGS:
        s_lh = all_results["lh_56y"]["configs"][cfg]["gross_metrics"]["sharpe"]
        s_vt = all_results["vt_real"]["configs"][cfg]["gross_metrics"]["sharpe"]
        s_nd = all_results["ndx_real"]["configs"][cfg]["gross_metrics"]["sharpe"]
        print(f"{cfg:<32} {CONFIG_TYPE[cfg]:<6} {s_lh:>8.3f} {s_vt:>8.3f} {s_nd:>9.3f}")

    # KILL #1 explicit monotonic check
    print("\n--- KILL #1 (no-free-lunch monotonic): Sharpe must NOT rise with VXX% ---")
    for ds in DATASETS:
        sharpes = [all_results[ds]["configs"][c]["gross_metrics"]["sharpe"] for c in CONFIGS]
        diffs = [sharpes[i+1] - sharpes[i] for i in range(len(sharpes)-1)]
        all_decreasing = all(d <= 0.005 for d in diffs)  # tolerance 0.005
        if all_decreasing:
            print(f"  {ds}: monotonic decrease ✓ (diffs: {[f'{d:+.3f}' for d in diffs]})")
        else:
            print(f"  {ds}: NON-monotonic ⚠️ (diffs: {[f'{d:+.3f}' for d in diffs]})")


if __name__ == "__main__":
    main()
