# Plano B — Portfolio 3-leg EW LETF rotation (SSO + QLD + UGL)

> **Living strategy doc.** Descreve a estratégia do winner Plano B em
> nível conceitual e decisório. Para o runbook operacional dia-a-dia
> (abrir conta, emitir ordens, DARFs, checklist mensal) ver
> [`reports/phase3_5b/PRODUCTION.md`](../../reports/phase3_5b/PRODUCTION.md).
> Para evidência bruta dos 5 gates ver
> [`reports/phase3_5b/variants_letf_execution/`](../../reports/phase3_5b/variants_letf_execution/).
> Este doc é **atualizado quando a estratégia evolui**; PRODUCTION.md
> é atualizado quando o procedimento operacional muda.

**Path tag:** [SWING BROKER] • **Broker:** Banco Inter Global •
**Timeframe:** daily • **Hold median:** multi-week por leg, sem gate swap.
**Status:** ✅ Winner Phase 3.5b (2026-04-17 consolidado; V4 promoted
2026-04-18; expansão V5-V8 ratificou V4 no mesmo dia).

---

## 1. TL;DR

Portfolio 3-leg equal-weight em LETFs 2× (SSO + QLD + UGL), sinais
computados nos índices 1× correspondentes (SPY/QQQ/GLD) e execução no
LETF 2× quando o sinal disparar LONG. Rebalance por threshold 10pp
(não diário). Default **V4** (todos legs 2×); **V1** (1 leg 2× + 2 legs
1×) é fallback conservador; **V8** (todos legs 3×) é ultra-aggressive
documentado mas não recomendado.

V4 canonical (2004-2026, 21.4y testfol.io ground-truth): **Sharpe OOS
2.609, CAGR 39.19%, MaxDD -12.22%**. Extended (1986-2026, 40y):
**Sharpe 2.320, CAGR 37.93%, MaxDD -16.91%** — sobrevive Black Monday
1987, dot-com 2000-2002, Lehman 2008, COVID 2020, 2022. Passa os 5
gates formais (PBO-equivalent via DSR n_trials=8, WF 8/8, OOS/Stress
Sharpe > 0, bootstrap 99.9% CI > 0) em **ambas** as janelas.

Base científica única: `[leverage_for_the_long_run, Gayed 2016/2020,
p.7-21]` + 5-gate framework `[advances_fin_ml, López de Prado,
p.196-211]`.

---

## 2. Regras de sinal e execução

### 2.1 Sinais — computados no 1× (signal-clean)

Três sinais independentes, avaliados diariamente no close US (~16:00 ET),
todos sobre dados do **índice 1×** (não no LETF):

| Perna | Signal source | Regra | Trigger LONG |
|---|---|---|---|
| 1 — S&P500 | `SPY` close | EMA-100 regime filter | `close > EMA100` |
| 2 — NASDAQ-100 | `QQQ` close | Donchian 20/10 breakout | `close > max(close_20d)` entrada; `close < min(close_10d)` saída |
| 3 — Gold | `GLD` close | Donchian 40/20 breakout | `close > max(close_40d)` entrada; `close < min(close_20d)` saída |

**Key insight:** sinais são computados nos índices 1× (menos noise,
signal clean). Execução usa os LETFs 2× (SSO/QLD/UGL) para amplificar
retornos durante períodos LONG. Essa separação signal/execution é o
princípio central do desenho `[leverage_for_the_long_run, p.13]`.

### 2.2 Portfolio target allocation

Equal-weight (1/3, 1/3, 1/3) nos três LETFs quando todos os sinais
estão LONG. Cada perna opera **independente**:

- Leg com signal LONG → posição no LETF 2× correspondente.
- Leg com signal OFF → cash **dentro dessa perna** (não realoca pras outras).
- Cross-leg rebalance **só acontece em evento de threshold** (§2.3).

### 2.3 Rebalance trigger — threshold 10pp (não diário)

Monitorar diariamente a alocação realizada; rebalancear para target 1/3
somente quando qualquer perna drifta > 10pp do target (> 43.3% ou
< 23.3% da carteira). Expected: ~1.3 rebal events/yr (9× menos que
monthly_sell; ~12-15 DARFs/ano total incluindo saídas de signal).

Decisão de threshold 10pp revista em 2026-04-18 após sweep completo
(5/10/15/25/100pp). 10pp domina 5pp em operabilidade (Sharpe idêntico
dentro do ruído, metade das DARFs, MaxDD igual). `[advances_fin_ml, p.275-278]`.

### 2.4 Sizing dentro do LONG

