# Phase 3 — FINAL — Combined stop-loss + risk-signal + 7-gate battery

> **Educational / experimental.** Mandate §1: projeto em MAINTENANCE,
> 100% Plano C. Este estudo fecha como **resultado negativo honesto** e
> NÃO propõe reativar slot A/B/D.

## TL;DR (veredicto honesto)

**Zero candidatos passam no critério cross-dataset do spec §0.** A
bateria de 7 gates, aplicada rigorosamente com n_trials = 4 020
(Phase 1 + 2 + 3 cumulativo), rejeita todo (base, combo) testado.

| critério spec §0 | resultado |
|---|---|
| Passa ≥ 5/7 em educational (synth 40y) | ✅ vários passam |
| Passa ≥ 4/7 em spy_real (17y) | ❌ **nenhum** |
| Passa ≥ 4/7 em ndx_real (16y) | ❌ **poucos** (2 passam) |
| Passa os três simultaneamente | ❌ **zero** |

Os candidatos mais fortes reduzem MDD de forma expressiva (35-45%
absoluto) no synth 40y, mas a estrutura dos gates estatísticos
(walk-forward, PBO grid-level, DSR com n_trials cumulativo) os
derruba nos datasets reais. Padrão consistente com os 113/113 honest
FAIL de 2 semanas antes deste estudo (MEMORY: project_phase_3_7_3_complete).

Este resultado é **valioso** — confirma que o edge aparente do
stop-loss + risk signal no synth é em grande parte artefato de
seleção de grid; no real data não sobrevive. Salvar como lição, não
como produção.

## Combinações testadas

Quatro pares de overlays selecionados ao final de Phase 2 (spec §5.3):

| label | stop | mode | param | indicator | λ |
|---|---|---|---|---|---|
| `sl20_cool21_composite05` | 20% | time_cooldown | 21 | composite | 0.5 |
| `sl20_cool21_cape05` | 20% | time_cooldown | 21 | cape | 0.5 |
| `sl30_rec10_composite05` | 30% | recovery_trigger | 0.1 | composite | 0.5 |
| `sl30_rec10_cape05` | 30% | recovery_trigger | 0.1 | cape | 0.5 |

Escopo:

* 20 bases/dataset × 4 combos = 80 variants/dataset
* 240 sims Phase 3 (17 s wall-time)
* **n_trials para DSR cumulativo**: 2 580 (Phase 1) + 1 200 (Phase 2) +
  240 (Phase 3) = **4 020**. Penalty √(ln 4020 / ln 384) ≈ 1.40× vs.
  sweep original.

## Análise de falhas — onde as gates matam

Padrão por gate cross-dataset, para as 16 combinações (4 common bases × 4 combos):

| gate | educational (synth) | spy_real | ndx_real |
|---|---|---|---|
| **G1 PBO** (grid-level) | ✅ PASS (PBO = 0.21) | ❌ FAIL (0.78) | ❌ FAIL (0.60) |
| **G2 DSR** (p < 0.05) | mixed (~50%) | ❌ FAIL universal | ❌ FAIL universal |
| **G3 Walk-Forward** (6/8 MDD<25%) | ❌ FAIL **universal** | ❌ FAIL universal | ❌ FAIL universal |
| **G4 OOS 70/30** Sharpe > 0 | ✅ PASS universal | ✅ PASS universal | ✅ PASS universal |
| **G5 FWD post-2020** Sharpe > 0 | ✅ PASS universal | ✅ PASS universal | ✅ PASS universal |
| **G6 Bootstrap** 99.9% CI low > 0 | ✅ PASS universal | mixed | mixed |
| **G7 Cross-lib** ±3pp CAGR | ✅ PASS universal | ✅ PASS universal | ✅ PASS universal |

**Os três killers estruturais**:

1. **G3 Walk-Forward** reprovado em 48/48 casos testados (16 common
   pairs × 3 datasets). A exigência de MDD<25% por janela é fatal
   porque:
   * synth 40y tem 4-5 crashes genuínos (1987, 2000-2002, 2008-2009,
     2020, 2022) — pelo menos 2-3 deles caem em diferentes janelas WF
     de 6m OOS, cada uma com MDD > 25% mesmo com overlay.
   * real data é ainda pior: janela curta amplifica cada crash.
2. **G1 PBO grid-level** falha em spy_real (0.78) e ndx_real (0.60).
   O grid de 80 variants por dataset foi suficiente pra gerar
   sobre-ajuste visível via método CSCV. Educational escapa (PBO 0.21)
   porque a janela 40y dilui o efeito.
