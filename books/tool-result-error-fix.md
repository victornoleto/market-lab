Plano — Diagnosticar e mitigar "Tool result missing due to internal error" em /absorb-book

Context

O fluxo /absorb-book falhou no Camada 3 round 3 para time_series_hamilton:
ambas as tool calls paralelas (summary-validator judge #1 e #2) retornaram
[Tool result missing due to internal error]. Como a arquitetura exige que
os 2 juízes rodem em paralelo na mesma assistant message (self-consistency),
uma falha simultânea bloqueia o pipeline inteiro. O veredicto provisório está
em BORDERLINE e books/TODO.md não pode ser atualizado sem a confirmação dos
juízes. Esse mesmo erro tende a repetir nos outros livros grandes da fila
(≥500 páginas / ≥300k tokens) e precisa de mitigação estrutural, não só de
um reenvio pontual.

---

Hipóteses de causa raiz (ranqueadas pela evidência)

H1 — Sobrecarga da API Anthropic (529/rate) com 2 subagents grandes em paralelo (mais provável)

- \_full.txt do Hamilton = 1,7 MB / 56.301 linhas / ~421k tokens.
- Cada juiz roda Read + múltiplos Grep no arquivo inteiro + escreve JSON grande (~80 KB).
- Round 3 já queimou tokens em: book-reader inicial (Opus, 421k in), 2 retries com feedback, 2 rodadas prévias de judges. Ambas
  as chamadas falharem ao mesmo tempo é assinatura clássica de throttling/overload, não de bug num prompt.
- Documentado: dev.to/subprime2010/claude-code-subagents-how-to-run-parallel-tasks-without-hitting-rate-limits-4bpl.

H2 — Cap de 32.000 tokens no output do subagent (provável para retry #1/#2)

- Bug conhecido em Claude Code: CLAUDE_CODE_MAX_OUTPUT_TOKENS é ignorado; subagent corta em 32K.
- Ref: github.com/anthropics/claude-code/issues/25569.
- summary-validator escreve JSON em arquivo (bom), mas a spec pede também: "Se FAIL, liste explicitamente as 3 piores
  hallucinations no texto de resposta" — com 12 claims analisadas e evidence_quotes de até 300 chars cada, o reasoning textual
  pode aproximar-se do cap em livros grandes.

H3 — Perda de transmissão do tool result pelo harness (minoritária mas real)

- Bug conhecido: github.com/anthropics/claude-code/issues/44068 — execução completa, resultado some em trânsito. Ocorre em
  sessões longas com uso pesado de ferramentas (exatamente o estado do round 3).

H4 — Colisão de contexto entre subagents paralelos (improvável, mas agravante)

- Cada juiz lê 1,7 MB independentemente; se o harness serializar prompt caching de forma ruim, o 2º pode bater 85% de contexto
  antes do 1º retornar.

Todas as 4 hipóteses são agravadas pelo tamanho específico de Hamilton (maior livro da fila, 814 páginas). H1 e H3 são
transitórias; H2 é estrutural. Precisa mitigar as três.

---

Design recomendado: mitigação em 3 camadas

Camada A — Retry resiliente no orquestrador (/validate-summary)

Adicionar, em .claude/commands/validate-summary.md, um loop de retry explícito em torno do dispatch paralelo dos juízes:

- Se qualquer juiz retornar [Tool result missing due to internal error] ou resultado vazio, verificar se o arquivo
  .validation/<slug>_judge_<N>.json foi escrito em disco.
  - Se foi: o juiz concluiu; ler do disco e ignorar o erro de transporte (mitiga H3).
  - Se não foi: retry com backoff.
- Política: máx 2 retries com delays 60s e 180s. No 1º retry, ainda dispatcha ambos em paralelo. No 2º retry, cai para serial
  (um juiz de cada vez) para eliminar H1/H4 — a perda de self-consistency é preço aceitável ante uma validação que não roda.
- Log em books/summaries/.logs/<slug>.log cada retry com motivo.

Camada B — Shrink do output final dos juízes (.claude/agents/summary-validator.md)

Mitigar H2 reduzindo o que o juiz devolve via tool result (o JSON em disco continua completo):

- Trocar a regra atual "liste as 3 piores hallucinations no texto" por:
  ▎ "Liste no texto de resposta APENAS: verdict, support_ratio, contagem de hallucinations, path do JSON. Não inclua
  evidence_quotes nem reasoning. Orquestrador vai ler o JSON do disco."
- Target de output de subagent: ≤1 KB de texto (vs. potencialmente 10–20 KB hoje com top-3 hallucinations embutidos).
- O orquestrador já lê os arquivos JSON no passo de agregação — a duplicação no texto de retorno é redundante e pode custar o
  run.

Camada C — Dispatch condicional por tamanho (/validate-summary)

Para livros muito grandes, trocar paralelo por serial por padrão (não só como fallback):

- Threshold: n_pages > 500 ou tamanho de \_full.txt > 1,2 MB ou recommended_mode = "map_reduce" no metadata.
- Quando acima do threshold: juízes em série, com ~30s entre eles. Perda de self-consistency pura, mas ganho claro de
  confiabilidade — e livros grandes já têm mais claims, então o risco de BORDERLINE por contaminação entre juízes é menor
  proporcionalmente.
- Livros pequenos (≤500 páginas) continuam em paralelo (preserva o design original para o caso majoritário).
  │ Antes de implementar A/B/C, destravar a sessão atual: │
  │ │
  │ 1. Ler se books/summaries/.validation/time*series_hamilton_judge*{1,2}.json existem do round 3. Se existirem, pular │
  │ dispatch e ir direto para agregação. │
  │ 2. Se não existirem: re-dispatchar os 2 juízes sequencialmente (não paralelos), com prompt reduzido que só pede verdict + │
  │ path — espelhando o que a Camada B vai formalizar. │
  │ 3. Com os JSON em disco, rodar agregação e atualizar books/TODO.md. │
  │ │
  │ --- │
  │ Arquivos a modificar │
  │ │
  │ ┌────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────── │
  │ ────┐ │
  │ │ Arquivo │ Mudança │
  │ │ │
  │ ├────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────── │
  │ ────┤ │
  │ │ .claude/commands/validate-summary.md │ Camada A (retry + leitura do disco como fallback) e Camada C (dispatch │
  │ │ │
  │ │ │ condicional paralelo/serial por tamanho). Linhas-alvo: 50–97. │
  │ │ │
  │ ├────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────── │
  │ ────┤ │
  │ │ │ Camada B: reescrever seção "Output final para o orquestrador" (linhas │
  │ │ │
  │ │ .claude/agents/summary-validator.md │ 184–199) para proibir evidence*quotes/reasoning no texto de retorno e │
  │ │ │
  │ │ │ exigir resposta ≤1 KB. │
  │ │ │
  │ ├────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────── │
  │ ────┤ │
  │ │ .claude/commands/absorb-book.md │ Propagar a mesma política de retry/fallback no passo que chama │
  │ │ │
  │ │ │ /validate-summary (linhas 63–89). │
  │ │ │
  │ ├────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────── │
  │ ────┤ │
  │ │ books/summaries/.logs/time_series_hamilton.log │ (gerado) registro do hotfix e das novas tentativas. │
  │ │ │
  │ ├────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────── │
  │ ────┤ │
  │ │ books/TODO.md │ Atualizado ao final com veredicto definitivo do Hamilton. │
  │ │ │
  │ └────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────── │
  │ ────┘ │
  │ │
  │ Funções/utilidades existentes reusáveis: scripts/check_citations.py (offset detection já funciona; falsos positivos de │
  │ [p.257]/[p.372] são outro issue rastreado, fora do escopo deste plano). │
  │ │
  │ --- │
  │ Verification │
  │ │
  │ 1. Hotfix Hamilton: rodar os passos 1–3 da seção "Hotfix imediato". Confirmar que │
  │ books/summaries/.validation/time_series_hamilton_judge*{1,2}.json existem e têm JSON válido. Rodar agregação manualmente. │
  │ Gravar veredicto em books/TODO.md com nota "hotfix serial". │
  │ 2. Camada B (shrink output): depois de editar summary-validator.md, re-rodar /validate-summary em um livro médio já │
  │ aprovado (ex.: systematic_trading) — esperar tempo de run menor e zero [Tool result missing]. │
  │ 3. Camada A (retry): simular falha injetando um slug inválido em um dos dispatches paralelos; confirmar que o │
  │ orquestrador detecta ausência de JSON, faz retry e no 2º retry serializa os juízes. Log deve mostrar a transição. │
  │ 4. Camada C (serial condicional): re-rodar /absorb-book para trading_systems_methods (outro livro grande da fila). Log │
  │ deve indicar "serial dispatch (n_pages>500)". Run completo sem erro interno. │
  │ 5. Regressão: rodar /absorb-book em 1 livro pequeno já aprovado (stocks_on_the_move) — deve continuar paralelo e passar │
  │ igual a antes. │
  │ │
  │ Critério de sucesso global: conseguir absorver os 3 maiores livros restantes (time_series_hamilton, │
  │ trading_systems_methods, machine_trading) sem intervenção manual e sem [Tool result missing].
