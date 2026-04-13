"""
rename_books.py — One-shot: map current filenames in books/ to canonical slugs.

Moves each recognized PDF to `books/raw/<slug>.pdf` and generates:
  - books/MAPPING.md (human-readable inventory: old_name → slug → title → author)

Also extracts the two companion C++ zips into books/code/ when called with
`--unzip-only` (idempotent).

No LLM calls. Deterministic file mapping based on size+filename hashes.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = ROOT / "books"
RAW_DIR = BOOKS_DIR / "raw"
CODE_DIR = BOOKS_DIR / "code"


@dataclass(frozen=True)
class BookMapping:
    slug: str
    current_filename: str
    title: str
    author: str
    year: int
    notes: str = ""


# Mapping source: /home/victor/.claude/plans/synthetic-snuggling-wren.md
# Each entry: (canonical slug, current filename in books/, title, author, year, notes)
MAPPINGS: tuple[BookMapping, ...] = (
    BookMapping(
        "systematic_trading",
        "Robert Carver - Systematic Trading_ A unique new method for designing trading and investing systems-Harriman House (2015).pdf",
        "Systematic Trading",
        "Robert Carver",
        2015,
    ),
    BookMapping(
        "trading_systems_methods",
        "TSaM.pdf",
        "Trading Systems and Methods (5th ed)",
        "Perry J. Kaufman",
        2013,
    ),
    BookMapping(
        "advances_fin_ml",
        "advances-in-financial-machine-learning-1nbsped-9781119482109-9781119482116-9781119482086.pdf",
        "Advances in Financial Machine Learning",
        "Marcos López de Prado",
        2018,
    ),
    BookMapping(
        "leverage_space",
        "57 . Ralph_Vince.pdf",
        "The Leverage Space Trading Model",
        "Ralph Vince",
        2009,
    ),
    BookMapping(
        "math_money_mgmt",
        "Vince, Ralph - The mathematics of money management.pdf",
        "The Mathematics of Money Management",
        "Ralph Vince",
        1992,
    ),
    BookMapping(
        "rocket_science",
        "ROCKET SCIENCE FOR  TRADER.pdf",
        "Rocket Science for Traders",
        "John F. Ehlers",
        2001,
    ),
    BookMapping(
        "cybernetic_analysis",
        "Ehlers J.F. Cybernetic analysis for stocks and futures (Wiley, 2004)(ISBN 0471463078)(O)(274s)_FT_.pdf",
        "Cybernetic Analysis for Stocks and Futures",
        "John F. Ehlers",
        2004,
        notes="Initial download was front-matter only (L-G-...pdf, 28pp); replaced with full 274pp edition.",
    ),
    BookMapping(
        "cycle_analytics",
        "Cycle Analytics for Traders Advanced Technical Trading Concepts by John F. Ehlers.pdf",
        "Cycle Analytics for Traders",
        "John F. Ehlers",
        2013,
        notes="Initial download was front-matter only (L-G-...pdf, 26pp); replaced with full 252pp edition.",
    ),
    BookMapping(
        "stat_sound_indicators",
        "statistically-sound-machine-learning-for-algorithmic-trading-of-financial-instruments-developing-predictive-model-based-trading-systems-using-tssb_compress.pdf",
        "Statistically Sound Machine Learning for Algorithmic Trading",
        "David Aronson & Timothy Masters",
        2013,
        notes="Aronson+Masters 2013 (TSSB). Substitui Masters 2019 solo; cobre o mesmo território com mais profundidade.",
    ),
    BookMapping(
        "universal_trend_tactics",
        "_OceanofPDF.com_The_Universal_tactics_of_Successful_Trend_Trading_-_Brent_Penfold.pdf",
        "The Universal Tactics of Successful Trend Trading",
        "Brent Penfold",
        2020,
    ),
    BookMapping(
        "stocks_on_the_move",
        "Stocks on the Move Beating the Market with Hedge Fund Momentum Strategies (Andreas F. Clenow) (Z-Library).pdf",
        "Stocks on the Move",
        "Andreas F. Clenow",
        2015,
    ),
    BookMapping(
        "cybernetic_trading",
        "0006120.pdf",
        "Cybernetic Trading Strategies",
        "Murray A. Ruggiero, Jr.",
        1997,
    ),
    BookMapping(
        "testing_tuning",
        "testing-and-tuning-market-trading-systems-algorithms-in-c-9781484241738-1484241738.pdf",
        "Testing and Tuning Market Trading Systems",
        "Timothy Masters",
        2018,
    ),
    BookMapping(
        "numerical_recipes",
        "William H. Press _.pdf",
        "Numerical Recipes in C (2nd ed)",
        "William H. Press et al.",
        1992,
    ),
    BookMapping(
        "data_driven_science",
        "databookRL.pdf",
        "Data-Driven Science and Engineering",
        "Steven L. Brunton & J. Nathan Kutz",
        2021,
    ),
    BookMapping(
        "tech_analysis_patterns",
        "_OceanofPDF.com_Technical_analysis_for_algorithmic_pattern_recognition_-_Prodromos_E_Tsinaslanidis.pdf",
        "Technical Analysis for Algorithmic Pattern Recognition",
        "Prodromos E. Tsinaslanidis",
        2016,
    ),
    BookMapping(
        "regime_change",
        "detecting-regime-change-in-computational-finance-data-science-machine-learning-and-algorithmic-trading-1nbsped-9780367536282_compress.pdf",
        "Detecting Regime Change in Computational Finance",
        "Jun Chen & Edward P. K. Tsang",
        2020,
        notes="Initial download was a 17pp preview; replaced with full 165pp edition (ISBN 978-0-367-53628-2).",
    ),
    BookMapping(
        "trading_on_sentiment",
        "L-G-0007665089-0013629476.pdf",
        "Trading on Sentiment",
        "Richard L. Peterson",
        2016,
    ),
    BookMapping(
        "evidence_based_ta",
        "Evidence-Based Technical Analysis - Applying the Scientific Method and Statistical Inference to Trading Signals 2007.pdf",
        "Evidence-Based Technical Analysis",
        "David Aronson",
        2007,
    ),
    BookMapping(
        "trading_evolved",
        "trading-evolved-anyone-can-build-killer-trading-strategies-in-python-1-independently-published.pdf",
        "Trading Evolved",
        "Andreas F. Clenow",
        2019,
    ),
    BookMapping(
        "ml_for_asset_managers",
        "SSRN-id3558728.pdf",
        "Machine Learning for Asset Managers",
        "Marcos López de Prado",
        2020,
    ),
    BookMapping(
        "ml_for_algo_trading",
        "Machine_Learning_for_Algorithmic_Trading_Predictive.pdf",
        "Machine Learning for Algorithmic Trading",
        "Stefan Jansen",
        2020,
    ),
    # --- 9 new books (ai-trade-library-audit.md §4) ---
    BookMapping(
        "algo_trading_chan",
        "Algorithmic Trading - Winning Strategies and Their Rationale 2013.pdf",
        "Algorithmic Trading: Winning Strategies and Their Rationale",
        "Ernest P. Chan",
        2013,
        notes="Fills L4 (mean reversion / stat-arb); cointegration, Kalman filter, pairs.",
    ),
    BookMapping(
        "fin_time_series_tsay",
        "Analysis of Financial Time Series Third Edition  By Ruey S.Tsay.pdf",
        "Analysis of Financial Time Series (3rd ed)",
        "Ruey S. Tsay",
        2010,
        notes="Fills L2 (econometrics): GARCH/EGARCH, state-space, cointegration, MCMC.",
    ),
    BookMapping(
        "eval_opt_strategies",
        "the-evaluation-and-optimization-of-trading-strategies.pdf",
        "The Evaluation and Optimization of Trading Strategies (2nd ed)",
        "Robert Pardo",
        2008,
        notes="Fills L3 (walk-forward analysis); canonical WFA/robustness profiling reference.",
    ),
    BookMapping(
        "trading_exchanges",
        "trading-and-exchanges-market-microstructure-for-practitioners.pdf",
        "Trading and Exchanges: Market Microstructure for Practitioners",
        "Larry Harris",
        2003,
        notes="Fills L1 (microstructure). PDF is Mar-2002 pre-publication draft; citations must reference the published Oxford UP 2003 edition.",
    ),
    BookMapping(
        "quant_trading_chan",
        "Quantitative Trading How to Build Your Own Algorithmic Trading Business.pdf",
        "Quantitative Trading: How to Build Your Own Algorithmic Trading Business (2nd ed)",
        "Ernest P. Chan",
        2021,
        notes="End-to-end retail quant framework; 2e adds regime change + ML.",
    ),
    BookMapping(
        "volatility_trading",
        "Volatility Trading, + Website-Wiley (2013).pdf",
        "Volatility Trading (2nd ed)",
        "Euan Sinclair",
        2013,
        notes="Fills L5 (vol modeling): realized vs implied, variance premium, Kelly for options.",
    ),
    BookMapping(
        "risk_parity",
        "Risk_Parity_Fundamentals.pdf",
        "Risk Parity Fundamentals",
        "Edward Qian",
        2016,
        notes="Fills L6 (portfolio construction); formal risk budgeting / equal risk contribution.",
    ),
    BookMapping(
        "time_series_hamilton",
        "Hamilton Time Series Analysis.pdf",
        "Time Series Analysis",
        "James D. Hamilton",
        1994,
        notes="Fills L2 complementary: Markov-switching (ch. 22) seminal reference for regime detection.",
    ),
    BookMapping(
        "machine_trading",
        "Machine Trading_ Deploying Computer Algorithms to Conquer The Markets (Ernest Chan 2017).pdf",
        "Machine Trading: Deploying Computer Algorithms to Conquer the Markets",
        "Ernest P. Chan",
        2017,
        notes="Deployment-focused: Bayesian hyperparam opt, factor models, intraday mean reversion.",
    ),
)

# Zips to extract into books/code/
ZIP_MAPPINGS: dict[str, str] = {
    "assessing-and-improving-prediction-and-classification-master.zip": "masters-assessing",
    "testing-and-tuning-market-trading-systems-master.zip": "masters-testing-tuning",
}

# Files we intentionally ignore (duplicates, wrong/incomplete versions).
IGNORED_FILES: tuple[tuple[str, str], ...] = (
    (
        "brent-penfold-the-universal-principles-of-successful-tradingpdf_compress.pdf",
        "Different Penfold book (Universal *Principles* 2010, not Universal *Tactics* 2020). Out of scope.",
    ),
    (
        "pdfcoffee.com_brent-penfold-the-universal-principles-of-successful-tradingpdf-pdf-free.pdf",
        "Exact duplicate of the Penfold 'Principles' file above.",
    ),
    (
        "The Universal Tactics of Successful Trend Trading - 2020 - Penfold - Front Matter.pdf",
        "Front Matter only — superseded by the full PDF mapped to universal_trend_tactics.",
    ),
    (
        "Permutation Tests (Masters 2020).pdf",
        "MISLABELED: this is a Bachelor Thesis by Jaime Turón Rodríguez (Univ. of Seville, 2021), NOT Timothy Masters' 2020 book. Topic is covered by AFML + Testing & Tuning + MCPT C++ code.",
    ),
    (
        "[ALGO-TRADING][Algorithmic Trading & DMA- An introduction to direct access trading strategies].pdf",
        "Johnson 2010 — scan-only PDF with no text layer (pdftotext returns empty). Audit §4.7 documents removal. L1 microstructure covered by Harris (trading_exchanges) instead.",
    ),
)


def move_pdfs(dry_run: bool) -> list[BookMapping]:
    """Move each mapped file to books/raw/<slug>.pdf. Returns the list of mappings
    that were actually moved (skips files already in raw/ and files that don't
    exist). Raises on name collisions or missing files that we can't skip."""
    moved: list[BookMapping] = []
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for m in MAPPINGS:
        src = BOOKS_DIR / m.current_filename
        dst = RAW_DIR / f"{m.slug}.pdf"

        if dst.exists() and not src.exists():
            console.print(f"[dim]skip[/dim]  {m.slug}.pdf already in books/raw/")
            continue

        if not src.exists():
            console.print(
                f"[yellow]WARN[/yellow]  source missing for {m.slug!r}: "
                f"{m.current_filename!r}"
            )
            continue

        if dst.exists():
            console.print(
                f"[yellow]WARN[/yellow]  {dst.name} already exists; leaving {src.name} in place"
            )
            continue

        action = "would move" if dry_run else "moved"
        console.print(f"[green]{action}[/green]  {src.name} → books/raw/{dst.name}")
        if not dry_run:
            shutil.move(src, dst)
        moved.append(m)

    return moved