Quando uma perna está LONG, aloca 100% daquela fatia no LETF (sem
dynamic sizing). A alavancagem já vem embutida no ETF 2× — Gayed Table
12 `[p.21]` mostra que full-size em LETF on-regime + cash off-regime é
superior a fractional sizing para essa classe.

---

## 3. Espaço de 8 variantes — V1 a V8

Em 2026-04-18 expandimos sistematicamente o espaço de leverage por perna
para cobrir tudo entre "1× passivo" e "3× máximo listado":

| V | Leg 1 (S&P) | Leg 2 (NDX) | Leg 3 (Gold) | Papel |
|---|---|---|---|---|
| V1 | SSO 2× | QQQ 1× | GLD 1× | Fallback conservador |
| V2 | SSO 2× | **QLD 2×** | GLD 1× | Dominado por V4 |
| V3 | SSO 2× | QQQ 1× | **UGL 2×** | Dominado por V4 |
| **V4** ⭐ | **SSO 2×** | **QLD 2×** | **UGL 2×** | **Default** |
| V5 | **UPRO 3×** | QQQ 1× | GLD 1× | Dominado por V1 |
| V6 | **UPRO 3×** | **TQQQ 3×** | GLD 1× | Dominado por V8 |
| V7 | **UPRO 3×** | QQQ 1× | **UGL 2×** | Dominado por V4 |
| V8 | **UPRO 3×** | **TQQQ 3×** | **UGL 2×** | Ultra-aggressive documentado |

**Nota estrutural:** não existe ETF 3× gold. DGP era 2× e foi descontinuado.
V7/V8 ficam com UGL 2× por essa razão.

### 3.1 Ranking canonical 2004-2026 (todas 8 PASS 5 gates)

| Rank | Variant | OOS Sh | CAGR | MaxDD | Boot 99.9% lo | Status |
|---:|---|---:|---:|---:|---:|:-:|
| 1 | V8 | **2.622** | **58.17%** | -17.14% | 1.309 | ultra-aggressive |
| 2 | **V4** ⭐ | 2.609 | 39.19% | -12.22% | 1.274 | **default** |
| 3 | V2 | 2.595 | 35.03% | -12.62% | 1.304 | dominated |
| 4 | V6 | 2.573 | 53.02% | -17.05% | 1.325 | dominated |
| 5 | V1 | 2.478 | 26.53% | **-9.39%** | 1.043 | fallback |
| 6 | V7 | 2.428 | 38.98% | -12.38% | 1.176 | dominated |
| 7 | V3 | 2.392 | 30.89% | -10.88% | 1.081 | dominated |
| 8 | V5 | 2.354 | 34.46% | -14.06% | 1.024 | dominated |

### 3.2 Por que V4 é default, não V8

V8 tem **melhor OOS Sharpe** (+0.013 canonical) e CAGR dramático
(+18.98pp), mas **não** é recomendado por 4 razões:

1. **Margem ao gate MaxDD 25% (mandate §5).** V4 canonical 12.22%
   (margem 12.78pp); V8 extended **22.84%** (margem **2.16pp**). Um
   stress event tipo 1973-74 Volcker fora da amostra provavelmente
   leva V8 real a violar gate.
2. **Drag real LETF.** `[leverage_for_the_long_run, p.21, Table 12]`
   reporta UPRO real com drag ~2%/yr vs teórico. Em 3× empilhados
   (UPRO + TQQQ), expected drag real ~4-5pp CAGR + 3-5pp MaxDD em
   produção → V8 real MaxDD esperado 27-30% → **viola gate**.
3. **Sharpe edge V8 dentro do ruído.** Com T≈5000 bars,
   std(Sharpe) ≈ 0.014. Δ 0.013 entre V8 e V4 não é estatisticamente
   distinguível `[fortune_formula]`, `[leverage_space]`.
4. **Behavioral risk (prospect theory 2×).** Diferença -17% vs -22%
   DD é psicologicamente muito maior do que aparenta.

### 3.3 V1 fallback — por que e quando

V1 (baseline 2×/1×/1×) tem MaxDD -9.39% canonical (melhor de todos) com
Sharpe 2.478 e CAGR 26.53%. Se algum dia:
- Inter Global delistar QLD ou UGL (improvável mas possível).
- Stress real exceder budget behavioral de V4.
- User preferir menor variância pós-track-record insuficiente.

→ degrada para V1. Também gate-passing, documentado em `PRODUCTION.md §13`.

### 3.4 Achado estrutural — interaction effect

Em CAGR 40y **standalone**:

