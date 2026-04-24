"""Iter 017 — Pure-numpy reference for regional rotation (G7 parity).

Independent re-implementation of ``apply_regional_rotation_vm`` in pure
numpy (no pandas). Required by G7 cross-lib parity per
`[advances_fin_ml, p.31-34]`.

The routine mirrors:

1. Iter 016's ``apply_static_stack_vol_managed`` on each region (inlined
   via ``apply_static_stack_vm_np`` from iter 016's numpy reference).
2. 12-1 skip-a-month momentum on the cumulative price of each region.
3. Monthly top-1 region selection.
4. Concatenation of per-window net-return segments + switch cost.

Output: a single numpy array of portfolio net returns, length equal to
the iter 016 trimmed index (N_bars - lookback).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_ITER_016_DIR = (
    Path(__file__).resolve().parent.parent
    / "016-2026-04-24-1729-static-stack-vm-hybrid"
)
sys.path.insert(0, str(_ITER_016_DIR))

from numpy_reference_stack_vm import apply_static_stack_vm_np  # noqa: E402


def _compute_12_1_momentum_np(prices: np.ndarray, long_window: int, skip: int) -> np.ndarray:
    """Pure-numpy 12-1 skip-a-month momentum on a price level series."""
    n = len(prices)
    out = np.full(n, np.nan, dtype=float)
    for t in range(long_window, n):
        num_idx = t - skip
        den_idx = t - long_window
        if num_idx >= 0 and den_idx >= 0:
            out[t] = prices[num_idx] / prices[den_idx] - 1.0
    return out


def apply_regional_rotation_vm_np(
    regions: dict[str, tuple[np.ndarray, np.ndarray]],
    *,
    eq_weight: float,
    bd_weight: float,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    long_window: int = 252,
    skip: int = 21,
    rebalance_every: int = 21,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
    switch_cost_bps: float = 0.0002,
) -> np.ndarray:
    """Return a numpy array of portfolio net returns (length N - lookback).

    Parameters
    ----------
    regions : dict[str, tuple[np.ndarray, np.ndarray]]
        Region name → (equity_returns, bond_returns) numpy arrays of
        identical length.

    Output aligns with ``result_pd['net'].values`` from the pandas engine
    starting at bar ``lookback`` of the original series (per iter 016).
    """
    region_names = list(regions.keys())
    # Check aligned lengths
    n = len(regions[region_names[0]][0])
    for name in region_names[1:]:
        if len(regions[name][0]) != n or len(regions[name][1]) != n:
            raise ValueError(f"region {name!r} length mismatch")

    # Run iter 016 on each region
    per_region_net: dict[str, np.ndarray] = {}
    per_region_pos_eq: dict[str, np.ndarray] = {}
    per_region_pos_bd: dict[str, np.ndarray] = {}
    for name, (r_eq, r_bd) in regions.items():
        net, pos_eq, pos_bd, _ = apply_static_stack_vm_np(
            r_eq, r_bd,
            eq_weight=eq_weight, bd_weight=bd_weight,
            target_vol=target_vol, lookback=lookback,
            max_leverage=max_leverage,
            periods_per_year=periods_per_year,
            cost_bps_per_leg=cost_bps_per_leg,
        )
        per_region_net[name] = net
        per_region_pos_eq[name] = pos_eq
        per_region_pos_bd[name] = pos_bd

    # Compute 12-1 momentum on each region's cumulative price (full index)
    momentum_by_region: dict[str, np.ndarray] = {}
    for name, (r_eq, _r_bd) in regions.items():
        price = np.cumprod(1.0 + r_eq)
        momentum_by_region[name] = _compute_12_1_momentum_np(
            price, long_window=long_window, skip=skip,
        )

    # The iter 016 numpy stream starts at bar `lookback` of the original
    # series (it drops the first `lookback` NaN bars). The pandas engine
    # indexes these against full_idx. In numpy, we track the trimmed-
    # index offset: trimmed_bar_k corresponds to full_bar_k+lookback.
    trimmed_len = len(per_region_net[region_names[0]])
    # Verify all regions have the same trimmed length.
    for name in region_names:
        if len(per_region_net[name]) != trimmed_len:
            raise ValueError("region streams have different trimmed lengths")

    # Rebalance dates in FULL-index space, starting at
    # first_valid_ordinal = max(long_window, lookback + 1)
    first_valid_ord = max(long_window, lookback + 1)
    schedule_ords_full = list(range(first_valid_ord, n, rebalance_every))

    # Convert full-index ordinals to trimmed-index ordinals (offset by lookback).
    # schedule_trimmed_k = schedule_full_ord - lookback
    schedule_ords_trimmed = [ord_ - lookback for ord_ in schedule_ords_full]

    # The output begins at the first rebalance date's trimmed ordinal.
    # In pandas, net = pd.concat(net_pieces).sort_index() starting at first
    # rebalance date. So output length = trimmed_len - schedule_ords_trimmed[0].
    output_start = schedule_ords_trimmed[0]
    net_out = np.empty(trimmed_len - output_start, dtype=float)

    prev_region = None
    for i, ord_trimmed in enumerate(schedule_ords_trimmed):
        if i + 1 < len(schedule_ords_trimmed):
            next_ord = schedule_ords_trimmed[i + 1]
        else:
            next_ord = trimmed_len

        # Decide region using momentum at the corresponding full-index bar.
        full_ord = ord_trimmed + lookback
        mom_at = {
            name: momentum_by_region[name][full_ord]
            for name in region_names
        }
        if any(np.isnan(v) for v in mom_at.values()):
            winner = sorted(region_names)[0]
        else:
            sorted_pairs = sorted(
                mom_at.items(), key=lambda kv: (-kv[1], kv[0])
            )
            winner = sorted_pairs[0][0]

        # Copy that region's net for [ord_trimmed, next_ord).
        net_piece = per_region_net[winner][ord_trimmed:next_ord].copy()

        # Apply switch cost if transition.
        if prev_region is not None and prev_region != winner and len(net_piece) > 0:
            eq_notional = float(per_region_pos_eq[winner][ord_trimmed])
            transition_cost = 2.0 * eq_notional * switch_cost_bps
            net_piece[0] = net_piece[0] - transition_cost

        net_out[ord_trimmed - output_start : next_ord - output_start] = net_piece
        prev_region = winner

    return net_out
