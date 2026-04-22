# CAGR e MDD deixam de ser gates bloqueantes — viram classificação por tier

**Data:** 2026-04-22 12:52 UTC
**Branch:** `phase3.6/swing-winner-hunt-20260423`
**Quem decidiu:** usuário, em conversa com assistant após Phase 3.7-1 literature sprint
**Files tocados:** mandate §2 / §4.8 / §5 / §7, CLAUDE.md §📌, `.claude/CLAUDE.md` §📌,
docs/plans/2026-04-23-find-swing-winner-phase-3-6.md §5

---

## O que mudou em uma frase

O mandate não rejeita mais estratégias por causa de CAGR baixo ou
drawdown alto — agora classifica em tiers e emite warning. Só os gates
estatísticos (PBO, DSR, walk-forward, Sharpe, cross-lib etc.) continuam
hard-block.

---

## Por quê

A Phase 3.6 fechou 10/10 FAIL e várias famílias foram rejeitadas só
porque não bateram o CDI floor (13% CAGR) ou porque o MDD passou de
−25%. Exemplo: Family H (HMM regime) teve OOS Sharpe 0.69, CAGR 9,47%,
MDD −21% — com PBO baixo (0.19), cross-lib clean, todo o trabalho
estatístico feito certo. Foi auto-rejeitada pelo gate 3 (CAGR < 13%).
Sob o novo framework, essa família seria classificada como **"folclore
CAGR + excelente MDD"** — ainda não vai a live, mas fica visível pro
usuário como referência de pesquisa em vez de desaparecer no pool de
FAILs indistinguíveis.

A Phase 3.7-1 literature sprint confirmou que até os melhores papers
publicados pós-2022 (Zarattini 2024 SPY intraday: Sharpe 1.33 net,
CAGR 19.6%) **não chegam nem perto** do target mandate original
(5-10%/mês = 60-120% CAGR). Esse target nunca foi realista em OOS
honest — era aspiração de abril/2016 quando o projeto começou, antes
dos 10 FAIL da Phase 3.6 e dos 3+3 FAIL das Phases 3.5a V1/V2.

A alternativa a afrouxar era o Plano C passive fallback (§4.7 do
mandate). O usuário optou por tentar mais uma rodada de hunt (Phase
3.7-2 data sprint + 3.7-3 hunt) com gates mais honestos, em vez de
jogar a toalha.

---

## Tiers em linguagem humana

**CAGR Strategy A (Pepperstone CFD, sem DARF modelado):**

| Tier | CAGR | Significado |
|---|---|---|
| Folclore | < 13% | Pior que CDI bruto. Não é winner. |
| Marginal | 13-25% | Acima do CDI mas broker-risk-premium Pepperstone não compensa. Warning visível. |
| **Válido** | **25-50%** | Winner candidate. |
| Forte | 50-100% | Prime winner. Target original (5-10%/mês) vive aqui. |
| Extraordinário | > 100% | Suspeito. PBO < 0.3 obrigatório + extra robustness. |

**CAGR Strategy B (Inter pós 15% DARF):**

| Tier | CAGR | Significado |
|---|---|---|
| Folclore | < 11% | Pior que CDI líquido. Não é winner. |
| Marginal | 11-17% | Acima do CDI mas não vale o esforço. Warning visível. |
| **Válido** | **17-25%** | Winner candidate. |
| Forte | 25-40% | Prime winner. |
| Extraordinário | > 40% | Suspeito. |

**MDD Strategy A (alavancada):** Excelente ≤ 25%, Válido 25-40%, Warning
40-50%, Forte warning 50-75%, **Reject > 75%**.

**MDD Strategy B (moderada):** Excelente ≤ 15%, Válido 15-25%, Warning
25-35%, Forte warning 35-50%, **Reject > 50%**.

---

## Pepperstone: por que não adicionamos o 15% DARF ao cost model

Decisão explícita do usuário 2026-04-22: "na Pepperstone não vamos
precisar emitir DARF". O contexto legal diz outra coisa — Lei 14.754/2023
estabeleceu DARF 6015 sobre ganho de capital offshore, 15% flat, apurado
mensalmente pelo próprio investidor. Pepperstone não emite informe de
rendimentos BR e não faz retenção, então o trigger legal é puramente
self-reported.

Para o backtest, a decisão é **ignorar o 15%** no cost model Pepperstone.
Inter continua modelando DARF porque é ganho de capital BR-source com
informe emitido pelo próprio banco — é o cenário realista.

Isso tem uma consequência honesta: o CAGR reportado em backtest
Pepperstone é "pre-DARF self-reported". Comparação cross-broker (A vs
B) precisa lembrar disso. Documentado em mandate §7 entry 2026-04-22 +
§4.8.

---

## Pepperstone: staging de depósitos

Novidade documentada formalmente em §4.8 do mandate. A ideia: o dinheiro
em Pepperstone deve ser mentalmente "escrito off" — é jurisdição SCB
Bahamas (Tier-3, sem investor-compensation scheme tipo FSCS UK £85k).
Automation elimina o atrito operacional do "colocar saldo", mas não
elimina o counterparty risk.

Protocolo:

1. Paper 3 meses (já obrigatório por mandate §2.4).
2. Live inicial USD 500-1.000 — "proof it runs", não proof de retorno.
3. Escalada mensal condicional: cada green month autoriza o próximo
   degrau.
4. Cap em USD 5-10k até 6 meses de live verde.
5. Nunca exceder tolerância pessoal de perda total — se USD 20k na
   conta te destruiria, não coloca USD 20k.

---

## Impacto na Phase 3.6 BREADTH_NO_WINNER

Não muda o verdict. Das 10 famílias rejeitadas:
- 7 falharam gates hard-block também (PBO, DSR, Sharpe bootstrap,
  cross-lib) — **continuam FAIL.**
- 3 (H, A, J) tinham falha principalmente em CAGR/MDD — **agora
  classificariam como "folclore" ou "marginal"**. Teriam ficado como
  leads de referência, não winners.

A BREADTH_NO_WINNER.md fica preservada como forensic record; o
framework novo se aplica a partir da Phase 3.7-3 (próxima hunt).

---

## Próximo passo

Usuário vai abrir **Phase 3.7-2 (data sprint)** em uma nova sessão.
Essa fase consome:
- `docs/research/2026-04-23-phase3.7-literature-sprint.md` (inventário
  de papers + hypothesis shortlist)
- `docs/investment-mandate.md` com §2.2/§2.3/§4.8/§7 atualizados

Phase 3.7-2 endereça os data gaps identificados no sprint (VIX feed,
crypto honest OHLCV, SPY minute pós-2023, Pepperstone swap snapshot).

Phase 3.7-3 (hunt) vai operar sob o framework novo — leads como H1
(Zarattini 2024 intraday SPY, CAGR 19.6% net) agora podem passar como
"Marginal" A em vez de auto-rejeitar.

---

## Entry no glossário

- **Tier CAGR:** classificação de 5 níveis (Folclore/Marginal/Válido/Forte/Extraordinário)
  por rota A ou B. Mandate §2.2.
- **Tier MDD:** classificação de 5 níveis (Excelente/Válido/Marginal warning/
  Forte warning/Reject) por rota A ou B. Mandate §2.3.
- **Hard-block gates:** os que continuam zero-bypass — PBO, DSR, WF,
  single-block OOS, FWD, bootstrap CI, cross-lib, Sharpe. Mandate §2.4.
- **SCB Bahamas Tier-3:** jurisdição efetiva de Pepperstone pra retail BR
  via cTrader Open API. Sem investor compensation scheme. Motiva staging
  de depósitos §4.8.