| Asset | CAGR 1× | CAGR 2× | CAGR 3× | Efetivo 2× | Efetivo 3× |
|---|---:|---:|---:|---:|---:|
| SPY → SSO → UPRO | 11.49% | 14.58% | 13.51% | 1.27× | 1.18× |
| QQQ → QLD → TQQQ | 14.58% | 17.27% | **12.16%** | 1.19× | **0.84×** |
| GLD → UGL → — | 6.92% | **6.34%** | — | **0.92×** | — |

- **TQQQ 3×** standalone tem CAGR < QQQ 1× (daily-rebal decay devastador
  em 40y).
- **UGL 2×** standalone tem CAGR < GLD 1× (gold tem regiões flat 2012-2018,
  2020-2023 onde decay domina).

Mas em **blend EW 3-leg**, UGL e TQQQ viram **positive-alpha via
interaction effect**: quando vol do resto do portfolio está alta,
correlação baixa paga proporcionalmente mais — Sharpe é **não-aditivo**.
V8 > V1 em Sharpe apesar de UGL e TQQQ standalone perderem para 1×
passivo. `[advances_fin_ml, p.298-313, ch.16]` (HRP correlation structure).

---

## 4. Mecanismo de leverage — LETF vs CFD (comparação com Plano A)

### 4.1 LETF daily-rebal

O LETF 2× rebalance diário o notional para manter razão constante 2:1
vs o índice. Em intraday upswings amplifica 2×; em downswings amplifica
2× — **mas o daily rebal em vol alta cria decay**. Exemplo canonical:

- SPY faz +10%, -10%, +10%, -10% em 4 dias: líquido SPY = -0.99%.
- SSO 2× o mesmo path: +20%, -20%, +20%, -20% → líquido SSO = -3.94%.

Decay = 2% sobre 4 dias de chop. Em período longo flat + choppy, LETF
2× underperforms 2× CAGR teórico por 1-3%/yr (Gayed p.16-17).

### 4.2 Por que aceitar decay em Plano B

Plano B é **swing-and-hold**. O LETF fica exposto 2-3 semanas por leg
típico. A maior parte do tempo em regime LONG é drift (não chop) —
drag é pequeno comparado ao benefício de 2× amplification nos drifts
bons. Gayed mostra empiricamente que LETF + regime filter (cash em
off) é superior a 2× CFD direto porque o filter evita decay no chop
prolongado — que é quando o mercado está em off-regime.

### 4.3 Plano A usa CFD, não LETF — por quê

Plano A tem hold median **6 dias**. Em 6 dias o decay LETF é trivial
(<0.5%), mas o cost fixo CFD (spread + commission) por trade é
dominante em Plano A `[systematic_trading, p.185-188]`. CFD permite
entrar/sair sem decay drag mas paga commission.

Plano B tem hold multi-week → decay LETF se dilui em retorno base;
cost fixo é per-trade (poucos trades/ano) → cost é trivial. LETF é
escolha ótima.

**Heurística:** hold ≤ 1 semana → CFD (Plano A). Hold ≥ 2 semanas →
LETF (Plano B). Mesmo edge Gayed, mecanismo de leverage diferente por
timeframe. Ver [`plano_a_v2_l2_gayed_cfd.md §3`](plano_a_v2_l2_gayed_cfd.md)
para o lado CFD.

### 4.4 Compatibilidade operacional

| Plano | Broker | Leverage via | Tax regime | Hold |
|---|---|---|---|---|
| A | Pepperstone CFD | margin CFD direto | 15% IR BR (variable) | 6 dias median |
| B | Banco Inter Global | LETF 2× | 15% IR BR (stocks, DARF 6015) | 2-3 sem median por leg |

Zero overlap de ativos — Plano A em SPY+QQQ+GLD CFDs; Plano B em
SSO+QLD+UGL LETFs. Correlação de retorno paper-measured na Phase 4
informa ponderação dual-path.

---

## 5. Execução via Banco Inter Global — specifics

### 5.1 Broker e entity

Banco Inter Internacional (Inter&Co Securities FINRA locked 2026-04-18).
Zero corretagem, spread FX 0.99-1.50% (por remessa), T+1 liquidation.
Catálogo confirmado pelo user: **SSO, QLD, UGL, UPRO, TQQQ todos
disponíveis**.

### 5.2 Tax model

- 15% IR BR sobre lucro bruto por venda, monthly DARF 6015.
- IOF 3.5% na remessa inicial para USD.
- PTAX fixing diário B3 para cost basis.
- ~12-15 DARFs/ano esperados (3 legs × ~4-5 exits/yr).

### 5.3 Pre-deploy checklist (ordem)

Ver `PRODUCTION.md §7` para checklist completo. Resumo:

