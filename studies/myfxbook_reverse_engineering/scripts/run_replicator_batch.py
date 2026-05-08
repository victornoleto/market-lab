"""Batch driver — run replicator + comparator + score for all 52 systems.

Spec: `specs/replicator_full_addendum.md` §6, `specs/decoding_score_formula.md`.

Per-system outputs:
    systems/<id>/decoding/synthetic_trades.parquet
    systems/<id>/decoding/comparison_metrics.json
    systems/<id>/decoding/decoding_score.json
    systems/<id>/decoding/comparison_report.md

Cross-system output:
    _diagnostics/batch_summary.json
"""
from __future__ import annotations

import argparse
import json
import signal
import sys
import time
import traceback
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from studies.myfxbook_reverse_engineering.shared import config
from studies.myfxbook_reverse_engineering.shared.adversarial_validator import adversarial_validate
from studies.myfxbook_reverse_engineering.shared.pre_decode_screen import (
    screen_system,
    write_pre_screen_json,
)
from studies.myfxbook_reverse_engineering.shared.replicator import (
    run_one_full,
    load_frozen_rule,
    smoke_invariants,
)
from studies.myfxbook_reverse_engineering.shared.ohlc_dukascopy import OhlcLoader


PAUSE_GATES_BLOCKING_FINAL_RANKING = [
    "NEWS_RELEASE_MOMENTUM remains provisional with n=1 after R1",
    "needs_m1_review is high after R1: 13/30 systems",
]


def _trade_rows(df: pd.DataFrame) -> pd.DataFrame:
    if "is_trade" not in df.columns:
        return df.copy()
    return df[df["is_trade"] == True].copy()


def _load_real_trades(system_id: str) -> pd.DataFrame:
    path = config.trades_parquet_path(system_id)
    if not path.exists() and system_id == "1407880":
        path = config.STUDY_ROOT / "2026-05-01-happy_market_hours_v231" / "data" / "trades_1407880.parquet"
    if not path.exists():
        raise FileNotFoundError(f"trades.parquet not found at {path}")
    return pd.read_parquet(path)


def _adversarial_summary(real_trades: pd.DataFrame, synth: pd.DataFrame) -> dict:
    """Run real-vs-synthetic AUC validation `[advances_fin_ml, ch.5]`."""
    try:
        adv = adversarial_validate(real_trades, synth)
        return {
            "adversarial_auc": adv.auc,
            "adversarial_ci_low_95": adv.auc_ci_low_95,
            "adversarial_ci_high_95": adv.auc_ci_high_95,
            "adversarial_n_real": adv.n_real,
            "adversarial_n_synthetic": adv.n_synthetic,
            "adversarial_n_features": adv.n_features,
            "adversarial_top_features": list(adv.feature_importance.keys())[:5],
            "adversarial_notes": adv.notes,
        }
    except Exception as exc:
        return {
            "adversarial_auc": None,
            "adversarial_ci_low_95": None,
            "adversarial_ci_high_95": None,
            "adversarial_n_real": int(len(real_trades)),
            "adversarial_n_synthetic": int(len(synth)),
            "adversarial_n_features": None,
            "adversarial_top_features": [],
            "adversarial_notes": [f"adversarial_error: {type(exc).__name__}: {exc}"],
        }


def _r1_pool_ids(base: Path) -> list[str]:
    """Return the R1 v3 pool from the pre-R1 manifest.

    This intentionally ignores `status.tsv`, which is known incomplete (25/30 rows).
    The manifest + promoted frozen rules are the audit source for the deterministic
    5R-1 run. Final ranking remains blocked by R1 pause gates; this driver only
    produces per-system replicator/comparator/score artifacts.
    """
    manifest_path = base / "_diagnostics" / "R1_pre_manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)
    return sorted(item["system_id"] for item in manifest["items"])


