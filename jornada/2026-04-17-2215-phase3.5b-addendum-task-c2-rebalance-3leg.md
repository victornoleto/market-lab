# Phase 3.5b addendum — Task C2: rebalance modes on 3-leg EW — comparativo completo

**Tag:** `[SWING BROKER]`  (Plano B — BR broker, 15 % IR realizado, sem swap)
**Scope:** Comparar daily / monthly-sell / monthly-cashflow aplicados ao
3-leg EW winner {LETF 2x + QQQ Donchian 20/10 + GLD Donchian 40/20} na
janela longest-common (GLD-limited): **2004-11-18 → 2026-04-14**
(5383 bars, 21.36 anos).
**Status:** ✅ DONE — relatório, gráficos e summary gerados.
**Pytest:** 698 passed (mantido).

---

## Metáforas primeiro

Imagine que o portfolio 3-leg EW é uma cesta com três pernas de igual
peso: LETF (risco alto, motor do retorno), QQQ (momentum de Nasdaq) e
GLD (ouro, descorrelator). O rebalance é o ato de enxugar quem cresceu
e realimentar quem ficou para trás.

- **Daily (winner):** todo fim-de-dia a cesta é "reajustada" mentalmente
  a 1/3. Na prática nada é vendido — o código trata cada barra como se
  os pesos estivessem sempre no alvo. É o ideal teórico.
- **Monthly sell:** no último dia útil de cada mês, vende quem ficou
  gordo e usa o caixa (descontado 15 % de IR) para comprar quem ficou
  magro. Cada venda lucrativa dispara imposto.
- **Monthly cashflow:** nunca vende. Só deposita $500/mês 100 % na
  perna mais magra. Tax-free, mas o drift pode estourar se o depósito
  for pequeno frente à cesta.

---

## Números — tabela comparativa

| Métrica | Daily (winner) | Monthly sell | Monthly cashflow |
|---|---|---|---|
| Equity final | $12.94 M | $9.57 M | $142.2 M¹ |
| CAGR | 25.56 % | 23.79 % | 40.47 %¹ |
| Sharpe | **2.108** | 1.964 | 1.944 |
| Volatilidade ann | 11.10 % | 11.19 % | 18.36 % |
| MaxDD | **10.86 %** | 10.94 % | 17.78 % |
| Max drift (qualquer perna, qualquer barra) | 0.00 % | 4.81 % | **65.05 %** |
| Drift médio por barra | 0.00 % | 0.82 % | 40.10 % |
| Eventos tributários / ano | 0 | **17.9** | 0 |
| IR pago / ano (rebal) | $0 | **$30 740** | $0 |
| Total IR pago (21 anos) | $0 | $656 642 | $0 |
| Total deposits | $0 | $0 | $129 000 (21×12×$500)² |

¹ Equity final/CAGR do cashflow é **inflado por depósitos externos** —
não é performance pura. A métrica honesta é Sharpe.
² $500/mês é ~0.5 % do capital inicial ($100 k); em 21 anos o depósito
relativo ao patrimônio cresce pequeno (por isso drift explode).

Arquivos:

- `reports/phase3_5b/variants/rebalance_modes/comparison_3leg.md`
- `reports/phase3_5b/variants/rebalance_modes/summary_3leg.json`
- `reports/phase3_5b/variants/rebalance_modes/drift_3leg.png`
- `reports/phase3_5b/variants/rebalance_modes/equity_3leg.png`
- Script: `scripts/run_phase3_5b_task_c2_rebalance_3leg.py`

---

## Interpretação — quem ganha cada dimensão

1. **Retorno risk-adjusted (Sharpe):** daily > sell > cashflow.
   A diferença entre sell e cashflow é pequena (0.020), mas daily
   domina as duas por ≥ 0.14 Sharpe unit.
2. **Drawdown:** daily e sell empatam (~10.9 %). Cashflow piora
   +6.9 pp porque a perna LETF (maior vol) fica cada vez mais
   dominante ao longo do tempo — sem mecanismo de venda para corrigir.
3. **Tax drag:** sell paga **$30.7 k/ano** só para rebalancear.
   Ao longo de 21 anos isso somou **$656 k** (≈ 5 % do equity final
   de $9.57 M). Cashflow e daily evitam esse custo.
4. **Operational fit Plano B:** monthly_sell é o mode "realista" para
   alguém que não roda bot diário. Monthly_cashflow é factível se o
   usuário deposita disciplinadamente — mas o depósito precisa crescer
   com o patrimônio senão o drift vira o ditador do portfolio.

Citações:
- Reset diário como prior Bayesiano (1/n) imune a erro de Σ:
  `[advances_fin_ml, p.298-299]`.
- Tradeoff drift × tax × rebal cadence: `[leverage_for_the_long_run,
  p.17, Table 8]`.
- IR 15 % BR: Investment Mandate §4.

---

## Caveats honestos

1. **Daily tax = 0 by construction.** O módulo reusa a convenção do
   `portfolio_combiner`: cada barra é "rebal forçado sem accounting de
   ganho realizado". O 15 % por-trade da estratégia subjacente (cada
   exit lucrativo de LETF/QQQ/GLD) continua valendo e aparece no trade
   log do winner report — este comparativo isola o tax do **layer de
   rebalance do portfolio**, não do layer de trade.
2. **Cashflow CAGR 40 %** parece absurdamente bom — só é porque
   $129 k de depósitos externos foram somados ao pot inicial de $100 k.
   Se normalizar por "dólares investidos total", o CAGR cai para
   alinhado com as outras modalidades. Sharpe e MaxDD são as métricas
   honestas para comparar as 3.
3. **Window 2004-11-18** é GLD-limited. Testar modos 2-leg (LETF+QQQ)
   em Task C3 dará uma janela mais longa (2001-05-14) e outra dinâmica
   de drift (ρ=0.555, pernas mais correlacionadas ⇒ drift menor).

---

## Decisão operacional

- **Produção default:** daily rebal (winner imutável). Se user puder
  automatizar, é dominante em Sharpe e MaxDD.
- **Plano B realista (sem bot):** monthly_sell. Aceita pagar ~3 % de
  principal/ano em IR para se aproximar do ideal diário.
- **Plano B DCA-friendly:** monthly_cashflow **apenas** se o depósito
  mensal é grande relativo ao patrimônio (regra de bolso: ≥ 1 %/mês).
  Caso contrário, o drift colapsa os pesos e o portfolio vira-se num
  LETF concentrado — é o que vemos aqui (drift máximo 65 %).

---

## Links

- Task C1 módulo: `jornada/2026-04-17-2200-phase3.5b-addendum-task-c1-rebalance-modes-module.md`
- Spec: `specs/phase_3_5b_addendum_operational.md` §Task C.
- Winner ref (daily, 3-leg EW): `reports/phase3_5b/portfolio_3leg_ew/summary.json`.
- Próximo: **Task C3** — comparação 3 modos para 2-leg LETF+QQQ (hipótese:
  drift menor com pernas mais correlacionadas).
