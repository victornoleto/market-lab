"""Universe screener — Phase 3.5a-V2 V2-L0 [atomic]

Builds `data/universe_plano_a_v2.json` + `reports/phase3_5a_v2/L0_universe_screener.md`
with per-instrument metadata (first_dt, last_dt, n_bars, vol_252d,
hurst_100d, corr_spy, adv_usd_last252, asset_class) over the longest
Tiingo daily cache window per ticker.

Citations:
- `[advances_fin_ml, ch.2]` — data integrity pre-screen.
- `[systematic_trading, p.~90-100]` — universe selection breadth.
- `[algo_trading_chan, p.44-46, ch.2]` — Hurst exponent via structure function.

Run once from V2-L0 iter. No sweep, no registry.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.tiingo_storage import TiingoStorage
from ai_trade.backtest.screener.hurst import hurst_exponent

ROOT = Path(__file__).resolve().parents[1]
TIINGO_ROOT = ROOT / "data" / "tiingo"
OUT_JSON = ROOT / "data" / "universe_plano_a_v2.json"
OUT_MD = ROOT / "reports" / "phase3_5a_v2" / "L0_universe_screener.md"

# Universe per specs/phase_3_5a_v2.md §2.
UNIVERSE: list[tuple[str, str, str]] = [
    # (display_ticker, parquet_key, asset_class)
    # Equity index proxies
    ("SPY", "SPY", "etf"),
    ("QQQ", "QQQ", "etf"),
    ("DIA", "DIA", "etf"),
    ("IWM", "IWM", "etf"),
    ("EFA", "EFA", "etf"),
    ("EEM", "EEM", "etf"),
    # Sector ETFs (SPDR 11 sectors)
    ("XLK", "XLK", "etf"),
    ("XLF", "XLF", "etf"),
    ("XLE", "XLE", "etf"),
    ("XLV", "XLV", "etf"),
    ("XLI", "XLI", "etf"),
    ("XLY", "XLY", "etf"),
    ("XLP", "XLP", "etf"),
    ("XLU", "XLU", "etf"),
    ("XLB", "XLB", "etf"),
    ("XLRE", "XLRE", "etf"),
    ("XLC", "XLC", "etf"),
    # Commodities
    ("GLD", "GLD", "etf"),
    ("SLV", "SLV", "etf"),
    ("USO", "USO", "etf"),
    ("UNG", "UNG", "etf"),
    ("DBA", "DBA", "etf"),
    # Fixed income
    ("TLT", "TLT", "etf"),
    ("IEF", "IEF", "etf"),
    ("HYG", "HYG", "etf"),
    ("LQD", "LQD", "etf"),
    # FX majors + metals (daily Tiingo forex endpoint, lowercase key)
    ("EURUSD", "eurusd", "forex"),
    ("GBPUSD", "gbpusd", "forex"),
    ("USDJPY", "usdjpy", "forex"),
    ("AUDUSD", "audusd", "forex"),
    ("USDCAD", "usdcad", "forex"),
    ("NZDUSD", "nzdusd", "forex"),
    ("USDCHF", "usdchf", "forex"),
    ("EURJPY", "eurjpy", "forex"),
    ("EURGBP", "eurgbp", "forex"),
    ("GBPJPY", "gbpjpy", "forex"),
    ("XAUUSD", "xauusd", "forex"),
    ("XAGUSD", "xagusd", "forex"),
    # Crypto
    ("BTCUSD", "btcusd", "crypto"),
]


def _annualization_factor(asset_class: str) -> float:
    """Trading periods per year for vol annualization."""
    if asset_class == "crypto":
        return 365.0
    if asset_class == "forex":
        return 260.0  # 5-day forex week ≈ 260 bars
    return 252.0  # equity/ETF


def _trailing(series: pd.Series, n: int) -> pd.Series:
    return series.tail(n) if len(series) >= n else series


def _vol_ann(returns: pd.Series, asset_class: str) -> float:
    if returns.empty:
        return float("nan")
    return float(returns.std(ddof=1) * np.sqrt(_annualization_factor(asset_class)))


def _adv_usd(df: pd.DataFrame, n: int = 252) -> float:
    """Approx. average daily dollar volume over last n bars."""
    if "volume" not in df.columns or df["volume"].isna().all():
        return float("nan")
    tail = df.tail(n)
    close = tail["close"].astype(float)
    vol = tail["volume"].astype(float)
    return float((close * vol).mean())


def main() -> None:
    storage = TiingoStorage(TIINGO_ROOT)
    manifest = storage.manifest

    # Load SPY first for corr basis.
    spy_df = storage.read("SPY", frequency="daily").sort_index()
    spy_ret = spy_df["close"].astype(float).pct_change().dropna()

    rows: list[dict] = []
    errors: list[dict] = []
    for display, key, asset_class in UNIVERSE:
        entry = manifest.get(key, {}).get("daily")
        if entry is None:
            errors.append({"ticker": display, "reason": "not in manifest"})
            continue
        try:
            df = storage.read(key, frequency="daily").sort_index()
        except Exception as exc:
            errors.append({"ticker": display, "reason": f"read failed: {exc}"})
            continue

        if df.empty or "close" not in df.columns:
            errors.append({"ticker": display, "reason": "empty/missing close"})
            continue

        close = df["close"].astype(float)
        ret = close.pct_change().dropna()
        vol_252 = _vol_ann(_trailing(ret, 252), asset_class)

        # Hurst on last 252 bars (100 min observations enforced by helper).
        hurst_val: float | None = None
        hurst_r2: float | None = None
        try:
            tail_close = _trailing(close.dropna(), 252)
            h = hurst_exponent(tail_close, min_obs=100)
            hurst_val = float(h.h)
            hurst_r2 = float(h.r2)
        except ValueError as exc:
            hurst_val = None
            hurst_r2 = None
            errors.append({"ticker": display, "reason": f"hurst failed: {exc}"})

        # Corr vs SPY over last 252 aligned daily dates.
        if display == "SPY":
            corr_spy = 1.0
        else:
            tail_ret = _trailing(ret, 252)
            aligned = pd.concat(
                [tail_ret.rename("x"), spy_ret.rename("spy")], axis=1, join="inner"
            ).dropna()
            if len(aligned) >= 30:
                corr_spy = float(aligned["x"].corr(aligned["spy"]))
            else:
                corr_spy = float("nan")

        adv_usd = _adv_usd(df, 252)

        row = {
            "ticker": display,
            "parquet_key": key,
            "asset_class": asset_class,
            "first_dt": entry["first_dt"][:10],
            "last_dt": entry["last_dt"][:10],
            "n_bars": int(entry["n_bars"]),
            "vol_252d_ann": round(vol_252, 6),
            "hurst_100d": round(hurst_val, 4) if hurst_val is not None else None,
            "hurst_r2": round(hurst_r2, 4) if hurst_r2 is not None else None,
            "corr_spy_252d": round(corr_spy, 4) if not np.isnan(corr_spy) else None,
            "adv_usd_252d": round(adv_usd, 0) if not np.isnan(adv_usd) else None,
        }
        rows.append(row)

    payload = {
        "schema_version": 1,
        "phase": "3.5a-v2",
        "lead": "V2-L0",
        "built_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "n_instruments": len(rows),
        "errors": errors,
        "citations": [
            "advances_fin_ml, ch.2",
            "systematic_trading, p.~90-100",
            "algo_trading_chan, p.44-46, ch.2",
        ],
        "instruments": rows,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT_JSON.with_suffix(".json.tmp")
    with open(tmp, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=False)
        fh.flush()
    tmp.replace(OUT_JSON)
    print(f"Wrote {OUT_JSON} ({len(rows)} instruments, {len(errors)} errors).")

    # Markdown report.
    lines: list[str] = []
    lines.append("# V2-L0 — Universe screener (Phase 3.5a-V2)\n")
    lines.append(
        f"**Built:** {payload['built_at']} | **Instruments:** {len(rows)} | "
        f"**Errors:** {len(errors)}\n"
    )
    lines.append("**Source:** Tiingo daily cache (`data/tiingo/daily/prices/*.parquet`).")
    lines.append(
        "**Window per ticker:** longest available (`first_dt → last_dt` from manifest)."
    )
    lines.append("")
    lines.append(
        "Citations: `[advances_fin_ml, ch.2]`, `[systematic_trading, p.~90-100]`, "
        "`[algo_trading_chan, p.44-46, ch.2]`.\n"
    )

    # Summary table per asset class.
    lines.append("## Summary by asset class\n")
    lines.append("| Asset class | N | Avg n_bars | Avg vol_252d | Avg Hurst100 | Avg corr_SPY |")
    lines.append("|-------------|--:|-----------:|-------------:|-------------:|-------------:|")
    df_rows = pd.DataFrame(rows)
    for ac, grp in df_rows.groupby("asset_class"):
        n = len(grp)
        avg_bars = grp["n_bars"].mean()
        avg_vol = grp["vol_252d_ann"].mean()
        avg_h = grp["hurst_100d"].dropna().mean() if "hurst_100d" in grp else float("nan")
        avg_c = grp["corr_spy_252d"].dropna().mean() if "corr_spy_252d" in grp else float("nan")
        lines.append(
            f"| {ac} | {n} | {avg_bars:.0f} | {avg_vol:.3f} | "
            f"{avg_h:.3f} | {avg_c:.3f} |"
        )
    lines.append("")

    # Full table.
    lines.append("## Full per-ticker table\n")
    lines.append(
        "| Ticker | Class | first_dt | last_dt | n_bars | vol_252 | Hurst100 | H-R² | corr_SPY | ADV USD |"
    )
    lines.append(
        "|--------|-------|---------|---------|------:|--------:|--------:|-----:|--------:|--------:|"
    )
    for r in rows:
        adv = (
            f"{r['adv_usd_252d']:.2e}"
            if r["adv_usd_252d"] is not None
            else "—"
        )
        h = f"{r['hurst_100d']:.3f}" if r["hurst_100d"] is not None else "—"
        hr2 = f"{r['hurst_r2']:.2f}" if r["hurst_r2"] is not None else "—"
        cs = (
            f"{r['corr_spy_252d']:.3f}"
            if r["corr_spy_252d"] is not None
            else "—"
        )
        lines.append(
            f"| {r['ticker']} | {r['asset_class']} | {r['first_dt']} | "
            f"{r['last_dt']} | {r['n_bars']} | {r['vol_252d_ann']:.3f} | "
            f"{h} | {hr2} | {cs} | {adv} |"
        )
    lines.append("")

    # Flags: staleness, low liquidity, short windows.
    today = pd.Timestamp.today().normalize()
    stale_cutoff = today - pd.Timedelta(days=60)
    stale = [r for r in rows if pd.Timestamp(r["last_dt"]) < stale_cutoff]
    short_win = [r for r in rows if r["n_bars"] < 1500]
    low_adv = [
        r
        for r in rows
        if r["adv_usd_252d"] is not None and r["adv_usd_252d"] < 10_000_000
    ]

    lines.append("## Integrity flags\n")
    lines.append(
        f"- Stale (last_dt older than 60d): {len(stale)} — "
        + ", ".join(f"{r['ticker']}({r['last_dt']})" for r in stale)
    )
    lines.append(
        f"- Short window (< 1500 bars ≈ < 6y): {len(short_win)} — "
        + ", ".join(f"{r['ticker']}({r['n_bars']})" for r in short_win)
    )
    lines.append(
        f"- Low ADV USD (< $10M): {len(low_adv)} — "
        + ", ".join(f"{r['ticker']}" for r in low_adv)
    )
    if errors:
        lines.append(f"- Errors: {len(errors)}")
        for e in errors:
            lines.append(f"  - {e['ticker']}: {e['reason']}")
    else:
        lines.append("- Errors: 0")
    lines.append("")

    lines.append("## Verdict for downstream leads\n")
    lines.append(
        "- Total instruments present: **{n}** (target ≥ 30). {verdict}".format(
            n=len(rows),
            verdict="PASS — V2-L0 gate satisfied." if len(rows) >= 30 else "FAIL",
        )
    )
    lines.append(
        "- Short-window instruments (< 6y daily) excluded from V2-L1/L2/L6 "
        "IS partitioning; still usable in V2-L5 equity pairs if peer exists."
    )
    lines.append(
        "- Stale instruments deprioritized in V2-L1/L2/L6. V2-L3 meta-label "
        "CPCV can handle shorter windows."
    )
    lines.append("")
    lines.append("## Next lead\n")
    lines.append(
        "V2-L1 — TSMOM multi-asset daily [sweep-configs] (14 iters expected). "
        "Bootstrap registry populates `configs` (4 lookbacks × 3 vol targets = 12) "
        "and `tickers_pending` derived from this universe minus stale/short-flagged tickers."
    )
    lines.append("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    tmp_md = OUT_MD.with_suffix(".md.tmp")
    with open(tmp_md, "w") as fh:
        fh.write("\n".join(lines))
    tmp_md.replace(OUT_MD)
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
