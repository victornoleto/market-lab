"""Calibrate _CARRY_SCALAR_BY_CLASS per Carver [systematic_trading, ch.9 p.183].

Target: carry forecast SD = 10 over the full lh_56y window.
For each class (equity, bond), compute the median SD of (carry_raw / rolling_std)
across representative assets, then scalar = 10.0 / median_sd.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt import signals_carry as sc
from studies.letf_rotation_hunt.data_loader import load_ffr_daily, load_testfolio_series


CALIBRATION_ASSETS_BY_CLASS: dict[str, list[str]] = {
    "equity": ["UPRO", "QLD"],
    "bond": ["TMF"],
}


def main() -> None:
    ffr = load_ffr_daily()
    suggested: dict[str, float] = {"gold": 0.0}
    for cls, assets in CALIBRATION_ASSETS_BY_CLASS.items():
        sds: list[float] = []
        for a in assets:
            tf_ticker, _ = sc._ASSET_CARRY_MAP[a].yield_kind, None  # noqa
            # Build raw normalized signal with scalar=1, fdm=1, then measure SD
            prices = load_testfolio_series("SPYSIM" if a == "UPRO" else
                                            "QLDSIM" if a in ("QLD", "TQQQ") else
                                            "ZROZSIM").dropna()
            yield_series = sc._load_yield_for_asset(a).reindex(prices.index).ffill()
            ffr_annual = sc._ffr_daily_to_annual(ffr).reindex(prices.index).ffill()
            cfg = sc._ASSET_CARRY_MAP[a]
            carry_raw = yield_series - cfg.leverage * ffr_annual
            carry_std = carry_raw.rolling(252, min_periods=126).std()
            normalized = (carry_raw / carry_std).dropna()
            sds.append(float(normalized.std()))
        median_sd = float(np.median(sds))
        scalar = 10.0 / median_sd if median_sd > 0 else 10.0
        suggested[cls] = round(scalar, 4)
        print(f"{cls}: median SD={median_sd:.4f} → scalar={scalar:.4f}")
    print("\nSuggested _CARRY_SCALAR_BY_CLASS:")
    for k, v in suggested.items():
        print(f"  {k!r}: {v},")


if __name__ == "__main__":
    main()
