# Adversarial Chat — MyFxBook Pipeline

Debate versionado entre modelos para chegar a um consenso operacional sobre o pipeline de reverse-engineering MyFxBook.

## Objetivo

Produzir uma decisão prática e adversarialmente revisada sobre o que implementar a seguir, sem transformar revisão em validação teatral.

## Arquivos

- `001-opus.md`: prompt/contexto inicial enviado ao GPT, preservado como a posição inicial do Opus/usuário.
- `002-gpt.md`: primeira resposta do GPT ao prompt.
- `003-opus.md`: próxima resposta do Opus, lendo `002-gpt.md` e criticando/convergindo.
- `004-gpt.md`: próxima resposta do GPT, lendo `003-opus.md`.
- Continuar em ordem numérica até haver consenso.

## Protocolo

Cada nova mensagem deve:

1. Responder diretamente ao arquivo anterior.
2. Separar `Concordo`, `Discordo`, `Riscos restantes` e `Próxima ação proposta`.
3. Citar arquivos/dados concretos quando fizer afirmações sobre o estudo.
4. Distinguir claramente `decodabilidade`, `replicabilidade` e `edge econômico`.
5. Evitar aumentar escopo sem justificar o ganho esperado.

## Critério De Consenso

O chat termina quando ambos concordarem em uma lista curta de próximos passos, com ordem, kill-switches e entregáveis verificáveis.

## Regra De Qualidade

Nenhum arquivo deve dizer que há candidato `HIGH` para paper trading sem antes explicar qual evidência existe para:

1. `entry timing`: a regra prevê quando entrar contra timestamps sem trade.
2. `direction`: a regra prevê Buy/Sell nos eventos previstos.
3. `exit/sizing`: a regra aproxima duração, saída e lote.
4. `PnL`: a regra sobrevive a custos e gates do mandate.
