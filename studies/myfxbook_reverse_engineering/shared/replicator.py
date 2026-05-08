"""Replicator (full) — Phase 5R-1 of the decode-and-score pipeline.

Replaces `replicator_lite.py`. Implements:

  * Rule executor cascade: yaml_literal → tree_rank1 → ripper_rank1 → univariate_rank1
  * Backtest engine: entry on rule fire (M5 bar) → exit on max_holding_hours →
    PnL via OHLC[entry].open vs OHLC[exit].open (no costs; Stage 3 models them).
  * Synthetic trades parquet schema-compatible with `data/trades/<id>/trades.parquet`.
  * Comparator: synthetic-vs-real match within ±5min + symbol + direction.
  * Score formula 0-1 with 6 terms (lift_vs_baseline included for anti-degenerate),
    NaN→0 convention, count_ratio_proximity log2-symmetric.

Spec authority:
  * `specs/replicator_lite_pre_reg.md` — case-control entry detection (frozen)
  * `specs/replicator_full_addendum.md` — backtest + executors + schema (frozen)
  * `specs/decoding_score_formula.md` — score formula (frozen)

Citations (Regra 2 CLAUDE.md):
  * [advances_fin_ml, ch.5] — feature importance + clustered MDA
  * [evidence_based_ta, p.367-380] — session/hour FX regime + pip convention
  * [evidence_based_ta, p.247-260] — data-mining bias / baseline lift
  * [chan_quant_trading, ch.3] — direction predictability
  * [testing_tuning] — KS distribution comparison sim-vs-live
  * [systematic_trading, ch.4] — equity-curve correlation diagnostic
  * [advances_fin_ml, p.196-211] — DSR/PBO downstream Stage 3
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Literal

import numpy as np
import pandas as pd
from scipy import stats

from .decoder_features import compute_entry_features
from .ohlc_dukascopy import OhlcLoader, _DUKAS_PAIR_MAP

# ===========================================================================
# Constants — frozen by spec; do NOT tune.
# ===========================================================================

BAR_FREQ = "M5"
BAR_MINUTES = 5
BAR_MINUTES_BY_FREQ = {"M1": 1, "M5": 5}
ENTRY_TOL_MINUTES = 5  # ±5 min match window
DEFAULT_MAX_HOLDING_HOURS = 24.0  # fallback when frozen rule has no max_holding_hours
LOW_N_TRADES_THRESHOLD = 50
LOW_N_MATCHED_THRESHOLD = 5
SCORE_LIFT_NORMALIZATION_PP = 20.0  # lift in pp that maps to baseline_lift_normalized=1.0

Direction = Literal["Buy", "Sell", "NA"]
Banda = Literal["HIGH", "MEDIUM", "LOW", "NONE"]


# ===========================================================================
# Pip table — FX majors / Gold / Crypto.
# ===========================================================================

# pip_size: smallest price unit per pair (1 pip = X price units)
# usd_per_pip_per_lot: USD value of 1 pip per 1 standard lot (100,000 units)
# Source: standard FX broker conventions [evidence_based_ta, p.367-380].
_PIP_TABLE: dict[str, tuple[float, float]] = {
    # FX majors / crosses (USD-quoted; 1 pip = 0.0001; $10 per pip per std lot)
    "EURUSD": (0.0001, 10.0),
    "GBPUSD": (0.0001, 10.0),
    "AUDUSD": (0.0001, 10.0),
    "NZDUSD": (0.0001, 10.0),
    "USDCAD": (0.0001, 7.4),  # approx, USD-base
    "USDCHF": (0.0001, 11.0),
    "USDJPY": (0.01, 6.7),    # JPY pair: pip=0.01
    "EURGBP": (0.0001, 12.4),
    "EURCHF": (0.0001, 11.0),
    "EURJPY": (0.01, 6.7),
    "GBPJPY": (0.01, 6.7),
    "GBPCHF": (0.0001, 11.0),
    "AUDJPY": (0.01, 6.7),
    "CHFJPY": (0.01, 6.7),
    "EURAUD": (0.0001, 6.6),
    "EURCAD": (0.0001, 7.4),
    "GBPAUD": (0.0001, 6.6),
    "GBPCAD": (0.0001, 7.4),
    "AUDCHF": (0.0001, 11.0),
    "AUDCAD": (0.0001, 7.4),
    "AUDNZD": (0.0001, 6.0),
    "NZDJPY": (0.01, 6.7),
    "NZDCHF": (0.0001, 11.0),
    "CADCHF": (0.0001, 11.0),
    "CADJPY": (0.01, 6.7),
    # Metals (XAUUSD: 1 pip = 0.01 typically; $1 per pip per 100oz lot)
    "XAUUSD": (0.01, 1.0),
    "XAGUSD": (0.001, 5.0),
    # Crypto (1 pip = 1.0 USD; $1 per pip per 1 BTC contract; approximation)
    "BTCUSD": (1.0, 1.0),
    "ETHUSD": (0.01, 1.0),
}


def pip_size(pair: str) -> float:
    """Smallest price increment for `pair`. Defaults to 0.0001 (FX-major-like)."""
    return _PIP_TABLE.get(pair, (0.0001, 10.0))[0]


def usd_per_pip(pair: str) -> float:
    """USD value of 1 pip per 1 standard lot (100k units). Defaults to $10."""
    return _PIP_TABLE.get(pair, (0.0001, 10.0))[1]


# ===========================================================================
# Frozen rule + cascading rule executors.
# ===========================================================================


@dataclass
class RuleExecutor:
    """Vectorized rule executor. `apply(features_df)` returns a Series of Buy/Sell/NA."""

    name: str  # 'yaml_literal' | 'tree_rank1' | 'ripper_rank1' | 'univariate_rank1'
    apply_fn: Callable[[pd.DataFrame], pd.Series]
    features_used: list[str]

    def apply(self, features_df: pd.DataFrame) -> pd.Series:
        return self.apply_fn(features_df)


@dataclass
class FrozenRule:
    system_id: str
    family: str
    confidence: float
    pairs: list[str]
    entry_hours_utc: set[int]
    max_holding_hours: float
    used_default_holding: bool
    executor: RuleExecutor
    raw_rule_text: str  # full direction body for audit
    # 5R-1-hardening Wave B item 2 (2026-05-02): UNCAT requires reason_code;
    # any non-enum label goes to candidate_new_family. v2 frozen_rules predate
    # the rule and may have None for both — see decoder_taxonomy.validate_decoder_output
    # called below with strict=False for legacy compat.
    reason_code: str | None = None
    candidate_new_family: str | None = None


# --- universal-rule-text utilities ------------------------------------------


_UNIVARIATE_RE = re.compile(
    r"^\s*([a-zA-Z0-9_]+)\s*(>=|<=|>|<|==|!=)\s*(-?[0-9.eE+]+)\s*[⇒=>→]+\s*(Buy|Sell)\s*$"
)


def _parse_univariate_text(text: str) -> tuple[str, str, float, str] | None:
    m = _UNIVARIATE_RE.match(text.strip())
    if not m:
        return None
    feat, op, thr, side = m.groups()
    return feat, op, float(thr), side


def _make_univariate_executor(feat: str, op: str, thr: float, side_true: str) -> RuleExecutor:
    side_false = "Sell" if side_true == "Buy" else "Buy"

    def apply_fn(df: pd.DataFrame) -> pd.Series:
        if feat not in df.columns:
            return pd.Series(["NA"] * len(df), index=df.index)
        f = df[feat]
        if op == ">":
            cond = f > thr
        elif op == ">=":
            cond = f >= thr
        elif op == "<":
            cond = f < thr
        elif op == "<=":
            cond = f <= thr
        elif op == "==":
            cond = f == thr
        elif op == "!=":
            cond = f != thr
        else:
            return pd.Series(["NA"] * len(df), index=df.index)
        out = pd.Series([side_false] * len(df), index=df.index, dtype=object)
        out.loc[cond.fillna(False)] = side_true
        out.loc[f.isna()] = "NA"
        return out

    return RuleExecutor(name="univariate_rank1", apply_fn=apply_fn, features_used=[feat])


# --- tree parser (sklearn ASCII tree) ---------------------------------------


_TREE_LINE_RE = re.compile(r"^(\|(\s+|---)*)?\s*([a-zA-Z0-9_]+)\s*(>=|<=|>|<)\s*(-?[0-9.eE+]+)\s*$")
_TREE_CLASS_RE = re.compile(r"^(\|(\s+|---)*)?\s*class:\s*(-?\d+)\s*$")


def _parse_tree_paths(rule_text: str) -> list[tuple[list[tuple[str, str, float]], int]]:
    """Parse sklearn ASCII tree into list of (path_conditions, leaf_class).

    Conditions are (feature, op, threshold) tuples. Op is one of <, <=, >, >=.
    """
    lines = [line for line in rule_text.splitlines() if line.strip().startswith("|")]
    paths: list[tuple[list[tuple[str, str, float]], int]] = []
    stack: list[tuple[int, str, str, float]] = []  # (depth, feat, op, thr)

    def line_depth(s: str) -> int:
        return s.count("|---")

    for line in lines:
        m_cond = re.match(
            r"^\s*(\|\s*)+(?:---\s*)?([a-zA-Z0-9_]+)\s*(>=|<=|>|<)\s*(-?[0-9.eE+]+)\s*$", line
        )
        m_class = re.match(r"^\s*(\|\s*)+(?:---\s*)?class:\s*(-?\d+)\s*$", line)
        depth = line.count("|")
        if m_cond:
            _, feat, op, thr = m_cond.groups()
            while stack and stack[-1][0] >= depth:
                stack.pop()
            stack.append((depth, feat, op, float(thr)))
        elif m_class:
            cls = int(m_class.group(2))
            conds = [(feat, op, thr) for (_d, feat, op, thr) in stack]
            paths.append((conds, cls))
    return paths


def _try_parse_tree(candidates: list[dict]) -> RuleExecutor | None:
    """Build executor from `tree` candidate rank 1.

    Class mapping: class=1 → first dominant direction (inferred from majority of
    `direction_when_majority` if available; fallback to "Buy"). Class=0 → opposite.
    """
    for c in candidates:
        if c.get("miner") != "tree" or c.get("rank") != 1:
            continue
        rule_text = c.get("rule_text", "")
        paths = _parse_tree_paths(rule_text)
        if not paths:
            continue
        # If all leaves have the same class, the tree is degenerate (always-X).
        # Don't reject — return executor that always fires that direction; the
        # baseline_lift term in the score will catch it as degenerate.
        classes = {leaf for _conds, leaf in paths}
        # Direction polarity: class=1 → primary direction. We conventionally map
        # class=1 → Buy, class=0 → Sell; if frozen rule's direction text says
        # otherwise (BUY if X), the yaml_literal parser handles it earlier in the
        # cascade. Tree fallback uses Buy/Sell convention.
        side_true = "Buy"  # class=1
        side_false = "Sell"  # class=0
        feats_used = sorted({f for path, _ in paths for (f, _op, _thr) in path})

        def apply_fn(df: pd.DataFrame) -> pd.Series:
            out = pd.Series(["NA"] * len(df), index=df.index, dtype=object)
            for conds, leaf in paths:
                mask = pd.Series([True] * len(df), index=df.index)
                any_missing = pd.Series([False] * len(df), index=df.index)
                for feat, op, thr in conds:
                    if feat not in df.columns:
                        return pd.Series(["NA"] * len(df), index=df.index)
                    fv = df[feat]
                    any_missing = any_missing | fv.isna()
                    if op == "<=":
                        cmask = fv <= thr
                    elif op == "<":
                        cmask = fv < thr
                    elif op == ">":
                        cmask = fv > thr
                    elif op == ">=":
                        cmask = fv >= thr
                    else:
                        cmask = pd.Series([False] * len(df), index=df.index)
                    mask = mask & cmask.fillna(False)
                # Only assign where path matches AND all features present
                final_mask = mask & ~any_missing
                out.loc[final_mask] = side_true if leaf == 1 else side_false
            return out

        return RuleExecutor(name="tree_rank1", apply_fn=apply_fn, features_used=feats_used)
    return None


# --- ripper parser (RIPPER notation) ----------------------------------------


def _try_parse_ripper(candidates: list[dict]) -> RuleExecutor | None:
    """Build executor from `ripper` candidate rank 1.

    RIPPER rule text format examples:
        "[bb_pos > 0.15 ^ ret_10 < -0.001] V [hour_utc == 23] => Sell"
        "prior_bar_sign_H4 = -1 AND (ret_10_M15 < -0.00092 OR hour_utc == 23) => Sell"

    Parser is best-effort: handles `^`/`AND`, `V`/`OR`, square brackets, and
    `feat OP value` literals. Falls back to None on parse failure.
    """
    for c in candidates:
        if c.get("miner") != "ripper" or c.get("rank") != 1:
            continue
        text = c.get("rule_text", "").strip()
        # Extract direction from `=> Sell` / `=> Buy` (or ⇒)
        m_dir = re.search(r"[⇒=>→]+\s*(Buy|Sell)\s*$", text)
        if not m_dir:
            continue
        side_true = m_dir.group(1)
        side_false = "Sell" if side_true == "Buy" else "Buy"
        body = text[: m_dir.start()].strip()
        # Normalize logical operators
        body = body.replace("AND", "^").replace("OR", "V").replace("∧", "^").replace("∨", "V")
        # Split on top-level V (OR) — simple impl, no nested parens beyond depth 1
        clauses_text = re.split(r"(?<![∧^])V(?![∨])", body)
        clauses: list[list[tuple[str, str, float]]] = []
        feats_used: set[str] = set()
        for ct in clauses_text:
            ct = ct.strip().lstrip("[").rstrip("]").strip()
            literals = re.split(r"\^", ct)
            parsed_lits: list[tuple[str, str, float]] = []
            for lit in literals:
                lit = lit.strip().lstrip("(").rstrip(")").strip()
                m_lit = re.match(
                    r"^([a-zA-Z0-9_]+)\s*(>=|<=|>|<|==|!=|=)\s*(-?[0-9.eE+]+)\s*$", lit
                )
                if not m_lit:
                    return None  # bail out on parse failure
                feat, op, val = m_lit.groups()
                if op == "=":
                    op = "=="
                parsed_lits.append((feat, op, float(val)))
                feats_used.add(feat)
            if parsed_lits:
                clauses.append(parsed_lits)
        if not clauses:
            return None

        def apply_fn(df: pd.DataFrame) -> pd.Series:
            for f in feats_used:
                if f not in df.columns:
                    return pd.Series(["NA"] * len(df), index=df.index)
            any_clause_fires = pd.Series([False] * len(df), index=df.index)
            any_missing = pd.Series([False] * len(df), index=df.index)
            for clause in clauses:
                clause_mask = pd.Series([True] * len(df), index=df.index)
                for feat, op, val in clause:
                    fv = df[feat]
                    any_missing = any_missing | fv.isna()
                    if op == "<=":
                        cm = fv <= val
                    elif op == "<":
                        cm = fv < val
                    elif op == ">":
                        cm = fv > val
                    elif op == ">=":
                        cm = fv >= val
                    elif op == "==":
                        cm = fv == val
                    elif op == "!=":
                        cm = fv != val
                    else:
                        cm = pd.Series([False] * len(df), index=df.index)
                    clause_mask = clause_mask & cm.fillna(False)
                any_clause_fires = any_clause_fires | clause_mask
            out = pd.Series([side_false] * len(df), index=df.index, dtype=object)
            out.loc[any_clause_fires] = side_true
            out.loc[any_missing] = "NA"
            return out

        return RuleExecutor(
            name="ripper_rank1", apply_fn=apply_fn, features_used=sorted(feats_used)
        )
    return None


# --- yaml_literal parser ('BUY if X' / 'SELL otherwise') ---------------------


_YAML_IF_RE = re.compile(
    r"^\s*(BUY|SELL)\s+if\s+([a-zA-Z0-9_]+)\s*(>=|<=|>|<|==|!=)\s*(-?[0-9.eE+]+)\s*$",
    re.IGNORECASE,
)
_YAML_OTHERWISE_RE = re.compile(r"^\s*(BUY|SELL)\s+otherwise\s*$", re.IGNORECASE)


def _try_parse_yaml_literal(rule_text: str) -> RuleExecutor | None:
    """Parse the `direction:` body of signal_rule.md when it's prose pseudo-Python.

    Supports a single primary `BUY/SELL if feat OP value` line plus an optional
    `BUY/SELL otherwise`. More complex multi-clause forms fall through to tree.
    """
    if not rule_text:
        return None
    primary: tuple[str, str, str, float] | None = None
    fallback_side: str | None = None
    for line in rule_text.splitlines():
        line = line.strip().lstrip("#").strip()
        if not line or line.startswith("#"):
            continue
        m_if = _YAML_IF_RE.match(line)
        m_other = _YAML_OTHERWISE_RE.match(line)
        if m_if and primary is None:
            side, feat, op, val = m_if.groups()
            primary = (side.capitalize(), feat, op, float(val))
        elif m_other and fallback_side is None:
            fallback_side = m_other.group(1).capitalize()
    if primary is None:
        return None
    side_true, feat, op, thr = primary
    side_false = fallback_side or ("Sell" if side_true == "Buy" else "Buy")

    def apply_fn(df: pd.DataFrame) -> pd.Series:
        if feat not in df.columns:
            return pd.Series(["NA"] * len(df), index=df.index)
        fv = df[feat]
        if op == "<=":
            cmask = fv <= thr
        elif op == "<":
            cmask = fv < thr
        elif op == ">":
            cmask = fv > thr
        elif op == ">=":
            cmask = fv >= thr
        elif op == "==":
            cmask = fv == thr
        elif op == "!=":
            cmask = fv != thr
        else:
            return pd.Series(["NA"] * len(df), index=df.index)
        out = pd.Series([side_false] * len(df), index=df.index, dtype=object)
        out.loc[cmask.fillna(False)] = side_true
        out.loc[fv.isna()] = "NA"
        return out

    return RuleExecutor(name="yaml_literal", apply_fn=apply_fn, features_used=[feat])


# --- cascade -----------------------------------------------------------------


def _try_parse_univariate(candidates: list[dict]) -> RuleExecutor | None:
    for c in candidates:
        if c.get("miner") != "univariate":
            continue
        parsed = _parse_univariate_text(c.get("rule_text", ""))
        if parsed is None:
            continue
        feat, op, thr, side = parsed
        return _make_univariate_executor(feat, op, thr, side)
    return None


def _build_executor(rule_text: str, candidates: list[dict]) -> RuleExecutor:
    for fn in (
        lambda: _try_parse_yaml_literal(rule_text),
        lambda: _try_parse_tree(candidates),
        lambda: _try_parse_ripper(candidates),
        lambda: _try_parse_univariate(candidates),
    ):
        ex = fn()
        if ex is not None:
            return ex
    raise ValueError("No parseable rule from yaml/tree/ripper/univariate cascade")


# ===========================================================================
# Frozen rule loading (with cascade-aware parser).
# ===========================================================================


def _expand_window_to_hours(window: list[str]) -> set[int]:
    if not window or len(window) != 2:
        return set()
    h0 = int(window[0].split(":")[0])
    h1 = int(window[1].split(":")[0])
    if h0 <= h1:
        return set(range(h0, h1 + 1))
    return set(range(h0, 24)) | set(range(0, h1 + 1))


def load_frozen_rule(system_id: str, base_dir: Path) -> FrozenRule:
    p_rule = base_dir / "frozen_rules" / f"{system_id}.md"
    p_cand = base_dir / "systems" / system_id / "decoder" / "candidates.json"
    p_fp = base_dir / "systems" / system_id / "decoder" / "fingerprint.md"
    if not p_rule.exists():
        raise FileNotFoundError(p_rule)
    if not p_cand.exists():
        raise FileNotFoundError(p_cand)

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
    # (mandatory in R1 v3; absent in v2). Read non-strictly — DeprecationWarning
    # if missing/invalid for legacy v2.
    rc = re.search(r"^reason_code:\s*(\S+)", block, re.MULTILINE)
    reason_code = rc.group(1).strip() if rc else None
    cnf = re.search(r"^candidate_new_family:\s*(\S+)", block, re.MULTILINE)
    candidate_new_family = cnf.group(1).strip() if cnf else None
    # Skip null-string sentinels
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
        strict=False,  # v2 legacy permissive; R1 v3 onwards will be strict at write-time
    )

    win = re.search(
        r"entry_window_utc:\s*\[\s*\"?([0-9:]+)\"?\s*,\s*\"?([0-9:]+)\"?\s*\]", block
    )
    window = [win.group(1), win.group(2)] if win else []
    hours = _expand_window_to_hours(window) if window else set()

    pm = re.search(r"pairs:\s*\[([^\]]+)\]", block)
    pairs: list[str] = []
    if pm:
        pairs = [p.strip().strip('"').strip("'") for p in pm.group(1).split(",") if p.strip()]

    hm = re.search(r"max_holding_hours:\s*([0-9.]+|null|None|nan|NaN)", block)
    if hm and hm.group(1) not in ("null", "None", "nan", "NaN"):
        max_hold = float(hm.group(1))
        used_default = False
    else:
        max_hold = DEFAULT_MAX_HOLDING_HOURS
        used_default = True

    # Fallback: parse fingerprint top-3 hours
    if not hours and p_fp.exists():
        fp_text = p_fp.read_text()
        m_fp = re.search(
            r"Top entry hours \(UTC\):\s*((?:- \d{1,2}:00 — \d+ trades\s*)+)", fp_text
        )
        if m_fp:
            hour_lines = re.findall(r"- (\d{1,2}):00 — (\d+) trades", m_fp.group(1))
            hour_lines.sort(key=lambda x: -int(x[1]))
            hours = {int(h) for h, _ in hour_lines[:3]}

    # Extract direction body for yaml_literal cascade (between `direction: |` and next yaml key)
    rule_text_match = re.search(
        r"direction:\s*\|\n(.*?)(?=\n\s{2,4}exit:|\n\s{0,4}[a-zA-Z_]+:)", block, re.DOTALL
    )
    direction_body = rule_text_match.group(1) if rule_text_match else ""

    candidates = json.load(open(p_cand))
    executor = _build_executor(direction_body, candidates)

    return FrozenRule(
        system_id=system_id,
        family=family,
        confidence=confidence,
        pairs=pairs,
        entry_hours_utc=hours,
        max_holding_hours=max_hold,
        used_default_holding=used_default,
        reason_code=reason_code,
        candidate_new_family=candidate_new_family,
        executor=executor,
        raw_rule_text=direction_body,
    )


# ===========================================================================
# Candidate window + entry labels.
# ===========================================================================


def _bar_minutes(bar_freq: str) -> int:
    if bar_freq not in BAR_MINUTES_BY_FREQ:
        raise ValueError(f"Unsupported bar_freq {bar_freq!r}; expected one of {sorted(BAR_MINUTES_BY_FREQ)}")
    return BAR_MINUTES_BY_FREQ[bar_freq]


def build_candidate_window(rule: FrozenRule, trades: pd.DataFrame, *, bar_freq: str = BAR_FREQ) -> pd.DataFrame:
    trades = trades[trades["is_trade"] == True]
    if trades.empty:
        return pd.DataFrame(columns=["pair", "ts"])

    pairs_in_data = sorted(trades["symbol"].dropna().unique().tolist())
    rule_pairs = [p for p in pairs_in_data if p in rule.pairs] or pairs_in_data
    rule_pairs = [p for p in rule_pairs if p in _DUKAS_PAIR_MAP]

    minutes = _bar_minutes(bar_freq)
    freq = f"{minutes}min"
    t_min = pd.to_datetime(trades["open_dt_utc"].min()).floor(freq)
    t_max = pd.to_datetime(trades["open_dt_utc"].max()).ceil(freq)

    rows: list[dict] = []
    ts_range = pd.date_range(t_min, t_max, freq=freq, tz="UTC")
    if rule.entry_hours_utc:
        ts_range = ts_range[ts_range.hour.isin(rule.entry_hours_utc)]
    for pair in rule_pairs:
        for ts in ts_range:
            rows.append({"pair": pair, "ts": ts})
    return pd.DataFrame(rows)


def label_real_entries(
    window: pd.DataFrame, trades: pd.DataFrame, *, bar_freq: str = BAR_FREQ
) -> pd.DataFrame:
    """Add `y_entry` (0/1) and `y_direction` (Buy/Sell/NA) per (pair, ts) bin."""
    trades = trades[trades["is_trade"] == True].copy()
    trades["ts_bin"] = pd.to_datetime(trades["open_dt_utc"]).dt.floor(
        f"{_bar_minutes(bar_freq)}min"
    )
    truth = (
        trades.groupby(["symbol", "ts_bin"])
        .agg(y_direction=("action", "first"))
        .reset_index()
    )
    out = window.merge(
        truth, left_on=["pair", "ts"], right_on=["symbol", "ts_bin"], how="left"
    )
    out["y_entry"] = out["y_direction"].notna().astype(int)
    out["y_direction"] = out["y_direction"].fillna("NA")
    return out.drop(columns=["symbol", "ts_bin"], errors="ignore")


# ===========================================================================
# Feature extraction wrapper.
# ===========================================================================


_TF_TO_PANDAS = {
    "M1": "1min", "M5": "5min", "M15": "15min",
    "H1": "1h", "H4": "4h",
}


def _resample_ohlc(m5: pd.DataFrame, freq: str) -> pd.DataFrame:
    """Resample M5 → target timeframe via pandas. UTC-indexed input expected."""
    if freq == "M5":
        return m5
    rule = _TF_TO_PANDAS.get(freq, freq)
    if freq == "M1":
        # Can't reconstruct M1 from M5 — fall back to M5.
        return m5
    out = m5.resample(rule, label="right", closed="right").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    ).dropna()
    return out


def _timeframes_for_base(bar_freq: str) -> tuple[str, ...]:
    if bar_freq == "M1":
        return ("M1", "M5", "M15", "H1", "H4")
    return ("M5", "M15", "H1", "H4")


def _vectorized_indicators(
    ohlc: pd.DataFrame, ema_len: int = 20, bb_len: int = 20, atr_len: int = 14
) -> pd.DataFrame:
    """Compute rolling indicators on a full OHLC timeline. Returns DataFrame
    aligned to ohlc.index with columns:
        ema_dist_20, bb_pos_20_2, range_norm, prior_bar_sign,
        ret_1, ret_3, ret_10, atr_14, close
    SHIFTED so value at index t uses only bars STRICTLY BEFORE t (no lookahead).
    """
    close = ohlc["close"].astype(float)
    high = ohlc["high"].astype(float)
    low = ohlc["low"].astype(float)
    open_ = ohlc["open"].astype(float)

    # ATR
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    atr = tr.rolling(atr_len, min_periods=atr_len).mean()

    # EMA
    ema = close.ewm(span=ema_len, adjust=False, min_periods=ema_len).mean()
    ema_dist = (close - ema) / atr

    # BB
    sma = close.rolling(bb_len, min_periods=bb_len).mean()
    std = close.rolling(bb_len, min_periods=bb_len).std()
    bb_pos = (close - sma) / (2.0 * std)
    bb_pos = bb_pos.where(std > 0, other=np.nan)

    # Returns (log)
    ret_1 = np.log(close / close.shift(1))
    ret_3 = np.log(close / close.shift(3))
    ret_10 = np.log(close / close.shift(10))

    # Range / sign
    range_norm = (high - low) / atr
    prior_sign = np.sign(close - open_)

    out = pd.DataFrame(
        {
            "ema_dist_20": ema_dist,
            "bb_pos_20_2": bb_pos,
            "range_norm": range_norm,
            "prior_bar_sign": prior_sign,
            "ret_1": ret_1,
            "ret_3": ret_3,
            "ret_10": ret_10,
            "atr_14": atr,
            "close": close,
        },
        index=ohlc.index,
    )
    # Shift by 1 — features at time t use only bars up to t-1 (no lookahead).
    out = out.shift(1)
    return out


def extract_features_for_window(
    window: pd.DataFrame,
    peer_pairs: list[str],
    loader: OhlcLoader,
    *,
    bar_freq: str = BAR_FREQ,
) -> pd.DataFrame:
    """Vectorized multi-tf feature extraction over the candidate window.

    Pre-loads M5 OHLC per pair once, resamples to {M5, M15, H1, H4}, computes
    rolling indicators vectorized, then point-lookups at candidate ts (with
    no-lookahead shift).

    Returns DataFrame aligned to `window.index` with feature columns matching
    the names in candidates.json (e.g., bb_pos_20_2_M15, ret_10_H1, ...).
    Includes calendar columns (hour_utc, dow) for rules that gate on them.

    Per replicator_full_addendum §3.5: lookback ends strictly before t.
    """
    if window.empty:
        return pd.DataFrame()

    pairs = sorted(window["pair"].unique().tolist())
    t_min = pd.to_datetime(window["ts"].min(), utc=True)
    t_max = pd.to_datetime(window["ts"].max(), utc=True)

    timeframes = _timeframes_for_base(bar_freq)

    # Pre-load base-frequency OHLC per pair, resample to needed timeframes, compute indicators.
    indicators_by_pair_tf: dict[tuple[str, str], pd.DataFrame] = {}
    for pair in pairs:
        base_ohlc = _preload_ohlc(loader, pair, t_min, t_max, bar_freq=bar_freq)
        if base_ohlc is None or base_ohlc.empty:
            continue
        for tf in timeframes:
            tf_ohlc = _resample_ohlc(base_ohlc, tf)
            ind = _vectorized_indicators(tf_ohlc)
            indicators_by_pair_tf[(pair, tf)] = ind

    # Build feature frame indexed like window. Internal `_pair`/`_ts` are used
    # for the merge_asof joins below and dropped before returning, so we don't
    # duplicate columns already present on `window`.
    out = pd.DataFrame(index=window.index)
    _pair = window["pair"].values
    _ts = pd.to_datetime(window["ts"].values, utc=True)
    out["hour_utc"] = pd.Series(_ts).dt.hour.values
    out["dow"] = pd.Series(_ts).dt.dayofweek.values
    out["minute"] = pd.Series(_ts).dt.minute.values

    # For each tf, do an as-of join (last bar of tf at-or-before each candidate ts)
    for tf in timeframes:
        # Concat all pairs' indicators for this tf with a 'pair' column
        frames = []
        for (pair, t), ind in indicators_by_pair_tf.items():
            if t != tf or ind.empty:
                continue
            f = ind.copy()
            f["pair"] = pair
            f["tf_ts"] = f.index
            frames.append(f)
        if not frames:
            continue
        # merge_asof with `by=` requires the `on` column sorted globally.
        all_ind = pd.concat(frames).sort_values("tf_ts").reset_index(drop=True)

        win_sorted = pd.DataFrame({"pair": _pair, "ts": _ts})
        win_sorted["_orig_idx"] = win_sorted.index
        win_sorted = win_sorted.sort_values("ts").reset_index(drop=True)

        merged = pd.merge_asof(
            win_sorted,
            all_ind,
            left_on="ts",
            right_on="tf_ts",
            by="pair",
            direction="backward",
        )

        # Restore original order
        merged = merged.sort_values("_orig_idx").reset_index(drop=True)

        # Add tf-suffixed columns to out
        for col in ("ema_dist_20", "bb_pos_20_2", "range_norm", "prior_bar_sign",
                    "ret_1", "ret_3", "ret_10", "atr_14"):
            if col in merged.columns:
                out[f"{col}_{tf}"] = merged[col].values

    return out


# ===========================================================================
# Backtest engine — entry → exit → PnL → synthetic_trades.parquet.
# ===========================================================================


def _preload_ohlc(
    loader: OhlcLoader,
    pair: str,
    t_min: pd.Timestamp,
    t_max: pd.Timestamp,
    *,
    bar_freq: str = BAR_FREQ,
) -> pd.DataFrame | None:
    """Bulk-load OHLC for `pair` across [t_min, t_max + buffer]. UTC-indexed.

    Returns the full M5 frame so subsequent lookups are O(log n) via .loc[ts].
    Adds a buffer to t_max so exits with max_holding can still find their bar.
    """
    if pair not in _DUKAS_PAIR_MAP:
        return None
    start = (t_min - pd.Timedelta(hours=2)).to_pydatetime()
    end = (t_max + pd.Timedelta(days=14)).to_pydatetime()
    try:
        bars = loader.load(pair, start, end, freq=bar_freq)
    except Exception:
        return None
    if bars is None or bars.empty:
        return None
    bars = bars.copy()
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _read_ohlc_at(
    ohlc: pd.DataFrame | None, ts: pd.Timestamp, *, bar_freq: str = BAR_FREQ
) -> dict | None:
    """Lookup OHLC bar at `ts` (floored to base freq) in a preloaded frame."""
    if ohlc is None or ohlc.empty:
        return None
    target = ts.floor(f"{_bar_minutes(bar_freq)}min")
    if target not in ohlc.index:
        return None
    row = ohlc.loc[target]
    return {
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
    }


def run_backtest(
    rule: FrozenRule,
    candidates_with_features: pd.DataFrame,
    loader: OhlcLoader,
    *,
    bar_freq: str = BAR_FREQ,
) -> pd.DataFrame:
    """Generate synthetic trades from rule firings on candidate window.

    Returns DataFrame with synthetic-trade schema (replicator_full_addendum §3.4).
    """
    pred_dir = rule.executor.apply(candidates_with_features)
    fired = pred_dir.isin(["Buy", "Sell"])
    n_fires = int(fired.sum())
    if n_fires == 0:
        return pd.DataFrame(
            columns=[
                "record", "symbol", "action", "lots", "open_price", "close_price",
                "pips", "profit", "open_dt_utc", "close_dt_utc", "duration_sec",
                "is_trade", "is_deposit", "direction_executor", "exit_truncated",
            ]
        )

    fires = candidates_with_features.loc[fired, ["pair", "ts"]].copy()
    fires["action"] = pred_dir.loc[fired].values
    fires = fires.reset_index(drop=True)

    # Pre-load OHLC for each pair once (avoids n_fires × parquet reads).
    fire_pairs = sorted(fires["pair"].unique().tolist())
    t_min = pd.to_datetime(fires["ts"].min(), utc=True)
    t_max = pd.to_datetime(fires["ts"].max(), utc=True)
    ohlc_cache: dict[str, pd.DataFrame | None] = {
        pair: _preload_ohlc(loader, pair, t_min, t_max, bar_freq=bar_freq) for pair in fire_pairs
    }

    # Debouncing per pair: once a synthetic position is open until exit_ts, skip
    # any subsequent fires on that pair until current position closes. Mirrors
    # real-trader behavior of not stacking concurrent positions; without this,
    # rule fires at every M5 bar in the entry window, blowing up count_ratio.
    open_until: dict[str, pd.Timestamp] = {}
    fires = fires.sort_values(["pair", "ts"]).reset_index(drop=True)

    rows: list[dict] = []
    for i, fr in fires.iterrows():
        pair = fr["pair"]
        ohlc = ohlc_cache.get(pair)
        if ohlc is None:
            continue
        entry_ts = pd.to_datetime(fr["ts"], utc=True)
        if pair in open_until and entry_ts < open_until[pair]:
            continue
        action = fr["action"]
        entry_bar = _read_ohlc_at(ohlc, entry_ts, bar_freq=bar_freq)
        if entry_bar is None:
            continue
        exit_ts = (entry_ts + pd.Timedelta(hours=rule.max_holding_hours)).floor(
            f"{_bar_minutes(bar_freq)}min"
        )
        exit_bar = _read_ohlc_at(ohlc, exit_ts, bar_freq=bar_freq)
        exit_truncated = False
        if exit_bar is None:
            for offset_min in (-5, -10, -15, -30, -60, -120):
                cand_ts = exit_ts + pd.Timedelta(minutes=offset_min)
                exit_bar = _read_ohlc_at(ohlc, cand_ts, bar_freq=bar_freq)
                if exit_bar is not None:
                    exit_ts = cand_ts
                    exit_truncated = True
                    break
        if exit_bar is None:
            continue

        entry_price = entry_bar["open"]
        close_price = exit_bar["open"]
        ps = pip_size(pair)
        upp = usd_per_pip(pair)
        if action == "Buy":
            pips = (close_price - entry_price) / ps
        else:
            pips = (entry_price - close_price) / ps
        lots = 0.01
        profit = pips * upp * lots
        duration_sec = (exit_ts - entry_ts).total_seconds()

        rows.append(
            {
                "record": f"synth_{rule.system_id}_{pair}_{i}",
                "symbol": pair,
                "action": action,
                "lots": lots,
                "open_price": entry_price,
                "close_price": close_price,
                "pips": float(pips),
                "profit": float(profit),
                "open_dt_utc": entry_ts,
                "close_dt_utc": exit_ts,
                "duration_sec": float(duration_sec),
                "is_trade": True,
                "is_deposit": False,
                "direction_executor": rule.executor.name,
                "exit_truncated": exit_truncated,
            }
        )
        open_until[pair] = exit_ts

    return pd.DataFrame(rows)


# ===========================================================================
# Comparator — synthetic vs real (matches within ±5min + symbol).
# ===========================================================================


@dataclass
class ComparisonReport:
    system_id: str
    n_real: int
    n_synthetic: int
    n_matched: int
    entry_timing_precision: float
    entry_timing_recall: float
    entry_timing_f1: float
    direction_acc_at_matched: float  # NaN-safe -- np.nan if n_matched=0
    hold_KS_stat: float  # np.nan if either side <5
    hold_similarity: float
    count_ratio: float  # np.nan if n_real=0
    pnl_correlation: float  # np.nan if n_matched<5
    # Baseline lift terms (computed from real-only baselines; synth provides combined-hit count)
    baseline_always_buy_combined_hit_rate: float
    baseline_hour_majority_combined_hit_rate: float
    baseline_pair_hour_majority_combined_hit_rate: float
    max_baseline_combined_hit_rate: float
    synthetic_combined_hit_rate: float
    lift_vs_baseline_pp: float


def _match_within_tolerance(
    synth: pd.DataFrame, real: pd.DataFrame, tol_min: int = ENTRY_TOL_MINUTES
) -> pd.DataFrame:
    """Greedy matching: each synthetic trade gets at most one real match within ±tol_min.

    Returns DataFrame with `synth_idx, real_idx, dir_synth, dir_real, pnl_synth, pnl_real`.
    """
    if synth.empty or real.empty:
        return pd.DataFrame(
            columns=["synth_idx", "real_idx", "dir_synth", "dir_real", "pnl_synth", "pnl_real"]
        )

    s = synth[["symbol", "open_dt_utc", "action", "profit"]].reset_index().rename(
        columns={"index": "synth_idx", "action": "dir_synth", "profit": "pnl_synth"}
    )
    r = real[["symbol", "open_dt_utc", "action", "profit"]].reset_index().rename(
        columns={"index": "real_idx", "action": "dir_real", "profit": "pnl_real"}
    )
    s["open_dt_utc"] = pd.to_datetime(s["open_dt_utc"], utc=True)
    r["open_dt_utc"] = pd.to_datetime(r["open_dt_utc"], utc=True)
    # merge_asof with `by=` requires both sides sorted by `on` globally.
    s = s.sort_values("open_dt_utc").reset_index(drop=True)
    r = r.sort_values("open_dt_utc").reset_index(drop=True)
    matched = pd.merge_asof(
        s,
        r,
        on="open_dt_utc",
        by="symbol",
        tolerance=pd.Timedelta(minutes=tol_min),
        direction="nearest",
    )
    matched = matched.dropna(subset=["real_idx"])
    return matched[
        ["synth_idx", "real_idx", "dir_synth", "dir_real", "pnl_synth", "pnl_real"]
    ].reset_index(drop=True)


def _baseline_combined_hit_rates(
    candidates_with_features: pd.DataFrame, real_trades: pd.DataFrame
) -> tuple[float, float, float]:
    """Compute combined-hit rate (entry hits AND direction matches) for 3 trivial baselines.

    Each baseline always-fires; combined-hit counts how many `(pair, ts)` slots
    in candidate window coincide with a real entry AND the baseline direction
    matches the real direction. Normalized by n_real.

    [evidence_based_ta, p.247-260] — anti-data-mining-bias control.
    """
    n_real = max((real_trades["is_trade"] == True).sum(), 1)
    cw = candidates_with_features
    if "y_entry" not in cw.columns or "y_direction" not in cw.columns:
        return (0.0, 0.0, 0.0)
    truths_mask = cw["y_entry"] == 1

    # always_buy
    ab = int(((truths_mask) & (cw["y_direction"] == "Buy")).sum()) / n_real

    # hour_majority (majority direction per hour-of-day)
    rt = real_trades[real_trades["is_trade"] == True].copy()
    rt["hour"] = pd.to_datetime(rt["open_dt_utc"]).dt.hour
    maj_h = rt.groupby("hour")["action"].agg(
        lambda s: s.mode().iat[0] if len(s.mode()) else "Buy"
    )
    cw_hour = pd.to_datetime(cw["ts"]).dt.hour
    pred_h = cw_hour.map(maj_h).fillna("Buy")
    hm = int(((truths_mask) & (cw["y_direction"] == pred_h)).sum()) / n_real

    # pair_hour_majority
    maj_ph = rt.groupby(["symbol", "hour"])["action"].agg(
        lambda s: s.mode().iat[0] if len(s.mode()) else "Buy"
    )
    keys = list(zip(cw["pair"], cw_hour))
    pred_ph = pd.Series([maj_ph.get(k, "Buy") for k in keys], index=cw.index)
    phm = int(((truths_mask) & (cw["y_direction"] == pred_ph)).sum()) / n_real

    return (ab, hm, phm)


def compare(
    system_id: str,
    synth: pd.DataFrame,
    real: pd.DataFrame,
    candidates_with_features: pd.DataFrame,
) -> ComparisonReport:
    real_t = real[real["is_trade"] == True].copy()
    n_real = len(real_t)
    n_synth = len(synth)

    matches = _match_within_tolerance(synth, real_t)
    n_matched = len(matches)

    # Entry timing precision/recall/F1 (direction-agnostic for entry timing).
    # Each synthetic can match at most 1 real (greedy via merge_asof).
    tp = n_matched
    fp = max(n_synth - tp, 0)
    fn = max(n_real - tp, 0)
    prec = tp / max(tp + fp, 1) if (tp + fp) > 0 else 0.0
    rec = tp / max(tp + fn, 1) if (tp + fn) > 0 else 0.0
    f1 = 2 * prec * rec / max(prec + rec, 1e-9) if (prec + rec) > 0 else 0.0

    # Direction accuracy among matched
    if n_matched >= 1:
        dir_acc = float((matches["dir_synth"] == matches["dir_real"]).mean())
    else:
        dir_acc = float("nan")

    # Hold similarity (1 - KS_stat)
    if n_synth >= LOW_N_MATCHED_THRESHOLD and n_real >= LOW_N_MATCHED_THRESHOLD:
        synth_holds = synth["duration_sec"].dropna().values / 3600.0
        real_holds = real_t["duration_sec"].dropna().values / 3600.0
        if len(synth_holds) >= LOW_N_MATCHED_THRESHOLD and len(real_holds) >= LOW_N_MATCHED_THRESHOLD:
            ks_stat = float(stats.ks_2samp(synth_holds, real_holds).statistic)
        else:
            ks_stat = float("nan")
    else:
        ks_stat = float("nan")
    hold_sim = 1.0 - ks_stat if not math.isnan(ks_stat) else float("nan")

    # Count ratio
    count_ratio = (n_synth / n_real) if n_real > 0 else float("nan")

    # PnL correlation among matched
    if n_matched >= LOW_N_MATCHED_THRESHOLD:
        try:
            pnl_corr = float(
                stats.pearsonr(
                    matches["pnl_synth"].astype(float).values,
                    matches["pnl_real"].astype(float).values,
                ).statistic
            )
        except Exception:
            pnl_corr = float("nan")
    else:
        pnl_corr = float("nan")

    # Baseline combined-hit rates
    ab, hm, phm = _baseline_combined_hit_rates(candidates_with_features, real)
    max_base = max(ab, hm, phm)

    # Synthetic combined-hit rate (matched AND direction correct, normalized by n_real)
    if n_matched > 0:
        synth_combined_hits = int(
            (matches["dir_synth"] == matches["dir_real"]).sum()
        )
    else:
        synth_combined_hits = 0
    synth_combined_hit_rate = synth_combined_hits / max(n_real, 1)

    lift_pp = (synth_combined_hit_rate - max_base) * 100.0

    return ComparisonReport(
        system_id=system_id,
        n_real=n_real,
        n_synthetic=n_synth,
        n_matched=n_matched,
        entry_timing_precision=round(prec, 4),
        entry_timing_recall=round(rec, 4),
        entry_timing_f1=round(f1, 4),
        direction_acc_at_matched=round(dir_acc, 4) if not math.isnan(dir_acc) else float("nan"),
        hold_KS_stat=round(ks_stat, 4) if not math.isnan(ks_stat) else float("nan"),
        hold_similarity=round(hold_sim, 4) if not math.isnan(hold_sim) else float("nan"),
        count_ratio=round(count_ratio, 4) if not math.isnan(count_ratio) else float("nan"),
        pnl_correlation=round(pnl_corr, 4) if not math.isnan(pnl_corr) else float("nan"),
        baseline_always_buy_combined_hit_rate=round(ab, 4),
        baseline_hour_majority_combined_hit_rate=round(hm, 4),
        baseline_pair_hour_majority_combined_hit_rate=round(phm, 4),
        max_baseline_combined_hit_rate=round(max_base, 4),
        synthetic_combined_hit_rate=round(synth_combined_hit_rate, 4),
        lift_vs_baseline_pp=round(lift_pp, 2),
    )


# ===========================================================================
# Score formula (specs/decoding_score_formula.md v1.0).
# ===========================================================================


def _nan_to_zero(x: float) -> float:
    """Per spec §4: any NaN term → 0 (no renormalization)."""
    return 0.0 if (x is None or (isinstance(x, float) and math.isnan(x))) else float(x)


def _count_ratio_proximity(r: float) -> float:
    """1.0 if r ∈ [0.5, 2.0]; else 1/(1 + |log2(r)|). NaN/r<=0 → 0."""
    if r is None or math.isnan(r) or r <= 0:
        return 0.0
    if 0.5 <= r <= 2.0:
        return 1.0
    return 1.0 / (1.0 + abs(math.log2(r)))


def compute_score(report: ComparisonReport, family: str) -> dict[str, Any]:
    """Compute fidelity_score 0-1 from comparison report.

    Six-term formula per `specs/decoding_score_formula.md`:
        0.25 × entry_timing_f1
      + 0.15 × baseline_lift_normalized   (clip(lift_pp / 20, 0, 1))
      + 0.20 × direction_acc_at_matched
      + 0.15 × hold_similarity
      + 0.15 × count_ratio_proximity
      + 0.10 × pnl_correlation_pos        (clip(pearson, 0, 1))

    NaN convention: any term NaN → 0 before combining (no renormalization).
    """
    f1 = _nan_to_zero(report.entry_timing_f1)
    lift_norm = max(0.0, min(1.0, report.lift_vs_baseline_pp / SCORE_LIFT_NORMALIZATION_PP))
    dir_acc = _nan_to_zero(report.direction_acc_at_matched)
    hold_sim = _nan_to_zero(report.hold_similarity)
    cr_prox = _count_ratio_proximity(report.count_ratio)
    pnl_pos = max(0.0, _nan_to_zero(report.pnl_correlation))

    score = (
        0.25 * f1
        + 0.15 * lift_norm
        + 0.20 * dir_acc
        + 0.15 * hold_sim
        + 0.15 * cr_prox
        + 0.10 * pnl_pos
    )
    score = max(0.0, min(1.0, score))

    if score >= 0.80:
        band: Banda = "HIGH"
    elif score >= 0.60:
        band = "MEDIUM"
    elif score >= 0.40:
        band = "LOW"
    else:
        band = "NONE"

    return {
        "system_id": report.system_id,
        "family_stage2": family,
        "fidelity_score": round(score, 4),
        "score_band": band,
        "terms": {
            "entry_timing_f1": round(f1, 4),
            "baseline_lift_normalized": round(lift_norm, 4),
            "lift_vs_baseline_pp": report.lift_vs_baseline_pp,
            "direction_acc_at_matched": round(dir_acc, 4),
            "hold_similarity": round(hold_sim, 4),
            "count_ratio_proximity": round(cr_prox, 4),
            "count_ratio": report.count_ratio,
            "pnl_correlation_pos": round(pnl_pos, 4),
            "pnl_correlation_raw": report.pnl_correlation,
        },
        "diagnostics": {
            "n_real": report.n_real,
            "n_synthetic": report.n_synthetic,
            "n_matched": report.n_matched,
            "low_n_flag": report.n_real < LOW_N_TRADES_THRESHOLD,
            "low_confidence_dir": 0 < report.n_matched < LOW_N_MATCHED_THRESHOLD,
        },
    }


# ===========================================================================
# Single-system runner (full pipeline).
# ===========================================================================


def run_one_full(
    system_id: str,
    base_dir: Path,
    loader: OhlcLoader | None = None,
    *,
    bar_freq: str = BAR_FREQ,
) -> dict[str, Any]:
    """End-to-end: load rule → window → features → backtest → compare → score.

    Returns dict with synthetic_trades_df, comparison_report, decoding_score, status.
    Does NOT write to disk — caller (batch driver) handles persistence.
    """
    rule = load_frozen_rule(system_id, base_dir)
    if not rule.entry_hours_utc:
        return {
            "system_id": system_id,
            "status": "skipped_no_hours",
            "rule": {"family": rule.family, "confidence": rule.confidence},
        }

    p_trades = base_dir / "data" / "trades" / system_id / "trades.parquet"
    if not p_trades.exists() and system_id == "1407880":
        p_trades = (
            base_dir / "2026-05-01-happy_market_hours_v231" / "data" / "trades_1407880.parquet"
        )
    if not p_trades.exists():
        return {"system_id": system_id, "status": "no_trades_parquet"}
    trades = pd.read_parquet(p_trades)

    window = build_candidate_window(rule, trades, bar_freq=bar_freq)
    if window.empty:
        return {"system_id": system_id, "status": "empty_window"}
    window = label_real_entries(window, trades, bar_freq=bar_freq)

    if loader is None:
        loader = OhlcLoader(freq=bar_freq)

    feats = extract_features_for_window(
        window, peer_pairs=rule.pairs, loader=loader, bar_freq=bar_freq
    )
    window = window.reset_index(drop=True)
    cw = pd.concat([window, feats], axis=1)

    synth = run_backtest(rule, cw, loader, bar_freq=bar_freq)

    report = compare(system_id, synth, trades, cw)
    score = compute_score(report, rule.family)

    return {
        "system_id": system_id,
        "status": "ok",
        "rule_summary": {
            "family": rule.family,
            "confidence": rule.confidence,
            "executor": rule.executor.name,
            "features_used": rule.executor.features_used,
            "entry_hours": sorted(rule.entry_hours_utc),
            "pairs": rule.pairs,
            "max_holding_hours": rule.max_holding_hours,
            "used_default_holding": rule.used_default_holding,
        },
        "synthetic_trades": synth,
        "comparison_report": report,
        "decoding_score": score,
    }


# ===========================================================================
# Smoke test — replicator_full_addendum.md §5 invariants.
# ===========================================================================


def smoke_invariants(result: dict[str, Any], rule: FrozenRule) -> dict[str, bool]:
    """Run smoke-test invariants per spec §5. Returns {invariant_name: passed}."""
    out: dict[str, bool] = {}
    synth: pd.DataFrame = result.get("synthetic_trades", pd.DataFrame())

    # I1: Schema
    expected_cols = {
        "record", "symbol", "action", "lots", "open_price", "close_price",
        "pips", "profit", "open_dt_utc", "close_dt_utc", "duration_sec",
        "is_trade", "is_deposit", "direction_executor", "exit_truncated",
    }
    out["I1_schema"] = expected_cols.issubset(set(synth.columns)) if not synth.empty else False

    # I2: Sanity counts (count_ratio in [0.5, 5.0])
    report: ComparisonReport = result["comparison_report"]
    if report.n_real > 0 and not math.isnan(report.count_ratio):
        out["I2_count_ratio"] = 0.5 <= report.count_ratio <= 5.0
    else:
        out["I2_count_ratio"] = False

    # I3: Entry hours coverage
    if not synth.empty:
        synth_hours = set(pd.to_datetime(synth["open_dt_utc"]).dt.hour.unique())
        out["I3_entry_hours"] = synth_hours.issubset(rule.entry_hours_utc)
    else:
        out["I3_entry_hours"] = False

    # I4: Direction sanity (if F1>0.3, dir_acc>=0.4)
    if report.entry_timing_f1 > 0.3 and not math.isnan(report.direction_acc_at_matched):
        out["I4_direction_sanity"] = report.direction_acc_at_matched >= 0.4
    else:
        out["I4_direction_sanity"] = True  # not testable

    return out
