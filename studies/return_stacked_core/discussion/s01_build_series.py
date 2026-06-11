#!/usr/bin/env python3
"""s01 — build discussion-local proxy series into ``series/`` with meta sidecars.

Outputs (all daily simple returns unless noted):

- ``series/primary_returns.parquet`` — the merged primary matrix (2000+),
  saved so downstream figures consume artifacts only.
- ``series/proxy_returns.parquet`` — RSSXSIM, TLTPROXY, TMFSIM_D on the
  primary calendar (RSSX NaN before 2010-07-20).
- ``series/extended_returns.parquet`` — 1970+ LOW-fidelity matrix incl.
  KMLM_SPLICED, RSST_EXT, RSST_EXT_HAIRCUT, TLTPROXY, TMFSIM_D (skipped
  loudly if Ken French CSVs are absent).
- ``series/rssy_monthly.parquet`` — MONTHLY returns: CARRY_SCALED, RSSYSIM
  plus monthly-compounded core sleeves (skipped loudly if AQR CSV absent).
  RSSY is monthly-native; it must never enter daily tables.
- ``series/series_meta.json`` — formula + window + provenance per series.

Proxy formulas replicate the repo's stacked-proxy financing model
(weighted returns minus excess-notional CASHX) from
``scripts/build_stacked_sim_proxies.py`` `[leverage_for_the_long_run, p.13]`.
RSSX spec (100% SPY + 80% gold + 20% BTC) mirrors ``PROXIES["RSSXSIM"]`` there;
BTCSIM carries structural survivorship and non-stationarity bias — treat any
RSSX result as assumption-heavy, not evidence `[testing_tuning, p.327-335]`.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.return_stacked_core.discussion import discussion_data as dd  # noqa: E402

TRADING_DAYS = dd.TRADING_DAYS
TMF_ER_ANNUAL = 0.0106  # Direxion TMF expense ratio
RSSY_VOL_TARGET = 0.10  # carry sleeve scaled to 10% annualized vol (in-sample scalar)
KMLM_INCEPTION = pd.Timestamp("1987-12-31")


def build_proxies(primary: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    meta: dict[str, dict] = {}
    out = pd.DataFrame(index=primary.index)

    # RSSX: 100% SPY + 80% gold + 20% BTC, 100% excess notional financed at CASHX.
    rssx = (
        1.0 * primary["SPYSIM"]
        + 0.8 * primary["GLDSIM"]
        + 0.2 * primary["BTCSIM"]
        - 0.8 * primary["CASHX"]
    )
    out["RSSXSIM"] = rssx
    first = rssx.dropna().index[0]
    meta["RSSXSIM"] = {
        "formula": "1.0*SPYSIM + 0.8*GLDSIM + 0.2*BTCSIM - 0.8*CASHX (daily returns)",
        "source_spec": "scripts/build_stacked_sim_proxies.py PROXIES['RSSXSIM']",
        "window_start": str(first.date()),
        "caveat": (
            "BTCSIM history starts 2010-07; structural survivorship and "
            "non-stationarity bias — assumption-heavy proxy, not evidence."
        ),
    }

    # TLT proxy: 50/50 ZROZ/IEF duration blend (~0.5*27y + 0.5*7.6y ≈ 17y ≈ TLT).
    tlt = 0.5 * primary["ZROZSIM"] + 0.5 * primary["IEFSIM"]
    out["TLTPROXY"] = tlt
    meta["TLTPROXY"] = {
        "formula": "0.5*ZROZSIM + 0.5*IEFSIM (daily returns)",
        "rationale": "duration blend ~17y matches TLT; cache has no TLTSIM",
    }

    # TMF: daily 3x TLT with explicit 2x cash borrow + ER drag.
    tmf = 3.0 * tlt - 2.0 * primary["CASHX"] - TMF_ER_ANNUAL / TRADING_DAYS
    out["TMFSIM_D"] = tmf
    meta["TMFSIM_D"] = {
        "formula": "3*TLTPROXY - 2*CASHX - 0.0106/252 (daily reset)",
        "citation": "[leverage_for_the_long_run, ch.3-4]",
        "note": (
            "financing-explicit; synths.tmf_synth_returns omits the 2x cash "
            "borrow and is not used (decision documented in METHODS.md)"
        ),
    }
    return out, meta


def build_extended() -> tuple[pd.DataFrame | None, dict]:
    if not dd.ken_french_available():
        print(
            "WARNING: data/ken_french/ CSVs missing — extended 1970+ matrix "
            "SKIPPED. See README.md for the one-time download.",
            file=sys.stderr,
        )
        return None, {
            "extended": {"status": "SKIPPED — Ken French CSVs missing"}
        }

    ext = dd.load_extended_returns()
    cash = ext["CASHX"]
    kmlm = ext["KMLM_SPLICED"]

    # Haircut: pre-1988 MF *excess over cash* scaled x0.5 — the UMD splice
    # overstates KMLM-like Sharpe ~3x (datasets.py warning).
    pre = ext.index < KMLM_INCEPTION
    kmlm_haircut = kmlm.copy()
    kmlm_haircut[pre] = cash[pre] + 0.5 * (kmlm[pre] - cash[pre])

    drag = dd.FINANCING_SPREAD_ANNUAL / TRADING_DAYS
    ext["RSST_EXT"] = ext["SPYSIM"] + kmlm - (cash + drag)
    ext["RSST_EXT_HAIRCUT"] = ext["SPYSIM"] + kmlm_haircut - (cash + drag)
    ext["TLTPROXY"] = 0.5 * ext["ZROZSIM"] + 0.5 * ext["IEFSIM"]
    ext["TMFSIM_D"] = 3.0 * ext["TLTPROXY"] - 2.0 * cash - TMF_ER_ANNUAL / TRADING_DAYS

    meta = {
        "extended": {
            "status": "BUILT",
            "fidelity": "LOW",
            "window": f"{ext.index[0].date()}..{ext.index[-1].date()}",
            "RSST_EXT": "SPYSIM + 1.0*KMLM_SPLICED - (CASHX + 0.0200/252)",
            "RSST_EXT_HAIRCUT": (
                "same, with pre-1988 MF excess over CASHX scaled x0.5 "
                "(UMD splice overstates MF Sharpe ~3x)"
            ),
            "caveats": [
                "KMLM pre-1988 = Ken French UMD + RF academic momentum proxy",
                "gold price administered until 1971-08 (Bretton Woods)",
                "[stocks_on_the_move, p.21-30] momentum-as-trend-proxy rationale",
            ],
        }
    }
    return ext, meta


def build_rssy_monthly(primary: pd.DataFrame) -> tuple[pd.DataFrame | None, dict]:
    try:
        carry = dd.load_carry_monthly()
    except FileNotFoundError as exc:
        print(f"WARNING: {exc} — RSSY monthly matrix SKIPPED.", file=sys.stderr)
        return None, {"rssy_monthly": {"status": "SKIPPED — AQR carry CSV missing"}}

    scale = RSSY_VOL_TARGET / (carry.std(ddof=0) * np.sqrt(12.0))
    carry_scaled = carry * scale

    monthly = dd.monthly_returns(
        primary[["SPYSIM", "GDESIM", "RSSTSIM", "ZROZSIM", "CASHX"]]
    )
    # AQR months are business-month-end; align both to month periods.
    carry_scaled.index = carry_scaled.index.to_period("M")
    monthly.index = monthly.index.to_period("M")
    common = monthly.index.intersection(carry_scaled.index)
    out = monthly.loc[common].copy()
    out["CARRY_SCALED"] = carry_scaled.loc[common]
    out["RSSYSIM"] = (
        out["SPYSIM"] + out["CARRY_SCALED"] - dd.FINANCING_SPREAD_ANNUAL / 12.0
    )
    out.index = out.index.to_timestamp("M")

    meta = {
        "rssy_monthly": {
            "status": "BUILT",
            "formula": (
                "RSSYSIM = SPYSIM_M + CARRY_SCALED - 0.0200/12; CARRY_SCALED = "
                f"AQR 'All Macro Carry' x {scale:.3f} (10% ann-vol target, "
                "full-sample in-sample scalar — disclosed)"
            ),
            "window": f"{out.index[0].date()}..{out.index[-1].date()}",
            "frequency": "MONTHLY-NATIVE — never mix into daily tables",
            "attribution": (
                "AQR Capital Management, 'Century of Factor Premia' dataset, "
                "AQR Data Library (research use with attribution)"
            ),
        }
    }
    return out, meta


def main() -> int:
    dd.SERIES_DIR.mkdir(parents=True, exist_ok=True)
    meta: dict = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "series": {},
    }

    primary = dd.load_primary_returns()
    primary.to_parquet(dd.SERIES_DIR / "primary_returns.parquet")
    meta["series"]["primary_returns"] = {
        "window": f"{primary.index[0].date()}..{primary.index[-1].date()}",
        "columns": sorted(primary.columns),
        "source": "sleeve matrix + cache (SSO/UPRO/IEF) + remote (NTSX/BTC) + MFBLEND",
    }

    proxies, proxy_meta = build_proxies(primary)
    proxies.to_parquet(dd.SERIES_DIR / "proxy_returns.parquet")
    meta["series"].update(proxy_meta)

    ext, ext_meta = build_extended()
    if ext is not None:
        ext.to_parquet(dd.SERIES_DIR / "extended_returns.parquet")
    meta["series"].update(ext_meta)

    rssy, rssy_meta = build_rssy_monthly(primary)
    if rssy is not None:
        rssy.to_parquet(dd.SERIES_DIR / "rssy_monthly.parquet")
    meta["series"].update(rssy_meta)

    (dd.SERIES_DIR / "series_meta.json").write_text(json.dumps(meta, indent=2))

    for name, info in meta["series"].items():
        status = info.get("status", "BUILT")
        window = info.get("window", info.get("window_start", ""))
        print(f"{name}: {status} {window}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
