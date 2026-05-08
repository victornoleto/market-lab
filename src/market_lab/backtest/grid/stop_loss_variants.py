"""Expand a base top-K config list into the stop-loss variant grid.

Phase 1 of the crash-protection sweep (see
``studies/SPEC_crash_protection_evolution.md``).

Given a list of top-K base configs (already-passing or top-ranked EMA/SMA
threshold configs), this module enumerates every combination of
``stop_loss_pct`` × ``reentry_mode`` × ``reentry_param`` that the sweep
should simulate. Returns a flat list of ``(base_cfg, stop_cfg,
variant_id)`` triples ready for simulation.

The expansion deduplicates degenerate combinations:

* ``stop_loss_pct = None`` → only one variant (baseline), any re-entry
  mode is irrelevant.
* ``reentry_mode = "next_signal"`` has no parameter to sweep, so only
  one variant is generated per stop-loss level.
* ``reentry_mode = "time_cooldown"`` and ``"recovery_trigger"`` sweep
  their respective parameter grids.

Default axes match ``SPEC_crash_protection_evolution.md §3.2``:
* stop_loss_pct ∈ {None, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40}
* time_cooldown bars ∈ {21, 63, 126}
* recovery_trigger fraction ∈ {0.05, 0.10, 0.15}

= 1 baseline + 6 × (1 next_signal + 3 time_cooldown + 3 recovery_trigger)
= 1 + 6 × 7 = 43 variants per base config.

Citations
---------
* Stop-loss axis choice: spec §3.1 / §3.2.
"""

from __future__ import annotations

from dataclasses import dataclass

from market_lab.backtest.strategies.ema_sma_threshold_educational import (
    EMASMAThresholdConfig,
)
from market_lab.backtest.strategies.stop_loss_and_risk_signals import (
    StopLossConfig,
)

DEFAULT_STOP_LEVELS: tuple[float, ...] = (0.15, 0.20, 0.25, 0.30, 0.35, 0.40)
DEFAULT_COOLDOWNS: tuple[int, ...] = (21, 63, 126)
DEFAULT_RECOVERY_PCTS: tuple[float, ...] = (0.05, 0.10, 0.15)


@dataclass(frozen=True)
class Variant:
    base_cfg: EMASMAThresholdConfig
    stop_cfg: StopLossConfig
    base_rank: int  # 1-based rank of base_cfg in the original top-K listing
    variant_idx: int  # 0-based index within the variants of base_cfg

    @property
    def variant_id(self) -> str:
        """Human-readable id: ``<base_rank>_<base_cfg_id>_<stop_tag>``."""
        return f"{self.base_rank:02d}_{self.base_cfg.cfg_id}_{self.stop_tag}"

    @property
    def stop_tag(self) -> str:
        sl = self.stop_cfg.stop_loss_pct
        if sl is None:
            return "baseline"
        pct_tag = f"sl{int(round(sl * 100))}"
        mode = self.stop_cfg.reentry_mode
        if mode == "next_signal":
            return f"{pct_tag}_next"
        if mode == "time_cooldown":
            return f"{pct_tag}_cool{int(self.stop_cfg.reentry_param)}"
        # recovery_trigger
        rec_pct = int(round(float(self.stop_cfg.reentry_param) * 100))  # type: ignore[arg-type]
        return f"{pct_tag}_rec{rec_pct}"


def expand_stop_loss_variants(
    top_configs: list[EMASMAThresholdConfig],
    *,
    stop_levels: tuple[float, ...] = DEFAULT_STOP_LEVELS,
    cooldowns: tuple[int, ...] = DEFAULT_COOLDOWNS,
    recovery_pcts: tuple[float, ...] = DEFAULT_RECOVERY_PCTS,
) -> list[Variant]:
    """Cartesian expansion with dedup — see module docstring.

    Parameters
    ----------
    top_configs : list[EMASMAThresholdConfig]
        Ranked list of base configs (rank 1 first).
    stop_levels : tuple[float, ...]
        Non-None drawdown thresholds to sweep. A ``None`` baseline is
        always added as variant 0 per base.
    cooldowns : tuple[int, ...]
        ``time_cooldown`` bar counts.
    recovery_pcts : tuple[float, ...]
        ``recovery_trigger`` fractional thresholds.

    Returns
    -------
    list[Variant]
        Flat list length = len(top_configs) × (1 + len(stop_levels) ×
        (1 + len(cooldowns) + len(recovery_pcts))).
    """
    variants: list[Variant] = []
    for rank_zero, base in enumerate(top_configs):
        rank = rank_zero + 1
        v_idx = 0
        # Baseline — no stop.
        variants.append(Variant(
            base_cfg=base,
            stop_cfg=StopLossConfig(stop_loss_pct=None),
            base_rank=rank,
            variant_idx=v_idx,
        ))
        v_idx += 1
        for sl in stop_levels:
            # next_signal — single variant.
            variants.append(Variant(
                base_cfg=base,
                stop_cfg=StopLossConfig(
                    stop_loss_pct=sl, reentry_mode="next_signal",
                ),
                base_rank=rank,
                variant_idx=v_idx,
            ))
            v_idx += 1
            # time_cooldown — one per cooldown.
            for cd in cooldowns:
                variants.append(Variant(
                    base_cfg=base,
                    stop_cfg=StopLossConfig(
                        stop_loss_pct=sl,
                        reentry_mode="time_cooldown",
                        reentry_param=int(cd),
                    ),
                    base_rank=rank,
                    variant_idx=v_idx,
                ))
                v_idx += 1
            # recovery_trigger — one per recovery pct.
            for rp in recovery_pcts:
                variants.append(Variant(
                    base_cfg=base,
                    stop_cfg=StopLossConfig(
                        stop_loss_pct=sl,
                        reentry_mode="recovery_trigger",
                        reentry_param=float(rp),
                    ),
                    base_rank=rank,
                    variant_idx=v_idx,
                ))
                v_idx += 1
    return variants
