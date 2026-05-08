# Mandate override proposal — Abertura de Strategy D

**Data:** 2026-04-22
**Proposto por:** Claude Code (sob pedido do usuário 2026-04-22)
**Status:** ✅ **Signed 2026-04-22 17:34** (usuário: "aprovado — não me preocupar
com split A/B/C/D agora, foco é encontrar estratégia vencedora").
**Afeta (aplicado):** `docs/investment-mandate.md` §1, §2.2, §2.3, novo §4b,
§7; `CLAUDE.md` + `.claude/CLAUDE.md` sumário.
**Reversível:** Não após assinatura. Este arquivo permanece imutável como
registro histórico; alterações futuras precisam de override subsequente.

---

## 🟢 Notas de aplicação (post-signature)

- **Split A/B/D deixado sem números fixos** — conforme feedback do usuário
  ("não se preocupar com o split agora"), a tabela §1 do mandate registra
  apenas "parte do 20-40% ativo" para A/B/D, com decisão concreta adiada
  até houver winner confirmado em algum slot. A proposta original sugeria
  40/35/25 — esse número foi removido para não sugerir compromisso que
  ainda não existe.
- **Strategy D foi adicionada como §4b** (não §5) para preservar as
  referências históricas existentes em `docs/plans/*`, `docs/strategies/*`
  e `reports/*` que apontam para §5 (anti-patterns), §6 (referências) e
  §7 (histórico). Renumerar teria exigido search-and-replace amplo
  sem ganho semântico.
- **§7 ganhou entry nova** documentando a abertura e citando este arquivo
  de override como pointer permanente.

---

## Por que este override

O mandate atual (§1) fixa 3 compartimentos: Plano C passivo (60-80%),
Strategy A (parte dos 20-40% ativos), Strategy B (parte dos 20-40% ativos).
A abertura de Strategy D como **3º slot ativo** requer alteração explícita do
§1, per regra interna do mandate §7 ("qualquer divergência é bug de raciocínio
— consulte §7 antes de agir contra").

Contexto empírico (em 2026-04-22):
- 29/29 validações honest FAIL nos slots A+B.
- Engine limpo, cross-lib a 1e-6 em 23/24 strategies.
- Edge estatístico procurado em A+B não existe sob gates honest.
- Usuário pediu abrir Strategy D (swing-trade BR ranking-based) como tentativa
  estruturalmente diferente, aproveitando isenção R$20k/mês de IR BR.

Este override NÃO reduz rigor dos gates, NÃO toca Plano C passivo, NÃO
elimina Strategy A/B (ambas continuam como slots, mesmo sem winner atual).

---

## Alterações propostas

### §1 — Capital allocation (alteração)

**De:**
> 1. **Capital allocation:** 60-80% passive buy&hold (ver
>    `portfolio-aposentadoria.md`), 20-40% split entre 2 strategies
>    ativas: **Strategy A (principal, Path A short-hold CFD
>    Pepperstone, agressiva alavancada)** e **Strategy B (secundária,
>    Path B swing broker BR, moderada).**

**Para:**
> 1. **Capital allocation:** 60-80% passive buy&hold (ver
>    `portfolio-aposentadoria.md`), 20-40% split entre **até 3 strategies
>    ativas**: **Strategy A (short-hold CFD Pepperstone, agressiva
>    alavancada)**, **Strategy B (swing broker US via Inter Internacional,
>    moderada, LETF rotation Gayed-anchored)** e **Strategy D (swing-trade
>    BR por ranking mensal, broker BR doméstico, moderada com benefício
>    tributário R$20k/mês).** Split default dentro dos 20-40% ativos: A 40%
>    / B 35% / D 25% (ajustável quando houver winner confirmado em algum
>    slot). Slots sem winner confirmado ficam inativos (zero alocação real)
>    até aprovação em backtest honest; alocação desses slots redistribui
>    pra Plano C passivo enquanto pendente.

**Rationale do split 40/35/25:** A tem o maior retorno-alvo (CFD alavancado,
tier Válido 25-50%) mas é o mais arriscado; B é o mais conservador em termos
de estrutura (LETF com DARF year-end); D é o novo e mais incerto (isenção
depende de capital < X). Peso pode ser renegociado quando houver winners.

### §2 — Gate framework (sem alteração estrutural, adicionar tier D)

Mantém §2.1-§2.4 intacto. Em §2.2 (CAGR tiers), adicionar coluna Strategy D:

**Strategy D (broker BR doméstico, isenção R$20k condicional):**
- Folclore: < 11% (abaixo do CDI líquido ~11%/ano — não compensa o risco de
  ações)
- Marginal: 11-17%
- **Válido: 17-25%**
- Forte: 25-40%
- Extraordinário: > 40% (suspect — validar extra com bootstrap 99.99%)

Benchmark âncora: **CDI líquido ~11%/ano** (mesmo que Strategy B, já que
Strategy D é comparável a alternativa conservadora brasileira).

Em §2.3 (MDD tiers), adicionar:
- D Excelente ≤ 15%
- D Válido ≤ 25%
- D Warning 25-50%
- D Reject > 50%

(Mais conservador que Strategy B porque D opera em ações BR, mais voláteis
que LETFs US sob regime rotation.)

### §5 — Strategy D rules (novo)

Criar nova seção §5 com:

1. **Universo:** IBrX-100 (proxy dinâmico "top 100 ações B3 por volume médio
   60d > R$5M/dia" na Fase D-MVP; composição point-in-time dos PDFs B3 se
   algum lead passar gates).
2. **Cadência:** mensal (1º dia útil do mês) — alinhada com cota de isenção.
3. **Cesta:** N stocks entre 15-30, grid-testável, cap setorial 20-30%.
4. **Sinais testáveis** (todos citados em livros absorvidos):
   - Momentum Clenow `[stocks_on_the_move, p.76-77]`
   - Magic Formula `[quant_trading_chan, ch.1, p.7]`
   - Multi-fator V+M+Q equal-weighted `[quant_trading_chan, ch.1, p.7]`
   - Low-vol + momentum hybrid
   - Combos com regime filter IBOV SMA 200
5. **Tax model:** isenção R$20k/mês condicional. Se vendas mensais ≤ R$20k →
   isento. Se > R$20k → 15% DARF sobre TODO o lucro do mês (regra CVM/RFB).
   Sensitivity obrigatória em R$50k / R$100k / R$500k de capital inicial.
6. **Cost model:** corretagem R$0 (Clear/Nubank) ou R$5 flat (XP/Rico
   conservador), grid-switchable. Emolumentos B3 0.025% sobre volume. Spread
   5 bps proxy para IBrX-100 top-30 stocks; 20 bps para stocks fora top 30
   (ATR%-proxy se promissor).
7. **Broker (Fase D-promotion):** XP / Clear / Rico / Inter DTVM / BTG
   Pactual — a decidir quando houver winner confirmado.
8. **Gates hard-block:** mesmos 13 de Phase 3.5f-3.8 + DSR deflator com
   N_trials = total de configs do grid (~64 esperadas).

### §7 — Histórico de overrides (adicionar entrada)

Adicionar entrada no histórico:

> **2026-04-22:** Abertura de Strategy D como 3º slot ativo. Motivação: 29/29
> validações honest FAIL em A+B; decisão de tentar estrutura diferente
> (ranking BR com isenção R$20k). Ver `docs/mandate_overrides/2026-04-22-strategy-d-open.md`.
> Autor proposta: Claude Code. Assinatura usuário: [pending].

### `CLAUDE.md` sumário — alteração

No bloco "📌 Investment Mandate":
- Item 1: de "20-40% split entre 2 strategies ativas" para "20-40% split
  entre até 3 strategies ativas: A (Pepperstone CFD), B (Inter LETF), D
  (broker BR ranking mensal)".
- Adicionar item 4.5 ou item 8 com regras resumo de Strategy D.

---

## O que NÃO está mudando

- **Plano C passivo** (60-80% portfolio-aposentadoria.md) continua intacto e
  prioritário.
- **Gates hard-block §2.4** (PBO < 0.5 + DSR p<0.05 + WF ≥ 6/8 + bootstrap
  99.9% CI low > 0 + cross-lib ±3pp) inalterados.
- **Strategy A** e **Strategy B** continuam como slots (alocação zero real
  até winner, mas disponíveis se hunt futuro produzir winner).
- **Regra de citação** (CLAUDE.md Regra 2) continua — Strategy D spec cita
  Clenow, Chan, López de Prado, Kaufman.
- **Gayed single-source** (§4) continua restringindo Strategy B apenas.
  Strategy D não herda essa restrição porque é novo slot.

---

## Como assinar (quando aprovar)

1. Responder nesta sessão com "**aprovado**" ou equivalente.
2. Eu (Claude Code) aplicaria as mudanças literais em
   `docs/investment-mandate.md` e `CLAUDE.md` exatamente como propostas
   acima.
3. Marco este arquivo como `status: ✅ Assinado 2026-04-22 HH:MM` e
   permanece no diretório `docs/mandate_overrides/` como registro histórico
   imutável.
4. Posso então começar Fase D-1 (data layer) e Fase D-MVP (backtest grids).

Se rejeitar: arquivar este arquivo como `status: ❌ Rejeitado 2026-04-22
HH:MM` + motivo, voltar para decisão R1-R5 do Phase 3.8-1 closure.
