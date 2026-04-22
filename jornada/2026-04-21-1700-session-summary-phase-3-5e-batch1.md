# Sessão 2026-04-21 — Phase 3.5e batch 1 (iters 14-43): 0 winners, pipeline consertada

**Duração:** ~4h (13:15 → 17:02)  
**Iters totais:** 30 (iter 14 a 43, em 2 shell loops)  
**Verdict:** 0 winners; 5 config families avaliadas; 38 de 144 trials consumidos.

---

## O arco da sessão

### Parte 1 — Loop original (iters 14-23) ROLLBACKED

Shell loop anterior (PID 2901102) rodando desde 13:15 produziu c01 completo + c02 parcial.
c01 AGGREGATOR: DEAD 0/12 (PBO=0.139 PASS — signal real; mas FWD tariff shock killed all).
Durante o c02 sweep, Stage-2 reportou ΔCAGR crescente em QQQ-base:
- iter 21 QLD c02: **8.21pp** divergente
- iter 23 TQQQ c02: **15.16pp** divergente

Usuário interrompeu: *"yfinance precisa ser a menos confiável; use Tiingo (pago) e
testfol.io (sólido). Por que essa divergência?"*

**Diagnóstico**: `reference_prices.parquet` cacheava yfinance post-inception para LETFs;
Stage-2 re-fetchava yfinance ao vivo. Dois snapshots da mesma fonte, drift pela
retroactive adjusted-close. Nunca foi "artifact synthetic". Era yfinance-vs-yfinance.

### Parte 2 — Fix Option C (commits f7c2810, 6729468)

| Componente | Antes | Depois |
|---|---|---|
| Tiingo bulk cache | sem LETFs | +SSO/QLD/UPRO/TQQQ/SHV (inception → today) |
| `reference_prices.py` post-inception | yfinance `yf.download()` | **Tiingo adj_close**; yf só fallback p/ UGL/SPXL/TMF |
| Stage-2 validator | yfinance re-fetch | `stage2_validation.py` helper + testfol.io `spysim_leverage.parquet` |
| Spec §3.1 | permissivo | proíbe yfinance direto em sweep scripts |
| Pytest | 908 green | 914 green (+6 stage2 tests) |

c02 foi resetado para re-sweep (3 trials deletados: QLD/SSO/TQQQ; c01 preservado — verdict
DEAD não muda com ±0.15 de Sharpe). trial_count 15→12.

### Parte 3 — Loop post-fix (iters 24-43) 

Shell loop relaunchado. Stage-2 concordance validada empiricamente:

| Ticker | Stage-2 fonte | ΔCAGR |
|---|---|---|
| SSO | testfol.io SSOSIM | **0.17pp** ✓ |
| QLD | bt cross-lib | 3.01pp marginal |
| TQQQ | testfol.io TQQQSIM | **0.05pp** ✓ |
| UPRO | testfol.io UPROSIM | **0.12pp** ✓ |

Contra 5-15pp do pipeline antigo. Fix funcionou.

**Descoberta colateral:** `data/testfolio/cache/history.parquet` contém
SSOSIM/QLDSIM/UPROSIM/TQQQSIM/UGLSIM além do cache SPY-only que meu helper usava.
O agente encontrou `testfolio_loader` e fez Stage-2 aplicando a strategy em *SIM
returns — muito melhor que CAGR buy-hold. Dívida técnica: atualizar
`stage2_validation.py` para consolidar os dois caminhos.

---

## Resultados por config family

