# Spec — Phase 4.0 (Index CFD Substitution Validation)

**Data:** 2026-04-19 (drafted post-capital-fragility discovery)
**Branch prevista:** `phase4_0/index-cfd-validation` (criar quando executar)
**Orçamento:** **5-10 iters** (1 tarde se T1/T2 já bloqueiam; 1-2 dias se cascata completa)
**Path tag:** `[PAPER PRE-REQ]` (gate para `[SHORT-HOLD CFD]` Phase 4 paper start)
**Pre-req:** Phase 3.5a-V2 encerrada com winner `gayed_ema100_L2_off_gld`. ✅ Satisfeito.
**Status:** DRAFT — aguarda aprovação do usuário antes de executar qualquer task.

---

## 0. Objetivo

Validar que a execução do **winner Plano A V2-L2** (sinal
`gayed_ema100_L2_off_gld`) pode ser transportada de **share CFDs**
(SPY/QQQ/GLD) para **index CFDs** (US500/USTEC/XAUUSD) na Pepperstone
Razor, **sem degradar os gates 13/13** que o V2-L2 passou, e
habilitar live-trading a partir de **$1.000** (em vez de $5.000 mínimo
que share CFD exige, conforme `docs/investment-mandate.md §3.6`).

**Não é** objetivo: refitar parâmetros, buscar novo sinal, varrer novas
famílias, substituir a estratégia. Phase 4.0 é **teste de
instrumento-adapter**, não research.

---

## 1. Memory compliance statement

`project_plano_a_v2_last_attempt.md` diz: "if V2 fails, no V3, abandon."
V2 **passou** (1 winner, 13/13 gates). A clause "no V3" foi condicional
a failure; não se aplica aqui.

Phase 4.0 **não é V3 de research** (não busca novo sinal). É **adaptação
de execução** (mesmo sinal, veículo diferente). Análogo a: "Plano B winner
roda em SSO, mas também pode rodar em UPRO se a spec tiver gates
equivalentes" — não é nova estratégia, é variante de execução do mesmo
winner.

Se essa interpretação for contestada pelo usuário em review, **abortar
Phase 4.0 e recomendar Caminho 2** (acumular $10k + share CFD).

---

## 2. Winner config sob teste

| Parâmetro | Valor (do JSON do winner) | Substituição Caminho 3 |
|---|---|---|
| `regime_signal` | `ema100` | ✅ sem mudança |
| `leverage` | `2.0` | ✅ sem mudança |
| `risk_on_assets` | `["SPY", "QQQ"]` | → `["US500", "USTEC"]` |
| `off_regime_asset` | `gld` | → `xauusd` |
| `rebalance_cadence` | `daily_close` | ✅ sem mudança |
| `broker_model` | `pepperstone_razor_cfd` | → `pepperstone_razor_index_cfd` (novo subset) |

Apenas universe de execução muda. Sinal, leverage, cadence idênticos.

---

## 3. Tasks (ordem sequencial, cada bloqueia a próxima)

### T1 — Rate card real Pepperstone Razor Index CFDs

**Status:** requires live Pepperstone account access (demo OK).
**Output:** `docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md`

Investigar e documentar **empiricamente** (não via marketing):

- Commission schedule: Razor tier em US500, USTEC, XAUUSD — é zero? Tem commission per lot? Per side?
- Spread típico: em horário US market open, normal session, close. 10 observações por instrumento min.
- Swap rates: long e short, em USD/lot/night, em condição Fed rate atual.
- Contract size: point value de 1 lot (confirmar $10/ponto US500, ou outro).
- Min lot e lot step: é 0.01? 0.1? Outro?
- Margin requirement em Pepperstone SCB para conta retail.

**Gate T1:**
- Commission total (commission + spread medido) ≤ 10 bps round-trip por trade em $1k notional.
- Min lot permite notional ≤ $1.000 sem rounding > 50%.

**Decisão se falha:**
- Se commission alto ou lot step gross → **Caminho 3 inviável**. Spec fecha aqui, documenta verdict, recomenda Caminho 1 (Plano B only) ou 2 (accumulate $10k).

### T2 — Dividend adjustment mechanics em Index CFD long

**Status:** requires T1 account + observação ao longo de 1 ciclo de
dividendo SPY (trimestral; SPY next ex-div ~mid-2026).
**Output:** seção adicional no doc de T1.

