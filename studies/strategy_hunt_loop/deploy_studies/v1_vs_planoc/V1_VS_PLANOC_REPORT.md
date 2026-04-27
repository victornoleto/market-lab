# V1 NTSX+GDE 67/33 vs Plano C V3_1 v3.5 — Comparação Empírica

**Janela**: 1994-05-05 → 2026-04-17 (31.9 anos, 8042 bars)
**Benchmark comum**: SPYSIM b&h
**Geradores**: `v1_vs_planoc_validator.py` + `plot_v1_vs_planoc.py`
**Dados**: `V1_VS_PLANOC_VALIDATION.json` + `v1_vs_planoc_returns.parquet`

---

## TL;DR

V1 (2 ETFs, capital efficiency) **dominou Plano C V3_1** em 8 de 9 dimensões
testadas neste backtest. **O único cenário onde V3_1 venceu foi 2022 rate
cycle** (V1 −23.0% vs V3_1 −15.3%) — exatamente o motivo pelo qual Plano C
V3.5 removeu NTSI/NTSE em 2026-04-23.

**NTSX_synth atualizado**: usa fórmula testfolio-validada
`0.90 × SPYSIM + 0.60 × IEFSIM − 0.50 × CASHX` (mecanicamente correta:
representa 90% S&P sem financing + 60% Treasury futures financiados ao
cash rate + 10% cash collateral em margem). User validou no testfolio
2026-04-26 que esta fórmula produz resultados idênticos ao NTSX real.

| dimensão | vencedor | margem |
|---|---|---|
| Sharpe full 32y | **V1** (0.809 vs 0.671) | +0.14 |
| CAGR full 32y | **V1** (13.50% vs 10.94%) | +2.56pp |
| MDD full 32y | **V1** (44.4% vs 52.4%) | −8pp |
| Rolling 5y Sharpe (mean) | **V1** (0.77 vs 0.69) | +0.08 |
| Rolling 5y melhor em % das janelas | **V1** wins 71.6% | — |
| Rolling 10y melhor em % das janelas | **V1** wins 72.8% | — |
| Stress 2008 GFC | **V1** (−32% vs −41%) | +9pp |
| Stress 2020 COVID | **V1** (−7% vs −14%) | +7pp |
| **Stress 2022 rate cycle** | **V3_1** (−15% vs −23%) ✅ | **−8pp** |

⚠️ **MAS**: meus proxies para V3_1 são CONSERVADORES. Veja seção "Caveats
críticos" — fechamento real do gap pode ser ~150-300 bps/yr a favor de V3_1
quando factor premium + BTC são contabilizados. **Decisão final é filosófica,
não puramente empírica.**

---

## Composição

### V1 NTSX+GDE 67/33

```
67% NTSX_synth  →  60% S&P 500 + 40% IEF (intermediate Treasury, futures-stack)
33% GDESIM      →  30% S&P 500 + 30% Gold (futures-stack)
─────────────
Notional total: 90% S&P + 40% bonds + 30% gold = 160%
Internal leverage: 1.6× via futures (zero margem externa)
ETFs reais: NTSX (US-domiciled, AUM $1.3B) + GDE (AUM $629M)
```

### Plano C V3_1 v3.5 (acumulação 30-45 anos)

```
25% GDE        → 22.5% S&P + 22.5% gold (stacked overlay)
12% AVUS       → US large core (Avantis factor methodology)
20% AVDE       → DM developed core (pure equity)
13% AVEM       → Emerging markets core (pure equity)
10% AVUV       → US Small Cap Value (factor tilt)
 5% AVDV       → DM Small Cap Value (factor tilt)
 7% SPMO       → US Momentum (factor tilt)
 3% IDMO       → DM Momentum (factor tilt)
 5% BTGD       → 2.5% BTC + 2.5% gold (stacked overlay)
─────────────
Notional total: 92.5% equity + 27.5% gold + 5% BTC = 125%
ETFs reais: 11 holdings, glidepath para BR FI após 45 anos
```

---

## Resultados — janela full 31.9y

| estratégia | Sharpe | CAGR | MDD | bootstrap 99.9% Sharpe CI |
|---|---|---|---|---|
| **V1 NTSX+GDE 67/33** | **0.809** | **13.50%** | **44.37%** | [0.29, 1.37] ✅ |
| Plano C V3_1 (proxies) | 0.671 | 10.94% | 52.43% | [0.15, 1.30] ✅ |
| SPYSIM b&h | 0.651 | 11.07% | 55.14% | — |

