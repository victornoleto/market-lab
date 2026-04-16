# 2026-04-15 (tarde) — Run 4 Step 1 (AFML rescue Ehlers SPY) — FAIL

**O que tentamos:** adicionar um "segurança" inteligente em cima do
Ehlers. A estratégia Ehlers identifica quando há uma oscilação pra
comprar barato e vender caro. Mas nem toda oscilação é tradável — às
vezes é ruído, às vezes a oscilação quebra no meio. A ideia do meta-
labeling (López de Prado, AFML) era treinar um modelo de Machine
Learning (RandomForest) pra olhar pros sinais e decidir
*"essa oscilação aqui parece boa, vamos tradear"* vs *"essa aqui é
ruidosa, pula"*.

**O que rodamos:** 48 configurações (5 eixos: hp × lp × pct × stop ×
threshold), SPY 2015-2023, Tiingo survivorship-free, treinou o
RandomForest nos primeiros 50% de eventos e filtrou os restantes.

**O que aconteceu:**
- **PBO 0.647** (vs 0.496 da baseline Ehlers puro) — **piorou**.
- **DSR 0/48 configs passam** p<0.05 (pior p=0.701 vs 0.332 baseline).
- **Walk-forward 0/48** passam (baseline tinha 7/24).
- **Melhor Sharpe:** 0.575 (config #18) — **abaixo da baseline 0.806**.

**Interpretação leiga:** o filtro foi ingênuo demais. O modelo foi
treinado em poucos exemplos (~50-100 eventos na primeira metade), com
split temporal simples (sem walk-forward CV com embargo). Ele acabou
cortando trades bons junto com ruins, reduzindo tanto o Sharpe quanto a
quantidade de sinal. E ainda por cima, dobrar o número de configs
testadas (24 → 48) aumentou o critério do DSR ser ainda mais rigoroso.

**Não é um enterro do AFML — é um enterro da versão simples dele.** O
"jeito certo" tem várias partes que pulamos:
- Cross-validation temporal com embargo (não split 50/50 único).
- Mais features (volume, RSI de curto, variáveis de outros ativos).
- Mais eventos (janela longa 1993-2026 em vez de 2015-2023).

**Decisão:** em vez de consertar o AFML agora, vamos testar o próximo
barato da lista: **rodar o Ehlers puro numa janela longa**. Se
funcionar, matamos o problema sem precisar de ML. Se não, voltamos pro
AFML com mais cuidado.

**Arquivos gerados:**
- `reports/grid_ehlers_meta_20260415-1349/diagnostic.md` (48 configs
  detalhadas).
- `src/ai_trade/backtest/strategies/ehlers_meta.py` (implementação,
  permanece no código — tem valor educacional e base para retomada).
- `scripts/run_grid_ehlers_meta.py` (orquestrador, permanece).
- `tests/test_ehlers_meta.py` (10 novos testes, 360/362 passando).
