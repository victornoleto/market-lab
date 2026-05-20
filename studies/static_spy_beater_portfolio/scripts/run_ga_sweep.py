"""Run a configurable GA sweep across universes, fitnesses and seeds.

This is orchestration only. Each child GA run remains discovery-only and writes its
own `results.json`; downstream validation must still account for the full search
breadth `[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.static_spy_beater_portfolio.scripts.universe import UNIVERSES  # noqa: E402


ALL_FITNESSES = [
    "cagr_robust",
    "sharpe_robust",
    "sortino_robust",
    "calmar_robust",
    "relative_wealth_spy",
    "relative_wealth_qqq",
    "core_relative_wealth_dominance",
    "balanced_spy_beater",
    "spy_beater_mdd_guard",
    "spy_beater_calmar_guard",
    "spy_beater_consistency_guard",
    "spy_beater_p10_mdd_guard",
    "balanced_dual_beater",
    "min_regret",
]


def parse_csv(value: str, allowed: list[str], label: str) -> list[str]:
    if value == "all":
        return allowed
    items = [item.strip() for item in value.split(",") if item.strip()]
    unknown = [item for item in items if item not in allowed]
    if unknown:
        raise SystemExit(f"unknown {label}: {unknown}; allowed: {allowed}")
    return items


def run_and_log(command: list[str], log_path: Path, *, dry_run: bool) -> int:
    printable = " ".join(command)
    if dry_run:
        print(printable)
        return 0
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"\n$ {printable}\n")
        log.flush()
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        try:
            assert process.stdout is not None
            for line in process.stdout:
                print(line, end="")
                log.write(line)
            return process.wait()
        except KeyboardInterrupt:
            log.write("\nKeyboardInterrupt: terminating child process\n")
            log.flush()
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                log.write("KeyboardInterrupt: killing child process after timeout\n")
                process.kill()
                process.wait()
            raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universes", default="all", help="Comma list or 'all'.")
    parser.add_argument("--fitnesses", default="all", help="Comma list or 'all'.")
    parser.add_argument("--seeds", default="20260518", help="Comma-separated integer seeds.")
    parser.add_argument("--population", type=int, default=80)
    parser.add_argument("--generations", type=int, default=80)
    parser.add_argument("--elite-size", type=int, default=10)
    parser.add_argument("--mutation-rate", type=float, default=0.15)
    parser.add_argument("--max-assets", type=int, default=15)
    parser.add_argument("--rolling-step", type=int, default=63)
    parser.add_argument("--finalist-exact", type=int, default=50)
    parser.add_argument("--patience", type=int, default=15)
    parser.add_argument("--min-delta", type=float, default=1e-6)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--log-every", type=int, default=10)
    parser.add_argument("--eval-log-every", type=int, default=500)
    parser.add_argument("--output-dir", type=Path, default=Path("studies/static_spy_beater_portfolio/results/ga"))
    parser.add_argument("--log-dir", type=Path, default=Path("logs/static_spy_beater_portfolio"))
    parser.add_argument("--no-fast-discovery", action="store_true")
    parser.add_argument("--skip-existing", action="store_true", default=True)
    parser.add_argument("--overwrite", action="store_true", help="Run even if results.json already exists.")
    parser.add_argument("--no-report", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    universes = parse_csv(args.universes, sorted(UNIVERSES), "universes")
    fitnesses = parse_csv(args.fitnesses, ALL_FITNESSES, "fitnesses")
    seeds = [int(seed.strip()) for seed in args.seeds.split(",") if seed.strip()]
    skip_existing = args.skip_existing and not args.overwrite

    total = len(universes) * len(fitnesses) * len(seeds)
    completed = 0
    failed: list[str] = []
    print(f"sweep_start runs={total} universes={universes} fitnesses={fitnesses} seeds={seeds}")

    for seed in seeds:
        for universe in universes:
            for fitness in fitnesses:
                run_name = f"{universe}_{fitness}_seed{seed}"
                run_dir = args.output_dir / run_name
                log_path = args.log_dir / f"{run_name}.log"
                if skip_existing and (run_dir / "results.json").exists():
                    print(f"skip_existing run={run_name}")
                    continue
                print(f"=== START {datetime.now().isoformat()} {run_name} ===")
                command = [
                    sys.executable,
                    "-m",
                    "studies.static_spy_beater_portfolio.scripts.run_ga",
                    "--universe",
                    universe,
                    "--fitness",
                    fitness,
                    "--population",
                    str(args.population),
                    "--generations",
                    str(args.generations),
                    "--elite-size",
                    str(args.elite_size),
                    "--mutation-rate",
                    str(args.mutation_rate),
                    "--max-assets",
                    str(args.max_assets),
                    "--rolling-step",
                    str(args.rolling_step),
                    "--finalist-exact",
                    str(args.finalist_exact),
                    "--patience",
                    str(args.patience),
                    "--min-delta",
                    str(args.min_delta),
                    "--jobs",
                    str(args.jobs),
                    "--seed",
                    str(seed),
                    "--log-every",
                    str(args.log_every),
                    "--eval-log-every",
                    str(args.eval_log_every),
                    "--output-dir",
                    str(args.output_dir),
                ]
                if not args.no_fast_discovery:
                    command.append("--fast-discovery")
                rc = run_and_log(command, log_path, dry_run=args.dry_run)
                if rc != 0:
                    failed.append(run_name)
                    print(f"run_failed run={run_name} rc={rc}")
                    continue
                if not args.no_report:
                    report_cmd = [
                        sys.executable,
                        "studies/static_spy_beater_portfolio/scripts/generate_report.py",
                        "--run-dir",
                        str(run_dir),
                    ]
                    rc = run_and_log(report_cmd, log_path, dry_run=args.dry_run)
                    if rc != 0:
                        failed.append(f"{run_name}:report")
                        print(f"report_failed run={run_name} rc={rc}")
                        continue
                completed += 1
                print(f"=== END {datetime.now().isoformat()} {run_name} ===")
    print(f"sweep_done completed={completed} failed={len(failed)} failed_runs={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
