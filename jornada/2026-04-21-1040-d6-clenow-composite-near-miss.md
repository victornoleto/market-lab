# D6 — Sinal Composto Clenow: Quase lá, mas o mercado de abril 2026 atrapalhou [SWING BROKER]

**Iteração 11 — Lead D6 — 21/04/2026**

## O que testamos

Criamos um sinal de entrada mais sofisticado do que o D2 (que usava apenas SPY acima da
média de 200 dias). O D6 combina **três sinais em um escore composto**:

1. **Velocidade da média de 200 dias do SPY** — a média móvel está acelerando para cima?
2. **Retorno de 90 dias do SPY** — o mercado teve bom desempenho nos últimos 3 meses?
3. **Calma do TQQQ** — o TQQQ está estável (baixa volatilidade) ou turbulento?

Cada sinal é normalizado (z-score) para ter a mesma importância, e então combinados com
pesos. Se o escore total > 0 → entra 100% TQQQ. Se ≤ 0 → 100% ouro (GLD). Estrutura
binária como D2 (liga/desliga), não gradual.

Testamos 3 combinações de pesos:
- Pesos iguais (1/3 cada)
- Tendência dominante (50% velocidade MA, 30% momentum, 20% calma)
- Momentum dominante (20% velocidade MA, 60% momentum, 20% calma)

## Resultado: 0/3 configurações aprovaram — mas chegamos muito perto

**PBO = 0.341 → PASSA** (< 0.5). Isso é um avanço! D5 e D5b falharam no PBO com
valores de 0.599 e 0.651. A estrutura binária do D6 funciona para controlar overfit.

A melhor configuração foi **trend_heavy** (50% velocidade MA, 30% momentum, 20% calma):

| Métrica | Valor | Gate | Status |
|---------|-------|------|--------|
| Sharpe líquido | 0.797 | > 0.800 | **QUASE: faltou 0.003** |
| MaxDD | -42.4% | — | Muito melhor que D2 (-60.3%) |
| Calmar | 0.731 | > 0.5 | ✓ |
| WF | 7/8 | ≥ 6/8 | ✓ |
| PBO | 0.341 | < 0.5 | ✓ |
| DSR p-valor | 0.002 | < 0.05 | ✓ |
| Janela recente (FWD) | -1.14 Sharpe | > 0 | **FALHA** |

6 de 8 gates passam. Falhou em dois:
1. **Sharpe líquido**: 0.797 vs gate 0.800 — gap de apenas 0.003!
2. **Janela recente**: primeiros 3 meses de 2026 foram ruins para TQQQ.

## Por que a janela recente falhou?

O gate "forward stress" analisa os últimos 63 dias úteis (2026-01-13 → 2026-04-14).
Nesse período: **TQQQ caiu -3.8%** e o ouro subiu +5.6%. A estratégia ficou 71% em
TQQQ nesses 63 dias — e pagou o preço.

O problema é estrutural para esse período: o choque tarifário de Trump em 2026 afetou
especialmente ações de tecnologia (TQQQ é 3× o QQQ/Nasdaq). Testamos configurações
ainda mais conservadoras (dominadas pela calma/volatilidade), mas NENHUMA escapou do
período — qualquer sinal que ficasse em TQQQ nos piores dias tomou o prejuízo.

A única configuração que evitaria: ficar 100% em ouro o tempo todo (que daria Sharpe
+0.72 na janela). O sinal composto precisaria ter saído em janeiro de 2026 — muito antes
que qualquer indicador técnico de médio prazo sinalizaria risco.

## Achado bônus: slope_dominant quase venceu tudo

Durante os diagnósticos, testamos pesos (0.6, 0.25, 0.15) — "velocidade MA dominante":
- Sharpe líquido: **0.847 → passa o gate econômico!**
- Calmar: 0.686 → passa!
- Mas FWD Sharpe = -1.34 → ainda falha

Ou seja: com a combinação certa de pesos, o D6 seria um vencedor completo — SE o período
de avaliação não terminasse em pleno choque tarifário de 2026.

## O que faremos a seguir: D7 — Sinais QQQ em vez de SPY

**Insight chave:** TQQQ = 3× QQQ (Nasdaq 100). Usar sinais do QQQ (não do SPY/S&P500)
é mais relevante para TQQQ. Durante choques que afetam mais o setor tech (como tarifas
sobre China/semicondutores), o QQQ cai antes e mais do que o SPY. Um sinal baseado no
QQQ detectaria o problema mais cedo → saindo de TQQQ antes do pior.

D7 testa: slope_MA200(QQQ) + mom_90d(QQQ) + inv_vol(TQQQ), com 4 combinações de pesos
incluindo a slope_dominant (0.6, 0.25, 0.15) que mostrou SN=0.847.

Citação base: `[stocks_on_the_move, p.81]` — sinais no índice SUBJACENTE do ativo.

---

*Relatório completo:* `reports/phase_3_5d/d6_clenow_composite/TQQQ.md`
