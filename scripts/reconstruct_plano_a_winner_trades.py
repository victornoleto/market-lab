"""Reconstruct the per-leg trade log for the Phase 3.5a-V2 winner
(``gayed_ema100_L2_off_gld``) by re-running ``simulate_plano_a_rotation``
with the winner config (deterministic — same inputs, same outputs) and
deriving entry/exit events from the resulting ``weights`` DataFrame.

The V2 framework persisted only aggregate stats (``n_switches_total``,
``switches_by_ticker``) plus daily returns. It never wrote a trade log.
This script closes that gap for the one config that actually matters.

Output
------
reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/trade_log.csv
reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/trade_log.md

Columns
-------
leg, entry_date, exit_date, hold_days, weight, entry_price, exit_price,
gross_ret_pct (underlying), leveraged_ret_pct (× L applied on risk-on legs),
split (IS / OOS / FWD)

Citation
--------
Winner config and strategy: ``[leverage_for_the_long_run, p.11-14]``.
Trade log convention matches scripts/run_phase3_5b_task_a_2leg.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ai_trade.backtest.strategies.plano_a_leveraged_rotation import (  # noqa: E402
    PlanoALeveragedRotationConfig,
    simulate_plano_a_rotation,
)

OUT_DIR = Path("reports/phase3_5a_v2/v2_l2_gayed_transported_cfd")
WINNER_JSON = OUT_DIR / "gayed_ema100_L2_off_gld.json"
UNIVERSE_PATH = Path("data/universe_plano_a_v2.json")
TIINGO_DAILY_DIR = Path("data/tiingo/daily/prices")

IS_END = pd.Timestamp("2017-12-31")
OOS_END = pd.Timestamp("2023-12-31")


def _parquet_key_for(ticker: str) -> str:
    u = json.loads(UNIVERSE_PATH.read_text())
    for inst in u["instruments"]:
        if inst["ticker"] == ticker:
            return inst["parquet_key"]
    return ticker


def _load_close(ticker_key: str) -> pd.DataFrame:
    path = TIINGO_DAILY_DIR / f"{ticker_key}.parquet"
    df = pd.read_parquet(path)
    df.index = pd.DatetimeIndex(df.index)
    return df


def _split_for(date: pd.Timestamp) -> str:
    if date <= IS_END:
        return "IS"
    if date <= OOS_END:
        return "OOS"
    return "FWD"


def _extract_segments(
    weights_col: pd.Series, price_col: pd.Series, leg_name: str, leverage: float,
    is_risk_on: bool,
) -> list[dict]:
    """Walk a weights series and emit one record per 0→positive→0 segment."""
    segs: list[dict] = []
    in_seg = False
    entry_date: pd.Timestamp | None = None
    entry_price: float = float("nan")
    weight: float = 0.0

    wv = weights_col.values
    pv = price_col.values
    idx = weights_col.index

    for i in range(len(wv)):
        w = wv[i]
        p = pv[i]
        if w > 1e-9 and not in_seg:
            in_seg = True
            entry_date = idx[i]
            entry_price = float(p)
            weight = float(w)
        elif w <= 1e-9 and in_seg:
            exit_date = idx[i]
            exit_price = float(pv[i])
            gross = (exit_price / entry_price - 1.0) if entry_price > 0 else 0.0
            effective_L = leverage if is_risk_on else 1.0
            lev_ret = gross * effective_L
            segs.append({
                "leg": leg_name,
                "entry_date": entry_date,
                "exit_date": exit_date,
                "hold_days": int((exit_date - entry_date).days),
                "weight": round(weight, 4),
                "entry_price": round(entry_price, 4),
                "exit_price": round(exit_price, 4),
                "gross_ret_pct": round(gross * 100.0, 4),
                "leveraged_ret_pct": round(lev_ret * 100.0, 4),
                "split": _split_for(entry_date),
            })
            in_seg = False

    if in_seg and entry_date is not None:
        exit_date = idx[-1]
        exit_price = float(pv[-1])
        gross = (exit_price / entry_price - 1.0) if entry_price > 0 else 0.0
        effective_L = leverage if is_risk_on else 1.0
        segs.append({
            "leg": leg_name,
            "entry_date": entry_date,
            "exit_date": exit_date,
            "hold_days": int((exit_date - entry_date).days),
            "weight": round(weight, 4),
            "entry_price": round(entry_price, 4),
            "exit_price": round(exit_price, 4),
            "gross_ret_pct": round(gross * 100.0, 4),
            "leveraged_ret_pct": round(gross * effective_L * 100.0, 4),
            "split": _split_for(entry_date) + "*open",
        })

    return segs


def main() -> None:
    winner = json.loads(WINNER_JSON.read_text())
    ce = winner["config_entry"]
    risk_on_tickers = list(ce["risk_on_assets"])
    off_regime = str(ce["off_regime_asset"]).lower()
    leverage = float(ce["leverage"])

    print(f"winner config: {winner['config_name']}")
    print(f"  risk-on: {risk_on_tickers} · leverage {leverage}× · off: {off_regime}")

    cfg = PlanoALeveragedRotationConfig(
        regime_signal=ce["regime_signal"],
        leverage=leverage,
        off_regime_asset=off_regime,
        risk_on_tickers=tuple(risk_on_tickers),
    )

    risk_on_panel = {t: _load_close(_parquet_key_for(t)) for t in risk_on_tickers}
    off_panel = None
    if off_regime in ("tlt", "gld"):
        off_panel = {off_regime: _load_close(_parquet_key_for(off_regime.upper()))}

    result = simulate_plano_a_rotation(risk_on_panel, cfg, off_regime_panel=off_panel)

    print(f"  n_bars: {len(result.daily_returns)}  "
          f"n_switches_total: {result.n_switches_total}  "
          f"median_hold: {result.median_hold_days:.2f}d")

    common_idx = result.weights.index
    close_df = pd.DataFrame(
        {t: risk_on_panel[t]["close"].astype(float).reindex(common_idx).ffill()
         for t in risk_on_tickers},
        index=common_idx,
    )
    if off_panel is not None:
        off_close = off_panel[off_regime]["close"].astype(float).reindex(common_idx).ffill()
    else:
        off_close = pd.Series(1.0, index=common_idx)  # cash: constant price proxy

    segs: list[dict] = []
    for t in risk_on_tickers:
        segs.extend(_extract_segments(
            result.weights[t], close_df[t], leg_name=t,
            leverage=leverage, is_risk_on=True,
        ))
    off_col = f"off_{off_regime}"
    segs.extend(_extract_segments(
        result.weights[off_col], off_close, leg_name=off_regime.upper(),
        leverage=1.0, is_risk_on=False,
    ))

    df = pd.DataFrame(segs)
    df = df.sort_values(["entry_date", "leg"]).reset_index(drop=True)
    df["entry_date"] = df["entry_date"].dt.strftime("%Y-%m-%d")
    df["exit_date"] = df["exit_date"].dt.strftime("%Y-%m-%d")

    csv_path = OUT_DIR / "trade_log.csv"
    df.to_csv(csv_path, index=False)
    print(f"wrote {csv_path}  ({len(df)} trades)")

    counts = df.groupby("leg").size().to_dict()
    splits = df.groupby("split").size().to_dict()
    mean_gross = df.groupby("leg")["gross_ret_pct"].mean().round(3).to_dict()
    mean_lev = df.groupby("leg")["leveraged_ret_pct"].mean().round(3).to_dict()
    win_rate = (df["leveraged_ret_pct"] > 0).mean() * 100.0
    hold_by_leg = df.groupby("leg")["hold_days"].median().to_dict()

    md_lines: list[str] = []
    md_lines.append("# Trade log — Plano A winner (`gayed_ema100_L2_off_gld`)")
    md_lines.append("")
    md_lines.append("Reconstructed by re-running `simulate_plano_a_rotation` with the winner "
                    "config from `gayed_ema100_L2_off_gld.json` (deterministic). Each row = "
                    "one continuous hold segment per leg (entry when weight 0→positive, exit "
                    "when positive→0).")
    md_lines.append("")
    first_off_price_date = None
    if off_panel is not None:
        off_raw = off_panel[off_regime]["close"].astype(float)
        first_off_price_date = pd.Timestamp(off_raw.sort_index().index[0])
    if first_off_price_date is not None and first_off_price_date > common_idx[0]:
        n_pre = int((common_idx < first_off_price_date).sum())
        pct_pre = n_pre / len(common_idx) * 100.0
        md_lines.append(
            f"> **Data caveat:** `{off_regime.upper()}` first bar is "
            f"`{first_off_price_date.date()}`; the strategy ran {n_pre} bars "
            f"({pct_pre:.1f}% of history) before that. Off-regime days in that "
            f"window earned **0%** (silent cash fallback) rather than the intended "
            f"`{off_regime.upper()}` return. Post-inception behaviour is authentic."
        )
        md_lines.append("")

    md_lines.append("## Summary")
    md_lines.append("")
    md_lines.append(f"- Total segments: **{len(df)}**")
    md_lines.append(f"- By leg: {counts}")
    md_lines.append(f"- By split: {splits}")
    md_lines.append(f"- Win rate (leveraged return > 0): **{win_rate:.1f}%**")
    md_lines.append(f"- Median hold days by leg: {hold_by_leg}")
    md_lines.append(f"- Mean gross return % by leg (underlying): {mean_gross}")
    md_lines.append(f"- Mean leveraged return % by leg (× L applied on risk-on): {mean_lev}")
    md_lines.append("")
    md_lines.append(f"**Cross-check vs gate JSON:** n_switches_total = {result.n_switches_total} "
                    f"(SPY={result.switches_by_ticker['SPY']}, QQQ={result.switches_by_ticker['QQQ']}). "
                    f"Each risk-on trade = 2 switches (entry + exit), so expected SPY trades "
                    f"≈ {result.switches_by_ticker['SPY'] // 2 + 1} and QQQ trades "
                    f"≈ {result.switches_by_ticker['QQQ'] // 2 + 1}. Observed in this log: "
                    f"SPY={counts.get('SPY', 0)}, QQQ={counts.get('QQQ', 0)}.")
    md_lines.append("")

    def _md_table(sub: pd.DataFrame) -> str:
        cols = list(sub.columns)
        out = ["| " + " | ".join(cols) + " |",
               "|" + "|".join("---" for _ in cols) + "|"]
        for _, row in sub.iterrows():
            out.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
        return "\n".join(out)

    md_lines.append("## First 10 trades (chronological)")
    md_lines.append("")
    md_lines.append(_md_table(df.head(10)))
    md_lines.append("")

    md_lines.append("## Last 10 trades")
    md_lines.append("")
    md_lines.append(_md_table(df.tail(10)))
    md_lines.append("")

    md_lines.append("## Top 10 by |leveraged_ret_pct|")
    md_lines.append("")
    top = df.iloc[df["leveraged_ret_pct"].abs().sort_values(ascending=False).head(10).index]
    md_lines.append(_md_table(top))
    md_lines.append("")

    md_lines.append("## Full log")
    md_lines.append("")
    md_lines.append(f"See `trade_log.csv` for all {len(df)} rows.")

    md_path = OUT_DIR / "trade_log.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()
