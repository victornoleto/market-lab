# Estado atual — market-lab (2026-05-09)

> **Propósito:** onboard rápido para humanos e agentes. Este doc é o
> snapshot vivo — a verdade canônica vive nos arquivos referenciados.

---

## TL;DR (2026-05-09)

🛑 **MAINTENANCE MODE** desde 2026-04-23 (mandate §1, §7).

- **Capital:** 100% **Plano C** passivo factor-tilted. Documentação pessoal movida para `victor-ia/verticals/investments/`.
- **Strategies A/B/D:** **DORMANT** (0% capital, infra retida).
- **113/113 honest FAIL** acumulado entre 2026-04-08 e 2026-04-23 (Phase 3.5f-3.8 + D-MVP + E-MVP). Pattern previsto por López de Prado DSR + Aronson 6402-rule + Li-Ferreira 2025 Network Momentum.
- **Sem hunt ativo;** revisão consolidada do mandato em 6-12 meses.

Ver `docs/investment-mandate.md` para regras canônicas, e `docs/CLEANUP_2026-04-24_LOG.md` + `docs/CLEANUP_2026-05-05_LOG.md` para audit trail dos cleanups.

---

## Status por linha de pesquisa (2026-05-09)

### Plano C — buy-hold passivo factor-tilted ✅ ATIVO
- **Status:** sole winner. 100% do capital. Zero alterações.
- **Refs:** documentação pessoal fora do repo público, em `victor-ia/verticals/investments/`.
- **Mandate §:** §1, §4.7

### Plano A (Pepperstone CFD short-hold) 🛑 DORMANT
- **Status:** V2 encerrado 2026-04-23 (6 leads honest re-validation FAIL após engine fix `7b90a8f`).
- **Reativação exige (mandate §3):** multi-asset (SPY/QQQ/Gold/BTC/ETH/FX), sweep alavancagem 1:1→1:200 × Kelly f/2, staging USD 500-1k → cap 5-10k. Single-asset edge não aceito.

### Plano B (Inter swing US LETF rotation) 🛑 DORMANT
- **Status:** Phase 3.5b/3.5c canonical preserved; Phase 3.5e c06-c12 pausado em 26%; Phase 3.8-1 hunt FAIL 5/5.
- **Reativação exige (mandate §4):** Inter Internacional, tese Gayed-anchored única fonte, CPCV+PBO+splits-mutex+bootstrap 0.001+15% DARF.

### Plano D (BR ranking mensal IBrX) 🛑 DORMANT
- **Status:** Phase E-MVP (2026-04-23) failed catastroficamente (PBO 0.786).
- **Reativação exige (mandate §4b):** literatura/regime novos. Specs novas devem viver em `docs/specs/`.

---

## Linhas exploratórias em studies/ (2026-05-09)

### studies/spy_beater_hunt/ 🛑 CLOSED 2026-04-30
- 55 iters; **B4 Conservative (25 NTSX / 25 GDE / 25 RSST / 25 ZROZ)** declared deploy-ready (Sharpe 0.745 net).
- Iters 040-055 = post-closure RSST-corrected validation.
- Refs: `studies/spy_beater_hunt/{TOP_STRATEGIES,WINNER_AND_RANKING,BASE_MEMORY}.md`.

### studies/myfxbook_reverse_engineering/ 🛑 CLOSED 2026-05-04
- Veredito final: `CLOSED_NO_OPERABLE_EDGE`.
- 55 systems avaliados Fase 1; 0 elegíveis Fase 2 (synthetics distinguíveis do real, decoder não captura regra robusta).
- Plano A continua DORMANT — não há base operacional.
- Refs: `studies/myfxbook_reverse_engineering/_diagnostics/PIPELINE_V4_CLOSURE.md`.
- Cleanup 2026-05-05: bulk OHLC (1.8GB) + trades (406MB) deletados (regeneráveis via Dukascopy se reativar).