3. **G2 DSR** universalmente reprovado no real data. Sharpe observado
   precisa exceder o null-benchmark `E[SR_max] ∝ √(ln 4020)` a p < 0.05,
   e em 17 anos com ~6 crashes e overlays que afetam apenas uma
   fração desses eventos, não há massa crítica de trading days para
   gerar essa significância.

G4/G5/G7 passam universal — confirmam que:
* O edge existe em OOS simples (G4).
* A estratégia não explode post-2020 (G5).
* A implementação está correta (G7 cross-lib).

## Top per-dataset (para referência honesta)

Cada linha é o melhor config do dataset dentro de ΔCAGR ≥ −5 pp,
ranqueado por ΔMDD. Gates específicos por dataset mostrados no
`phase3/<dataset>/phase3_summary.md` e no
`phase3/cross_dataset_gates.md`.

### educational (synth 40y)

| # | base | combo | CAGR | ΔCAGR | MDD | ΔMDD | gates |
|---|---|---|---|---|---|---|---|
| 1 | `EMA_N200_th5_bL2_sL0` (#19) | sl20_cool21_cape05 | 16.24% | −0.51 pp | **35.77%** | +27.88 pp | **6/7** |
| 2 | `SMA_N200_th5_bL2_sL0` (#16) | sl20_cool21_cape05 | 15.86% | −1.05 pp | 32.88% | +30.42 pp | 5/7 |
| 3 | `SMA_N200_th5_bL2_sL0` (#16) | sl20_cool21_composite05 | 16.25% | −0.66 pp | 33.57% | +29.74 pp | 5/7 |

*Observação*: o TOP-1 base do educational (`EMA_N150_th5_bL3_sL0`,
baseline CAGR 27.67% MDD 54%) **não aparece** no top por effectiveness.
Seu melhor combo (`sl30_rec10_cape05`) entrega CAGR 24.01%
(Δ −3.66 pp) MDD 44.55% (Δ +9.43 pp) — **ainda fora do target 40%**.
Dá 6/7 gates educacional mas reprova 3/7 em spy_real e 3/7 em ndx_real.

### spy_real (17y)

| # | base | combo | CAGR | ΔCAGR | MDD | ΔMDD | gates |
|---|---|---|---|---|---|---|---|
| 1 | `SMA_N200_th2_bL3_sL0` (#20) | sl30_rec10_composite05 | 17.76% | −0.42 pp | 38.83% | +18.61 pp | 3/7 |
| 2 | `SMA_N200_th2_bL3_sL0` (#20) | sl20_cool21_composite05 | 13.86% | −4.33 pp | 40.86% | +16.57 pp | 3/7 |
| 4 | `SMA_N200_th2_bL2_sL0` (#7) | sl20_cool21_composite05 | 13.41% | −0.31 pp | **27.39%** | +14.74 pp | **4/7** |
| 5 | `SMA_N150_th0_bL2_sL0` (#11) | sl20_cool21_cape05 | 14.42% | +1.10 pp | 28.39% | +14.27 pp | **4/7** |

4/7 é o máximo no spy_real porque G1 PBO e G2 DSR falham no real data.

### ndx_real (16y)

| # | base | combo | CAGR | ΔCAGR | MDD | ΔMDD | gates |
|---|---|---|---|---|---|---|---|
| 1 | `EMA_N200_th2_bL2_sL0` (#16) | sl30_rec10_cape05 | 19.27% | −2.29 pp | 36.09% | +10.02 pp | **4/7** |
| 2 | `EMA_N200_th2_bL2_sL0` (#16) | sl30_rec10_composite05 | 19.91% | −1.65 pp | 36.56% | +9.55 pp | **4/7** |
| 3 | `SMA_N150_th0_bL2_sL0` (#1) | sl20_cool21_composite05 | 20.99% | −4.34 pp | 31.89% | +8.64 pp | **4/7** |

Todos 4/7 pela mesma razão que spy_real.

## Cross-dataset detail (4 common bases × 4 combos = 16 pairs)

Arquivo: `phase3/cross_dataset_gates.md` tem a matriz gate-by-gate.

Resultado agregado:

| base | edu melhor gates | spy melhor gates | ndx melhor gates | spec §0? |
|---|---|---|---|---|
| `EMA_N150_th5_bL2_sL0` | 6/7 | 3/7 | 4/7 | ❌ |
| `EMA_N150_th5_bL3_sL0` | 6/7 | 3/7 | 4/7 | ❌ |
| `SMA_N200_th0_bL2_sL0` | 5/7 | 4/7 | 4/7 | ❌ (faltou 1 em spy) |
| `SMA_N200_th0_bL3_sL0` | 5/7 | 3/7 | 3/7 | ❌ |

**Candidato mais próximo**: `SMA_N200_th0_bL2_sL0 × sl20_cool21_composite05`
— 5/7 edu, **4/7 spy**, 3/7 ndx. Falta 1 gate em ndx_real (G6 Bootstrap
ou G2 DSR) para atender spec §0. Não conta como winner.

## Resposta à pergunta central (§2 do spec)

> *"Podemos reduzir o MDD de 54% do top-1 educational para 25-40% sem
> sacrificar > 3-5 pp CAGR, usando stop + signal?"*

**Não.** Para o TOP-1 `EMA_N150_th5_bL3_sL0` (3x UPRO synth, baseline
MDD 54%), o melhor combo é `sl30_rec10_cape05` → MDD 44.55%, ΔCAGR
−3.66 pp. Ainda 4.5 pp acima do limite superior do target (40%),
**apesar de** passar 6/7 gates em educational — reprova em spy/ndx.

Para bases de leverage menor (`EMA_N200_th5_bL2_sL0`, baseline MDD 63.65%),
chegamos a MDD 35.77% com ΔCAGR −0.51 pp e 6/7 gates no synth — mas
essa base não está no top-20 de spy_real/ndx_real (cfg_id não cruza),
portanto spec §0 cross-dataset não se aplica.

## Caveats honestos

1. **n_trials cumulativo 4 020** torna DSR muito duro no real data
   (16-17 anos ~4 000 trading days × baixa Sharpe depois de custos).
   Mesmo sem overlay, poucos configs passariam DSR com essa penalty.
2. **G3 WF com MDD<25%** é particularmente cruel para estratégias de
   leveraged trend. Mesmo baseline Gayed SMA-200 3x falharia essa
   gate — não é crítica específica dos overlays.
3. **CAPE stale 2023-09** — os overlays foram testados contra crashes
   até 2022. Crash hipotético 2024+ não coberto pelo signal.
4. **Sample period bias**: synth 40y vs real 17y é um 2.5× de diferença
   em nº de janelas WF. DSR e PBO penalizam dados mais curtos.
5. **Base pool restrita**: só 4/20 bases aparecem em todos 3 top-20 das
   fontes. Para um cross-dataset estudo robusto, seria melhor testar
   todos os 20 × 3 = 60 pairs, não 16.

## Patterns confirmados da literatura

Alguns resultados são **consistentes com a literatura** (Gilchrist-
Zakrajšek EBP, Shiller CAPE, Estrella-Mishkin yield curve):

* CAPE domina como single-indicator (spec §5.2 previa)
* `recovery_trigger` vence `next_signal` e `time_cooldown` (spec §8.2)
* Whipsaw cost é real em bL=3 (spec §8.1)
* Sinais macro têm lead-time variável — falha catastrófica em períodos
  como 2022-2024 (yield curve inverteu sem recessão clássica, spec §8.3)

## Next steps (após Phase 3)

1. **Study closes as educational negative result.** Preservar artefatos
   em `studies/ema_sma_threshold_crash_protected/` (código + reports +
   CSVs) para referência futura. Não promover a nenhum slot live.
2. **Mandate §1 MAINTENANCE continues** — 100% Plano C
   (`portfolio-aposentadoria.md`). Nada muda.
3. **Lições documentadas em jornada/** para não re-fazer esse mesmo
   experimento daqui 6-12 meses sem consultar este resultado.
4. **Código preservado para futura reativação de slot** (se houver):
   * `src/market_lab/backtest/strategies/stop_loss_and_risk_signals.py`
     (vectorized + numpy-pure + 3 simulators).
   * `src/market_lab/backtest/data/macro_data_loader.py` + cache
     `data/external/macro/`.
   * `src/market_lab/backtest/signals/risk_score.py`.
   * 57 testes novos cobrindo o pipeline (todos passing).

## Tests/baseline preservados

| antes Phase 1 | após Phase 3 | delta |
|---|---|---|
| 1 104 tests | 1 161 tests | +57 (stop, variants, risk_score, macro_loader, risk_signal, combined, cross_lib) |
| 0 regressões | 0 regressões | ✅ clean |

---

*Citations:* spec §0, §2, §5.3, §6.1, §6.2, §8.1-8.3. PBO
`[advances_fin_ml, p.208-211]`. DSR `[p.222-223]`. Walk-forward
`[ch.12]`. Bootstrap `[p.196-202]`. Cross-lib `[p.31-34]`. EBP:
Gilchrist & Zakrajšek 2012 AER. CAPE: Campbell & Shiller 1988.
Term spread: Estrella & Mishkin 1998. Gayed synth LETF formula:
`[leverage_for_the_long_run, p.16, footnote 22]`.
