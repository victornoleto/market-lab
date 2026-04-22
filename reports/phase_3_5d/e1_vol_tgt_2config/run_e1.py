"""
E1 — Vol-targeting with JUST 2 diverse configs (Phase 3.5e arbitration, iter 13).

Hypothesis: vol15_lk20 (D5 best, SN=0.855✓, FWD=0.182✓) alongside ONE structurally
different config (sma200_gld_binary) might produce PBO < 0.5 if vol15_lk20 is the
dominant IS-winner across CSCV folds.

Background:
  D5 (7 configs, all vol-targeting family): PBO=0.599 ✗
  D5b (3 diverse configs): PBO=0.651 ✗ — IS-winner flips by regime
  D8 insight: binary D2-style sma200_gld configs show PBO=0.115 in isolation.
  With 2 configs, PBO depends on whether vol15_lk20 dominates in all CSCV fold types.

Configs:
  vol15_lk20:      continuous vol-targeting, target=15%, lookback=20d
                   [advances_fin_ml, ch.14], [volatility_trading]
  sma200_gld_binary: binary SPY SMA200, 100% TQQQ when SPY>SMA200, else 100% GLD
                   [leverage_for_the_long_run, p.13]

Window: 2004-11-18 → 2026-04-15 (~21.4yr, longest TQQQ+GLD+SPY common window)
Off-leg: GLD (TMF eliminated D2, cash suboptimal)
PBO gate: < 0.5 [advances_fin_ml, p.208-211]
DSR gate: p < 0.05 [advances_fin_ml, p.298-299]
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, "/var/www/pessoal/ai-trade")
sys.path.insert(0, "/var/www/pessoal/ai-trade/src")

from ai_trade.backtest.validation.pbo import pbo as compute_pbo_cscv
from ai_trade.backtest.validation.dsr import dsr as compute_dsr

REPORT_DIR = "reports/phase_3_5d/e1_vol_tgt_2config"
PARQUET_PATH = "reports/phase_3_5c/cross_lib/data/reference_prices.parquet"
WINDOW_START = "2004-11-18"
WINDOW_END = "2026-04-15"
TAX_RATE = 0.15
ITER_NUM = 13
SMA200_PERIOD = 200


# ─── Signals ─────────────────────────────────────────────────────────────────

def vol_target_weight(prices: pd.Series, target_vol: float, lookback: int) -> pd.Series:
    """[advances_fin_ml, ch.14], [volatility_trading]"""
    daily_ret = prices.pct_change()
    realized_vol = daily_ret.rolling(lookback, min_periods=lookback).std() * np.sqrt(252)
    realized_vol = realized_vol.replace(0, np.nan)
    weight = (target_vol / realized_vol).clip(upper=1.0)
    return weight.fillna(0.0)


def sma200_binary_weight(spy_prices: pd.Series) -> pd.Series:
    """Binary 0/1 weight: 1 when SPY > SMA200, 0 otherwise. [leverage_for_the_long_run, p.13]"""
    sma = spy_prices.rolling(SMA200_PERIOD, min_periods=SMA200_PERIOD).mean()
    mask = (spy_prices > sma).astype(float)
    mask = mask.where(sma.notna(), other=0.0)
    return mask


# ─── Portfolio backtest ───────────────────────────────────────────────────────

def run_portfolio(prices: pd.DataFrame, config_name: str) -> tuple[pd.Series, pd.Series]:
    """Returns (daily_returns, weight_series). Signal shifted 1 bar to avoid lookahead."""
    if config_name == "vol15_lk20":
        w = vol_target_weight(prices["TQQQ"], target_vol=0.15, lookback=20)
    elif config_name == "sma200_gld_binary":
        w = sma200_binary_weight(prices["SPY"])
    else:
        raise ValueError(f"Unknown config: {config_name}")

    w_exec = w.shift(1).fillna(0.0)
    ret_tqqq = prices["TQQQ"].pct_change()
    ret_gld = prices["GLD"].pct_change()
    port = w_exec * ret_tqqq + (1.0 - w_exec) * ret_gld
    return port.dropna(), w_exec.reindex(port.index).fillna(0.0)


def run_portfolio_bt(prices: pd.DataFrame, config_name: str) -> pd.Series | None:
    """Cross-lib concordance via bt library."""
    try:
        import bt  # type: ignore

        if config_name == "vol15_lk20":
            w = vol_target_weight(prices["TQQQ"], target_vol=0.15, lookback=20)
        else:
            w = sma200_binary_weight(prices["SPY"])

        w_exec = w.shift(1).fillna(0.0)
        weights = pd.DataFrame(0.0, index=prices.index, columns=["TQQQ", "GLD"])
        weights["TQQQ"] = w_exec
        weights["GLD"] = 1.0 - w_exec

        strat = bt.Strategy(
            config_name,
            [bt.algos.RunDaily(), bt.algos.WeighTarget(weights), bt.algos.Rebalance()],
        )
        result = bt.run(bt.Backtest(strat, prices[["TQQQ", "GLD"]].copy()))
        equity = result.prices[config_name].rename("equity")
        return equity
    except Exception as e:
        print(f"  [bt] {config_name} error: {e}", file=sys.stderr)
        return None


# ─── Metrics ─────────────────────────────────────────────────────────────────

def compute_cagr(returns: pd.Series) -> float:
    equity = (1 + returns).cumprod()
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    return float("nan") if years < 0.5 else float(equity.iloc[-1] ** (1 / years) - 1)


def compute_sharpe(returns: pd.Series) -> float:
    if returns.std() < 1e-12 or len(returns) < 30:
        return float("nan")
    return float(returns.mean() / returns.std() * np.sqrt(252))


def compute_max_dd(returns: pd.Series) -> float:
    equity = (1 + returns).cumprod()
    running_max = equity.expanding().max()
    return float(((equity - running_max) / running_max).min())


def compute_calmar(cagr: float, max_dd: float) -> float:
    return float("nan") if max_dd == 0 or not np.isfinite(max_dd) else float(cagr / abs(max_dd))


def compute_wf(returns: pd.Series, n_splits: int = 8) -> tuple[list[float], int]:
    """Walk-forward: count splits with positive Sharpe. [AFML ch.12]"""
    n = len(returns)
    if n < n_splits * 63:
        return [], 0
    split_size = n // n_splits
    sharpes = [
        compute_sharpe(returns.iloc[i * split_size : (i + 1) * split_size])
        for i in range(n_splits)
    ]
    positive = sum(1 for s in sharpes if np.isfinite(s) and s > 0)
    return sharpes, positive


def compute_oos_holdout(returns: pd.Series) -> dict:
    """Single-block OOS: last 20% reserved. Gate: OOS Sharpe >= 0.5 × IS."""
    n = len(returns)
    split = int(n * 0.8)
    is_ret, oos_ret = returns.iloc[:split], returns.iloc[split:]
    is_s, oos_s = compute_sharpe(is_ret), compute_sharpe(oos_ret)
    return {
        "is_sharpe": float(is_s),
        "oos_sharpe": float(oos_s),
        "oos_pass": bool(np.isfinite(oos_s) and np.isfinite(is_s) and oos_s >= 0.5 * is_s),
        "is_start": str(returns.index[0].date()),
        "is_end": str(returns.index[split - 1].date()),
        "oos_start": str(returns.index[split].date()),
        "oos_end": str(returns.index[-1].date()),
    }


def compute_fwd_stress(returns: pd.Series) -> dict:
    """Forward-window stress: last 63 trading days (~1 quarter). Gate: Sharpe > 0."""
    fwd = returns.iloc[-63:]
    fwd_s = compute_sharpe(fwd)
    return {
        "fwd_sharpe": float(fwd_s),
        "fwd_pass": bool(np.isfinite(fwd_s) and fwd_s > 0),
        "fwd_start": str(fwd.index[0].date()),
        "fwd_end": str(fwd.index[-1].date()),
    }


# ─── Gates ───────────────────────────────────────────────────────────────────

def compute_pbo_gate(all_returns: dict[str, pd.Series]) -> dict:
    """PBO with n_blocks=10. [advances_fin_ml, p.208-211]"""
    names = list(all_returns)
    combined = pd.concat([all_returns[n].rename(n) for n in names], axis=1).dropna()
    if combined.shape[1] < 2 or len(combined) < 100:
        return {"pbo": float("nan"), "pass": None, "note": "insufficient data"}
    result = compute_pbo_cscv(combined.values, n_blocks=10)
    pbo_val = float(result.pbo)
    return {"pbo": pbo_val, "n_combinations": result.n_combinations, "pass": bool(pbo_val < 0.5)}


def compute_dsr_gate(port: pd.Series, n_configs: int) -> dict:
    """Deflated Sharpe. [advances_fin_ml, p.298-299]"""
    try:
        result = compute_dsr(port.values, n_trials=max(n_configs, 2))
        return {
            "dsr": float(result.dsr),
            "p_value": float(result.p_value),
            "pass": bool(result.p_value < 0.05),
        }
    except Exception as e:
        return {"dsr": float("nan"), "p_value": float("nan"), "pass": False, "error": str(e)}


def gate_summary(r: dict, pbo: dict, dsr: dict, spy_cagr_net: float) -> dict:
    m = r.get("metrics_is", {})
    wf = r.get("wf", {})
    oos = r.get("oos", {})
    fwd = r.get("fwd", {})

    g1 = bool(pbo.get("pass", False))
    g2 = bool(dsr.get("pass", False))
    g3 = bool(wf.get("pass", False))
    g4 = bool(oos.get("oos_pass", False))
    g5 = bool(fwd.get("fwd_pass", False))

    cagr_net = m.get("cagr_net", 0.0)
    calmar = m.get("calmar", 0.0)
    sharpe_net = m.get("sharpe_net", 0.0)

    e1 = bool(np.isfinite(cagr_net) and cagr_net > spy_cagr_net)
    e2 = bool(np.isfinite(calmar) and calmar > 0.5)
    e3 = bool(np.isfinite(sharpe_net) and sharpe_net > 0.8)

    all_pass = g1 and g2 and g3 and g4 and g5 and e1 and e2 and e3
    fail_parts = [n for n, ok in [
        ("PBO", g1), ("DSR", g2), ("WF", g3), ("OOS", g4), ("FWD", g5),
        ("SPY_BEAT", e1), ("CALMAR", e2), ("SHARPE_NET", e3)
    ] if not ok]

    return {
        "gate1_pbo": g1, "gate2_dsr": g2, "gate3_wf": g3,
        "gate4_oos": g4, "gate5_fwd": g5,
        "eco1_beats_spy": e1, "eco2_calmar": e2, "eco3_sharpe_net": e3,
        "ALL_PASS": all_pass,
        "fail_reason": "PASS" if all_pass else ", ".join(fail_parts),
    }


# ─── I/O ─────────────────────────────────────────────────────────────────────

def atomic_write_json(path: str, data: dict) -> None:
    tmp = path + f".tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, sort_keys=False, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    print(f"  Wrote {path}")


def write_report_md(path: str, results: list[dict], pbo: dict,
                    window: dict, spy_cagr_net: float) -> None:
    any_pass = any(r.get("gates", {}).get("ALL_PASS", False) for r in results)
    best = max(
        (r for r in results if "metrics_is" in r),
        key=lambda r: r["metrics_is"].get("sharpe", -999), default=None
    )

    lines = [
        f"# E1 Vol-targeting 2-config — TQQQ+GLD (iter {ITER_NUM}) [SWING BROKER]",
        "",
        "**Hypothesis:** vol15_lk20 (SN=0.855✓, FWD=0.182✓) + sma200_gld_binary as ONE",
        "  structurally different config → PBO might drop below 0.5 with only 2 configs.",
        f"**Window:** {window['start']} → {window['end']} ({window['years']:.1f}yr)",
        f"**Best config:** `{best['name'] if best else 'N/A'}` —"
        f" **{'✓ ALL PASS' if any_pass else 'NO PASS'}**",
        f"**PBO (2 configs):** {pbo.get('pbo', float('nan')):.3f}"
        f" ({'✓ PASS' if pbo.get('pass') else '✗ FAIL'})",
        "",
        "Citations: [advances_fin_ml, ch.14], [volatility_trading],",
        "  [leverage_for_the_long_run, p.13], [advances_fin_ml, p.208-211, p.298-299]",
        "",
        "## Results",
        "",
        "| Config | CAGR% | CAGR_net% | Sharpe | SN | MaxDD% | Calmar |"
        " WF | OOS_S | FWD_S | PBO | DSR_p | Beat_SPY | Cal>0.5 | SN>0.8 | PASS |",
        "|--------|-------|-----------|--------|----|--------|--------|"
        "----|-------|-------|-----|-------|----------|---------|--------|------|",
    ]

    for r in results:
        if "error" in r:
            lines.append(f"| {r['name']} | ERROR | — | — | — | — | — | — | — | — | — | — | — | — | — | ✗ |")
            continue
        m = r.get("metrics_is", {})
        wf = r.get("wf", {})
        oos = r.get("oos", {})
        fwd = r.get("fwd", {})
        g = r.get("gates", {})
        d = r.get("dsr", {})
        lines.append(
            f"| {r['name']} |"
            f" {m.get('cagr', float('nan'))*100:.2f} | {m.get('cagr_net', float('nan'))*100:.2f} |"
            f" {m.get('sharpe', float('nan')):.3f} | {m.get('sharpe_net', float('nan')):.3f} |"
            f" {m.get('max_dd', float('nan'))*100:.1f} | {m.get('calmar', float('nan')):.3f} |"
            f" {wf.get('positive', 0)}/8 | {oos.get('oos_sharpe', float('nan')):.2f} |"
            f" {fwd.get('fwd_sharpe', float('nan')):.2f} |"
            f" {pbo.get('pbo', float('nan')):.3f} | {d.get('p_value', float('nan')):.4f} |"
            f" {'✓' if g.get('eco1_beats_spy') else '✗'} |"
            f" {'✓' if g.get('eco2_calmar') else '✗'} |"
            f" {'✓' if g.get('eco3_sharpe_net') else '✗'} |"
            f" {'✓ PASS' if g.get('ALL_PASS') else '✗'} |"
        )

    lines += [
        "",
        f"**SPY B&H net CAGR threshold:** {spy_cagr_net*100:.2f}%",
        "",
        "## Cross-lib concordance (bt library)",
        "",
    ]
    for r in results:
        if "error" in r or "cross_lib_bt" not in r:
            continue
        cl = r["cross_lib_bt"]
        if cl.get("concordant") is None:
            lines.append(f"- {r['name']}: bt NOT AVAILABLE")
        elif cl.get("concordant"):
            lines.append(f"- {r['name']}: ✓ CONCORDANT (ΔCAGR={cl['cagr_delta_pp']:.2f}pp)")
        else:
            lines.append(f"- {r['name']}: ✗ DIVERGENT (ΔCAGR={cl['cagr_delta_pp']:.2f}pp)")

    lines += ["", "## Average TQQQ weight (time-in-market proxy)", "",
              "| Config | Avg TQQQ weight% | Min% | Max% |",
              "|--------|------------------|------|------|"]
    for r in results:
        if "error" in r or "weight_stats" not in r:
            continue
        ws = r["weight_stats"]
        lines.append(
            f"| {r['name']} | {ws['mean']*100:.1f} | {ws['min']*100:.1f} | {ws['max']*100:.1f} |"
        )

    lines += [
        "",
        "## Diagnosis",
        "",
        "PBO = fraction of CSCV folds where IS-winner is NOT also the OOS-winner.",
        "With 2 configs, PBO is volatile but reflects the structural dominance of vol15_lk20.",
        "Low PBO (<0.5) would indicate vol15_lk20 is a stable IS-winner across regimes.",
    ]

    tmp = path + f".tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        f.write("\n".join(lines) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    print(f"  Wrote {path}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> dict:
    print(f"\n=== E1 Vol-targeting 2-config TQQQ+GLD — iter {ITER_NUM} ===")
    print(f"  Window: {WINDOW_START} → {WINDOW_END}")
    print(f"  Configs: vol15_lk20 + sma200_gld_binary")
    print(f"  Hypothesis: PBO < 0.5 with just 2 structurally diverse configs?")

    # 1. Load data
    df = pd.read_parquet(PARQUET_PATH)
    df = df[(df["date"] >= WINDOW_START) & (df["date"] <= WINDOW_END)]
    prices = df.pivot(index="date", columns="ticker", values="close")
    prices.columns.name = None
    prices = prices.ffill().dropna(how="all")

    for t in ["TQQQ", "GLD", "SPY"]:
        if t not in prices.columns:
            raise RuntimeError(f"Missing ticker: {t}")

    window_info = {
        "start": WINDOW_START,
        "end": WINDOW_END,
        "n_bars": len(prices),
        "years": (prices.index[-1] - prices.index[0]).days / 365.25,
    }
    print(f"  Bars loaded: {len(prices)} ({window_info['years']:.2f}yr)")

    # 2. SPY benchmark
    spy_ret = prices["SPY"].pct_change().dropna()
    spy_cagr = compute_cagr(spy_ret)
    spy_cagr_net = spy_cagr * (1 - TAX_RATE)
    spy_sharpe = compute_sharpe(spy_ret)
    spy_max_dd = compute_max_dd(spy_ret)
    print(f"  SPY B&H: CAGR={spy_cagr*100:.2f}% net={spy_cagr_net*100:.2f}%"
          f" Sharpe={spy_sharpe:.3f} MaxDD={spy_max_dd*100:.1f}%")

    # 3. Run both configs
    configs = ["vol15_lk20", "sma200_gld_binary"]
    all_returns: dict[str, pd.Series] = {}
    results: list[dict] = []

    for config_name in configs:
        print(f"\n  → {config_name}", end=" ")
        try:
            port, w_series = run_portfolio(prices, config_name)
            all_returns[config_name] = port

            cagr = compute_cagr(port)
            cagr_net = cagr * (1 - TAX_RATE)
            sharpe = compute_sharpe(port)
            sharpe_net = sharpe * (1 - TAX_RATE)
            max_dd = compute_max_dd(port)
            calmar = compute_calmar(cagr, max_dd)
            wf_sharpes, wf_positive = compute_wf(port, n_splits=8)
            oos = compute_oos_holdout(port)
            fwd = compute_fwd_stress(port)

            weight_stats = {
                "mean": float(w_series.mean()),
                "min": float(w_series.min()),
                "max": float(w_series.max()),
                "std": float(w_series.std()),
            }

            # Cross-lib via bt
            bt_equity = run_portfolio_bt(prices, config_name)
            if bt_equity is not None:
                bt_rets = bt_equity.pct_change().dropna()
                bt_cagr = compute_cagr(bt_rets)
                cagr_delta = abs(cagr - bt_cagr) * 100
                cross_lib_ok = bool(cagr_delta <= 3.0)
            else:
                bt_cagr = float("nan")
                cagr_delta = float("nan")
                cross_lib_ok = None

            print(
                f"CAGR={cagr*100:.2f}% net={cagr_net*100:.2f}%"
                f" Sharpe={sharpe:.3f} SN={sharpe_net:.3f}"
                f" MaxDD={max_dd*100:.1f}% Calmar={calmar:.3f}"
                f" WF={wf_positive}/8 FWD={fwd['fwd_sharpe']:.3f}"
                f" AvgW={weight_stats['mean']*100:.1f}%"
            )

            results.append({
                "name": config_name,
                "metrics_is": {
                    "cagr": cagr, "cagr_net": cagr_net,
                    "sharpe": sharpe, "sharpe_net": sharpe_net,
                    "max_dd": max_dd, "calmar": calmar,
                    "n_bars": len(port),
                },
                "wf": {"sharpes": wf_sharpes, "positive": wf_positive,
                       "pass": bool(wf_positive >= 6)},
                "oos": oos,
                "fwd": fwd,
                "weight_stats": weight_stats,
                "cross_lib_bt": {
                    "bt_cagr": bt_cagr,
                    "cagr_delta_pp": cagr_delta,
                    "concordant": cross_lib_ok,
                },
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            traceback.print_exc()
            results.append({"name": config_name, "error": str(e)})

    # 4. PBO with just 2 configs [advances_fin_ml, p.208-211]
    pbo_result = compute_pbo_gate(all_returns)
    pbo_val = pbo_result.get("pbo", float("nan"))
    pbo_pass = pbo_result.get("pass", False)
    print(f"\n  PBO (2 configs): {pbo_val:.4f} ({'✓ PASS' if pbo_pass else '✗ FAIL'})")
    print(f"  n_combinations: {pbo_result.get('n_combinations', 'N/A')}")

    # 5. DSR + full gate summary per config
    n_configs = len(results)
    for r in results:
        if "error" in r or r["name"] not in all_returns:
            r["dsr"] = {"dsr": float("nan"), "p_value": float("nan"), "pass": False}
            r["gates"] = {"ALL_PASS": False, "fail_reason": "error"}
            continue
        r["dsr"] = compute_dsr_gate(all_returns[r["name"]], n_configs)
        r["gates"] = gate_summary(r, pbo_result, r["dsr"], spy_cagr_net)
        print(f"  {r['name']}: {r['gates']['fail_reason']}"
              f" | Sharpe={r['metrics_is']['sharpe']:.3f} SN={r['metrics_is']['sharpe_net']:.3f}"
              f" DSR_p={r['dsr']['p_value']:.4f}")

    any_pass = any(r.get("gates", {}).get("ALL_PASS", False) for r in results)
    vol15 = next((r for r in results if r["name"] == "vol15_lk20"), None)

    print(f"\n  ANY ALL_PASS: {any_pass}")
    if vol15 and "metrics_is" in vol15:
        m = vol15["metrics_is"]
        print(f"  vol15_lk20: CAGR_net={m['cagr_net']*100:.2f}%"
              f" Sharpe={m['sharpe']:.3f} SN={m['sharpe_net']:.3f}"
              f" MaxDD={m['max_dd']*100:.1f}% Calmar={m['calmar']:.3f}")

    # 6. Write outputs (atomic)
    json_data = {
        "ticker": "TQQQ",
        "frequency": "daily",
        "strategy": "e1_vol_tgt_2config",
        "window": window_info,
        "spy_benchmark": {
            "cagr": spy_cagr, "cagr_net": spy_cagr_net,
            "sharpe": spy_sharpe, "max_dd": spy_max_dd,
        },
        "pbo": pbo_result,
        "configs": results,
        "any_pass_all_gates": any_pass,
        "best_config": (vol15["name"] if vol15 else "N/A"),
        "best_sharpe": vol15["metrics_is"]["sharpe"] if vol15 and "metrics_is" in vol15 else float("nan"),
        "best_sharpe_net": vol15["metrics_is"]["sharpe_net"] if vol15 and "metrics_is" in vol15 else float("nan"),
        "citations": [
            "advances_fin_ml, ch.14",
            "volatility_trading",
            "leverage_for_the_long_run, p.13",
            "advances_fin_ml, p.208-211",
            "advances_fin_ml, p.298-299",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    atomic_write_json(os.path.join(REPORT_DIR, "TQQQ.json"), json_data)
    write_report_md(
        os.path.join(REPORT_DIR, "TQQQ.md"),
        results, pbo_result, window_info, spy_cagr_net
    )

    print(f"\n=== E1 complete — PBO={pbo_val:.4f}"
          f" {'✓ PASS' if pbo_pass else '✗ FAIL'} | vol15_lk20 ALL_PASS={any_pass} ===")
    return json_data


if __name__ == "__main__":
    main()
