"""Cross-validate Tiingo BTC/ETH daily against Kraken public OHLC API.

Report-only: prints a summary of Tiingo-vs-Kraken close-price agreement
on a recent sample window (default last 90 days). Does NOT write new
parquet — Tiingo crypto daily has been verified as clean (no weekend
pollution, 28.6% weekend bars as expected for 7d/week markets) in the
Phase 3.7-2 audit. This script exists so future sessions can quickly
re-confirm integrity without re-running the full audit.

Kraken public OHLC is free and auth-less. Rate limit: 1 req/sec per IP.

Output: logs to stdout + logs/phase3_7_data_sprint.log. Non-zero exit
if agreement is < 99.5% (indicates material divergence requiring attention).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent))
from _utils import REPO_ROOT, retry, setup_logger  # noqa: E402

KRAKEN_PAIR = {"btcusd": "XBTUSD", "ethusd": "ETHUSD"}
KRAKEN_URL = "https://api.kraken.com/0/public/OHLC"


def fetch_kraken_daily(pair: str, since_unix: int, log) -> pd.DataFrame:
    def _call() -> dict:
        r = requests.get(
            KRAKEN_URL,
            params={"pair": pair, "interval": 1440, "since": since_unix},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()

    data = retry(_call, log=log)
    if data.get("error"):
        raise RuntimeError(f"Kraken error: {data['error']}")
    result = data["result"]
    pair_key = next(k for k in result.keys() if k != "last")
    rows = result[pair_key]
    df = pd.DataFrame(
        rows,
        columns=["time", "open", "high", "low", "close", "vwap", "volume", "count"],
    )
    df["time"] = pd.to_datetime(df["time"].astype(int), unit="s").dt.normalize()
    df = df.set_index("time")
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c])
    return df[["open", "high", "low", "close", "volume"]]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--days", type=int, default=90)
    args = ap.parse_args()
    log = setup_logger("audit_crypto_integrity")

    since = pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(days=args.days)
    since_unix = int(since.timestamp())

    all_agree = True
    for ticker, kraken_pair in KRAKEN_PAIR.items():
        tiingo_path = REPO_ROOT / "data" / "tiingo" / "daily" / "prices" / f"{ticker}.parquet"
        if not tiingo_path.exists():
            log.warning("no Tiingo parquet for %s — skip", ticker)
            continue
        tiingo = pd.read_parquet(tiingo_path)
        tiingo.index = pd.to_datetime(tiingo.index).tz_localize(None).normalize()
        tiingo = tiingo[tiingo.index >= since][["close"]].rename(columns={"close": "tiingo_close"})

        log.info("kraken fetch %s since=%s", kraken_pair, since.date())
        kraken = fetch_kraken_daily(kraken_pair, since_unix, log)
        kraken = kraken[["close"]].rename(columns={"close": "kraken_close"})
        time.sleep(1.0)

        joined = tiingo.join(kraken, how="inner")
        if joined.empty:
            log.warning("%s: no overlapping days between Tiingo and Kraken", ticker)
            continue
        rel_diff = (joined["tiingo_close"] - joined["kraken_close"]).abs() / joined["kraken_close"]
        mean_diff = float(rel_diff.mean())
        max_diff = float(rel_diff.max())
        n = len(joined)
        pct_within_50bps = float((rel_diff < 0.005).mean())
        log.info(
            "%s: n=%d mean_rel_diff=%.4f%% max_rel_diff=%.4f%% within_50bps=%.2f%%",
            ticker, n, mean_diff * 100, max_diff * 100, pct_within_50bps * 100,
        )
        if pct_within_50bps < 0.995:
            log.error("%s AGREEMENT < 99.5%% — MATERIAL divergence", ticker)
            all_agree = False

    return 0 if all_agree else 1


if __name__ == "__main__":
    raise SystemExit(main())
