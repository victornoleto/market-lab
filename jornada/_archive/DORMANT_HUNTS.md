# DORMANT HUNTS — Consolidação narrativa (2026-04-24)

Este documento substitui **~38 entradas individuais de jornada** de fases
DORMANT (Plano A/B/D/E hunts 2026-04-21→23) removidas no cleanup de
2026-04-24. Veredicto comum a todas: **FAIL em honest gates**.

**Recuperação**: `git checkout pre-cleanup-2026-04-24 -- jornada/<arquivo>`

---

## Timeline resumida

**2026-04-21**: Phase 3.5e batch 1 (Plano B, 30 iters loop, c01-c06).
Pivot Tiingo-first. E1 vol-tgt initial PASS (retido pra arbitragem).

**2026-04-22 manhã**: Phase 3.5f engine lookahead bug descoberto. V2
revalidation 6 leads — ALL FAIL. Mandate §2.2/§2.3 CAGR/MDD tiers.
Strategy D opened.

**2026-04-22 tarde**: Phase 3.7-3 top-tier literature hunt (H1/H2/H3
× 8 subagents). 8/8 FAIL. Phase 3.8-1 B1-B5 robustness sweep. 5/5 FAIL.

**2026-04-22 noite**: Phase 3.6 swing-broad hunt (A-K, 10 families).
10/10 FAIL.

**2026-04-23 madrugada**: Phase D-MVP D1 Clenow BR ranking.
10/42 → BREADTH_NO_WINNER_D. Phase E-MVP multi-market extension.
43/43 FAIL. Mandate MAINTENANCE mode signed.

**Cumulativo**: 113 honest FAIL em 2 semanas.

---

## Hunts consolidados por fase

### Phase 3.5e (Plano B LETF continuation, 2026-04-21)

| Arquivo removido | Verdict |
|------------------|---------|
| `2026-04-21-07-d7-d8-phase35d-impasse.md` | D7/D8 phase 3.5d impasse |
| `2026-04-21-07-e1-vol-tgt-winner-pass.md` | E1 vol-tgt initial PASS (later invalidated by arbitration) |
| `2026-04-21-08-e1-arbitration-block.md` | E1 arbitration blocked |
| `2026-04-21-1040-d6-clenow-composite-near-miss.md` | D6 Clenow composite near-miss |
| `2026-04-21-1535-c02-sma150-cash-dead.md` | c02 SMA150/cash DEAD 0/4 |
| `2026-04-21-1640-c03-ema100-tlt-dead.md` | c03 EMA100/TLT DEAD |
| `2026-04-21-1644-c05-mom12mo-dead.md` | c05 Momentum 12mo DEAD |
| `2026-04-21-1700-session-summary-phase-3-5e-batch1.md` | Batch 1 summary: 0 winners/38 trials/5 families |
| `2026-04-21-19-c01-sma200-aggregator-dead.md` | c01 SMA200 aggregator DEAD |

Pattern-killers: FWD tariff Q1-2026 universal; cash off-leg floor
inaceitável; TLT off-leg falha 2022 joint crash.

### Phase 3.6 (Swing-broad 10 families, 2026-04-22 noite → 2026-04-23 noite)

| Arquivo removido | Família | Verdict |
|------------------|---------|---------|
| `2026-04-22-0310-phase3.6-d_chan_mr_pairs-FAIL.md` | D Chan MR pairs | FAIL |
| `2026-04-22-0411-phase3.6-breadth-no-winner-escalation.md` | Escalation | - |
| `2026-04-23-0025-phase3.6-f_vol_target_managed_futures-FAIL.md` | F Vol-target MF | FAIL |
| `2026-04-23-0027-phase3.6-h_amh_regime_switching-FAIL.md` | H HMM regime-switch | FAIL — HMM gaussiano separa regimes mas ret-cond idêntico |
| `2026-04-23-0307-phase3.6-e_ehlers_cycles-FAIL.md` | E Ehlers cycles | FAIL |
| `2026-04-23-0309-phase3.6-i_stat_sound_indicators-FAIL.md` | I Stat-sound indicators | FAIL |
| `2026-04-23-0346-phase3.6-j_ml_classical-FAIL.md` | J ML classical | FAIL |
| `2026-04-23-0405-phase3.6-k_universal_trend-FAIL.md` | K Universal trend | FAIL — PBO 0.68 |
| `2026-04-23-2339-phase3.6-b_risk_parity_inverse_vol-FAIL.md` | B Risk parity IV | FAIL — Qian exige leverage, 2022 bond+equity joint crash |
| `2026-04-23-2339-phase3.6-c_gtaa_faber_10mo-FAIL.md` | C GTAA Faber | FAIL |
| `2026-04-23-2349-phase3.6-a_clenow_momentum-FAIL.md` | A Clenow momentum | FAIL |

