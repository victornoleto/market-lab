# 2026-04-15 (tarde, segundo round) — Long-history Ehlers SPY (2005-2023) — FAIL

**Hipótese:** se o DSR está falhando por "testamos 24 configs em amostra
pequena demais", aumentar a janela de 9 anos para 19 anos triplica os
dados. A deflação do DSR depende de `Z(N)/√(T-1)`; mais T = divisor
maior = deflação menor. Zero código novo — só uma janela mais antiga.

**O que rodamos:** mesma grid Ehlers puro (24 configs), SPY 2005-2023
(4781 bars vs 2264 bars anteriormente), Tiingo.

**Resultado comparativo:**

| Métrica | Baseline 2015-2023 | Long 2005-2023 |
|---|---|---|
| PBO | 0.496 ✅ | **0.405 ✅ (melhorou)** |
| DSR 0/24 pass | ✅ reject | ❌ reject |
| DSR best p-value | 0.332 | **0.213 (melhorou, mas ainda fail)** |
| Walk-forward | 7/24 | **0/24 (piorou)** |
| Best Sharpe | 0.806 | 0.639 |
| Best config CAGR | — | 9.25% |
| Best config DD | — | 29.44% |

**Leitura leiga:**
- Aumentar a janela **ajudou** no PBO (overfitting) e **aproximou** o
  DSR do limiar (p 0.332 → 0.213; precisaria < 0.05 pra passar).
- Mas **quebrou o walk-forward**: com 19 anos divididos em 8 janelas,
  cada janela pega ~2.4 anos. E a janela 2005-2023 contém 2008-09
  (subprime), 2011 (debt ceiling), 2015 (correção), 2020 (COVID), 2022
  (juros). Cinco crises em oito janelas — parâmetros fixos não
  adaptam.
- A melhor config individual (hp=48, lp=20, pct=0.80, stop=0.02) teve
  6/8 janelas lucrativas (consistente!), mas drawdown máximo de
  **29%**, acima do gate de 25%. Quase passou — foi cortada por pouco.

**Conclusão:** a estratégia tem edge "real-mas-frágil". Em janela curta
ela passa no profitable/DD mas falha no DSR (sample pequeno). Em
janela longa ela melhora DSR/PBO mas quebra em crises específicas. Nem
uma janela nem a outra é a solução isolada.

**Próximo passo recomendado (F3.D no plano):** portfolio combinado
Clenow + Ehlers. As duas estratégias têm correlação ≈ −0.01 (ortogonais).
Combinar numa proporção volatility-scaled 50/50 pode elevar o Sharpe
efetivo (diversificação) **e** reduzir o drawdown em crises (Clenow
tende a "sair do mercado" via regime filter, Ehlers tende a
"oscilar"). Mas isso é código novo — vale alinhar com o usuário antes.

**Arquivos gerados:**
- `reports/grid_ehlers_20260415-1353/diagnostic.md` (24 configs, 19
  anos).
