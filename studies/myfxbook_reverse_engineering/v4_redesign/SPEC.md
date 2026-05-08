# SPEC — MyFxBook Pipeline v4 Redesign (frozen contract)

Este e o contrato congelado do redesenho. **Nao alterar sem decisao explicita
do usuario** registrada em `jornada/`. Source of truth: o plano aprovado em
2026-05-03 (`/home/victor/.claude/plans/majestic-greeting-sutton.md`).

## Decisoes travadas pelo usuario (2026-05-03)

| Decisao | Escolha | Impacto |
|---|---|---|
| Dados extras | **Free apenas** (Forex Factory + Dukascopy ticks + Tiingo) | A5 multi-broker spread fora |
| Objetivo | **Hibrido** (decode-self + filter-and-copy ambos rodam) | Fase 3a e 3b ambas executam apos decision gate |
| Janela R&D | **8-12 semanas, Fases 1+2+3 completas** | Cronograma fechado |

## Decisoes travadas apos review GPT-5.5 (2026-05-03 +1h)

| Item | Decisao | Razao |
|---|---|---|
| `is_live` no pre-screen | **Warning-only**, nao bloqueia | 5/52 systems sao Demo; bloquear eliminaria material decodavel arbitrariamente. Real exigido apenas para reativacao Plano A (mandate §3) |
| Track record do EA | **PSR** (nao DSR com M=1) | DSR pressupoe selecao ex-post entre M tentativas; track do EA e serie unica do vendor. PSR e o objeto certo `[advances_fin_ml, p.260-263]` |
| DSR com correcao M | Aplica em **Fase 3a apos LightGBM mining N candidate rules** | Ai sim ha M tentativas explicitas |
| PBO escopo | **Complementa WF**, nao substitui | PBO = sorte na selecao entre N candidates; WF = generalizacao temporal de UMA regra |
| LightGBM dependency | Adiciona ao extra `myfxbook_decoder` em pyproject.toml | Task 005 |
| Allow-list explicita de paths | PROTOCOL.md secao "Allow-list" enumera | Task scope vs guardrail clarity |
| Spec completeness | Apenas Fases 1 (tasks 001-008) sao detalhadas; 009-028 detalhadas on-demand | YAGNI; spec depende dos sobreviventes da Fase 1 |

## Decisao humana apos task 007 (2026-05-04)

| Item | Decisao | Razao |
|---|---|---|
| Survivor para Fase 2 | **`fase2_eligible_survivors` = `pre_screen_decision=GO AND adversarial_auc<0.65 AND mandate_24_pass=true`** | O batch gerou 21 `pre_screen GO`, acima do limite N<=10. A correcao separa pre-screen como evidencia operacional de elegibilidade downstream; thresholds ja estavam no SPEC e nao foram otimizados apos resultado `[evidence_based_ta, p.325-328]` `[advances_fin_ml, ch.5]` `[advances_fin_ml, p.273-275]`. |
| `pre_screen_go_systems` | **Audit-only** | Mantem a lista de EAs com track record estatisticamente aceitavel, mas nao autoriza Fase 2 se synthetic continua distinguivel ou falha hard gates. |

## Decisao humana apos Fase 1 STOP (2026-05-04)

| Item | Decisao | Razao |
|---|---|---|
| Proxima trilha | **Pivot para Fase 3b/filter-and-copy replanejado** | Fase 2A/decode-self nao tem universo valido (`n_fase2_eligible_survivors=0`), mas os 21 `pre_screen_go_systems` ainda sao evidencia auditavel de track records que passaram MCPT/PSR/concentration. Avaliar como sistemas externos filtraveis, nao como regras a reverse-engineer. |
| Primeira task do pivot | **`009-fase3b-replan-filter-copy`** | Criar contrato novo antes de rodar qualquer ranking/copy-monitor; sem paper/live, sem AutoTrade real, sem relaxar thresholds apos resultado. |
| Universo inicial | **21 `pre_screen_go_systems` audit-only** | Entrada para triagem de copiabilidade; nao sao survivors de decode-self nem autorizacao de deploy. |

## 8 modos de falha enderecados

1. Assimetria informacional (M5/M1 nao contem trigger do EA)
2. Metrica errada (`fidelity_score` mistura termos; timing F1 fica oculto)
3. Single-family classifier para EAs multi-estrategia
4. Feature set "livro-texto" sem cross-asset/news/tick
5. Gates §2.4 nao enforcados (DSR informativo, PBO ausente, WF8 sem purge)
6. Sem pre-filtro de tradeability do EA
7. Over-fire tratado como erro, nao como sinal de "falta meta-label"
8. Sem validacao adversarial (real-vs-synthetic AUC)

## Tres trilhas (escopos travados)

### Trilha A — Inputs ricos (free only)
- A1: News calendar (Forex Factory CSV)
- A2: Tick volume + tick imbalance (Dukascopy ticks)
- A3: Cross-asset state (DXY/VIX/gold-silver/BTC dominance via Tiingo)
- A4: Realized-vol regime (HAR-RV) `[volatility_trading, p.173-177]`
- A5: ~~Multi-broker spread differential~~ — **DESCARTADO**

