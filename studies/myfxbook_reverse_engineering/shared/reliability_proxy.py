"""Stage 3-lite reliability proxy — quick reliability score WITHOUT full OHLC replicator.

The full Stage 3 from the plan requires running the decoded rule on full OHLC
history, applying gates §2.4, etc. This module is the OVERNIGHT-friendly subset:
it combines artifacts already produced by Stage 1 (candidates.json, fingerprint
sanity/eda) and Stage 2 (signal_rule.md family + confidence) into a proxy
reliability score.

Score components (each ∈ [0,1], weighted):

  0.25  direction_predictability  — top candidate match_rate_cv normalized vs 0.5
  0.20  family_clarity            — confidence from signal_rule.md (LLM judgment)
  0.20  timing_concentration      — fraction of trades in top-3 entry hours
  0.10  sanity_pass               — k1_pass binary (martingale/grid filter)
  0.10  age_freshness             — recency of last trade (days since)
  0.10  vendor_quality            — Real > Demo, n_trades coverage
  0.05  pair_coverage             — fraction of trades on Dukascopy-supported pairs

reliability ∈ [0,1]:
  HIGH   ≥ 0.65  → paper-trading candidate (after manual /decode-system with Opus)
  MEDIUM 0.45-0.65 → investigate, possibly re-mine with full sample
  LOW    < 0.45  → folclore / unrecoverable

This is honestly a PROXY. The 5-component reliability formula in the plan
(direction_match + pnl_correlation + gates_passed + blackout_coverage +
cost_robustness) requires full Stage 3 replicator. The proxy lets the user
rank overnight; full Stage 3 happens when the user wakes up.

Citations:
- [advances_fin_ml, p.196-211] — DSR/PBO (proper Stage 3 statistical gates)
- [fooled_by_randomness, Taleb] — track-record bias (justifies vendor + age penalty)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from . import config
from .ohlc_dukascopy import _DUKAS_PAIR_MAP


@dataclass
class ReliabilityProxy:
    system_id: str
    reliability: float
    band: str  # HIGH | MEDIUM | LOW
    components: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    family: str = "UNKNOWN"
    confidence: float = 0.0
    n_trades: int = 0
    n_pairs: int = 0
    last_trade_date: str | None = None
    account_type: str | None = None

    def to_dict(self) -> dict:
        return {
            "system_id": self.system_id,
            "reliability": float(self.reliability),
            "band": self.band,
            "components": {k: float(v) for k, v in self.components.items()},
            "notes": self.notes,
            "family": self.family,
            "confidence": float(self.confidence),
            "n_trades": int(self.n_trades),
            "n_pairs": int(self.n_pairs),
            "last_trade_date": self.last_trade_date,
            "account_type": self.account_type,
        }


def _classify_band(reliability: float) -> str:
    if reliability >= 0.65:
        return "HIGH"
    if reliability >= 0.45:
        return "MEDIUM"
    return "LOW"


def _parse_signal_rule_yaml(path: Path) -> dict:
    """Best-effort YAML parse of signal_rule.md front-matter.

    Without PyYAML, hand-parse the simple keys we need (family, confidence).
    """
    if not path.exists():
        return {}
    text = path.read_text(errors="replace")
    m = re.search(r"^---\n(.*?)\n---", text, re.DOTALL | re.MULTILINE)
    if not m:
        return {}
    block = m.group(1)
    out: dict[str, Any] = {}
    fam = re.search(r"^family:\s*(\S+)", block, re.MULTILINE)
    if fam:
        out["family"] = fam.group(1).strip()
    conf = re.search(r"^confidence:\s*([0-9.]+)", block, re.MULTILINE)
    if conf:
        try:
            out["confidence"] = float(conf.group(1))
        except ValueError:
            pass
    risk_count = len(re.findall(r"^\s*-\s+\".*\"$", block, re.MULTILINE))
    out["risk_flag_count"] = risk_count
    out["raw_yaml"] = block
    return out


def _component_direction_predictability(candidates: list[dict]) -> float:
    """Top non-baseline candidate match_rate_cv normalized vs 0.5 chance.

    Linear scale: 0.5 → 0, 0.75 → 1.0.
    """
    real = [c for c in candidates if c.get("miner") != "baseline"]
    if not real:
        return 0.0
    top = max(real, key=lambda c: float(c.get("match_rate_cv", 0)))
    mr = float(top.get("match_rate_cv", 0.5))
    return max(0.0, min(1.0, (mr - 0.5) / 0.25))


def _component_timing_concentration(entry_hour_counts: dict[int, int]) -> float:
    """Fraction of trades in top-3 entry hours."""
    if not entry_hour_counts:
        return 0.0
    total = sum(entry_hour_counts.values())
    if total == 0:
        return 0.0
    top3 = sum(sorted(entry_hour_counts.values(), reverse=True)[:3])
    return top3 / total


def _component_age_freshness(last_close_utc: pd.Timestamp | None, today: datetime) -> float:
    """Linear decay: 0 days ago = 1.0, 5 years ago = 0.0."""
    if last_close_utc is None:
        return 0.5
    last = pd.Timestamp(last_close_utc)
    if last.tzinfo is None:
        last = last.tz_localize("UTC")
    if today.tzinfo is None:
        today = today.replace(tzinfo=timezone.utc)
    days = (today - last.to_pydatetime()).total_seconds() / 86400.0
    return max(0.0, min(1.0, 1.0 - days / (5 * 365)))


def _component_vendor_quality(account_type: str | None, n_trades: int) -> float:
    """Real account + ≥ 1000 trades = 1.0; Demo or low-volume = lower."""
    base = 0.0
    if account_type and account_type.lower() == "real":
        base += 0.6
    elif account_type and account_type.lower() == "demo":
        base += 0.3
    else:
        base += 0.4
    if n_trades >= 1000:
        base += 0.4
    elif n_trades >= 500:
        base += 0.25
    elif n_trades >= 200:
        base += 0.15
    elif n_trades >= 100:
        base += 0.05
    return min(1.0, base)


def _component_pair_coverage(symbol_counts: dict[str, int]) -> float:
    """Fraction of trade volume on Dukascopy-supported pairs."""
    if not symbol_counts:
        return 0.0
    total = sum(symbol_counts.values())
    supported = sum(n for s, n in symbol_counts.items()
                    if s.replace("/", "").upper() in _DUKAS_PAIR_MAP)
    return supported / max(total, 1)


def compute_reliability_proxy(
    system_id: str,
    *,
    today: datetime | None = None,
) -> ReliabilityProxy:
    """Read all stage1+stage2 artifacts for `system_id` and produce the proxy score.

    Tolerates missing inputs — each missing artifact pushes its component to 0
    and adds a note. Used by the overnight orchestrator.
    """
    today = today or datetime.now(timezone.utc)
    notes: list[str] = []
    components: dict[str, float] = {}

    # Trades parquet
    trades_path = config.trades_parquet_path(system_id)
    if not trades_path.exists():
        return ReliabilityProxy(
            system_id=system_id, reliability=0.0, band="LOW",
            notes=["trades.parquet missing"]
        )
    df = pd.read_parquet(trades_path)
    trades = df[df["is_trade"]].copy() if "is_trade" in df.columns else df.copy()
    n_trades = len(trades)
    symbol_counts = trades["symbol"].value_counts().to_dict() if "symbol" in trades.columns else {}
    last_close = trades["close_dt_utc"].max() if "close_dt_utc" in trades.columns and not trades.empty else None

    # System info
    info_path = config.system_info_json_path(system_id)
    account_type = None
    system_name = system_id
    if info_path.exists():
        try:
            info = json.loads(info_path.read_text())
            account_type = info.get("account", {}).get("account_type")
            system_name = info.get("name", system_id)
        except Exception as e:
            notes.append(f"system_info.json parse error: {e}")

    # Candidates
    cand_path = config.system_report_dir(system_id) / "decoder" / "candidates.json"
    candidates: list[dict] = []
    if cand_path.exists():
        try:
            candidates = json.loads(cand_path.read_text())
        except Exception as e:
            notes.append(f"candidates.json parse error: {e}")
    else:
        notes.append("candidates.json missing — Stage 1 incomplete")

    # Signal rule (stage 2)
    rule_path = config.system_report_dir(system_id) / "signal_rule.md"
    rule_meta = _parse_signal_rule_yaml(rule_path)
    family = rule_meta.get("family", "UNKNOWN")
    confidence = float(rule_meta.get("confidence", 0.0))
    if not rule_meta:
        notes.append("signal_rule.md missing — Stage 2 incomplete")

    # Compute components
    components["direction_predictability"] = _component_direction_predictability(candidates)
    components["family_clarity"] = confidence  # already [0,1]
    if "open_dt_utc" in trades.columns and not trades.empty:
        hour_counts = trades["open_dt_utc"].dt.hour.value_counts().to_dict()
        components["timing_concentration"] = _component_timing_concentration(hour_counts)
    else:
        components["timing_concentration"] = 0.0
    components["sanity_pass"] = 1.0  # default: assume pass; overridden below if sanity ran
    components["age_freshness"] = _component_age_freshness(last_close, today)
    components["vendor_quality"] = _component_vendor_quality(account_type, n_trades)
    components["pair_coverage"] = _component_pair_coverage(symbol_counts)

    # Pull sanity_pass from existing fingerprint.md if present (cheap regex).
    fp_path = config.system_report_dir(system_id) / "decoder" / "fingerprint.md"
    if fp_path.exists():
        fp_text = fp_path.read_text(errors="replace")
        if "FAIL (martingale-like" in fp_text:
            components["sanity_pass"] = 0.0
            notes.append("sanity FAIL — martingale signature detected")
        elif "PASS (no martingale)" in fp_text:
            components["sanity_pass"] = 1.0
        else:
            components["sanity_pass"] = 0.5
            notes.append("sanity status unclear")

    weights = {
        "direction_predictability": 0.25,
        "family_clarity": 0.20,
        "timing_concentration": 0.20,
        "sanity_pass": 0.10,
        "age_freshness": 0.10,
        "vendor_quality": 0.10,
        "pair_coverage": 0.05,
    }
    reliability = sum(components[k] * weights[k] for k in weights)
    band = _classify_band(reliability)

    # FOLCLORE override: if sanity FAIL → forced LOW
    if components.get("sanity_pass", 1.0) <= 0.0:
        band = "LOW"
        reliability = min(reliability, 0.3)
        notes.append("forced LOW: martingale/grid signature")

    # If family is UNCATEGORIZED with low confidence, demote MEDIUM → LOW border.
    # 5R-1-hardening Wave B item 2: use Family enum from decoder_taxonomy as
    # single source of truth (instead of string comparison).
    from studies.myfxbook_reverse_engineering.shared.decoder_taxonomy import Family
    if family.upper() == Family.UNCATEGORIZED.value and reliability < 0.55:
        band = "LOW"
        notes.append("UNCATEGORIZED family demotes to LOW band")

    return ReliabilityProxy(
        system_id=str(system_id),
        reliability=reliability,
        band=band,
        components=components,
        notes=notes,
        family=family,
        confidence=confidence,
        n_trades=n_trades,
        n_pairs=len(symbol_counts),
        last_trade_date=str(last_close) if last_close is not None else None,
        account_type=account_type,
    )