def write_comparison_report_md(
    system_id: str,
    rule_summary: dict,
    report,
    score: dict,
    invariants: dict,
    out_path: Path,
) -> None:
    md = [
        f"# Decoding comparison report — system `{system_id}`",
        "",
        f"- Family (Stage 2): **{rule_summary['family']}**  (confidence {rule_summary['confidence']})",
        f"- Direction executor: `{rule_summary['executor']}`",
        f"- Features used: {rule_summary['features_used']}",
        f"- Entry hours UTC: {rule_summary['entry_hours']}",
        f"- Pairs: {rule_summary['pairs']}",
        f"- Max holding hours: {rule_summary['max_holding_hours']}"
        + (" (default fallback)" if rule_summary["used_default_holding"] else ""),
        "",
        f"## Decoding fidelity score: **{score['fidelity_score']:.4f}** ({score['score_band']})",
        "",
        "| Term | Weight | Value | Contribution |",
        "|---|---:|---:|---:|",
        f"| entry_timing_f1 | 0.25 | {score['terms']['entry_timing_f1']} | {0.25 * score['terms']['entry_timing_f1']:.4f} |",
        f"| baseline_lift_normalized | 0.15 | {score['terms']['baseline_lift_normalized']} (lift_pp={score['terms']['lift_vs_baseline_pp']}) | {0.15 * score['terms']['baseline_lift_normalized']:.4f} |",
        f"| direction_acc_at_matched | 0.20 | {score['terms']['direction_acc_at_matched']} | {0.20 * score['terms']['direction_acc_at_matched']:.4f} |",
        f"| hold_similarity | 0.15 | {score['terms']['hold_similarity']} | {0.15 * score['terms']['hold_similarity']:.4f} |",
        f"| count_ratio_proximity | 0.15 | {score['terms']['count_ratio_proximity']} (ratio={score['terms']['count_ratio']}) | {0.15 * score['terms']['count_ratio_proximity']:.4f} |",
        f"| pnl_correlation_pos | 0.10 | {score['terms']['pnl_correlation_pos']} (raw={score['terms']['pnl_correlation_raw']}) | {0.10 * score['terms']['pnl_correlation_pos']:.4f} |",
        "",
        "## Comparison details",
        "",
        f"- n_real: {report.n_real}",
        f"- n_synthetic: {report.n_synthetic}",
        f"- n_matched (±5min): {report.n_matched}",
        f"- entry_timing_precision: {report.entry_timing_precision}",
        f"- entry_timing_recall: {report.entry_timing_recall}",
        f"- entry_timing_f1: {report.entry_timing_f1}",
        f"- direction_acc_at_matched: {report.direction_acc_at_matched}",
        f"- hold_KS_stat: {report.hold_KS_stat}",
        f"- hold_similarity: {report.hold_similarity}",
        f"- count_ratio: {report.count_ratio}",
        f"- pnl_correlation: {report.pnl_correlation}",
        "",
        "### Baseline comparison",
        "",
        f"- always_buy combined-hit rate: {report.baseline_always_buy_combined_hit_rate}",
        f"- hour_majority combined-hit rate: {report.baseline_hour_majority_combined_hit_rate}",
        f"- pair_hour_majority combined-hit rate: {report.baseline_pair_hour_majority_combined_hit_rate}",
        f"- max_baseline: {report.max_baseline_combined_hit_rate}",
        f"- synthetic combined-hit rate: {report.synthetic_combined_hit_rate}",
        f"- lift_vs_baseline_pp: {report.lift_vs_baseline_pp}",
        "",
        "## Smoke invariants",
        "",
    ]
    for inv_name, passed in invariants.items():
        md.append(f"- {inv_name}: {'PASS' if passed else 'FAIL'}")
    md.append("")
    md.append("---")
    md.append("")
    md.append("**Disclaimer:** fidelity_score mede capacidade de reproduzir trades reais via")
    md.append("regra recuperada de OHLC público. Não implica edge econômico (Stage 3) nem")
    md.append("tradeable state (sanity flags ortogonais).")
    out_path.write_text("\n".join(md))


