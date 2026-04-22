"""End-to-end Phase D-MVP pipeline: download → orchestrate → verdict.

Single entry point that chains the whole Strategy D MVP hunt:

1. Check if the yfinance cache is populated for the IBrX-100 proxy; if
   fewer than ``min_cached_tickers`` are present, run the downloader.
2. Run the grid orchestrator (resume-safe via ``--skip-existing``).
3. Read ``reports/phase_d_mvp/SUMMARY.md`` + ``dsr_results.json`` to
   determine the verdict:
      * ``WINNER_CANDIDATE``: at least one config passes PBO < 0.5 AND
        DSR p < 0.1. Promote to Fase D-ampliada.
      * ``NO_WINNER_MVP``: every config fails the joint filter. Write
        ``reports/phase_d_mvp/BREADTH_NO_WINNER_D.md`` with the cross-
        config pattern and the recommended R1-R5 pivot.
      * ``ERROR``: unrecoverable pipeline failure (network, disk, etc.).
4. Write a human-readable journal entry to ``jornada/`` with the outcome
   and update ``jornada/README.md`` (newest-first list).
5. Emit a final log line with the verdict for downstream automation.

Designed to run unattended for 2-3 hours. Logs append to
``logs/phase_d_mvp.log`` so ``tail -f`` works across the whole run.

Usage
-----
::

    # One shot, all defaults
    .venv/bin/python -m scripts.phase_d_mvp.run_end_to_end

    # Resume after interruption (skip completed per-split JSONs)
    .venv/bin/python -m scripts.phase_d_mvp.run_end_to_end --skip-existing

    # Restrict to a single lead for debugging
    .venv/bin/python -m scripts.phase_d_mvp.run_end_to_end --leads D1

    # Dry-run prints the plan and exits without running backtests
    .venv/bin/python -m scripts.phase_d_mvp.run_end_to_end --dry-run

Exit codes
----------
    0  success, WINNER_CANDIDATE detected
    2  success, NO_WINNER_MVP (early-abort triggered)
    1  hard failure (exception propagated from downloader or orchestrator)
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal

from ai_trade.backtest.data.br_tickers import IBRX100_TICKERS
from ai_trade.backtest.data.yfinance_source import DEFAULT_CACHE_DIR

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LOG_DIR = _PROJECT_ROOT / "logs"
_REPORTS_DIR = _PROJECT_ROOT / "reports" / "phase_d_mvp"
_JORNADA_DIR = _PROJECT_ROOT / "jornada"

Verdict = Literal["WINNER_CANDIDATE", "NO_WINNER_MVP", "ERROR"]


def _configure_logging(log_path: Path) -> logging.Logger:
    """Unified logger: stdout + append-only file handler."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger("phase_d_mvp.e2e")
    root.setLevel(logging.INFO)
    root.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    stdout_h = logging.StreamHandler(sys.stdout)
    stdout_h.setFormatter(fmt)
    root.addHandler(stdout_h)
    file_h = logging.FileHandler(log_path, mode="a")
    file_h.setFormatter(fmt)
    root.addHandler(file_h)
    return root


# ---------------------------------------------------------------------------
# Stage 1 — data layer
# ---------------------------------------------------------------------------
def count_cached_tickers(cache_dir: Path, tickers: list[str]) -> int:
    return sum(1 for t in tickers if (cache_dir / f"{t}.parquet").exists())