### studies/long_term_portfolio/ ⚠️ BLOCKED ON SCORING FIX
- 14 iters completos (codex-cli); incumbent iter 011 (NTSX 35 / GDE 25 / KMLM 40, Sharpe 1.046-1.104).
- Bloqueio: `iter 009` scoring usa benchmarks gross-of-tax vs candidates net (`apples-to-oranges`).
- Status: `pending_scoring_rework` em `BASE_MEMORY.md`. Não rodar iter 011+ até fix.

### studies/global_factor_tilt_loop/ ❄️ FROZEN (pre-launch checklist)
- 14 iters (6 winners). iter 009 (HAA+Gold) Sharpe pareto frontier; iter 014 (annual-DARF) prova rotation tax-neutral sob Lei 14.754.
- Reativação aguarda completion de gold_swing_loop + sinal usuário.

### studies/letf_rotation_hunt/ 🛑 CLOSED 2026-05-06 (post-close expansions ongoing)
- **26 iters** (iters 000-025); study winner: **`qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`** (T3d K=2, Sortino lh_56y 1.3246, Sharpe 0.9191). DSR PASS at N=426 (p_v2=0.0024).
- **2026-05-08 — T5 expansion** (post-close methodology amendment): 20 new configs across iters 022-025 (T5a σ-sweep, T5b carry, T5c-grid, T5d HRP/ERC). DSR cumulative re-computed for all ~426 configs; 22 early-tier T1 configs flipped PASS→FAIL (none are winners). KILL T5-expansion: **FIRES** (best Sortino 1.1399 < threshold 1.272); T3d K=2 remains canonical winner.
- **2026-05-09 — QQQ/NDX benchmark supplement:** Reddit-methodology check re-ran original top-20 strategy universe vs `QQQSIM` instead of SPY. Operative winner remains #1 by composite rolling robustness vs QQQ, with full-history end ratio **224.31× QQQ**, `pct_above_qqq=100.0%`, and average rolling end-ratio win rate **95.8%**. Worst relative windows concentrate in 3y/5y NDX bull-recovery regimes. Report: `studies/letf_rotation_hunt/reports/STUDY_QQQ_BENCHMARK_REPORT.md`.
- **2026-05-09 — post-close loop scaffold:** autonomous research loop added under `studies/letf_rotation_hunt/{loop.sh,LOOP_PROMPT.md,LOOP_MEMORY.md,LOOP_PROTOCOL.md}`. It writes only to `loop_iterations/`, benchmarks against the frozen T3d-K2 Sortino 1.3246 winner, uses global DSR trial accounting from N=426, and never triggers capital reallocation; mandate §1 remains unchanged `[advances_fin_ml, p.222-223]`.
- Spec: `docs/specs/2026-05-08-t5-expansion-design.md`; §17 disclosure in `STUDY_FINAL_REPORT.md`.
- Refs: `studies/letf_rotation_hunt/reports/{STUDY_FINAL_REPORT,STUDY_QQQ_BENCHMARK_REPORT,SORTINO_REANALYSIS_REPORT,TIER_5_REPORT}.md`.

### studies/day_swing_strategy_hunt/ 🌱 BOOTSTRAP
- Sem iter ainda. Docs/protocol prontos. Pode resumir a qualquer momento.