@contextmanager
def _hard_timeout(seconds: int, label: str):
    """Raise TimeoutError if the wrapped block exceeds `seconds`. Main thread only."""
    if seconds <= 0:
        yield
        return

    def _handler(signum, frame):
        raise TimeoutError(f"{label} exceeded {seconds}s")

    prev = signal.signal(signal.SIGALRM, _handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, prev)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Replicator batch driver — see specs/replicator_full_addendum.md §6"
    )
    ap.add_argument("--limit", type=int, default=None,
                    help="Process at most N systems (debug / smoke).")
    ap.add_argument("--only", nargs="*", default=None,
                    help="Process only the listed system_ids.")
    ap.add_argument("--force", action="store_true",
                    help="Re-run systems even if decoding outputs already exist.")
    ap.add_argument("--r1-pool", action="store_true",
                    help="Process the 30 R1-promoted frozen_rules v3 systems only. "
                         "Uses _diagnostics/R1_pre_manifest.json, not status.tsv.")
    ap.add_argument("--timeout-per-system", type=int, default=600,
                    help="Hard timeout per system in seconds (0 disables). "
                         "Default 600s — vectorized smoke is ~8s/system, so 600s catches loader hangs.")
    ap.add_argument("--freq", choices=("M1", "M5"), default="M5",
                    help="Base OHLC/candidate frequency. Default M5 preserves the original 5R-1 run.")
    ap.add_argument("--output-dir-name", default="decoding",
                    help="Per-system output directory name under systems/<id>/. "
                         "Use decoding_m1 for forensic M1 runs to avoid touching M5 outputs.")
    ap.add_argument("--summary-name", default=None,
                    help="Diagnostics summary filename. Defaults to batch_summary.json for decoding, "
                          "or batch_summary_<output-dir-name>.json otherwise.")
    ap.add_argument("--enable-pre-screen", action="store_true",
                    help="Run pre_decode_screen per system before decode; skip if decision=STOP.")
    ap.add_argument("--enable-adversarial", action="store_true",
                    help="Run adversarial_validator on real vs synthetic trades per system.")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    base = Path(__file__).resolve().parent.parent
    systems_dir = base / "systems"
    diag_dir = base / "_diagnostics"
    diag_dir.mkdir(parents=True, exist_ok=True)
    log_path = base.parent.parent / "logs" / "myfxbook_reverse_engineering.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if args.only:
        all_ids = list(args.only)
        batch_scope = "explicit_only"
    elif args.r1_pool:
        all_ids = _r1_pool_ids(base)
        batch_scope = "r1_pool_v3_30"
    else:
        all_ids = sorted(p.name for p in systems_dir.iterdir() if p.is_dir())
        batch_scope = "all_system_dirs"
    if args.limit:
        all_ids = all_ids[: args.limit]
    print(
        f"[batch] {len(all_ids)} systems to process; force={args.force}; "
        f"timeout_per_system={args.timeout_per_system}s; freq={args.freq}; "
        f"output_dir={args.output_dir_name}",
        flush=True,
    )

    loader = OhlcLoader(freq=args.freq)
    summary = {
        "scope": batch_scope,
        "approval_scope": "5R-1 deterministic replicator/comparator/score only",
        "freq": args.freq,
        "output_dir_name": args.output_dir_name,
        "enable_pre_screen": bool(args.enable_pre_screen),
        "enable_adversarial": bool(args.enable_adversarial),
        "final_ranking_allowed": False,
        "strategy_decision_allowed": False,
        "blocking_pause_gates": PAUSE_GATES_BLOCKING_FINAL_RANKING,
        "passed": [],
        "failed": {},
        "skipped": {},
    }
    t_start = time.time()

    for i, sid in enumerate(all_ids):
        # Resume guard: skip if outputs exist and --force not set
        out_dir = systems_dir / sid / args.output_dir_name
        score_path = out_dir / "decoding_score.json"
        if score_path.exists() and not args.force:
            summary["skipped"][sid] = "already_done"
            print(f"[{i+1:>2}/{len(all_ids)}] {sid} SKIP already_done", flush=True)
            continue

        t0 = time.time()
        pre_screen_extra = {}
        real_trade_rows = None
        if args.enable_pre_screen:
            try:
                real_trades = _load_real_trades(sid)
                real_trade_rows = _trade_rows(real_trades)
                pre_screen = screen_system(sid, trades_df=real_trade_rows)
                pre_screen_path = write_pre_screen_json(
                    pre_screen,
                    output_path=out_dir / "pre_decode_screen.json",
                )
                pre_screen_extra = {
                    "pre_screen_decision": pre_screen.decision,
                    "pre_screen_path": str(pre_screen_path),
                    "pre_screen_notes": pre_screen.notes,
                }
                if pre_screen.decision != "GO":
                    summary["skipped"][sid] = {
                        "status": "PRE_SCREEN_STOP",
                        **pre_screen_extra,
                    }
                    print(
                        f"[{i+1:>2}/{len(all_ids)}] {sid} SKIP PRE_SCREEN_STOP  "
                        "EA rejeitado pelo pre-screen",
                        flush=True,
                    )
                    continue
            except Exception as e:
                err = f"pre_screen_error: {type(e).__name__}: {e}"
                summary["skipped"][sid] = err
                print(f"[{i+1:>2}/{len(all_ids)}] {sid} SKIP  {err}", flush=True)
                with open(log_path, "a") as f:
                    f.write(f"[{time.strftime('%FT%T')}] [batch] {sid} SKIP: {err}\n")
                continue

        try:
            with _hard_timeout(args.timeout_per_system, f"run_one_full({sid})"):
                result = run_one_full(sid, base, loader=loader, bar_freq=args.freq)
        except TimeoutError as e:
            err = f"TimeoutError: {e}"
            summary["failed"][sid] = err
            print(f"[{i+1:>2}/{len(all_ids)}] {sid} TIMEOUT  {err}", flush=True)
            with open(log_path, "a") as f:
                f.write(f"[{time.strftime('%FT%T')}] [batch] {sid} TIMEOUT: {err}\n")
            continue
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            tb = traceback.format_exc(limit=2)
            summary["failed"][sid] = err
            print(f"[{i+1:>2}/{len(all_ids)}] {sid} FAIL  {err}", flush=True)
            with open(log_path, "a") as f:
                f.write(f"[{time.strftime('%FT%T')}] [batch] {sid} FAIL: {err}\n{tb}\n")
            continue

        if result["status"] != "ok":
            if pre_screen_extra:
                summary["skipped"][sid] = {"status": result["status"], **pre_screen_extra}
            else:
                summary["skipped"][sid] = result["status"]
            print(
                f"[{i+1:>2}/{len(all_ids)}] {sid} SKIP {result['status']}  "
                f"({time.time()-t0:.1f}s)",
                flush=True,
            )
            continue

        rule = load_frozen_rule(sid, base)
        report = result["comparison_report"]
        score = result["decoding_score"]
        score["phase_guard"] = {
            "approval_scope": "5R-1 deterministic replicator/comparator/score only",
            "freq": args.freq,
            "output_dir_name": args.output_dir_name,
            "final_ranking_allowed": False,
            "strategy_decision_allowed": False,
            "blocking_pause_gates": PAUSE_GATES_BLOCKING_FINAL_RANKING,
        }
        synth = result["synthetic_trades"]
        invariants = smoke_invariants(result, rule)
        adversarial_extra = {}
        if args.enable_adversarial:
            if real_trade_rows is None:
                real_trade_rows = _trade_rows(_load_real_trades(sid))
            adversarial_extra = _adversarial_summary(real_trade_rows, synth)

        out_dir = systems_dir / sid / args.output_dir_name
        out_dir.mkdir(parents=True, exist_ok=True)

        if not synth.empty:
            synth.to_parquet(out_dir / "synthetic_trades.parquet")

        with open(out_dir / "comparison_metrics.json", "w") as f:
            json.dump(asdict(report), f, indent=2, default=str)

        with open(out_dir / "decoding_score.json", "w") as f:
            json.dump(score, f, indent=2, default=str)

        write_comparison_report_md(
            system_id=sid,
            rule_summary=result["rule_summary"],
            report=report,
            score=score,
            invariants=invariants,
            out_path=out_dir / "comparison_report.md",
        )

        summary["passed"].append(
            {
                "system_id": sid,
                "family": rule.family,
                "fidelity_score": score["fidelity_score"],
                "score_band": score["score_band"],
                "n_real": report.n_real,
                "n_synthetic": report.n_synthetic,
                "n_matched": report.n_matched,
                **pre_screen_extra,
                **adversarial_extra,
            }
        )
        elapsed = time.time() - t0
        print(
            f"[{i+1:>2}/{len(all_ids)}] {sid:>10}  fam={rule.family:<28} "
            f"score={score['fidelity_score']:.3f} ({score['score_band']:<6}) "
            f"n_real={report.n_real:<5} n_synth={report.n_synthetic:<6} "
            f"({elapsed:.1f}s)",
            flush=True,
        )

    total_elapsed = time.time() - t_start
    summary["wallclock_seconds"] = round(total_elapsed, 1)
    summary["n_total"] = len(all_ids)
    summary["n_passed"] = len(summary["passed"])
    summary["n_failed"] = len(summary["failed"])
    summary["n_skipped"] = len(summary["skipped"])

    summary_name = args.summary_name
    if summary_name is None:
        summary_name = "batch_summary.json" if args.output_dir_name == "decoding" else f"batch_summary_{args.output_dir_name}.json"
    out_summary = diag_dir / summary_name
    with open(out_summary, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n[batch] DONE in {total_elapsed/60:.1f} min")
    print(f"[batch] {summary['n_passed']} passed, {summary['n_skipped']} skipped, "
          f"{summary['n_failed']} failed")
    print(f"[batch] summary written to {out_summary}")


if __name__ == "__main__":
    main()
