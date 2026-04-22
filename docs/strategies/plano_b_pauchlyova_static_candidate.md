# Plano B — Pauchlyova static multi-asset 5-leg (SSO/TLT/SPY/GLD/SHV)

> **Candidate doc, NOT A WINNER.** Consolida honestamente a família B3
> Pauchlyova static da Phase 3.8-1 (honest validation 2026-04-22,
> commit `f69b468` + escalation `bb0ef78`). Para evidência bruta dos
> 13 gates ver `reports/phase_3_8/b3_pauchlyova/AGGREGATE.md`. Este doc
> existe **para referência**: registra o que foi medido, o failure mode
> conhecido, e a decisão do usuário de **não prosseguir** em 2026-04-22.

**Path tag:** [SWING BROKER] • **Broker:** Banco Inter Global •
**Timeframe:** daily price / quarterly rebalance • **Hold median:** 63 dias.

---

## ⚠️ Status: NOT PROMOTED — candidate under mandate §7 override only

**Veredito honest Phase 3.8-1:** **FAIL 3/4 hard gates.** Bootstrap OOS
99.9% CI low < 0 (Gate 10), PBO 0.524 acima do 0.5 multi-feature (Gate 11),
DSR p 0.150 (Gate 12). Cross-lib limpo (Gate 9: |Δ|=0.578pp) e cost×2
Sharpe 0.894 (Gate 13: único B da família que passa).

**Decisão do usuário (2026-04-22):** não prosseguir. Razão dada — "se
essa estratégia não foi eficaz num período longo, então eu nem quero me
arriscar a mergulhar nela." O que motivou: o **FWD 2021-2026** caiu para
Sharpe 0.42 / CAGR 4.66% / MDD −29.8% por causa do 2022 rate shock no
sleeve TLT 40%. O brilho OOS 2016-2020 (Sharpe 1.14 / CAGR 11.9%) não
se manteve no out-of-sample vivido.

**Por que este doc ainda existe:** registra o lead mais próximo de
"algo real" entre as 29 validações honest cumulativas do projeto. Se,
em futuro, regime mudar significativamente (e.g., bonds voltarem a
hedgar equity como no 2009-2020), este é o ponto de partida mais
honesto para re-avaliação — **não como winner automático**, mas como
candidato para nova honest validation sob os windows expandidos.

---

## 1. TL;DR

Alocação estática 5-legs com rebalanceamento trimestral, inspirada na
Pauchlyova 2025 Quantpedia `[phase3_7_literature_sprint, §T1]` e
estruturalmente próxima de Ray Dalio All-Weather com sleeve de equity
alavancada:

| Leg | Peso | Ativo | Função |
|---|---:|---|---|
| LETF 2× | 20% | SSO | sleeve equity alavancada (leveraged SPY) |
| Long bonds | 40% | TLT | hedge macro contra recession |
| Equity | 20% | SPY | equity unleveraged base |
| Gold | 10% | GLD | hedge inflação / crisis |
| Cash | 10% | SHV | dry powder |
| **Total** | **100%** | — | — |

**Rebalance:** trimestral (primeiro dia útil Q1/Q2/Q3/Q4) de volta aos
pesos base. **Sem signal / sem regime filter** — a variante com trend
overlay (B3-trend) piorou em 4/4 configs (trend filter sinalizou crise
falsa durante COVID Q2-2020 e mandou 100% das legs pra cash — catastrófico).

**Período testado:** IS 2004-11-18 → 2015-12-31 (11y; GLD inception-limited),
OOS 2016-01-01 → 2020-12-31 (5y), FWD 2021-01-01 → 2026-04-15 (5.3y).

**Turnover:** 4.1 rebals/ano (tax-minimal). DARF 15% year-end modelado
explicitamente `[phase3_8_b1_gayed_canonical.apply_darf_year_end]`.

**Base científica:**
- Pauchlyova 2025 Quantpedia para static+trend framework
  `[phase3_7_literature_sprint, §T1]`
- Dalio All-Weather risk parity spiritual base (não citação direta de
  livro do corpus — Dalio não foi absorvido; mas é implícito no peso
  60/30/10 equity/bonds/hedges)
- Gayed canonical 2× leverage sleeve para equity
  `[leverage_for_the_long_run, p.17, Table 8]`
- DARF year-end realization model
  `[docs/investment-mandate.md §4.6]`

---

## 2. Performance honest por janela

### IS (2004-11-18 → 2015-12-31, 11.1y)

