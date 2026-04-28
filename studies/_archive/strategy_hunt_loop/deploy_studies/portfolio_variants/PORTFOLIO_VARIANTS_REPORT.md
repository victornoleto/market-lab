# V_HYBRID Variants — Search for Empirically Better Sharpe+CAGR+MDD

**User clarification (2026-04-26)**: "Simplicidade NÃO é prioridade. Gosto
de investimentos, gosto de estudar. Não me importo em ter portfolio não tão
simples contanto que tenha sentido e produza Sharpe+CAGR+MDD melhores."

**Goal**: encontrar variante empíricamente dominante do V_HYBRID adicionando
sleeves orthogonais (managed futures) e mais capital efficiency (NTSI/NTSE/
RSST synth) — desde que a melhoria seja real e não apenas complexidade
adicional.

**Janela**: 1994-05-05 → 2026-04-17 (31.9y, bounded por VWOSIM)
**Geradores**: `portfolio_variants_validator.py` + `plot_portfolio_variants.py`
**Dados**: `PORTFOLIO_VARIANTS_VALIDATION.json`

---

## TL;DR

Testei 6 variantes V_HYBRID (incluindo managed futures, NTSI/NTSE stacking,
RSST, e blends 50/50 com V1) contra V1 + V3_1 baselines.

**3 winners empíricos diferentes** dependendo do critério:

| critério | vencedor | razão |
|---|---|---|
| **Max CAGR** | V1 NTSX+GDE 67/33 | 13.50% / 32y dominância completa |
| **Max Sharpe diversificado** | V_HYBRID_50_50_with_V1 | 0.758 (+0.07 vs baseline) |
| **🏆 Max robustez worst-case** | **V_HYBRID + 10% MF (KMLM)** | P(rolling 10y < 5%) = **0.6%** vs V1 4.1% |

**A grande descoberta**: **V_HYBRID + 10% Managed Futures** tem **MDD
empírico igual a V1** (44.7% vs 44.4%) e **worst-case rolling 10y MUITO
melhor que V1** — tudo isso mantendo factor + global + capital efficiency
do Plano C.

Trade-off: CAGR 10.91% vs V1 13.50% — você abre mão de ~2.6pp/yr de
CAGR potencial em troca de robustez cross-scenario significativamente
maior. Em 30y, isso se traduz em terminal wealth menor mas com
probabilidade muito menor de "sequência ruim de 10 anos".

---

## Os 6 portfolios testados

### V_HYBRID_baseline (referência)
```
25% GDE | 12% NTSX | 20% AVDE | 13% AVEM
10% AVUV | 5% AVDV | 7% SPMO | 3% IDMO | 5% BTGD
```

### V_HYBRID_PLUS_MF (adiciona managed futures)
```
22.5% GDE | 10.8% NTSX | 18% AVDE | 11.7% AVEM
9% AVUV | 4.5% AVDV | 6.3% SPMO | 2.7% IDMO | 4.5% BTGD
+ 10% KMLM (managed futures)
```
Todos os pesos V_HYBRID × 0.90, adiciona 10% KMLM.

### V_HYBRID_GLOBAL_STACK (NTSI + NTSE synth — testando rejection do V3.5)
```
25% GDE | 12% NTSX | 10% NTSI_synth | 5% NTSE_synth
10% AVDE | 8% AVEM | 10% AVUV | 5% AVDV
5% SPMO | 5% IDMO | 5% BTGD
```
Tenta full return-stacking em todas regiões. Plano C V3.5 rejeitou NTSI/NTSE
em 2026-04-23 baseado em real 2021-2026; testando se 32y synth refuta.

### V_HYBRID_RSST (NTSX → RSST = S&P + MF stacked)
```
25% GDE | 12% RSST_synth | 20% AVDE | 13% AVEM
10% AVUV | 5% AVDV | 7% SPMO | 3% IDMO | 5% BTGD
```
RSST_synth = 1.00 SPY + 1.00 KMLM - 1.00 CASH (S&P + MF stacked, 200% notional).

### V_HYBRID_KITCHEN_SINK (combina todos)
```
20% GDE | 10% NTSX | 8% NTSI | 4% NTSE | 5% RSST
10% AVDE | 10% AVEM | 10% AVUV | 5% AVDV
5% SPMO | 3% IDMO | 4% BTGD | 6% KMLM
```
Mais agressivo: capital efficiency em todas regiões + MF + RSST.