**V1 domina em todos os 3 eixos** vs V3_1 (com proxies). V3_1 com proxies
performa quase igual ao SPY puro — porque os proxies REMOVEM o factor premium
e o BTC contribution.

---

## Rolling windows — onde V1 vence?

### Rolling 5 anos (n = 6783 janelas, daily-stepped)

- **V1 Sharpe melhor que V3_1 em 71.6% das janelas**
- V1 mean Sharpe 0.77 / V3_1 0.69
- V1 mean CAGR 12.00% / V3_1 9.73%

V3_1 ganha em ~28% das janelas — concentradas em períodos onde:
1. Factor premia (AVUV/SPMO) tiveram outperformance vs cap-weighted
2. EM e DM internacional bateram US (2002-2007 EM bull, 2025+ DM rotation)
3. Bond bear markets (2022) onde NTSX sofre
4. Cash rate alto (2008, 2022-2024) penaliza financing cost de NTSX

### Rolling 10 anos (n = 5523 janelas)

- **V1 Sharpe melhor em 72.8% das janelas**
- V1 mean CAGR 11.78% vs V3_1 9.72%
- Em horizonte 10y+, V1 vence em ~3 de cada 4 janelas

Plot: `V1_VS_PLANOC_rolling_5y_sharpe.png` mostra visualmente onde cada
estratégia lidera.

---

## Stress tests — comportamento em crashes

| período | V1 retorno | V1 MDD | V3_1 retorno | V3_1 MDD | SPY retorno | vencedor |
|---|---|---|---|---|---|---|
| 2000 dot-com (3y) | −23.46% | −36.9% | −27.16% | −38.6% | −37.36% | **V1** |
| 2008 GFC (1.5y) | **−32.21%** | −44.4% | −41.06% | −52.4% | −45.89% | **V1** |
| 2008 ano completo | −26.85% | −43.8% | −35.07% | −50.9% | −36.75% | **V1** |
| 2011 eurozone (8m) | **+0.25%** | −11.7% | −11.99% | −19.9% | −6.43% | **V1** |
| 2020 COVID (2.5m) | −7.15% | −29.5% | −14.24% | −33.3% | −13.41% | **V1** |
| **2022 rate cycle** | **−22.96%** | −29.8% | **−15.33%** | −25.2% | −18.09% | **V3_1** ✅ |

**Padrão claro**: V1 amortece equity drawdowns (gold + bonds defendem).
V1 sofre quando bonds caem junto com equity (2022). V3_1 sem bonds
estruturais é mais resiliente em rate-cycle shocks.

Plot: `V1_VS_PLANOC_stress.png` mostra 2008 vs 2022 lado a lado.

---

## ⚠️ Caveats críticos — leia antes de decidir

Os proxies usados para V3_1 são CONSERVADORES. Itens que **subestimam V3_1**:

### 1. Factor premium não modelado (~50-150 bps/yr ignorados)

| componente real | proxy usado | premium acadêmico esperado |
|---|---|---|
| AVUS (Avantis large) | SPYSIM | +30-50 bps/yr (mild factor tilt) |
| AVUV (US SCV) | VBRSIM | ✅ proxy correto |
| AVDV (DM SCV) | 50% VEA + 50% VBR | +50-150 bps/yr não capturados |
| SPMO (US Momentum) | SPYSIM | +50-100 bps/yr (Asness-Frazzini) |
| IDMO (DM Momentum) | VEASIM | +50-100 bps/yr |

**Total estimado de factor premium não capturado: 150-300 bps/yr a favor de
V3_1.** Se incluído: V3_1 CAGR sobe pra ~12.5-13.9%, gap com V1 fecha bastante.

### 2. BTGD ≈ GLD apenas (BTC ignorado)

BTGD aloca 50/50 BTC + gold. Sem BTC pre-2014 e BTC dominou massivamente
2014-2026 (~70-80% CAGR vs gold ~5-7%). Impacto: ~50-200 bps/yr a favor de
V3_1 não capturados.

### 3. Janela 1994-2026 favorece capital efficiency

Bonds tiveram **bull market secular 1994-2020** — NTSX/V1 se beneficiou
disso. 2022 mostrou o lado contrário (e V3_1 venceu). Em janela 1980-2026
(stagflation 70s), V3_1 provavelmente venceria mais.

### 4. 30y horizonte real-world favorece V3_1?

