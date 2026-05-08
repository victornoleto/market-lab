"""Replicator-lite — Etapa 1 of the consensus plan.

See `specs/replicator_lite_pre_reg.md` for the FROZEN protocol. This module is
the executable form. Any deviation from the spec invalidates the pre-registration.

Goal: measure REPLICABILITY (not decodability, not edge) of `frozen_rules/<id>.md`
against real trades using case-control entry detection on M5 bars.

Pipeline (per system):

  1. Load frozen rule + candidates.json + fingerprint.md → entry_window_utc, pairs,
     direction executor (top-1 univariate by default).
  2. Build candidate window W_i = pairs × hours × M5 bars in trade-date range.
  3. Label each (p, t): y_entry=1 iff real trade open within ±5min, y_direction=Buy/Sell.
  4. Apply frozen rule via decoder_features.compute_entry_features at each candidate.
  5. Compute metrics + 3 trivial baselines + lift.
  6. Apply Pass/Borderline/Fail bands.

This is the SKELETON. Full per-system run + CSV output happens in next session
per `007-opus.md` time-budget. The code below is functionally complete enough to
run on one system end-to-end as smoke test, but the batch driver (10 systems)
and CSV/memo emitter are TODO markers (`_TODO_BATCH`).

Citations preserved from `signal_rule.md`:
- [advances_fin_ml, ch.5] — feature importance + clustered MDA
- [evidence_based_ta, Aronson, p.367-380] — session/hour FX regime
- [advances_fin_ml, p.196-211] — DSR/PBO methodology (Stage 3 downstream)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from .decoder_features import compute_entry_features
from .ohlc_dukascopy import OhlcLoader, _DUKAS_PAIR_MAP

# ---------------------------------------------------------------------------
# Constants — frozen by spec, do NOT tune.
# ---------------------------------------------------------------------------

BAR_FREQ = "M5"
BAR_MINUTES = 5
ENTRY_TOL_MINUTES = 5  # ±5 min for "real entry hit"
LIFT_FAIL_PP = 5.0
LIFT_PASS_PP = 10.0
RATIO_FAIL_MAX = 3.0
LOW_N_THRESHOLD = 200

Direction = Literal["Buy", "Sell"]
Banda = Literal["Pass", "Borderline", "Fail"]


# ---------------------------------------------------------------------------
# Frozen rule loading
# ---------------------------------------------------------------------------


@dataclass
class FrozenRule:
    system_id: str
    family: str
    confidence: float
    pairs: list[str]
    entry_hours_utc: set[int]
    max_holding_hours: float | None
    direction_executor: str  # 'top1_univariate' | 'tree_rank1' | 'yaml_literal'
    direction_feature: str | None
    direction_op: str | None  # '>' | '<=' | '<' | '>='
    direction_threshold: float | None
    direction_when_true: Direction | None
    direction_when_false: Direction | None
    raw_yaml: dict
    # 5R-1-hardening Wave B item 2 (2026-05-02): UNCAT requires reason_code;
    # any non-enum label goes to candidate_new_family. v2 frozen_rules pre-date
    # the rule and may have None for both — validated non-strictly below.
    reason_code: str | None = None
    candidate_new_family: str | None = None


def _expand_window_to_hours(window: list[str]) -> set[int]:
    """['22:00', '00:59'] → {22, 23, 0}."""
    if not window or len(window) != 2:
        return set()
    h0 = int(window[0].split(":")[0])
    h1 = int(window[1].split(":")[0])
    if h0 <= h1:
        return set(range(h0, h1 + 1))
    return set(range(h0, 24)) | set(range(0, h1 + 1))


_UNIVARIATE_RE = re.compile(
    r"^\s*([a-zA-Z0-9_]+)\s*(>=|<=|>|<)\s*([-0-9.eE]+)\s*[⇒=>→]+\s*(Buy|Sell)\s*$"
)


def _parse_univariate(rule_text: str) -> tuple[str, str, float, Direction] | None:
    """Parse 'feat OP threshold ⇒ Direction'. Returns None on failure."""
    m = _UNIVARIATE_RE.match(rule_text)
    if not m:
        return None
    feat, op, thr_s, side = m.groups()
    return feat, op, float(thr_s), side  # type: ignore[return-value]


def load_frozen_rule(system_id: str, base_dir: Path) -> FrozenRule:
    """Read frozen_rules/<id>.md + candidates.json + fingerprint.md, build executor."""
    p_rule = base_dir / "frozen_rules" / f"{system_id}.md"
    p_cand = base_dir / "systems" / system_id / "decoder" / "candidates.json"
    p_fp = base_dir / "systems" / system_id / "decoder" / "fingerprint.md"
    if not p_rule.exists():
        raise FileNotFoundError(p_rule)

    text = p_rule.read_text()
    m = re.search(r"^---\n(.*?)\n---", text, re.DOTALL | re.MULTILINE)
    if not m:
        raise ValueError(f"{system_id}: malformed YAML front-matter")
    block = m.group(1)

    fm = re.search(r"^family:\s*(\S+)", block, re.MULTILINE)
    family = fm.group(1).strip() if fm else "?"
    cf = re.search(r"^confidence:\s*([0-9.]+)", block, re.MULTILINE)
    confidence = float(cf.group(1)) if cf else 0.0

    # 5R-1-hardening Wave B item 2: optional reason_code + candidate_new_family
    rc = re.search(r"^reason_code:\s*(\S+)", block, re.MULTILINE)
    reason_code = rc.group(1).strip() if rc else None
    cnf = re.search(r"^candidate_new_family:\s*(\S+)", block, re.MULTILINE)
    candidate_new_family = cnf.group(1).strip() if cnf else None
    if reason_code in ("null", "None", "~", '""', "''"):
        reason_code = None
    if candidate_new_family in ("null", "None", "~", '""', "''"):
        candidate_new_family = None
    from studies.myfxbook_reverse_engineering.shared.decoder_taxonomy import (
        validate_decoder_output,
    )
    validate_decoder_output(
        family=family,
        reason_code=reason_code,
        candidate_new_family=candidate_new_family,
        strict=False,  # legacy v2 permissive
    )

    win = re.search(r"entry_window_utc:\s*\[\s*\"?([0-9:]+)\"?\s*,\s*\"?([0-9:]+)\"?\s*\]", block)
    window = [win.group(1), win.group(2)] if win else []
    hours = _expand_window_to_hours(window) if window else set()

    pm = re.search(r"pairs:\s*\[([^\]]+)\]", block)
    pairs: list[str] = []
    if pm:
        pairs = [p.strip().strip('"').strip("'") for p in pm.group(1).split(",") if p.strip()]

    hm = re.search(r"max_holding_hours:\s*([0-9.]+)", block)
    max_hold = float(hm.group(1)) if hm else None

    front = {"family": family, "confidence": confidence, "pairs": pairs}
    rule = {"pairs": pairs, "entry_window_utc": window, "exit": {"max_holding_hours": max_hold}}

    # Fallback: parse fingerprint top-3 hours
    if not hours and p_fp.exists():
        fp_text = p_fp.read_text()
        m = re.search(r"Top entry hours \(UTC\):\s*((?:- \d{1,2}:00 — \d+ trades\s*)+)", fp_text)
        if m:
            hour_lines = re.findall(r"- (\d{1,2}):00 — (\d+) trades", m.group(1))
            hour_lines.sort(key=lambda x: -int(x[1]))
            hours = {int(h) for h, _ in hour_lines[:3]}

    # Direction executor v1: try top-1 univariate from candidates.json
    feat = op = side = None
    thr = None
    executor = "top1_univariate"
    if p_cand.exists():
        cands = json.load(open(p_cand))
        for c in cands:
            if c.get("miner") == "univariate":
                parsed = _parse_univariate(c.get("rule_text", ""))
                if parsed:
                    feat, op, thr, side = parsed
                    break

    return FrozenRule(
        system_id=system_id,
        family=family,
        confidence=confidence,
        pairs=pairs,
        entry_hours_utc=hours,
        reason_code=reason_code,
        candidate_new_family=candidate_new_family,
        max_holding_hours=max_hold,
        direction_executor=executor,
        direction_feature=feat,
        direction_op=op,
        direction_threshold=thr,
        direction_when_true=side,
        direction_when_false=("Sell" if side == "Buy" else "Buy") if side else None,
        raw_yaml=front,
    )


# ---------------------------------------------------------------------------
# Candidate window construction
# ---------------------------------------------------------------------------


def build_candidate_window(
    rule: FrozenRule, trades: pd.DataFrame
) -> pd.DataFrame:
    """Return DataFrame with columns [pair, ts] of all candidate (pair, M5_bar)
    in trade-date range, restricted to entry_hours_utc."""
    trades = trades[trades["is_trade"] == True]
    if trades.empty:
        return pd.DataFrame(columns=["pair", "ts"])

    pairs_in_data = sorted(trades["symbol"].dropna().unique().tolist())
    rule_pairs = [p for p in pairs_in_data if p in rule.pairs] or pairs_in_data

    t_min = pd.to_datetime(trades["open_dt_utc"].min()).floor("5min")
    t_max = pd.to_datetime(trades["open_dt_utc"].max()).ceil("5min")

    rows: list[dict] = []
    for pair in rule_pairs:
        if pair not in _DUKAS_PAIR_MAP:
            continue
        ts_range = pd.date_range(t_min, t_max, freq="5min", tz="UTC")
        if rule.entry_hours_utc:
            ts_range = ts_range[ts_range.hour.isin(rule.entry_hours_utc)]
        for ts in ts_range:
            rows.append({"pair": pair, "ts": ts})
    return pd.DataFrame(rows)


def label_entries(window: pd.DataFrame, trades: pd.DataFrame) -> pd.DataFrame:
    """Add y_entry (0/1) and y_direction (Buy/Sell/NA) to candidate window.
    A candidate (pair, ts) is y_entry=1 iff a real trade with same symbol opened
    in [ts, ts + ENTRY_TOL_MINUTES)."""
    trades = trades[trades["is_trade"] == True].copy()
    trades["ts_bin"] = pd.to_datetime(trades["open_dt_utc"]).dt.floor(f"{ENTRY_TOL_MINUTES}min")

    truth = (
        trades.groupby(["symbol", "ts_bin"])
        .agg(y_direction=("action", "first"), n=("action", "size"))
        .reset_index()
    )
    out = window.merge(
        truth, left_on=["pair", "ts"], right_on=["symbol", "ts_bin"], how="left"
    )
    out["y_entry"] = out["y_direction"].notna().astype(int)
    out["y_direction"] = out["y_direction"].fillna("NA")
    out = out.drop(columns=["symbol", "ts_bin", "n"], errors="ignore")
    return out


# ---------------------------------------------------------------------------
# Direction prediction
# ---------------------------------------------------------------------------


def apply_direction_rule(
    rule: FrozenRule,
    candidates_with_features: pd.DataFrame,
) -> pd.Series:
    """Vectorized application of the univariate rule.
    Returns Series[Buy/Sell/NA] aligned to candidates_with_features.
    NA when the feature is missing (insufficient OHLC history)."""
    if rule.direction_feature is None:
        return pd.Series(["NA"] * len(candidates_with_features), index=candidates_with_features.index)

    f = candidates_with_features[rule.direction_feature]
    op = rule.direction_op
    thr = rule.direction_threshold
    if op == ">":
        cond = f > thr
    elif op == ">=":
        cond = f >= thr
    elif op == "<":
        cond = f < thr
    elif op == "<=":
        cond = f <= thr
    else:
        return pd.Series(["NA"] * len(candidates_with_features), index=candidates_with_features.index)

    out = pd.Series(rule.direction_when_false, index=candidates_with_features.index, dtype=object)
    out.loc[cond.fillna(False)] = rule.direction_when_true
    out.loc[f.isna()] = "NA"
    return out


# ---------------------------------------------------------------------------
# Trivial baselines
# ---------------------------------------------------------------------------


def baseline_always_buy(window: pd.DataFrame) -> pd.Series:
    return pd.Series(["Buy"] * len(window), index=window.index)


def baseline_hour_majority(window: pd.DataFrame, trades: pd.DataFrame) -> pd.Series:
    t = trades[trades["is_trade"] == True].copy()
    t["hour"] = pd.to_datetime(t["open_dt_utc"]).dt.hour
    maj = t.groupby("hour")["action"].agg(lambda s: s.mode().iat[0] if len(s.mode()) else "Buy")
    w_hour = window["ts"].dt.hour
    return w_hour.map(maj).fillna("Buy")


def baseline_pair_hour_majority(window: pd.DataFrame, trades: pd.DataFrame) -> pd.Series:
    t = trades[trades["is_trade"] == True].copy()
    t["hour"] = pd.to_datetime(t["open_dt_utc"]).dt.hour
    maj = t.groupby(["symbol", "hour"])["action"].agg(
        lambda s: s.mode().iat[0] if len(s.mode()) else "Buy"
    )
    keys = list(zip(window["pair"], window["ts"].dt.hour))
    return pd.Series([maj.get(k, "Buy") for k in keys], index=window.index)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


@dataclass
class SystemMetrics:
    system_id: str
    pair: str  # 'AGGREGATE' or specific pair
    n_window: int
    n_actual_entries: int
    n_predicted_entries: int
    predicted_actual_ratio: float
    entry_precision: float
    entry_recall: float
    entry_f1: float
    fp_per_day: float
    direction_accuracy: float
    direction_acc_ci95_low: float
    direction_acc_ci95_high: float
    combined_hit_rate: float
    combined_hit_ci95_low: float
    combined_hit_ci95_high: float
    baseline_always_buy: float
    baseline_hour_majority: float
    baseline_pair_hour_majority: float
    max_baseline: float
    lift_vs_baseline_pp: float
    banda: Banda
    low_n_flag: bool
    direction_executor: str


def compute_metrics(
    window: pd.DataFrame,
    pred_direction: pd.Series,
    pred_entry: pd.Series,
    n_actual: int,
    n_days: float,
    system_id: str,
    pair_label: str,
    direction_executor: str,
    n_trades: int,
    baselines: dict[str, pd.Series],
) -> SystemMetrics:
    n_w = len(window)
    n_pred = int(pred_entry.sum())
    ratio = n_pred / max(n_actual, 1)

    tp = int(((pred_entry == 1) & (window["y_entry"] == 1)).sum())
    fp = int(((pred_entry == 1) & (window["y_entry"] == 0)).sum())
    fn = int(((pred_entry == 0) & (window["y_entry"] == 1)).sum())
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    f1 = 2 * prec * rec / max(prec + rec, 1e-9)
    fp_day = fp / max(n_days, 1.0)

    # Direction accuracy on predicted entries (where ground truth has direction)
    mask = (pred_entry == 1) & (window["y_entry"] == 1)
    dir_correct = (pred_direction[mask] == window["y_direction"][mask]).sum()
    dir_n = int(mask.sum())
    dir_acc = dir_correct / max(dir_n, 1)
    dir_lo, dir_hi = wilson_ci(int(dir_correct), dir_n)

    # Combined hit: rule-fires AND real entry within ±5min AND direction match
    combined_hit = int(((pred_entry == 1) & (window["y_entry"] == 1) &
                        (pred_direction == window["y_direction"])).sum())
    combined_hit_rate = combined_hit / max(n_actual, 1)
    ch_lo, ch_hi = wilson_ci(combined_hit, max(n_actual, 1))

    # Baselines: combined-hit rate using baseline direction, entry always fires
    base_rates = {}
    for name, bdir in baselines.items():
        bcombined = int(((window["y_entry"] == 1) & (bdir == window["y_direction"])).sum())
        base_rates[name] = bcombined / max(n_actual, 1)
    max_base = max(base_rates.values()) if base_rates else 0.0
    lift_pp = (combined_hit_rate - max_base) * 100

    # Banding
    if ratio > RATIO_FAIL_MAX or lift_pp <= LIFT_FAIL_PP:
        banda: Banda = "Fail"
    elif lift_pp >= LIFT_PASS_PP and ratio <= RATIO_FAIL_MAX and ch_lo > max_base:
        banda = "Pass"
    else:
        banda = "Borderline"

    return SystemMetrics(
        system_id=system_id,
        pair=pair_label,
        n_window=n_w,
        n_actual_entries=n_actual,
        n_predicted_entries=n_pred,
        predicted_actual_ratio=round(ratio, 3),
        entry_precision=round(prec, 3),
        entry_recall=round(rec, 3),
        entry_f1=round(f1, 3),
        fp_per_day=round(fp_day, 2),
        direction_accuracy=round(dir_acc, 3),
        direction_acc_ci95_low=round(dir_lo, 3),
        direction_acc_ci95_high=round(dir_hi, 3),
        combined_hit_rate=round(combined_hit_rate, 3),
        combined_hit_ci95_low=round(ch_lo, 3),
        combined_hit_ci95_high=round(ch_hi, 3),
        baseline_always_buy=round(base_rates.get("always_buy", 0), 3),
        baseline_hour_majority=round(base_rates.get("hour_majority", 0), 3),
        baseline_pair_hour_majority=round(base_rates.get("pair_hour_majority", 0), 3),
        max_baseline=round(max_base, 3),
        lift_vs_baseline_pp=round(lift_pp, 2),
        banda=banda,
        low_n_flag=n_trades < LOW_N_THRESHOLD,
        direction_executor=direction_executor,
    )


# ---------------------------------------------------------------------------
# Single-system runner (skeleton — full batch driver TODO_BATCH)
# ---------------------------------------------------------------------------


def run_one(system_id: str, base_dir: Path, loader: OhlcLoader | None = None) -> dict:
    """Smoke-test runner for one system. Returns dict with per-pair + aggregate metrics.

    Per spec §4 — ALL operations on frozen inputs. Does not modify any source file.
    Output is in-memory only; CSV/memo emitter is the batch driver responsibility.
    """
    rule = load_frozen_rule(system_id, base_dir)
    if not rule.pairs or not rule.entry_hours_utc or rule.direction_feature is None:
        return {
            "system_id": system_id,
            "status": "skipped_unparseable",
            "reason": (
                f"pairs={rule.pairs} hours={rule.entry_hours_utc} "
                f"feat={rule.direction_feature}"
            ),
        }

    # Locate trades.parquet
    p_trades = base_dir / "data" / "trades" / system_id / "trades.parquet"
    if not p_trades.exists() and system_id == "1407880":
        p_trades = base_dir / "2026-05-01-happy_market_hours_v231" / "data" / "trades_1407880.parquet"
    if not p_trades.exists():
        return {"system_id": system_id, "status": "no_trades_parquet"}
    trades = pd.read_parquet(p_trades)

    window = build_candidate_window(rule, trades)
    if window.empty:
        return {"system_id": system_id, "status": "empty_window"}
    window = label_entries(window, trades)

    n_trades_real = int((trades["is_trade"] == True).sum())
    print(
        f"[{system_id}] window={len(window)} bars, "
        f"actual_entries={int(window['y_entry'].sum())}, "
        f"trades={n_trades_real}, hours={sorted(rule.entry_hours_utc)}",
        flush=True,
    )

    # Feature extraction on candidates: re-uses decoder_features.compute_entry_features
    # but with synthetic anchors. We construct a "virtual trades_df" matching its API.
    if loader is None:
        loader = OhlcLoader(freq=BAR_FREQ)
    virt_trades = pd.DataFrame({
        "symbol": window["pair"],
        "open_dt_utc": window["ts"],
        "action": "Buy",  # dummy; we don't use y_buy
        "is_trade": True,
    })
    feats, stats = compute_entry_features(virt_trades, loader, peer_pairs=rule.pairs, progress=False)
    print(f"[{system_id}] features extracted: {stats}", flush=True)

    # Align features index to window
    feats = feats.reset_index(drop=True)
    window = window.reset_index(drop=True)
    cw = pd.concat([window, feats], axis=1)

    # Apply rule
    pred_dir = apply_direction_rule(rule, cw)
    pred_entry = (pred_dir != "NA").astype(int)  # rule "fires" wherever feature exists

    # Baselines
    bases = {
        "always_buy": baseline_always_buy(cw),
        "hour_majority": baseline_hour_majority(cw, trades),
        "pair_hour_majority": baseline_pair_hour_majority(cw, trades),
    }

    n_days = max(
        (cw["ts"].max() - cw["ts"].min()).total_seconds() / 86400,
        1.0,
    )

    # Aggregate metrics
    n_actual_total = int(cw["y_entry"].sum())
    agg = compute_metrics(
        cw, pred_dir, pred_entry, n_actual_total, n_days,
        system_id, "AGGREGATE", rule.direction_executor, n_trades_real, bases,
    )

    # Per-pair metrics
    per_pair = []
    for pair, sub in cw.groupby("pair"):
        sub = sub.reset_index(drop=True)
        sub_pred_dir = pred_dir.loc[sub.index]
        sub_pred_entry = pred_entry.loc[sub.index]
        sub_bases = {k: v.loc[sub.index] for k, v in bases.items()}
        n_actual_pair = int(sub["y_entry"].sum())
        m = compute_metrics(
            sub, sub_pred_dir, sub_pred_entry, n_actual_pair, n_days,
            system_id, pair, rule.direction_executor, n_trades_real, sub_bases,
        )
        per_pair.append(m.__dict__)

    return {
        "system_id": system_id,
        "status": "ok",
        "rule_summary": {
            "family": rule.family,
            "confidence": rule.confidence,
            "feature": rule.direction_feature,
            "op": rule.direction_op,
            "threshold": rule.direction_threshold,
            "direction_executor": rule.direction_executor,
            "entry_hours": sorted(rule.entry_hours_utc),
            "pairs": rule.pairs,
        },
        "aggregate": agg.__dict__,
        "per_pair": per_pair,
    }


# ---------------------------------------------------------------------------
# Batch driver — TODO_BATCH next session
# ---------------------------------------------------------------------------


def run_batch(top10_ids: list[str], base_dir: Path, csv_out: Path, memo_out: Path) -> None:
    """TODO_BATCH (next session): iterate run_one over top-10 + aggregate to CSV + memo.
    Spec: `specs/replicator_lite_pre_reg.md` §4.7."""
    raise NotImplementedError("Batch driver pending next session per 007-opus.md time budget")