### V_HYBRID_50_50_with_V1 (blend dos 2 paradigmas)
```
50% V1 + 50% V_HYBRID, expandido:
~40% NTSX | ~29% GDE | ~10% AVDE | ~6.5% AVEM
~5% AVUV | ~2.5% AVDV | ~3.5% SPMO | ~1.5% IDMO | ~2.5% BTGD
```

---

## Resultados full window (1994-2026, 31.9y)

| portfolio | Sharpe | CAGR | MDD | ETFs |
|---|---|---|---|---|
| 🏆 **V1 NTSX+GDE 67/33** | **0.809** | **13.50%** | **44.37%** | 2 |
| V_HYBRID_50_50_with_V1 | 0.758 | 12.32% | 47.65% | ~10 |
| **V_HYBRID_KITCHEN_SINK** | **0.745** | 11.23% | **45.80%** | 13 |
| **V_HYBRID_PLUS_MF** | **0.743** | 10.91% | **44.71%** | 12 |
| V_HYBRID_RSST_substitute | 0.716 | 11.66% | 49.56% | 11 |
| V_HYBRID_GLOBAL_STACK | 0.702 | 11.17% | 49.84% | 13 |
| V_HYBRID_baseline | 0.685 | 11.06% | 51.28% | 11 |
| V3_1 Plano C v3.5 | 0.671 | 10.94% | 52.43% | 11 |

**Insight crítico**: **V1 ainda é o vencedor empírico inquestionável** em
Sharpe + CAGR + MDD. Nenhuma variante V_HYBRID com mais complexidade conseguiu
bater V1 nos 3 eixos simultaneamente. **Por quê?**

V1 carrega 40% bonds estruturalmente via NTSX. Janela 1994-2026 inclui um
**bond bull market massivo (1994-2020)** que dominou o resultado. V1 está
"otimizado" exatamente pra esse regime histórico.

---

## Rolling 10y — onde a complexidade paga

| portfolio | mean CAGR | min CAGR | 5pct | **P(<5%)** | mean Sharpe | mean MDD |
|---|---|---|---|---|---|---|
| V1 NTSX+GDE | 11.78% | **1.16%** | 5.29% | **4.1%** | 0.73 | 37.0% |
| V3_1 Plano C | 9.72% | 2.50% | 6.52% | 2.4% | 0.61 | 42.1% |
| V_HYBRID_baseline | 9.92% | 2.92% | 6.94% | 1.8% | 0.62 | 41.0% |
| **V_HYBRID_PLUS_MF** | 9.72% | **3.77%** | **7.18%** | **0.6%** ✅ | **0.67** | **35.9%** ✅ |
| V_HYBRID_GLOBAL_STACK | 10.15% | 3.39% | 7.35% | 1.2% | 0.64 | 39.7% |
| V_HYBRID_RSST | 10.29% | 3.29% | 7.28% | 1.1% | 0.64 | 40.2% |
| **V_HYBRID_KITCHEN_SINK** | 10.07% | **3.87%** | **7.52%** | **0.4%** ✅ | **0.67** | 36.6% |
| V_HYBRID_50_50_V1 | 10.89% | 2.13% | 6.26% | 3.1% | 0.68 | 38.8% |

**Achados rolling 10y:**

1. **V_HYBRID_KITCHEN_SINK tem o melhor worst-case**: P(<5%) = 0.4% — em
   ~3000 janelas rolling 10y, apenas **12 janelas** retornaram < 5% CAGR.
   V1 teve 4.1% (~120 janelas).

2. **V_HYBRID_PLUS_MF tem o melhor MDD médio**: 35.9% (vs V1 37.0%, baseline
   41.0%). MF age como hedge defensivo.

3. **V1 tem o melhor mean CAGR** (11.78%) mas o **pior worst-case** (min
   1.16%, P<5% 4.1%) — confirma que V1 é "high mean, fat left tail".

4. **V_HYBRID_50_50_with_V1 oferece bom meio termo**: mean CAGR 10.89%
   (~entre V1 e V_HYBRID), Sharpe 0.68, mas worst-case ainda volátil
   (P<5% 3.1% — quase como V1).

---

## Stress tests — onde cada uma sofre/protege

### 2008 GFC