| Lead | Configs | Tickers | Trials | Status | Best Sharpe_net | Killer |
|---|---|---|---|---|---|---|
| **c01** sma200 × 3 off-legs | 3 | 4 | 12/12 DEAD | PBO=0.139 PASS, econ FAIL | 0.660 (QLD+GLD) | FWD tariff shock |
| **c02** sma150_cash | 1 | 4 | 4/4 DEAD | econ FAIL | 0.475 (QLD) | cash 0% yield bottleneck |
| **c03** ema100_tlt | 1 | 4 | 4/4 DEAD | DSR+OOS+econ FAIL | 0.505 (TQQQ) | TLT 2022 equity+bond crash |
| **c04** sma200_shv | 1 | — | SKIPPED | SHV missing from parquet | — | data pipeline incompleto |
| **c05** mom12mo × 3 off-legs | 3 | 4 | 12/12 DEAD | econ FAIL, DSR FAIL | 0.560 (QLD+GLD) | monthly can't protect intra-month LETF crashes |
| **c06** mom6mo × 3 off-legs | 3 | 2/4 parcial | 6/12 | sweep incompleto | 0.547 (QLD) | mesmo c05 + FWD tariff |

Soma: **38 trials completos** (c01+c02+c03+c05+c06), ~44 esperados se c04 rodasse.

---

## Padrões estruturais aprendidos

1. **FWD tariff shock Q1-2026 é o killer dominante** de todas binary-MA e monthly-momentum.
   Só SMA150 (c02) e TLT off-leg (c03 TQQQ) sobreviveram — mas aí Sharpe despenca por
   whipsaw/crash respectivamente.

2. **Cash off-leg tem floor inaceitável**: c02 fracassa mesmo com SMA150 passando FWD
   porque 28% do tempo em cash @ 0% yield puxa Calmar abaixo de 0.5.

3. **TLT off-leg falha em regime 2022**: equity+bond joint crash. Gayed assume não-
   correlação; em rates-hike regime isso quebra.

4. **Monthly momentum (c05/c06) não protege 3× LETF** de crashes intra-mês. Mesma
   conclusão do D4 da 3.5d; mantida.

5. **15% IR BR tax drag é estrutural**: gross Sharpe ≥ 0.94 necessário pro net 0.8 gate.
   Nenhuma config até agora atinge isso consistentemente na janela 2001-2026.

---

## Estado ao fim da sessão

- Branch `phase3.5d/plano-b-v2-3x-letf-20260420`, memory iter=43, phase 3.5e-breadth-hunt.
- active_lead_registry = `c06_mom6mo_abs_momentum` (status=sweeping, pending=[TQQQ, UPRO]).
- 0 winners; 2 config families restantes no grid (c07 Clenow composite, c08-c11
  Donchian/vol-target, c12 buy-hold) + c04 pending fix.
- Pytest 914 green. Dívidas técnicas: task #11 (helper merge) e task #12 (SHV fix).

## Próxima sessão — decisão pendente

**Option A (finalizar grid honesto)**: fixa SHV, reativa c04, continua loop até c12
aggregator. ~50 iters a mais (~5h). Produz grid completo de 44+ trials para PBO honesto.

**Option B (escalar decisão)**: reconhece padrão — 3 famílias estruturalmente
diferentes (binary MA, EMA+bond, monthly momentum) todas falham por razões
complementares. Hipótese: LETF rotation daily com 15% IR BR é matematicamente
apertado no regime SPY/QQQ atual. Escalar ao usuário: afrouxar gate, trocar universo,
ou aceitar Plano B sem winner e focar só em Plano A.

**Recomendação**: rodar c07 (Clenow composite) e c10-c11 (vol-target) **antes** de
escalar — são as últimas families estruturalmente diferentes. Se falharem, B é o caminho.

## Citações acumuladas na sessão

- `[leverage_for_the_long_run, ch.2]` — SMA200 canonical Gayed
- `[leverage_for_the_long_run, p.30]` — SMA150 sensitivity
- `[leverage_for_the_long_run, p.31]` — EMA100 + bond off-leg
- `[leverage_for_the_long_run, p.16-17]` — synthetic formula + FFR-aware
- `[dual_momentum, ch.6]` — Antonacci abs momentum (12mo + 6mo)
- `[advances_fin_ml, p.208-211]` — PBO CSCV, grid pre-declaration
- `[advances_fin_ml, p.31-34]` — two-stage data isolation
- `[advances_fin_ml, p.276]` — DSR honest n_trials