| Métrica | Valor |
|---|---|
| Sharpe (daily→annualized) | 0.694 |
| CAGR (pós-DARF) | 6.71% |
| MDD | −29.75% |
| N rebals | 45 |
| Turnover | 4.1/yr |

IS é **curto** (11y) porque GLD inception é 2004-11-18. Isso é um
caveat importante: o grid não teve 1970-1999 benchmark como B1/B2/B4/B5.

### OOS (2016-01-01 → 2020-12-31, 5.0y) — "o brilho"

| Métrica | Valor | Tier |
|---|---|---|
| Sharpe | **1.140** | (< 1.3 gate, mas alto entre os 5 winners da Phase 3.8) |
| CAGR | **11.91%** | Marginal ⚠️ |
| MDD | **−17.52%** | Válido ⚠️ |
| N rebals | 20 | |

**Contexto:** este OOS cobre COVID crash + Fed easing + AI-rally setup.
É um regime **favorável a portfolio 60/40-style** (equity + bonds ambos
performando, gold + cash amortecendo). Toda a "edge" documentada aqui é
dependente deste contexto específico.

### FWD (2021-01-01 → 2026-04-15, 5.3y) — **O failure real**

| Métrica | Valor | Tier |
|---|---|---|
| Sharpe | **0.420** | ❌ (< 0 seria reject formal; aqui é "sobreviveu mas fraco") |
| CAGR | **4.66%** | Folclore (abaixo CDI líquido 11%) |
| MDD | −29.83% | Reject-warning |
| N rebals | 22 | |

**Contexto:** FWD cobre 2022 rate shock (TLT −31% no ano) + 2023 AI rally
+ 2024 bull continuation + 2025 late-cycle. O **sleeve TLT 40% foi o
single point of failure**: quando bonds + equity caem juntos (2022), não
há diversificação efetiva. O gold sleeve (10%) é pequeno demais para
compensar. O cash sleeve (10%) só protege 10%.

**Esta é a razão estrutural pela qual o FWD não replicou o OOS.** O
2022 rate shock expôs a fragilidade do modelo 60/30/10 tradicional em
regime onde correlação equity-bonds flipa positiva.

---

## 3. Gate table (13 gates, rota B Inter)

Legend: ✅ pass; ❌ fail; ⚠️ warning (mandate §2.2/§2.3 tier framework).
Hard gates = 9/10/11/12.

| # | Gate | Valor | Verdict |
|---|---|---|---|
| 1 | IS Sharpe > 0.5 | 0.694 | ✅ |
| 2 | OOS Sharpe ≥ 1.3 | 1.140 | ❌ (closest miss dos 5 B-family winners) |
| 3 | OOS CAGR tier | 11.91% | ⚠️ Marginal |
| 4 | OOS MDD tier | −17.52% | ⚠️ Válido |
| 5 | FWD Sharpe > 0 | 0.420 | ✅ (tecnicamente passa, mas fraco) |
| 6 | WF ≥ 6/8 windows positive | (ver AGGREGATE) | ✅ |
| 7 | Median hold ≥ 5 days | 63d | ✅ |
| 8 | IR vs SPY BH ≥ 0.2 | −0.31 | ❌ (SPY buy-hold net Inter teve 13-15%/yr OOS, melhor) |
| 9 | **Cross-lib Δ CAGR OOS ≤ 3pp** | 0.578pp (pandas vs `bt`) | ✅ **HARD** |
| 10 | **Bootstrap 99.9% CI low OOS > 0** | −6e-5 | ❌ **HARD** |
| 11 | **PBO < 0.5** (8-config multi-feature) | 0.524 | ❌ **HARD** |
| 12 | **DSR p < 0.05** | 0.150 | ❌ **HARD** |
| 13 | Cost×2 Sharpe > 0.8 | 0.894 | ✅ (único B da Phase 3.8 que passa) |

**Hard gates: 1/4 pass, 3/4 fail.** Os 3 que falham todos tocam "o sinal
é statistically distinguível do null?" — e a resposta é não.

**Relaxações necessárias para considerar promoção:**
- R3 (mandate §7) relaxaria apenas gates 3/4 (CAGR/MDD ceilings). Não
  afeta 10/11/12. **Relaxamento R3 sozinho não basta.**
- Um segundo override §7 específico para aceitar "signal estatístico
  fraco em troca de perfil estrutural atraente" seria necessário.
  Nenhum override desse tipo foi concedido até 2026-04-22.

---

## 4. Mechanism — por que o perfil é estruturalmente atraente

**O que funciona (quando funciona):**
1. **Diversificação macro genuína:** 20% equity + 20% leveraged equity +
   40% long-bonds + 10% gold + 10% cash cobre três regimes
   distintos (risk-on, bond rally, crise inflacionária).
