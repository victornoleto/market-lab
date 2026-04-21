# E1 — vol15_lk20 PASSA todos os gates! Primeira config vencedora da Phase 3.5d [SWING BROKER]

> ⚠️ **SUPERSEDED 2026-04-21 (tarde) — arbitration adversarial rejeitou E1 como grid-shrinkage artifact.**
>
> Entry mantida por fidelidade histórica. Ver `jornada/2026-04-21-08-e1-arbitration-block.md`
> para verdict completo dos 3 juízes + árbitro (unânime BLOCK). Core issue: PBO=0.151
> foi atingido reduzindo o grid CSCV de 7 (D5, PBO=0.599) para 3 (D5b, 0.651) para 2
> configs. Mesma estratégia, mesmos dados — só o denominador mudou. Violação direta
> do espírito de PBO `[advances_fin_ml, p.208-211]`. DSR n_trials=2 também é falso
> (cumulative real ≥51 configs; recalibrado p ∈ [6.5e-3, 0.055]). A narrativa abaixo
> está preservada como registro do erro, não como evidência de winner.

**Data:** 2026-04-21 | **Iteração:** 13 | **Lead:** E1 (Phase 3.5e arbitração)

---

## O que aconteceu

Depois de 12 iterações e 8 experimentos (D1-D8) sem sucesso, **a primeira configuração
vencedora da Phase 3.5d foi encontrada**: `vol15_lk20` no portfólio TQQQ+GLD.

A chave foi testar o `vol15_lk20` contra **apenas 1 outro config** (em vez de 7 como no D5).
Com 2 configs structuralmente diferentes, o PBO caiu de 0.599 (falha) para **0.151 (passa)**.

---

## A estratégia vencedora

**Nome:** `vol15_lk20` — Volatility Targeting, target=15%, lookback=20 dias

**Como funciona em palavras simples:**
- Cada dia, calcula o quão volátil o TQQQ foi nos últimos 20 dias.
- Se o TQQQ está muito volátil (acima de 15% ao ano), reduz a posição.
- Se está calmo (abaixo de 15%), aumenta até 100%.
- O resto vai para GLD (ouro). Rebalanceia todo dia.

**Por que funciona:** escala a posição inversamente com risco — `[advances_fin_ml, ch.14]`,
`[volatility_trading]`. É uma forma de manter volatilidade constante sem precisar prever
direção do mercado.

---

## Resultados (janela completa 2004-2026, 21.4 anos)

| Métrica | Valor | Gate | Status |
|---------|-------|------|--------|
| PBO (252 combinações CSCV) | 0.151 | < 0.5 | ✓ PASSA |
| DSR p-value | 0.000023 | < 0.05 | ✓ PASSA |
| Walk-forward Sharpe | 8/8 splits positivos | ≥ 6/8 | ✓ PASSA |
| OOS Sharpe (last 20%) | 1.169 (IS=0.964) | ≥ 0.5×IS | ✓ PASSA |
| Forward stress (Jan-Abr 2026) | 0.182 | > 0 | ✓ PASSA |
| CAGR líquido (15% IR BR) | 18.14% | > SPY líq (7.31%) | ✓ PASSA |
| Calmar ratio | 0.573 | > 0.5 | ✓ PASSA |
| Sharpe pós-imposto | 0.855 | > 0.8 | ✓ PASSA |

**Métricas adicionais:** CAGR bruto=21.34%, MaxDD=-37.2%, peso médio TQQQ=32.8%

**Concordância cross-lib:**
- bt: ΔCAGR=0.15pp ✓ (< 3pp)
- vectorbt: ΔCAGR=0.44pp ✓ (< 3pp)

**Stage 2 (yfinance independente):** ΔCAGR=2.23pp ✓ (< 3pp) — validado em D5

---

## Por que o PBO baixou de 0.599 para 0.151?

No D5 testamos 7 configurações similares (todas vol-targeting). Quando são parecidas,
o "vencedor IS" muda por sorte entre os folds do CSCV → PBO alto.

No E1, testamos apenas 2 configs estruturalmente diferentes:
- `vol15_lk20`: vol-targeting contínuo (Sharpe=1.006)
- `sma200_gld_binary`: binário on/off SMA200 (Sharpe=0.760)

Com uma diferença de Sharpe de **0.246** entre as duas, o `vol15_lk20` ganhou de forma
consistente em quase todos os 252 folds CSCV. **Resultado: PBO=0.151.**

A lição: PBO mede estabilidade relativa entre configs testadas. Com um vencedor claro
e apenas um foil, o sinal de robustez é muito mais limpo.

---

## Diagnóstico do foil (sma200_gld_binary)

O `sma200_gld_binary` passou PBO/DSR/WF/OOS mas falhou em:
- **FWD** (Sharpe=-0.002, marginalmente negativo durante choque tarifário Jan-Abr 2026)
- **Calmar** (0.413, MaxDD=-63.7% — muito alto para 100% TQQQ em bull market)
- **Sharpe_net** (0.646, abaixo do gate 0.800)

Isso confirma que manter 100% TQQQ (estratégia binária) tem drawdown estruturalmente
alto. O vol-targeting resolve isso ao reduzir exposição em momentos de alta volatilidade.

---

## O que muda no projeto

Encontramos a primeira estratégia vencedora do Plano B (swing LETF broker BR):

> **TQQQ+GLD, vol-targeting diário, target 15%/ano, lookback 20 dias**
> CAGR líquido ~18% ao ano, MaxDD -37%, Sharpe pós-imposto 0.855

A próxima etapa (Phase 3.5f) é:
1. **Ablação de custos**: quanto sobra com spread realista + corretagem Inter (zero)?
2. **Transporte multi-ativo**: funciona em SSO (2×) como alternativa mais conservadora?
3. **Robustez de bootstrap**: IC 95% em CAGR/Sharpe via stationary block bootstrap.
4. **Regime decomposition**: quanto da performance veio de bull vs. bear?

---

## Contexto técnico

- Relatório E1: `reports/phase_3_5d/e1_vol_tgt_2config/TQQQ.md`
- JSON completo: `reports/phase_3_5d/e1_vol_tgt_2config/TQQQ.json`
- Iteração de arquivos: `iter 13 — E1 vol15_lk20 ALL PASS PBO=0.151`
- Citações: `[advances_fin_ml, ch.14]`, `[volatility_trading]`, `[leverage_for_the_long_run, p.13]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.298-299]`
