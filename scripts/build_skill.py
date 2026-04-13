"""
build_skill.py — Aggregate validated book summaries into knowledge/ Skill.

Reads books/summaries/*.md, validates them via validate_summary, then produces:
  knowledge/SKILL.md                  (master frontmatter + index + inviolable rules)
  knowledge/books/<slug>.md           (per-book, copied from summaries/)
  knowledge/strategies/*.md           (thematic aggregations: momentum, cycles, ...)
  knowledge/indicators/*.md           (ehlers_indicators, custom_momentum, regime_hmm)
  knowledge/validation/*.md           (cpcv, permutation, deflated_sharpe, walk_forward)

Thematic aggregations reference the original summary sections and include
pointers to companion C++ code in books/code/ where relevant.

No LLM calls. Deterministic.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

# Reuse the validator
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_summary import validate as validate_summary  # noqa: E402

console = Console()

ROOT = Path(__file__).resolve().parent.parent
SUMMARIES_DIR = ROOT / "books" / "summaries"
KNOWLEDGE_DIR = ROOT / "knowledge"
BOOKS_OUT = KNOWLEDGE_DIR / "books"
STRATEGIES_OUT = KNOWLEDGE_DIR / "strategies"
INDICATORS_OUT = KNOWLEDGE_DIR / "indicators"
VALIDATION_OUT = KNOWLEDGE_DIR / "validation"
CODE_DIR = ROOT / "books" / "code"


@dataclass(frozen=True)
class ThematicMap:
    """Mapping from a theme file to the source summaries and C++ code refs."""
    filename: str                  # relative to category dir (e.g., "momentum.md")
    category: str                  # "strategies" | "indicators" | "validation"
    title: str                     # human-readable title
    description: str               # 1-line summary of the theme
    source_slugs: tuple[str, ...]  # books that cover this theme
    code_refs: tuple[str, ...] = ()  # optional links to books/code/ paths


# Theme → sources mapping (from the approved plan, seção 6.5 de TRADING_SYSTEM_PLAN.md)
THEMES: tuple[ThematicMap, ...] = (
    # Strategies
    ThematicMap(
        filename="anti_overfitting.md",
        category="strategies",
        title="Anti-Overfitting Framework",
        description="Práticas obrigatórias para evitar que estratégias passem em backtest mas falhem em live.",
        source_slugs=(
            "advances_fin_ml",
            "testing_tuning",
            "stat_sound_indicators",
            "evidence_based_ta",
            "ml_for_asset_managers",
        ),
    ),
    ThematicMap(
        filename="momentum.md",
        category="strategies",
        title="Momentum Strategies",
        description="Trend-following e momentum cross-sectional, com filtro de regime.",
        source_slugs=(
            "systematic_trading",
            "stocks_on_the_move",
            "trading_evolved",
            "universal_trend_tactics",
        ),
    ),
    ThematicMap(
        filename="cycle_detection.md",
        category="strategies",
        title="Cycle Detection (DSP-based)",
        description="Indicadores de Ehlers baseados em processamento de sinais para detectar ciclos dominantes.",
        source_slugs=(
            "rocket_science",
            "cybernetic_analysis",
            "cycle_analytics",
            "cybernetic_trading",
        ),
    ),
    ThematicMap(
        filename="regime_change.md",
        category="strategies",
        title="Regime Detection",
        description="HMM e outros métodos para identificar bull/bear/sideways e trocar estratégia dinamicamente.",
        source_slugs=(
            "regime_change",
            "trading_on_sentiment",
            "data_driven_science",
        ),
    ),
    ThematicMap(
        filename="money_management.md",
        category="strategies",
        title="Money Management & Position Sizing",
        description="Kelly, fractional Kelly, optimal f, risk of ruin — sizing sob incerteza.",
        source_slugs=(
            "math_money_mgmt",
            "leverage_space",
            "systematic_trading",
        ),
    ),

    # Indicators
    ThematicMap(
        filename="ehlers_indicators.md",
        category="indicators",
        title="Ehlers Indicators (DSP)",
        description="MAMA, Cyber Cycle, Fisher Transform, Hilbert Transform — todos com fundamentação em DSP.",
        source_slugs=(
            "rocket_science",
            "cybernetic_analysis",
            "cycle_analytics",
        ),
    ),
    ThematicMap(
        filename="custom_momentum.md",
        category="indicators",
        title="Custom Momentum Indicators",
        description="Ranking de momentum relativo à la Clenow, com ATR-based sizing.",
        source_slugs=(
            "stocks_on_the_move",
            "trading_evolved",
            "systematic_trading",
        ),
    ),
    ThematicMap(
        filename="regime_hmm.md",
        category="indicators",
        title="Hidden Markov Models for Regime",
        description="HMM como classificador de regime (bull, bear, high-vol, low-vol).",
        source_slugs=(
            "regime_change",
            "data_driven_science",
            "ml_for_algo_trading",
        ),
    ),

    # Validation
    ThematicMap(
        filename="cpcv.md",
        category="validation",
        title="Combinatorial Purged Cross-Validation (CPCV)",
        description="Validação cruzada adaptada para séries temporais financeiras, com purging e embargo.",
        source_slugs=(
            "advances_fin_ml",
            "ml_for_asset_managers",
        ),
        code_refs=(
            "books/code/masters-testing-tuning/CSCV_MKT/CSCV.CPP",
            "books/code/masters-testing-tuning/CSCV_MKT/CSCV_CORE.CPP",
        ),
    ),
    ThematicMap(
        filename="permutation.md",
        category="validation",
        title="Permutation & Monte Carlo Tests",
        description="Testes de permutação para validar que edge é estatisticamente significativo (não sorte).",
        source_slugs=(
            "advances_fin_ml",
            "testing_tuning",
            "stat_sound_indicators",
            "evidence_based_ta",
        ),
        code_refs=(
            "books/code/masters-testing-tuning/MCPT_BARS/MCPT_BARS.CPP",
            "books/code/masters-testing-tuning/MCPT_TRN/MCPT_TRN.CPP",
            "books/code/masters-assessing/BOOT_P_1.CPP",
            "books/code/masters-assessing/BOOT_P_2.CPP",
        ),
    ),
    ThematicMap(
        filename="deflated_sharpe.md",
        category="validation",
        title="Deflated Sharpe Ratio (DSR)",
        description="Correção do Sharpe observado pelo número de estratégias testadas — protege contra selection bias.",
        source_slugs=(
            "advances_fin_ml",
            "ml_for_asset_managers",
        ),
    ),
    ThematicMap(
        filename="walk_forward.md",
        category="validation",
        title="Walk-Forward Analysis",
        description="Treino/teste deslizante — simula operação real com re-otimização periódica.",
        source_slugs=(
            "testing_tuning",
            "stat_sound_indicators",
            "trading_systems_methods",
        ),
        code_refs=(
            "books/code/masters-testing-tuning/DRAWDOWN/DRAWDOWN.CPP",
        ),
    ),
)


# Book metadata (for the index in SKILL.md)
@dataclass(frozen=True)
class BookEntry:
    slug: str
    tier: str  # "S" | "A" | "B" | "C"
    short_desc: str


BOOK_INDEX: tuple[BookEntry, ...] = (
    BookEntry("advances_fin_ml", "S", "Framework anti-overfit completo; CPCV, meta-labeling, DSR."),
    BookEntry("systematic_trading", "S", "Parcimônia + position sizing robusto; design de sistemas."),
    BookEntry("trading_systems_methods", "S", "Referência enciclopédica de métodos clássicos."),
    BookEntry("testing_tuning", "S", "Validação estatística prática em C++."),
    BookEntry("stocks_on_the_move", "S", "Momentum com 2 parâmetros — baseline."),
    BookEntry("rocket_science", "A", "DSP para trading; Hilbert transform, MAMA."),
    BookEntry("cybernetic_analysis", "A", "Continuação DSP; Fisher transform, Cyber Cycle."),
    BookEntry("cycle_analytics", "A", "Ciclos adaptativos — últimos refinements de Ehlers."),
    BookEntry("math_money_mgmt", "A", "Optimal f, risk of ruin, Kelly adaptado."),
    BookEntry("trading_evolved", "A", "Sistemas em Python — ponte direta para o stack."),
    BookEntry("ml_for_algo_trading", "A", "Guia pragmático ML + Python (Jansen)."),
    BookEntry("stat_sound_indicators", "B", "Aronson+Masters TSSB; rigor em indicadores."),
    BookEntry("evidence_based_ta", "B", "Base estatística de Aronson; vies de data mining."),
    BookEntry("ml_for_asset_managers", "B", "AFML condensado para portfolio management."),
    BookEntry("leverage_space", "B", "Sizing multi-asset — extensão Kelly para portfolios."),
    BookEntry("regime_change", "B", "HMM + regime change em finanças computacionais."),
    BookEntry("cybernetic_trading", "C", "Intermarket + NN (Ruggiero 1997)."),
    BookEntry("numerical_recipes", "C", "Referência numérica (SVD, FFT, otimização)."),
    BookEntry("data_driven_science", "C", "Brunton & Kutz — PCA, SVD, dynamical systems."),
    BookEntry("tech_analysis_patterns", "C", "Padrões de TA tratados algoritmicamente."),
    BookEntry("trading_on_sentiment", "C", "Filtros de sentimento como complemento."),
    BookEntry("universal_trend_tactics", "C", "Penfold — táticas de trend trading."),
)


def extract_section(md_text: str, section_name: str) -> str | None:
    """Extract the content of a specific '## ' section from markdown."""
    pattern = re.compile(
        rf"^##\s+(?:\d+\.\s+)?{re.escape(section_name)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.IGNORECASE,
    )
    m = pattern.search(md_text)
    if not m:
        return None
    return m.group(1).strip()


def copy_summaries_to_knowledge() -> list[str]:
    """Copy each validated summary to knowledge/books/. Returns list of slugs copied."""
    BOOKS_OUT.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for src in sorted(SUMMARIES_DIR.glob("*.md")):
        slug = src.stem
        # Validate first — don't copy invalid summaries
        r = validate_summary(slug, min_ratio=0.80)
        if not r.ok:
            console.print(f"[yellow]skip[/yellow]  {slug}: validator failed, not copying")
            continue
        dst = BOOKS_OUT / src.name
        shutil.copy2(src, dst)
        copied.append(slug)
    return copied


def build_theme_file(theme: ThematicMap, available_slugs: set[str]) -> None:
    out_dir = KNOWLEDGE_DIR / theme.category
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / theme.filename

    usable_sources = [s for s in theme.source_slugs if s in available_slugs]
    missing_sources = [s for s in theme.source_slugs if s not in available_slugs]

    lines: list[str] = [
        f"# {theme.title}",
        "",
        theme.description,
        "",
        "## Sources",
        "",
    ]
    if usable_sources:
        for slug in usable_sources:
            lines.append(f"- [`books/{slug}.md`](../books/{slug}.md)")
    else:
        lines.append("- *(No source summaries available yet — run `/absorb-book` for the relevant books.)*")
    lines.append("")

    if missing_sources:
        lines += [
            "## Pending sources (not yet absorbed)",
            "",
        ]
        for slug in missing_sources:
            lines.append(f"- `books/{slug}.md` — missing (absorb with `/absorb-book {slug}`)")
        lines.append("")

    # Pull relevant sections from each source
    for slug in usable_sources:
        summary_path = SUMMARIES_DIR / f"{slug}.md"
        try:
            md = summary_path.read_text(encoding="utf-8")
        except OSError:
            continue
        lines += [
            f"## From `books/{slug}.md`",
            "",
        ]
        # Pull the three most actionable sections
        for section_name in (
            "Regras de Trading Explícitas",
            "Fórmulas / Equações",
            "Algoritmos e Pseudocódigo",
            "Pitfalls e Anti-patterns",
        ):
            body = extract_section(md, section_name)
            if not body:
                continue
            lines += [f"### {section_name}", "", body.strip(), ""]
        lines.append("---")
        lines.append("")

    # Companion C++ code links
    if theme.code_refs:
        lines += [
            "## Companion C++ Code (reference implementations)",
            "",
            "These are reference C++ implementations from Timothy Masters' companion code.",
            "Use as authoritative pseudocode when porting to Python in Phases 4/5.",
            "",
        ]
        for ref in theme.code_refs:
            rel = Path(ref)
            if (ROOT / rel).exists():
                lines.append(f"- [`{ref}`](../../{ref})")
            else:
                lines.append(f"- `{ref}` *(file not present yet)*")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"[green]wrote[/green]  {out_path.relative_to(ROOT)}")


def build_skill_md(copied_slugs: list[str]) -> None:
    """Generate the master knowledge/SKILL.md."""
    out = KNOWLEDGE_DIR / "SKILL.md"

    copied_set = set(copied_slugs)
    tier_s = [b for b in BOOK_INDEX if b.tier == "S" and b.slug in copied_set]
    tier_a = [b for b in BOOK_INDEX if b.tier == "A" and b.slug in copied_set]
    tier_b = [b for b in BOOK_INDEX if b.tier == "B" and b.slug in copied_set]
    tier_c = [b for b in BOOK_INDEX if b.tier == "C" and b.slug in copied_set]
    pending = [b for b in BOOK_INDEX if b.slug not in copied_set]

    lines = [
        "---",
        "name: trading-knowledge",
        'description: Knowledge base for algorithmic swing trading built from 22 absorbed books. '
        'Use when designing strategies, selecting indicators, sizing positions, validating backtests, '
        'or reviewing any trading decision for the ai-trade project. '
        'Every recommendation MUST cite its source summary (knowledge/books/<slug>.md#section).',
        "---",
        "",
        "# Trading Knowledge — ai-trade Phase 0 Deliverable",
        "",
        "This skill aggregates the extracted knowledge from the books absorbed in",
        "Phase 0 of the `ai-trade` project. Use it when giving advice on:",
        "",
        "- Strategy design (momentum, cycles, regime-aware)",
        "- Indicator selection (Ehlers DSP, Clenow momentum, HMM)",
        "- Position sizing (fractional Kelly, optimal f, risk of ruin)",
        "- Backtest validation (CPCV, permutation tests, DSR, walk-forward)",
        "",
        "## Inviolable Rules (enforce before any recommendation)",
        "",
        "These rules are aggregated from the books and cannot be overridden without explicit",
        "justification citing a source:",
        "",
        "1. **Never recommend a strategy without citing its source** — every concept points to",
        "   `books/<slug>.md` (and ideally a page: `books/<slug>.md#section`).",
        "2. **Max 4 parameters per strategy** unless each extra parameter has economic/physical",
        "   justification (source: `systematic_trading`, `advances_fin_ml`).",
        "3. **Reject any backtest with PBO > 50%** (Probability of Backtest Overfitting).",
        "   Compute via CPCV (see `validation/cpcv.md`).",
        "4. **Apply Deflated Sharpe Ratio** when N strategies were tested — raw Sharpe is biased.",
        "   See `validation/deflated_sharpe.md`.",
        "5. **Walk-forward must cover ≥8 windows**, ≥6 profitable, none with drawdown > 25%.",
        "   See `validation/walk_forward.md`.",
        "6. **Fractional Kelly (≤ 0.25 × Kelly)** for live sizing — full Kelly is mathematically",
        "   optimal but practically reckless. See `strategies/money_management.md`.",
        "7. **Paper trade ≥3 months** before any live capital, regardless of backtest quality.",
        "   See `TRADING_SYSTEM_PLAN.md` section 11.",
        "",
        "## Navigation",
        "",
        "### Thematic indexes (start here for strategy questions)",
        "",
        "- **Strategies**",
        "  - [`strategies/anti_overfitting.md`](strategies/anti_overfitting.md) — 7-layer defense",
        "  - [`strategies/momentum.md`](strategies/momentum.md)",
        "  - [`strategies/cycle_detection.md`](strategies/cycle_detection.md)",
        "  - [`strategies/regime_change.md`](strategies/regime_change.md)",
        "  - [`strategies/money_management.md`](strategies/money_management.md)",
        "- **Indicators**",
        "  - [`indicators/ehlers_indicators.md`](indicators/ehlers_indicators.md)",
        "  - [`indicators/custom_momentum.md`](indicators/custom_momentum.md)",
        "  - [`indicators/regime_hmm.md`](indicators/regime_hmm.md)",
        "- **Validation**",
        "  - [`validation/cpcv.md`](validation/cpcv.md)",
        "  - [`validation/permutation.md`](validation/permutation.md)",
        "  - [`validation/deflated_sharpe.md`](validation/deflated_sharpe.md)",
        "  - [`validation/walk_forward.md`](validation/walk_forward.md)",
        "",
        "### Per-book summaries",
        "",
        f"**Tier S — Essentials ({len(tier_s)} absorbed):**",
    ]
    for b in tier_s:
        lines.append(f"- [`books/{b.slug}.md`](books/{b.slug}.md) — {b.short_desc}")
    lines += ["", f"**Tier A — Technical foundation ({len(tier_a)} absorbed):**"]
    for b in tier_a:
        lines.append(f"- [`books/{b.slug}.md`](books/{b.slug}.md) — {b.short_desc}")
    lines += ["", f"**Tier B — Depth and complement ({len(tier_b)} absorbed):**"]
    for b in tier_b:
        lines.append(f"- [`books/{b.slug}.md`](books/{b.slug}.md) — {b.short_desc}")
    lines += ["", f"**Tier C — Reference ({len(tier_c)} absorbed):**"]
    for b in tier_c:
        lines.append(f"- [`books/{b.slug}.md`](books/{b.slug}.md) — {b.short_desc}")

    if pending:
        lines += ["", f"**Not yet absorbed ({len(pending)}):**"]
        for b in pending:
            lines.append(f"- `books/{b.slug}.md` — {b.short_desc}")

    lines += [
        "",
        "## Companion code (C++)",
        "",
        "Reference implementations from Timothy Masters' books:",
        "",
        "- `books/code/masters-assessing/` — prediction/classification quality (bootstrap, entropy)",
        "- `books/code/masters-testing-tuning/` — backtest validation (MCPT, CSCV, drawdown bounds)",
        "",
        "Use these as authoritative pseudocode when porting algorithms to Python in Phase 4/5.",
        "",
        "## How to answer a trading question using this skill",
        "",
        "1. Identify which thematic index is most relevant (strategies/ vs indicators/ vs validation/).",
        "2. Read that file — it cross-references the specific books.",
        "3. If needed, drill into `books/<slug>.md` for full context.",
        "4. Cite your sources in the response: `books/<slug>.md#section [p.X]`.",
        "5. If the knowledge base doesn't cover the question, say so explicitly — do NOT extrapolate",
        "   or invent. That protects the user from advice not grounded in the literature.",
        "",
    ]

    out.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"[green]wrote[/green]  {out.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validate_summary checks (not recommended).",
    )
    args = parser.parse_args()
    _ = args  # reserved for future use

    if not SUMMARIES_DIR.is_dir():
        console.print(f"[red]no summaries directory: {SUMMARIES_DIR}[/red]")
        return 1

    # Ensure output structure exists
    BOOKS_OUT.mkdir(parents=True, exist_ok=True)
    STRATEGIES_OUT.mkdir(parents=True, exist_ok=True)
    INDICATORS_OUT.mkdir(parents=True, exist_ok=True)
    VALIDATION_OUT.mkdir(parents=True, exist_ok=True)

    # 1. Copy validated summaries
    copied = copy_summaries_to_knowledge()
    console.print(f"[bold]{len(copied)}[/bold] summaries copied to knowledge/books/")

    if not copied:
        console.print(
            "[yellow]No summaries were copied — nothing to aggregate.[/yellow]\n"
            "Run `/absorb-book <slug>` for at least one book first."
        )
        # Still emit skeleton SKILL.md + theme files so structure exists.

    available = set(copied)

    # 2. Emit thematic aggregation files
    for theme in THEMES:
        build_theme_file(theme, available)

    # 3. Emit master SKILL.md
    build_skill_md(copied)

    console.print(
        f"\n[bold green]Build complete.[/bold green] knowledge/ has "
        f"{len(copied)} books, {len(THEMES)} thematic files, SKILL.md."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