2. **Leverage limitado:** 20% em SSO (2×) dá ~1.2× exposure total a
   equity — moderado, não catastrófico como UPRO 3× puro.
3. **Rotation mínima:** 4 rebals/ano vs ~5 rebals/ano do Gayed canonical
   vs ~15/ano de MA-100 sweeps. **Custa DARF 15% year-end apenas sobre
   realizações trimestrais pequenas** — `cum_tax_pct` foi 0.18% no OOS
   inteiro (vs 0.31% do Gayed 1-leg, e 32.8% do MA-100 B2).
4. **Cost×2 robusto (Gate 13):** mesmo dobrando todos os custos (DARF
   30%, expense 1.90%), Sharpe cai apenas de 1.14 → 0.89. O perfil é
   genuinamente "baixo-custo-por-unidade-de-edge".

**O que quebra (e quebrou em 2022):**
1. **Correlação equity-bonds positiva sob inflação.** O modelo 60/30/10
   assume que bonds amortecem equity drawdowns (vide 2008, 2020-Q1). Em
   2022, Fed apertou 500bps e bonds + equity caíram juntos. TLT 40%
   sleeve perdeu 31% no ano.
2. **GLD 10% é pequeno demais para hedgar.** Em regimes inflacionários
   sérios (2022-2023 early), a alocação eficiente pediria 20-30% gold —
   mas aí deixa de ser Pauchlyova e vira outra estratégia.
3. **SSO 2× amplifica os drawdowns de equity sem o offset de bonds.**

---

## 5. Known failure mode — 2022-style rate shock

O FWD 2021-2026 evidenciou o failure mode. A pergunta estrutural é:
**o 2022 foi regime novo (bonds não mais hedge) ou anomalia temporária
(Fed moveu rápido demais)?** A literatura `[phase3_7_literature_sprint,
§T1 Pauchlyova 2025]` e outras fontes 2023-2025 ainda divergem.

**Se anomalia:** B3 pode retomar performance OOS-like quando bonds
voltarem a correlação negativa com equity. Esperar e re-validar.

**Se regime novo:** a alocação 40% TLT é estruturalmente quebrada e o
B3 nunca mais atinge o perfil 2016-2020. Não há conserto sem mudar a
composição — e aí deixa de ser Pauchlyova canonical.

**Como seria mitigado (não testado, não recomendado sem honest validation):**
- Substituir TLT por TIPS (inflation-protected bonds) — diferente
  thesis, exigiria novo grid + gates
- Reduzir TLT de 40% → 20% e aumentar gold de 10% → 30% — fora do
  paper Pauchlyova; vira strategy própria
- Adicionar filtro macro simples: cash quando yield-curve invertida
  persistente — vira B3-with-overlay, o que B3-trend-monthly tentou e
  FAIL em 4/4

Nenhum desses caminhos foi validado honest. Qualquer um requereria
Phase 4+ honest hunt próprio.

---

## 6. Configuração exata (reprodutibilidade)

```python
from ai_trade.backtest.strategies.phase3_8_b3_pauchlyova_static_trend import (
    B3Config,
    simulate_b3,
)

config = B3Config(
    letf_kind="SSO",       # 2× equity sleeve
    trend_filter_on=False, # STATIC ablation — no SMA overlay
    rebal_cadence="quarterly",
    sma_period=200,        # ignored (trend off)
)

# Allocation base (hard-coded in simulate_b3):
#   SSO:  20%
#   TLT:  40%
#   SPY:  20%
#   GLD:  10%
#   SHV:  10%
# Rebalance: first trading day of Q1/Q2/Q3/Q4
```

**Cost model:**
- Commission: 0 (Inter&Co Securities)
- FX spread: 1.20% only on USD deposit (não intra-strategy)
- LETF expense: 0.95%/yr (SSO embedded)
- Other ETF expense: ~0.15-0.4%/yr (real prices embedded)
- **15% DARF year-end realization** (via `apply_darf_year_end` helper)

**Data windows:**
- IS: 2004-11-18 → 2015-12-31 (GLD inception limits IS start)
- OOS: 2016-01-01 → 2020-12-31
- FWD: 2021-01-01 → 2026-04-15

---

## 7. Path forward (honesto)

**Nenhum path recomendado ativamente** a partir de 2026-04-22.
O usuário viu o FWD 2021-2026 (post-publication real OOS) e optou por
não prosseguir — decisão coerente com o dado.

