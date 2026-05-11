"""12-variant grid for the threshold_sweep sub-study (spec §2.2).

Layout:
  - 1 baseline (canonical T3d K=2, no buffers)
  - 5 symmetric SMA buffer variants: ±0.5%, 1%, 2%, 3%, 5%
  - 3 asymmetric SMA hysteresis variants: on=2%/3%/5%, off=0%
  - 3 AR(1) buffer variants: 0.05, 0.10, 0.15

All variants share: on_asset=QLD, off_asset=ZROZ, signal_type=vote_of_k, k=2.
"""
from __future__ import annotations


def _make(name: str, *,
          sma_buf_on: float = 0.0, sma_buf_off: float = 0.0,
          ar1_buf: float = 0.0) -> dict:
    return {
        "name": name,
        "on_asset": "QLD",
        "off_asset": "ZROZ",
        "signal_type": "vote_of_k",
        "k": 2,
        "sma_long_buffer_on": sma_buf_on,
        "sma_long_buffer_off": sma_buf_off,
        "sma_short_buffer_on": sma_buf_on,
        "sma_short_buffer_off": sma_buf_off,
        "ar1_buffer": ar1_buf,
    }


VARIANTS: list[dict] = [
    # Baseline (canonical T3d K=2)
    _make("t3d_k2_baseline"),
    # Symmetric SMA buffer (5 levels)
    _make("t3d_k2_smabuf_05pct", sma_buf_on=0.005, sma_buf_off=0.005),
    _make("t3d_k2_smabuf_1pct",  sma_buf_on=0.01,  sma_buf_off=0.01),
    _make("t3d_k2_smabuf_2pct",  sma_buf_on=0.02,  sma_buf_off=0.02),
    _make("t3d_k2_smabuf_3pct",  sma_buf_on=0.03,  sma_buf_off=0.03),
    _make("t3d_k2_smabuf_5pct",  sma_buf_on=0.05,  sma_buf_off=0.05),
    # Asymmetric SMA hysteresis (3 variants — on > off=0)
    _make("t3d_k2_hyst_2on_0off", sma_buf_on=0.02, sma_buf_off=0.0),
    _make("t3d_k2_hyst_3on_0off", sma_buf_on=0.03, sma_buf_off=0.0),
    _make("t3d_k2_hyst_5on_0off", sma_buf_on=0.05, sma_buf_off=0.0),
    # AR(1) buffer (3 variants)
    _make("t3d_k2_ar1buf_05", ar1_buf=0.05),
    _make("t3d_k2_ar1buf_10", ar1_buf=0.10),
    _make("t3d_k2_ar1buf_15", ar1_buf=0.15),
]