Consolidado em `reports/_archive/phase_3_6_BREADTH_NO_WINNER.md`
(204 linhas).

### Phase 3.7-3 (Literário intraday H1/H2/H3, 2026-04-22)

| Arquivo removido | Hipótese | Verdict |
|------------------|----------|---------|
| `2026-04-22-1140-phase3.7-h1-maroy-ladder-FAIL.md` | H1.c Maróy Ladder | FAIL 9/13 gates — 4 flips/round-trip × 0.67bps = 104% drag IS |
| `2026-04-22-1143-phase3.7-h1-maroy-vwap-FAIL.md` | H1.b Maróy VWAP | FAIL 10/14 — Sharpe OOS −2.96 |
| `2026-04-22-1145-phase3.7-h1-zarattini-base-FAIL.md` | H1.a Zarattini base | FAIL |
| `2026-04-22-1200-phase3.7-h2-bozovic-vix-FAIL.md` | H2.a Božović VIX | FAIL — 28 eventos DARF/35y = 316% drag; signal estável mas mediocre |
| `2026-04-22-1201-phase3.7-h2-gayed-vix-floor-FAIL.md` | H2.b Gayed VIX floor | FAIL |
| `2026-04-22-1203-phase3.7-h2-vix-term-FAIL.md` | H2.c VIX term-structure | FAIL 4 hard gates — 312 switches 15y, IR vs SPY −0.24 |
| `2026-04-22-1219-phase3.7-h3-btc-donchian-FAIL.md` | H3.a BTC Donchian | FAIL 3 hard — Pepperstone N=2 crypto neutraliza rotação |
| `2026-04-22-1228-phase3.7-breadth-no-winner.md` | Closure | 8/8 FAIL, 4 recomendações R1-R4 |
| `2026-04-22-2330-phase3.7-h3-eth-donchian-FAIL.md` | H3.b ETH Donchian | FAIL 2 hard (IS Sharpe 1.68 único > 1 mas OOS Sharpe 0.66/CAGR 3.63%, IR vs ETH BH −1.23) |

3 killers estruturais cross-wave: H1 signal não replica pós-HFT;
H2 VIX reativo + DARF drag; H3 2-day swap cap amputa fat-right-tail.
Consolidado em `reports/_archive/phase_3_7_BREADTH_NO_WINNER.md`
(243 linhas).

### Phase 3.8-1 (Plano B robustness sweep B1-B5, 2026-04-22)

| Arquivo removido | Hipótese | Verdict |
|------------------|----------|---------|
| `2026-04-22-1518-phase3.8-b1-fail.md` | B1 Gayed canonical SMA-200 UPRO/SSO | FAIL 2/2 variantes — DARF year-end + SMA-200 atrasado |
| `2026-04-22-1531-phase3.8-b2-fail.md` | B2 MA-robustness sweep | FAIL 2/4 — SMA-200 × SSO winner literal, edge não statistically real pós-DARF |
| `2026-04-22-1533-phase3.8-b4-fail.md` | B4 Hsieh-Chang-Chen AR(1) | FAIL 2/4 — lookbacks curtos Sharpe ≈ 0 |
| `2026-04-22-1535-phase3.8-b3-fail.md` | B3 Pauchlyova static+trend 5-asset | FAIL 3/4 — OOS Sharpe 1.14 (único > 1.0) mas PBO 0.524 |
| `2026-04-22-1547-phase3.8-b5-fail.md` | B5 Faber 10-mo GTAA | FAIL 2/4 — turnover 1.39/yr tax-minimal mas signal weak |
| `2026-04-22-1552-phase3.8-breadth-no-winner-b.md` | Closure | 5/5 FAIL, 5 recomendações R1-R5 |

