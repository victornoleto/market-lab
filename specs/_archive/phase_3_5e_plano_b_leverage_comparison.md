# Phase 3.5e — Plano B leverage comparison (honest-grid swing LETF search)

> **Status:** draft autoritativo para o self-improve loop.
> **Criado:** 2026-04-21 (pós-arbitration BLOCK de Phase 3.5d E1).
> **Antecessor:** Phase 3.5d (3× LETF swing) — encerrada sem winner após
> arbitration adversarial rejeitar E1 como grid-shrinkage artifact. Ver
> `reports/phase_3_5d/ESCALATION_PENDING.md` e
> `jornada/2026-04-21-08-e1-arbitration-block.md`.
> **Execução:** self-improve loop autônomo (branch dedicada, não `main`).

---

## 0. Por que Phase 3.5e existe

Phase 3.5d rodou 13 iters sobre 3× LETFs e encontrou 1 "winner" (E1
`vol15_lk20` TQQQ+GLD) que passou aparentemente todos os gates mas foi
rejeitado por arbitration adversarial unânime. Núcleo do problema: PBO=0.151
de E1 foi atingido reduzindo o grid CSCV de 7 configs (D5: 0.599) para 3
(D5b: 0.651) para 2. Mesma estratégia, mesmos dados, só o denominador mudou.
Isso é exatamente o anti-pattern que PBO foi desenhado para detectar
`[advances_fin_ml, p.208-211]`.

**Diagnóstico:** o loop permitiu geração iterativa de leads onde o grid de
CSCV era definido pelo próprio lead. Cada lead escolhia seu próprio N. Isso é
cherry-picking procedural do gate.

**Corretivo Phase 3.5e:**

1. **Grid de configs pré-declarado no spec**, não no código do lead.
2. **Todos os configs rodam em todos os leverage levels** (2× e 3×)
   para comparação apples-to-apples.
3. **Cumulative N_trials tracked** em `docs/self_improvement/trial_count.json`
   — DSR usa contagem honesta, não N=2 por lead.
4. **Loop patchado** (já feito em iter anterior): bloqueia auto-advance past
   phases com token `arbitration`/`escalation`, aborta em `*_concern:`
   unresolved, testes regressivos em `tests/test_validation.py`.
5. **Universe mandate-aligned:** SSO/QLD (2×) primary + UPRO/TQQQ (3×)
   comparison. Gayed original testou SPX+T-bills
   `[leverage_for_the_long_run, ch.2]` — SSO é o LETF Gayed-validated mais
   próximo do original. Inclui 3× pra permitir comparação Calmar/Sharpe
   risk-adjusted conforme decisão do usuário 2026-04-21.

---

## 1. Objetivo (north star)

Encontrar **uma ou mais configurações swing trade** sobre 2× ou 3× LETFs que:

1. Passe gates obrigatórios imutáveis (§6) do investment mandate.
2. Supere SPY buy-and-hold pós 15% IR BR na janela comum.
3. Seja validada cross-lib (bt, vectorbt, backtrader) ≥ 2/3 engines
   dentro de ±3pp CAGR.
4. Sobreviva à comparação cross-leverage:
   - Calmar(candidate) > Calmar(buy-hold leveraged)
   - Sharpe_net(candidate) > Sharpe_net(buy-hold SPY net 0.756)
5. Cite `[book.slug, p.X]` em toda parameter/filter/rebalance rule.

**Decisão final de qual leverage adotar sai do par Calmar/Sharpe
risk-adjusted, não de CAGR nem MaxDD isolados** (decisão do usuário
2026-04-21).

---

## 2. Universe (2× e 3× LETFs, mandate-aligned)

### 2.1 Primary universe (2× LETFs — track principal)

| Ticker | Underlying | Leverage | Inception | ER |
|---|---|---|---|---|
| SSO | S&P 500 | 2× | 2006-06-21 | 0.91% |
| QLD | NASDAQ-100 | 2× | 2006-06-21 | 0.95% |

SSO é o LETF 2× Gayed-validated mais próximo do `[leverage_for_the_long_run, ch.2]`
(Gayed testou SPX+T-bills sintético L=2). Windows reais ≥ 19 anos em 2026.

### 2.2 Comparison universe (3× LETFs — para risk-adjusted comparison)

| Ticker | Underlying | Leverage | Inception | ER |
|---|---|---|---|---|
| UPRO | S&P 500 | 3× | 2009-06-25 | 0.91% |
| TQQQ | NASDAQ-100 | 3× | 2010-02-09 | 0.84% |

