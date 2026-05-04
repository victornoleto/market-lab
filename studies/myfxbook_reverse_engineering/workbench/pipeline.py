"""Single-system MyFxBook reverse-engineering pipeline.

The workbench accepts one MyFxBook accountOid/system_id and coordinates the
existing study modules:

1. optional download of system info + trade history;
2. parse / load trade history;
3. Stage 1 feature extraction + candidate rule mining;
4. deterministic candidate-rule backtest;
5. two scores: replication fidelity and decoded-strategy efficacy.

This is research-only. It does not alter `frozen_rules/`, does not declare a
tradeable strategy, and does not place paper/live orders.

Citations:
- Candidate mining and no-lookahead features: [advances_fin_ml, ch.5, ch.7].
- Baseline/lift controls against data-mining bias: [evidence_based_ta, p.247-260].
- Costs can dominate short-horizon systems: [systematic_trading, p.182-197].
- DSR/bootstrap-style inference: [advances_fin_ml, p.196-211].
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.myfxbook_reverse_engineering.shared import config, parser  # noqa: E402
from studies.myfxbook_reverse_engineering.shared.download_data import (  # noqa: E402
    WARMUP_URL,
    _csrf,
    _load_playwright,
    scrape_one_system,
)
from studies.myfxbook_reverse_engineering.shared.ohlc_dukascopy import OhlcLoader  # noqa: E402
from studies.myfxbook_reverse_engineering.shared.replicator import (  # noqa: E402
    BAR_FREQ,
    DEFAULT_MAX_HOLDING_HOURS,
    FrozenRule,
    _build_executor,
    build_candidate_window,
    compare,
    compute_score,
    extract_features_for_window,
    run_backtest,
    smoke_invariants,
)
from studies.myfxbook_reverse_engineering.shared.run_decoder_stage1 import (  # noqa: E402
    run_stage1,
)


TRADING_DAYS_PER_YEAR = 252
BOOTSTRAP_N = 5000
BOOTSTRAP_CI_Q = 0.001
BOOTSTRAP_SEED = 20260503


@dataclass(frozen=True)
class EfficacyScore:
    """Economic score for the decoded synthetic strategy, not the vendor track record."""

    score: float
    band: str
    n_trades: int
    total_net_pips: float
    avg_net_pips: float
    daily_sharpe: float
    full_bootstrap_sharpe_low_999: float | None
    oos_sharpe: float
    oos_bootstrap_sharpe_low_999: float | None
    profit_factor: float
    max_drawdown_pips: float
    wf_positive: int
    wf_total: int
    terms: dict[str, float]
    notes: list[str]


def workbench_dir(system_id: str) -> Path:
    return config.system_report_dir(system_id) / "workbench"


def _load_candidates(system_id: str) -> list[dict[str, Any]]:
    path = config.system_report_dir(system_id) / "decoder" / "candidates.json"
    if not path.exists():
        raise FileNotFoundError(f"candidates.json missing at {path}; run Stage 1 first")
    return json.loads(path.read_text())


def _load_trades(system_id: str) -> pd.DataFrame:
    path = config.trades_parquet_path(system_id)
    if not path.exists():
        raise FileNotFoundError(f"trades parquet missing at {path}; run with --download or provide cached data")
    return pd.read_parquet(path)


def _top_executable_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Pick the highest-ranked non-baseline candidate parseable by replicator."""
    for cand in candidates:
        if cand.get("miner") == "baseline":
            continue
        try:
            _build_executor("", [cand])
        except Exception:
            continue
        return cand
    raise ValueError("No parseable non-baseline candidate rule found")


def _entry_hours_from_trades(trades: pd.DataFrame, max_hours: int = 3) -> set[int]:
    t = trades[trades["is_trade"] == True].copy()
    if t.empty or "open_dt_utc" not in t:
        return set()
    counts = pd.to_datetime(t["open_dt_utc"], utc=True).dt.hour.value_counts()
    return {int(h) for h in counts.head(max_hours).index.tolist()}