Plano C V3.5 ANALYSIS reporta esperativa "10-12% real-world CAGR com MDD
40-55%" — coerente com meu V3_1 proxy (10.94%, 52% MDD). V1 entrega
14.28% no backtest mas isso assume:
- Persistência do bond bull (não garantido pós-2022)
- WisdomTree NTSX/GDE não suspendem ou aumentam ER
- Treasury funding cost não sobe (atualmente ~5% Fed funds)

### 5. Estate Tax US não modelado

Plano C V3.5 alerta: brasileiro com >$60k em ETFs US-domiciliados → 40%
estate tax federal na morte. Mitigação V3_1: **UCITS irlandeses (CSPX,
IWDA) substituem AVUS/AVDE** quando patrimônio cresce. **V1 (NTSX+GDE)
não tem versão UCITS** — exposição estate tax é total.

Em $1M+ patrimônio, este é um custo material que NENHUM backtest captura.

---

## Trade-off filosófico (a decisão real)

| critério | Capital Efficiency (V1) | Factor Investing (V3_1) |
|---|---|---|
| Tese teórica | WisdomTree return-stacking | Fama-French + AQR + Avantis |
| Evidência empírica 32y backtest | **+3.34pp CAGR / Sharpe +0.18** | proxies subestimam ~150-300 bps |
| Diversificação geográfica | 0% (só US) | **55% US / 30% DM / 15% EM** |
| Factor exposure | 0 | **25% factor tilts** |
| Bond exposure | 40% USD Treasury (NTSX) | 0% durante acumulação |
| BR FI integration | impossível (2 ETFs) | **glidepath aos 45+** |
| ETFs total | **2** | 11 (ou ~13 com BR FI) |
| Operacional | aporte mensal trivial | rebalance + glidepath |
| Estate Tax mitigação | impossível | **UCITS substituible** |
| Tese tax (Lei 14.754 PF) | buy-hold = zero realização | mesma + factor turnover |
| Sensibilidade rate cycle | **alta** (NTSX bonds) | baixa (zero structural bonds) |

---

## Decisão recomendada

Honesto: **NÃO HÁ resposta universalmente correta**. Depende de:

### Cenário A — você acredita em factor premium + global diversification

Mantém Plano C V3_1 v3.5. Aceita que:
- Backtest com proxies parece pior que V1 — mas factor premium real e BTC
  contribution real (não capturados) provavelmente fecham a maior parte do gap
- 11 ETFs + glidepath é mais complexo, mas ortogonal a um ciclo de juros
  específico
- Estate tax mitigation via UCITS está disponível
- Tese acadêmica defendida em 30+ anos de pesquisa Fama-French + AQR

### Cenário B — você prioriza simplicidade + evidência empírica direta

Migra pra V1 NTSX+GDE 67/33. Aceita que:
- Backtest sólido em 32y mostra dominância clara
- 2 ETFs vs 11 reduz fricção operacional drasticamente
- Bond exposure estrutural pode sofrer outro 2022-style shock no futuro
- Sem mitigação UCITS para estate tax
- Sem factor premium estatisticamente esperado (mas backtest mostrou que
  factor proxies não dominaram empiricamente em 32y)

### Cenário C — híbrido (não testado aqui mas viável)

Mantém Plano C V3_1 como core, **substitui parte de AVUS por NTSX_synth**:
- Ex: 25% GDE + 6% AVUS + 6% NTSX (em vez de 12% AVUS) + resto idem
- Adiciona capital efficiency parcialmente sem abandonar factor + global
- Trade-off: bond exposure estrutural 3.6% (=6%×60%) — pequeno mas viola
  princípio "bonds em BRL only" parcialmente

⚠️ **Mandate maintenance §1**: nenhuma das 3 vias é deploy autorizado sem
override §7 explícito. Esta análise é deploy-readiness research.

---

## Anexo A — Fórmula NTSXSIM (resolvido 2026-04-26)

User testou no testfolio web e confirmou que a fórmula correta é:
```json
{"SPYSIM": 90, "IEFSIM": 60, "CASHX": -50}
```
(weights percentuais; total = 100%; pesos negativos = posição short).

**Mecânica**:
- Long 90% SPY (S&P cash equity, sem financing cost)
- Long 60% IEF (proxy bond futures, ganho do IEF return)
- Short 50% CASHX (= emprestar 50% ao cash rate)
- Total notional gross: 90 + 60 + 50 = 200%
- Total notional net: 100% (resoluble com 100% capital)

