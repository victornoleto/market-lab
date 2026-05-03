"""Stage 1 orchestrator — feature extraction + candidate rule mining per system.

Pipeline (per system_id):
  1. Load `data/trades/<id>/trades.parquet`
  2. compute_sanity (reuse existing module) — for fingerprint header
  3. compute_eda (reuse existing module) — for timing/exit/direction context
  4. compute_entry_features (new) — multi-tf OHLC features per trade
  5. mine_candidate_rules (new) — top-K candidate direction rules
  6. Persist: systems/<id>/decoder/{features.parquet, candidates.json, fingerprint.md}

Usage:
    uv run python -m studies.myfxbook_reverse_engineering.shared.run_decoder_stage1 --system-id 1407880
    # Pilot iteration (N most recent trades only, fast OHLC fetch):
    uv run python -m studies.myfxbook_reverse_engineering.shared.run_decoder_stage1 --system-id 1407880 --sample 200

Citations:
- [advances_fin_ml, ch.5,7] — features + purged k-fold
- [evidence_based_ta, Aronson, p.367-380] — session/hour FX
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.myfxbook_reverse_engineering.shared import (  # noqa: E402
    config, eda, sanity,
)
from studies.myfxbook_reverse_engineering.shared.decoder_candidates import (  # noqa: E402
    Candidate, mine_candidate_rules,
)
from studies.myfxbook_reverse_engineering.shared.decoder_features import (  # noqa: E402
    FeatureExtractionStats, compute_entry_features,
)
from studies.myfxbook_reverse_engineering.shared.ohlc_dukascopy import OhlcLoader  # noqa: E402

LOG_PATH = REPO_ROOT / "logs" / "myfxbook_reverse_engineering.log"


def log(msg: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().isoformat(timespec='seconds')}] [stage1] {msg}"
    print(line, flush=True)
    with LOG_PATH.open("a") as f:
        f.write(line + "\n")


def decoder_dir(system_id: int | str) -> Path:
    return config.system_report_dir(system_id) / "decoder"


def _format_fingerprint(
    system_id: str,
    sanity_stats: sanity.SanityStats,
    eda_stats: eda.EDAStats,
    feat_stats: FeatureExtractionStats,
    candidates: list[Candidate],
    sampled: int | None,
) -> str:
    """Single-page synthesis for the LLM Stage 2 to read."""
    lines: list[str] = []
    lines.append(f"# Decoder fingerprint — system {system_id}")
    lines.append("")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    if sampled:
        lines.append(f"⚠ Sampled run: only the most-recent {sampled} trades were used (full = {sanity_stats.n_trades})")
    lines.append("")

    # === Sanity summary ===
    lines.append("## Sanity (martingale + lot dynamics)")
    lines.append("")
    lines.append(f"- n_trades: **{sanity_stats.n_trades}**, deposits: {sanity_stats.n_deposits}")
    lines.append(f"- pairs: {sanity_stats.symbols}")
    lines.append(f"- actions: {sanity_stats.actions}")
    lines.append(f"- date range: {sanity_stats.first_open_utc} → {sanity_stats.last_close_utc}")
    lines.append(f"- max gap days: {sanity_stats.max_gap_days:.1f}")
    lines.append(f"- lot p50/p95/p99/max: {sanity_stats.lot_p50:.2f} / {sanity_stats.lot_p95:.2f} / "
                 f"{sanity_stats.lot_p99:.2f} / {sanity_stats.lot_max:.2f}")
    lines.append(f"- lot p95/p50 ratio: {sanity_stats.lot_ratio_p95_p50:.2f}")
    lines.append(f"- martingale flag: **{'PASS (no martingale)' if sanity_stats.k1_pass else 'FAIL (martingale-like dynamics)'}**, "
                 f"steps={sanity_stats.n_martingale_steps}, max_streak={sanity_stats.max_doubling_streak}")
    if sanity_stats.k1_flags:
        lines.append(f"- k1 flags: {sanity_stats.k1_flags}")
    lines.append(f"- hold p50/p95/max (h): {sanity_stats.hold_p50_h:.2f} / {sanity_stats.hold_p95_h:.2f} / {sanity_stats.hold_max_h:.2f}")
    lines.append("")

    # === EDA summary ===
    lines.append("## EDA (timing / exit / direction)")
    lines.append("")
    top_hours = eda_stats.entry_hour.sort_values(ascending=False).head(5)
    lines.append("Top entry hours (UTC):")
    for h, n in top_hours.items():
        lines.append(f"  - {int(h):02d}:00 — {int(n)} trades")
    lines.append("")
    lines.append("Top entry hour:5min (UTC):")
    for (h, m), n in eda_stats.entry_hour_minute_top20.head(5).items():
        lines.append(f"  - {int(h):02d}:{int(m):02d} — {int(n)} trades")
    lines.append("")
    lines.append("Exit kind distribution:")
    for k, n in eda_stats.exit_kind.items():
        lines.append(f"  - {k}: {int(n)}")
    lines.append("")
    lines.append("Direction by pair (Buy %):")
    if "buy_pct" in eda_stats.direction_by_pair.columns:
        for sym, row in eda_stats.direction_by_pair.iterrows():
            lines.append(f"  - {sym}: total={int(row['total'])}, buy_pct={row['buy_pct']:.1f}%")
    lines.append("")
    lines.append("Direction by hour (Buy %, top 5 by activity):")
    if "total" in eda_stats.direction_by_hour.columns:
        top = eda_stats.direction_by_hour.sort_values("total", ascending=False).head(5)
        for h, row in top.iterrows():
            lines.append(f"  - hour={int(h):02d}: total={int(row['total'])}, buy_pct={row['buy_pct']:.1f}%")
    lines.append("")

    # === Feature extraction stats ===
    lines.append("## Feature extraction")
    lines.append("")
    lines.append(f"- trades processed: {feat_stats.n_trades}")
    lines.append(f"- feature columns: {feat_stats.n_features}")
    lines.append(f"- skipped (no OHLC at anchor): {feat_stats.n_skipped_no_ohlc}")
    lines.append(f"- skipped (insufficient lookback history): {feat_stats.n_skipped_short_history}")
    lines.append("")

    # === Candidates ===
    lines.append("## Top candidate direction rules")
    lines.append("")
    lines.append("| rank | miner | rule | match_rate (CV) | std | coverage | p_corr |")
    lines.append("|---:|---|---|---:|---:|---:|---:|")
    for c in candidates:
        rule = c.rule_text.replace("\n", " ").replace("|", "\\|")
        if len(rule) > 130:
            rule = rule[:127] + "..."
        p = "—" if pd.isna(c.p_value_corrected) else f"{c.p_value_corrected:.3f}"
        std = "—" if c.match_rate_std == 0 else f"{c.match_rate_std:.3f}"
        lines.append(
            f"| {c.rank} | {c.miner} | {rule} | {c.match_rate_cv:.3f} | {std} | {c.coverage:.2f} | {p} |"
        )
    lines.append("")

    # Print full tree/ripper text below the table for completeness.
    for c in candidates:
        if c.miner in {"tree", "ripper"}:
            lines.append(f"### {c.miner.upper()} full output (rank {c.rank})")
            lines.append("```")
            lines.append(c.rule_text)
            lines.append("```")
            lines.append("")

    lines.append("## Notes for Stage 2 (LLM family naming)")
    lines.append("")
    lines.append(
        "Use the timing peaks (top entry hours), pair universe, exit_kind, and the candidates table "
        "above to identify the strategy family. Cross-check candidates with the literature: "
        "[evidence_based_ta, Aronson, p.367-380] for session/hour FX, [advances_fin_ml, ch.5] for "
        "feature importance interpretation. Cite ≥ 2 books in `signal_rule.md`."
    )
    return "\n".join(lines) + "\n"


def run_stage1(system_id: int | str, *, sample: int | None = None) -> dict:
    sid = str(system_id)
    parquet_path = config.trades_parquet_path(sid)
    if not parquet_path.exists():
        raise FileNotFoundError(
            f"trades parquet not found at {parquet_path}. Run download_data.py first."
        )

    log(f"START system_id={sid}, sample={sample}")
    t0 = time.time()
    trades_df = pd.read_parquet(parquet_path)
    trades_only = trades_df[trades_df["is_trade"]].copy().sort_values("open_dt_utc")
    if sample is not None:
        trades_only = trades_only.tail(sample)
    log(f"  loaded {len(trades_only)} trades (full={int(trades_df['is_trade'].sum())})")

    sanity_stats = sanity.compute_sanity(trades_df, sid)
    eda_stats = eda.compute_eda(trades_df, sid)
    log(f"  sanity computed (k1_pass={sanity_stats.k1_pass}, n_trades={sanity_stats.n_trades})")
    log(f"  eda computed (top hour count = {int(eda_stats.entry_hour.max())})")

    out_dir = decoder_dir(sid)
    out_dir.mkdir(parents=True, exist_ok=True)

    loader = OhlcLoader(freq="M1")
    log(f"  extracting features for {len(trades_only)} trades …")
    features_df, feat_stats = compute_entry_features(trades_only, loader, progress=True)
    log(f"  features done: shape={features_df.shape}, "
        f"skipped_no_ohlc={feat_stats.n_skipped_no_ohlc}, skipped_short={feat_stats.n_skipped_short_history}")

    feat_path = out_dir / "features.parquet"
    # parquet doesn't accept the multi-pair object index; reset to columns.
    features_to_save = features_df.reset_index().rename(columns={"index": "trade_idx"})
    features_to_save.to_parquet(feat_path, index=False)

    log(f"  mining candidate rules …")
    candidates = mine_candidate_rules(features_df, top_k=10)
    cand_path = out_dir / "candidates.json"
    cand_path.write_text(json.dumps([c.to_dict() for c in candidates], indent=2))
    log(f"  candidates: {len(candidates)} (best match_rate_cv={candidates[0].match_rate_cv:.3f} "
        f"miner={candidates[0].miner})")

    fingerprint_md = _format_fingerprint(
        sid, sanity_stats, eda_stats, feat_stats, candidates, sampled=sample if sample else None
    )
    fp_path = out_dir / "fingerprint.md"
    fp_path.write_text(fingerprint_md)
    log(f"  fingerprint written ({len(fingerprint_md)} chars) → {fp_path.relative_to(REPO_ROOT)}")

    elapsed = time.time() - t0
    log(f"DONE system_id={sid} in {elapsed:.1f}s")
    return {
        "system_id": sid,
        "n_trades_processed": int(feat_stats.n_trades),
        "n_features": int(feat_stats.n_features),
        "best_candidate_match_rate": float(candidates[0].match_rate_cv) if candidates else 0.0,
        "best_candidate_miner": candidates[0].miner if candidates else "none",
        "elapsed_sec": elapsed,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Stage 1 — feature + candidates per system")
    ap.add_argument("--system-id", required=True, help="MyFxBook system_id (folder under data/trades/)")
    ap.add_argument("--sample", type=int, default=None,
                    help="Take only the most-recent N trades (faster pilot iteration; default: all)")
    args = ap.parse_args(argv)
    summary = run_stage1(args.system_id, sample=args.sample)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