def _pairs_from_trades(trades: pd.DataFrame) -> list[str]:
    t = trades[trades["is_trade"] == True].copy()
    return sorted(str(s).replace("/", "").upper() for s in t["symbol"].dropna().unique().tolist())


def _max_holding_from_trades(trades: pd.DataFrame) -> tuple[float, bool]:
    t = trades[trades["is_trade"] == True].copy()
    if t.empty or "duration_sec" not in t:
        return DEFAULT_MAX_HOLDING_HOURS, True
    hours = t["duration_sec"].dropna().astype(float) / 3600.0
    if hours.empty:
        return DEFAULT_MAX_HOLDING_HOURS, True
    # p80 avoids one-off zombie positions while preserving the typical EA exit horizon.
    return max(1.0, float(hours.quantile(0.80))), False


def build_candidate_rule(system_id: str, trades: pd.DataFrame, candidates: list[dict[str, Any]]) -> tuple[FrozenRule, dict[str, Any]]:
    cand = _top_executable_candidate(candidates)
    executor = _build_executor("", [cand])
    max_hold, used_default_hold = _max_holding_from_trades(trades)
    rule = FrozenRule(
        system_id=system_id,
        family=f"AUTO_{cand.get('miner', 'candidate').upper()}",
        confidence=float(cand.get("match_rate_cv", 0.0)),
        pairs=_pairs_from_trades(trades),
        entry_hours_utc=_entry_hours_from_trades(trades),
        max_holding_hours=max_hold,
        used_default_holding=used_default_hold,
        executor=executor,
        raw_rule_text=str(cand.get("rule_text", "")),
        reason_code="auto_candidate_rule_not_frozen",
        candidate_new_family=None,
    )
    return rule, cand


def _cost_for_symbol(symbol: str) -> float:
    # Reuse Pepperstone FX model when available; fallback is the max known FX cost.
    cm = config.pepperstone_razor_2025()
    return cm.cost_for(str(symbol).replace("/", "").upper())


def _daily_net_pips(synth: pd.DataFrame) -> pd.Series:
    if synth.empty:
        return pd.Series(dtype=float)
    trades = synth.copy()
    trades["cost_pips"] = trades["symbol"].map(_cost_for_symbol)
    trades["net_pips"] = trades["pips"].astype(float) - trades["cost_pips"].astype(float)
    trades["close_date"] = pd.to_datetime(trades["close_dt_utc"], utc=True).dt.date
    return trades.groupby("close_date")["net_pips"].sum().sort_index()


def _annualized_sharpe(daily: pd.Series) -> float:
    daily = daily.dropna().astype(float)
    if len(daily) < 2 or float(daily.std()) <= 0:
        return 0.0
    return float(daily.mean() / daily.std() * math.sqrt(TRADING_DAYS_PER_YEAR))


def _bootstrap_sharpe_low(daily: pd.Series, seed: int) -> float | None:
    arr = daily.dropna().astype(float).to_numpy()
    if len(arr) < 30:
        return None
    rng = np.random.default_rng(seed)
    sharpes = np.empty(BOOTSTRAP_N)
    for i in range(BOOTSTRAP_N):
        sample = rng.choice(arr, size=len(arr), replace=True)
        std = float(sample.std())
        sharpes[i] = float(sample.mean() / std * math.sqrt(TRADING_DAYS_PER_YEAR)) if std > 0 else 0.0
    return float(np.quantile(sharpes, BOOTSTRAP_CI_Q))


def _profit_factor(net_pips: pd.Series) -> float:
    gains = float(net_pips[net_pips > 0].sum())
    losses = float(-net_pips[net_pips < 0].sum())
    if losses == 0:
        return float("inf") if gains > 0 else 0.0
    return gains / losses


def _max_drawdown_pips(net_pips: pd.Series) -> float:
    if net_pips.empty:
        return 0.0
    equity = net_pips.cumsum()
    return float((equity.cummax() - equity).max())