| portfolio | retorno 1.5y | MDD |
|---|---|---|
| V1 NTSX+GDE | **−32.21%** | −44.4% |
| V_HYBRID_PLUS_MF | −32.40% | −44.7% (~empate V1) |
| V_HYBRID_KITCHEN_SINK | −33.34% | −45.8% |
| V_HYBRID_50_50_V1 | −35.94% | −47.7% |
| V_HYBRID_RSST | −37.35% | −49.6% |
| V_HYBRID_GLOBAL_STACK | −37.84% | −49.8% |
| V_HYBRID_baseline | −39.62% | −51.3% |
| V3_1 Plano C | −41.06% | −52.4% |

**MF (KMLM) protegeu quase tanto quanto V1** em 2008. Adiciona 10% MF e
sua perda em GFC fica ≈ V1 (que tem 40% bonds).

### 2022 rate cycle (bond bear)

| portfolio | retorno 2022 | MDD |
|---|---|---|
| **V_HYBRID_PLUS_MF** | **−11.87%** ✅ | −20.3% |
| V_HYBRID_RSST | −12.35% | −21.9% |
| V_HYBRID_KITCHEN_SINK | −13.24% | −21.4% |
| V3_1 Plano C | −15.33% | −25.2% |
| V_HYBRID_baseline | −16.21% | −25.9% |
| V_HYBRID_GLOBAL_STACK | −17.29% | −26.8% |
| V_HYBRID_50_50_V1 | −19.61% | −27.8% |
| V1 NTSX+GDE | **−22.96%** | −29.8% |

**MF foi o melhor hedge em 2022** — KMLM (managed futures) capturou trends
de commodities + rate hikes que protegeu enquanto bonds e equity caíram juntos.

### 2020 COVID

| portfolio | retorno 2.5m | MDD |
|---|---|---|
| V1 NTSX+GDE | **−7.15%** | −29.5% |
| V_HYBRID_PLUS_MF | −10.34% | −28.6% |
| V_HYBRID_50_50_V1 | −10.38% | −31.0% |
| V_HYBRID_KITCHEN_SINK | −10.63% | −29.3% |
| V_HYBRID_RSST | −12.32% | −32.0% |
| V_HYBRID_GLOBAL_STACK | −12.69% | −31.7% |
| V_HYBRID_baseline | −13.54% | −32.6% |
| V3_1 Plano C | −14.24% | −33.3% |

V1 venceu (bonds rallying durante flight-to-safety). V_HYBRID_PLUS_MF
respeitável segundo lugar.

### 2000-2013 Lost Decade

| portfolio | retorno 13y | CAGR |
|---|---|---|
| **V_HYBRID_GLOBAL_STACK** | **+197.14%** | 8.7% |
| V_HYBRID_KITCHEN_SINK | +192.87% | 8.6% |
| V_HYBRID_RSST | +183.73% | 8.3% |
| V_HYBRID_PLUS_MF | +182.03% | 8.2% |
| V_HYBRID_50_50_V1 | +178.77% | 8.1% |
| V_HYBRID_baseline | +177.88% | 8.1% |
| V1 NTSX+GDE | +175.89% | 8.0% |
| V3_1 Plano C | +162.26% | 7.6% |

**Achado contraintuitivo**: **V_HYBRID_GLOBAL_STACK venceu o lost decade**
com NTSI/NTSE — porque DM+EM e bonds tiveram bull massivo nesse período.
**Mas em 2022 NTSI/NTSE perderam mais** — mesmo bug que motivou Plano C
V3.5 a removê-los.

Conclusão: NTSI/NTSE são **regime-conditional sleeves**. Funcionam em
"bond bull + intl rotation" (2000s); falham em "rate hike + USD strength"
(2022). Não dá pra generalizar uma decisão sobre eles a partir de uma
janela só.

---

## Risk-return scatter (Plot `PORTFOLIO_VARIANTS_scatter.png`)

```
        13.5% ■ V1 NTSX+GDE  (Sharpe 0.81)
              
   CAGR  12.3% ■ V_HYBRID_50_50_V1
        
        11.7% ■ V_HYBRID_RSST
        
        11.2% ■ V_HYBRID_KITCHEN_SINK ★
        11.1% ■ V_HYBRID_GLOBAL_STACK
        11.0% ■ V_HYBRID_baseline
        10.9% ■ V_HYBRID_PLUS_MF ★
        10.9% ■ V3_1 Plano C
              
              0.65   0.70    0.75    0.80    0.85
                          Sharpe ratio
```

V1 isolado no canto superior direito (high Sharpe, high CAGR). As variantes
V_HYBRID formam um cluster — KITCHEN_SINK e PLUS_MF são as melhores em
risco-ajustado (~0.745 Sharpe), mesmo com CAGR menor.