Inclui 3× **para comparação**, não como track primário. Todos os configs
que rodam em SSO devem também rodar em UPRO; QLD ↔ TQQQ. Decisão final usa
Calmar/Sharpe cross-leverage.

### 2.3 Off-leg universe (multi-tested, não pre-selecionado)

| Ticker | Papel | Lições 3.5d | Status |
|---|---|---|---|
| Cash (0%) | baseline | passivo, sem rendimento; D2 baseline | ativo |
| GLD | Gold | off-leg dominante em D2 TQQQ | ativo |
| TLT | 20+Y treasury | off-leg tradicional Gayed; TMF 3× é structural fail | ativo |
| SHV | 1-3Y treasury ETF | equivalente cash com carry | opt-in (fetch em iter 0 se usado) |

Cada config é rodado em **todas as 3 off-legs ativas** inicialmente (cash,
GLD, TLT) = 3 × 4 tickers × 12 configs = **144 trials iniciais**. Se a
análise 3.5e-arbitration indicar que SHV adicionaria valor, fetch + expande
o grid (recompute PBO honesto sobre 192 trials). **Off-leg fixo em TMF 3×
proibido** (3.5d D2: MaxDD -82% a -87%, structural fail).

### 2.4 Benchmark universe (comparação obrigatória)

| Ticker | Papel |
|---|---|
| SPY | buy-and-hold benchmark (CDI + 15% IR BR) |
| 50/50 SPY+GLD | passive baseline alvo risk-adjusted |

---

## 3. Data pipeline

### 3.1 Source discipline

1. **Stage 1** — `reports/phase_3_5c/cross_lib/data/reference_prices.parquet`:
   precisa incluir SSO, QLD, UPRO, TQQQ, SPY, GLD, TLT, SHV. **Tiingo é a
   fonte primária** (SPY/QQQ/GLD/TLT/SHV + LETFs SSO/QLD/UPRO/TQQQ adicionados
   em 2026-04-21). yfinance apenas fallback para UGL/SPXL/TMF (ainda não em
   Tiingo).
2. **Stage 2** — `reports/phase_3_5c/cross_lib/stage2_validation.run_stage2()`.
   Usa testfol.io `testfolio_spysim_leverage.parquet` como fonte independente
   (SPY 1x/2x/3x equity 1885-2026). Tolerância Δ CAGR ≤ 3 pp.
   - SSO → `spy_2x_equity`, UPRO/SPXL → `spy_3x_equity` (concordance check possível)
   - QLD/TQQQ/UGL/TMF → Stage-2 = `na` (sem QQQSIM/GLDSIM/TLTSIM; work future)
   - **Proibido** chamar yfinance direto em sweep scripts — causa yfinance-vs-
     yfinance drift (iter 21: QLD Δ8.21pp; iter 23: TQQQ Δ15.16pp).
3. **Synthetic extensions:** SSO/QLD pre-2006 via `r = L × r_SPX_TR - drag -
   expense` conforme mandate §4. Pre-inception synthetic é opcional — só se
   um winner passar gates no histórico real e precisar de 1970-2005 para
   stress.

### 3.2 Reference_prices update necessário

SSO/QLD e SHV podem não estar no parquet atual. Verificar:

```bash
.venv/bin/python -c "import pandas as pd; df=pd.read_parquet('reports/phase_3_5c/cross_lib/data/reference_prices.parquet'); print(df['ticker'].unique())"
```

Se faltar, bootstrap iter inicial (D0-prep) adiciona os missing tickers.
Regra: **não re-rodar leads se parquet mudou** — rebaseline mandatório.

---

## 4. Grid de configs pré-declarado (IMUTÁVEL, ≥12 famílias)

**Esse grid é o "universe of trials" que entra na CSCV `[advances_fin_ml, p.208-211]`.
Qualquer modificação post-hoc invalida PBO+DSR. Adições requerem nova Phase.**

Cada config tem: signal family, parameterização, citação. Todas rodam em todos
os 4 tickers de asset (SSO, QLD, UPRO, TQQQ) × 4 off-legs (cash, SHV, GLD, TLT)
= 16 combinações por config × 12 configs = **192 trials totais**.

### Family 1 — Binary regime MA (Gayed canonical)

| Config | Asset signal | Threshold | Off-leg select | Citação |
|---|---|---|---|---|
| `c01_sma200_gld` | SMA200 | price > SMA | GLD | `[leverage_for_the_long_run, ch.2]` |
| `c02_sma150_cash` | SMA150 | price > SMA | cash | `[leverage_for_the_long_run, p.30]` |
| `c03_ema100_tlt` | EMA100 | price > EMA | TLT | `[leverage_for_the_long_run, p.31]` |
| `c04_sma200_shv` | SMA200 | price > SMA | SHV | `[leverage_for_the_long_run, ch.2]` |