Single killer: bootstrap OOS CI low < 0 + DSR p > 0.05.
Consolidado em `reports/_archive/phase_3_8_BREADTH_NO_WINNER_B.md`
(235 linhas).

### Phase D-MVP + Strategy D open (2026-04-22 tarde → 2026-04-23 madrugada)

| Arquivo removido | Verdict |
|------------------|---------|
| `2026-04-22-1734-strategy-d-open.md` | Strategy D proposta (IBrX-100 ranking mensal, 4 famílias); override aguarda assinatura |
| `2026-04-23-0044-phase-d-mvp-no-winner.md` | Phase D aborted 10/42 — 10/10 Sharpe OOS negativo, regime break BR 2020-2023 inverte signal |

Consolidado em `reports/_archive/phase_d_mvp_BREADTH_NO_WINNER_D.md`
(89 linhas).

### Phase E-MVP (Multi-market extension, 2026-04-23)

| Arquivo removido | Verdict |
|------------------|---------|
| `2026-04-23-0618-phase-e-mvp-no-winner-mvp.md` | 42/42 FAIL catastrófico — PBO 0.786, DSR 0/42 passam, median CAGR −4.5%; 113/113 cumulativo |

Consolidado em `reports/_archive/phase_e_mvp_SUMMARY.md` (66 linhas).

### Plano A V2 honest revalidation (2026-04-22)

| Arquivo removido | Verdict |
|------------------|---------|
| `2026-04-22-plano-a-honest-revalidation.md` | 6 V2 leads re-avaliadas sob engine honest (pós-fix commit 7b90a8f). ALL FAIL. V2-L2 Gayed cai de Sharpe 2.28/CAGR 79%/MDD −21% pra Sharpe 0.56/CAGR ~14%/MDD −37% (65pp inflation). V2-L1/L3/L4/L5/L6 já DEAD. Hipótese "L2 dilui em L4 Carver RP" invalidada (L2 pesa 4.8%, não 66%). |

Detalhes completos em `reports/phase_3_5f/` (preservado, 900K).

---

## Leituras cruzadas preservadas (fora deste consolidado)

Entradas NÃO removidas — contexto arquitetural/bug forensic permanente:

- `2026-04-22-2212-engine-lookahead-bias-descoberto.md` — sessão que
  descobriu o bug
- `2026-04-22-engine-lookahead-bug.md` — narrativa humana do bug
- `2026-04-22-1252-cagr-mdd-gates-relaxados-tier-framework.md` — decisão
  mandate §2.2/§2.3
- `2026-04-21-14-data-pipeline-tiingo-first.md` — arquitetura Tiingo
- `2026-04-23-0700-overnight-summary.md` — resumo madrugada 3.5f
- `2026-04-23-0756-maintenance-mode.md` — consolidação final signed

---

## Padrão de failure: o que os 113 FAIL ensinaram

Literatura: `[advances_fin_ml, p.208-211, p.196-202, p.31-34]` +
`[leverage_for_the_long_run, p.16 fn.22]` + Harvey-Liu 2015 JOIM +
Ilmanen 2011 + Cederburg 2024.

1. **PBO > 0.5** (grid-level) — universal killer de estratégias com
   n_configs > 30
2. **DSR p > 0.05** após deflator por n_trials — universal killer de
   Sharpe ≈ 0.6-0.8 observados com N > 500
3. **Walk-Forward CAGR/MDD per-window** — killer estrutural de Plano B
   (Phase 3.8-1) e Plano E (multi-market)
4. **Bootstrap OOS 99.9% CI low < 0** — killer de signals com IR vs BH
   marginal
5. **Cross-lib |ΔCAGR| > 3pp** — expõe bugs de engine (passou em 17/18
   post-3.5c, engine clean)

O edge retail único em 2026 é **backbone passivo factor-tilted** com
diversificação geográfica + tax-aware broker selection (Plano C).
Ver `portfolio-aposentadoria.md` + `reports/portfolio_aposentadoria_v2/`.