### studies/weekly_momentum/ 🌱 BOOTSTRAP
- Novo estudo de momentum semanal com duas variações (`stocks`, `etfs`).
- Config inicial honesta com dados diários: sinal na quinta usando valorização ajustada dos últimos 4 pregões, venda na sexta se o vencedor mudou, compra do top-1 na segunda (`settlement_delay_days=0`) ou terça (`settlement_delay_days=1`), e manutenção se o vencedor não muda.
- Validação defensiva adicionada: `stocks` usa S&P 500 atual por padrão e, quando todos os candidatos têm momentum semanal não-positivo, a estratégia vende e fica em cash (ou usa `--defensive-asset`, ex. `ZROZ`).
- Filtro de regime opcional adicionado: `--market-filter-sma-days N` permite risco apenas quando SPY > SMA(N); primeiro diagnóstico favoreceu `top_k=5` + SMA100 para reduzir a quebra pós-2022.
- Run diagnóstico `stocks/lb4_sig3_sell1_sd0_k5_pos1_defcash_mf100`: CAGR 26.76%, MDD -48.42%, Sharpe 1.069 vs SPY CAGR 14.03%, MDD -33.70%, Sharpe 0.853. Ainda exploratório e sujeito a survivorship bias.
- Estudo comparativo preservado em `studies/weekly_momentum/STUDY_REPORT.md`: agressivo `lb60_k3_SMA200` (CAGR 47.43%, MDD -48.30%, Sharpe 1.244) e balanceado `lb60_k10_SMA100` (CAGR 28.12%, MDD -33.61%, Sharpe 1.154). Próximo passo obrigatório: universo point-in-time + custos + PBO/DSR/WF/bootstrap.
- Reporting agora inclui `plots/rolling_windows_1_3_5_10y.png` em todos os bundles regenerados. Walk-forward inicial em `walk_forward/stocks/`: 36 configs, 3y train / 1y test, CAGR 14.94%, MDD -53.57%, Sharpe 0.642 vs SPY CAGR 14.69%, MDD -33.70%, Sharpe 0.835 — alerta de overfit/instabilidade.
- Sweep controlado 2026-05-09: 200 configs por universo (`lookbacks=4,20,60,90,126`, `top_k=3,5,10,20`, filtros `none/sma100/sma200/ema100/ema200`, `allow_negative=0,1`) para momentum semanal/mensal `[stocks_on_the_move, p.60]`; outputs em `sweeps/stocks/{stocks_sp500_controlled,stocks_all_controlled}/`.
- Walk-forward controlado 3y train / 1y test `[advances_fin_ml, p.208-211]`: S&P 500 atual CAGR 42.30%, MDD -50.84%, Sharpe 1.216 vs SPY 14.69%/-33.70%/0.835; full stock cache CAGR 61.83%, MDD -60.52%, Sharpe 1.200 vs SPY 14.69%/-33.70%/0.835. Ainda **não deployable**: universo não point-in-time, custos/slippage/taxes ausentes, PBO/DSR/bootstrap pendentes `[advances_fin_ml, p.196-202]`.
- Deploy candidates congelados em `studies/weekly_momentum/DEPLOY_CANDIDATES.md`: `fixed_aggressive_sp500` (47.43% CAGR, -48.30% MDD, Sharpe 1.244), `fixed_balanced_sp500` (28.12%, -33.61%, 1.154), `dynamic_wf_sp500` (42.30%, -50.84%, 1.216), `dynamic_wf_all_stocks` (61.83%, -60.52%, 1.200). Painel comparativo em `deploy_candidates/CANDIDATE_VALIDATION_REPORT.md`; próxima validação: custos/slippage/taxes, liquidez/listing, PIT universe e PBO/DSR/bootstrap.
- Cost/liquidity stress 2026-05-09: 10/25/50 bps one-way costs + DARF anual após 10 bps + ADV20 `[stocks_on_the_move, p.81]`. 10 bps CAGR: all-stocks WF 57.29%, WF S&P 40.47%, fixed aggressive 45.25%, fixed balanced 26.39%; 10 bps + DARF CAGR: 27.19%, 17.72%, 16.64%, -3.38%. Median held ADV20: $45.5m all-stocks WF, >$260m nos S&P candidates; liquidez não é blocker a $100k AUM, mas tax drag e PIT/listing bias viraram riscos centrais.
- Anti-overfit + plots 2026-05-09: `deploy_candidates/CANDIDATE_VALIDATION_REPORT.md` agora inclui performance plot e rolling 1/3/5/10y vs SPY por candidate. Gates `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`: all-stocks WF falha PBO (0.798); WF S&P falha DSR (p=0.191); balanced falha DSR (p=0.092) e tax stress; fixed aggressive passa PBO context (0.175), DSR (p=0.046), OOS 7/9 e bootstrap CAGR low 8.15%, mas segue research-only por MDD/tax/PIT caveats.
- Replicação ETF preservada em `studies/weekly_momentum/ETF_STUDY_REPORT.md`: 43 ETFs no cache; melhor variante replicada (`lb60_k10_SMA100`) CAGR 10.76%, MDD -35.96%, Sharpe 0.665 vs SPY CAGR 10.96%, MDD -55.20%, Sharpe 0.652; walk-forward ETF CAGR 6.41%, MDD -48.64%, Sharpe 0.459 vs SPY Sharpe 0.619. Conclusão: sinal stock não migra bem para ETFs sem redesenho.
- Outputs padronizados em `results/{variation}/{config_slug}/` com CSV/JSON, benchmark SPY, plots e `report.md` determinístico conforme `REPORT_SPEC.md`.
- Usa cache Tiingo (`asset_class=equity|etf`) e disclosure obrigatório de survivorship bias enquanto não houver universo point-in-time.