### Family 2 — Momentum-based (Antonacci + Clenow)

| Config | Signal | Trigger | Citação |
|---|---|---|---|
| `c05_mom12mo` | 12-month abs momentum | mom > 0 → leveraged, else off-leg | `[dual_momentum, ch.6]` |
| `c06_mom6mo` | 6-month abs momentum | mom > 0 → leveraged, else off-leg | `[dual_momentum, ch.6]` |
| `c07_clenow_trend_heavy` | composite 90d trend+mom+vol (0.5/0.3/0.2) | score > 0 | `[stocks_on_the_move, p.81]` |

### Family 3 — Breakout

| Config | Signal | Citação |
|---|---|---|
| `c08_donchian_20_10` | Donchian entry=20d, exit=10d | `[kaufman_trading_systems, ch.4]` |
| `c09_donchian_40_20` | Donchian 40/20 | `[kaufman_trading_systems, ch.4]` |

### Family 4 — Vol-targeting (continuous sizing)

| Config | Target vol | Lookback | Off-leg | Citação |
|---|---|---|---|---|
| `c10_volTarget15_lk20` | 15%/yr | 20 days | weighted remainder | `[volatility_trading, ch.2]` |
| `c11_volTarget20_lk30` | 20%/yr | 30 days | weighted remainder | `[volatility_trading, ch.2]` |

### Family 5 — Passive baselines (informational gates)

| Config | Rule | Citação |
|---|---|---|
| `c12_bh_50_50` | fixed 50/50 asset+GLD, rebal monthly | `[permanent_portfolio, ch.3]` |

**Total inicial:** 12 configs × 4 assets × 3 off-legs = **144 trials** (opt-in SHV
expande para 192 se necessário pós-arbitration).

### Regra IMUTÁVEL

Mudanças neste grid após iter 1 são **bloqueadas**. Se uma família parecer
claramente fora do universo relevante (ex: Donchian falhar em TODOS os
assets), ela permanece no grid como "known loser" — PBO precisa dos trials
completos `[advances_fin_ml, p.211]`.

---

## 5. Rejected (explicitly do NOT revisit)

- **TMF como off-leg 3×** — structural fail 3.5d D2 (-82% a -87% MaxDD).
- **Inverse LETFs** (SQQQ, SPXS, SDOW) — decay structural, out of mandate.
- **Grid shrinkage for PBO passing** — arbitration rejected Phase 3.5d E1.
- **Single-asset TQQQ+GLD pipeline isolado** — Phase 3.5d already explored.
  3.5e deve testar todos em apples-to-apples cross-leverage.
- **Ad-hoc gate loosening** — Calmar>0.5 e SN>0.8 são imutáveis do mandate.
- **Intraday LETF trading** — Plano A lane only, fora Phase 3.5e.

---

## 6. Gates obrigatórios (imutáveis, do mandate §5)

Todos DEVEM passar simultaneamente para um config virar winner:

| Gate | Threshold | Citação |
|---|---|---|
| PBO (CSCV, n_blocks=10) | < 0.5 | `[advances_fin_ml, p.208-211]` |
| DSR p-value (n_trials = cumulative count) | < 0.05 | `[advances_fin_ml, p.275]` |
| Walk-forward (8 splits) | ≥ 6/8 positive | `[advances_fin_ml, ch.12]` |
| Single-block OOS (last 20% hold-out) | Sharpe ≥ 0.5 × IS | `[advances_fin_ml, ch.12]` |
| Forward-window stress (last 63 days) | Sharpe > 0 | `[advances_fin_ml, ch.12]` |
| CAGR_net vs SPY_net | CAGR_net > SPY_net (common window) | mandate §2 |
| Calmar | > 0.5 | mandate §5 |
| Sharpe_net (após 15% IR BR) | > 0.8 | mandate §2,§5 |
| Cross-lib concordance | ≥ 2/3 libs, Δ CAGR ≤ 3pp | spec 3.5c §6.2 |
| Stage-2 data concordance | Δ CAGR ≤ 3pp vs yfinance | spec 3.5c §6.3 |

**Zero bypass.** Gate afrouxado ≠ gate.

### 6.1 PBO honest computation

PBO roda sobre a matriz (T, N_configs) com N_configs = 192 trials (todo o
grid). **Não é aceitável** calcular PBO sobre subconjunto do grid.

### 6.2 DSR cumulative n_trials