1. Abrir conta Inter Global (KYC completo).
2. Remeter capital (IOF 3.5% sobre USD convertido).
3. Validar catálogo SSO + QLD + UGL (todos listados 2026-04-18).
4. Montar planilha cost basis USD + PTAX diário.
5. Configurar alerta diário de signal (script `scripts/plano_b_daily_signal.py` a construir em Phase 4).
6. Backup plan V1 documentado caso catálogo mude.

---

## 6. Gates e evidência

### 6.1 5-gate framework (mandate §5)

Todos 5 gates obrigatórios passam em **ambas** as janelas (canonical
21.4y + extended 40y):

| Gate | Threshold | V4 canonical | V4 extended | Status |
|---|---|---|---|:---:|
| PBO-equivalent (DSR, n_trials=8) | p < 0.05 | 0.000288 | 0.00041 | ✅ |
| WF profitable | ≥ 6/8 | 8/8 | 8/8 | ✅ |
| OOS Sharpe | > 0 (binding) / ≥ 2.0 (winner) | 2.609 | 2.320 | ✅ |
| OOS MaxDD | ≤ 25% | -12.22% | -16.91% | ✅ |
| Bootstrap 99.9% CI low | > 0 | 1.274 | (análoga) | ✅ |

Ver [`reports/phase3_5b/variants_letf_execution/gates_verdict.md`](../../reports/phase3_5b/variants_letf_execution/gates_verdict.md)
para JSON + MD com 8 rows por janela.

### 6.2 Extended window 1986-2026 (★ stress test suplementar)

40 anos via testfol.io SPYSIM/QQQSIM/GLDSIM. Sobreviveu sem violação
de gates:

- Black Monday 1987 (-22.6% single-day SPX).
- Dot-com 2000-2002 (-49% SPX peak-to-trough).
- Lehman 2008 (-57% SPX, gold flat).
- COVID 2020 (-34% SPX em 5 semanas).
- 2022 rate hikes (-25% QQQ, -19% SPX, -10% GLD).

**V4 MaxDD worst-case nessas janelas:** -16.91% em 2008-2009 (ainda
8pp abaixo do gate 25%). Ver `PRODUCTION.md §10`.

### 6.3 Rejeição de alternativas documentada

- **SSO+ZROZ+GLD (risk parity static):** 4 weight variants testadas em
  1986-2026; todas Pareto-dominadas por V4 tactical. Ver
  [`reports/phase3_5b/rejected_alternatives/static_sso_zroz_gld/`](../../reports/phase3_5b/rejected_alternatives/static_sso_zroz_gld/).
- **2-leg LETF+QQQ (drop GLD):** Sharpe -0.22 vs V4, ⚠️ FAIL Diebold-Ribeiro
  1.121 < 1.20. Deploy só se broker bloquear GLD.
- **3-leg com 2.5× synthetic leverage:** passa gates mas
  synthetic-only (ninguém lista ETF 2.5×).

---

## 7. Overrides possíveis + riscos

### 7.1 Overrides documentados

| Override | Quando | Consequência |
|---|---|---|
| V4 → V1 | Inter delistar QLD ou UGL | CAGR -12.66pp, MaxDD -2.83pp melhor |
| V4 → V8 | ≥ 12-24m V4 live track record ±30% backtest + user aceita gate violation risk | Mandate §7 override obrigatório |
| Threshold 10pp → 5pp | User quer Sharpe ligeiramente melhor (fora do ruído) | ~2× DARFs/yr, Sharpe +0.013 |
| Threshold 10pp → 15pp | User quer menos DARFs | CAGR +0.88pp, MaxDD +1.12pp (aceitável) |

### 7.2 Riscos (pré-deploy awareness)

- **LETF daily rebal drag.** Modelado no testfol.io ground-truth; real
  pode ter drag adicional ~1-2%/yr. Phase 4 paper trading mede.
- **Rate shock correlação.** 2022 provou que TLT/ZROZ não é safe-haven
  anti-correlation garantida em rate hikes — por isso V4 usa GOLD (UGL)
  não bonds.
- **Broker risk.** Inter Global (Inter&Co FINRA) tem SIPC protection mas
  concentra risk em uma entity. Considerar split futuro (Avenue, TD
  Ameritrade) se capital > $100k.
- **Tax complexity.** 12-15 DARFs/ano manual. Errar DARF = multa 20%+
  IR. Planilha + lembrete mensal obrigatório.

---

## 8. Próximos passos — Phase 4 paper trading

Path B paper começa imediato (não bloqueado por OAuth Spotware como
Path A). Deploy recomendado com **capital mínimo real** (não demo) para
validar ops + tax workflow:

