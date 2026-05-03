"""Overnight validation loop — Stage 1 + Stage 2 (LLM via claude CLI) + Stage 3-lite per system.

Iterates every downloaded system in `data/trades/<id>/`, runs the full decoder
pipeline, computes the reliability proxy, persists per-system reports, and
finally produces an aggregate `ranking/OVERNIGHT_VALIDATION_REPORT.md`.

Stage 2 is invoked via:
  claude --dangerously-skip-permissions --model sonnet -p "/decode-system <id>"
Sonnet 4.6 is sufficient for the structured family-naming task; user can re-run
top-N candidates with Opus when awake.

Per-system output:
  systems/<id>/decoder/{features.parquet, candidates.json, fingerprint.md}  (Stage 1)
  systems/<id>/signal_rule.md                                                (Stage 2)
  systems/<id>/validation_report.md                                          (this script)
  systems/<id>/reliability_score.json                                        (this script)

Cross-system output:
  ranking/OVERNIGHT_VALIDATION_REPORT.md  — written incrementally so partial
                                            results are usable if loop crashes.

Resilient defaults:
  - Skip systems with < MIN_TRADES (= 100) trades
  - Skip systems where < MIN_PAIR_COVERAGE (= 0.5) of trades are on
    Dukascopy-supported pairs
  - Resume: skip systems where validation_report.md already exists (unless --force)
  - Per-system try/except — single failure does not crash the loop
  - Stage 1 and Stage 2 each have a SUBPROCESS_TIMEOUT_SEC budget

Usage:
    nohup uv run python -m studies.myfxbook_reverse_engineering.shared.run_overnight_validation \
        > /tmp/overnight_validation.out 2>&1 &
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.myfxbook_reverse_engineering.shared import config  # noqa: E402
from studies.myfxbook_reverse_engineering.shared.ohlc_dukascopy import _DUKAS_PAIR_MAP  # noqa: E402
from studies.myfxbook_reverse_engineering.shared.reliability_proxy import (  # noqa: E402
    ReliabilityProxy, compute_reliability_proxy,
)

LOG_PATH = REPO_ROOT / "logs" / "myfxbook_reverse_engineering.log"
RANKING_DIR = REPO_ROOT / "studies" / "myfxbook_reverse_engineering" / "ranking"
AGGREGATE_REPORT = RANKING_DIR / "OVERNIGHT_VALIDATION_REPORT.md"
AGGREGATE_JSON = RANKING_DIR / "overnight_results.json"

MIN_TRADES = 100
MIN_PAIR_COVERAGE = 0.5
STAGE1_TIMEOUT_SEC = 60 * 60       # 1h max per system Stage 1 (Dukascopy fetch + features + mining)
STAGE2_TIMEOUT_SEC = 10 * 60       # 10min max per Stage 2 LLM call


def log(msg: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().isoformat(timespec='seconds')}] [overnight] {msg}"
    print(line, flush=True)
    with LOG_PATH.open("a") as f:
        f.write(line + "\n")


def list_candidate_systems() -> list[str]:
    """Return system_ids that have a trades.parquet on disk, sorted."""
    base = REPO_ROOT / "studies" / "myfxbook_reverse_engineering" / "data" / "trades"
    out: list[str] = []
    for d in sorted(base.iterdir()):
        if d.is_dir() and (d / "trades.parquet").exists():
            out.append(d.name)
    return out


def precheck_system(system_id: str) -> tuple[bool, str]:
    """Return (eligible, reason). Skip systems below thresholds."""
    parquet = config.trades_parquet_path(system_id)
    df = pd.read_parquet(parquet)
    if "is_trade" not in df.columns:
        return False, "trades.parquet has no is_trade column"
    trades = df[df["is_trade"]]
    if len(trades) < MIN_TRADES:
        return False, f"only {len(trades)} trades (< MIN_TRADES={MIN_TRADES})"
    syms = trades["symbol"].astype(str).str.replace("/", "").str.upper()
    supported = syms.isin(set(_DUKAS_PAIR_MAP.keys()))
    cov = float(supported.mean())
    if cov < MIN_PAIR_COVERAGE:
        bad = sorted(syms[~supported].unique().tolist())[:5]
        return False, f"only {cov:.0%} pair coverage; unsupported (top): {bad}"
    return True, f"{len(trades)} trades, pair coverage {cov:.0%}"


def run_stage1(system_id: str) -> tuple[bool, str]:
    """Subprocess: run_decoder_stage1 for system. Full sample (no --sample)."""
    cmd = [
        "uv", "run", "python", "-m",
        "studies.myfxbook_reverse_engineering.shared.run_decoder_stage1",
        "--system-id", system_id,
    ]
    try:
        r = subprocess.run(
            cmd, cwd=REPO_ROOT, timeout=STAGE1_TIMEOUT_SEC,
            capture_output=True, text=True, check=False,
        )
    except subprocess.TimeoutExpired:
        return False, f"Stage 1 timeout after {STAGE1_TIMEOUT_SEC}s"
    except Exception as e:
        return False, f"Stage 1 subprocess error: {type(e).__name__}: {e}"
    tail = (r.stdout + "\n" + r.stderr)[-1500:]
    if r.returncode != 0:
        return False, f"Stage 1 returncode={r.returncode}; tail:\n{tail}"
    fp = config.system_report_dir(system_id) / "decoder" / "fingerprint.md"
    if not fp.exists():
        return False, f"Stage 1 finished rc=0 but fingerprint.md missing"
    return True, "Stage 1 OK"


def run_stage2(system_id: str) -> tuple[bool, str, dict]:
    """Subprocess: claude CLI executes /decode-system <id>.

    Auto-skip auth/permission prompts via --dangerously-skip-permissions. Uses
    Sonnet for cost. With `--output-format json` we capture usage/cost.

    Returns (ok, msg, usage_dict). usage_dict carries input_tokens, output_tokens,
    cost_usd, duration_api_ms — empty dict if parse fails.
    """
    cmd = [
        "claude",
        "--dangerously-skip-permissions",
        "--model", "sonnet",
        "--output-format", "json",
        "-p", f"/decode-system {system_id}",
    ]
    try:
        r = subprocess.run(
            cmd, cwd=REPO_ROOT, timeout=STAGE2_TIMEOUT_SEC,
            capture_output=True, text=True, check=False,
        )
    except subprocess.TimeoutExpired:
        return False, f"Stage 2 timeout after {STAGE2_TIMEOUT_SEC}s", {}
    except FileNotFoundError:
        return False, "claude CLI not on PATH", {}
    except Exception as e:
        return False, f"Stage 2 subprocess error: {type(e).__name__}: {e}", {}

    # Try to parse JSON envelope for usage tracking. Tolerate missing fields.
    usage: dict = {}
    try:
        envelope = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(envelope, dict):
            u = envelope.get("usage") or {}
            usage = {
                "input_tokens": u.get("input_tokens"),
                "output_tokens": u.get("output_tokens"),
                "cache_read_input_tokens": u.get("cache_read_input_tokens"),
                "cost_usd": envelope.get("total_cost_usd") or envelope.get("cost_usd"),
                "duration_api_ms": envelope.get("duration_api_ms"),
                "num_turns": envelope.get("num_turns"),
            }
    except (json.JSONDecodeError, AttributeError):
        pass

    tail = (r.stdout + "\n" + r.stderr)[-1500:]
    rule_path = config.system_report_dir(system_id) / "signal_rule.md"
    if not rule_path.exists():
        return False, f"Stage 2 returncode={r.returncode}; signal_rule.md not produced; tail:\n{tail}", usage
    return True, "Stage 2 OK", usage


def _format_validation_report(
    system_id: str,
    pre_result: tuple[bool, str],
    s1_result: tuple[bool, str],
    s2_result: tuple[bool, str] | None,
    proxy: ReliabilityProxy,
    elapsed: float,
) -> str:
    lines: list[str] = []
    lines.append(f"# Validation report — system {system_id}")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append(f"Elapsed: {elapsed:.1f}s")
    lines.append("")
    overall_pass = (
        pre_result[0]
        and s1_result[0]
        and (s2_result is None or s2_result[0])
        and proxy.reliability > 0
    )
    lines.append(f"## Overall: {'✅ PASS' if overall_pass else '❌ FAIL'}")
    lines.append("")
    lines.append(f"- **Family:** `{proxy.family}` (confidence {proxy.confidence:.2f})")
    lines.append(f"- **Reliability score:** **{proxy.reliability:.3f} ({proxy.band})**")
    lines.append(f"- **Trades / pairs:** {proxy.n_trades} / {proxy.n_pairs}")
    lines.append(f"- **Last trade:** {proxy.last_trade_date}")
    lines.append(f"- **Account type:** {proxy.account_type}")
    lines.append("")
    lines.append("## Pipeline status")
    lines.append("")
    lines.append(f"- Pre-check: {'✅' if pre_result[0] else '❌'} — {pre_result[1]}")
    lines.append(f"- Stage 1 (features + candidates): {'✅' if s1_result[0] else '❌'} — {s1_result[1]}")
    if s2_result is None:
        lines.append("- Stage 2 (LLM family naming): ⏭ skipped (Stage 1 failed)")
    else:
        lines.append(f"- Stage 2 (LLM family naming): {'✅' if s2_result[0] else '❌'} — {s2_result[1]}")
    lines.append("")
    lines.append("## Reliability components")
    lines.append("")
    lines.append("| component | weight | value |")
    lines.append("|---|---:|---:|")
    weights = {
        "direction_predictability": 0.25, "family_clarity": 0.20,
        "timing_concentration": 0.20, "sanity_pass": 0.10,
        "age_freshness": 0.10, "vendor_quality": 0.10, "pair_coverage": 0.05,
    }
    for k, w in weights.items():
        v = proxy.components.get(k, 0.0)
        lines.append(f"| {k} | {w:.2f} | {v:.3f} |")
    lines.append("")
    if proxy.notes:
        lines.append("## Notes")
        lines.append("")
        for n in proxy.notes:
            lines.append(f"- {n}")
        lines.append("")
    lines.append("## Linked artifacts")
    lines.append("")
    sd = config.system_report_dir(system_id).relative_to(REPO_ROOT)
    lines.append(f"- Fingerprint: `{sd / 'decoder' / 'fingerprint.md'}`")
    lines.append(f"- Candidates: `{sd / 'decoder' / 'candidates.json'}`")
    lines.append(f"- Signal rule: `{sd / 'signal_rule.md'}`")
    lines.append("")
    return "\n".join(lines) + "\n"


def _write_aggregate(results: list[dict]) -> None:
    RANKING_DIR.mkdir(parents=True, exist_ok=True)
    AGGREGATE_JSON.write_text(json.dumps(results, indent=2))

    df = pd.DataFrame(results)
    if df.empty:
        AGGREGATE_REPORT.write_text("# Overnight validation report\n\n_no systems processed yet_\n")
        return

    df = df.sort_values(["band_rank", "reliability"], ascending=[True, False])

    high = df[df["band"] == "HIGH"]
    medium = df[df["band"] == "MEDIUM"]
    low = df[df["band"] == "LOW"]
    failed = df[df["status"] != "OK"]

    lines: list[str] = []
    lines.append("# Overnight validation report — myfxbook reverse-engineering")
    lines.append("")
    lines.append(f"Generated (last update): {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append(f"Systems processed: {len(df)}  |  HIGH: {len(high)}  |  MEDIUM: {len(medium)}  |  LOW: {len(low)}  |  FAIL: {len(failed)}")
    lines.append("")
    lines.append("**This is Stage 3-lite (proxy reliability score)**, not the full")
    lines.append("Stage 3 from the plan (which requires OHLC replicator + gates §2.4).")
    lines.append("Top-N HIGH systems should be re-mined manually with `/decode-system <id>`")
    lines.append("on Opus + Stage 3 replicator before paper-trading consideration.")
    lines.append("")

    def _section(title: str, rows: pd.DataFrame, *, show_components: bool = False) -> None:
        lines.append(f"## {title} ({len(rows)})")
        lines.append("")
        if rows.empty:
            lines.append("_none_")
            lines.append("")
            return
        cols = ["system_id", "name", "reliability", "family", "confidence", "n_trades", "account_type"]
        if show_components:
            cols += ["dir_pred", "timing_conc", "age_fresh"]
        header = "| " + " | ".join(cols) + " |"
        sep = "|" + "|".join(["---"] * len(cols)) + "|"
        lines.append(header)
        lines.append(sep)
        for _, r in rows.iterrows():
            row = []
            for c in cols:
                v = r.get(c, "—")
                if isinstance(v, float):
                    row.append(f"{v:.3f}")
                else:
                    row.append(str(v))
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    _section("🟢 HIGH (paper-trading candidates after manual /decode-system + Stage 3)", high, show_components=True)
    _section("🟡 MEDIUM (investigate; may be false negatives)", medium, show_components=True)
    _section("🔴 LOW (folclore / unrecoverable / off-criteria)", low)
    _section("⚠️ FAILED (pipeline error)", failed)

    lines.append("## Top families across all PASS systems")
    lines.append("")
    if not df[df["status"] == "OK"].empty:
        fam_dist = df[df["status"] == "OK"]["family"].value_counts()
        for fam, n in fam_dist.items():
            lines.append(f"- `{fam}`: {int(n)} systems")
        lines.append("")

    lines.append("## What worked / what didn't")
    lines.append("")
    lines.append("**Worked:**")
    lines.append(f"- Pipeline ran on {len(df)} systems, {len(df[df['status'] == 'OK'])} reached signal_rule.md")
    if not high.empty:
        top_h = high.iloc[0]
        lines.append(f"- Top reliability: `{top_h['system_id']}` ({top_h.get('name', '?')}) "
                     f"= {top_h['reliability']:.3f} as `{top_h['family']}`")
    lines.append("")
    lines.append("**Didn't work:**")
    if not failed.empty:
        for _, r in failed.head(10).iterrows():
            lines.append(f"- `{r['system_id']}` ({r.get('name', '?')}): {r.get('reason', '?')}")
    if len(failed) > 10:
        lines.append(f"- _… and {len(failed) - 10} more failures_")
    if failed.empty:
        lines.append("- _no pipeline failures_")
    lines.append("")
    lines.append("## Next steps for user")
    lines.append("")
    lines.append("1. Manually invoke `/decode-system <id>` with **Opus** on top-3 HIGH for refined signal_rule.md.")
    lines.append("2. Implement Stage 3 proper (replicator on full OHLC + gates §2.4) per the plan.")
    lines.append("3. Cross-validate top family clusters — many systems sharing a family suggests vendor pattern.")
    lines.append("4. For LOW systems, sanity-check whether sanity_pass=0 reflects real martingale or parsing artifact.")
    lines.append("")
    AGGREGATE_REPORT.write_text("\n".join(lines))


def _band_rank(b: str) -> int:
    return {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(b, 3)


def process_one(system_id: str, force: bool) -> dict:
    t0 = time.time()
    sys_dir = config.system_report_dir(system_id)
    sys_dir.mkdir(parents=True, exist_ok=True)
    report_path = sys_dir / "validation_report.md"
    score_path = sys_dir / "reliability_score.json"

    if report_path.exists() and score_path.exists() and not force:
        log(f"  SKIP {system_id}: validation_report.md already exists (--force to override)")
        try:
            data = json.loads(score_path.read_text())
            data["status"] = "SKIP"
            data["band_rank"] = _band_rank(data.get("band", "LOW"))
            return data
        except Exception:
            pass

    pre_ok, pre_msg = precheck_system(system_id)
    if not pre_ok:
        log(f"  PRECHECK FAIL {system_id}: {pre_msg}")
        proxy = ReliabilityProxy(system_id=system_id, reliability=0.0, band="LOW", notes=[pre_msg])
        report = _format_validation_report(system_id, (pre_ok, pre_msg), (False, "skipped"), None, proxy, time.time() - t0)
        report_path.write_text(report)
        d = proxy.to_dict()
        d.update({"status": "SKIP_PRECHECK", "reason": pre_msg, "band_rank": _band_rank(proxy.band)})
        score_path.write_text(json.dumps(d, indent=2))
        return d

    fp = config.system_report_dir(system_id) / "decoder" / "fingerprint.md"
    cands = config.system_report_dir(system_id) / "decoder" / "candidates.json"
    if fp.exists() and cands.exists() and not force:
        log(f"  STAGE 1 {system_id}: SKIP (fingerprint+candidates already exist)")
        s1_ok, s1_msg = True, "Stage 1 SKIP — artifacts present"
    else:
        log(f"  STAGE 1 {system_id}: running …")
        s1_ok, s1_msg = run_stage1(system_id)
        log(f"  STAGE 1 {system_id}: {'OK' if s1_ok else 'FAIL'} — {s1_msg[:200]}")

    s2_result: tuple[bool, str] | None = None
    s2_usage: dict = {}
    rule_path = config.system_report_dir(system_id) / "signal_rule.md"
    if s1_ok:
        if rule_path.exists() and not force:
            log(f"  STAGE 2 {system_id}: SKIP (signal_rule.md already exists)")
            s2_result = (True, "Stage 2 SKIP — signal_rule.md present")
        else:
            log(f"  STAGE 2 {system_id}: running (sonnet via claude CLI) …")
            t_s2 = time.time()
            s2_ok, s2_msg, s2_usage = run_stage2(system_id)
            s2_elapsed = time.time() - t_s2
            tok_in = s2_usage.get("input_tokens")
            tok_out = s2_usage.get("output_tokens")
            cost = s2_usage.get("cost_usd")
            usage_str = (
                f" | tokens={tok_in}in/{tok_out}out cost=${cost} elapsed={s2_elapsed:.1f}s"
                if tok_in is not None else f" | elapsed={s2_elapsed:.1f}s"
            )
            log(f"  STAGE 2 {system_id}: {'OK' if s2_ok else 'FAIL'} — {s2_msg[:200]}{usage_str}")
            s2_result = (s2_ok, s2_msg)

    proxy = compute_reliability_proxy(system_id)
    elapsed = time.time() - t0
    report = _format_validation_report(
        system_id, (pre_ok, pre_msg), (s1_ok, s1_msg), s2_result, proxy, elapsed
    )
    report_path.write_text(report)

    status = "OK" if (s1_ok and s2_result and s2_result[0]) else ("PARTIAL" if s1_ok else "FAIL")
    reason = s1_msg if not s1_ok else (s2_result[1] if s2_result and not s2_result[0] else "OK")
    d = proxy.to_dict()
    # Pull system name for the aggregate
    info_path = config.system_info_json_path(system_id)
    name = system_id
    if info_path.exists():
        try:
            name = json.loads(info_path.read_text()).get("name", system_id)
        except Exception:
            pass
    d.update({
        "name": name[:60],
        "status": status,
        "reason": reason[:200],
        "elapsed_sec": elapsed,
        "band_rank": _band_rank(proxy.band),
        # Flat aliases for the table renderer
        "dir_pred": proxy.components.get("direction_predictability", 0.0),
        "timing_conc": proxy.components.get("timing_concentration", 0.0),
        "age_fresh": proxy.components.get("age_freshness", 0.0),
        # 5R-1-hardening Wave A item 9: token-log per Stage 2 call
        "stage2_usage": s2_usage,
    })
    score_path.write_text(json.dumps(d, indent=2))
    return d


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="Re-validate systems even if validation_report.md exists.")
    ap.add_argument("--limit", type=int, default=None, help="Process at most N systems (debug).")
    ap.add_argument("--only", nargs="*", default=None, help="Only process listed system_ids.")
    args = ap.parse_args(argv)

    systems = args.only or list_candidate_systems()
    if args.limit:
        systems = systems[: args.limit]
    log(f"START — {len(systems)} systems to process; force={args.force}; pid={os.getpid()}")

    results: list[dict] = []
    for i, sid in enumerate(systems, start=1):
        log(f"========== [{i}/{len(systems)}] system_id={sid} ==========")
        try:
            d = process_one(sid, force=args.force)
        except Exception as e:
            tb = traceback.format_exc()
            log(f"  FATAL {sid}: {type(e).__name__}: {e}\n{tb[-1000:]}")
            d = {
                "system_id": sid, "reliability": 0.0, "band": "LOW", "band_rank": 3,
                "family": "FATAL", "confidence": 0.0, "n_trades": 0, "n_pairs": 0,
                "status": "FAIL", "reason": f"{type(e).__name__}: {e}",
                "name": sid, "components": {},
                "dir_pred": 0.0, "timing_conc": 0.0, "age_fresh": 0.0,
            }
        results.append(d)
        # Write aggregate after EACH system so partial state is usable.
        _write_aggregate(results)
        log(f"  → reliability={d.get('reliability', 0):.3f} band={d.get('band', '?')} family={d.get('family', '?')}")

    log(f"DONE — {len(results)} systems processed; aggregate at {AGGREGATE_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
