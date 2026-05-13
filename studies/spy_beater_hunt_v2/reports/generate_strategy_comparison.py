from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series

STUDY = REPO_ROOT / "studies" / "spy_beater_hunt_v2"
ITER_DIR = STUDY / "iterations"
REPORT_DIR = STUDY / "reports"
PLOT_DIR = REPORT_DIR / "plots"
TABLE_DIR = REPORT_DIR / "tables"

ASSET_COLORS = {
    "SPY": "black",
    "002 static diversifier": "#4c78a8",
    "003 Gayed LRS UPRO": "#f58518",
    "004 vol-target LRS": "#54a24b",
    "005 Carver EWMAC": "#b279a2",
    "006 Clenow SPY/QQQ 3x": "#e45756",
    "007 vol-scaled relmom": "#72b7b2",
    "008 KAMA trend": "#ff9da6",
    "009 Hirsch seasonal": "#9d755d",
    "010 cross-asset Clenow": "#bab0ac",
}


def equity_from_returns(returns: pd.Series) -> pd.Series:
    return (1.0 + returns.dropna()).cumprod()


def annualized_cagr(equity: pd.Series) -> float:
    equity = equity.dropna()
    if len(equity) < 2 or float(equity.iloc[0]) <= 0:
        return float("nan")
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    if years <= 0:
        return float("nan")
    return float((float(equity.iloc[-1]) / float(equity.iloc[0])) ** (1.0 / years) - 1.0)


def max_drawdown(equity: pd.Series) -> float:
    equity = equity.dropna()
    if equity.empty:
        return float("nan")
    dd = equity / equity.cummax() - 1.0
    return float(dd.min())


def rolling_cagr(returns: pd.Series, years: int) -> pd.Series:
    equity = equity_from_returns(returns)
    window = years * 252
    if len(equity) <= window:
        return pd.Series(dtype=float)

    def calc(values: np.ndarray) -> float:
        if values[0] <= 0:
            return np.nan
        return float((values[-1] / values[0]) ** (252.0 / (len(values) - 1)) - 1.0)

    return equity.rolling(window).apply(calc, raw=True).dropna()


def rolling_mdd(returns: pd.Series, years: int) -> pd.Series:
    equity = equity_from_returns(returns)
    window = years * 252
    if len(equity) <= window:
        return pd.Series(dtype=float)

    def calc(values: np.ndarray) -> float:
        peak = np.maximum.accumulate(values)
        dd = values / peak - 1.0
        return float(np.min(dd))

    return equity.rolling(window).apply(calc, raw=True).dropna()


def adjusted_slope_series(price: pd.Series, window: int = 90) -> pd.Series:
    log_price = np.log(price)
    x = np.arange(window, dtype=float)
    x_centered = x - x.mean()
    denom = float((x_centered**2).sum())

    def calc(values: np.ndarray) -> float:
        if np.any(~np.isfinite(values)):
            return np.nan
        y = values.astype(float)
        y_centered = y - y.mean()
        slope = float((x_centered * y_centered).sum() / denom)
        y_ss = float((y_centered**2).sum())
        if y_ss <= 0:
            return 0.0
        fitted = y.mean() + slope * x_centered
        resid_ss = float(((y - fitted) ** 2).sum())
        r_squared = max(0.0, min(1.0, 1.0 - resid_ss / y_ss))
        return float(np.exp(slope * 250.0) - 1.0) * r_squared

    return log_price.rolling(window).apply(calc, raw=True)


def kama(price: pd.Series, er_lookback: int = 10, fast_days: int = 2, slow_days: int = 30) -> pd.Series:
    direction = (price - price.shift(er_lookback)).abs()
    volatility = price.diff().abs().rolling(er_lookback).sum()
    er = (direction / volatility).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    fastest = 2.0 / (fast_days + 1.0)
    slowest = 2.0 / (slow_days + 1.0)
    sc = (er * (fastest - slowest) + slowest) ** 2
    values = price.to_numpy(dtype=float)
    out = np.full(len(price), np.nan, dtype=float)
    if len(values) == 0:
        return pd.Series(out, index=price.index)
    out[0] = values[0]
    sc_values = sc.to_numpy(dtype=float)
    for i in range(1, len(values)):
        smooth = float(sc_values[i]) if np.isfinite(sc_values[i]) else slowest**2
        out[i] = out[i - 1] + smooth * (values[i] - out[i - 1])
    return pd.Series(out, index=price.index, name="KAMA")


