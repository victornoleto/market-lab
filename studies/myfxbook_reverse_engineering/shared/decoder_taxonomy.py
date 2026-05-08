"""Single source of truth for myfxbook reverse-engineering family taxonomy.

5R-1-hardening Wave B item 2 (2026-05-02). Created in response to:
- Stage 1 sample test alarm (60% reclass rate on random sample of non-rechecked).
- User decisions D5/D6/D7 admitting 3 provisional families.
- User rule: UNCATEGORIZED is legitimate but requires `reason_code`; family outside
  the closed enum must go to `candidate_new_family: str | None`.

Consumers (refactored to import from here):
- shared/replicator.py — load_frozen_rule reads family/reason_code/candidate_new_family.
- shared/replicator_lite.py — same.
- shared/reliability_proxy.py — uses Family.UNCATEGORIZED for demote check.
- .claude/agents/decoder.md — prompt references this module's enum + rules.

`provisional=True` sticks until a 2nd independent system supports the family in
later runs (R1 onwards). If the provisional flag is ever removed without a 2nd
supporter being recorded, that is a methodological regression — see
_diagnostics/5R-1-hardening.md §1 (final caveat from user 2026-05-02).

Citações (CLAUDE.md Regra 2):
- López de Prado [advances_fin_ml, ch.3] — label consistency.
- [ml_for_algo_trading] — supervised classification needs closed label space.
- Pardo [testing_tuning] — reproducibility via deterministic schemas.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class Family(str, Enum):
    """Closed enum of strategy families. The ONLY allowed `family` values in
    Stage 2 decoder output. Any label outside this enum must be written into
    `candidate_new_family: str | None` with `family=UNCATEGORIZED` and
    `reason_code=taxonomy_gap`."""

    # 9 originais (decoder.md prompt 2026-05-01 + UNCATEGORIZED como classe legítima)
    LATE_NY_BREAKOUT = "LATE_NY_BREAKOUT"
    LONDON_OPEN_MOMENTUM = "LONDON_OPEN_MOMENTUM"
    LONDON_OPEN_MR = "LONDON_OPEN_MR"
    NY_SESSION_REVERSAL = "NY_SESSION_REVERSAL"
    OVERLAP_NY_LONDON_RANGE = "OVERLAP_NY_LONDON_RANGE"
    OVERNIGHT_GAP_FADE = "OVERNIGHT_GAP_FADE"
    FACTOR_SCALPING = "FACTOR_SCALPING"
    MARTINGALE_GRID = "MARTINGALE_GRID"
    UNCATEGORIZED = "UNCATEGORIZED"

    # 3 provisórias (D5/D6/D7 do usuário 2026-05-02). Marked provisional=True in
    # TAXONOMY registry below. Revisão obrigatória após R1: se nenhum 2º system
    # suportar a assinatura, downgrade para UNCATEGORIZED + reason_code=taxonomy_gap.
    H1_MOMENTUM_GOLD = "H1_MOMENTUM_GOLD"
    NEWS_RELEASE_MOMENTUM = "NEWS_RELEASE_MOMENTUM"
    SWING_TREND_MOMENTUM = "SWING_TREND_MOMENTUM"


class UncatReason(str, Enum):
    """Mandatory reason_code when family == UNCATEGORIZED. Decisão usuário 2026-05-02:
    UNCAT é classe legítima quando evidência é insuficiente, NÃO bucket-de-fuga."""

    UNDERPOWERED = "underpowered"               # n<100 ou cobertura insuficiente
    DEGENERATE = "degenerate"                   # tree/ripper colapsa para always-Buy/Sell baseline
    HOLD_MISMATCH = "hold_mismatch"             # sanity intraday violado por hold real
    MIXED_STRATEGY = "mixed_strategy"           # múltiplos peaks de timing / sub-estratégias coexistem
    TAXONOMY_GAP = "taxonomy_gap"               # estratégia coerente mas fora do enum atual
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"  # fingerprint+candidates não permitem decisão


@dataclass(frozen=True)
class FamilySpec:
    """Metadata por família. Single source of truth — nada de duplicar em prompts."""

    name: Family
    provisional: bool
    n_supporting_systems: int
    description: str
    criteria: str
    review_gate: str
    citations: tuple[str, ...]


# Registry. Ordem reflete prioridade de match heurístico no decoder agent.
TAXONOMY: Mapping[Family, FamilySpec] = {
    Family.LATE_NY_BREAKOUT: FamilySpec(
        name=Family.LATE_NY_BREAKOUT,
        provisional=False,
        n_supporting_systems=2,  # 1407880, 10224499 (par 6R primário sobrevivente)
        description="Late NY breakout em FX majors com USD/EUR.",
        criteria="Entry concentrado 21-01 UTC, exit 1-3h. Captura overnight breakout do range Asian.",
        review_gate="—",
        citations=("[evidence_based_ta, p.367-380] (session/hour FX)",),
    ),
    Family.LONDON_OPEN_MOMENTUM: FamilySpec(
        name=Family.LONDON_OPEN_MOMENTUM,
        provisional=False,
        n_supporting_systems=0,
        description="London open momentum em FX.",
        criteria="Entry 06-09 UTC, BUY/SELL alinhado com sign do range Asian, exit < 4h.",
        review_gate="—",
        citations=("[evidence_based_ta, p.367-380]",),
    ),
    Family.LONDON_OPEN_MR: FamilySpec(
        name=Family.LONDON_OPEN_MR,
        provisional=False,
        n_supporting_systems=0,
        description="London open mean-reversion (fade do Asian range).",
        criteria="Entry 06-09 UTC, BUY/SELL opposite ao Asian range.",
        review_gate="—",
        citations=("[algo_trading_chan] (mean-reversion vs momentum regimes)",),
    ),
    Family.NY_SESSION_REVERSAL: FamilySpec(
        name=Family.NY_SESSION_REVERSAL,
        provisional=False,
        n_supporting_systems=0,  # vazia pós-Wave 1+2+3 do 5R-0 (finding sobre vendor)
        description="Reversal NY session.",
        criteria="Entry 12-16 UTC, exit time-based 1-3h, sign opposite ao London move.",
        review_gate="Finding 2026-05-02: vazia após Opus re-decode (vendor HappyForex sem reversal genuíno na library).",
        citations=("[evidence_based_ta, p.367-380]",),
    ),
    Family.OVERLAP_NY_LONDON_RANGE: FamilySpec(
        name=Family.OVERLAP_NY_LONDON_RANGE,
        provisional=False,
        n_supporting_systems=2,  # 9375654, 11207608 (pós-Opus v2)
        description="Range fade no overlap NY/London.",
        criteria="Entry 12-16 UTC, BUY/SELL determinado por posição na BB ou range, exit time-based.",
        review_gate="—",
        citations=("[evidence_based_ta, p.367-380]",),
    ),
    Family.OVERNIGHT_GAP_FADE: FamilySpec(
        name=Family.OVERNIGHT_GAP_FADE,
        provisional=False,
        n_supporting_systems=0,
        description="Fade do gap de fim de semana.",
        criteria="Entry sexta tarde / segunda manhã, fade do gap.",
        review_gate="—",
        citations=("[evidence_based_ta]",),
    ),
    Family.FACTOR_SCALPING: FamilySpec(
        name=Family.FACTOR_SCALPING,
        provisional=False,
        n_supporting_systems=0,  # vazia pós-Wave 1+2+3 (6→0; finding sobre Sonnet)
        description="Scalping multi-fator.",
        criteria="Entry distribuído, durations < 30min, edge tipicamente vol-targeting ou pair-trading intraday.",
        review_gate="Finding 2026-05-02: 6/6 systems pré-Opus reclassificados (hold NaN não comprovava <30min — Stage 1 bug R4 corrigido).",
        citations=("[advances_fin_ml, ch.5] (feature importance)",),
    ),
    Family.MARTINGALE_GRID: FamilySpec(
        name=Family.MARTINGALE_GRID,
        provisional=False,
        n_supporting_systems=0,  # k1_pass=False já filtrado em Stage 1
        description="Martingale ou grid (capital risk).",
        criteria="k1_pass=False na sanity (já filtrado pela Stage 1).",
        review_gate="Sair imediatamente; valide cross-check com sanity flags.",
        citations=("[fooled_by_randomness, Taleb] (martingale risk)",),
    ),
    Family.UNCATEGORIZED: FamilySpec(
        name=Family.UNCATEGORIZED,
        provisional=False,
        n_supporting_systems=10,  # v2 frozen_rules state
        description="Heurísticas inconclusivas. Classe LEGÍTIMA, NÃO bucket-de-fuga.",
        criteria="Confidence < 0.5 OU evidência insuficiente para qualquer família do enum. Exige reason_code obrigatório.",
        review_gate="Toda atribuição UNCAT carrega reason_code ∈ UncatReason. Ranking não penaliza UNCAT automaticamente.",
        citations=("[advances_fin_ml, ch.3] (label consistency over forced labels)",),
    ),
    # ---------- Provisionals (D5/D6/D7 do usuário 2026-05-02) ----------
    Family.H1_MOMENTUM_GOLD: FamilySpec(
        name=Family.H1_MOMENTUM_GOLD,
        provisional=True,
        n_supporting_systems=1,  # 6541963 (Happy Gold Tickmill M15)
        description="Momentum em Gold/XAU em timeframe H1.",
        criteria="Gold/XAU + entry-on-H1-momentum + tree balanced + dir_acc>0.7.",
        review_gate=(
            "D7 2026-05-02. Provisional até R1 trazer 2º system com mesma assinatura. "
            "Se R1 não trouxer suporte, downgrade UNCATEGORIZED + reason_code=taxonomy_gap + "
            "candidate_new_family=H1_MOMENTUM_GOLD."
        ),
        citations=(
            "[carver_systematic_trading] (cross-section momentum)",
            "[machine_trading]",
        ),
    ),
    Family.NEWS_RELEASE_MOMENTUM: FamilySpec(
        name=Family.NEWS_RELEASE_MOMENTUM,
        provisional=True,
        n_supporting_systems=1,  # 1612420 (OLD Happy News v1.4.1)
        description="Momentum em janela de news release (clock-anchored).",
        criteria=(
            "Clock-anchored ≥1 bucket horário com >30% trades + name-flag NEWS/HF News + "
            "sign momentum-following. Confirmado pós-R4 com p50=0.01h (~36s) no system de referência."
        ),
        review_gate=(
            "D5 2026-05-02. Provisional até R1 trazer 2º system com mesma assinatura. "
            "Se R1 não trouxer suporte, downgrade UNCATEGORIZED + reason_code=taxonomy_gap + "
            "candidate_new_family=NEWS_RELEASE_MOMENTUM."
        ),
        citations=("[evidence_based_ta, p.247-260] (event windows + small-sample bias)",),
    ),
    Family.SWING_TREND_MOMENTUM: FamilySpec(
        name=Family.SWING_TREND_MOMENTUM,
        provisional=True,
        n_supporting_systems=1,  # 8577442 (Happy Way FM)
        description="Swing trend/momentum (multi-day hold).",
        criteria=(
            "Mediana hold >72h + top hour <15% + H4/D1 trend/momentum features dominam tree. "
            "Confirmado pós-R4 com p50=213.99h (~9d) no system de referência."
        ),
        review_gate=(
            "D6 2026-05-02. Provisional até R1 trazer 2º system com mesma assinatura. "
            "Se R1 não trouxer suporte, downgrade UNCATEGORIZED + reason_code=taxonomy_gap + "
            "candidate_new_family=SWING_TREND_MOMENTUM. "
            "Nomenclatura: SWING_TREND_MOMENTUM (não SWING_H4_TREND) — H4 é feature/timeframe, não essência."
        ),
        citations=(
            "[testing_tuning, Pardo] (swing-trade systems)",
            "[stocks_on_the_move, Clenow] (swing/trend momentum cross-section)",
        ),
    ),
}


# Convenience accessors -------------------------------------------------------

def family_names() -> tuple[str, ...]:
    """All Family.value strings, in registry order. For prompt sync + CLI display."""
    return tuple(f.value for f in TAXONOMY.keys())


def provisional_families() -> tuple[Family, ...]:
    return tuple(f for f, spec in TAXONOMY.items() if spec.provisional)


def reason_code_values() -> tuple[str, ...]:
    return tuple(r.value for r in UncatReason)


# Validators ------------------------------------------------------------------

class TaxonomyError(ValueError):
    """Raised when decoder output violates the taxonomy contract."""


def validate_family_label(label: str) -> Family:
    """Coerce a raw string to Family. Raises TaxonomyError if not in enum.

    Use case: when reading frozen_rules/<id>.md or signal_rule.md YAML.
    """
    if label is None:
        raise TaxonomyError("family label is None; expected one of " + ", ".join(family_names()))
    try:
        return Family(label)
    except ValueError as e:
        valid = ", ".join(family_names())
        raise TaxonomyError(
            f"family={label!r} is not in the closed taxonomy enum. Valid: [{valid}]. "
            f"For a novel pattern outside the enum, set family=UNCATEGORIZED + "
            f"reason_code=taxonomy_gap + candidate_new_family={label!r}."
        ) from e


def validate_decoder_output(
    *,
    family: str,
    reason_code: str | None = None,
    candidate_new_family: str | None = None,
    strict: bool = True,
) -> Family:
    """Validate a Stage 2 decoder output triple (family, reason_code, candidate_new_family).

    Rules (5R-1-hardening §1):
    - `family` must be a member of Family enum (always strict — non-enum labels are
      a contract violation, not a soft warning).
    - If `family == UNCATEGORIZED`: `reason_code` must be set and ∈ UncatReason.
    - If `reason_code == taxonomy_gap`: `candidate_new_family` must be set
      (the proposed label that the agent considered but couldn't fit into the enum).

    Modes:
    - `strict=True` (default; new outputs from R1 onwards): violations raise TaxonomyError.
    - `strict=False` (legacy reads of v2 frozen_rules pre-R1): violations emit
      DeprecationWarning, do not raise. Allows reading existing rules without breaking.

    Returns the validated Family enum member.
    """
    fam = validate_family_label(family)  # always strict on enum membership

    if fam is not Family.UNCATEGORIZED:
        return fam

    # UNCATEGORIZED branch: reason_code mandatory.
    if reason_code is None:
        msg = (
            "family=UNCATEGORIZED requires reason_code (one of: "
            + ", ".join(reason_code_values())
            + "). User decision 2026-05-02: UNCAT é classe legítima quando evidência é "
            "insuficiente, mas NÃO bucket-de-fuga."
        )
        if strict:
            raise TaxonomyError(msg)
        warnings.warn(
            f"[decoder_taxonomy] {msg} (legacy v2 frozen_rule — will be enforced from R1 v3 onwards)",
            DeprecationWarning,
            stacklevel=2,
        )
        return fam

    try:
        reason = UncatReason(reason_code)
    except ValueError as e:
        valid = ", ".join(reason_code_values())
        raise TaxonomyError(
            f"reason_code={reason_code!r} is not in UncatReason. Valid: [{valid}]."
        ) from e

    if reason is UncatReason.TAXONOMY_GAP and not candidate_new_family:
        msg = (
            "reason_code=taxonomy_gap requires candidate_new_family (the proposed "
            "label the agent considered but couldn't fit into the enum)."
        )
        if strict:
            raise TaxonomyError(msg)
        warnings.warn(f"[decoder_taxonomy] {msg}", DeprecationWarning, stacklevel=2)

    return fam


__all__ = [
    "Family",
    "UncatReason",
    "FamilySpec",
    "TAXONOMY",
    "TaxonomyError",
    "family_names",
    "provisional_families",
    "reason_code_values",
    "validate_family_label",
    "validate_decoder_output",
]