def compute_efficacy_score(synth: pd.DataFrame) -> EfficacyScore:
    notes: list[str] = []
    if synth.empty:
        return EfficacyScore(
            score=0.0,
            band="NONE",
            n_trades=0,
            total_net_pips=0.0,
            avg_net_pips=0.0,
            daily_sharpe=0.0,
            full_bootstrap_sharpe_low_999=None,
            oos_sharpe=0.0,
            oos_bootstrap_sharpe_low_999=None,
            profit_factor=0.0,
            max_drawdown_pips=0.0,
            wf_positive=0,
            wf_total=0,
            terms={},
            notes=["synthetic strategy generated zero trades"],
        )

    trades = synth.copy()
    trades["cost_pips"] = trades["symbol"].map(_cost_for_symbol)
    trades["net_pips"] = trades["pips"].astype(float) - trades["cost_pips"].astype(float)
    daily = _daily_net_pips(trades)
    sharpe = _annualized_sharpe(daily)
    full_low = _bootstrap_sharpe_low(daily, BOOTSTRAP_SEED)

    daily_ts = daily.copy()
    daily_ts.index = pd.to_datetime(daily_ts.index)
    oos_cut = int(len(daily_ts) * 0.8)
    oos = daily_ts.iloc[oos_cut:] if len(daily_ts) else daily_ts
    oos_sharpe = _annualized_sharpe(oos)
    oos_low = _bootstrap_sharpe_low(oos, BOOTSTRAP_SEED + 1)

    wf_sharpes: list[float] = []
    for idxs in np.array_split(daily_ts.index, 8):
        if len(idxs) < 5:
            continue
        wf_sharpes.append(_annualized_sharpe(daily_ts.loc[idxs.min():idxs.max()]))
    wf_positive = int(sum(1 for s in wf_sharpes if s > 0))

    net = trades["net_pips"]
    total = float(net.sum())
    avg = float(net.mean())
    pf = _profit_factor(net)
    dd = _max_drawdown_pips(net)

    # 0..1 score, deliberately conservative. It is a triage score, not a mandate PASS.
    terms = {
        "sharpe_term": max(0.0, min(1.0, sharpe / 2.0)),
        "full_bootstrap_term": 1.0 if full_low is not None and full_low > 0 else 0.0,
        "oos_term": max(0.0, min(1.0, oos_sharpe / 1.5)),
        "oos_bootstrap_term": 1.0 if oos_low is not None and oos_low > 0 else 0.0,
        "profit_factor_term": max(0.0, min(1.0, (pf - 1.0) / 1.0)) if math.isfinite(pf) else 1.0,
        "wf_term": wf_positive / max(len(wf_sharpes), 1),
    }
    score = (
        0.25 * terms["sharpe_term"]
        + 0.20 * terms["full_bootstrap_term"]
        + 0.20 * terms["oos_term"]
        + 0.15 * terms["oos_bootstrap_term"]
        + 0.10 * terms["profit_factor_term"]
        + 0.10 * terms["wf_term"]
    )
    if full_low is None:
        notes.append("full bootstrap skipped: fewer than 30 active days")
    if oos_low is None:
        notes.append("OOS bootstrap skipped: fewer than 30 OOS active days")
    if score >= 0.80:
        band = "HIGH"
    elif score >= 0.60:
        band = "MEDIUM"
    elif score >= 0.40:
        band = "LOW"
    else:
        band = "NONE"
    return EfficacyScore(
        score=round(float(score), 4),
        band=band,
        n_trades=int(len(trades)),
        total_net_pips=round(total, 4),
        avg_net_pips=round(avg, 4),
        daily_sharpe=round(float(sharpe), 4),
        full_bootstrap_sharpe_low_999=None if full_low is None else round(float(full_low), 4),
        oos_sharpe=round(float(oos_sharpe), 4),
        oos_bootstrap_sharpe_low_999=None if oos_low is None else round(float(oos_low), 4),
        profit_factor=round(float(pf), 4) if math.isfinite(pf) else float("inf"),
        max_drawdown_pips=round(float(dd), 4),
        wf_positive=wf_positive,
        wf_total=len(wf_sharpes),
        terms={k: round(float(v), 4) for k, v in terms.items()},
        notes=notes,
    )