def load_prices(tickers: list[str]) -> pd.DataFrame:
    return pd.concat({t: load_testfolio_series(t).dropna().sort_index() for t in tickers}, axis=1).dropna()


def spy_returns_for(index: pd.Index) -> pd.Series:
    spy = load_testfolio_series("SPYSIM").dropna().sort_index().pct_change().dropna()
    return spy.reindex(index).dropna().rename("SPY")


def static_002() -> pd.Series:
    prices = load_prices(["SPYSIM", "ZROZSIM", "GLDSIM", "KMLMSIM"])
    returns = prices.pct_change().dropna()
    weights = {"SPYSIM": 0.60, "ZROZSIM": 0.20, "GLDSIM": 0.10, "KMLMSIM": 0.10}
    return sum(returns[t] * w for t, w in weights.items()).rename("002 static diversifier")


def lrs_003() -> pd.Series:
    prices = load_prices(["SPYSIM", "UPROSIM", "CASHX"])
    signal = (prices["SPYSIM"] > prices["SPYSIM"].rolling(200).mean()).shift(1).fillna(False)
    asset_returns = prices[["UPROSIM", "CASHX"]].pct_change()
    return asset_returns["UPROSIM"].where(signal, asset_returns["CASHX"]).dropna().rename("003 Gayed LRS UPRO")


def vt_lrs_004() -> pd.Series:
    prices = load_prices(["SPYSIM", "UPROSIM", "CASHX"])
    signal = (prices["SPYSIM"] > prices["SPYSIM"].rolling(200).mean()).shift(1).fillna(False)
    asset_returns = prices[["UPROSIM", "CASHX"]].pct_change()
    realized_vol = asset_returns["UPROSIM"].rolling(63).std().shift(1) * np.sqrt(252)
    weight = (0.25 / realized_vol).clip(lower=0.0, upper=1.0).fillna(0.0)
    risk_on = weight * asset_returns["UPROSIM"] + (1.0 - weight) * asset_returns["CASHX"]
    return risk_on.where(signal, asset_returns["CASHX"]).dropna().rename("004 vol-target LRS")


def ewmac_005() -> pd.Series:
    prices = load_prices(["SPYSIM", "UPROSIM", "CASHX"])
    fast = prices["SPYSIM"].ewm(span=32, adjust=False).mean()
    slow = prices["SPYSIM"].ewm(span=128, adjust=False).mean()
    price_vol = prices["SPYSIM"].diff().rolling(25).std()
    forecast = (2.65 * ((fast - slow) / price_vol)).clip(lower=-20.0, upper=20.0).replace([np.inf, -np.inf], np.nan)
    weight = (forecast.shift(1).clip(lower=0.0, upper=20.0) / 20.0).fillna(0.0)
    asset_returns = prices[["UPROSIM", "CASHX"]].pct_change()
    return (weight * asset_returns["UPROSIM"] + (1.0 - weight) * asset_returns["CASHX"]).dropna().rename("005 Carver EWMAC")


def relmom_006() -> pd.Series:
    prices = load_prices(["SPYSIM", "QQQSIM", "UPROSIM", "TQQQSIM", "CASHX"])
    spy_score = adjusted_slope_series(prices["SPYSIM"])
    qqq_score = adjusted_slope_series(prices["QQQSIM"])
    regime_on = prices["SPYSIM"] > prices["SPYSIM"].rolling(200).mean()
    pick = pd.Series("CASHX", index=prices.index, dtype="object")
    pick = pick.mask(regime_on & (spy_score >= qqq_score), "UPROSIM")
    pick = pick.mask(regime_on & (qqq_score > spy_score), "TQQQSIM")
    signal = pick.shift(1).fillna("CASHX")
    asset_returns = prices[["UPROSIM", "TQQQSIM", "CASHX"]].pct_change()
    values = np.select([signal == "UPROSIM", signal == "TQQQSIM"], [asset_returns["UPROSIM"], asset_returns["TQQQSIM"]], default=asset_returns["CASHX"])
    return pd.Series(values, index=prices.index).dropna().rename("006 Clenow SPY/QQQ 3x")