SPY paga ~1.5-1.8% div yield/yr em 4 distribuições. Pepperstone documenta
que index CFD long recebe **dividend cash adjustment**. Validar:

- Em ciclos passados (cTrader histórico): o cash adjustment foi 100% do
  dividend yield gross? Teve haircut? Quando foi creditado (ex-date, pay-date,
  outro)?
- Em CFD short: adjustment é cobrado? Full?

**Gate T2:**
- Gross dividend yield SPY recebido em CFD long ≥ 95% (tolerância 5%
  para haircut/timing/FX).

**Decisão se falha:**
- Se dividend yield < 90% → tracking error estimado > 0.2%/yr nas métricas;
  re-validar se é > threshold de viability no T3.
- Se dividend yield < 50% → **Caminho 3 inviável** (cuts SPY TR by half).

### T3 — Re-backtest V2-L2 em séries SPX TR / NDX TR

**Status:** puro offline; pode ser executado independente de Pepperstone
account.
**Output:** `reports/phase4_0/gayed_ema100_L2_index_cfd_backtest/`:
- `summary.json`
- `equity_curve.png` (2 painéis equivalente à Phase 3.5a-V2)
- `trade_log.csv` + `trade_log.md`
- `standard_report.md`

Adaptar `simulate_plano_a_rotation`:
- Input panel: SPX TR price (já existe em `src/ai_trade/backtest/data/spx_tr_loader.py`)
  + NDX TR synthesis (NÃO existe — precisa ser sintetizado: `r_NDX_TR = r_NDX + div_yield_NDX`, yield ~0.7%/yr via pegar `^NDX` Tiingo close e adicionar div).
  + XAU-USD price series (Tiingo ou alternativa) para off-regime.
- Cost model: **ajustar**:
  - `commission_round_trip_bps = 0.0` (assumindo T1 = Razor Index commission-free).
  - Se T1 revela commission > 0, usar valor real medido.
  - `spread_half_bps` = valor medido em T1 (pode ser maior que 2 bps share CFD).
  - `swap_daily_pct_long` = medido em T1 (tipicamente Index CFD swap é pior que share CFD porque exposto a futures basis).
- Window: **mesma** 2001-05-14 → 2026-04-14 que V2-L2.
- Splits: **mesmos** IS 2001-2017 / OOS 2018-2023 / FWD 2024-2026.

**Gate T3 (single-config sanity check antes de rodar gates full):**
- OOS Sharpe ≥ 2.0 (tolerância −13% vs 2.285 share CFD baseline).
- OOS CAGR ≥ 60% (tolerância −24% vs 79% baseline).
- OOS MaxDD ≤ −25% (sem tolerância; cap rigoroso do mandate §5).

**Decisão se falha T3:**
- Qualquer uma das 3 métricas abaixo do threshold → Caminho 3
  **inviável matematicamente** (não é bug de substituição, é fato de
  que SPX TR não reproduz edge SPY+QQQ combinado). Fechar spec aqui.

### T4 — Gates completos (PBO, DSR, bootstrap, WF) em T3 output

**Status:** sequencial depois de T3 pass.
**Output:** `reports/phase4_0/AGGREGATE.md`

Se T3 passou os 3 sanity-checks, rodar os 13 gates V2:
1. PBO CSCV 10-block < 0.5 (reuse `compute_pbo_cscv` do V2).
2. PBO CSCV 16-block < 0.5.
3. DSR p-value < 0.05 (reuse `compute_dsr_p_value`).
4. Bootstrap 99.9% CI low > 0 (stationary block, 10k resamples).
5. WF 8 windows profitable ≥ 6/8.
6. WF max-window DD ≤ 25%.
7-13. Restantes 7 subset gates conforme §6 Phase 3.5a-V2 spec.

**Importante:** n_trials dos gates (PBO, DSR) é **n_trials = 1** no
Caminho 3 (não varrermos 27 configs como o V2). Isso **afeta DSR** (que
ajusta para múltiplas tentativas). DSR com n_trials=1 é equivalente a
Sharpe ratio convencional — gate trivializa para "Sharpe > 2σ?".

**Gate T4:**
- 13/13 gates pass com zero tolerância (regras do mandate §5).

