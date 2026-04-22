# Prompt — retomada Plano B LETF hunt (próxima sessão Claude Code)

> **How to use this file:** abrir nova sessão Claude Code em
> `/var/www/pessoal/ai-trade`, copiar o bloco fenced abaixo como primeiro
> prompt. Não precisa cortar branch nova antes — o próprio Claude vai
> te apresentar um menu de paths e aguardar sua decisão.
>
> **Contexto desta pausa (2026-04-22):** Phase 3.8-1 fechou
> BREADTH_NO_WINNER_B com 5/5 FAIL (B1 Gayed, B2 MA-sweep, B3 Pauchlyova,
> B4 AR(1), B5 Faber). 29/29 honest validations cumulativas. B3 foi
> descartado pelo usuário após plot mostrar que SPY BH post-DARF bate
> B3 em CAGR em TODAS as janelas. Usuário optou por pausar e reforçar o
> objetivo: **estratégia Plano B deve ser centrada em ETFs alavancados
> como motor principal de retorno** (Gayed LETF rotation spirit,
> mandate §2.4).

---

```
Retomar trabalho de Plano B em ai-trade.

## OBJETIVO ESTRATÉGICO (reforçado pelo usuário em 2026-04-22)

A estratégia Plano B DEVE usar ETFs alavancados (LETFs: SSO 2×, UPRO 3×,
QLD 2×, TQQQ 3×, possivelmente SOXL 3×) como motor principal de retorno.
A tese central é Gayed LRS canonical `[leverage_for_the_long_run, p.7-8,
p.13, p.17]`: leverage on durante regime de baixa volatilidade; cash
durante regime stressado; compounding em streaks de bull market entrega
CAGR well-above SPY buy-hold quando o regime filter funciona.

Isto é consistente com mandate §2.4 ("família LETF rotation") e é o que
o usuário acredita ser o caminho mais rápido para retorno agressivo.

**O que ISSO SIGNIFICA em termos de sub-seleção de hipóteses:**

1. ✅ LETF-centric (~100% LETF quando ON, ~100% cash/bonds quando OFF)
   são prioridade.
2. ⚠️ Multi-asset com sleeve LETF pequeno (B3 Pauchlyova-style 20% SSO +
   80% diversified) está DESPRIORIZADO — diluição da alavancagem foi
   exatamente o que fez o B3 perder pra SPY BH post-DARF em CAGR.
3. ❌ Estratégias unleveraged puras (B5 Faber SPY, passive buy-hold)
   NÃO são candidatos a Plano B — tier teto seria ~CDI, abaixo do alvo.
4. ⚠️ Estratégias com baixa alocação média a LETF (e.g., on_regime_fraction
   < 50%) também desprioritizadas — LETF tem que estar ON mais da metade
   do tempo pra o compounding valer a pena vs SPY BH.

## ESTADO DE SAÍDA (2026-04-22)

- Phase 3.8-1 fechou BREADTH_NO_WINNER_B (commit bb0ef78 + d55036b plot)
- 29/29 honest validations cumulativas FAIL
- Nenhuma decisão R1-R5 ainda tomada
- B3 Pauchlyova explicitamente descartado: usuário viu plot B3 vs SPY BH
  e concluiu que diluição multi-asset não é caminho
- Pytest baseline 929 passed, 2 skipped, 0 failures
- Branch main atualizada, todos commits pushed

## LEITURA OBRIGATÓRIA ANTES DE QUALQUER AÇÃO

1. `jornada/README.md` — estado humano atualizado
2. `docs/CURRENT_STATE.md` — TL;DR
3. `reports/phase_3_8/BREADTH_NO_WINNER_B.md` §4 — os 5 paths R1-R5
4. `docs/strategies/plano_b_pauchlyova_static_candidate.md` — por que
   B3 foi descartado (context da última decisão; instruir contra
   diluição de alavancagem)
5. `docs/plans/2026-04-22-phase3.9-composer-inspired-hunt-prompt.md` —
   plano Phase 3.9 composer-inspired (R5) se usuário quiser
6. `books/summaries/leverage_for_the_long_run.md` — Gayed LRS canonical,
   **revisitar p.7-8, p.13-17, p.21** para alinhar qualquer nova hipótese
   LETF-centric com a base científica única do Plano B
7. `memory/MEMORY.md` + `memory/project_cagr_mdd_tier_framework.md` +
   `memory/feedback_pepperstone_staging_and_darf.md`

Rodar `git log --since "2026-04-22"` para detectar movimento entre
sessões. Se `git log` mostrar commits novos, investigar antes de
apresentar o menu.

Rodar `date` no início para saber quantos meses passaram. Se > 3 meses,
avisar que OOS/FWD teriam ~N meses mais dados disponíveis e isso reabre
janelas analíticas — talvez valha rodar honest revalidation em janelas
estendidas antes de tentar nova hipótese.

## O QUE PRODUZIR (decision-support, NÃO ação)

Em até 1 página:

(a) **Estado resumido em 3 bullets:** onde paramos, o que ficou
    commitado, o que está pendente de decisão.

(b) **5 paths R1-R5 re-apresentados LETF-focused:**
    - R1 paper-trade B5 Faber: ⚠️ ABANDONAR — B5 é unleveraged, não
      alinha com objetivo LETF-centric reforçado em 2026-04-22
    - R2 pivot Plano C 100% passive: preserva, mas DEPRIORITIZAR — é
      "desistir do Plano B", não o que usuário quer agora
    - R3 re-spec Válido=CDI-matcher: preserva como contingência
    - R4 wait 6-12 meses + re-run: preserva como option passiva
    - **R5 Phase 3.9 composer-inspired**: PRIMARY — os arquétipos B6/B7/B8
      já são LETF-centric (UPRO/SSO quando ON) e testam layered
      conditionals não-exercitados. Plano pronto em
      `docs/plans/2026-04-22-phase3.9-composer-inspired-hunt-prompt.md`.

(c) **R6+ novos caminhos LETF-centric** não listados em
    BREADTH_NO_WINNER_B §4 — sugestões para discussão:
    - R6 Multi-LETF cross-asset rotation: SSO+QLD+TQQQ por regime
      individual (não static weights; dynamic regime flip por asset)
    - R7 LETF com dynamic leverage adjustment baseado em realized vol
      (Božović-style managed vol mas rota B weekly/monthly, não daily
      que já matou H2 na Phase 3.7-3)
    - R8 LETF + VIX-managed exposure sizing (reduzir para 50% UPRO
      quando VIX > 20, full quando VIX < 20, cash quando VIX > 35)
    - R9 Paired LETF rotation: SPY regime ON → UPRO; SPY regime OFF
      mas trending down → SQQQ ou SPXU (inverse leveraged); neutro →
      cash. Testar se trend-following em ambas direções bate long-only.
    - R10 LETF + gold sleeve condicional: canonical Gayed + 10-20%
      UGL (2× gold) quando VIX > 25 (não static — apenas em stress)

(d) **Sua recomendação informal atualizada** considerando o objetivo
    LETF-centric reforçado.

## HARD CONSTRAINTS (zero bypass)

- AGUARDAR decisão explícita minha antes de executar qualquer path
- NÃO dispatch subagents sem aprovação explícita minha
- NÃO editar `docs/investment-mandate.md` nem `docs/strategies/*.md`
  sem sign-off meu
- NÃO criar branches novas sem aprovação
- NÃO relaxar §2.4 hard-block gates (bootstrap 99.9% CI, DSR p<0.05,
  PBO, cross-lib ±3pp CAGR) sem decisão R3 explícita
- Pytest baseline 929 deve continuar green se rodar pytest (rodar só
  se eu pedir)
- NÃO paga feeds pagos (decisão usuário 2026-04-23 permanente)
- NÃO testar variantes unleveraged como Plano B candidate (violaria o
  objetivo LETF-centric reforçado)
- NÃO testar variantes multi-asset com sleeve LETF < 50% (violaria o
  objetivo: diluição foi o killer do B3 contra SPY BH)
- NÃO testar daily-rotation variants (Phase 3.7-3 §2.3 Wave 2 killer:
  DARF + daily rebal = 3-7%/ano drag tóxico)

## DEFAULT se eu disser "pode começar"

Assume R5 Phase 3.9 (composer-inspired B6/B7/B8 layered-conditional
LETF rotation). É o único path que:
1. Testa hipóteses novas dentro do framework honest existente
2. É LETF-centric (B6/B7/B8 todos têm UPRO/SSO como on-asset)
3. Não exige decisão estratégica grande (sem relax de gates, sem pivot)

Para R1/R2/R3/R4 OU R6-R10, exigir sinalização explícita.

## DEFAULT se eu disser "propõe novo caminho LETF"

Assume R6+ discussion. Pesquisar (NÃO rodar backtest — só análise de
hipótese) se algum dos R6/R7/R8/R9/R10 já foi testado no projeto
(`git log --all --grep`, `grep -r` em `src/ai_trade/backtest/strategies/`,
`reports/`, `jornada/`). Se já testado, reportar o veredict. Se não
testado, proponha um sketch de Phase 3.10 plan (análogo ao Phase 3.9
prompt mas LETF-centric R6+).

Começar pela leitura obrigatória + `date` + `git log --since "2026-04-22"`
antes de qualquer outra coisa.
```

---

## Notas para o usuário sobre este prompt

**Por que LETF-centric é coerente com o mandate:**

- Mandate §2.4 já define Strategy B como "família LETF rotation" — este
  prompt apenas reforça em prompt-level o que já é contrato.
- Gayed LRS canonical é a base científica única do Plano B
  (`books/summaries/leverage_for_the_long_run.md`). LETF on/off é o
  core; sem LETF, não é Plano B — é outra coisa.
- O B3 Pauchlyova tinha só 20% em SSO (e 20% em SPY unleveraged + 40%
  TLT + 10% GLD + 10% cash). Sob DARF rota B, a diluição da alavancagem
  fez SPY BH post-DARF bater o B3 em CAGR em 4/4 janelas. A lição
  gratuita: **Plano B com sleeve LETF < 50% não justifica a complexidade
  operacional vs SPY BH + CDI**.

**Por que R5 fica PRIMARY:**

- Os 3 arquétipos B6/B7/B8 da Phase 3.9 já são LETF-centric por design
  (UPRO/SSO quando ON, cash quando OFF — ~100% leverage exposure no
  on-regime).
- A família "layered conditionals" (RSI + VIX + MA + max_dd) ainda não
  foi testada honestamente. Os 29 FAILs foram todos 1-signal ou
  multi-asset; nenhum foi 1-asset-LETF + 2-3 signals acumulando
  conditionals.
- Custo é limitado (~6-12h LLM) e conclui cleanly: OR passa (ótimo) OR
  adiciona 3 ao contador de FAIL com aprendizado específico sobre
  layered-regime robustness.

**Por que R6-R10 são sugestões LETF-nativas novas:**

- R6 Multi-LETF rotation (SSO+QLD+TQQQ individual): usa cross-asset
  trend dentro do universo LETF. Sector rotation mas alavancada.
- R7 LETF + dynamic leverage via realized vol: a tese Božović (Phase
  3.7-3 H2.a) mas a WEEKLY/MONTHLY (não daily) pra evitar DARF drag.
- R8 LETF + VIX-sizing (não on/off mas tri-state 100%/50%/0%): meio
  caminho entre Gayed canonical e B7 sideways deleverage.
- R9 Paired LETF (long UPRO + short via SPXU): teoricamente dobra o
  edge trend-following mas enfrenta borrow-cost e expense em ambos os
  lados; historical precedente limitado.
- R10 LETF + conditional gold sleeve: leva o "black swan catcher" do
  B8 para um patamar mais ambicioso (gold ao invés de VIXY — menos
  decay negativo).

Nenhum dos R6-R10 tem plano pronto. Se você escolher algum, o Claude
proporá um Phase 3.10 plan-doc análogo ao da Phase 3.9.

## Como usar quando voltar

1. Abrir nova sessão Claude Code em `/var/www/pessoal/ai-trade`
2. Copiar APENAS o bloco entre ``` ``` acima (o prompt propriamente dito)
3. Colar como primeiro prompt
4. Aguardar menu de decisão-support
5. Decidir R5 (default) OR sinalizar R6-R10 OR R2/R3/R4 explicitamente