def vt_relmom_007() -> pd.Series:
    prices = load_prices(["SPYSIM", "QQQSIM", "UPROSIM", "TQQQSIM", "CASHX"])
    spy_score = adjusted_slope_series(prices["SPYSIM"])
    qqq_score = adjusted_slope_series(prices["QQQSIM"])
    regime_on = prices["SPYSIM"] > prices["SPYSIM"].rolling(200).mean()
    signal = pd.Series("CASHX", index=prices.index, dtype="object")
    signal = signal.mask(regime_on & (spy_score >= qqq_score), "UPROSIM")
    signal = signal.mask(regime_on & (qqq_score > spy_score), "TQQQSIM")
    signal = signal.shift(1).fillna("CASHX")
    risk_returns = prices[["UPROSIM", "TQQQSIM"]].pct_change()
    asset_returns = prices[["UPROSIM", "TQQQSIM", "CASHX"]].pct_change()
    exposure = (0.25 / (risk_returns.rolling(63).std() * np.sqrt(252))).clip(upper=1.0).shift(1)
    weights = pd.DataFrame(0.0, index=prices.index, columns=["UPROSIM", "TQQQSIM", "CASHX"])
    for risk_asset in ("UPROSIM", "TQQQSIM"):
        weights[risk_asset] = exposure[risk_asset].where(signal == risk_asset, 0.0).fillna(0.0)
    weights["CASHX"] = 1.0 - weights[["UPROSIM", "TQQQSIM"]].sum(axis=1)
    return (weights.clip(lower=0.0, upper=1.0) * asset_returns).sum(axis=1).dropna().rename("007 vol-scaled relmom")


def kama_008() -> pd.Series:
    prices = load_prices(["SPYSIM", "SSOSIM", "CASHX"])
    signal = (prices["SPYSIM"] > kama(prices["SPYSIM"])).shift(1).fillna(False).astype(bool)
    asset_returns = prices[["SSOSIM", "CASHX"]].pct_change()
    return asset_returns["CASHX"].where(~signal, asset_returns["SSOSIM"]).dropna().rename("008 KAMA trend")


def seasonal_009() -> pd.Series:
    prices = load_prices(["UPROSIM", "CASHX"])
    signal = pd.Series(prices.index.month.isin({11, 12, 1, 2, 3, 4}), index=prices.index)
    asset_returns = prices[["UPROSIM", "CASHX"]].pct_change()
    return asset_returns["CASHX"].where(~signal, asset_returns["UPROSIM"]).dropna().rename("009 Hirsch seasonal")


def xasset_010() -> pd.Series:
    assets = ["SPYSIM", "ZROZSIM", "GLDSIM", "KMLMSIM"]
    prices = load_prices([*assets, "CASHX"])
    scores = pd.concat({a: adjusted_slope_series(prices[a]) for a in assets}, axis=1)
    regime_on = prices["SPYSIM"] > prices["SPYSIM"].rolling(200).mean()
    is_rebalance = pd.Series(prices.index.weekday == 2, index=prices.index)
    weights = pd.DataFrame(0.0, index=prices.index, columns=[*assets, "CASHX"])
    current = pd.Series(0.0, index=[*assets, "CASHX"])
    for dt in prices.index:
        if bool(is_rebalance.loc[dt]):
            current[:] = 0.0
            row = scores.loc[dt].dropna().sort_values(ascending=False)
            if bool(regime_on.loc[dt]) and len(row) >= 1:
                current[row.index[0]] = 1.0
            else:
                current["CASHX"] = 1.0
        weights.loc[dt] = current
    asset_returns = prices[[*assets, "CASHX"]].pct_change().fillna(0.0)
    return (weights.shift(1).fillna(0.0) * asset_returns).sum(axis=1).iloc[201:].dropna().rename("010 cross-asset Clenow")


def build_returns() -> dict[str, pd.Series]:
    return {
        "002 static diversifier": static_002(),
        "003 Gayed LRS UPRO": lrs_003(),
        "004 vol-target LRS": vt_lrs_004(),
        "005 Carver EWMAC": ewmac_005(),
        "006 Clenow SPY/QQQ 3x": relmom_006(),
        "007 vol-scaled relmom": vt_relmom_007(),
        "008 KAMA trend": kama_008(),
        "009 Hirsch seasonal": seasonal_009(),
        "010 cross-asset Clenow": xasset_010(),
    }


