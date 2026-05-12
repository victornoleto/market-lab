# Estado atual — market-lab (2026-05-12)

> **Propósito:** onboard rápido para humanos e agentes. Este doc é o
> snapshot vivo — a verdade canônica vive nos arquivos referenciados.

---

## TL;DR (2026-05-12)

🛑 **MAINTENANCE MODE** desde 2026-04-23 (mandate §1, §7).

- **Capital:** 100% **Plano C** passivo factor-tilted. Documentação pessoal movida para `victor-ia/verticals/investments/`.
- **Strategies A/B/D:** **DORMANT** (0% capital, infra retida).
- **113/113 honest FAIL** acumulado entre 2026-04-08 e 2026-04-23 (Phase 3.5f-3.8 + D-MVP + E-MVP). Pattern previsto por López de Prado DSR + Aronson 6402-rule + Li-Ferreira 2025 Network Momentum.
- **Sem hunt ativo;** revisão consolidada do mandato em 6-12 meses.

Ver `docs/investment-mandate.md` para regras canônicas, e `docs/CLEANUP_2026-04-24_LOG.md` + `docs/CLEANUP_2026-05-05_LOG.md` para audit trail dos cleanups.

---

## Status por linha de pesquisa (2026-05-11)

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

## Linhas exploratórias em studies/ (2026-05-11)

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
- **Closed study:** 26 iters (iters 000-025); study winner: **`qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`** (T3d K=2, Sortino lh_56y 1.3246, Sharpe 0.9191). DSR PASS at N=426 (p_v2=0.0024).
- **2026-05-08 — T5 expansion** (post-close methodology amendment): 20 new configs across iters 022-025 (T5a σ-sweep, T5b carry, T5c-grid, T5d HRP/ERC). DSR cumulative re-computed for all ~426 configs; 22 early-tier T1 configs flipped PASS→FAIL (none are winners). KILL T5-expansion: **FIRES** (best Sortino 1.1399 < threshold 1.272); T3d K=2 remains canonical winner.
- **2026-05-09 — QQQ/NDX benchmark supplement:** Reddit-methodology check re-ran original top-20 strategy universe vs `QQQSIM` instead of SPY. Operative winner remains #1 by composite rolling robustness vs QQQ, with full-history end ratio **224.31× QQQ**, `pct_above_qqq=100.0%`, and average rolling end-ratio win rate **95.8%**. Worst relative windows concentrate in 3y/5y NDX bull-recovery regimes. Report: `studies/letf_rotation_hunt/reports/STUDY_QQQ_BENCHMARK_REPORT.md`.
- **2026-05-09 — post-close loop scaffold:** autonomous research loop added under `studies/letf_rotation_hunt/{loop.sh,LOOP_PROMPT.md,LOOP_MEMORY.md,LOOP_PROTOCOL.md}`. It writes only to `runs/post_close/`, benchmarks against the frozen T3d-K2 Sortino 1.3246 winner, uses global DSR trial accounting from N=426, and never triggers capital reallocation; mandate §1 remains unchanged `[advances_fin_ml, p.222-223]`.
- **2026-05-09 — loop 001-010 report:** post-close loop found research beaters in iters 009-010. Best is iter 010 `graded-master-bridge` (Sortino_lh56y 1.4670, edge +0.1424 vs T3d-K2, PBO 0.393, score 81.5 STRONG). Report/plots: `studies/letf_rotation_hunt/runs/post_close/LOOP_10_ITER_REPORT.md`. Not deploy-authorized; score < 90 and mandate §1 remains 100% Plano C `[advances_fin_ml, p.222-223]`.
- **2026-05-10 — Phase 3 performance-first loop 011-020:** user-directed focus shifted from Sortino-only safety to CAGR/equity performance vs T3d-K2. Phase 3 found strict-supersets: iter 012 first, iter 017 first novel non-replica. Best balanced candidate is iter 017 `postcrash-rearm-tqqq-streak` (CAGR 32.66%, Sortino 1.4030, terminal equity 1.61× T3d-K2, PBO 0.440). Highest CAGR is iter 011 (36.69%, terminal 5.39×, but lower Sortino 1.227). Report/plots: `studies/letf_rotation_hunt/runs/post_close/LOOP_PHASE3_011_020_REPORT.md`. Not deploy-authorized; mandate §1 unchanged `[advances_fin_ml, p.208-211]`.
- **2026-05-10 — Phase 4 focused loop 021-030:** iter 017's post-crash rearm family was validated/refined. The post-close research winner is now iter 030 **`qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120`** (T35D60 + LRS1.20): Sortino 1.3839, CAGR 36.68%, terminal equity ~5.4× T3d-K2, PBO 0.0357, score 79.5 STRONG. It remains research-only: score <90 and mandate §1 keeps capital 100% Plano C `[leverage_for_the_long_run, ch.4-5, p.40-60]`, `[advances_fin_ml, p.222-223]`. Report/plots: `studies/letf_rotation_hunt/reports/POST_CLOSE_LOOP_REPORT.md`.
- **2026-05-10 — Iter 031 no-margin/tax diagnostic:** fair tax panel added executable proxy `ON normal=100% QLD`, `turbo=80% TQQQ + 20% CASHX`, `OFF=100% ZROZ` plus annual 15% tax on realized net gains (Lei 14.754 semantics), and also taxes T3d-K2 state changes. T3d-K2 annual-tax: CAGR 24.24%, Sortino 1.0826. Proxy state-change annual-tax: CAGR 25.05%, Sortino 1.0966, terminal 1.299× taxed T3d-K2, 378 sale events. SPY/NDX buy-hold static no-tax: CAGR 11.47% / 14.59%. Verdict: proxy beats taxed T3d-K2 modestly, but is not deploy-equivalent to iter 030 gross (36.68%, Sortino 1.3839); no-margin route requires redesign/validation before any monitoring app `[leverage_for_the_long_run, ch.4-5, p.40-60]`.
- **2026-05-10 — Iter 032 taxed underlying/risk-on variants:** tested T3d-K2 annual-tax variants with risk-on `TQQQ`, `SPY/SSO`, and `SPY/UPRO`, plus plots of equity, benchmark-relative equity, and rolling windows. Best CAGR is `t3d_k2_tqqq_taxed`: CAGR 27.88%, Sortino 1.0279, MDD -70.74%, terminal 3.194× taxed T3d-K2. Best Sortino among dynamic variants remains iter 30 proxy tax-aware: CAGR 25.05%, Sortino 1.0966, MDD -59.29%, terminal 1.299× taxed T3d-K2. SPY/SSO and SPY/UPRO variants underperform static NDX/QQQ and taxed T3d-K2. Report: `studies/letf_rotation_hunt/runs/post_close/032-2026-05-10-taxed-underlying-riskon-variants/REPORT.md` `[leverage_for_the_long_run, ch.4-5, p.40-60]`.
- **2026-05-10 — T3d-K2 tax-aware consolidation:** readable conclusion added at `studies/letf_rotation_hunt/reports/T3D_K2_TAX_AWARE_CONCLUSION.md`. Operational ranking: simple baseline = T3d-K2 annual-tax; balanced upgrade = iter 30 proxy annual-tax; performance-first challenger = T3d-K2 with TQQQ annual-tax; rejected = SPY/SSO and SPY/UPRO transplants. This is a research reference only and does not override mandate §1 `[leverage_for_the_long_run, ch.4-5, p.40-60]`, `[advances_fin_ml, p.222-223]`.
- **2026-05-11 — LRS baseline comparison vs T3d-K2 / iter030:** head-to-head report compares the closed-study anchor (t3d-k2) and post-close winner (iter030) against four naive Gayed LRS variants (SMA200 → SSO/UPRO/QLD/TQQQ, FFR cash off-leg) plus SPY/NDX buy-and-hold over 1986–2026 gross. **iter030 decisively dominates every naive LRS** on Sortino (1.38 vs best LRS 0.98), Sharpe (0.96 vs 0.71), CAGR (36.7% vs 22.5%), and Calmar (0.66 vs 0.30), with worst-case 15y rolling CAGR 21.2% vs 1.4%. The naive SMA200 LRS adds only ~3pp CAGR over SPY buy-hold at the 2× level — modest, not spectacular. Higher LRS leverage *reduces* risk-adjusted return: Sharpe drops from SSO 2× (0.71) to TQQQ 3× (0.65) while MDD plumbs −94.2%. **v1 of this report (same day) had inverted findings due to a 1-day signal lookahead in the new runner**; bug caught via user-supplied testfol.io cross-check (SPY→SSO LRS: testfol.io CAGR 15.70% / MDD −51.67% vs corrected runner 15.04% / −50.57%, Δ ≤ 1pp) and fixed via `regime.shift(1)`. The published t3d-k2 / iter030 numbers are unaffected (their `backtest.py` already lags signals). The reference `src/market_lab/backtest/strategies/letf_rotation.py::simulate_letf_rotation` carries the same lookahead and needs a follow-up patch + re-validation of any T1/T2/T3 result that depends on it. Mandate §1 unchanged. Report: `studies/letf_rotation_hunt/reports/LRS_BASELINE_COMPARISON.md` (runner: `studies/letf_rotation_hunt/runners/run_lrs_baseline_comparison.py`) `[leverage_for_the_long_run, p.13, p.16, p.21]`.
- Spec: `docs/specs/2026-05-08-t5-expansion-design.md`; §17 disclosure in `STUDY_FINAL_REPORT.md`.
- Refs: `studies/letf_rotation_hunt/reports/{STUDY_FINAL_REPORT,POST_CLOSE_LOOP_REPORT,T3D_K2_TAX_AWARE_CONCLUSION,STUDY_QQQ_BENCHMARK_REPORT,SORTINO_REANALYSIS_REPORT,TIER_5_REPORT,LRS_BASELINE_COMPARISON}.md`.