def extract_zips(dry_run: bool) -> None:
    CODE_DIR.mkdir(parents=True, exist_ok=True)
    for zip_name, dest_subdir in ZIP_MAPPINGS.items():
        src = BOOKS_DIR / zip_name
        dst = CODE_DIR / dest_subdir
        if not src.exists():
            # Maybe already extracted? Check if dst has content.
            if dst.exists() and any(dst.iterdir()):
                console.print(f"[dim]skip[/dim]  {dest_subdir}/ already populated")
                continue
            console.print(f"[yellow]WARN[/yellow]  zip missing: {zip_name}")
            continue

        if dst.exists() and any(dst.iterdir()):
            console.print(f"[dim]skip[/dim]  {dest_subdir}/ already populated")
            continue

        action = "would extract" if dry_run else "extracting"
        console.print(f"[green]{action}[/green]  {zip_name} → books/code/{dest_subdir}/")
        if not dry_run:
            dst.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(src) as zf:
                # Most of these zips have a single top-level folder; strip it so
                # files land directly in books/code/<dest_subdir>/.
                top_dirs = {
                    Path(n).parts[0]
                    for n in zf.namelist()
                    if n and not n.startswith("__MACOSX")
                }
                strip_top = len(top_dirs) == 1

                for member in zf.namelist():
                    if member.endswith("/"):
                        continue
                    if member.startswith("__MACOSX"):
                        continue
                    parts = Path(member).parts
                    if strip_top and len(parts) > 1:
                        out_rel = Path(*parts[1:])
                    else:
                        out_rel = Path(*parts)
                    out_path = dst / out_rel
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src_f, open(out_path, "wb") as dst_f:
                        shutil.copyfileobj(src_f, dst_f)


