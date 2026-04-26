# Strategy Hunt — resumão pro celular

*Pra ler na cama. Versão completa em `FINAL_REPORT.md`.*

---

## TL;DR (3 frases)

Rodamos 74 iterações em ~32h, achamos **3 estratégias que batem o SPY/QQQ
em retorno E em Sharpe** num teste de 40 anos (1986-2026). A campeã pra
**máximo retorno** é absurdamente simples: 90% SPY + 60% bond longo +
30% ouro, sem sinal nenhum (iter 035). A campeã pra **melhor relação
risco/retorno** adiciona uma camada de "vol-target" em cima dessa mistura
e corta o drawdown pela metade (iter 016/074).

---

## 🥇 Top 3 candidatos pra deploy

### 1. Pra MAIS GRANA: `static_stack_90_60_spy_gld` (iter 035)
- 40 anos sintéticos: **CAGR 19.6%** (vs SPY 11.5%) — **+8 pontos por ano**
- Sharpe 0.92 (vs 0.68 do SPY)
- Drawdown 46% — parecido com SPY (55%)
- Como funciona: portfolio mensal/trimestral 90% SPY + 60% bond longo + 30% ouro = 180% notional
- **Pra quem quer "mesmo perfil do SPY mas amplificado"**

### 2. Pra DORMIR BEM: `ntsx_vm_vt15_L21_cap20` (iter 016/074)
- 40 anos: Sharpe **0.95** (vs 0.68 do SPY) — melhor relação risco/retorno
- CAGR 15.1% (vs SPY 11.5%)
- **Drawdown 34.6% (−20 pontos vs SPY 55%)**
- Como funciona: mesma mistura 90/60 mas todo dia recalcula vol e ajusta tamanho pra atingir 15% vol-target
- **Pra quem quer dormir tranquilo na próxima crise**

### 3. Pra DEFESA SIMPLES: `vol_managed_60_40` (iter 006)
- 40 anos: Sharpe 0.93, CAGR 14.4%, MDD 34.7%
- Praticamente igual ao iter 016 mas sem a camada NTSX (mais simples)
- 60% SPY + 40% bond, com vol-target em cima

---

## 📊 Como sabemos que não é coincidência

Validei de 3 formas:

**1) 4 bibliotecas concordam**
Recalculei Sharpe/CAGR/MDD com pandas, numpy, vectorbt e quantstats
para os top-20. Todos os 180 valores bateram (<1% de diferença). Não é
bug de fórmula.

**2) Janela de 40 anos**
Rodei as estratégias simples nos dados sintéticos do testfolio
(1986-2026, inclui crash de 87, dot-com, 2008, COVID, 2022). Todas as
6 estratégias simples dominam o SPYSIM em retorno E em Sharpe. Não é
"sorte da década 2009-2026".

**3) 7 testes estatísticos por iteração**
Cada estratégia passou por bateria de gates (PBO, DSR, walk-forward,
OOS, FWD, bootstrap, cross-lib). Top 3 passam 6-7 de 7 nos 3 datasets.

---

## 🧠 O que NÃO funcionou (lições)

- **Sector momentum** (rotação de SPDRs): morreu. Universo pequeno demais.
- **Vol-scaling em ativo único** (só SPY): teto em +0.10 Sharpe. Não
  escala.
- **Meta-labeling com ML**: regrediu. ML em cima de sinal já bom não
  ajuda.
- **Overlay de momentum simples** sobre vol-managed: regrediu também.

A direção que VENCEU foi **stacking estático multi-asset** (a iter 035
e família). O segredo não foi sinal nem ML — foi a combinação correta
de classes de ativos com pesos fixos.

---

## ⚠️ O que ainda falta antes de deploy

1. **Re-validar em vectorbt/backtrader do PREÇO** (não só do retorno).
   Hoje validamos só os números finais; falta confirmar que o motor
   de backtest reproduz o mesmo resultado em outros engines. Faltam
   2-4 dias de trabalho.
2. **Modelar slippage e custos reais** no Inter Internacional. Hoje
   assumimos 2 bps/trade. Real provavelmente come 50-150 bps de CAGR.
3. **Paper trading** em conta real por algumas semanas antes de capital
   significativo.
4. **Override do mandate §7** (continua MAINTENANCE 100% Plano C).
   Mesmo se fôssemos deployar, precisa decisão consciente de mudar
   alocação.

---

## 🔄 O que está rodando agora (overnight)

- Loop iter 075-100 rodando em background (PID 2386820)
- Começou 23:20 hoje, deve terminar ~6h-8h da manhã
- Pode encontrar candidato melhor (improvável, mas possível)
- Roda em branch separada (`strategy-hunt-relaxed/iter-075-100`)
  então não impacta nada que você pode estar fazendo em paralelo

Quando terminar, vou regerar o `FINAL_REPORT.md` com os top-K finais.

---

## 📁 Onde olhar (pelo PC)

- **Resumão técnico completo**: `studies/strategy_hunt_loop/FINAL_REPORT.md`
- **Plot 40y top-5**: `studies/strategy_hunt_loop/LONG_WINDOW_TOP5_vs_SPYSIM.png`
- **Plot 40y drawdown top-3**: `studies/strategy_hunt_loop/LONG_WINDOW_TOP3_DRAWDOWN.png`
- **Plot iter 035 vs SPY**: `studies/strategy_hunt_loop/iterations/035-*/plot_vs_benchmark_spy_real.png`
- **Plot iter 016 vs SPY**: `studies/strategy_hunt_loop/iterations/016-*/plot_vs_benchmark_spy_real.png`

Boa noite. 😴