def load_results() -> list[dict[str, Any]]:
    out = []
    for path in sorted(ITER_DIR.glob("[0-9][0-9][0-9]-*/RESULTS.json")):
        data = json.loads(path.read_text())
        data["dir"] = path.parent.name
        out.append(data)
    return out


def plot_equity(equities: dict[str, pd.Series], spy_equity: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(15, 9))
    spy_equity.plot(ax=ax, lw=2.5, color=ASSET_COLORS["SPY"], label="SPY benchmark")
    for name, equity in equities.items():
        equity.plot(ax=ax, lw=1.4, alpha=0.9, color=ASSET_COLORS.get(name), label=name)
    ax.set_yscale("log")
    ax.set_title("spy_beater_hunt_v2: equity curves, best config per iteration")
    ax.set_ylabel("Growth of $1, log scale")
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=2, fontsize=9)
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "01_equity_curves.png", dpi=180)
    plt.close(fig)


def plot_relative(equities: dict[str, pd.Series], spy_equity: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(15, 9))
    for name, equity in equities.items():
        aligned = pd.concat([equity.rename("candidate"), spy_equity.rename("spy")], axis=1).dropna()
        rel = aligned["candidate"] / aligned["spy"]
        rel.plot(ax=ax, lw=1.5, color=ASSET_COLORS.get(name), label=name)
    ax.axhline(1.0, color="black", lw=1.0, ls="--", label="SPY parity")
    ax.set_yscale("log")
    ax.set_title("Relative equity: candidate / SPY benchmark")
    ax.set_ylabel("Relative wealth, log scale")
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=2, fontsize=9)
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "02_relative_equity_vs_spy.png", dpi=180)
    plt.close(fig)


def plot_rolling(returns: dict[str, pd.Series], spy_returns: pd.Series, kind: str) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharex=False)
    for ax, years in zip(axes.flatten(), (3, 5, 10, 15), strict=True):
        if kind == "cagr":
            spy_line = rolling_cagr(spy_returns, years)
            ylabel = "Rolling CAGR"
            title = f"{years}y rolling CAGR"
        else:
            spy_line = rolling_mdd(spy_returns, years)
            ylabel = "Rolling max drawdown"
            title = f"{years}y rolling max drawdown"
        spy_line.plot(ax=ax, color="black", lw=2.0, label="SPY")
        for name, series in returns.items():
            line = rolling_cagr(series, years) if kind == "cagr" else rolling_mdd(series, years)
            if not line.empty:
                line.plot(ax=ax, lw=1.0, alpha=0.8, color=ASSET_COLORS.get(name), label=name)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.25)
        ax.yaxis.set_major_formatter(lambda x, _: f"{x:.0%}")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=8)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    filename = "03_rolling_cagr_windows.png" if kind == "cagr" else "04_rolling_mdd_windows.png"
    fig.savefig(PLOT_DIR / filename, dpi=180)
    plt.close(fig)


