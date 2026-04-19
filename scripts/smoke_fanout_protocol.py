"""End-to-end smoke test for the fan-out sweep protocol.

Runs in a throwaway sandbox under ``/tmp``. Creates a dummy phase
("smoke") with one lead (SX) having 2 tickers × 2 configs, then
simulates the four iters the self-improve loop would produce:

    iter 1 — bootstrap registry.json
    iter 2 — sweep first ticker
    iter 3 — sweep second ticker
    iter 4 — aggregator (AGGREGATE.md + jornada)

Each iter makes its own atomic git commit, mimicking what
``scripts/self_improve_loop.sh`` does after each agent turn. The script
asserts the full state-machine trajectory and writes a short report
to stdout.

Usage:
    python scripts/smoke_fanout_protocol.py

This does NOT invoke the claude CLI — the LLM-driven E2E is exercised
by the first 4 iters of the Phase 3.5a relaunch (Task 5). This script
covers the infra contract (registry helpers + per-iter file/commit
sequence) deterministically.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from ai_trade.backtest.sweeps.registry import (  # noqa: E402
    advance_status,
    append_done,
    atomic_write_registry,
    load_registry,
    new_registry,
    pop_pending,
)


LEAD_SLUG = "sx_smoke_lead"
PHASE = "smoke"
CONFIGS = [
    {"name": "cfg_a", "type": "noop", "param": 1},
    {"name": "cfg_b", "type": "noop", "param": 2},
]
TICKERS = ["AAAA", "BBBB"]


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def git(sandbox: Path, *args: str) -> str:
    return run(["git", *args], cwd=sandbox)


def git_commit(sandbox: Path, message: str) -> str:
    git(sandbox, "add", "-A")
    # --no-gpg-sign mirrors the real loop script; author env avoids
    # hard-failing on machines without a global git config.
    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", "smoke-fanout")
    env.setdefault("GIT_AUTHOR_EMAIL", "smoke@fanout.local")
    env.setdefault("GIT_COMMITTER_NAME", env["GIT_AUTHOR_NAME"])
    env.setdefault("GIT_COMMITTER_EMAIL", env["GIT_AUTHOR_EMAIL"])
    subprocess.run(
        ["git", "commit", "--no-gpg-sign", "-m", message],
        cwd=sandbox,
        check=True,
        env=env,
        capture_output=True,
    )
    return git(sandbox, "rev-parse", "HEAD")


def _per_ticker_files(lead_dir: Path, ticker: str, best_sharpe: float) -> Dict[str, str]:
    md = f"""# {ticker} — SX smoke (iter N)

**Best config:** `cfg_a` — NO PASS (smoke stub)

## Standard report — cfg_a (best)

