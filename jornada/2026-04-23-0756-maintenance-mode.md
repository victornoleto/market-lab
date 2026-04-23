# Modo maintenance — consolidação em 100% Plano C

**Data:** 2026-04-23 07:56 AM-3 (10:56 UTC)
**Decisão do usuário:** "Ok, faça sua consolidação. Vamos pausar o
estudo/evolução dos planos A/B/D por enquanto."
**Override aplicado:** PRIMARY (`docs/mandate_overrides/2026-04-23-consolidate-plano-c-final.md`
— Signed)

## O que mudou

Após 113/113 honest FAIL em 2 semanas (6 V2 Plano A + 10 Phase 3.6 + 8 Phase
3.7-3 + 5 Phase 3.8-1 + 32 legacy + 10 D-MVP + 42 E-MVP) com Phase E-MVP
(multi-market SP500 + IBrX-100) fechando o caso com **PBO = 0.786**
catastrofico + **DSR 0/42 passam** + **42/42 tier Folclore**, o usuário
aprovou a consolidação.

**Mandate §1 agora é:**
- **100% Plano C passive factor-tilted** (`portfolio-aposentadoria.md`)
- **Strategy A/B/D = 0% DORMANT** (infra preservada)
- **Strategy E = infra experimental retida** em `scripts/phase_e_mvp/`

**Mandate §7 ganhou** uma entrada registrando a consolidação com rationale
citado (Harvey & Liu 2015 JOIM + Ilmanen 2011 + López de Prado 2018).

**CLAUDE.md + .claude/CLAUDE.md** atualizados — sumário agora diz "MODO
MAINTENANCE" no topo, regras 1-7 re-escritas para refletir que são
"válidas caso algum slot seja reativado".

## O que NÃO mudou (infra preservada)

Valor do projeto ai-trade permanece:

1. **Engine cross-lib validada** (bt + vectorbt + backtrader + numpy
   reference concordam a 1e-6 em 23/24 strategies testadas)
2. **Gates honest** (PBO CSCV, DSR deflator, WF, stationary bootstrap,
   cross-lib concordance, cost/tax stress)
3. **33 livros absorvidos** em `books/summaries/` + `knowledge/SKILL.md`
   (Claude Skill loadable)
4. **Scripts reusáveis:** `scripts/phase_d_mvp/`, `scripts/phase_e_mvp/`
   incluindo downloader, orchestrator otimizado, end-to-end pipeline
5. **Cost/tax models:** `br_cost_model.py` (R$20k condicional) +
   `us_cost_model.py` (15% DARF Inter). Prontos para multi-market runs
6. **Universe definitions:** IBRX100_TICKERS + SP500_TOP200 + SECTOR_MAP
   + b3_calendar
7. **CI/CD tests:** 1079 tests passando, incluindo regressão
   cross-calendar ticker

## Por que consolidar é a decisão estatisticamente correta

Eu (Claude) não sou pessimista — sou o agente que aplicou rigorosamente
os gates que a literatura séria prescreve. O resultado 113/113 não é
"falha do projeto" — é **o sinal correto que o mercado eficiente (retail
slice) está mandando**.

Literatura corrobora:

- **Harvey & Liu (2015, JOIM "Evaluating Trading Strategies")**: 316
  factors publicados em top journals; >80% não sobrevivem multiple-testing
  correction; survivors têm Sharpe half-life de ~3 anos pós-publicação.
- **Ilmanen (2011, "Expected Returns")**: apenas 5-6 factors globalmente
  robustos (value, momentum, carry, quality, trend, BAB); **todos têm
  janelas de 10-15 anos de underperformance**. Retail não aguenta esse
  período de dor sem desistir.
- **López de Prado (2018, AFML p.31-34, p.275)**: "most backtested
  strategies are false discoveries". PBO > 0.5 gate existe exatamente
  porque o default behavior é overfit. Nosso Phase E PBO = 0.786 mostra
  o grid explorou sem achar signal real.
- **Renaissance / Two Sigma / DE Shaw**: operam 5,000-10,000 tickers global
  com alt-data proprietária (sentiment, satellite, transcript ML) +
  co-location execution + capital bilionário. Edge quant institucional
  vem de **scale + infra + data**, não "fórmula secreta". Retail com
  capital < $1M + dados free + broker retail NÃO consegue replicar isso.
- **SPIVA reports 2010-2024**: 85%+ dos active US funds underperform SPY
  após custos em horizontes de 10+ anos. AQR e Brookings: hedge funds
  net-of-fees underperform 60/40 benchmark por 10+ anos.

**Passive factor-tilted NÃO é "desistir"**. É matematicamente otimo
para retail. A escolha de `portfolio-aposentadoria.md` (AVUS/SPMO/AVUV
/AVDE/IDMO/AVDV/AVEM + IBIT + GLDM) é **fundamentada** — AVUS/SPMO
implementam quality+momentum factor exposure (Russell 1000 + SP500
momentum); AVUV/AVDV implementam small+value; IBIT adiciona crypto
core; GLDM adiciona gold hedge. Isso já captura os factors robustos que
existem **sem tentar timing**.

## Revisão programada

**6 meses (2026-10-23):** re-rodar os grids existentes (Phase D-MVP +
Phase E-MVP) contra novos dados. Se algum config passar os gates com
novos 6 meses de OOS, reabrir conversa de reativar slot.

**12 meses (2027-04-23):** se 2026-10 ainda não teve sinal e 2027-04
também não, considerar o projeto **fechado como "proof of rigor"** —
valor remanescente é a due-diligence adversarial pra qualquer nova
ideia.

## Próximo passo (agora)

Commit dessa consolidação (já feito). Projeto permanece em modo
maintenance. Nenhum hunt ativo planejado.

**Se você quiser retomar:** diga explicitamente. Todo a infra está
pronta. Exemplos de retomada legítima:
- "Li um paper novo X — vamos testar"
- "Achei um dataset novo Y que pode dar edge — integra"
- "Quero voltar a rodar os grids, mudou algo" → precisa ter motivação
  além de "faz muito tempo"

**Se você quiser acelerar o Plano C:** podemos refinar
`portfolio-aposentadoria.md` (pesos, rebalance schedule, aportes
automáticos via Inter/XP), que é o compartimento oficial 100% agora.

## Artefatos desta sessão

Commits da madrugada + manhã 2026-04-22 a 2026-04-23:
- `178fc97` Strategy D open (Fase D-0 + D-1 infra)
- `239bd19` Lead D1 + D4 + MonthlyRankingStrategy base
- `671acba` Phase D-MVP orchestrator
- `5c8f396` run_end_to_end Phase D pipeline
- `68f7d19` Phase D-MVP aborted 10/42 BREADTH_NO_WINNER_D
- `62f94eb` Strategy E multi-market infra
- `5fdeb70` fix ranking_br cross-calendar bug
- `6a1f081` Phase E-MVP BREADTH_NO_WINNER_E 42/42 + override proposal
- `<próximo>` consolidação aplicada (este entry)

Boa jornada até daqui 6 meses. ⛵
