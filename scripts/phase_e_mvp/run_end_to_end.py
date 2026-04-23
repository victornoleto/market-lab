"""End-to-end Phase E-MVP pipeline (multi-market).

Analogous to ``scripts.phase_d_mvp.run_end_to_end`` but targets the
Strategy E universe (SP500 top-200 + IBrX-100). Reuses the Phase D
``run_end_to_end`` structure: download → orchestrate → verdict →
journal.

Usage::

    .venv/bin/python -m scripts.phase_e_mvp.run_end_to_end \
        [--skip-existing] [--leads D1 D4] [--dry-run]

Exit codes: 0 WINNER / 2 NO_WINNER / 1 ERROR.
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

from ai_trade.backtest.data.yfinance_source import DEFAULT_CACHE_DIR

from scripts.phase_e_mvp.universe import MULTIMARKET_TICKERS

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LOG_DIR = _PROJECT_ROOT / "logs"
_REPORTS_DIR = _PROJECT_ROOT / "reports" / "phase_e_mvp"
_JORNADA_DIR = _PROJECT_ROOT / "jornada"

Verdict = Literal["WINNER_CANDIDATE", "NO_WINNER_MVP", "ERROR"]


def _configure_logging(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("phase_e_mvp.e2e")
    log.setLevel(logging.INFO)
    log.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    stdout_h = logging.StreamHandler(sys.stdout)
    stdout_h.setFormatter(fmt)
    log.addHandler(stdout_h)
    file_h = logging.FileHandler(log_path, mode="a")
    file_h.setFormatter(fmt)
    log.addHandler(file_h)
    return log


def count_cached(tickers: list[str]) -> int:
    return sum(1 for t in tickers if (DEFAULT_CACHE_DIR / f"{t}.parquet").exists())


def ensure_ohlcv(log, start: date, end: date, min_cached: int):
    n = count_cached(MULTIMARKET_TICKERS)
    log.info("OHLCV cache: %d/%d tickers", n, len(MULTIMARKET_TICKERS))
    if n >= min_cached:
        log.info("cache sufficient — skipping download")
        return
    log.info("launching Phase E downloader")
    cmd = [
        sys.executable, "-m", "scripts.phase_e_mvp.download",
        "--start", start.isoformat(), "--end", end.isoformat(),
        "--log-path", str(_LOG_DIR / "download_phase_e.log"),
    ]
    log.info("exec: %s", " ".join(cmd))
    r = subprocess.run(cmd, check=False, cwd=_PROJECT_ROOT)
    if r.returncode != 0:
        raise RuntimeError(f"Phase E downloader failed rc={r.returncode}")
    n_after = count_cached(MULTIMARKET_TICKERS)
    log.info("post-download cache: %d/%d", n_after, len(MULTIMARKET_TICKERS))


def run_orchestrator(log, skip_existing: bool, leads, initial_cash: float) -> int:
    cmd = [
        sys.executable, "-m", "scripts.phase_e_mvp.orchestrator",
        "--initial-cash", str(initial_cash), "--leads", *leads,
    ]
    if skip_existing:
        cmd.append("--skip-existing")
    log.info("exec: %s", " ".join(cmd))
    r = subprocess.run(cmd, check=False, cwd=_PROJECT_ROOT)
    log.info("orchestrator rc=%d", r.returncode)
    return r.returncode


def interpret(log, rc: int) -> Verdict:
    summary = _REPORTS_DIR / "SUMMARY.md"
    dsr_path = _REPORTS_DIR / "dsr_results.json"
    if rc == 2:
        return "NO_WINNER_MVP"
    if rc != 0 or not summary.exists():
        return "ERROR"
    if dsr_path.exists():
        with open(dsr_path) as f:
            d = json.load(f)
        n_pass = sum(1 for v in d.values() if v.get("p_value", 1) < 0.1)
        log.info("%d configs pass DSR p<0.1", n_pass)
    return "WINNER_CANDIDATE"


def _now_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")


def write_journal(log, verdict: Verdict) -> Path:
    slug = _now_slug()
    fname = f"{slug}-phase-e-mvp-{verdict.lower().replace('_', '-')}.md"
    path = _JORNADA_DIR / fname
    titles = {
        "WINNER_CANDIDATE": "Phase E-MVP — WINNER candidato detectado (multi-market)",
        "NO_WINNER_MVP": "Phase E-MVP — BREADTH_NO_WINNER_E (multi-market)",
        "ERROR": "Phase E-MVP — falha técnica",
    }
    lines = [
        f"# {titles[verdict]}",
        "",
        f"**Data:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Verdict:** `{verdict}`",
        f"**Universo:** SP500 top-200 + IBrX-100 (~300 tickers combinados)",
        "",
    ]

    if verdict == "WINNER_CANDIDATE":
        lines.extend([
            "## Contexto",
            "",
            "Pelo menos **1 config em Strategy E passa o filtro mínimo** (PBO<0.5 AND "
            "DSR p<0.1) no universo multi-market. Primeiro winner-candidate do projeto "
            "em 72 tentativas honest (71 FAIL anteriores + Strategy E).",
            "",
            "Ver `reports/phase_e_mvp/SUMMARY.md` pra configs específicas.",
            "",
            "**Próximos passos (decisão do usuário):**",
            "1. Revisar winner-config no SUMMARY.",
            "2. Rodar gates pesados da Fase E-gate: cross-lib (bt/vectorbt/backtrader), "
            "bootstrap 99.9% CI, cost×2 stress, sector/liquidity stress.",
            "3. Se passar todos 13 gates: redigir mandate override formal pra "
            "Strategy E slot, escolher broker (Inter Global for US + Clear/Rico for BR), "
            "draft Fase E-promotion paper-trade plan.",
        ])
    elif verdict == "NO_WINNER_MVP":
        lines.extend([
            "## Contexto",
            "",
            "Strategy E em universo multi-market falhou pelo mesmo critério que "
            "Strategy D: 0 configs passam o filtro mínimo. Isso é o **72º FAIL "
            "consecutivo** do projeto.",
            "",
            "**Interpretação honesta:** com 33 livros absorvidos + engine cross-lib "
            "validada + gates rigorosos + 4 famílias de signal testadas em 2 mercados "
            "× 3 janelas temporais × ~40 configs cada, o resultado é consistente com a "
            "literatura séria (Harvey & Liu 2015 JOIM: 80%+ dos factors publicados "
            "falham multiple-testing). Retail com capital limitado enfrenta:",
            "- Spreads e comissões absorvendo ≥ 50% do edge teórico",
            "- Universo inacessível pra scale (Renaissance opera 10,000+ tickers "
            "globalmente com alt-data proprietária)",
            "- Regimes 2020+ adversos (COVID + tariff war + tech-hype switching)",
            "",
            "**Recomendação oficial: consolidar Plano C passivo 60-80% factor-tilted** "
            "(já verificado em `portfolio-aposentadoria.md`) e parar de caçar active "
            "alpha. Mathematically optimal pra retail com capital < $1M.",
            "",
            "Strategy A, B, D permanecem como slots abertos no mandate — se futura "
            "literatura ou regime shift sugerir novo signal, a infra está pronta pra "
            "testar com CI/CD de gates honest.",
        ])
    else:
        lines.extend([
            "## Contexto",
            "",
            "Pipeline Phase E-MVP falhou antes de produzir verdict. Ver "
            "`logs/phase_e_mvp.log`. Retomada via `--skip-existing`.",
        ])

    lines.extend([
        "",
        "## Artefatos",
        "",
        f"- `reports/phase_e_mvp/SUMMARY.md`",
        f"- `reports/phase_e_mvp/dsr_results.json`",
        f"- `reports/phase_e_mvp/oos_returns_matrix.npz`",
        f"- `reports/phase_e_mvp/<slug>/` per-config (IS/OOS/FWD json + equity parquet)",
        "",
        "## Referências",
        "- Spec: `specs/strategy_d_br_ranking.md` (E reusa signals de D)",
        "- Plano: `/home/victor/.claude/plans/zazzy-booping-oasis.md`",
        "- Mandate override Strategy E: "
        "`docs/mandate_overrides/2026-04-23-strategy-e-multimarket.md` (PENDING)",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))
    log.info("journal entry: %s", path)
    return path


def update_readme(log, entry_path: Path, verdict: Verdict):
    readme = _JORNADA_DIR / "README.md"
    if not readme.exists():
        return
    text = readme.read_text()
    marker = "## Entradas (mais recente primeiro)"
    if marker not in text:
        return
    head, sep, tail = text.partition(marker)
    tail_lines = tail.splitlines(keepends=True)
    insert_idx = next(
        (i for i, ln in enumerate(tail_lines) if ln.startswith("- [")),
        None,
    )
    labels = {
        "WINNER_CANDIDATE": "**Phase E-MVP — WINNER candidato detectado (multi-market)**",
        "NO_WINNER_MVP": "**Phase E-MVP — BREADTH_NO_WINNER_E (multi-market)**",
        "ERROR": "**Phase E-MVP — falha técnica**",
    }
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    new_line = (
        f"- [{ts} — {labels[verdict]} [MULTI-MARKET] — auto-gerado pelo "
        f"`run_end_to_end.py`. Ver `{entry_path.name}` e "
        f"`reports/phase_e_mvp/SUMMARY.md`.]({entry_path.name})\n"
    )
    if insert_idx is None:
        new_tail = tail + new_line
    else:
        tail_lines.insert(insert_idx, new_line)
        new_tail = "".join(tail_lines)
    readme.write_text(head + sep + new_tail)
    log.info("jornada/README.md updated")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-start", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                        default=date(2010, 1, 1))
    parser.add_argument("--data-end", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                        default=date(2026, 4, 15))
    parser.add_argument("--min-cached-tickers", type=int, default=270)
    parser.add_argument("--leads", nargs="*", default=["D1", "D4"],
                        choices=["D1", "D4"])
    parser.add_argument("--initial-cash", type=float, default=50_000.0)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log-path", type=Path, default=_LOG_DIR / "phase_e_mvp.log")
    args = parser.parse_args(argv)

    log = _configure_logging(args.log_path)
    log.info("=" * 72)
    log.info("Phase E-MVP end-to-end pipeline started")
    log.info("args: %s", vars(args))

    if args.dry_run:
        n = count_cached(MULTIMARKET_TICKERS)
        log.info("DRY-RUN: cache %d/%d; download=%s",
                 n, len(MULTIMARKET_TICKERS), n < args.min_cached_tickers)
        return 0

    try:
        ensure_ohlcv(log, args.data_start, args.data_end, args.min_cached_tickers)
    except Exception:
        log.exception("stage 1 failed")
        verdict: Verdict = "ERROR"
        path = write_journal(log, verdict)
        update_readme(log, path, verdict)
        return 1

    try:
        rc = run_orchestrator(log, args.skip_existing, args.leads, args.initial_cash)
    except Exception:
        log.exception("stage 2 failed")
        verdict = "ERROR"
        path = write_journal(log, verdict)
        update_readme(log, path, verdict)
        return 1

    verdict = interpret(log, rc)
    path = write_journal(log, verdict)
    update_readme(log, path, verdict)
    log.info("pipeline complete — verdict=%s", verdict)
    return {"WINNER_CANDIDATE": 0, "NO_WINNER_MVP": 2, "ERROR": 1}[verdict]


if __name__ == "__main__":
    raise SystemExit(main())
