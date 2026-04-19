# 2026-04-17 1310 — Phase 3.5b Task 7a [PLANO B] FFR gate DISPARADO

## TL;DR

O cross-check testfolio vs nossa função `synthesize_letf_returns` (Gayed
flat-1% fee) dispara o **FFR-aware gate** com folga: gap médio de
**+6.0%/ano** na janela 1962-01-03 → 2026-02-27 (16,146 dias úteis),
concentrado no regime de juros altos (**+9.72%/ano no bucket FFR≥5%,
32 anos de dados**). Implementei `synthesize_letf_returns_ffr_aware()`
como **nova função** (a antiga intacta), com 11 testes unitários novos.
Pytest: 587 → **597 passed**. Winner Phase 3 B1c **não alterado ainda** —
próxima iter re-roda os gates com a nova função e decide.

## Contexto

Task 7a do `specs/phase_3_5b_winners_validation.md` pede comparar três
curvas de equity 2x em 1962-2026:

1. Nossa síntese: `synthesize_letf_returns(spx_tr, L=2, fee=0.01)` —
   fórmula Gayed `r = L·r_spx − 0.01/252`
   [`leverage_for_the_long_run, p.16`].
2. Testfolio `spy_2x_equity` — custo `SW·(L−1)·(FFR+SP)`, time-varying.
3. UPRO/SSO reais (Tiingo) pós-2006/2009.

Se o gap nosso-vs-testfolio passar **2%/ano em algum bucket FFR com
≥5 anos**, temos que fazer uma função FFR-aware e re-rodar B1c.

## O que eu fiz

### Script de análise

`scripts/robustness_testfolio_vs_synthetic_letf.py` (novo, 190 loc).
Loader do testfolio parquet + KF daily + `load_spx_tr_daily` stitched.
Alinha na interseção de datas, reconstrói equity a partir de retornos
(não usa o start value absoluto do parquet, que é 1885) e agrupa por
ano calendário em buckets de FFR anualizado médio.

### Finding: UPRO/SSO não estão no Tiingo

Inspeção do `data/tiingo/manifest.json` (2026-04-17): **UPRO, SSO, SPXL,
SPUU ausentes**. A comparação 3-way vira 2-way. Isso é uma lacuna
conhecida; flaguei no relatório e no memory. Iter futura precisa puxar
UPRO (2009-06+) e SSO (2006-06+) pro Tiingo pra fechar o 3-way. O gap
Gayed-vs-UPRO real do paper (p.21, Table 12 ≈ 2-3%/ano no 3x 2009-2020)
não pode ser verificado aqui.

### Resultados numéricos (janela 1962-01-03 → 2026-02-27, 64.1 anos)

**Full-window CAGR:**

| Série | CAGR |
|-------|------|
| Synth 2x (flat 1%) | **17.41%** |
| Testfolio 2x (FFR-aware) | 11.41% |
| **Gap (synth − tf)** | **+6.00%/yr** |

Gap positivo = nossa síntese **superestima** o return (sub-modela o custo).

**Por bucket FFR:**

| Bucket | Anos | FFR médio | Synth CAGR | Testfolio CAGR | Gap |
|--------|-----:|----------:|-----------:|---------------:|----:|
| FFR<2%  | 15 | 0.87% | 25.61% | 25.16% | **+0.46%** |
| 2≤FFR<5% | 18 | 3.27% | 19.29% | 15.15% | **+4.15%** |
| FFR≥5% | 32 | 7.42% | 12.55% | 2.84% | **+9.72%** |

**GATE TRIGGERED**: bucket FFR≥5% tem 32 anos de dados e gap +9.72%/ano
(≫ 2%/ano). Bucket 2-5% também passa do gate (+4.15% em 18 anos). Só
o bucket <2% (era pós-GFC 2010-2022) está dentro do threshold.

### Implicação imediata para o winner B1c Phase 3