def maybe_download_system(
    system_id: str,
    *,
    url: str | None,
    name: str | None,
    force: bool,
    headed: bool,
    timeout_ms: int,
    max_history_pages: int,
    rate_limit_ms: int,
) -> dict[str, Any]:
    row = pd.Series({
        "system_id": int(system_id),
        "name": name or f"MyFxBook system {system_id}",
        "url": url or f"https://www.myfxbook.com/members/{config.VENDOR_NAME}/system/{system_id}",
    })
    sync_playwright = _load_playwright()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not headed)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
            locale="en-US",
        )
        page = ctx.new_page()
        page.goto(WARMUP_URL, wait_until="domcontentloaded", timeout=timeout_ms)
        csrf = _csrf(ctx)
        result = scrape_one_system(
            page,
            row,
            csrf,
            max_history_pages=max_history_pages,
            timeout_ms=timeout_ms,
            rate_limit_ms=rate_limit_ms,
            force=force,
        )
        browser.close()
    return result


def parse_cached_raw_if_needed(system_id: str) -> None:
    parquet = config.trades_parquet_path(system_id)
    if parquet.exists():
        return
    raw_dir = config.trades_raw_dir(system_id)
    html_files = sorted(raw_dir.glob("history_page_*.html"))
    if html_files:
        parser.parse_history_html_files_to_parquet(html_files, parquet)
        return
    batch_files = sorted(raw_dir.glob("batch_*.json"))
    if batch_files:
        parser.parse_batches_to_parquet(raw_dir, parquet)
        return
    raise FileNotFoundError(f"No cached raw history found under {raw_dir}")


def run_candidate_backtest(system_id: str, *, freq: str = BAR_FREQ) -> dict[str, Any]:
    trades = _load_trades(system_id)
    candidates = _load_candidates(system_id)
    rule, selected_candidate = build_candidate_rule(system_id, trades, candidates)
    if not rule.entry_hours_utc:
        raise ValueError("candidate rule has no entry hours; cannot build candidate window")
    window = build_candidate_window(rule, trades, bar_freq=freq)
    if window.empty:
        raise ValueError("candidate window is empty")
    window = label_real_entries_safe(window, trades, freq=freq)
    loader = OhlcLoader(freq=freq)
    feats = extract_features_for_window(window, peer_pairs=rule.pairs, loader=loader, bar_freq=freq)
    cw = pd.concat([window.reset_index(drop=True), feats.reset_index(drop=True)], axis=1)
    synth = run_backtest(rule, cw, loader, bar_freq=freq)
    report = compare(system_id, synth, trades, cw)
    fidelity_score = compute_score(report, rule.family)
    efficacy_score = compute_efficacy_score(synth)
    invariants = smoke_invariants({"synthetic_trades": synth, "comparison_report": report}, rule)
    return {
        "rule": rule,
        "selected_candidate": selected_candidate,
        "candidate_window": cw,
        "synthetic_trades": synth,
        "comparison_report": report,
        "fidelity_score": fidelity_score,
        "efficacy_score": efficacy_score,
        "smoke_invariants": invariants,
    }


def label_real_entries_safe(window: pd.DataFrame, trades: pd.DataFrame, *, freq: str) -> pd.DataFrame:
    # Import lazily to keep public import block small; this is a stable function in replicator.py.
    from studies.myfxbook_reverse_engineering.shared.replicator import label_real_entries

    return label_real_entries(window, trades, bar_freq=freq)


def _jsonable(obj: Any) -> Any:
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    if isinstance(obj, float) and math.isnan(obj):
        return None
    return str(obj)