**Decisão se falha T4:**
- Se qualquer gate falha → Caminho 3 **inviável estatisticamente**.
  Documentar qual gate, jornada entry, fechar spec. Recomendar C1 ou C2.

### T5 — Verdict + propagação

**Status:** sequencial após T4.
**Output:**
- Jornada entry `jornada/YYYY-MM-DD/NN-phase4_0-verdict.md`.
- Update `docs/strategies/plano_a_v2_l2_gayed_cfd.md`:
  - §4.2: confirm Index CFD como primary recommendation para conta pequena.
  - §6.3: Phase 5.1 habilitar $1.000 real em Index CFD sem condicional.
- Update `docs/investment-mandate.md §3.6`: confirmar threshold $1k
  para Index CFD, sem asterisco.
- Update `specs/phase_4_paper_trading.md §1`: adicionar variante Index
  CFD como alternativa paper a $1k.
- Update `reports/phase3_5a_v2/AGGREGATE.md §7.5`: remover "not yet
  validated" flag do Index CFD path.

---

## 4. Gates Phase 4.0 (execute → live)

| Gate | Threshold | Fonte |
|---|---:|---|
| T1 commission + spread RT | ≤ 10 bps @ $1k notional | T1 measured |
| T1 min lot notional | ≤ $1.000 | T1 contract spec |
| T2 dividend yield capture | ≥ 95% gross | T2 historical CFD |
| T3 OOS Sharpe (new instruments) | ≥ 2.0 | T3 backtest |
| T3 OOS CAGR | ≥ 60% | T3 backtest |
| T3 OOS MaxDD | ≤ −25% | T3 backtest |
| T4 PBO/DSR/bootstrap/WF full | 13/13 pass | T4 aggregator |

**Todos os gates são AND (conjunção)**. Qualquer falha → Caminho 3
fechado, documentado, archived.

---

## 5. Não-objetivos (fora de escopo Phase 4.0)

1. **Refitar EMA-100 para NDX/SPX TR combo.** Usar EMA-100 idêntico.
2. **Explorar outros off-regime assets** (TLT CFD, BTCUSD, etc.). Só XAUUSD.
3. **Varrer leverage.** L=2 fixo conforme V2-L2 winner.
4. **Optimizar commission/spread para caso best-case T1.** Usar valores realizados.
5. **Testar em windowing diferente** do V2 (IS/OOS/FWD mesmas datas).
6. **Replicar share CFD path** em paralelo (Phase 4 paper já faz isso).

---

## 6. Orçamento e timeline

| Task | Dependência | Orçamento (iters) | Wall-clock estimate |
|---|---|---:|---|
| T1 | account Pepperstone (demo OK) | 2 | 1-2 horas (inclui abrir demo conta) |
| T2 | T1 + 1 div cycle | 1 + tempo de espera | 1h código, 3 meses calendar wait (SPY next div) |
| T3 | dados SPX TR + NDX synth | 3-4 | 4-6 horas (inclui síntese NDX TR) |
| T4 | T3 output | 2 | 2-3 horas (rodar gates completos) |
| T5 | T1+T2+T3+T4 pass | 1 | 1-2 horas (docs + jornada) |

**Total:** 9-10 iters em ~1 tarde + 3 meses de espera (T2 cycle).
**Fast-path (executar só T3+T4):** 5-6 iters, uma tarde, decision point
sobre se gates passam sem precisar de T1/T2 ainda.

---

## 7. Infraestrutura

### Novos arquivos

- `specs/phase_4_0_index_cfd_validation.md` (este)
- `docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md` (T1 output)
- `scripts/run_phase4_0_index_cfd_backtest.py` (T3 runner)
- `scripts/run_phase4_0_index_cfd_gates.py` (T4 aggregator)
- `reports/phase4_0/` directory completo (T3+T4 artefatos)
- `src/ai_trade/backtest/data/ndx_tr_loader.py` (T3 NDX TR synth — se não existir equivalente)
- `jornada/YYYY-MM-DD/NN-phase4_0-verdict.md` (T5)

### Arquivos modificados (só T5, se Caminho 3 passa)