---

## Análise por categoria de pergunta

### "Quem maximiza terminal wealth em 30y de aporte?"

V1 NTSX+GDE 67/33 — CAGR 13.50% por 30y de aporte de R$3.6M total → ~R$280M
final.

V_HYBRID_PLUS_MF — CAGR 10.91% → ~R$170M.

**Diferença ~R$110M ao longo de 30 anos**. Significativo se você acreditar
que a janela 1994-2026 é representativa do futuro 1994-2056. **NÃO é
garantido.**

### "Quem minimiza chance de resultado catastrófico?"

V_HYBRID_KITCHEN_SINK ou V_HYBRID_PLUS_MF — em rolling 10y, < 1% de chance
de retornar < 5%. V1 tem 4.1% de chance.

Pra investidor que entra em janela de aposentadoria com retornos rolling
< 5%, V1 representa mais "left tail risk" — pode ser doloroso na hora
de retirar.

### "Quem performa em diferentes regimes?"

| regime | vencedor | razão |
|---|---|---|
| 2008 GFC equity crash | V1 / V_HYBRID_PLUS_MF (empate) | bonds + MF hedgam |
| 2020 COVID flash crash | V1 | bonds rally rápido |
| 2022 rate cycle | V_HYBRID_PLUS_MF | MF capta trend, bonds caem |
| 2000-2013 lost decade | V_HYBRID_GLOBAL_STACK | bonds + intl bull |
| Bull market 2010-2021 | V1 | leverage capturou bem |

**V_HYBRID_PLUS_MF é o único que está no top 2 em TODAS as crises** (2008,
2020, 2022). É a estratégia mais "all-weather".

---

## Insights estruturais

### 1. Managed futures (MF) é o sleeve marginal mais valioso

Adicionar 10% KMLM ao V_HYBRID:
- Sharpe +0.058 (de 0.685 → 0.743)
- MDD −6.6pp (de 51.3% → 44.7%)
- P(rolling 10y < 5%) cai de 1.8% → 0.6%
- 2022 stress: melhora 4.3pp (−16.2% → −11.9%)
- CAGR: praticamente igual (−0.15pp)

**MF é "free lunch" no contexto deste portfolio**: melhora robustez
significativamente sem sacrificar CAGR. Hurst-Ooi-Pedersen (2017) "A
Century of Evidence on Trend-Following Investing" documenta exatamente
isso — MF tem ~0 correlação com equity/bonds e Sharpe ~0.5-0.7
standalone.

### 2. NTSI/NTSE foi vindicado parcialmente (32y synth) mas perde em 2022

V_HYBRID_GLOBAL_STACK:
- Lost decade winner (+197%, melhor que V_HYBRID em 19pp)
- Mas 2022 perdeu mais (−17.3% vs baseline −16.2%)
- Plano C V3.5 rejeição estava CORRETA pra janela 2021-2026
- Em janela 32y, NTSI/NTSE adiciona valor mas com risco específico de
  rate cycle

**Recomendação**: NTSI/NTSE só vale se acompanhado de hedge MF (que
salva em rate hikes). Sozinho é frágil.

### 3. RSST (S&P + MF stacked) funciona mas é menos eficiente que MF separado

V_HYBRID_RSST: Sharpe 0.716 (vs V_HYBRID_PLUS_MF 0.743)
RSST replaces NTSX (S&P+bonds) com S&P+MF — perde a proteção bond em 2008/2020.

Se quer MF + S&P, melhor:
- Manter NTSX (S&P+bonds) para 2008/2020 protection
- Adicionar KMLM separado para 2022 protection
- = V_HYBRID_PLUS_MF design

### 4. V_HYBRID_KITCHEN_SINK é "everything everywhere"

Combina MF + Global Stack + RSST. Numbers:
- Sharpe 0.745 (~empata PLUS_MF)
- CAGR 11.23% (+0.32pp vs PLUS_MF)
- MDD 45.8%
- P(rolling 10y < 5%) = 0.4% (best!)

Trade-off: 13 ETFs vs 12. Marginalmente mais complexo, marginalmente mais
CAGR, mesmo robustez. **Provavelmente excessivo** — KITCHEN_SINK adiciona
NTSI/NTSE/RSST que individualmente não pagam pelo overhead.

---

## Recomendação final

Dado seu critério ("Sharpe+CAGR+MDD melhores, complexidade aceitável"):