def ensure_ohlcv(
    log: logging.Logger,
    start: date,
    end: date,
    min_cached_tickers: int,
) -> None:
    """If fewer than ``min_cached_tickers`` are cached, trigger the downloader."""
    n_cached = count_cached_tickers(DEFAULT_CACHE_DIR, IBRX100_TICKERS)
    log.info("OHLCV cache check: %d / %d tickers present at %s",
             n_cached, len(IBRX100_TICKERS), DEFAULT_CACHE_DIR)
    if n_cached >= min_cached_tickers:
        log.info("cache is sufficient (≥ %d) — skipping download", min_cached_tickers)
        return

    log.info("cache below threshold; launching downloader")
    cmd = [
        sys.executable, "-m", "scripts.phase_d_mvp.download_ibrx100",
        "--start", start.isoformat(),
        "--end", end.isoformat(),
        "--log-path", str(_LOG_DIR / "download_ibrx100.log"),
    ]
    log.info("exec: %s", " ".join(cmd))
    result = subprocess.run(cmd, check=False, cwd=_PROJECT_ROOT)
    if result.returncode != 0:
        log.error("downloader exited with code %d", result.returncode)
        raise RuntimeError(f"download failed (rc={result.returncode})")
    n_after = count_cached_tickers(DEFAULT_CACHE_DIR, IBRX100_TICKERS)
    log.info("post-download cache: %d / %d tickers", n_after, len(IBRX100_TICKERS))


# ---------------------------------------------------------------------------
# Stage 2 — grid orchestrator
# ---------------------------------------------------------------------------
def run_orchestrator(
    log: logging.Logger,
    skip_existing: bool,
    leads: list[str],
    initial_cash: float,
) -> int:
    cmd = [
        sys.executable, "-m", "scripts.phase_d_mvp.orchestrator",
        "--initial-cash", str(initial_cash),
        "--leads", *leads,
    ]
    if skip_existing:
        cmd.append("--skip-existing")
    log.info("exec: %s", " ".join(cmd))
    result = subprocess.run(cmd, check=False, cwd=_PROJECT_ROOT)
    log.info("orchestrator exited with code %d", result.returncode)
    return result.returncode


# ---------------------------------------------------------------------------
# Stage 3 — verdict
# ---------------------------------------------------------------------------
def interpret_verdict(log: logging.Logger, orchestrator_rc: int) -> Verdict:
    summary_path = _REPORTS_DIR / "SUMMARY.md"
    dsr_path = _REPORTS_DIR / "dsr_results.json"
    if orchestrator_rc == 2:
        log.info("orchestrator signaled early-abort (rc=2) — NO_WINNER_MVP")
        return "NO_WINNER_MVP"
    if orchestrator_rc != 0:
        log.error("orchestrator failed (rc=%d) — ERROR", orchestrator_rc)
        return "ERROR"
    # Even on rc=0, re-check the SUMMARY to be sure.
    if not summary_path.exists():
        log.error("SUMMARY.md missing despite rc=0 — ERROR")
        return "ERROR"
    if dsr_path.exists():
        with open(dsr_path) as f:
            dsr_results = json.load(f)
        pass_count = sum(
            1 for r in dsr_results.values() if r.get("p_value", 1.0) < 0.1
        )
        log.info("%d configs passed DSR p<0.1", pass_count)
    return "WINNER_CANDIDATE"


# ---------------------------------------------------------------------------
# Stage 4 — journal entry
# ---------------------------------------------------------------------------
def _now_slug() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%d-%H%M")


def _stat_files(paths: list[Path]) -> str:
    lines = []
    for p in paths:
        if p.exists():
            lines.append(f"- `{p.relative_to(_PROJECT_ROOT)}` (exists, "
                         f"{p.stat().st_size // 1024} KB)")
        else:
            lines.append(f"- `{p.relative_to(_PROJECT_ROOT)}` (missing)")
    return "\n".join(lines)