DSR usa n_trials = **total de configs testadas no dataset cumulativamente**
(lido de `docs/self_improvement/trial_count.json`, atualizado por cada iter).
Não n_trials=n_configs_do_lead.

### 6.3 Regressive test hooks

`pbo()` com N<4 emite `UserWarning`. `test_small_n_pbo_is_unstable_regression`
documenta a instabilidade. Loop bail em `*_concern:` unresolved. Ver
`tests/test_validation.py::TestPBO`.

---

## 7. Winner selection & leverage comparison

### 7.1 Primary winner selection

De todos os 192 trials, seleciona configs que:

1. Passam todos os gates §6.
2. Passam gate adicional: **beat passive 50/50 SPY+GLD pós 15% IR BR** em
   CAGR_net sem piorar Calmar significativamente (|ΔCalmar| < 0.2).

### 7.2 Cross-leverage comparison

Se múltiplos configs passam, comparar:

| Métrica | Prioridade |
|---|---|
| Sharpe_net | 1ª — risco ajustado puro |
| Calmar | 2ª — tail-risk adjusted |
| CAGR_net | 3ª — apenas desempate |
| MaxDD | desempate inverso (preferir menor) |

**Critério final:** se Sharpe_net(2×) ≥ Sharpe_net(3×) − 0.1 E Calmar(2×) >
Calmar(3×), prefere 2× (decay drag menor, mais robusto regime-cross). Caso
contrário, 3× é aceito se justifica-se pelo Sharpe gap.

### 7.3 Escalation triggers (spec §7 do template)

1. Se nenhum config dos 192 passa gates § 6 → escalar humano. Opções:
   (A) expandir grid pra outra leverage (intermediário 1.5×), (B) revisar
   gate thresholds, (C) abandonar Plano B.
2. Se ≥ 10 configs passam → suspeita de gate afrouxamento ou data leak;
   escalar.
3. Se PBO subir > 0.4 em qualquer rebaseline → escalar.

---

## 8. Loop protocol (respeita guards Phase 3.5d corretivo)

1. **Phase name:** `phase: 3.5e-breadth-hunt` (sem token
   arbitration/escalation, não dispara guard).
2. **Iter tasks (fanout mode):** cada iter processa UM dos 192 trials, bump
   `trial_count.json`, append to `active_lead_registry`.
3. **Aggregator iter:** quando pending=0, aggregator computa PBO+DSR sobre
   matriz completa (192 configs), filtra gates, reporta winners.
4. **Sem auto-advance phase** — ao completar aggregator, fica em
   `phase: 3.5e-arbitration`. Loop pára. Human lance arbitration (`Skill
   judge-spec`).
5. **`*_concern:` fields** só quando human reviewed + documented em jornada.

---

## 9. Artifacts por iter

```
reports/phase_3_5e/
├── trial_registry.json         # 192 pending → sweeping → done
├── configs/
│   ├── c01_sma200_gld.py       # signal implementation
│   ├── c02_sma150_cash.py
│   └── ...
├── results/
│   ├── c01_sma200_gld__SSO__GLD.json
│   ├── c01_sma200_gld__SSO__cash.json
│   └── ...
├── AGGREGATE.md                 # PBO+DSR over full matrix
└── WINNERS.md                   # configs passing §6 gates
```

---

## 10. Citations

- `[advances_fin_ml, p.208-211]` — PBO CSCV methodology
- `[advances_fin_ml, p.275]` — DSR Harvey-Liu deflator
- `[advances_fin_ml, ch.12]` — walk-forward validation
- `[leverage_for_the_long_run, ch.2]` — Gayed SMA regime canonical
- `[leverage_for_the_long_run, p.30-31]` — MA period sensitivity
- `[dual_momentum, ch.6]` — Antonacci absolute momentum
- `[stocks_on_the_move, p.81]` — Clenow composite signal
- `[kaufman_trading_systems, ch.4]` — Donchian breakout
- `[volatility_trading, ch.2]` — vol-targeting mechanics
- `[permanent_portfolio, ch.3]` — passive benchmark baseline
- `docs/investment-mandate.md §2,§4,§5` — CAGR floor, universe, gates

---

## 11. Próximo passo concreto

1. Verificar parquet tem SSO, QLD, SHV (bootstrap se faltar).
2. Avançar `memory.md` phase `3.5e-escalation-pivot` → `3.5e-breadth-hunt`
   com leads c01-c12 em `## Leads`.
3. Relançar loop com `MAX_ITER=20 SWEEP_MODE=fanout`. Cada iter = 1 trial do
   grid 192.
4. Ao completar, human roda arbitration antes de aceitar qualquer winner.