1. Fase inicial (~6-12m): **V1 deploy** com 10% do capital Plano B alvo.
   Valida Inter Global ops + DARF workflow + signal timing.
2. Migração V1 → V4 após 6m V1 track record ±30% backtest expected.
3. V8 **não** é recomendado em Phase 4 — tight a gate 25% + drag real
   não modelado; aguarda ≥ 12-24m V4 live antes de considerar.

**Entregáveis Phase 4 build (Path B):**

- `scripts/plano_b_daily_signal.py` — signal emit + planilha manual
  (user executa ordens na Inter).
- `src/ai_trade/live/letf_rotation_service.py` — idempotent daily
  compute dos 3 sinais.
- Planilha cost basis USD+PTAX (template).
- Monitor dashboard: equity curve vs backtest expected.

**Gates paper → live (Plano B):**

- Realized Sharpe ≥ 0.7 × backtest (1.58 minimum).
- MaxDD realizado ≤ 1.5 × backtest (16.3% maximum em 3 meses).
- Slippage médio ≤ 30 bps/trade.
- Signal → fill delay ≤ 1 dia útil (não ≤ 5 min como Plano A intraday).

Ver [`specs/phase_4_paper_trading.md`](../../specs/phase_4_paper_trading.md).

---

## 9. Referências e leitura complementar

**Base científica (citação obrigatória):**

- `[leverage_for_the_long_run, Gayed 2016/2020, p.7-21]` — base teórica LETF rotation
- `[leverage_for_the_long_run, p.16-17]` — daily rebal decay explicado
- `[leverage_for_the_long_run, p.21, Table 12]` — UPRO real drag vs teórico
- `[advances_fin_ml, p.196-211]` — 5-gate framework (PBO/DSR/bootstrap)
- `[advances_fin_ml, p.275-278]` — threshold rebalance rationale
- `[advances_fin_ml, p.298-313, ch.16]` — HRP + interaction effect não-aditivo
- `[systematic_trading, p.185-188]` — fixed cost CFD vs LETF trade-off

**Documentos do projeto:**

- [`reports/phase3_5b/PRODUCTION.md`](../../reports/phase3_5b/PRODUCTION.md) — runbook operacional canônico
- [`reports/phase3_5b/README.md`](../../reports/phase3_5b/README.md) — index técnico Phase 3.5b
- [`reports/phase3_5b/variants_letf_execution/`](../../reports/phase3_5b/variants_letf_execution/) — evidência V1-V8 gates
- [`reports/phase3_5b/extended_window_1986_2026/`](../../reports/phase3_5b/extended_window_1986_2026/) — stress test 40y
- [`reports/phase3_5b/rejected_alternatives/`](../../reports/phase3_5b/rejected_alternatives/) — alternativas testadas e rejeitadas
- [`docs/investment-mandate.md`](../investment-mandate.md) — 7 regras invioláveis
- [`docs/strategies/plano_a_v2_l2_gayed_cfd.md`](plano_a_v2_l2_gayed_cfd.md) — strategy doc companion (Plano A)
- [`docs/reference/letf_rotation_reddit_analysis.md`](../reference/letf_rotation_reddit_analysis.md) — contexto ilustrativo (NÃO gospel)

**Jornadas-chave:**

- [`jornada/2026-04-17/07-b1c-letf-rotation-gates-PASS.md`](../../jornada/2026-04-17/07-b1c-letf-rotation-gates-PASS.md) — lead B1c original
- [`jornada/2026-04-17/24-phase3.5b-full-validation-summary.md`](../../jornada/2026-04-17/24-phase3.5b-full-validation-summary.md) — validação end-to-end
- [`jornada/2026-04-18/08-phase3.5b-V4-promoted-gate-verdict.md`](../../jornada/2026-04-18/08-phase3.5b-V4-promoted-gate-verdict.md) — V4 promoted 2026-04-18
- [`jornada/2026-04-18/16-phase3.5b-3x-variants-V5-V8-tested.md`](../../jornada/2026-04-18/16-phase3.5b-3x-variants-V5-V8-tested.md) — expansão V5-V8
- [`jornada/2026-04-18/04-phase3.5b-extended-window-PASS.md`](../../jornada/2026-04-18/04-phase3.5b-extended-window-PASS.md) — stress 1986-2026

---

## Changelog deste doc

- **2026-04-19:** versão inicial — criado como companion estratégico a
  `plano_a_v2_l2_gayed_cfd.md`. Espaço V1-V8 + V4 default rationale +
  interaction effect documentados. Fonte-primária para decisão
  estratégica; PRODUCTION.md permanece como runbook operacional
  granular.
