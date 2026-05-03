# MyFxBook reverse-engineering — par 6R diagnóstico evaporou; um sobrevivente

A rodada Opus 4.7 de re-decode (Phase 5R-0, Wave 1+2+3 com 15 systems) mudou a história dos dois pares 6R da Etapa 2.

## Antes (Sonnet v1, 2026-05-02 manhã)

Dois pares foram pré-registrados no consenso adversarial 005-007 para testar regra-congelada cross-system:

- **Primário (decisivo)**: `1407880` (OLD Happy Market Hours v2.3.1, 3304 trades) → `10224499` (HMH FM REAL, 221 trades). Mesma família LATE_NY_BREAKOUT em ambos.
- **Diagnóstico (informativo)**: `2373850` (OLD Happy Algorithm PRO, 1691 trades) → `11171596` (Algorithm PRO FM, 1083 trades). Famílias divergem (UNCATEGORIZED vs NY_SESSION_REVERSAL) — a tese era "se o old é UNCAT mas o new é reversal, talvez o vendor tenha trocado motor; valor diagnóstico".

## Depois (Opus v2, 2026-05-02 tarde)

15 frozen_rules re-decodificados com Opus 4.7 num batch autorizado (chmod u+w → re-freeze chmod a-w, registrado em `frozen_rules/CHANGELOG.md` v2). 73% dos labels Sonnet foram reclassificados.

- **Par primário SOBREVIVE.** Ambos confirmados como LATE_NY_BREAKOUT por mérito próprio (1407880 com confidence 0.62, 10224499 com 0.72). Wave 1 ainda removeu `11206045` da família (Opus reclassificou como Tokyo Open momentum, não NY breakout) — família mais limpa.
- **Par diagnóstico EVAPORA.** Opus reclassificou os dois para UNCATEGORIZED. `11171596` virou "always-Sell em EUR/USDCHF com p95_hold=561h" — label degenerate, regra é viés direcional puro, não estratégia. `2373850` mantido UNCATEGORIZED com rationale tightened.

## O que isso muda

O par diagnóstico vira **caso negativo sobre vendor library HappyForex** ao invés de fonte de informação sobre mudança de motor. Findings de nível-estudo:

1. **Família NY_SESSION_REVERSAL ficou vazia** após sanity-check Opus (Sonnet classificava por timing 12-16 UTC sem checar sign da regra). Vendor não tem reversal genuíno na library inteira.
2. **Família FACTOR_SCALPING ficou vazia** (6 → 0). Hold NaN não comprova <30min; várias eram trees degenerate (always-Buy clone do baseline).
3. **Hold extraction bug em Stage 1**: 5+ systems reportam `hold p50/p95/max = NaN` por bug em `shared/eda.py` ou `decoder_features.py`. Phase 5R precisa reconstruir hold dos raw timestamps.
4. **Score formula 5R-3 é ortogonal ao label** — par evaporado não impede 5R, só reduz o escopo da Phase 6R para o sobrevivente.

## Decisão de escopo

Phase 6R agora roda **apenas no par primário** (`1407880 → 10224499`). Par diagnóstico fica documentado como finding sobre vendor, sem teste de regra-congelada cross-system (ambos UNCAT = não há regra a congelar).

Narrativa do estudo passa de "**dois pares 6R replicáveis**" para "**um par principal sobrevivente + um caso negativo sobre vendor library HappyForex**".

## Por que confiar no Opus aqui

73% reclass rate parece alto, mas os 15 systems da Wave 1+2+3 foram **selecionados a priori como suspeitos** (Pool A: 12 systems com sanity flag inconsistente com família — e.g., `11171596` NY_SESSION_REVERSAL com p95=561h; Pool B: 3 systems extras com inconsistência forte). Não é amostra aleatória.

Para checar se o Sonnet é frágil **mesmo nos não-suspeitos**, o item 8 do 5R-1-hardening dispara Opus em 5 systems aleatórios (seed=42) fora dos 15 já rechecados. Threshold de alarme: >30% reclass = Stage 1 (fingerprint + classificação Sonnet) precisa revisão antes de qualquer ranking público. Resultado pendente desta sessão.

## Custo da operação

~$2-3 estimados nos 5 Opus subagents do sample test (item 8). Wave 1+2+3 do 5R-0 já rodou em waves anteriores; budget do batch consumido.

## O que vem a seguir

- 5R-1-hardening Wave A (current): narrativa atualizada (este memo), CHANGELOG com SHA-256 + diff + chmod log, Stage 1 sample test rodando, `--limit/timeout` em runners.
- 5R-1-hardening Wave B: enum fechado de família em `shared/decoder_taxonomy.py` (10 entries, incluindo `H1_MOMENTUM_GOLD` provisório por D1).
- 5R-1-hardening Wave C: fatiar `replicator.py` (1295 linhas, sem testes) em 5 módulos + adicionar baselines `always_sell` / `random_frequency_matched` / `permutation_test` no comparator.
- 5R-1-hardening Wave D: testes unitários por componente + `hold_unknown` segregado em ranking secundário.
- Só após Wave D: liberar 5R-2 (comparator pleno) e 5R-3 (score).

Compatibilidade com mandate: 100% Plano C continua. Plano A DORMANT. Estudo segue research-only.

## Glossário (a integrar em `jornada/README.md`)

- **Par 6R primário (sobrevivente)**: `1407880 → 10224499`, ambos LATE_NY_BREAKOUT confirmados Opus.
- **Par 6R diagnóstico (evaporado)**: `2373850 → 11171596`, ambos UNCATEGORIZED após Opus. Caso negativo, não diagnóstico-de-coisa-nenhuma.
- **5R-1-hardening**: checklist bloqueante de 10 itens (5 grandes + 2 secundários + ponto narrativo + 2 do plan) que precisa fechar antes de 5R-2/5R-3. Documentos: `studies/myfxbook_reverse_engineering/_diagnostics/5R-1-hardening.md` (diretiva) + `5R-1-hardening-plan.md` (plano executável em 4 waves).