**Por que `-0.50 × CASH` (não -0.60)**: NTSX usa Treasury futures que embutem
financing cost ao cash rate (paga -0.60 × CASH); E o capital de margem da
parte de futuros (~10%) fica em cash earning rate (recebe +0.10 × CASH). Net:
-0.60 + 0.10 = **-0.50 × CASH**. Algebricamente:
```
r_NTSX = 0.90 × r_SPY + 0.60 × r_IEF − 0.50 × r_CASH
```

**Implementação**: `v1_vs_planoc_validator.py` agora usa essa fórmula com
CASHX puxado direto do testfolio (141 anos de cobertura, 1885+). Captura
variação histórica do cash rate (>16% em 1981, ~0% em 2009-2020, ~5% em
2022-2024) — captura corretamente o cost penalty do bond bear de 2022.

**Comparação com fórmula anterior (constant ER 0.20%)**:

| metric | synth ER 0.20% | synth -0.50×CASH | delta |
|---|---|---|---|
| V1 Sharpe full 32y | 0.848 | 0.809 | −0.04 |
| V1 CAGR full 32y | 14.28% | 13.50% | −0.78pp |
| V1 MDD full 32y | 44.30% | 44.37% | +0.07pp |
| V1 better 5y rolling | 76.8% | 71.6% | −5.2pp |
| V1 2022 retorno | −22.5% | −23.0% | −0.42pp |

Os resultados são **direcionalmente idênticos** mas a fórmula com CASHX é mais
honesta — captura financing cost real (alto quando Fed sobe juros). User
mantém-se vencedor em ~72% das janelas de 5 anos vs ~77% antes.

---

## Anexo B — Return Stacked ETFs (RSST/RSSY/RSSX/RSBT)

**Pergunta**: o strategy_hunt_loop testou ETFs Return Stacked da
returnstackedetfs.com?

**Resposta**: **NÃO**. Verificado via grep em todas iterações + DEAD_ENDS.md:
- `NTSX/NTSI/NTSE` (WisdomTree) foram considerados como "Option G" em iter
  013/014 e implementados como synth em iter 015
- **Nenhuma menção a RSST, RSSY, RSSX, RSBT, RSBY** na hunt loop
- Plano C V3.5 menciona RSSX brevemente como "⏳ Esperar track record —
  Inception mai-2025" mas não foi backtested

**Por que não foram testados**:
1. Inception recente (RSST set/2023, RSBT mai/2024, RSSX mai/2025) → zero
   long-window track record
2. Underlying strategies (managed futures trend, futures yield) são
   complexas de sintetizar sem dados granulares de futuros
3. Hunt loop focou em primitives já bem-documentados (NTSX-style return
   stacking, vol-target overlays, momentum)

**Bom achado lateral**: na sessão de hoje puxei **RSSBSIM** (Return Stacked
Bonds & Bitcoin? Ou Return Stacked U.S. Stocks & Bonds? Verificar) para
o cache. Disponível 1969+. Pode entrar no global_factor_tilt_loop se for
relevante — vou inspecionar próximo turn.

**Sugestão futura**: adicionar `RSST`, `RSBT`, `RSSY`, `RSSX` ao Tier 3
da cache testfolio se eles estiverem disponíveis lá. Permitirá iter
80+ no hunt loop testar return-stacking com managed futures (que poderia
ser ortogonal a tudo testado até agora).

---

## Plots disponíveis

- `V1_VS_PLANOC_equity.png` — equity curves log-scale 32y
- `V1_VS_PLANOC_drawdowns.png` — drawdowns simultâneos
- `V1_VS_PLANOC_rolling_5y_sharpe.png` — rolling 5y Sharpe com fill regions
- `V1_VS_PLANOC_rolling_10y_cagr.png` — rolling 10y CAGR
- `V1_VS_PLANOC_yearly.png` — barras de retorno anual
- `V1_VS_PLANOC_stress.png` — 2008 GFC vs 2022 rate cycle side-by-side

## Files referenced

- `v1_vs_planoc_validator.py` — runner com gates
- `plot_v1_vs_planoc.py` — plot generator
- `V1_VS_PLANOC_VALIDATION.json` — raw metrics
- `v1_vs_planoc_returns.parquet` — daily returns series
- `rolling_5y_v1.parquet`, `rolling_5y_v3.parquet` — rolling 5y
- `rolling_10y_v1.parquet`, `rolling_10y_v3.parquet` — rolling 10y
