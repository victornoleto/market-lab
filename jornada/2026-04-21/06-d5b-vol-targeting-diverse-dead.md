# D5b — Vol-targeting Structural Diversity: Hipótese Errada (iter 10) [SWING BROKER]

**Veredito:** DEAD END — PBO=0.651 (pior que D5's 0.599)

**Data:** 2026-04-21

---

## O que tentamos

D5 tinha 7 configs de vol-targeting similares e PBO=0.599 (falha por 0.099).
A hipótese de D5b: "diversidade estrutural entre configs → IS-melhor sempre domina OOS → PBO cai".

Testamos 3 famílias estruturalmente diversas no mesmo ativo TQQQ+GLD:
1. `sma200_gld` — regime binário puro (SMA200 do SPY, sem vol-scaling)
2. `vol15_lk20` — vol-targeting contínuo puro (15%, lb=20d)
3. `vol15_lk20_sma200` — combo: vol-target × overlay de regime

Resultado: PBO=**0.651** — pior, não melhor.

---

## Por que a hipótese falhou

A confusão era entre "diversidade de família" e "consistência de ranking OOS".

PBO mede se o config IS-melhor também é OOS-melhor nos splits CSCV. O que
importa não é se os configs são diferentes entre si, mas se O MESMO config
domina em TODOS os períodos de IS e OOS.

O problema com configs heterogêneos:
- `sma200_gld` vence IS em períodos bull fortes (100% TQQQ, retorno alto)
- `vol15_lk20` vence IS em períodos moderados (peso adaptativo, Sharpe alto)
- O IS-vencedor MUDA entre splits → quando muda, tende a perder OOS

Com configs homogêneos (D5, 7 configs similares): o IS-vencedor é selecionado
por pequena diferença aleatória → qualquer dos outros pode superar OOS → PBO alto.
Com configs heterogêneos (D5b, 3 famílias): o IS-vencedor muda por regime →
mesmo problema, PBO alto.

---

## Insight crítico: quem passa PBO nesta família?

**D2 (regime binário SMA/EMA × cash/GLD/TMF): PBO=0.115 ← PASS**

Configs binários ON/OFF têm PBO baixo porque o sinal SMA200/EMA100 é
**regime-consistente**: em qualquer bloco de IS, a mesma config (sma200_gld)
tende a dominar porque a vantagem é estrutural, não aleatória.

A barreira: D2 sma200_gld tem Sharpe_net=0.780 (gate=0.800, gap=0.020).

**Conclusão:** o único caminho para PBO < 0.5 nesta família é via regime
**binário** (como D2), não vol-targeting contínuo. D6 usa composite score
binário (MA slope + momentum + 1/vol > 0 → TQQQ, else GLD) que mantém o
caráter ON/OFF mas com sinal mais sofisticado que pode boostar Sharpe_net
acima de 0.800.

---

## Métricas D5b (3 configs, janela 2004-2026, 21.4yr)

| Config | Sharpe | Sharpe_net | MaxDD% | Calmar | WF | PBO |
|--------|--------|------------|--------|--------|----|-----|
| sma200_gld | 0.760 | 0.646 | -63.7 | 0.413 | 8/8 | 0.651 |
| vol15_lk20 | 1.006 | 0.855 | -37.2 | 0.573 | 8/8 | 0.651 |
| vol15_lk20_sma200 | 0.956 | 0.813 | -30.2 | 0.646 | 8/8 | 0.651 |

SPY B&H net CAGR threshold: 7.31% — todos batem ✓

Nota: sma200_gld tem Sharpe mais baixo aqui (0.760) vs D2 (0.918) porque
D5b usa janela 2004-2026 (inclui sintético pré-2010) enquanto D2 usa 2010-2026
(pós-inception TQQQ real).

---

## Próximo: D6 — Composite Score Binário (Clenow)

Composite score = w1·slope_MA200 + w2·mom_90d + w3·(1/vol_20d)
Score > 0 → 100% TQQQ, Score ≤ 0 → 100% GLD (binário como D2)
3 triplas de pesos — mantém caráter ON/OFF (PBO esperado baixo como D2)
Se score composto é mais preciso que SMA200 puro, Sharpe_net pode superar 0.800

Citações: [stocks_on_the_move, p.81, ch.6]