**Paths opcionais, se decisão mudar:**

1. **Paper trading 6-12m** (zero custo) rodando B3-SSO-static-quarterly
   live no Inter paper. Coleta data 2026-04 → 2026-10+. Não aumenta a
   significância estatística material (sample size), mas valida
   execução operacional (rebalances trimestrais, DARF modelagem,
   slippage real vs modelado).

2. **Honest re-validation em 2028+** quando tivermos ~2.5y mais dados
   FWD. Se o período 2026-2028 replicar o perfil OOS 2016-2020, a
   hipótese "2022 foi anomalia" ganha força. Se replicar o perfil
   2021-2026, a hipótese "regime novo" se consolida.

3. **Nunca promover direto pra live** sem mandate §7 override explícito
   cobrindo: (a) relaxamento R3 CAGR/MDD ceilings, (b) override dos
   hard gates 10/11/12, (c) aceitação explícita do failure mode 2022-style.

---

## 8. Citations (completas)

- **Pauchlyova 2025** static+trend LETF framework base:
  `[phase3_7_literature_sprint, §T1 Quantpedia Pauchlyova entry]`
- **Gayed 2×/3× LETF rotation canonical** (leverage sleeve rationale):
  `[leverage_for_the_long_run, p.7-8, p.13, p.17 Table 8]`
- **López de Prado DSR** (gate 12 basis, why p=0.150 falha):
  `[advances_fin_ml, p.196-211]`
- **López de Prado CSCV / PBO** (gate 11 basis, why 0.524 falha):
  `[advances_fin_ml, p.208-211]`
- **F2 engine prev_weight × return alignment** (look-ahead fix):
  `[advances_fin_ml, p.31-34]`
- **Aronson data-mining bias null** (por que 29/29 FAIL era esperado):
  `[evidence_based_ta, p.459]`
- **Hsu/Kuan post-selection decay** (82% de rules decaem pós-seleção):
  `[evidence_based_ta, p.450]`
- **Inter rota B DARF 15% year-end**:
  `[docs/investment-mandate.md §4.6]`
- **Mandate tier framework (CAGR/MDD warning-only) + hard gates §2.4**:
  `[docs/investment-mandate.md §2.2, §2.3, §2.4, §7]`
- **Phase 3.8-1 BREADTH_NO_WINNER_B** (contexto da descoberta):
  `[reports/phase_3_8/BREADTH_NO_WINNER_B.md]`

---

## 9. Historical decisions (decision log)

- **2026-04-22 15:35** — B3 Pauchlyova subagent Wave 2 conclui. Winner
  config = B3-SSO-static-quarterly (trend overlay HURT em 4/4 configs).
  OOS Sharpe 1.14 + MDD Válido, mas 3/4 hard gates FAIL. Commit `f69b468`.
  `reports/phase_3_8/b3_pauchlyova/AGGREGATE.md` documenta.
- **2026-04-22 15:52** — `reports/phase_3_8/BREADTH_NO_WINNER_B.md`
  formaliza 5/5 Phase 3.8-1 FAIL. Cita B3 no §2.4 como "closest to
  edge" mas explicitamente NOT a winner. Commit `bb0ef78`.
- **2026-04-22 (conversa)** — Usuário identifica B3 como candidato
  interessante após escalation. Claude aponta que a frase original
  "passa sob R3" foi otimista demais; full gate picture mostra 3/4
  hard FAIL + FWD 2021-2026 degradado (Sharpe 0.42).
- **2026-04-22 (decisão)** — Usuário opta por **não prosseguir** com B3:
  > "Se essa estratégia não foi eficaz num período longo, então eu nem
  > quero me arriscar a mergulhar nela."
- **2026-04-22 (este doc)** — Criado como candidate-reference, **NOT
  promoted**. Registra o que foi medido, o failure mode, e a decisão
  explícita de não prosseguir. Mandate intacto, nenhuma §7 entry aberta.

---

**Veja também:**
- `reports/phase_3_8/b3_pauchlyova/AGGREGATE.md` — evidência bruta
  completa das 8 variantes (4 LETF × 2 cadences × 2 trend on/off)
- `reports/phase_3_8/BREADTH_NO_WINNER_B.md` — contexto das 5 famílias
  Phase 3.8-1 + 5 recomendações R1-R5
- `jornada/2026-04-22-1535-phase3.8-b3-fail.md` — narrativa humana
- `src/ai_trade/backtest/strategies/phase3_8_b3_pauchlyova_static_trend.py` — código
- `scripts/phase3_8/run_b3_pauchlyova_static_trend.py` — runner