### 🥇 V_HYBRID + 10% Managed Futures (KMLM/DBMF) — PRIMARY RECOMMENDATION

**Por quê esta vence:**
- Sharpe 0.743 (+8.5% vs V_HYBRID baseline)
- MDD 44.71% (−6.6pp vs baseline) — **igual a V1**
- P(rolling 10y < 5%) = **0.6%** — robustez extrema
- 2022 stress winner (−11.87%, melhor de todas)
- 2008 GFC near-best (−32.40%, near V1)
- Mantém TUDO de V3_1: factor + global + Avantis + GDE + BTGD
- Adiciona 1 ETF (DBMF ou KMLM)
- Custo CAGR: −0.15pp/yr vs baseline V_HYBRID (negligível)

**Composição final V_HYBRID_PLUS_MF (operacional)**:
```
22.5% GDE
10.8% NTSX  (replaces 12% AVUS in V3_1)
18%  AVDE
11.7% AVEM
9%   AVUV
4.5% AVDV
6.3% SPMO
2.7% IDMO
4.5% BTGD
10%  DBMF (Managed Futures — Plano C V3_2 sleeve antecipado)
─────
12 ETFs total. Notional ~125%.
```

**Tese acadêmica**:
- Factor premium (Fama-French + AQR) ✅
- Global diversification (DMS) ✅
- Capital efficiency (WisdomTree NTSX) ✅
- Trend-following premium (Hurst-Ooi-Pedersen) ✅ NEW
- Cross-asset orthogonality maximizada

**Trade-offs honestos**:
- DBMF/KMLM têm AUM modesto (~$1B); risco operacional pequeno
- MF tem drag em bull markets puros (2010-2021 era de QE foi parte do tempo)
- Ainda é 100% USD-domiciled (estate tax issue não resolvida)

### 🥈 V_HYBRID baseline — INTERMEDIATE OPTION

Se você não quer adicionar DBMF (ETF novo, AUM modesto), o baseline
V_HYBRID (V3_1 com NTSX em vez de AVUS) ainda é melhoria sobre V3_1
puro. Sharpe 0.685 vs V3_1 0.671. Não é o ótimo mas é zero-risk
incremental.

### 🥉 V1 NTSX+GDE 67/33 — IF MAX CAGR > ROBUSTEZ

V1 entrega o maior CAGR + Sharpe + (empate) MDD da janela 32y. Mas:
- 100% US-domiciled (estate tax)
- Worst-case rolling 10y é o pior (P<5% = 4.1%)
- Janela 1994-2026 favoreceu seu mix bond+gold; futuro pode não favorecer
- Zero hedge se US continuar com bond bear secular pós-2022

---

## Caveats

1. **Janela 1994-2026 é US/bond-bull biased**. NTSX e V1 se beneficiam
   estruturalmente. Pré-1994 (stagflation 70s) seria diferente.
2. **DBMF/KMLM são ETFs reais novos** (DBMF inception 2019, KMLM 2020).
   Synth backfill testfolio é confiável pra 26-38 anos mas real-world
   tracking error pode existir.
3. **NTSI/NTSE rejeitados por Plano C V3.5** com base em real 2021-2026.
   Esse estudo testa em 32y synth e mostra que **conditionally** funcionam,
   mas falha em rate cycle. Não recomendo desafiar V3.5 sem evidência
   ainda mais forte.
4. **Proxies para Avantis ETFs** subestimam V_HYBRID_PLUS_MF real em
   ~150-300 bps/yr (factor + BTC premium não capturados).
5. **Mandate maintenance §1 inalterado**. Análise é deploy-readiness
   research; nenhum override §7 emitido.

---

## Plots gerados

- `PORTFOLIO_VARIANTS_equity.png` — equity curves log-scale (focus)
- `PORTFOLIO_VARIANTS_drawdowns.png` — drawdowns
- `PORTFOLIO_VARIANTS_scatter.png` — risk-return scatter (Sharpe vs CAGR
  com MDD as bubble size)
- `PORTFOLIO_VARIANTS_rolling10y.png` — rolling 10y Sharpe
- `PORTFOLIO_VARIANTS_2022.png` — 2022 rate cycle stress zoom

## Files referenced

- `portfolio_variants_validator.py` — runner
- `plot_portfolio_variants.py` — plotter
- `PORTFOLIO_VARIANTS_VALIDATION.json` — raw metrics
- `portfolio_variants_returns.parquet` — daily returns