### Trilha B — Metodologia
- B1: LightGBM purged-CV substitui univariate+tree+RIPPER `[advances_fin_ml, ch.5]`
- B2: Meta-labeling primary side + secondary take/skip `[advances_fin_ml, p.84-89]`
- B3: Transformer encoder small (4 layers, 64 dim) sobre janela [-200, 0] bars
- B4: HMM 3-estados regime mixture (trend/MR/quiet)
- B5: Adversarial discriminator real-vs-synthetic LightGBM AUC

### Trilha C — Reformular objetivo
- C1: Pre-filtro de tradeability (K1 sanity + MCPT + PSR + concentration; is_live warning-only)
- C2: ~~Cluster-level decoding~~ (deferido para v5 se v4 fechar)
- C3: Filter-and-copy via myfxbook AutoTrade (Fase 3b)
- C4: Symbolic regression (PySR/gplearn) — conditional, so se Transformer estagnar
- C5: Out-of-domain validation (EUR train, JPY test)

## Cronograma 12 semanas

| Sem | Fase | Output |
|---|---|---|
| 1-2 | Fase 1 | `pre_decode_screen.py` (K1+MCPT+PSR+concentration), `cpcv.py` (PBO), `adversarial_validator.py`. Gates §2.4 hard refactor — DSR aplicado sobre **synthetic post-mining** (nao na track record do EA). **Output: lista N≤10 `fase2_eligible_survivors`** |
| 3-4 | Fase 2A (A1-A4) | News + cross-asset + tick volume + RV regime em `decoder_features.py` |
| 5-6 | Fase 2B (B1-B2) | LightGBM miner + meta-labeling. **Decision gate sem 6** |
| 7-8 | Fase 3a + 3b | Transformer + HMM (3a); ranking score + start forward monitor 60d (3b) |
| 9-10 | Fase 3a refino | Symbolic regression (cond.); cross-lib ±3pp |
| 11-12 | Validacao final | Out-of-domain transfer; `_diagnostics/PIPELINE_V4_FINAL.md` |

## Decision Gate Fase 2 → 3 (semana 6)

Avaliar nos N≤10 `fase2_eligible_survivors`:

- F1 timing > 0.30 em ≥ 3 systems?
- Adversarial AUC < 0.65 nesses 3?
- Mandate §2.4 gates (PBO < 0.5, DSR p < 0.05, WF ≥ 6/8 com purge, OOS bootstrap CI 99.9% low > 0)?

**Se SIM:** Fase 3a (decode-self) prioridade; 3b paralelo como hedge.
**Se NAO:** Fase 3b (filter-and-copy) prioridade; 3a paralelo como exploracao.
**Em ambos:** Fase 3a e 3b executam (decisao usuario 2026-05-03), so a alocacao varia.

## Criterios de sucesso final (semana 12)

≥1 system passa SIMULTANEAMENTE:

- MCPT p < 0.05 (own track) `[evidence_based_ta, p.325-328]`
- DSR p < 0.05 (synthetic) `[advances_fin_ml, p.273-275]`
- PBO < 0.5 via CSCV `[advances_fin_ml, p.208-222]`
- WF ≥ 6/8 com purge+embargo `[testing_tuning, p.148-162]`
- OOS bootstrap CI 99.9% low > 0
- Cross-lib ±3pp em vectorbt+backtrader
- Out-of-domain transfer ≥ 50% in-domain Sharpe
- Adversarial AUC < 0.65

Se zero passa: pipeline v4 retornou diagnostico definitivo — Fase 3b (copy
trading) virou a unica via aberta para myfxbook.

## Citacoes obrigatorias

Toda task que define indicador/parametro/gate cita livro de `books/summaries/`.
Exemplos:
- Meta-labeling: `[advances_fin_ml, p.84-89]`
- MCPT: `[evidence_based_ta, p.325-328]`, `[testing_tuning, p.310-322]`
- CSCV/PBO: `[advances_fin_ml, p.208-222]`
- WF purgado: `[testing_tuning, p.148-162]`
- DSR (synthetic, post-mining): `[advances_fin_ml, p.273-275]`
- PSR (own track, pre-screen): `[advances_fin_ml, p.260-263]`
- HMM regime: `[machine_trading, ch.4]`
- Symbolic regression: `[advances_fin_ml, ch.7]` (genericamente feature engineering)
- Custos curtos: `[systematic_trading, p.182-197]`

## Guardrails do mandato preservados

- §1 Plano A DORMANT — preservado, nenhum paper/live nesta proposta
- §2.4 hard-block gates — REFORCADOS (DSR p<0.05 vira hard, PBO entra)
- §2.2/§2.3 CAGR/MDD warning-only tiers — preservados
- §7 overrides — Trilha C3 (filter+copy) e divergencia possivel; aprovacao usuario explicita registrada em 2026-05-03