### studies/day_swing_strategy_hunt/ 🌱 BOOTSTRAP
- Sem iter ainda. Docs/protocol prontos. Pode resumir a qualquer momento.

### studies/weekly_momentum/ 🛑 CLOSED 2026-05-10
- Veredito final: nenhum deploy. `studies/weekly_momentum/FINAL_REPORT.md` consolida a evolução por fase, plots finais contra SPY e rejeição após Tiingo backfill, PIT expandido, Phase 5 ADV5M e gates DSR/PBO/bootstrap `[advances_fin_ml, p.208-211]`.
- Melhor lead S&P 500 pós-Phase 4: `lb80/k5/SMA250` com CAGR 19.36%, MDD -37.77%, Sharpe 0.817 vs SPY Sharpe 0.884; falha DSR (p=0.418) e bootstrap low CAGR (-2.10%).
- Melhor branch all-stocks ADV5M pós-Phase 5c: CAGR 48.09%, MDD -36.26%, Sharpe 1.184, mas falha PBO (0.579) e bootstrap low (-3.11%); otimizações locais melhoraram PBO apenas sacrificando DSR/bootstrap/performance.
- 2026-05-12 post-close ETF focus: runner `scripts/etf_focus_evolution.py` testou rotação ETF-specific (`lb80/100/126`, `k=10/20`, `SMA200/250`, defensivos `cash/IEF/ZROZ`). Universo completo WF melhorou para CAGR 11.29%, MDD -26.03%, Sharpe 0.712 vs SPY Sharpe 0.619, com PBO 0.313 e bootstrap low +0.06%, mas falha DSR (`p=0.152`). Sem ETFs alavancados/inversos cai para CAGR 6.65%, Sharpe 0.647 e falha DSR/bootstrap. Branch encerrada: research-only, dependente de alavancados, sem novos sweeps locais sem hipótese nova `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.
- Estrutura limpa em 2026-05-10: relatórios em `studies/weekly_momentum/reports/`, evidências pequenas em `evidence/`, plots finais em `plots/final/` e comparação Phase 5 ADV5M em `plots/phase5/`; bulk generated artifacts removidos (~437 MB → ~3.3 MB).
- Código importável preservado na raiz (`core.py`, `data.py`, `reporting.py`); runners/análises em `scripts/`; `REPORT_SPEC.md` preservado. Novos bundles gerados continuam fora do registro canônico final.

### studies/qld_nasdaq_ath_gate/ 🌱 QUICK DIAGNOSTIC
- Novo estudo rápido para regra QQQ/QLD: risco em `QQQSIM?L=2` quando `QQQSIM` fecha acima de `85%` do high-watermark das últimas `46` semanas; caso contrário `CASHX`.
- Dados testfol.io long-history para `QQQSIM`, alavancagens via sintaxe `?L` (`QQQSIM?L=2`→`QLDSIM`, `QQQSIM?L=3`→`TQQQSIM`) e `CASHX`; sinal semanal aplicado no próximo pregão para evitar same-close look-ahead.
- Run `results/default/` (1986-11-14..2026-04-17): CAGR 23.42%, MDD -63.67%, Sharpe 0.744 vs QQQSIM CAGR 14.66%, QQQSIM?L=2 CAGR 17.44% e QQQSIM?L=3 CAGR 12.28%.
- Report/plots: `studies/qld_nasdaq_ath_gate/results/default/report.md`, incluindo equity, drawdown, signal line, rolling Sharpe e rolling windows 1/3/5/10y.

### studies/technical_signal_vote_hunt/ 🛑 STAGE 1 HONEST FAIL
- Novo estudo para generalizar a T3d-K2 em grids `n` sinais / `k` votos, com branches nativas SPY→SSO/UPRO e QQQ→QLD/TQQQ.
- Stage 1 close-only usa testfolio long-history e sinais baseados em preço; runners em `runners/run_stage1_close_only.py` e `runners/run_stage1_close_only_fast.py` geram rankings, benchmarks nativos e importância de indicadores.
- Run exploratório inicial lento `max_n=2` gerou 4.356 configs em `results/stage1_close_only/`.
- Runner NumPy rápido validado em 2026-05-11: `max_n=5` gerou **5.471.268 configs** em `results/stage1_close_only_fast/`; top preliminar QQQ→QLD usa `n=5/k=4` com `EMA200 + EMA250 + MACD + ROC20 + ROC60` (Sortino 1.3375, CAGR 30.21%). Busca exata `n=1..33` é inviável (**566.9 bilhões** de configs antes de gates).
- GA runner adicionado em `runners/run_stage1_ga.py` para busca ampla monitorável por geração; smoke `QQQ→QLD`, population 24 × 5 generations passou e escreveu `results/stage1_ga/QQQ_QLD_2x_seed7/`.
- Stage 1 deep-dive report adicionado em `reports/stage1_top_strategies/`: seleciona top-3 por branch/risk-on do grid `max_n=5`, gera plots de equity, relative equity, drawdown, rolling CAGR e rolling Sortino. Top QQQ→QLD `n=5/k=4` (`EMA200 + EMA250 + MACD + ROC20 + ROC60`) tem Sortino 1.3375 / CAGR 30.21% vs iter030-like QQQ→QLD Sortino 1.0581 / CAGR 27.64%.
- Stage 1 validation completa (12 candidatos, bootstrap 2.000, DSR `n_trials=5.471.268`) fechou **0/12 pass**: todos passaram OOS/FWD/WF/bootstrap, mas todos falharam DSR (`p=0.1890..0.4631`, gate `<0.05`) e PBO diagnóstico do painel top-k (`0.8095..0.9921`, gate `<0.5`). Veredito: leads econômicos in-sample, nenhum winner honesto `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`. Report: `studies/technical_signal_vote_hunt/reports/stage1_validation/REPORT.md`.
- Pós-validação, GA QQQ→QLD seed43 (1.024.000 avaliações) encontrou incumbent in-sample mais forte `n=7/k=5` (`SMA10 + SMA20 + EMA100 + EMA200 + EMA250 + ROC20 + ROC60`): Sortino 1.3776 / CAGR 32.79% / MDD -56.38%. Local-search exato de 1 edição (`216` subsets, `1.531` configs) confirmou que a base vence todos drops/adds/swaps por fitness; isso é apenas discovery e exige nova validação com trial accounting acumulado. Report: `studies/technical_signal_vote_hunt/results/stage1_local_search/QQQ_QLD_2x_ZROZSIM_local/REPORT.md` `[advances_fin_ml, p.222-223]`.
- Pós-GA/local-search validation dos 2 incumbents QQQ (`QQQ→QLD n=7/k=5` e `QQQ→TQQQ n=8/k=6`) com DSR `n_trials=7.554.054` também fechou **0/2 pass**: ambos passaram OOS/FWD/WF/bootstrap e PBO diagnóstico de painel branch (`0.2302`), mas falharam DSR (`p=0.1444` e `0.2260`, gate `<0.05`). Report: `studies/technical_signal_vote_hunt/reports/stage1_ga_local_validation/REPORT.md` `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.222-223]`.
- Stage 2 Tiingo OHLC implementado em `runners/run_stage2_tiingo_ohlc.py`: usa Tiingo real-inception, ajusta OHLC via `adj_close/close`, e testa replay + neighborhood OHLC de uma edição. Primeiro diagnóstico QQQ: `QQQ→QLD + ZROZ` replay caiu para Sortino 1.2775 / CAGR 26.31%; melhor OHLC local `+atr14_pct_lt_3` ficou só marginalmente melhor. `QQQ→TQQQ + ZROZ` replay ficou Sortino 1.2337 / CAGR 34.75%; melhor OHLC local `-roc120_gt_0+atr14_pct_lt_3` subiu para Sortino 1.3307 / CAGR 38.77% / MDD -62.06%. Ainda é discovery local, não validação honesta; precisa runner Stage 2 de WF/OOS/FWD/bootstrap/PBO/DSR antes de qualquer claim `[quant_trading_chan, p.37]`, `[trading_systems_methods, p.732-733]`, `[advances_fin_ml, p.208-211]`.
- Overnight Stage 2 exact grids revisados em `reports/stage2_grid_overnight/REPORT.md`: 115.029.492 configs persistidos (`QQQ+ZROZ n<=5`, `QQQ+BIL n<=5`, `SPY+ZROZ n<=5`, `QQQ→TQQQ+ZROZ n=6`). Top QQQ→TQQQ+ZROZ `n=5/k=2` marcou CAGR 62.19% / Sortino 1.6280 / MDD -62.37%; top QQQ→QLD+ZROZ CAGR 40.94%; top SPY→UPRO+ZROZ CAGR 50.07%. Recomputação pandas independente reproduziu CAGR/MDD, sem bug imediato de cálculo ou same-close lookahead identificado. Porém extra lag derruba QQQ→TQQQ+ZROZ para ~15% CAGR, e o trial count acumulado mínimo já é >=122.583.546; veredito continua discovery-only, suspect-by-default, aguardando validação Stage 2 `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.222-223]`.
- Stage 2 grid operacional atualizado em 2026-05-12: runner agora suporta `CASH_USD`, `--extra-lag-days` e exclusão default de sinais redundantes dentro da mesma config (MACD equivalente e thresholds nested). Grids QQQ `CASH_USD + extra_lag_days=1 + n<=5` completos: `QQQ→TQQQ` testou 7.067.694 configs e topou `n=5/k=3` com Sortino 1.4124 / CAGR 53.00% / MDD -51.03%; `QQQ→QLD` testou 7.067.694 configs e topou `n=5/k=2` com Sortino 1.3181 / CAGR 34.54% / MDD -53.09%. Estimativas QQQ QLD+TQQQ deduped: `n<=6` 115.350.684, `n<=7` 761.622.940, `n<=8` 4.183.106.396; exact `n<=7/8` não é rotina, GA/beam search é o caminho prático. PSR pode entrar como diagnóstico, mas DSR segue hard gate pelo mandate `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.222-223]`.
- Stage 2 window audit: a comparação QQQ→TQQQ vs QQQ→QLD era contaminada por janela (`QLD` incluía 2008; `TQQQ` começa em 2010). Re-rodando QLD desde 2010-02-12, o top vira a mesma regra do TQQQ (`sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70`, `k=3`) com Sortino 1.4209 / CAGR 36.26% / MDD -37.54%; TQQQ na mesma regra fica Sortino 1.4124 / CAGR 53.00% / MDD -51.03%. Testfolio 1986+ é possível apenas para essa regra close-only e enfraquece o resultado: `QLDSIM+CASHX` CAGR 17.06% / MDD -76.73%, `TQQQSIM+CASHX` CAGR 18.90% / MDD -93.95%. Report: `studies/technical_signal_vote_hunt/reports/stage2_window_and_testfolio_audit/REPORT.md` `[advances_fin_ml, p.208-211]`.

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

- **2026-05-12:** `studies/weekly_momentum/` ganhou e encerrou evolução ETF-specific pós-fechamento. `focused_full_universe` melhorou o WF para CAGR 11.29% / Sharpe 0.712 vs SPY 10.63% / 0.619, mas falha DSR (`p=0.152`); `focused_no_leveraged` caiu para CAGR 6.65% e falha DSR/bootstrap. Conclusão: lead diagnóstico dependente de alavancados, sem autorização de deploy e sem novos sweeps locais sem hipótese nova `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.
- **2026-05-12:** `studies/technical_signal_vote_hunt/` adicionou Stage 2 operacional com `CASH_USD`, `extra_lag_days` e dedupe de sinais redundantes; QQQ `n<=5` cash+lag1 completo para TQQQ/QLD gerou leads discovery-only, e estimativas mostram `n<=7/8` exato grande demais para rotina.
- **2026-05-12:** added `docs/plans/2026-05-12-ai-etf-exit-monitoring.md`, an educational operational plan for monitoring a tactical AI/semis ETF sleeve (`DRAM`, `SMH`, `AIS`, `SOXL`, `TQQQ`, `POW`) with yellow/red exits, profit-taking, allocation critique and a proposed Python monitor. This does not override maintenance mode or mandate §1.
- **2026-05-09:** `studies/letf_rotation_hunt/` ganhou suplemento QQQ/NDX para responder benchmark criticism: top-20 original reavaliado contra `QQQSIM`, sem reotimização; winner T3d sma250/100 permanece #1 por robustez composta vs QQQ.
- **2026-05-09:** `studies/letf_rotation_hunt/` ganhou loop pós-fechamento isolado em `runs/post_close/`, com state próprio, limite de 50 iters, critério `beats_winner` congelado e trial accounting global para DSR.
- **2026-05-09:** `studies/letf_rotation_hunt/` consolidou relatório loop 001-010. Iters 009-010 bateram o winner T3d-K2 pelo critério congelado; iter 010 é o melhor research beater (Sortino 1.4670, score 81.5), sem autorização de deploy.
- **2026-05-10:** `studies/letf_rotation_hunt/` rodou Phase 3 performance-first (iters 011-020). Iter 012 foi o primeiro strict-superset CAGR+Sortino; iter 017 virou melhor research incumbent balanceado (CAGR 32.66%, Sortino 1.4030, terminal 1.61× T3d-K2), ainda sem deploy.
- **2026-05-10:** `studies/letf_rotation_hunt/` concluiu Phase 4 focused loop (iters 021-030). Iter 030 `T35D60 + LRS1.20` virou novo research winner pós-fechamento (Sortino 1.3839, CAGR 36.68%, terminal ~5.4× T3d-K2, PBO 0.0357), documentado em `reports/POST_CLOSE_LOOP_REPORT.md`; segue sem deploy por score <90 e mandate §1.
- **2026-05-10:** `studies/letf_rotation_hunt/` adicionou iter 031 para testar proxy sem margem `80% TQQQ + 20% CASHX` com tributação anual de 15% sobre lucro líquido realizado, comparando também T3d-K2 taxada e SPY/NDX buy-hold sem venda. Proxy annual-tax bate T3d-K2 taxada modestamente (25.05% vs 24.24% CAGR; terminal 1.299×), mas fica muito abaixo da iter 030 gross; veredito continua sem deploy.
- **2026-05-10:** `studies/letf_rotation_hunt/` adicionou iter 032 para comparar variantes tax-aware de underlying/risk-on. T3d-K2 com TQQQ melhora CAGR/terminal (27.88%, 3.194× taxed T3d-K2), mas com Sortino menor e MDD -70.74%; SPY/SSO e SPY/UPRO não competem.
- **2026-05-10:** `studies/letf_rotation_hunt/` consolidou a conclusão tax-aware da T3d-K2 em `reports/T3D_K2_TAX_AWARE_CONCLUSION.md`, separando ranking operacional simples/balanceado/performance-first/rejeitado sem mudar o mandate.
- **2026-05-09:** `studies/weekly_momentum/` bootstrapped for weekly cross-sectional momentum over cached Tiingo stocks/ETFs, then adjusted to an honest daily-bar timing model and standardized report bundle: Thursday signal, Friday sale, Monday/Tuesday buy via `settlement_delay_days`, outputs under `results/{variation}/{config_slug}/`.
- **2026-05-09:** `studies/weekly_momentum/` added controlled stock sweeps and walk-forward diagnostics over 200 configs per universe. S&P 500 WF: CAGR 42.30%, MDD -50.84%, Sharpe 1.216; full stock cache WF: CAGR 61.83%, MDD -60.52%, Sharpe 1.200. Verdict remains research-only pending PIT universe, costs and PBO/DSR/bootstrap.
- **2026-05-09:** `studies/weekly_momentum/` froze 4 deploy candidates and generated a comparable validation panel under `deploy_candidates/`; candidates remain research-only pending operational/statistical hard gates.
- **2026-05-09:** `studies/weekly_momentum/` added proxy transaction-cost, annual DARF and ADV20 liquidity stress to the deploy-candidate panel. Gross edge survives transaction-cost stress, but tax drag materially reduces fixed-candidate attractiveness.
- **2026-05-09:** `studies/weekly_momentum/` added required candidate plots plus first anti-overfit gate pass (PBO/DSR/OOS/bootstrap). Only `fixed_aggressive_sp500` passes this first statistical screen, still research-only.
- **2026-05-09:** `studies/weekly_momentum/` Phase 2 ran the fixed-aggressive neighborhood and filtered all-stocks exploratory WF. Fixed neighborhood is robust enough to continue; all-stocks remains exploratory after PBO/DSR failures.
- **2026-05-10:** `studies/weekly_momentum/` Phase 3 added approximate PIT S&P membership. Original fixed-aggressive lead weakened materially; `lb80_k5_sma200/sma250` remain the only worthwhile leads, still research-only.
- **2026-05-10:** `studies/weekly_momentum/` consolidated `STRATEGY_TESTED_SUMMARY.md` with all tested families, top-6 strategy comparison versus SPY and final non-deploy verdict.
- **2026-05-10:** `studies/weekly_momentum/` completed Phase 4 Tiingo survivorship audit/backfill and expanded-cache PIT rerun. Coverage improved, but `lb80/k5/SMA200-250` failed DSR/bootstrap and lost risk-adjusted appeal versus SPY; family stopped.
- **2026-05-10:** `studies/weekly_momentum/` added Phase 5 dynamic all-stocks WF branch with PIT tradability filters and SPMO/FMTM benchmarks. ADV5M is economically strong but fails PBO/bootstrap; branch remains research-only.
- **2026-05-10:** `studies/weekly_momentum/` finalized cleanup after closure: canonical reports moved to `reports/`, decision evidence to `evidence/`, final plots to `plots/final/`, and regenerable bulk outputs removed.
- **2026-05-09:** `studies/qld_nasdaq_ath_gate/` added as a quick diagnostic for QQQ 46-week high-watermark threshold gating into QLD/CASHX, then migrated to long-history testfol.io `QQQSIM` with `?L` leverage aliases (`QQQSIM?L=2/3`) and regenerated `results/default/`.
- **2026-05-11:** `studies/technical_signal_vote_hunt/` bootstrapped para buscar combinações `n`/`k` de sinais técnicos em branches SPY e QQQ. Stage 1 close-only gerou runner inicial (`max_n=2`, 4.356 configs), runner NumPy rápido (`max_n=5`, 5.471.268 configs), runner GA monitorável por geração, deep-dive report com plots dos top-3 por branch e validação completa. Veredito Stage 1: **0/12 honest PASS** após DSR global e PBO diagnóstico; Stage 2 Tiingo OHLC ficou especificado para implementação posterior.
- **2026-05-11:** `technical_signal_vote_hunt` adicionou GA longo + local-search QQQ→QLD pós-validação: novo incumbent in-sample `n=7/k=5` melhorou Sortino/MDD e venceu neighborhood exato de 1 edição, mas permanece não validado até nova rodada honesta com trials acumulados.
- **2026-05-08:** T5 expansion of `letf_rotation_hunt` completed (post-close methodology amendment). 20 new configs added (iters 022-025); DSR cumulative re-computed at N=426; KILL T5-expansion FIRES (best Sortino 1.1399 < 1.272); Track A winner confirmed. Pytest baseline updated to 969. §17 disclosure in STUDY_FINAL_REPORT.md. `studies/letf_rotation_hunt/` entry added to state.
- **2026-05-05:** refresh total. MAINTENANCE MODE consolidado; status de studies/ atualizado (myfxbook CLOSED 2026-05-04, spy_beater B4 deploy-ready, long_term_portfolio BLOCKED, factor_tilt FROZEN, day_swing bootstrap). Pytest baseline 813.
- **2026-04-23:** rewrite total após Phase 3.5f fechar sem winner. Plano A V2 encerrado; Plano B c06-c12 pausado.
- **2026-04-19:** versão inicial.