def table_rows(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for result in results:
        best = result.get("metrics", {}).get("best") or {}
        gates = result.get("gates", {})
        failed = [name for name, gate in gates.items() if isinstance(gate, dict) and gate.get("pass") is False]
        rows.append(
            {
                "iter": result["iteration"],
                "best_config": result.get("best_config"),
                "status": result.get("status"),
                "winner": result.get("winner"),
                "cagr": best.get("cagr"),
                "mdd": best.get("mdd"),
                "sharpe": best.get("sharpe"),
                "terminal_ratio_vs_spy": best.get("terminal_ratio_vs_spy"),
                "pbo": gates.get("pbo", {}).get("value"),
                "dsr_p": gates.get("dsr", {}).get("p_value"),
                "wf": (
                    f"{gates.get('walk_forward', {}).get('pass_count')}/{gates.get('walk_forward', {}).get('total')}"
                    if gates.get("walk_forward", {}).get("pass_count") is not None and gates.get("walk_forward", {}).get("total") is not None
                    else "n/a"
                ),
                "failed_gates": ", ".join(failed),
            }
        )
    return rows


def pct(value: Any, digits: int = 2) -> str:
    if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
        return "n/a"
    return f"{float(value):.{digits}%}"


def num(value: Any, digits: int = 2) -> str:
    if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
        return "n/a"
    return f"{float(value):.{digits}f}"


def multiple(value: Any, digits: int = 2) -> str:
    formatted = num(value, digits)
    return formatted if formatted == "n/a" else f"{formatted}x"


def gate_label(gate: dict[str, Any]) -> str:
    if gate.get("computed") is False:
        return "NOT_COMPUTED"
    if "pass" not in gate:
        return "NOT_COMPUTED"
    return "PASS" if gate.get("pass") else "FAIL"


DESCRIPTIONS = {
    "001-2026-05-13-bootstrap-audit": ("Bootstrap/audit", "Infrastructure-only audit: confirmed SPYSIM benchmark and validation modules. No strategy was tested."),
    "002-2026-05-13-static-diversifier-control": ("Static diversifier control", "Constant-weight SPY/ZROZ/GLD/KMLM portfolio inspired by diversified futures/asset allocation controls `[systematic_trading, p.72-85]`. It improved drawdown but could not beat SPY CAGR and failed multiple gates."),
    "003-2026-05-13-gayed-lrs-control": ("Canonical Gayed LRS", "SPY above SMA200 gates exposure into UPRO, otherwise cash, with a one-day lag `[leverage_for_the_long_run, p.13]`. Strong CAGR and most gates passed, but bootstrap failed."),
    "004-2026-05-13-vol-targeted-lrs": ("Vol-targeted LRS", "Same Gayed SMA200 shell, but UPRO exposure is scaled by lagged realized volatility to a 25% target `[systematic_trading, p.137-148]`. It reduced drawdown but lost temporal robustness."),
    "005-2026-05-13-carver-ewmac-trend": ("Carver EWMAC trend", "EWMAC forecast maps positive SPY trend strength into partial UPRO exposure `[systematic_trading, p.112-119]`. It failed economics and most gates."),
    "006-2026-05-13-clenow-relative-momentum": ("Clenow SPY/QQQ relative momentum", "Ranks SPY and QQQ by 90-day adjusted slope and holds the matching 3x LETF only when SPY is above SMA200 `[stocks_on_the_move, p.75-77]`. Best economic lead; failed only bootstrap 99.9%."),
    "007-2026-05-13-vol-scaled-relative-momentum": ("Vol-scaled relative momentum", "Iteration 006 mechanism with lagged realized-vol scaling to 25% target. It reduced drawdown but failed FWD and bootstrap."),
    "008-2026-05-13-kaufman-kama-er-trend": ("Kaufman KAMA/ER trend", "KAMA adaptive trend gate using Kaufman's efficiency ratio `[trading_systems_methods, p.780-781]`. It underperformed badly."),
    "009-2026-05-13-seasonal-hirsch-window": ("Hirsch/Kaeppel seasonality", "Holds UPRO during November-April and cash in May-October `[trading_systems_methods, p.480]`. Beat SPY economically but failed OOS/FWD/bootstrap."),
    "010-2026-05-13-cross-asset-clenow-momentum": ("Cross-asset Clenow momentum", "Ranks SPY/ZROZ/GLD/KMLM by adjusted slope with SPY SMA200 regime filter `[stocks_on_the_move, p.83-89]`. Improved risk but did not beat SPY CAGR."),
}


def write_report(results: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("# spy_beater_hunt_v2 — 10-Iteration Strategy Comparison")
    lines.append("")
    lines.append("## Plots")
    lines.append("")
    lines.append("![Equity curves](plots/01_equity_curves.png)")
    lines.append("")
    lines.append("![Relative equity](plots/02_relative_equity_vs_spy.png)")
    lines.append("")
    lines.append("![Rolling CAGR](plots/03_rolling_cagr_windows.png)")
    lines.append("")
    lines.append("![Rolling max drawdown](plots/04_rolling_mdd_windows.png)")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("No strategy passed all hard gates. The best research lead is iteration 006, `clenow_relmom_90d_3x_cash`: it beat SPY by a wide margin and passed PBO, DSR, WF, OOS, FWD and cross-lib, but failed the 99.9% bootstrap lower-bound gate by a small amount. Under the project mandate, that remains a hard fail, not a winner `[advances_fin_ml, p.196-202]`.")
    lines.append("")
    lines.append("Iteration 001 was infrastructure-only, so the plots compare SPY plus the best strategy config from iterations 002-010. Iteration 001 is documented in the strategy-by-strategy section below.")
    lines.append("")
    lines.append("## Ranking Table")
    lines.append("")
    lines.append("| iter | best config | CAGR | MDD | Sharpe | terminal/SPY | PBO | DSR p | WF | failed gates |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for row in rows:
        lines.append(
            f"| {row['iter'][:3]} | `{row['best_config']}` | {pct(row['cagr'])} | {pct(-float(row['mdd']) if row['mdd'] and row['mdd'] > 0 else row['mdd'])} | {num(row['sharpe'], 3)} | {multiple(row['terminal_ratio_vs_spy'], 2)} | {num(row['pbo'], 3)} | {num(row['dsr_p'], 5)} | {row['wf']} | {row['failed_gates'] or 'none'} |"
        )
    lines.append("")
    lines.append("## Strategy-by-Strategy Review")
    lines.append("")
    for result in results:
        title, description = DESCRIPTIONS.get(result["iteration"], (result["iteration"], result.get("notes", "")))
        best = result.get("metrics", {}).get("best") or {}
        spy = result.get("spy_benchmark") or {}
        gates = result.get("gates") or {}
        failed = [name for name, gate in gates.items() if isinstance(gate, dict) and gate.get("pass") is False]
        lines.append(f"### {result['iteration'][:3]} — {title}")
        lines.append("")
        lines.append(description)
        lines.append("")
        lines.append(f"- Best config: `{result.get('best_config')}`")
        lines.append(f"- Verdict: `{result.get('status')}`; winner: `{result.get('winner')}`")
        if best:
            lines.append(f"- Candidate: CAGR {pct(best.get('cagr'))}, MDD {pct(-float(best.get('mdd')) if best.get('mdd') and best.get('mdd') > 0 else best.get('mdd'))}, Sharpe {num(best.get('sharpe'), 3)}, terminal/SPY {num(best.get('terminal_ratio_vs_spy'), 2)}x")
        if spy:
            lines.append(f"- SPY same-window: CAGR {pct(spy.get('cagr'))}, MDD {pct(-float(spy.get('mdd')) if spy.get('mdd') and spy.get('mdd') > 0 else spy.get('mdd'))}, Sharpe {num(spy.get('sharpe'), 3)}")
        if gates:
            gate_bits = []
            for gate_name in ("economic", "pbo", "dsr", "walk_forward", "oos", "fwd", "bootstrap", "cross_lib"):
                gate = gates.get(gate_name)
                if isinstance(gate, dict):
                    gate_bits.append(f"{gate_name}={gate_label(gate)}")
            lines.append(f"- Gates: {', '.join(gate_bits)}")
            if failed:
                lines.append(f"- Failed gates: {', '.join(failed)}")
        lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("The main pattern is not lack of economic ideas. Several strategies beat SPY and pass DSR/PBO. The binding control is temporal robustness, especially bootstrap 99.9% and, for some variants, OOS/FWD. Iteration 006 deserves follow-up as a research lead, but only through a distinct robustness test or independent confirmation, not a local lookback/leverage grid that would inflate DSR and PBO risk `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.")
    lines.append("")
    (REPORT_DIR / "STRATEGY_COMPARISON.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    returns = build_returns()
    spy_returns = load_testfolio_series("SPYSIM").dropna().sort_index().pct_change().dropna().rename("SPY")
    common_index = sorted(set().union(*(set(s.index) for s in returns.values()), set(spy_returns.index)))
    spy_returns = spy_returns.reindex(pd.DatetimeIndex(common_index)).dropna()
    equities = {name: equity_from_returns(series) for name, series in returns.items()}
    spy_equity = equity_from_returns(spy_returns)

    plot_equity(equities, spy_equity)
    plot_relative(equities, spy_equity)
    plot_rolling(returns, spy_returns, "cagr")
    plot_rolling(returns, spy_returns, "mdd")

    results = load_results()
    rows = table_rows(results)
    pd.DataFrame(rows).to_csv(TABLE_DIR / "strategy_comparison.csv", index=False)
    write_report(results, rows)


if __name__ == "__main__":
    main()