def _sanitize_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _sanitize_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_json(v) for v in obj]
    if isinstance(obj, tuple):
        return [_sanitize_json(v) for v in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj


def write_outputs(system_id: str, result: dict[str, Any], *, freq: str, stage1_summary: dict[str, Any] | None, download_summary: dict[str, Any] | None) -> Path:
    out_dir = workbench_dir(system_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    synth: pd.DataFrame = result["synthetic_trades"]
    cw: pd.DataFrame = result["candidate_window"]
    if not synth.empty:
        synth.to_parquet(out_dir / "synthetic_trades.parquet")
    cw.to_parquet(out_dir / "candidate_window.parquet")

    report = result["comparison_report"]
    rule: FrozenRule = result["rule"]
    summary = {
        "system_id": system_id,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "research_only": True,
        "paper_live_allowed": False,
        "freq": freq,
        "download_summary": download_summary,
        "stage1_summary": stage1_summary,
        "selected_candidate": result["selected_candidate"],
        "auto_rule_summary": {
            "family": rule.family,
            "confidence": rule.confidence,
            "executor": rule.executor.name,
            "features_used": rule.executor.features_used,
            "entry_hours_utc": sorted(rule.entry_hours_utc),
            "pairs": rule.pairs,
            "max_holding_hours": rule.max_holding_hours,
            "used_default_holding": rule.used_default_holding,
            "frozen_rules_modified": False,
        },
        "fidelity_score": result["fidelity_score"],
        "efficacy_score": asdict(result["efficacy_score"]),
        "comparison_metrics": asdict(report),
        "smoke_invariants": result["smoke_invariants"],
        "artifacts": [
            "pipeline_summary.json",
            "pipeline_report.md",
            "candidate_window.parquet",
            "synthetic_trades.parquet" if not synth.empty else "synthetic_trades.parquet (not written: empty)",
        ],
        "caveats": [
            "auto_rule is an ephemeral candidate derived from Stage 1; it is not promoted to frozen_rules/.",
            "fidelity_score measures replication of public MyFxBook entries from OHLC-derived rules, not economic edge.",
            "efficacy_score measures the decoded synthetic stream after simple cost overlay; it is not a mandate PASS.",
        ],
    }
    (out_dir / "pipeline_summary.json").write_text(
        json.dumps(_sanitize_json(summary), indent=2, default=_jsonable, allow_nan=False)
    )
    write_markdown_report(system_id, summary, out_dir / "pipeline_report.md")
    return out_dir


def write_markdown_report(system_id: str, summary: dict[str, Any], path: Path) -> None:
    fs = summary["fidelity_score"]
    es = summary["efficacy_score"]
    cm = summary["comparison_metrics"]
    rule = summary["auto_rule_summary"]
    cand = summary["selected_candidate"]
    lines = [
        f"# MyFxBook workbench — system `{system_id}`",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "Research-only. No paper/live, no `frozen_rules/` modification, no strategy decision.",
        "",
        "## Selected Pattern",
        "",
        f"- Miner: `{cand.get('miner')}`",
        f"- Candidate match_rate_cv: `{cand.get('match_rate_cv')}`",
        f"- Candidate coverage: `{cand.get('coverage')}`",
        f"- Rule text: `{str(cand.get('rule_text', '')).splitlines()[0][:180]}`",
        f"- Executor: `{rule['executor']}`",
        f"- Features used: `{rule['features_used']}`",
        f"- Entry hours UTC: `{rule['entry_hours_utc']}`",
        f"- Pairs: `{rule['pairs']}`",
        f"- Max holding hours: `{rule['max_holding_hours']:.2f}`",
        "",
        "## Score A — Backtest Fidelity",
        "",
        f"- Fidelity score: **{fs['fidelity_score']:.4f}** (`{fs['score_band']}`)",
        f"- n_real: `{cm['n_real']}`",
        f"- n_synthetic: `{cm['n_synthetic']}`",
        f"- n_matched within ±5min: `{cm['n_matched']}`",
        f"- entry_timing_f1: `{cm['entry_timing_f1']}`",
        f"- direction_acc_at_matched: `{cm['direction_acc_at_matched']}`",
        f"- count_ratio: `{cm['count_ratio']}`",
        f"- lift_vs_baseline_pp: `{cm['lift_vs_baseline_pp']}`",
        "",
        "## Score B — Decoded Strategy Efficacy",
        "",
        f"- Efficacy score: **{es['score']:.4f}** (`{es['band']}`)",
        f"- synthetic trades: `{es['n_trades']}`",
        f"- total net pips: `{es['total_net_pips']}`",
        f"- avg net pips/trade: `{es['avg_net_pips']}`",
        f"- daily Sharpe: `{es['daily_sharpe']}`",
        f"- full bootstrap 99.9% low: `{es['full_bootstrap_sharpe_low_999']}`",
        f"- OOS Sharpe: `{es['oos_sharpe']}`",
        f"- OOS bootstrap 99.9% low: `{es['oos_bootstrap_sharpe_low_999']}`",
        f"- profit factor: `{es['profit_factor']}`",
        f"- WF positive: `{es['wf_positive']}/{es['wf_total']}`",
        f"- max drawdown pips: `{es['max_drawdown_pips']}`",
        "",
        "## Caveats",
        "",
    ]
    for caveat in summary["caveats"]:
        lines.append(f"- {caveat}")
    lines.extend([
        "",
        "Method citations: candidate mining/no-lookahead `[advances_fin_ml, ch.5, ch.7]`; baseline controls `[evidence_based_ta, p.247-260]`; cost overlay `[systematic_trading, p.182-197]`; bootstrap/DSR inference `[advances_fin_ml, p.196-211]`.",
        "",
    ])
    path.write_text("\n".join(lines))


def _print_terminal_summary(summary_path: Path) -> None:
    if not summary_path.exists():
        return
    data = json.loads(summary_path.read_text())
    print("\n=== MyFxBook Workbench Summary ===")
    print(f"system_id: {data.get('system_id')}")
    if data.get("status"):
        print(f"status: {data.get('status')}")
        print(f"message: {data.get('message')}")
        return

    cand = data.get("selected_candidate") or {}
    rule = data.get("auto_rule_summary") or {}
    fidelity = data.get("fidelity_score") or {}
    efficacy = data.get("efficacy_score") or {}
    comp = data.get("comparison_metrics") or {}

    print("\nDecoded pattern:")
    print(f"  miner: {cand.get('miner')}")
    print(f"  candidate_match_rate_cv: {cand.get('match_rate_cv')}")
    first_rule_line = str(cand.get("rule_text", "")).splitlines()[0] if cand.get("rule_text") else ""
    print(f"  rule: {first_rule_line[:220]}")
    print(f"  executor: {rule.get('executor')}")
    print(f"  features_used: {rule.get('features_used')}")
    print(f"  entry_hours_utc: {rule.get('entry_hours_utc')}")
    print(f"  pairs: {rule.get('pairs')}")
    print(f"  max_holding_hours: {rule.get('max_holding_hours')}")

    print("\nScore A - fidelity to MyFxBook system:")
    print(f"  fidelity_score: {fidelity.get('fidelity_score')} ({fidelity.get('score_band')})")
    print(f"  n_real: {comp.get('n_real')}")
    print(f"  n_synthetic: {comp.get('n_synthetic')}")
    print(f"  n_matched_+-5min: {comp.get('n_matched')}")
    print(f"  entry_timing_f1: {comp.get('entry_timing_f1')}")
    print(f"  direction_acc_at_matched: {comp.get('direction_acc_at_matched')}")
    print(f"  count_ratio: {comp.get('count_ratio')}")
    print(f"  lift_vs_baseline_pp: {comp.get('lift_vs_baseline_pp')}")

    print("\nScore B - decoded strategy efficacy:")
    print(f"  efficacy_score: {efficacy.get('score')} ({efficacy.get('band')})")
    print(f"  synthetic_trades: {efficacy.get('n_trades')}")
    print(f"  total_net_pips: {efficacy.get('total_net_pips')}")
    print(f"  avg_net_pips: {efficacy.get('avg_net_pips')}")
    print(f"  daily_sharpe: {efficacy.get('daily_sharpe')}")
    print(f"  full_bootstrap_999_low: {efficacy.get('full_bootstrap_sharpe_low_999')}")
    print(f"  oos_sharpe: {efficacy.get('oos_sharpe')}")
    print(f"  oos_bootstrap_999_low: {efficacy.get('oos_bootstrap_sharpe_low_999')}")
    print(f"  profit_factor: {efficacy.get('profit_factor')}")
    print(f"  wf_positive: {efficacy.get('wf_positive')}/{efficacy.get('wf_total')}")
    print(f"  max_drawdown_pips: {efficacy.get('max_drawdown_pips')}")


def run_pipeline(args: argparse.Namespace) -> Path:
    system_id = str(args.account_oid)
    download_summary = None
    if args.download:
        download_summary = maybe_download_system(
            system_id,
            url=args.url,
            name=args.name,
            force=args.force_download,
            headed=args.headed,
            timeout_ms=args.timeout_ms,
            max_history_pages=args.max_history_pages,
            rate_limit_ms=args.rate_limit_ms,
        )
    parse_cached_raw_if_needed(system_id)

    trades = _load_trades(system_id)
    n_trades = int(trades["is_trade"].sum()) if "is_trade" in trades.columns else 0
    if n_trades == 0:
        out_dir = workbench_dir(system_id)
        out_dir.mkdir(parents=True, exist_ok=True)
        summary = {
            "system_id": system_id,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "NO_TRADES_PARSED",
            "research_only": True,
            "paper_live_allowed": False,
            "download_summary": download_summary,
            "rows": int(len(trades)),
            "trades": 0,
            "non_trades": int(len(trades)),
            "message": "Trade history was downloaded/parsed but no Buy/Sell rows were detected; Stage 1/backtest skipped.",
        }
        (out_dir / "pipeline_summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False))
        (out_dir / "pipeline_report.md").write_text(
            f"# MyFxBook workbench — system `{system_id}`\n\n"
            "Status: `NO_TRADES_PARSED`\n\n"
            "Trade history was downloaded/parsed, but no Buy/Sell rows were detected. "
            "Stage 1 and synthetic backtest were skipped.\n"
        )
        return out_dir

    stage1_summary = None
    if args.force_stage1 or not (config.system_report_dir(system_id) / "decoder" / "candidates.json").exists():
        stage1_summary = run_stage1(system_id, sample=args.sample)

    result = run_candidate_backtest(system_id, freq=args.freq)
    return write_outputs(system_id, result, freq=args.freq, stage1_summary=stage1_summary, download_summary=download_summary)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run MyFxBook single-system reverse-engineering workbench")
    ap.add_argument("--account-oid", required=True, help="MyFxBook accountOid/system id")
    ap.add_argument("--download", action="store_true", help="Download system info + trade history via Playwright before analysis")
    ap.add_argument("--url", default=None, help="Full MyFxBook system URL. Recommended when using --download for non-catalog systems.")
    ap.add_argument("--name", default=None, help="Optional human-readable system name for manifests")
    ap.add_argument("--force-download", action="store_true", help="Re-download even when cached parquet/info exists")
    ap.add_argument("--force-stage1", action="store_true", help="Re-run Stage 1 candidate mining even if candidates.json exists")
    ap.add_argument("--sample", type=int, default=None, help="Only use most recent N trades for Stage 1 mining")
    ap.add_argument("--freq", choices=("M1", "M5"), default="M5", help="Base OHLC/candidate frequency for synthetic backtest")
    ap.add_argument("--headed", action="store_true", help="Show browser during Playwright download")
    ap.add_argument("--timeout-ms", type=int, default=60_000)
    ap.add_argument("--max-history-pages", type=int, default=200)
    ap.add_argument("--rate-limit-ms", type=int, default=1500)
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    t0 = time.time()
    out_dir = run_pipeline(args)
    _print_terminal_summary(out_dir / "pipeline_summary.json")
    print(f"Workbench complete in {time.time() - t0:.1f}s")
    print(f"Outputs: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