### studies/qld_nasdaq_ath_gate/ 🌱 QUICK DIAGNOSTIC
- Novo estudo rápido para regra QQQ/QLD: risco em `QQQSIM?L=2` quando `QQQSIM` fecha acima de `85%` do high-watermark das últimas `46` semanas; caso contrário `CASHX`.
- Dados testfol.io long-history para `QQQSIM`, alavancagens via sintaxe `?L` (`QQQSIM?L=2`→`QLDSIM`, `QQQSIM?L=3`→`TQQQSIM`) e `CASHX`; sinal semanal aplicado no próximo pregão para evitar same-close look-ahead.
- Run `results/default/` (1986-11-14..2026-04-17): CAGR 23.42%, MDD -63.67%, Sharpe 0.744 vs QQQSIM CAGR 14.66%, QQQSIM?L=2 CAGR 17.44% e QQQSIM?L=3 CAGR 12.28%.
- Report/plots: `studies/qld_nasdaq_ath_gate/results/default/report.md`, incluindo equity, drawdown, signal line, rolling Sharpe e rolling windows 1/3/5/10y.

### studies/bestfolio_meta_wf_hunt/ 🛑 CLOSED 2026-04-29
- iter 001 dead-end: walk-forward solver sobre sleeves gate-screened com Sharpe density tight = noise (turnover 177-222%/ano sem edge).
- Lesson preservada (anti-pattern documentado).

### studies/_shared/ 🔒 CRITICAL INFRA
- `tax_engine.py` (espelho byte-identical de `global_factor_tilt_loop/tax_engine_v2.py`). AnnualDarfEngine canônico Lei 14.754. Não tocar.

### studies/_archive/ 📦 PRESERVED
- strategy_hunt_loop (78 iters, 1 strict winner iter 079); gold_swing_loop (25 iters, 0 winner, structural ceiling); ema_sma_threshold (Phase 1 legacy).

---

## Engine status (pós-2026-04-22)

| Componente | Status | Ref |
|---|---|---|
| `src/market_lab/backtest/strategies/plano_a_leveraged_rotation.py` | ✅ HONEST (fix 7b90a8f) | `tests/test_plano_a_lookahead_bias.py` |
| `letf_rotation.py` | ✅ NEVER HAD BUG | F1 audit |
| Cross-lib validation (bt/vectorbt/backtrader/numpy) | ✅ 1e-6 concordance | `studies/_archive/phase_3_5f/reports/v2_l2_gayed_redo/cross_lib_report.md` |
| Pytest baseline | ✅ **969 collected** (updated 2026-05-08 T5 expansion) | — |

---

## Regras invioláveis (lembrete operacional)

Sumário do mandate (`docs/investment-mandate.md` é canônico):

1. **Capital:** 100% Plano C; A/B/D = 0% DORMANT.
2. **CAGR/MDD = tiers warning-only** (mandate §2.2/§2.3 desde 2026-04-22).
3. **Plano A reativação:** multi-asset + sweep leverage + staging USD 500-1k → 5-10k.
4. **Plano B reativação:** Inter Internacional + Gayed-anchored + CPCV/PBO/15% DARF.
4b. **Plano D reativação:** literatura/regime novos exigidos.
5. **Gates hard-block (zero bypass):** PBO<0.5, DSR p<0.05, WF≥6/8, single-block OOS, FWD stress, bootstrap 99.9% CI low > 0, cross-lib ±3pp CAGR.
6. **Threading model live (Phase 4)** pausado.
7. **Dynamic sizing preservado.**

