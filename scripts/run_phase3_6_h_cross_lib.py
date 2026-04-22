"""Phase 3.6 Family H — cross-lib concordance check (gate 9).

Reconciles canonical AMH regime-switching daily returns vs a
hand-rolled pure-pandas reimplementation on the OOS split. Since Family
H verdict is FAIL (OOS Sharpe 0.69 vs 1.5 target, OOS CAGR 9.47% vs CDI
13%, DSR p=0.56), this cross-lib run is documentary — does not change
the verdict — but the scaffolding is kept to match the template used by
the winner candidates.

Sanity: reconstruct the winner cell (n_states=2, feature_set=sigma,
rebalance_cadence_days=21) by (a) reading the canonical daily_returns
parquet, and (b) running a hand-rolled path that uses the exported
regime_labels series to replay allocations without costs/tax. A ±3pp
CAGR tolerance per plan §5 gate 9.

Citations
---------
* Cross-lib concordance requirement: `[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/var/www/pessoal/ai-trade")
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.strategies.phase3_6_h_amh_regime_switching import (  # noqa: E402
    AMHRegimeConfig,
    REGIME_ALLOCATION,
    simulate_amh_regime,
)

OUT_DIR = ROOT / "reports/phase_3_6/h_amh_regime_switching"
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"
OOS_RANGE = ("2018-01-01", "2023-12-31")
IS_RANGE = ("2004-11-18", "2017-12-31")


def _load_tiingo(t: str) -> pd.DataFrame:
    df = pd.read_parquet(TIINGO_DAILY / f"{t}.parquet")
    df.index = pd.DatetimeIndex(df.index).normalize()
    return df


def _cagr(series: pd.Series, periods_per_year: int = 252) -> float:
    r = series.dropna()
    if len(r) < 2:
        return 0.0
    n = len(r)
    eq = float((1.0 + r).prod())
    if eq <= 0:
        return -1.0
    return eq ** (periods_per_year / n) - 1.0


def _slice(s: pd.Series, start: str, end: str) -> pd.Series:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return s.loc[(s.index >= a) & (s.index <= b)]


def _hand_rolled_from_labels(
    labels: pd.Series,
    rets: pd.DataFrame,
    cadence: int,
) -> pd.Series:
    """Pure-pandas replay from the regime-label series.

    Reads the exported regime_labels (which includes all IS+OOS+FWD),
    applies the canonical REGIME_ALLOCATION mapping at each rebalance
    date (every `cadence` trading days starting at first non-null
    label), enforces one-day shift, ignores costs/tax (isolates
    mechanics).
    """
    labels = labels.dropna()
    valid_idx = rets.index.intersection(labels.index)
    full_idx = rets.index

    # Determine rebalance dates: every `cadence` trading days from first
    # valid index position.
    first_pos = full_idx.get_loc(valid_idx[0])
    rebal_positions = list(range(first_pos, len(full_idx), cadence))

    weights = pd.DataFrame(0.0, index=full_idx, columns=["SPY", "TLT", "GLD"])
    for p in rebal_positions:
        rd = full_idx[p]
        if rd not in labels.index:
            continue
        label = labels.loc[rd]
        if not isinstance(label, str):
            continue
        alloc = REGIME_ALLOCATION.get(label)
        if alloc is None:
            continue
        for a, w in alloc.items():
            weights.loc[rd:, a] = w

    prev_w = weights.shift(1).fillna(0.0)
    r = (prev_w[["SPY", "TLT", "GLD"]] * rets[["SPY", "TLT", "GLD"]].fillna(0.0)).sum(axis=1)
    return r


def main() -> None:
    print("=" * 80)
    print("Phase 3.6 Family H — cross-lib concordance")
    print("=" * 80)

    # -- Load returns panel ------------------------------------------------------
    ret_panel = {}
    for t in ("SPY", "TLT", "GLD"):
        df = _load_tiingo(t)
        ret_panel[t] = df["adj_close"].pct_change()
    rets = pd.concat(ret_panel, axis=1).dropna(how="any")

    # -- Canonical: winner cell reproduction ------------------------------------
    # Winner from run_phase3_6_h_amh_regime_switching.py = n2_sigma_rc21, no costs
    cfg = AMHRegimeConfig(
        n_states=2,
        feature_set="sigma",
        rebalance_cadence_days=21,
        commission_bps=0.0,
        spread_bps=0.0,
        slippage_bps=0.0,
        tax_rate=0.0,
    )
    canonical_result = simulate_amh_regime(
        rets["SPY"], rets["TLT"], rets["GLD"], cfg,
        pd.Timestamp(IS_RANGE[0]), pd.Timestamp(IS_RANGE[1]),
    )
    canonical = canonical_result.daily_returns
    labels = canonical_result.regime_labels

    # -- Hand-rolled replay from labels -----------------------------------------
    hand = _hand_rolled_from_labels(labels, rets, cadence=21)

    c_oos = _slice(canonical, *OOS_RANGE)
    h_oos = _slice(hand, *OOS_RANGE)

    cagr_c = _cagr(c_oos)
    cagr_h = _cagr(h_oos)
    delta_pp = abs(cagr_c - cagr_h) * 100
    print(
        f"Canonical OOS CAGR: {cagr_c*100:+.3f}%   |   "
        f"Hand-rolled OOS CAGR: {cagr_h*100:+.3f}%   Δ={delta_pp:.3f}pp"
    )

    pass_tol = delta_pp <= 3.0
    print(f"Gate 9 (≤3pp): {'PASS' if pass_tol else 'FAIL'}")

    out_md = OUT_DIR / "cross_lib_check.md"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(
        "# Cross-lib concordance — Family H AMH regime-switching\n\n"
        f"- Winner cell: **n_states=2, feature_set=sigma, rebalance_cadence_days=21, no costs/tax (isolated mechanics)**\n"
        f"- OOS window: {OOS_RANGE[0]} → {OOS_RANGE[1]}\n"
        f"- Canonical OOS CAGR: **{cagr_c*100:+.3f}%**\n"
        f"- Hand-rolled (pure-pandas, replayed from regime_labels) OOS CAGR: **{cagr_h*100:+.3f}%**\n"
        f"- |Δ|: **{delta_pp:.3f}pp** (tolerance ≤ 3pp)\n"
        f"- Gate 9 verdict: **{'PASS' if pass_tol else 'FAIL'}**\n\n"
        "## Notes\n\n"
        "The hand-rolled path replays the exact same regime labels\n"
        "produced by the canonical HMM fit — it isolates the\n"
        "weight/allocation/rebalance-cadence mechanics from the HMM\n"
        "fitting logic. Any Δ > 0 would indicate a bug in the weight\n"
        "shifting or cadence alignment. The HMM fitting itself is not\n"
        "independently replicated (no hmmlearn in .venv) — this gate\n"
        "therefore verifies the allocation pipeline, not the HMM.\n"
        "The Family verdict (FAIL) is dominated by OOS Sharpe/CAGR\n"
        "undercut, not by mechanics.\n"
    )

    out_json = OUT_DIR / "cross_lib_summary.json"
    out_json.write_text(json.dumps({
        "cell": "n2_sigma_rc21_no_frictions",
        "oos_window": list(OOS_RANGE),
        "canonical_oos_cagr": cagr_c,
        "hand_rolled_oos_cagr": cagr_h,
        "delta_pp": delta_pp,
        "tolerance_pp": 3.0,
        "pass": bool(pass_tol),
        "note": (
            "Hand-rolled path reuses canonical regime_labels and replays "
            "REGIME_ALLOCATION mapping. Isolates allocation mechanics, "
            "not HMM fit."
        ),
    }, indent=2, default=float))

    print(f"\n[write] {out_md}")
    print(f"[write] {out_json}")


if __name__ == "__main__":
    main()
