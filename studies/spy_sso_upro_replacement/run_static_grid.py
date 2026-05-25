from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

import numpy as np
import pandas as pd

from market_lab.backtest.data.testfolio_loader import load_testfolio_frame


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = ROOT / "REPORT.md"

ASSETS = ["SPYSIM", "SSOSIM", "UPROSIM", "ZROZSIM", "GLDSIM", "IEFSIM", "CASHX"]
RETURN_ASSETS = ["SPYSIM", "SSOSIM", "UPROSIM"]
DIVERSIFIERS = ["ZROZSIM", "GLDSIM", "IEFSIM", "CASHX"]
HORIZONS_YEARS = [3, 5, 10, 15, 20, 30]
EXACT_REBALANCE_FREQS = {"monthly": "M", "quarterly": "Q", "annual": "Y"}
TRADING_DAYS = 252
GRID_UNITS = 20
BATCH_SIZE = 5000
HIT_TOLERANCE = 1e-10
CAGR_SPREAD_TOLERANCE = 1e-6


PREDEFINED: dict[str, dict[str, float]] = {
    "SPY buy-hold": {"SPYSIM": 1.00},
    "50 SSO / 25 ZROZ / 25 GLD": {"SSOSIM": 0.50, "ZROZSIM": 0.25, "GLDSIM": 0.25},
    "60 SSO / 40 ZROZ": {"SSOSIM": 0.60, "ZROZSIM": 0.40},
    "70 SSO / 30 ZROZ": {"SSOSIM": 0.70, "ZROZSIM": 0.30},
    "40 UPRO / 60 ZROZ": {"UPROSIM": 0.40, "ZROZSIM": 0.60},
    "45 UPRO / 55 ZROZ": {"UPROSIM": 0.45, "ZROZSIM": 0.55},
    "50 UPRO / 50 ZROZ": {"UPROSIM": 0.50, "ZROZSIM": 0.50},
    "55 UPRO / 45 ZROZ": {"UPROSIM": 0.55, "ZROZSIM": 0.45},
    "40 UPRO / 40 ZROZ / 20 GLD": {"UPROSIM": 0.40, "ZROZSIM": 0.40, "GLDSIM": 0.20},
    "35 UPRO / 20 SSO / 45 ZROZ": {"UPROSIM": 0.35, "SSOSIM": 0.20, "ZROZSIM": 0.45},
    "50 SPY / 20 UPRO / 30 ZROZ": {"SPYSIM": 0.50, "UPROSIM": 0.20, "ZROZSIM": 0.30},
    "50 SSO / 35 ZROZ / 15 CASH": {"SSOSIM": 0.50, "ZROZSIM": 0.35, "CASHX": 0.15},
}


@dataclass(frozen=True)
class Metrics:
    start: str
    end: str
    years: float
    cagr: float
    mdd: float
    sharpe: float
    sortino: float
    calmar: float
    terminal: float


