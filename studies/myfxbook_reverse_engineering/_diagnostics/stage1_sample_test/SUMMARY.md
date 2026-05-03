# Stage 1 sample test — 5R-1-hardening Wave A item 8

**Data**: 2026-05-02
**Threshold de alarme**: reclass > 30% (i.e. ≥ 2 de 5)
**Resultado**: **reclass 3/5 = 60% — ALARME DISPARADO**

## Pool e seleção

Pool de 15 systems não-rechecados pelo 5R-0 Opus:
- 7 PARTIAL_DECODED: `9843883, 1612420, 8577442, 10251631, 10067081, 9830783, 9841939`
- 8 DECODED: `10563761, 11355455, 10734338, 10192401, 10475089, 1603276, 10249298, 1152318`

NOT_DECODED excluído por design (re-decode lá seria first-decode, não re-decode).

Sample (5 random, seed=42, alfabético):
```python
['10067081', '10192401', '10475089', '1612420', '8577442']
```

Mix: 3 PARTIAL + 2 DECODED. Disparados em paralelo como 5 subagents Opus 4.7 com prompt do agent decoder, escrevendo em `_diagnostics/stage1_sample_test/<id>_opus.md` (baseline Sonnet em `systems/<id>/signal_rule.md` preservada).

## Resultados

| system_id | n_trades | label original | family Sonnet | conf Sonnet | family Opus | conf Opus | reclass | nota |
|---|---:|---|---|---:|---|---:|---|---|
| 10067081 | 4000 | PARTIAL | UNCATEGORIZED | 0.43 | UNCATEGORIZED | 0.40 | ❌ | agreement |
| 10192401 | 420  | DECODED | FACTOR_SCALPING | 0.52 | OVERLAP_NY_LONDON_RANGE | 0.58 | ✅ | tree single-feature dominance bb_pos_20_2_H1 (87% CV); BTC entry 15-18 UTC + BB-driven direction matches NY/London overlap, não scalping multi-fator |
| 10475089 | 117  | DECODED | UNCATEGORIZED | 0.38 | UNCATEGORIZED | 0.42 | ❌ | agreement |
| 1612420  | 788  | PARTIAL | OVERLAP_NY_LONDON_RANGE | 0.52 | UNCATEGORIZED | 0.40 | ✅ | name "Happy News" + 45% trades em bucket 15:30 UTC + 50/50 buy% por hora + ret_3_H4 momentum-following = clock-anchored news-release momentum, taxonomy não tem classe NEWS |
| 8577442  | 934  | PARTIAL | OVERLAP_NY_LONDON_RANGE | 0.52 | UNCATEGORIZED | 0.40 | ✅ | mediana hold 192h (~8 dias) + top hour só 11.9% disqualificam todas as famílias intraday; H4 EMA-distance domina, taxonomy não tem swing-H4 family |

**Reclass rate: 3/5 = 60%**.

## Padrão observado

2 dos 3 reclass vão de família labeled → UNCATEGORIZED. Sonnet rotula com base em timing sem cruzar com hold distribution / sign da regra / nome do system. Mesmo padrão observado em Wave 1+2+3 (Pool A+B selecionado a priori como suspeito, 73% reclass) reaparece em amostra aleatória (60% reclass).

Conclusão: classificação Sonnet é **sistemicamente frágil** quando fingerprint+candidates apresentam ambiguidade. Não é viés do pool suspeito da Wave 1+2+3.

## Ações implicadas (escala para usuário antes de Wave B)

> ⚠ Threshold 30% disparado em 60% — não basta consertar enum (Wave B item 2). Possíveis caminhos:
>
> 1. **Re-decodificar todos os 23 DECODED + 7 PARTIAL com Opus** antes de Phase 5R-2/5R-3 (custo: ~$15-25, ~25-30 systems × $0.50). Aceita o achado e remedia integralmente.
> 2. **Aceitar UNCATEGORIZED como label dominante** e ajustar score formula 5R-3 para tolerar UNCAT como classe legítima (família não bloqueia score; sanity ortogonal).
> 3. **Adicionar famílias à taxonomia** (`NEWS_RELEASE_MOMENTUM`, `SWING_H4_TREND`, `H1_MOMENTUM_GOLD` already provisional) para reduzir o peso de UNCATEGORIZED como bucket-de-fuga.
> 4. **Revisar Stage 1 (fingerprint extraction)** — bug NaN em hold extraction (5+ systems reportam hold p50/p95/max=NaN) é parcialmente responsável; consertar antes de re-decode reduz custo Opus.
>
> Recomendação do orchestrator: combinação de (4) primeiro (consertar hold extraction) + (1) seletivamente sobre os 8 DECODED não-rechecados (custo ~$4) + (3) parcial (avaliar caso-a-caso) antes de Wave B fechar enum.

**Aguardando decisão do usuário.**

## Reprodutibilidade

```bash
python3 -c "
import random
pool = sorted(['10067081','10192401','10249298','10251631','10475089','10563761','10734338','11355455','1152318','1603276','1612420','8577442','9830783','9841939','9843883'])
random.seed(42)
print(sorted(random.sample(pool, 5)))
"
# → ['10067081', '10192401', '10475089', '1612420', '8577442']
```

## Citações

- Aronson `[evidence_based_ta, p.281, p.291]` — small-sample bias, necessidade de cross-validation aleatória contra confirmação seletiva. Justifica o sample test como antídoto à seleção a priori da Wave 1+2+3.
- López de Prado `[advances_fin_ml, ch.7]` — purged k-fold como protocolo OOS independente.

## Output files

- `10067081_opus.md` — Opus re-decode (UNCATEGORIZED 0.40)
- `10192401_opus.md` — Opus re-decode (OVERLAP_NY_LONDON_RANGE 0.58)
- `10475089_opus.md` — Opus re-decode (UNCATEGORIZED 0.42)
- `1612420_opus.md`  — Opus re-decode (UNCATEGORIZED 0.40, news momentum)
- `8577442_opus.md`  — Opus re-decode (UNCATEGORIZED 0.40, swing H4)

Custo total estimado: ~$2-3 (5 × Opus subagents, ~30k-40k tokens cada).