**Citação obrigatória** em toda decisão: `[book.slug, p.X]`. 33 livros em `books/summaries/`, skill em `knowledge/SKILL.md`.

---

## Referências cruzadas

- **Mandate canônico:** `docs/investment-mandate.md`
- **Setup + arquitetura:** `README.md`
- **Cleanup playbook:** `docs/CLEANUP.md`; logs forenses `docs/CLEANUP_2026-04-24_LOG.md` + `docs/CLEANUP_2026-05-05_LOG.md`
- **Histórico público:** `docs/PROJECT_HISTORY.md`
- **Knowledge base:** `books/MAPPING.md` + `knowledge/SKILL.md`
- **Convenções:** `CLAUDE.md`

---

## Changelog

- **2026-05-09:** `studies/letf_rotation_hunt/` ganhou suplemento QQQ/NDX para responder benchmark criticism: top-20 original reavaliado contra `QQQSIM`, sem reotimização; winner T3d sma250/100 permanece #1 por robustez composta vs QQQ.
- **2026-05-09:** `studies/letf_rotation_hunt/` ganhou loop pós-fechamento isolado em `loop_iterations/`, com state próprio, limite de 50 iters, critério `beats_winner` congelado e trial accounting global para DSR.
- **2026-05-09:** `studies/weekly_momentum/` bootstrapped for weekly cross-sectional momentum over cached Tiingo stocks/ETFs, then adjusted to an honest daily-bar timing model and standardized report bundle: Thursday signal, Friday sale, Monday/Tuesday buy via `settlement_delay_days`, outputs under `results/{variation}/{config_slug}/`.
- **2026-05-09:** `studies/weekly_momentum/` added controlled stock sweeps and walk-forward diagnostics over 200 configs per universe. S&P 500 WF: CAGR 42.30%, MDD -50.84%, Sharpe 1.216; full stock cache WF: CAGR 61.83%, MDD -60.52%, Sharpe 1.200. Verdict remains research-only pending PIT universe, costs and PBO/DSR/bootstrap.
- **2026-05-09:** `studies/weekly_momentum/` froze 4 deploy candidates and generated a comparable validation panel under `deploy_candidates/`; candidates remain research-only pending operational/statistical hard gates.
- **2026-05-09:** `studies/weekly_momentum/` added proxy transaction-cost, annual DARF and ADV20 liquidity stress to the deploy-candidate panel. Gross edge survives transaction-cost stress, but tax drag materially reduces fixed-candidate attractiveness.
- **2026-05-09:** `studies/weekly_momentum/` added required candidate plots plus first anti-overfit gate pass (PBO/DSR/OOS/bootstrap). Only `fixed_aggressive_sp500` passes this first statistical screen, still research-only.
- **2026-05-09:** `studies/qld_nasdaq_ath_gate/` added as a quick diagnostic for QQQ 46-week high-watermark threshold gating into QLD/CASHX, then migrated to long-history testfol.io `QQQSIM` with `?L` leverage aliases (`QQQSIM?L=2/3`) and regenerated `results/default/`.
- **2026-05-08:** T5 expansion of `letf_rotation_hunt` completed (post-close methodology amendment). 20 new configs added (iters 022-025); DSR cumulative re-computed at N=426; KILL T5-expansion FIRES (best Sortino 1.1399 < 1.272); Track A winner confirmed. Pytest baseline updated to 969. §17 disclosure in STUDY_FINAL_REPORT.md. `studies/letf_rotation_hunt/` entry added to state.
- **2026-05-05:** refresh total. MAINTENANCE MODE consolidado; status de studies/ atualizado (myfxbook CLOSED 2026-05-04, spy_beater B4 deploy-ready, long_term_portfolio BLOCKED, factor_tilt FROZEN, day_swing bootstrap). Pytest baseline 813.
- **2026-04-23:** rewrite total após Phase 3.5f fechar sem winner. Plano A V2 encerrado; Plano B c06-c12 pausado.
- **2026-04-19:** versão inicial.