def fmt_pct(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{100.0 * value:.{digits}f}%"


def fmt_pp(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "n/a"
    sign = "+" if value >= 0 else ""
    return f"{sign}{100.0 * value:.{digits}f}pp"


def fmt_num(value: float, digits: int = 3) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.{digits}f}"


def fmt_x(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.{digits}f}x"


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._\n"
    header = "| " + " | ".join(columns) + " |"
    sep = "|" + "|".join("---" for _ in columns) + "|"
    body = ["| " + " | ".join(str(row.get(col, "")) for col in columns) + " |" for row in rows]
    return "\n".join([header, sep, *body]) + "\n"


def compositions(n: int, total: int = GRID_UNITS):
    if n == 1:
        yield (total,)
        return
    for value in range(total + 1):
        for rest in compositions(n - 1, total - value):
            yield (value, *rest)


def generate_weight_grid() -> np.ndarray:
    units = np.array(list(compositions(len(ASSETS), GRID_UNITS)), dtype=np.float64)
    weights = units / GRID_UNITS
    idx = {asset: ASSETS.index(asset) for asset in ASSETS}

    return_weight = weights[:, [idx[a] for a in RETURN_ASSETS]].sum(axis=1)
    diversifier_weight = weights[:, [idx[a] for a in DIVERSIFIERS]].sum(axis=1)
    effective_sp = weights[:, idx["SPYSIM"]] + 2.0 * weights[:, idx["SSOSIM"]] + 3.0 * weights[:, idx["UPROSIM"]]
    mask = (
        (return_weight >= 0.45)
        & (return_weight <= 0.95)
        & (weights[:, idx["UPROSIM"]] <= 0.55)
        & (weights[:, idx["SSOSIM"]] <= 0.80)
        & (effective_sp >= 1.00)
        & (effective_sp <= 2.10)
        & (diversifier_weight >= 0.05)
    )
    return weights[mask]


def metrics_from_returns(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> Metrics:
    clean = returns.dropna().astype(float)
    equity = (1.0 + clean).cumprod()
    years = len(clean) / periods_per_year
    drawdown = equity / equity.cummax() - 1.0
    vol = clean.std(ddof=0)
    downside = clean[clean < 0.0].std(ddof=0)
    cagr = equity.iloc[-1] ** (1.0 / years) - 1.0
    mdd = float(drawdown.min())
    return Metrics(
        start=str(clean.index[0].date()),
        end=str(clean.index[-1].date()),
        years=float(years),
        cagr=float(cagr),
        mdd=mdd,
        sharpe=float(clean.mean() / vol * math.sqrt(periods_per_year)) if vol and vol > 0 else math.nan,
        sortino=float(clean.mean() / downside * math.sqrt(periods_per_year)) if downside and downside > 0 else math.nan,
        calmar=float(cagr / abs(mdd)) if mdd < 0 else math.nan,
        terminal=float(equity.iloc[-1]),
    )


def drawdown_from_returns(returns: pd.Series) -> pd.Series:
    equity = (1.0 + returns.dropna()).cumprod()
    return equity / equity.cummax() - 1.0


def monthly_window_returns(equity: np.ndarray, horizon_months: int) -> np.ndarray:
    n = equity.shape[0]
    prev = np.vstack([np.ones((1, equity.shape[1])), equity[: n - horizon_months]])
    end = equity[horizon_months - 1 :]
    return end / prev


def monthly_spy_window_returns(spy_equity: np.ndarray, horizon_months: int) -> np.ndarray:
    n = spy_equity.shape[0]
    prev = np.concatenate([[1.0], spy_equity[: n - horizon_months]])
    end = spy_equity[horizon_months - 1 :]
    return end / prev


def triage_grid(monthly_returns: pd.DataFrame, grid: np.ndarray) -> pd.DataFrame:
    returns_matrix = monthly_returns[ASSETS].to_numpy(dtype=np.float64)
    spy_returns = monthly_returns["SPYSIM"].to_numpy(dtype=np.float64)
    spy_equity = np.cumprod(1.0 + spy_returns)
    spy_metrics = metrics_from_returns(monthly_returns["SPYSIM"], periods_per_year=12)
    years = len(monthly_returns) / 12.0

    rows: list[dict[str, float | str | bool]] = []
    idx = {asset: ASSETS.index(asset) for asset in ASSETS}
    for batch_start in range(0, len(grid), BATCH_SIZE):
        weights = grid[batch_start : batch_start + BATCH_SIZE]
        portfolio_returns = returns_matrix @ weights.T
        equity = np.cumprod(1.0 + portfolio_returns, axis=0)
        cagr = np.power(equity[-1], 1.0 / years) - 1.0
        running_max = np.maximum.accumulate(equity, axis=0)
        mdd = (equity / running_max - 1.0).min(axis=0)
        mean = portfolio_returns.mean(axis=0)
        std = portfolio_returns.std(axis=0, ddof=0)
        sharpe = np.divide(mean * math.sqrt(12), std, out=np.full_like(mean, np.nan), where=std > 0)
        terminal = equity[-1]

        hit: dict[int, np.ndarray] = {}
        p10: dict[int, np.ndarray] = {}
        latest: dict[int, np.ndarray] = {}
        for horizon in HORIZONS_YEARS:
            months = horizon * 12
            if len(monthly_returns) <= months:
                continue
            port_window = monthly_window_returns(equity, months)
            spy_window = monthly_spy_window_returns(spy_equity, months)
            relative = port_window / spy_window[:, None] - 1.0
            relative[np.abs(relative) <= HIT_TOLERANCE] = 0.0
            hit[horizon] = (relative > HIT_TOLERANCE).mean(axis=0)
            p10[horizon] = np.quantile(relative, 0.10, axis=0)
            latest[horizon] = relative[-1]

        min_hit_5p = np.minimum.reduce([hit[h] for h in hit if h >= 5])
        min_hit_10p = np.minimum.reduce([hit[h] for h in hit if h >= 10])
        min_p10_5p = np.minimum.reduce([p10[h] for h in p10 if h >= 5])
        min_p10_10p = np.minimum.reduce([p10[h] for h in p10 if h >= 10])
        effective_sp = weights[:, idx["SPYSIM"]] + 2.0 * weights[:, idx["SSOSIM"]] + 3.0 * weights[:, idx["UPROSIM"]]
        return_weight = weights[:, [idx[a] for a in RETURN_ASSETS]].sum(axis=1)
        diversifier_weight = weights[:, [idx[a] for a in DIVERSIFIERS]].sum(axis=1)
        preferred_pass = (
            ((cagr - spy_metrics.cagr) > CAGR_SPREAD_TOLERANCE)
            & (min_hit_10p >= 0.90)
            & ((mdd >= spy_metrics.mdd - 0.05) | (mdd >= -0.60))
        )
        strict_pass = ((cagr - spy_metrics.cagr) > CAGR_SPREAD_TOLERANCE) & (min_hit_5p >= 0.90) & (mdd >= spy_metrics.mdd)
        score = (
            2.00 * min_hit_10p
            + 0.75 * min_p10_10p
            + 5.00 * (cagr - spy_metrics.cagr)
            + 0.35 * (mdd - spy_metrics.mdd)
            + 0.15 * np.nan_to_num(latest.get(10, np.zeros_like(cagr)), nan=0.0)
        )

        for i in range(weights.shape[0]):
            row: dict[str, float | str | bool] = {
                "source": "grid_monthly_triage",
                "monthly_score": float(score[i]),
                "preferred_pass_monthly": bool(preferred_pass[i]),
                "strict_pass_monthly": bool(strict_pass[i]),
                "cagr_monthly": float(cagr[i]),
                "cagr_spread_monthly": float(cagr[i] - spy_metrics.cagr),
                "mdd_monthly": float(mdd[i]),
                "mdd_spread_monthly": float(mdd[i] - spy_metrics.mdd),
                "sharpe_monthly": float(sharpe[i]),
                "terminal_monthly": float(terminal[i]),
                "terminal_vs_spy_monthly": float(terminal[i] / spy_metrics.terminal),
                "min_hit_5p_monthly": float(min_hit_5p[i]),
                "min_hit_10p_monthly": float(min_hit_10p[i]),
                "min_p10_5p_monthly": float(min_p10_5p[i]),
                "min_p10_10p_monthly": float(min_p10_10p[i]),
                "effective_sp500_exposure": float(effective_sp[i]),
                "return_sleeve_weight": float(return_weight[i]),
                "diversifier_weight": float(diversifier_weight[i]),
            }
            for asset in ASSETS:
                row[f"w_{asset}"] = float(weights[i, idx[asset]])
            for horizon in HORIZONS_YEARS:
                if horizon in hit:
                    row[f"hit_{horizon}y_monthly"] = float(hit[horizon][i])
                    row[f"p10_{horizon}y_monthly"] = float(p10[horizon][i])
                    row[f"latest_{horizon}y_monthly"] = float(latest[horizon][i])
            rows.append(row)
    return pd.DataFrame(rows).sort_values("monthly_score", ascending=False).reset_index(drop=True)


def weights_from_row(row: pd.Series) -> dict[str, float]:
    return {asset: float(row[f"w_{asset}"]) for asset in ASSETS if float(row[f"w_{asset}"]) > 0.0}


def weights_key(weights: dict[str, float]) -> tuple[int, ...]:
    return tuple(int(round(weights.get(asset, 0.0) * GRID_UNITS)) for asset in ASSETS)


def select_finalists(summary: pd.DataFrame) -> dict[str, dict[str, float]]:
    buckets = [
        summary[summary["preferred_pass_monthly"]].head(120),
        summary.sort_values("monthly_score", ascending=False).head(120),
        summary.sort_values("cagr_monthly", ascending=False).head(80),
        summary.sort_values("min_hit_10p_monthly", ascending=False).head(80),
        summary.sort_values("min_p10_10p_monthly", ascending=False).head(80),
    ]
    finalists: dict[tuple[int, ...], tuple[str, dict[str, float]]] = {}
    for bucket in buckets:
        for _, row in bucket.iterrows():
            weights = weights_from_row(row)
            key = weights_key(weights)
            if key not in finalists:
                finalists[key] = ("grid finalist", weights)
    for name, weights in PREDEFINED.items():
        key = weights_key(weights)
        finalists.setdefault(key, (name, weights))
    return {name if name != "grid finalist" else weight_label(weights): weights for name, weights in finalists.values()}


def weight_label(weights: dict[str, float]) -> str:
    return " / ".join(f"{int(round(weight * 100))} {asset.replace('SIM', '')}" for asset, weight in weights.items())


def rebalanced_returns(asset_returns: pd.DataFrame, weights: dict[str, float], freq: str) -> pd.Series:
    aligned = asset_returns[list(weights)].dropna()
    target = np.array([weights[col] for col in aligned.columns], dtype=np.float64)
    values: list[np.ndarray] = []
    dates: list[pd.DatetimeIndex] = []
    portfolio_value = 1.0
    periods = aligned.index.to_period(freq)
    for _period, block in aligned.groupby(periods, sort=True):
        growth = np.cumprod(1.0 + block.to_numpy(dtype=np.float64), axis=0)
        block_values = portfolio_value * (growth @ target)
        values.append(block_values)
        dates.append(block.index)
        portfolio_value = float(block_values[-1])
    equity = pd.Series(np.concatenate(values), index=dates[0].append(dates[1:]), name="equity")
    returns = equity.pct_change()
    returns.iloc[0] = equity.iloc[0] - 1.0
    returns.name = "portfolio"
    return returns


def rolling_relative_stats(portfolio_returns: pd.Series, spy_returns: pd.Series) -> dict[str, float]:
    aligned = pd.concat({"portfolio": portfolio_returns, "spy": spy_returns}, axis=1).dropna()
    peq = (1.0 + aligned["portfolio"]).cumprod().to_numpy(dtype=np.float64)
    seq = (1.0 + aligned["spy"]).cumprod().to_numpy(dtype=np.float64)
    out: dict[str, float] = {}
    n = len(aligned)
    for horizon in HORIZONS_YEARS:
        days = horizon * TRADING_DAYS
        if n <= days:
            continue
        pprev = np.concatenate([[1.0], peq[: n - days]])
        sprev = np.concatenate([[1.0], seq[: n - days]])
        pend = peq[days - 1 :]
        send = seq[days - 1 :]
        relative = (pend / pprev) / (send / sprev) - 1.0
        relative[np.abs(relative) <= HIT_TOLERANCE] = 0.0
        out[f"hit_{horizon}y"] = float((relative > HIT_TOLERANCE).mean())
        out[f"p10_{horizon}y"] = float(np.quantile(relative, 0.10))
        out[f"median_{horizon}y"] = float(np.quantile(relative, 0.50))
        out[f"latest_{horizon}y"] = float(relative[-1])
        out[f"min_{horizon}y"] = float(relative.min())
    return out


def named_regime_stats(portfolio_returns: pd.Series, spy_returns: pd.Series) -> list[dict[str, float | str]]:
    regimes = {
        "Dot-com bust": ("2000-03-24", "2002-10-09"),
        "GFC": ("2007-10-09", "2009-03-09"),
        "Covid crash": ("2020-02-19", "2020-03-23"),
        "Inflation/rates shock": ("2022-01-03", "2022-10-14"),
        "Recent recovery": ("2022-10-14", "2026-05-21"),
    }
    aligned = pd.concat({"portfolio": portfolio_returns, "spy": spy_returns}, axis=1).dropna()
    rows: list[dict[str, float | str]] = []
    for name, (start, end) in regimes.items():
        subset = aligned.loc[pd.Timestamp(start) : pd.Timestamp(end)]
        if len(subset) < 5:
            continue
        peq = (1.0 + subset["portfolio"]).cumprod()
        seq = (1.0 + subset["spy"]).cumprod()
        rows.append(
            {
                "regime": name,
                "start": str(subset.index[0].date()),
                "end": str(subset.index[-1].date()),
                "portfolio_return": float(peq.iloc[-1] - 1.0),
                "spy_return": float(seq.iloc[-1] - 1.0),
                "return_spread": float(peq.iloc[-1] - seq.iloc[-1]),
                "portfolio_mdd": float((peq / peq.cummax() - 1.0).min()),
                "spy_mdd": float((seq / seq.cummax() - 1.0).min()),
            }
        )
    return rows


def exact_evaluate(daily_returns: pd.DataFrame, finalists: dict[str, dict[str, float]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    spy_returns = daily_returns["SPYSIM"]
    spy_metrics = metrics_from_returns(spy_returns)
    exact_rows: list[dict[str, float | str | bool]] = []
    regime_rows: list[dict[str, float | str]] = []

    for name, weights in finalists.items():
        for freq_name, freq in EXACT_REBALANCE_FREQS.items():
            returns = rebalanced_returns(daily_returns, weights, freq)
            metrics = metrics_from_returns(returns)
            rolling = rolling_relative_stats(returns, spy_returns)
            min_hit_5p = min(rolling.get(f"hit_{h}y", 1.0) for h in HORIZONS_YEARS if h >= 5)
            min_hit_10p = min(rolling.get(f"hit_{h}y", 1.0) for h in HORIZONS_YEARS if h >= 10)
            min_p10_5p = min(rolling.get(f"p10_{h}y", 999.0) for h in HORIZONS_YEARS if h >= 5)
            min_p10_10p = min(rolling.get(f"p10_{h}y", 999.0) for h in HORIZONS_YEARS if h >= 10)
            mdd_spread = metrics.mdd - spy_metrics.mdd
            cagr_spread = metrics.cagr - spy_metrics.cagr
            preferred_pass = cagr_spread > CAGR_SPREAD_TOLERANCE and min_hit_10p >= 0.90 and (mdd_spread >= -0.05 or metrics.mdd >= -0.60)
            strict_pass = cagr_spread > CAGR_SPREAD_TOLERANCE and min_hit_5p >= 0.90 and mdd_spread >= 0.0
            effective_sp = weights.get("SPYSIM", 0.0) + 2.0 * weights.get("SSOSIM", 0.0) + 3.0 * weights.get("UPROSIM", 0.0)
            row: dict[str, float | str | bool] = {
                "name": name,
                "rebalance": freq_name,
                "weights": weight_label(weights),
                "preferred_pass": preferred_pass,
                "strict_pass": strict_pass,
                "start": metrics.start,
                "end": metrics.end,
                "years": metrics.years,
                "cagr": metrics.cagr,
                "spy_cagr": spy_metrics.cagr,
                "cagr_spread": cagr_spread,
                "mdd": metrics.mdd,
                "spy_mdd": spy_metrics.mdd,
                "mdd_spread": mdd_spread,
                "sharpe": metrics.sharpe,
                "sortino": metrics.sortino,
                "calmar": metrics.calmar,
                "terminal": metrics.terminal,
                "terminal_vs_spy": metrics.terminal / spy_metrics.terminal,
                "min_hit_5p": min_hit_5p,
                "min_hit_10p": min_hit_10p,
                "min_p10_5p": min_p10_5p,
                "min_p10_10p": min_p10_10p,
                "effective_sp500_exposure": effective_sp,
            }
            for asset in ASSETS:
                row[f"w_{asset}"] = weights.get(asset, 0.0)
            row.update(rolling)
            exact_rows.append(row)

            for regime in named_regime_stats(returns, spy_returns):
                regime_rows.append({"name": name, "rebalance": freq_name, "weights": weight_label(weights), **regime})

    exact = pd.DataFrame(exact_rows).sort_values(
        ["preferred_pass", "min_hit_10p", "cagr", "mdd"], ascending=[False, False, False, False]
    )
    regimes = pd.DataFrame(regime_rows)
    return exact, regimes


def formatted_exact_rows(frame: pd.DataFrame, limit: int = 15) -> list[dict[str, object]]:
    rows = []
    for _, row in frame.head(limit).iterrows():
        rows.append(
            {
                "Name": row["name"],
                "Rebal": row["rebalance"],
                "Weights": row["weights"],
                "CAGR": fmt_pct(row["cagr"]),
                "Spread": fmt_pp(row["cagr_spread"]),
                "MDD": fmt_pct(row["mdd"]),
                "MDD vs SPY": fmt_pp(row["mdd_spread"]),
                "10y+ hit min": fmt_pct(row["min_hit_10p"], 1),
                "5y+ hit min": fmt_pct(row["min_hit_5p"], 1),
                "10y+ p10 min": fmt_pct(row["min_p10_10p"], 1),
                "Terminal/SPY": fmt_x(row["terminal_vs_spy"]),
                "Preferred": "yes" if row["preferred_pass"] else "no",
            }
        )
    return rows


def formatted_regime_rows(frame: pd.DataFrame, selected_names: list[str]) -> list[dict[str, object]]:
    rows = []
    subset = frame[frame["name"].isin(selected_names)]
    for _, row in subset.iterrows():
        rows.append(
            {
                "Name": row["name"],
                "Rebal": row["rebalance"],
                "Regime": row["regime"],
                "Window": f"{row['start']}..{row['end']}",
                "Return": fmt_pct(row["portfolio_return"]),
                "SPY": fmt_pct(row["spy_return"]),
                "Spread": fmt_pp(row["return_spread"]),
                "MDD": fmt_pct(row["portfolio_mdd"]),
                "SPY MDD": fmt_pct(row["spy_mdd"]),
            }
        )
    return rows


def write_report(summary: pd.DataFrame, exact: pd.DataFrame, regimes: pd.DataFrame, daily_returns: pd.DataFrame) -> None:
    spy_metrics = metrics_from_returns(daily_returns["SPYSIM"])
    monthly_preferred = summary[summary["preferred_pass_monthly"]]
    exact_monthly = exact[exact["rebalance"] == "monthly"].copy()
    exact_preferred = exact[exact["preferred_pass"]]
    exact_monthly_preferred = exact_monthly[exact_monthly["preferred_pass"]]
    exact_strict = exact[exact["strict_pass"]]
    best_preferred = exact_preferred.iloc[0] if not exact_preferred.empty else None
    nearest_candidate = exact_monthly.iloc[0] if not exact_monthly.empty else None
    best_cagr = exact_monthly.sort_values("cagr", ascending=False).iloc[0]

    selected_names = ["SPY buy-hold"]
    if best_preferred is not None:
        selected_names.append(str(best_preferred["name"]))
    elif nearest_candidate is not None:
        selected_names.append(str(nearest_candidate["name"]))
    selected_names.extend(["50 SSO / 25 ZROZ / 25 GLD", "60 SSO / 40 ZROZ"])
    selected_names = list(dict.fromkeys(selected_names))

    if best_preferred is None:
        conclusion = "The first static run did not find a preferred-target candidate under daily exact diagnostics. "
    elif exact_monthly_preferred.empty:
        conclusion = "The first monthly static run did not pass the preferred target, but lower-frequency static rebalancing did. "
    elif exact_strict.empty:
        conclusion = "The first static run found preferred-target candidates for 10y+ rolling windows, but found no strict 5y+ solution. "
    else:
        conclusion = "The first static run found at least one strict 5y+ candidate, but this still needs independent validation. "
    if best_preferred is not None:
        conclusion += (
            f"The lead candidate is `{best_preferred['weights']}` with `{best_preferred['rebalance']}` rebalance, CAGR {fmt_pct(best_preferred['cagr'])}, "
            f"MDD {fmt_pct(best_preferred['mdd'])}, minimum 10y+ hit rate {fmt_pct(best_preferred['min_hit_10p'], 1)} "
            f"and terminal wealth {fmt_x(best_preferred['terminal_vs_spy'])} versus SPY."
        )
    elif nearest_candidate is not None:
        conclusion += (
            f"The nearest monthly candidate is `{nearest_candidate['weights']}` with CAGR {fmt_pct(nearest_candidate['cagr'])}, "
            f"MDD {fmt_pct(nearest_candidate['mdd'])} and minimum 10y+ hit rate {fmt_pct(nearest_candidate['min_hit_10p'], 1)}, "
            "which is below the 90% target."
        )
    else:
        conclusion += "No static candidate passed the preferred target under daily exact diagnostics."

    if best_preferred is None:
        practical = (
            "Practical conclusion: static SPY/SSO/UPRO mixes can improve CAGR versus SPY, "
            "but this full 1968+ common-window run did not reach the 90%+ long-window hit target. "
            "The static branch is therefore a near-miss, not a validated SPY replacement."
        )
    else:
        practical = (
            "Practical conclusion: static SPY/SSO/UPRO mixes can improve long-horizon return versus SPY, "
            "but five-year windows remain too regime-sensitive for a static strategy to claim near-always outperformance. "
            "The current lead is cadence-sensitive, so quarterly/annual rebalancing must be part of the specification."
        )

    sections = [
        "# SPY/SSO/UPRO Replacement - Static Phase 1 Report\n\n"
        "Status: research-only static-grid execution. This report does not authorize deployment, paper trading or mandate changes.\n\n"
        "Method references: rolling-window robustness and parameter sensitivity are diagnostics against overfit and regime dependence `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`. LETF exposure and volatility-decay caveats follow `[leverage_for_the_long_run, p.13]`.\n\n"
        "## Executive Conclusion\n\n"
        f"{conclusion}\n\n"
        f"{practical}\n\n"
        "## Source Data\n\n"
        "| Item | Value |\n|---|---|\n"
        f"| Testfol.io cache | `data/testfolio/cache/history.parquet` |\n"
        f"| Daily common window | `{daily_returns.index[0].date()}` to `{daily_returns.index[-1].date()}` |\n"
        f"| Assets | `{', '.join(ASSETS)}` |\n"
        f"| SPY baseline | CAGR {fmt_pct(spy_metrics.cagr)}, MDD {fmt_pct(spy_metrics.mdd)}, Sharpe {fmt_num(spy_metrics.sharpe)} |\n"
        f"| Grid candidates after constraints | `{len(summary):,}` |\n"
        f"| Monthly-triage preferred pass count | `{len(monthly_preferred):,}` |\n"
        f"| Exact preferred rows across cadences | `{len(exact_preferred):,}` |\n"
        f"| Exact monthly preferred rows | `{len(exact_monthly_preferred):,}` |\n"
        f"| Exact finalist rows | `{len(exact):,}` including rebalance cadence variants |\n\n"
        "The broad grid uses monthly returns for scalable triage. The finalist table below is recomputed with daily returns and exact monthly/quarterly/annual rebalancing.\n"
    ]

    sections.append(
        "## Top Exact Daily Finalists\n\n"
        "Analysis: This table is the primary result. It ranks finalist portfolios after daily exact recomputation, not just monthly triage. `Preferred=yes` means CAGR beats SPY, 10y+ rolling hit rate is at least 90%, and drawdown is no worse than SPY by more than 5pp or better than -60%.\n\n"
        + (
            "Conclusion: No listed static candidate passes the preferred target. The nearest candidates add modest SSO/UPRO exposure plus ZROZ/GLD, improving CAGR but topping out below the 90% long-window hit-rate target.\n\n"
            if best_preferred is None
            else "Conclusion: Preferred candidates exist only after allowing lower-frequency static rebalancing. The lead is a modest-leverage S&P mix with small ZROZ/GLD sleeves, not an aggressive HFEA-style portfolio.\n\n"
        )
        + md_table(
            formatted_exact_rows(exact, 25),
            ["Name", "Rebal", "Weights", "CAGR", "Spread", "MDD", "MDD vs SPY", "10y+ hit min", "5y+ hit min", "10y+ p10 min", "Terminal/SPY", "Preferred"],
        )
    )

    sections.append(
        "## Rebalance Cadence Sensitivity\n\n"
        "Analysis: Rebalance cadence matters because LETF drawdowns interact with when the portfolio buys back into the levered sleeve. Quarterly and annual variants can materially change drawdown and terminal wealth.\n\n"
        "Conclusion: Static does not mean cadence-free. Any implementation candidate must specify rebalance frequency explicitly.\n\n"
        + md_table(
            formatted_exact_rows(exact[exact["name"].isin(selected_names)].sort_values(["name", "rebalance"]), 60),
            ["Name", "Rebal", "Weights", "CAGR", "Spread", "MDD", "MDD vs SPY", "10y+ hit min", "5y+ hit min", "10y+ p10 min", "Terminal/SPY", "Preferred"],
        )
    )

    sections.append(
        "## Named-Regime Stress\n\n"
        "Analysis: The preferred static mixes tend to improve long-run terminal wealth but can still suffer hard in equity-led crashes. ZROZ helps in classic equity crashes, but 2022-style stock/bond correlation shocks remain the key static-portfolio weakness.\n\n"
        "Conclusion: Static LETF replacement candidates must be judged mainly by whether their 2022 and recent-window behavior is tolerable, not only by full-history CAGR.\n\n"
        + md_table(
            formatted_regime_rows(regimes, selected_names),
            ["Name", "Rebal", "Regime", "Window", "Return", "SPY", "Spread", "MDD", "SPY MDD"],
        )
    )

    sections.append(
        "## Static Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Does a static candidate beat SPY CAGR? | Yes; best monthly exact finalist CAGR is {fmt_pct(best_cagr['cagr'])}. |\n"
        f"| Does a static candidate pass the preferred 10y+ target? | {'Yes' if best_preferred is not None else 'No'}. |\n"
        f"| Does a static candidate pass strict 5y+ 90% hit with no worse MDD than SPY? | {'Yes' if not exact_strict.empty else 'No'}. |\n"
        "| Is this enough to claim a guaranteed SPY replacement? | No. It is enough to continue with focused robustness, not to deploy. |\n\n"
        "Recommended next step: run Phase 1b around the lead static family with finer weights, explicit fee/drag stress and rolling daily drawdown diagnostics. If strict 5y+ behavior remains impossible, move to Phase 2 low-turnover LRS overlay.\n"
    )

    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    frame = load_testfolio_frame()
    daily_prices = frame[ASSETS].dropna()
    daily_returns = daily_prices.pct_change().dropna()
    monthly_prices = daily_prices.resample("ME").last().dropna()
    monthly_returns = monthly_prices.pct_change().dropna()

    grid = generate_weight_grid()
    summary = triage_grid(monthly_returns, grid)
    summary.to_csv(RESULTS / "static_grid_summary.csv", index=False)

    finalists = select_finalists(summary)
    exact, regimes = exact_evaluate(daily_returns, finalists)
    exact.to_csv(RESULTS / "static_exact_finalists.csv", index=False)
    exact[exact["name"].isin(PREDEFINED)].to_csv(RESULTS / "static_predefined_exact.csv", index=False)
    regimes.to_csv(RESULTS / "static_regime_stress.csv", index=False)
    write_report(summary, exact, regimes, daily_returns)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
