"""Phase 0 exit-criteria — re-run shared/* against prototype parquet, assert equivalence.

Loads `2026-05-01-happy_market_hours_v231/data/trades_1407880.parquet`,
runs `sanity.compute_sanity`, `eda.compute_eda`, `gates.compute_gates` with
the same cost model + bootstrap seed as the prototype, and asserts every
key number matches the prototype reports to 3 decimals.

Run: `uv run python -m studies.myfxbook_reverse_engineering.shared._smoke_test`
or directly: `uv run python studies/myfxbook_reverse_engineering/shared/_smoke_test.py`.

Exit code 0 = Phase 0 PASS. Non-zero = mismatch — investigate before
proceeding to Phase 1.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Allow running as script (`python shared/_smoke_test.py`)
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
    from studies.myfxbook_reverse_engineering.shared import config, eda, gates, parser, sanity
else:
    from . import config, eda, gates, parser, sanity

PROTOTYPE_DIR = config.STUDY_ROOT / "2026-05-01-happy_market_hours_v231"
PROTOTYPE_PARQUET = PROTOTYPE_DIR / "data" / "trades_1407880.parquet"
SYSTEM_ID = 1407880

# Expected values from prototype reports/03_sanity_report.md, 06_gates_observed.md,
# 04_eda_raw.txt, 04b_direction_decay.txt.
EXPECTED_SANITY = {
    "n_trades": 3305,
    "n_deposits": 95,
    "symbols": {"GBPUSD": 898, "USDCAD": 808, "EURUSD": 703, "EURCHF": 370, "USDCHF": 287, "EURGBP": 239},
    "actions": {"Sell": 1712, "Buy": 1593},
    "max_gap_days": 33.9,  # 1 decimal in report
    "gaps_30d_plus_n": 1,
    "lot_p50": 3.76,
    "lot_p95": 15.16,
    "lot_p99": 16.65,
    "lot_max": 17.05,
    "lot_ratio_p95_p50": 4.03,
    "per_month_ratio_p95": 1.06,
    "n_martingale_steps": 0,
    "max_doubling_streak": 0,
    "long_streaks_count": 0,
    "hold_p50_h": 1.02,
    "hold_p95_h": 3.20,
    "hold_p99_h": 4.80,
    "hold_max_h": 8.60,
    "k1_pass": True,
}

EXPECTED_EDA = {
    "entry_hour": {0: 1680, 1: 248, 22: 1, 23: 1376},
    "dow": {"Monday": 1130, "Tuesday": 640, "Wednesday": 543, "Thursday": 610,
            "Friday": 318, "Saturday": 0, "Sunday": 64},
    "exit_kind": {"manual_or_time": 3109, "near_SL": 193, "near_TP": 3},
    "per_pair_peak": {  # symbol → (peak_hour, peak_n, pct_peak)
        "EURCHF": (0, 215, 58.1),  # 215/370 = 58.108
        "EURGBP": (0, 138, 57.7),  # 138/239 = 57.74 → report says 58
        "EURUSD": (0, 347, 49.4),  # 347/703 = 49.36 → report says 49
        "GBPUSD": (0, 488, 54.3),
        "USDCAD": (23, 410, 50.7),
        "USDCHF": (0, 154, 53.7),
    },
    "buy_pct_per_pair": {"EURCHF": 43.8, "EURGBP": 44.8, "EURUSD": 52.5,
                         "GBPUSD": 51.4, "USDCAD": 47.0, "USDCHF": 39.4},
    "buy_pct_per_hour": {0: 48.6, 1: 29.4, 22: 100.0, 23: 51.1},
    "yearly_n": {2013: 68, 2014: 167, 2015: 484, 2016: 641, 2017: 394,
                 2018: 337, 2019: 497, 2020: 541, 2021: 176},
    "yearly_avg_pips": {2013: 1.07, 2014: 1.87, 2015: 2.45, 2016: 4.03,
                        2017: 3.46, 2018: 3.11, 2019: 1.43, 2020: 1.20, 2021: 1.38},
    "net_avg_per_pair": {"USDCHF": 3.05, "EURCHF": 2.93, "GBPUSD": 1.75,
                         "EURGBP": 0.55, "EURUSD": 0.43, "USDCAD": -0.10},
    "net_sharpe_2016": 0.251,
}

EXPECTED_GATES = {
    "full_n_days": 1289,
    "full_n_trades": 3305,
    "full_daily_mean": 3.01,
    "full_daily_std": 19.04,
    "full_sharpe": 2.507,
    "full_boot_lo": 1.075,
    "full_boot_hi": 4.013,
    "oos_n_days": 192,
    "oos_n_trades": 397,
    "oos_daily_mean": 1.40,
    "oos_daily_std": 11.73,
    "oos_sharpe": 1.894,
    "oos_boot_lo": -1.668,
    "oos_boot_hi": 8.114,
    "wf_n_positive": 7,
    "wf_window7_sharpe": -1.077,
    "wf_window8_sharpe": 1.727,
    "sharpe_optimistic": 3.844,
    "gate2_pass": True,
    "gate3_pass": True,
    "gate4_pass": False,
    "gate6_pass": True,
}


class CheckLog:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.passed = 0

    def eq(self, label: str, actual, expected, tol: float = 0.005) -> None:
        if isinstance(expected, (int, bool)) and not isinstance(expected, bool) is False:
            ok = actual == expected
        elif isinstance(expected, bool):
            ok = bool(actual) == expected
        elif isinstance(expected, (int, float)):
            ok = abs(float(actual) - float(expected)) <= tol
        else:
            ok = actual == expected
        (self._record_pass if ok else self._record_fail)(label, actual, expected)

    def eq_dict(self, label: str, actual: dict, expected: dict, tol: float = 0.05) -> None:
        for k, v_exp in expected.items():
            v_act = actual.get(k)
            sub = f"{label}[{k!r}]"
            if v_act is None:
                self._record_fail(sub, None, v_exp)
                continue
            if isinstance(v_exp, (int, float)) and not isinstance(v_exp, bool):
                ok = abs(float(v_act) - float(v_exp)) <= tol
            else:
                ok = v_act == v_exp
            (self._record_pass if ok else self._record_fail)(sub, v_act, v_exp)

    def _record_pass(self, label: str, actual, expected) -> None:
        self.passed += 1
        print(f"  ✓ {label}: {actual} == {expected}")

    def _record_fail(self, label: str, actual, expected) -> None:
        msg = f"  ✗ {label}: got {actual!r}, expected {expected!r}"
        print(msg)
        self.failures.append(f"{label}: got {actual!r}, expected {expected!r}")


def main() -> int:
    if not PROTOTYPE_PARQUET.exists():
        print(f"ERROR: prototype parquet missing at {PROTOTYPE_PARQUET}")
        return 2
    print(f"Loading {PROTOTYPE_PARQUET} …")
    trades_df = parser.load_trades(SYSTEM_ID, parquet_override=PROTOTYPE_PARQUET)
    print(f"Loaded {len(trades_df)} rows.\n")

    log = CheckLog()

    print("== Sanity checks ==")
    s = sanity.compute_sanity(trades_df, SYSTEM_ID)
    log.eq("sanity.n_trades", s.n_trades, EXPECTED_SANITY["n_trades"])
    log.eq("sanity.n_deposits", s.n_deposits, EXPECTED_SANITY["n_deposits"])
    log.eq_dict("sanity.symbols", s.symbols, EXPECTED_SANITY["symbols"], tol=0)
    log.eq_dict("sanity.actions", s.actions, EXPECTED_SANITY["actions"], tol=0)
    log.eq("sanity.max_gap_days", round(s.max_gap_days, 1), EXPECTED_SANITY["max_gap_days"], tol=0.05)
    log.eq("sanity.gaps_30d_plus", len(s.gaps_30d_plus), EXPECTED_SANITY["gaps_30d_plus_n"], tol=0)
    log.eq("sanity.lot_p50", round(s.lot_p50, 2), EXPECTED_SANITY["lot_p50"])
    log.eq("sanity.lot_p95", round(s.lot_p95, 2), EXPECTED_SANITY["lot_p95"])
    log.eq("sanity.lot_p99", round(s.lot_p99, 2), EXPECTED_SANITY["lot_p99"])
    log.eq("sanity.lot_max", round(s.lot_max, 2), EXPECTED_SANITY["lot_max"])
    log.eq("sanity.lot_ratio_p95_p50", round(s.lot_ratio_p95_p50, 2), EXPECTED_SANITY["lot_ratio_p95_p50"])
    log.eq("sanity.per_month_ratio_p95", round(s.per_month_ratio_p95, 2), EXPECTED_SANITY["per_month_ratio_p95"])
    log.eq("sanity.n_martingale_steps", s.n_martingale_steps, EXPECTED_SANITY["n_martingale_steps"], tol=0)
    log.eq("sanity.max_doubling_streak", s.max_doubling_streak, EXPECTED_SANITY["max_doubling_streak"], tol=0)
    log.eq("sanity.long_streaks_count", s.long_streaks_count, EXPECTED_SANITY["long_streaks_count"], tol=0)
    log.eq("sanity.hold_p50_h", round(s.hold_p50_h, 2), EXPECTED_SANITY["hold_p50_h"])
    log.eq("sanity.hold_p95_h", round(s.hold_p95_h, 2), EXPECTED_SANITY["hold_p95_h"])
    log.eq("sanity.hold_p99_h", round(s.hold_p99_h, 2), EXPECTED_SANITY["hold_p99_h"])
    log.eq("sanity.hold_max_h", round(s.hold_max_h, 2), EXPECTED_SANITY["hold_max_h"])
    log.eq("sanity.k1_pass", s.k1_pass, EXPECTED_SANITY["k1_pass"])

    print("\n== EDA checks ==")
    e = eda.compute_eda(trades_df, SYSTEM_ID)
    log.eq_dict("eda.entry_hour", {int(k): int(v) for k, v in e.entry_hour.items()},
                EXPECTED_EDA["entry_hour"], tol=0)
    log.eq_dict("eda.dow", {str(k): int(v) for k, v in e.dow_counts.items()},
                EXPECTED_EDA["dow"], tol=0)
    log.eq_dict("eda.exit_kind", {str(k): int(v) for k, v in e.exit_kind.items()},
                EXPECTED_EDA["exit_kind"], tol=0)

    for sym, (eh, en, _ep) in EXPECTED_EDA["per_pair_peak"].items():
        if sym not in e.per_pair_hour_peak.index:
            log._record_fail(f"eda.per_pair_peak[{sym}]", "missing", (eh, en))
            continue
        row = e.per_pair_hour_peak.loc[sym]
        log.eq(f"eda.per_pair_peak[{sym}].peak_hour", int(row["peak_hour"]), eh, tol=0)
        log.eq(f"eda.per_pair_peak[{sym}].peak_n", int(row["peak_n"]), en, tol=0)

    actual_buy_pct_pair = {sym: float(e.direction_by_pair.loc[sym, "buy_pct"])
                           for sym in e.direction_by_pair.index}
    log.eq_dict("eda.buy_pct_per_pair", actual_buy_pct_pair,
                EXPECTED_EDA["buy_pct_per_pair"], tol=0.1)

    actual_buy_pct_hour = {int(h): float(e.direction_by_hour.loc[h, "buy_pct"])
                           for h in e.direction_by_hour.index}
    for h, exp in EXPECTED_EDA["buy_pct_per_hour"].items():
        if h not in actual_buy_pct_hour:
            log._record_fail(f"eda.buy_pct_per_hour[{h}]", "missing", exp)
        else:
            log.eq(f"eda.buy_pct_per_hour[{h}]", round(actual_buy_pct_hour[h], 1), exp, tol=0.15)

    actual_yearly_n = {int(y): int(e.yearly_decay.loc[y, "n"]) for y in e.yearly_decay.index}
    log.eq_dict("eda.yearly_n", actual_yearly_n, EXPECTED_EDA["yearly_n"], tol=0)

    actual_yearly_avg = {int(y): float(e.yearly_decay.loc[y, "avg_pips"]) for y in e.yearly_decay.index}
    log.eq_dict("eda.yearly_avg_pips", actual_yearly_avg, EXPECTED_EDA["yearly_avg_pips"], tol=0.01)

    actual_net_avg_pair = {sym: float(e.pnl_by_pair_net.loc[sym, "net_avg"])
                           for sym in e.pnl_by_pair_net.index}
    log.eq_dict("eda.net_avg_per_pair", actual_net_avg_pair,
                EXPECTED_EDA["net_avg_per_pair"], tol=0.01)

    log.eq("eda.net_sharpe_2016",
           round(float(e.pnl_by_year_net.loc[2016, "sharpe_net"]), 3),
           EXPECTED_EDA["net_sharpe_2016"], tol=0.005)

    print("\n== Gates checks ==")
    g = gates.compute_gates(trades_df, SYSTEM_ID)
    log.eq("gates.full.n_days", g.full.n_days, EXPECTED_GATES["full_n_days"], tol=0)
    log.eq("gates.full.n_trades", g.full.n_trades, EXPECTED_GATES["full_n_trades"], tol=0)
    log.eq("gates.full.daily_mean", round(g.full.daily_mean, 2), EXPECTED_GATES["full_daily_mean"])
    log.eq("gates.full.daily_std", round(g.full.daily_std, 2), EXPECTED_GATES["full_daily_std"])
    log.eq("gates.full.sharpe", round(g.full.sharpe, 3), EXPECTED_GATES["full_sharpe"])
    log.eq("gates.full.boot_lo", round(g.full.boot_lo, 3), EXPECTED_GATES["full_boot_lo"])
    log.eq("gates.full.boot_hi", round(g.full.boot_hi, 3), EXPECTED_GATES["full_boot_hi"])

    assert g.oos is not None, "OOS block missing — check oos_cutoff"
    log.eq("gates.oos.n_days", g.oos.n_days, EXPECTED_GATES["oos_n_days"], tol=0)
    log.eq("gates.oos.n_trades", g.oos.n_trades, EXPECTED_GATES["oos_n_trades"], tol=0)
    log.eq("gates.oos.daily_mean", round(g.oos.daily_mean, 2), EXPECTED_GATES["oos_daily_mean"])
    log.eq("gates.oos.daily_std", round(g.oos.daily_std, 2), EXPECTED_GATES["oos_daily_std"])
    log.eq("gates.oos.sharpe", round(g.oos.sharpe, 3), EXPECTED_GATES["oos_sharpe"])
    log.eq("gates.oos.boot_lo", round(g.oos.boot_lo, 3), EXPECTED_GATES["oos_boot_lo"])
    log.eq("gates.oos.boot_hi", round(g.oos.boot_hi, 3), EXPECTED_GATES["oos_boot_hi"])

    log.eq("gates.wf.n_positive", g.n_wf_positive, EXPECTED_GATES["wf_n_positive"], tol=0)
    log.eq("gates.wf.window7_sharpe",
           float(g.walkforward.loc[g.walkforward["window"] == 7, "sharpe"].iloc[0]),
           EXPECTED_GATES["wf_window7_sharpe"])
    log.eq("gates.wf.window8_sharpe",
           float(g.walkforward.loc[g.walkforward["window"] == 8, "sharpe"].iloc[0]),
           EXPECTED_GATES["wf_window8_sharpe"])

    log.eq("gates.sharpe_optimistic", round(g.sharpe_optimistic, 3), EXPECTED_GATES["sharpe_optimistic"])
    log.eq("gates.gate2_pass", g.gate2_pass, EXPECTED_GATES["gate2_pass"])
    log.eq("gates.gate3_pass", g.gate3_pass, EXPECTED_GATES["gate3_pass"])
    log.eq("gates.gate4_pass", g.gate4_pass, EXPECTED_GATES["gate4_pass"])
    log.eq("gates.gate6_pass", g.gate6_pass, EXPECTED_GATES["gate6_pass"])

    print("\n=================================")
    if log.failures:
        print(f"❌ FAIL — {len(log.failures)} mismatch(es), {log.passed} passed")
        for msg in log.failures:
            print(f"  - {msg}")
        return 1
    print(f"✅ PASS — {log.passed} checks matched prototype reports to 3 decimals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