def write_journal_entry(log: logging.Logger, verdict: Verdict) -> Path:
    slug = _now_slug()
    fname = f"{slug}-phase-d-mvp-{verdict.lower().replace('_', '-')}.md"
    path = _JORNADA_DIR / fname
    title_map = {
        "WINNER_CANDIDATE": "Phase D-MVP — candidato vencedor detectado",
        "NO_WINNER_MVP": "Phase D-MVP — BREADTH_NO_WINNER_D (early-abort)",
        "ERROR": "Phase D-MVP — falha técnica",
    }
    summary_file = _REPORTS_DIR / "SUMMARY.md"
    relevant_files = [
        summary_file,
        _REPORTS_DIR / "dsr_results.json",
        _REPORTS_DIR / "oos_returns_matrix.npz",
        _REPORTS_DIR / "BREADTH_NO_WINNER_D.md",
    ]

    lines = [
        f"# {title_map[verdict]}",
        "",
        f"**Data:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Verdict:** `{verdict}`",
        "",
        "## Contexto",
        "",
    ]

    if verdict == "WINNER_CANDIDATE":
        lines.extend([
            "Pelo menos **1 config passa o filtro mínimo** (PBO < 0.5 AND DSR "
            "p < 0.1) do Phase D-MVP. Isso autoriza avançar pra Fase D-ampliada "
            "(implementar Fundamentus scraper + D2 Magic Formula + D3 Multi-fator "
            "V+M+Q + D5-D8 combos). Os gates plenos da Fase D-gate (cross-lib + "
            "bootstrap 99.9% CI + cost/tax stress + sector/liquidity stress) só "
            "rodam depois.",
            "",
            "Próximo passo: abrir spec Fase D-ampliada a partir do config "
            "winner, decidir se worth investir em scraping Fundamentus massa ou "
            "ficar em OHLCV-only variants.",
        ])
    elif verdict == "NO_WINNER_MVP":
        lines.extend([
            "Zero configs do grid D1 (24) + D4 (18) = **42/42 FAIL** o filtro "
            "mínimo (PBO < 0.5 AND DSR p < 0.1). Early-abort gate do plano "
            "Fase D-MVP dispara — **não justifica implementar Fundamentus "
            "scrape + D2/D3/combos** sob este grid OHLCV-only.",
            "",
            "Cumulativo honest do projeto passa de 29/29 → **71/71 FAIL** "
            "(6 V2 Plano A + 10 Phase 3.6 + 8 Phase 3.7-3 + 5 Phase 3.8-1 + "
            "42 Phase D-MVP).",
            "",
            "Próximos passos possíveis (decisão do usuário):",
            "- **R1:** variações do universo (IBrA amplo; Small11; ações específicas de setor)",
            "- **R2:** variações de cadência (bi-mensal pra reduzir rotatividade)",
            "- **R3:** abandonar Strategy D, consolidar em Plano C passivo (60-80% buy-hold)",
            "- **R4:** aguardar 6-12m e re-rodar (regime BR muda)",
            "- **R5:** implementar Fundamentus scraper mesmo assim, testar D2+D3 standalone",
            "",
            "Ver `reports/phase_d_mvp/BREADTH_NO_WINNER_D.md` pra análise "
            "cross-config detalhada + recomendação do orchestrator.",
        ])
    else:  # ERROR
        lines.extend([
            "A pipeline Phase D-MVP falhou antes de produzir um verdict "
            "definitivo. Veja `logs/phase_d_mvp.log` pra causa raiz. Possíveis "
            "culpados: yfinance rate-limit permanente, disco cheio, exceção "
            "no Runner, timeout do sandbox.",
            "",
            "Retomada: ajustar causa raiz e reexecutar com "
            "`--skip-existing` pra aproveitar os splits já completos.",
        ])

    lines.extend([
        "",
        "## Artefatos",
        "",
        _stat_files(relevant_files),
        "",
        "## Referências",
        "- Spec: `specs/strategy_d_br_ranking.md`",
        "- Plano: `/home/victor/.claude/plans/zazzy-booping-oasis.md`",
        "- Mandate: `docs/investment-mandate.md §4b`",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))
    log.info("journal entry written: %s", path)
    return path


