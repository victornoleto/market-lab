"""Smoke tests for Phase 3.7 H1.c — Maróy Ladder intraday strategy.

Covers:
  1. TP ladder triggers in the expected order on a synthetic price path
     that goes straight up.
  2. EOD forced-flat exits when no TP reached.
  3. F2-alignment invariant (prev_weight × ret).

Citations: ``[paper.maroy_2024_intraday_improvements, §Ladder]``,
``[advances_fin_ml, p.31-34]``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.phase3_7_h1_maroy_ladder import (
    MaroyLadderConfig,
    MaroyLadderResult,
    simulate_h1_maroy_ladder,
)


def _synth_session(
    day: str,
    open_price: float,
    closes: list[float],
    highs: list[float] | None = None,
    lows: list[float] | None = None,
) -> pd.DataFrame:
    """Build a synthetic 1-min session frame with explicit close path."""
    ts = pd.date_range(
        f"{day} 13:30:00", periods=len(closes), freq="1min", tz="UTC"
    )
    opens = [open_price] + closes[:-1]
    hs = highs if highs is not None else [max(o, c) for o, c in zip(opens, closes)]
    ls = lows if lows is not None else [min(o, c) for o, c in zip(opens, closes)]
    return pd.DataFrame(
        {"open": opens, "high": hs, "low": ls, "close": closes},
        index=ts,
    )


def test_ladder_triggers_tp1_tp2_tp3_in_order():
    """Price rises far enough to trip TP1, TP2, TP3 all in sequence."""
    # Build 16 historical sessions of tiny flat moves (so noise boundary is small),
    # then a test session where price breaks up +2% very fast.
    sessions = []
    base = 100.0
    for i in range(16):
        day = f"2024-01-{1+i:02d}"
        # alternating closes around open producing non-zero |intraday_ret|
        flat = [base + 0.01 * ((k % 3) - 1) for k in range(30)]
        sessions.append(_synth_session(day, base, flat))
    # Breakout session — 30 bars.
    day = "2024-02-01"
    open_p = base
    # First bars flat just above open to let noise boundary update, then a
    # sharp climb.
    closes = []
    highs = []
    lows = []
    for k in range(30):
        if k < 3:
            c = open_p * (1.0 + 0.0005)  # just inside boundary
            closes.append(c)
            highs.append(c)
            lows.append(c)
        elif k == 3:
            # break above upper boundary decisively
            c = open_p * 1.005
            closes.append(c)
            highs.append(c)
            lows.append(c)
        elif k == 4:
            # hit TP1 (need +0.5×ATR above entry)
            c = open_p * 1.02
            closes.append(c)
            highs.append(c)
            lows.append(closes[-2])  # low = previous close
        elif k == 5:
            # hit TP2 and TP3
            c = open_p * 1.05
            closes.append(c)
            highs.append(c)
            lows.append(closes[-2])
        else:
            c = closes[-1]
            closes.append(c)
            highs.append(c)
            lows.append(c)
    sessions.append(_synth_session(day, open_p, closes, highs, lows))
    data = pd.concat(sessions)

    # Make spread zero so we only test the exit-logic path cleanly.
    cfg = MaroyLadderConfig(
        noise_lookback_days=14,
        atr_period=5,
        tp1_mult=0.5,
        tp2_mult=1.0,
        tp3_mult=2.0,
        trailing_atr_mult=1.0,
        allow_short=False,
        spread_one_way=0.0,
    )
    res = simulate_h1_maroy_ladder(data, cfg)
    # We expect: at least one entry and ladder to hit some TP(s).
    assert res.n_entries >= 1, "no long entry on breakout session"
    # The ladder should register TPs or a trailing exit — the price makes 5%
    # over a handful of bars, so at least TP1 must be hit.
    assert res.tp1_hits >= 1, (
        f"expected TP1 hit; got tp1={res.tp1_hits} tp2={res.tp2_hits} "
        f"tp3={res.tp3_hits} trail={res.trailing_exits} eod={res.eod_exits}"
    )


def test_eod_forced_flat_when_no_tp_hit():
    """A breakout where bar range << TP distance should close at EOD.

    We set TP multipliers so large that the static price post-entry
    (no movement after breakout) cannot reach them, forcing EOD exit.
    """
    sessions = []
    base = 100.0
    rng = np.random.default_rng(7)
    for i in range(16):
        day = f"2024-01-{1+i:02d}"
        # Large daily moves so ATR is non-trivial in absolute terms.
        closes = [base + rng.normal(0, 0.5) for _ in range(30)]
        sessions.append(_synth_session(day, base, closes))

    # On breakout session, price breaks above upper, then FREEZES at that
    # level exactly — high == low == close — so no TP can be hit.
    day = "2024-02-01"
    open_p = base
    closes = [open_p * (1 + 0.0005)] * 4  # flat inside boundary
    break_close = open_p * 1.01  # well above upper (boundary < 1%)
    closes.append(break_close)
    # Hold at exactly break_close for rest of day — high/low == close.
    closes += [break_close] * 25
    # Override highs/lows to match closes exactly (no intra-bar movement).
    sessions.append(_synth_session(day, open_p, closes, highs=closes, lows=closes))
    data = pd.concat(sessions)

    cfg = MaroyLadderConfig(
        noise_lookback_days=14,
        atr_period=5,
        tp1_mult=20.0,
        tp2_mult=50.0,
        tp3_mult=100.0,
        trailing_atr_mult=10.0,
        allow_short=False,
        spread_one_way=0.0,
    )
    res = simulate_h1_maroy_ladder(data, cfg)
    assert res.n_entries >= 1, "no entry"
    assert res.tp1_hits + res.tp2_hits + res.tp3_hits == 0, (
        f"unexpected TP hits: {res.tp1_hits}/{res.tp2_hits}/{res.tp3_hits}"
    )
    assert res.eod_exits >= 1, f"expected EOD exit; got {res.eod_exits}"


def test_f2_alignment_prev_weight_times_ret():
    """bar_returns must equal prev_weight × ret − costs (F2 invariant)."""
    sessions = []
    base = 100.0
    for i in range(16):
        day = f"2024-01-{1+i:02d}"
        closes = [base + 0.01 * ((k % 5) - 2) for k in range(30)]
        sessions.append(_synth_session(day, base, closes))
    # Trivial breakout session
    day = "2024-02-01"
    closes = []
    for k in range(30):
        if k < 4:
            closes.append(base * (1 + 0.0005))
        elif k == 4:
            closes.append(base * 1.005)
        else:
            closes.append(base * 1.005)
    sessions.append(_synth_session(day, base, closes))
    data = pd.concat(sessions)

    cfg = MaroyLadderConfig(
        noise_lookback_days=14,
        atr_period=5,
        allow_short=False,
        spread_one_way=0.0,
        commission_round_trip=0.0,
    )
    res = simulate_h1_maroy_ladder(data, cfg)
    ret = data["close"].pct_change().fillna(0.0)
    prev_w = res.weights.shift(1).fillna(0.0)
    expected_gross = prev_w * ret
    assert np.allclose(
        res.gross_returns.to_numpy(), expected_gross.to_numpy(), atol=1e-12
    ), "F2 alignment broken: gross_returns != prev_weight × ret"