- `docs/strategies/plano_a_v2_l2_gayed_cfd.md` (§4.2, §6.3, §9 update log)
- `docs/investment-mandate.md` (§3.6)
- `specs/phase_4_paper_trading.md` (§1)
- `reports/phase3_5a_v2/AGGREGATE.md` (§7.5)

### Arquivos intocáveis (IMMUTÁVEIS)

- Todo `src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py`
  — zero mudança no simulator; T3 runa com instâncias novas de config,
  não patches.
- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/*` (winner canônico).
- Qualquer arquivo Phase 3.5b (Plano B).

### Testes

- Novos: `tests/test_ndx_tr_loader.py` (se T3 cria synth), `tests/test_phase4_0_runner.py` (T3 integration).
- Pytest baseline atual (>= 783) deve continuar passando.
- Zero bypass de gate/fixture.

---

## 8. Risks e mitigations

| Risk | Probabilidade | Mitigation |
|---|---|---|
| T1 revela commission not-zero em Index CFD | Média (30%) | Abort with clear verdict; user opts Caminho 1/2 |
| T2 dividend adjustment < 95% (Pepperstone específico) | Média (25%) | Add tracking error column no re-backtest; re-validate T3/T4 |
| T3 OOS Sharpe degrada > 15% com NDX em vez de QQQ | Baixa (15%) | Aceitar se ≥ 2.0 absolute; flag as documented tradeoff |
| Gate T4 PBO/DSR falha em single-config (n_trials=1) | Baixa (10%) | DSR trivial; PBO não aplicável a single; usar bootstrap 99.9% como gate primário |
| NDX TR loader introduzir lookahead bug | Média (20%) | Validate via unit test: reconstructed NDX close matches QQQ up to dividend, ex-div dates match published NDX calendar |

---

## 9. Citações

- Memory clause re V3: `project_plano_a_v2_last_attempt.md` (V2 passou → clause inativa)
- Gates framework: `[advances_fin_ml, López de Prado, p.196-211, ch.11, ch.14]`
- Fixed commission dominance: `[systematic_trading, Carver, p.185-188]`
- Index CFD dividend adjustment practice: industry standard (Pepperstone docs + cTrader API)
- EMA-100 regime signal: `[leverage_for_the_long_run, Gayed, p.11-14]`
- L=2 Kelly f/2: `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`
- Phase 4.0 trigger (capital-fragility): `jornada/2026-04-19/11-capital-fragility-cost-model-bps.md`

---

## 10. Stop rules

Esta spec tem **3 stop conditions** (conjunção com §4 gates):

1. **T1/T2 abort:** commission > 10 bps ou dividend < 95% → fechar spec,
   archive Caminho 3, recomendar C1 (Plano B only) ou C2 ($10k+ share CFD).
2. **T3 abort:** OOS Sharpe < 2.0 ou CAGR < 60% → Caminho 3
   matematicamente inviável mesmo com commission zero. Fechar.
3. **T4 abort:** qualquer gate falha → Caminho 3 estatisticamente
   inviável. Fechar com post-mortem detalhado.

Qualquer stop dispara:
- Jornada entry "caminho 3 DEAD: <motivo>".
- Sem mudanças em `docs/strategies/plano_a_v2_l2_gayed_cfd.md` (fica
  como está, só share CFD path viável).
- Sem mudanças em `docs/investment-mandate.md §3.6` (threshold $5k
  continua binding para share CFD).
- Branch `phase4_0/*` fica como tombstone histórico.

**Não** criar Phase 4.0 V2 / re-try. Stop rule é binding — 1 tentativa,
go/no-go.

---

## 11. Decision point antes de execução

Antes de autorizar execução, usuário revisa:

- [ ] Interpretação memory ("Phase 4.0 é execução-adapter, não V3") — aceitável?
- [ ] Gates T3 (Sharpe ≥ 2.0, CAGR ≥ 60%, MDD ≤ −25%) — thresholds corretos?
- [ ] T4 PBO/DSR em n_trials=1 — aceitar bootstrap 99.9% como gate primário?
- [ ] Scope de arquivos modificados em T5 — algum intocável que eu listei errado?
- [ ] Timeline (1 tarde T3+T4 fast-path; T1/T2 esperam conta) — ok?

Se todos ✅ → criar branch, executar começando por **T3 (fast-path,
sem precisar de conta Pepperstone)** ou **T1 (full-path, conta primeiro)**.