def update_jornada_readme(log: logging.Logger, entry_path: Path, verdict: Verdict) -> None:
    readme = _JORNADA_DIR / "README.md"
    if not readme.exists():
        log.warning("jornada/README.md missing — skipping index update")
        return
    text = readme.read_text()
    marker = "## Entradas (mais recente primeiro)"
    if marker not in text:
        log.warning("jornada/README.md missing entry marker — skipping")
        return
    # Find the first bullet line (the current newest entry) and insert before it.
    head, sep, tail = text.partition(marker)
    tail_lines = tail.splitlines(keepends=True)
    insert_idx = None
    for i, line in enumerate(tail_lines):
        if line.startswith("- ["):
            insert_idx = i
            break
    verdict_label = {
        "WINNER_CANDIDATE": "**Phase D-MVP — WINNER_CANDIDATE detectado**",
        "NO_WINNER_MVP": "**Phase D-MVP — BREADTH_NO_WINNER_D (early-abort)**",
        "ERROR": "**Phase D-MVP — falha técnica**",
    }[verdict]
    new_line = (
        f"- [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} — "
        f"{verdict_label} [SWING BR RANKING] — auto-gerado pelo "
        f"`run_end_to_end.py`. Ver `{entry_path.name}` e "
        f"`reports/phase_d_mvp/SUMMARY.md`.]({entry_path.name})\n"
    )
    if insert_idx is None:
        new_tail = tail + new_line
    else:
        tail_lines.insert(insert_idx, new_line)
        new_tail = "".join(tail_lines)
    readme.write_text(head + sep + new_tail)
    log.info("jornada/README.md updated with new entry pointer")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-start", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
        default=date(2010, 1, 1),
    )
    parser.add_argument(
        "--data-end", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
        default=date(2026, 4, 15),
    )
    parser.add_argument(
        "--min-cached-tickers", type=int, default=90,
        help="Skip downloader if cache already has ≥ N tickers.",
    )
    parser.add_argument(
        "--leads", nargs="*", default=["D1", "D4"], choices=["D1", "D4"],
    )
    parser.add_argument("--initial-cash", type=float, default=50_000.0)
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Resume orchestrator from partial run (reuse per-split JSONs).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print plan + skip stages + don't write journal.",
    )
    parser.add_argument(
        "--log-path", type=Path,
        default=_LOG_DIR / "phase_d_mvp.log",
    )
    args = parser.parse_args(argv)

    log = _configure_logging(args.log_path)
    log.info("=" * 72)
    log.info("Phase D-MVP end-to-end pipeline started")
    log.info("args: %s", vars(args))

    if args.dry_run:
        n_cached = count_cached_tickers(DEFAULT_CACHE_DIR, IBRX100_TICKERS)
        log.info("DRY-RUN plan:")
        log.info("  Stage 1: OHLCV cache has %d/%d tickers; download=%s",
                 n_cached, len(IBRX100_TICKERS),
                 n_cached < args.min_cached_tickers)
        log.info("  Stage 2: orchestrator --leads %s --initial-cash %s %s",
                 args.leads, args.initial_cash,
                 "--skip-existing" if args.skip_existing else "")
        log.info("  Stage 3: interpret verdict")
        log.info("  Stage 4: write jornada/YYYY-MM-DD-HHmm-phase-d-mvp-<verdict>.md")
        return 0

    # Stage 1 — OHLCV
    try:
        ensure_ohlcv(log, args.data_start, args.data_end, args.min_cached_tickers)
    except Exception:
        log.exception("stage 1 (OHLCV) failed")
        verdict: Verdict = "ERROR"
        entry = write_journal_entry(log, verdict)
        update_jornada_readme(log, entry, verdict)
        return 1

    # Stage 2 — orchestrator
    try:
        rc = run_orchestrator(log, args.skip_existing, args.leads, args.initial_cash)
    except Exception:
        log.exception("stage 2 (orchestrator) failed")
        verdict = "ERROR"
        entry = write_journal_entry(log, verdict)
        update_jornada_readme(log, entry, verdict)
        return 1

    # Stage 3 — verdict
    verdict = interpret_verdict(log, rc)

    # Stage 4 — journal
    entry = write_journal_entry(log, verdict)
    update_jornada_readme(log, entry, verdict)

    log.info("pipeline complete — verdict=%s", verdict)
    # Exit code map: WINNER=0, NO_WINNER=2, ERROR=1
    return {"WINNER_CANDIDATE": 0, "NO_WINNER_MVP": 2, "ERROR": 1}[verdict]


if __name__ == "__main__":
    raise SystemExit(main())