Sharpe OOS                 {best_sharpe:.2f}
(stub — infra smoke, not a real backtest)
"""
    js: Dict[str, Any] = {
        "ticker": ticker,
        "frequency": "daily",
        "window": {"start": "2020-01-01", "end": "2026-04-17", "n_bars": 1000},
        "configs": [
            {
                "name": "cfg_a",
                "metrics_oos": {"sharpe": best_sharpe, "cagr": 0.05, "maxdd": -0.10},
                "gates": {"any_pass": False, "why_fail": "smoke stub"},
            },
            {
                "name": "cfg_b",
                "metrics_oos": {"sharpe": best_sharpe - 0.1, "cagr": 0.04, "maxdd": -0.12},
                "gates": {"any_pass": False, "why_fail": "smoke stub"},
            },
        ],
        "best_config": "cfg_a",
        "any_pass_5gate": False,
    }
    md_path = lead_dir / f"{ticker}.md"
    json_path = lead_dir / f"{ticker}.json"
    md_path.write_text(md, encoding="utf-8")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(js, f, indent=2)
    return {
        "result_file_md": str(md_path.relative_to(lead_dir.parent.parent.parent)),
        "result_file_json": str(json_path.relative_to(lead_dir.parent.parent.parent)),
    }


def iter_bootstrap(sandbox: Path, lead_dir: Path) -> None:
    lead_dir.mkdir(parents=True, exist_ok=True)
    reg = new_registry(
        phase=PHASE,
        lead_id="SX",
        lead_slug=LEAD_SLUG,
        lead_title="Smoke lead — protocol E2E",
        configs=CONFIGS,
        tickers_pending=TICKERS,
        citations_seed=["smoke_doc, p.1"],
    )
    atomic_write_registry(lead_dir / "registry.json", reg)
    # The shell loop's memory.md bump is simulated with a one-line file.
    (sandbox / "memory.md").write_text(
        "iteration: 1\nactive_lead_registry: reports/smoke/sx_smoke_lead/registry.json\n",
        encoding="utf-8",
    )


def iter_sweep(sandbox: Path, lead_dir: Path, expected_ticker: str, iter_num: int) -> None:
    reg = load_registry(lead_dir / "registry.json")
    ticker, reg = pop_pending(reg)
    assert ticker == expected_ticker, f"expected {expected_ticker}, popped {ticker}"
    paths = _per_ticker_files(lead_dir, ticker, best_sharpe=0.40 + 0.02 * iter_num)
    summary = {
        "ticker": ticker,
        "frequency": "daily",
        "window_start": "2020-01-01",
        "window_end": "2026-04-17",
        "iter": iter_num,
        "n_configs_tested": len(CONFIGS),
        "best_config": "cfg_a",
        "best_sharpe_oos": 0.40 + 0.02 * iter_num,
        "best_cagr": 0.05,
        "best_maxdd": -0.10,
        "any_pass_5gate": False,
        "median_hold_days": 2.0,
        **paths,
    }
    reg = append_done(reg, summary)
    reg = advance_status(reg)
    atomic_write_registry(lead_dir / "registry.json", reg)
    (sandbox / "memory.md").write_text(
        f"iteration: {iter_num}\n"
        f"active_lead_registry: reports/smoke/sx_smoke_lead/registry.json\n"
        f"history: iter {iter_num} — SX sweep {ticker}\n",
        encoding="utf-8",
    )


def iter_aggregate(sandbox: Path, lead_dir: Path, iter_num: int) -> None:
    reg = load_registry(lead_dir / "registry.json")
    assert reg["status"] == "aggregating", f"expected status=aggregating, got {reg['status']}"
    assert reg["tickers_pending"] == []
    assert len(reg["tickers_done"]) == len(TICKERS)

    aggregate_md_path = lead_dir / "AGGREGATE.md"
    aggregate_md_path.write_text(
        "# Lead SX — Smoke (aggregate)\n\n"
        f"Tested: {len(TICKERS)} tickers × {len(CONFIGS)} configs.\n"
        "Status: DEAD END (0/2 PASS) — this is a smoke, not a real result.\n",
        encoding="utf-8",
    )
    jornada_dir = sandbox / "jornada"
    jornada_dir.mkdir(exist_ok=True)
    jornada_path = jornada_dir / f"2026-04-18-phase-{PHASE}-SX-DEAD.md"
    jornada_path.write_text(
        "# [SHORT-HOLD CFD] Smoke lead SX — DEAD END\n\n"
        "Infra smoke; no real backtest.\n",
        encoding="utf-8",
    )

    reg["status"] = "done"
    reg["aggregation_iter"] = iter_num
    reg["aggregate_file_md"] = str(aggregate_md_path.relative_to(sandbox))
    reg["aggregate_jornada"] = str(jornada_path.relative_to(sandbox))
    atomic_write_registry(lead_dir / "registry.json", reg)

    (sandbox / "memory.md").write_text(
        f"iteration: {iter_num}\n"
        "active_lead_registry: null\n"
        f"history: iter {iter_num} — SX aggregator DEAD END\n",
        encoding="utf-8",
    )


def main() -> int:
    sandbox = Path(tempfile.mkdtemp(prefix="ai_trade_smoke_fanout_"))
    print(f"[smoke] sandbox: {sandbox}")
    try:
        git(sandbox, "init", "-q", "-b", "smoke")
        # Seed repo with a commit so HEAD~N is defined later.
        (sandbox / ".gitkeep").write_text("", encoding="utf-8")
        git_commit(sandbox, "chore: seed smoke sandbox")

        lead_dir = sandbox / "reports" / PHASE / LEAD_SLUG

        iter_bootstrap(sandbox, lead_dir)
        c1 = git_commit(sandbox, "self-improve: iter 1 — SX bootstrap registry")

        iter_sweep(sandbox, lead_dir, TICKERS[0], iter_num=2)
        c2 = git_commit(sandbox, f"self-improve: iter 2 — SX sweep {TICKERS[0]}")

        iter_sweep(sandbox, lead_dir, TICKERS[1], iter_num=3)
        c3 = git_commit(sandbox, f"self-improve: iter 3 — SX sweep {TICKERS[1]}")

        iter_aggregate(sandbox, lead_dir, iter_num=4)
        c4 = git_commit(sandbox, "self-improve: iter 4 — SX aggregator DEAD")

        # Verification
        log = git(sandbox, "log", "--oneline")
        print("[smoke] git log:")
        for line in log.splitlines():
            print(f"    {line}")
        commits_added = len(log.splitlines()) - 1  # minus the seed commit
        assert commits_added == 4, f"expected 4 atomic commits, got {commits_added}"

        reg = load_registry(lead_dir / "registry.json")
        assert reg["status"] == "done"
        assert reg["aggregate_file_md"]
        assert reg["aggregate_jornada"]
        assert len(reg["tickers_done"]) == len(TICKERS)
        assert reg["tickers_pending"] == []

        assert (lead_dir / "AGGREGATE.md").exists()
        assert (lead_dir / f"{TICKERS[0]}.md").exists()
        assert (lead_dir / f"{TICKERS[0]}.json").exists()
        assert (lead_dir / f"{TICKERS[1]}.md").exists()
        assert (lead_dir / f"{TICKERS[1]}.json").exists()

        print("[smoke] invariants OK:")
        print("    - 4 atomic commits, one per iter")
        print(f"    - registry.status: {reg['status']}")
        print(f"    - tickers_done: {[e['ticker'] for e in reg['tickers_done']]}")
        print(f"    - aggregate_file_md: {reg['aggregate_file_md']}")
        print(f"    - commits: {c1[:7]} {c2[:7]} {c3[:7]} {c4[:7]}")
        print("[smoke] PASS")
        return 0
    except Exception as exc:
        print(f"[smoke] FAIL: {exc}", file=sys.stderr)
        raise
    finally:
        # Leave the sandbox on disk for inspection if requested; we only
        # clean up on success to aid debugging of future regressions.
        if os.environ.get("SMOKE_KEEP"):
            print(f"[smoke] sandbox retained at {sandbox} (SMOKE_KEEP set)")
        else:
            shutil.rmtree(sandbox, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