def write_mapping_md() -> None:
    """Generate books/MAPPING.md — human-readable inventory."""
    out = BOOKS_DIR / "MAPPING.md"
    lines: list[str] = [
        "# Books — Canonical Mapping",
        "",
        "Generated by `scripts/rename_books.py`. Human-readable inventory of the",
        f"{len(MAPPINGS)} books absorbed by the knowledge pipeline, plus ignored files.",
        "",
        "## Active books (books/raw/<slug>.pdf)",
        "",
        "| # | Slug | Title | Author | Year | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for i, m in enumerate(MAPPINGS, start=1):
        notes = m.notes.replace("|", "\\|") if m.notes else ""
        lines.append(f"| {i} | `{m.slug}` | {m.title} | {m.author} | {m.year} | {notes} |")

    lines += [
        "",
        "## Companion C++ code (books/code/)",
        "",
        "| Destination | Source zip | Book |",
        "|---|---|---|",
        "| `books/code/masters-assessing/` | `assessing-and-improving-prediction-and-classification-master.zip` | Masters 2013 (PDF indisponível; código é a fonte primária) |",
        "| `books/code/masters-testing-tuning/` | `testing-and-tuning-market-trading-systems-master.zip` | Masters 2018 (complementa `testing_tuning.pdf`) |",
        "",
        "## Ignored files",
        "",
        "| Filename | Reason |",
        "|---|---|",
    ]
    for fname, reason in IGNORED_FILES:
        lines.append(f"| `{fname}` | {reason} |")
    lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"[green]wrote[/green]  {out.relative_to(ROOT)}")


def print_summary(moved: list[BookMapping]) -> None:
    table = Table(title="Rename summary")
    table.add_column("slug", style="cyan")
    table.add_column("title")
    table.add_column("author", style="dim")
    for m in moved:
        table.add_row(m.slug, m.title, m.author)
    console.print(table)

    total = len(MAPPINGS)
    have = sum(1 for m in MAPPINGS if (RAW_DIR / f"{m.slug}.pdf").exists())
    console.print(
        f"\n[bold]{have}/{total}[/bold] PDFs present in books/raw/. "
        f"{total - have} missing."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would happen without moving files."
    )
    parser.add_argument(
        "--unzip-only",
        action="store_true",
        help="Only extract the companion C++ zips; skip PDF renaming.",
    )
    args = parser.parse_args()

    if not BOOKS_DIR.is_dir():
        console.print(f"[red]ERROR[/red] books/ directory not found at {BOOKS_DIR}")
        return 1

    if args.unzip_only:
        extract_zips(args.dry_run)
        return 0

    moved = move_pdfs(args.dry_run)
    extract_zips(args.dry_run)
    if not args.dry_run:
        write_mapping_md()
    print_summary(moved)
    return 0


if __name__ == "__main__":
    sys.exit(main())