A janela IS do B1c é **1970-2000** — FFR médio nesse trecho é ~8%
(Volcker, pós-Volcker, final 90s alto). Isso cai inteiro dentro do
bucket FFR≥5% onde nossa síntese superestima CAGR em quase 10%/ano.

Se o cost real do 2x leverage nos anos 70-90 era 6-12%/ano e nós
modelamos 1%/ano, o Sharpe IS do LETF rotation winner (1.854) é
quase certamente inflado. **Mas**: a LRS só fica alavancada quando
ON-regime (~70% do tempo em Gayed's numbers), então o erro efetivo
sobre a equity final é menor que o gap bruto — precisa ser medido.

### Implementação FFR-aware

Adicionei `synthesize_letf_returns_ffr_aware()` em
`src/ai_trade/backtest/helpers/synthetic_letf.py`:

```
annual_cost[t] = SW·(L−1)·(FFR[t] + SP) + expense_ratio
r_synth[t] = L·r_spx[t] − annual_cost[t]/252
```

Defaults testfolio: `SW=1.1`, `SP=0.004`, `expense_ratio=0.0095`.
Input FFR é reindexado e `ffill + bfill` pra absorver diffs de
calendário KF vs SPY. 11 testes novos cobrem:
formula match, L=1 reduz a expense_ratio, FFR=0 só spread sobre swap,
time-varying FFR, ffill, bfill, no-overlap raise, L=0 raise,
gap vs flat model > 0.5%/ano numa simulação controlada.

**Função antiga `synthesize_letf_returns` intacta** (constraint #9
do memory: precisa manter o Gayed paper original pra compat).

## Limitação (⚠️ FLAG)

- **UPRO/SSO reais ausentes do Tiingo** — 3-way reduzido a 2-way.
  Não consigo confirmar se o testfolio model bate com UPRO/SSO real
  ou se diverge em direção à nossa síntese. Confiabilidade da
  conclusão depende de o testfolio ser de fato fiel a UPRO/SSO real
  na sub-janela onde existem (2006+ / 2009+). Iter futura resolve.

- **Expense ratio additivo**: eu modelei o ER como adição (fund
  operations + swap cost). Testfolio pode estar colocando isso dentro
  do SW; precisa verificar no curl payload. Se estiver, meu ER=0.95%
  é double-count e o gap aware-vs-testfolio vai ficar ~0.9%/ano
  negativo. Teste de calibração na próxima iter.

## Próxima iteração (Task 7a parte 2)

Re-rodar B1c gates (`tests/test_letf_rotation_b1c.py` ou grid direto)
com `synthesize_letf_returns_ffr_aware()` injetando a série FFR de
Ken French. Se o winner sobreviver (PBO<0.5, DSR p<0.05, WF≥6/8) → ok,
Phase 3 LETF winner continua válido. Se cair → é **⚠️ flag crítica**
(winner imutável Phase 3.5b, mas ficar registrado para a `status:
done` da allocation doc).

## Artefatos

- `scripts/robustness_testfolio_vs_synthetic_letf.py` (novo)
- `reports/phase3_5b/robustness/testfolio_vs_synthetic_letf.md` (novo)
- `reports/phase3_5b/robustness/testfolio_vs_synth_yearly.csv` (novo)
- `reports/phase3_5b/robustness/testfolio_vs_synth_buckets.csv` (novo)
- `src/ai_trade/backtest/helpers/synthetic_letf.py` (modificado: +1 função,
  +3 constantes)
- `tests/test_helpers_synthetic_letf.py` (modificado: +11 tests)

## Pytest

587 → **597 passed** (+10 novos, +1 `test_defaults_match_testfolio`
que é assert on constants). Baseline preservado.

## Citações

- Custo `SW·(L-1)·(FFR+SP)`: `data/external/README.md` Task 7a.
- Expense ratio UPRO 0.95%: `[leverage_for_the_long_run, p.16]` fn.23.
- Pre-1962 exclusion: `data/external/README.md` lines 75-83.
- Gayed flat-fee mantido intacto: `[leverage_for_the_long_run, p.16]`.
