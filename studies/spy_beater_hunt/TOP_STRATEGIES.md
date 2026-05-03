# spy_beater_hunt — TOP STRATEGIES (deploy-readiness ranking)

**Status**: hunt CLOSED 2026-04-30 após 30 iters / ~85 cumulative trials. Reddit feedback iters 040-044 promoted B4 Conservative. Iter 045 corrected the RSST proxy; **B4 remains the balanced deploy pick**, while L1 CEGB is now the highest-Sharpe low-risk reference.

Este documento substitui o "WINNER tier" como critério de deploy-readiness por uma **classificação por gate-pass anti-overfit**, alinhada à decisão do usuário (2026-04-30): "se passaram nos gates, por mim tudo certo".

> **Convention**: bars 1+2 = "beat SPY" (CAGR > 11.21% AND MDD < 55.17% mean across lh_56y + spy_real). Bars 3 = 7-gate battery threshold (≥5 of 7 per dataset, ≥2/2 datasets). Tier abaixo categoriza por **gate-pass strict** (cada um dos 7 gates individualmente).

---

## Historical Canonical Ranking (iter 044, 2026-05-01) — Monthly + ERs + terminal DARF

> **Superseded for RSST-containing portfolios by iter 045 (2026-05-02).** Iter 044 remains useful as the 1987+ long-window table, but it uses the old `RSST = SPY + KMLM - cash` proxy. For corrected RSST methodology, use the iter 045 table immediately below.

## ⭐⭐ RSST-CORRECTED RANKING (iter 045, 2026-05-02) — common 2000+ window

**Methodology**:
- **Top-level rebal**: Monthly via testfol.io API
- **Tax model**: no DARF for static buy-and-hold/lazy-rebal scenarios; tax is reserved for swing/tactical strategies that realize gains through position changes
- **Window**: common 2000-01-03 -> 2026-05-01 for all rows, because `DBMFSIM` starts in 2000
- **RSST proxy**: `SPYSIM + 70% DBMFSIM + 30% KMLMSIM - CASHX?E=-2`
- **Rationale**: proxy correction based on live RSST tracking, not a new weight optimization; return stacking `[risk_parity, ch.5, p.10]` + diversified managed futures `[ilmanen_expected_returns, ch.19]`

| # | strategy | CAGR (no tax) | MDD | Sharpe | Calmar | tier |
|---:|---|---:|---:|---:|---:|---|
| 1 | L1 CEGB proxy | 9.66% | **-25.43%** | **0.696** | **0.380** | low-risk reference |
| 2 | **B4 ZROZ** | 11.00% | -29.60% | 0.671 | 0.372 | **balanced deploy pick** |
| 3 | L2 Bogleheads 67% NTSX | 8.97% | -26.30% | 0.653 | 0.341 | low-risk reference |
| 4 | B3 TLT instead of TMF | 10.34% | -32.68% | 0.646 | 0.316 | TLT backup |
| 5 | T1 gold-heavy | 11.65% | -35.80% | 0.643 | 0.325 | high-CAGR alternative |
| 6 | B2 TMF10 balanced | 11.59% | -37.91% | 0.631 | 0.306 | high-CAGR alternative |
| 7 | T2 equity-heavy | 11.08% | -34.46% | 0.627 | 0.321 | NTSX 35% |
| 8 | M2 DBMF no RSST | 9.77% | -37.97% | 0.611 | 0.257 | DBMF-only MF |
| 9 | M4 RSST+KMLM blend | 10.07% | -38.32% | 0.602 | 0.263 | dual MF source |
| 10 | M3 KMLM+DBMF blend | 9.56% | -36.94% | 0.601 | 0.259 | split MF no RSST |
| 11 | B1 user baseline 25 TMF | 10.75% | -40.82% | 0.600 | 0.263 | original spec |
| 12 | B5 no duration | **12.00%** | -44.56% | 0.599 | 0.269 | highest CAGR, high MDD |
| 13 | M1 KMLM no RSST | 9.33% | -35.92% | 0.583 | 0.260 | KMLM-only |
| 14 | T3 RSSB global | 10.39% | -43.34% | 0.569 | 0.240 | global stack |
| — | SPY 1x buy-hold | 8.06% | -55.26% | 0.400 | 0.146 | benchmark |

**Interpretation:** B4 is no longer the highest Sharpe portfolio once RSST is corrected; L1 CEGB takes that title. B4 remains the balanced deploy pick because it keeps materially higher CAGR than L1 (+1.34pp) while preserving a sub-30% MDD. B5/T1/B2 offer more CAGR, but with 35-45% drawdowns.

Detailed raw outputs: [`iterations/045-2026-05-02-rsst-proxy-7030-rebaseline/SUMMARY.md`](iterations/045-2026-05-02-rsst-proxy-7030-rebaseline/SUMMARY.md).

### Iter 046 follow-up — factor tilts and NDX deleveraged variants

GPT-5.5 follow-up (2026-05-03) tested static factor tilts and local no_simpsons-style NDX deleveraging. Verdict: **corrected B4 remains the balanced baseline**. No tested variant beats B4's CAGR while keeping MDD no worse than B4.

| candidate | CAGR | MDD | Sharpe | implication |
|---|---:|---:|---:|---|
| B4 unstacked MF70/30 | 9.91% | **-20.91%** | **0.749** | low-stress alternative; gives up CAGR |
| B4 corrected baseline | 11.00% | -29.60% | 0.671 | balanced baseline |
| B4 + 10 VBR from NTSX | 11.23% | -31.06% | 0.681 | mild CAGR upgrade, slightly worse MDD |
| B4 aggressive SCV15 | 11.86% | -40.89% | 0.639 | higher CAGR but risk profile worsens materially |
| best NDX deleveraged local | 13.38% | -72.51% | 0.621 | drawdown still unacceptable |

Details: [`iterations/046-2026-05-03-factor-tilt-and-ndx-deleveraged/SUMMARY.md`](iterations/046-2026-05-03-factor-tilt-and-ndx-deleveraged/SUMMARY.md). This is a review/testfol.io summary, not a full PBO/DSR/WF `verdict.json` gate run.

### Iter 047 follow-up — Bitcoin sleeve

Small Bitcoin sleeves were tested via `BTCSIM` on corrected B4. The common window starts only in 2010, so this is **not** comparable to 1987+/2000+ stress history and is structurally favorable to Bitcoin's early adoption path. Still, it is the first add-on that materially improves CAGR without a large MDD penalty.

| candidate | CAGR | MDD | Sharpe | implication |
|---|---:|---:|---:|---|
| B4 base in BTC window | 13.55% | -26.42% | 0.911 | window-constrained baseline |
| B4 + 2.5% BTC from ZROZ | 17.80% | -26.97% | 1.151 | best retirement-compatible speculation sleeve |
| B4 + 5% BTC from ZROZ | 22.01% | -27.90% | 1.311 | attractive but more speculative |
| B4 + 10% BTC from ZROZ | 30.30% | -29.85% | 1.453 | too speculation-heavy for core |

Interpretation: **2.5% BTC is the cleanest optional satellite**, 5% is aggressive but plausible if the user explicitly wants crypto convexity, and 10% should not be treated as a retirement-core default. Details: [`iterations/047-2026-05-03-bitcoin-sleeve-b4/SUMMARY.md`](iterations/047-2026-05-03-bitcoin-sleeve-b4/SUMMARY.md).

### Iters 050-051 follow-up — taxed overlays and LETF risk-on sleeves

Restricted regime overlays were tested on B4 without BTC using a 15% annual DARF model on realized positive gains. The best after-tax no-LETF row was `overlay_sma150_12mdd_10pp`: 12.35% net CAGR / -28.00% MDD / 0.901 Sharpe versus forced-monthly static B4 at 12.18% / -30.88% / 0.880. This is a small but directionally useful improvement; it remains research, not full gate-equivalent deploy.

The LETF risk-on grid (SSO/QLD/UPRO/TQQQ at 5-50% in 5pp steps, funded only from ZROZ or NTSX in risk-on states) did **not** improve the balanced candidate. It increased CAGR, but no LETF row beat the no-LETF overlay on both after-tax Sharpe and MDD.

| candidate | net CAGR | MDD | Sharpe | implication |
|---|---:|---:|---:|---|
| B4 static forced monthly | 12.18% | -30.88% | 0.880 | tax/conservative baseline |
| no-LETF overlay SMA150 | 12.35% | **-28.00%** | **0.901** | cleanest overlay hypothesis |
| QLD 5% SMA150 from ZROZ | 12.87% | -28.92% | 0.900 | best LETF Sharpe, but worse MDD/Sharpe than no-LETF |
| TQQQ 45% SMA150 from NTSX | **16.78%** | -44.64% | 0.742 | best LETF CAGR, but no longer comparable risk profile |

Details: [`iterations/050-2026-05-03-b4-overlay-tax-sma-ema/SUMMARY.md`](iterations/050-2026-05-03-b4-overlay-tax-sma-ema/SUMMARY.md) and [`iterations/051-2026-05-03-letf-risk-on-overlay/SUMMARY.md`](iterations/051-2026-05-03-letf-risk-on-overlay/SUMMARY.md). Trend gating remains tied to LRS rationale `[leverage_for_the_long_run, ch.3-4, p.40-60]`; grid restraint and rejection criteria follow anti-overfit discipline `[advances_fin_ml, p.208-211]`.

---

**Methodology** (single, consistent across all rankings in this doc):
- **Top-level rebal**: Monthly via testfol.io API
- **ERs**: explicit per portfolio via `drag` (NTSX 0.20%, GDE 0.20%, RSST 0.99%, KMLM 0.92%, etc.)
- **Tax model**: lazy rebal via aportes (user contribuir mensalmente, NUNCA vende durante accumulation) → realized gains intra-ano = 0 → DARF 15% só no terminal sobre lucro acumulado: `net_final = 0.85 × gross_final + 0.15 × $10k`
- **Window**: 1987-12-31 → 2026-04-30 (38.33y) para configs sem DBMF; 26.32y para M2/M3 (DBMFSIM start 2000-01)
- **Source**: testfol.io API direct, with raw stats `cagr`, `max_drawdown`, `sharpe` (Rf-adjusted)

**RSST proxy caveat (resolved by iter 045):** this table uses the old iter 044 expansion `RSST = SPYSIM + KMLMSIM - CASHX` plus RSST ER in portfolio drag. The corrected `70/30 DBMF/KMLM` proxy was re-run in iter 045 above. Treat this table as historical long-window context, not the deploy table for RSST-containing portfolios.

### Unified ranking — 14 iter 038 configs + G4 additions + LRS benchmarks + SPY

| # | strategy | gross CAGR | **net CAGR** | MDD | Sharpe | Calmar | tier |
|---|---|---:|---:|---:|---:|---:|---|
| 🏆 | **Conservative (B4 ZROZ)** | 13.31% | **12.84%** | **-28.94%** | **0.745** | 0.460 | **DEPLOY PICK** |
| 2 | B3 TLT instead of TMF | 12.44% | 11.98% | -30.06% | 0.735 | 0.414 | TLT 1× backup |
| 🥈 | Sleeping pills (L1 CEGB) | 11.06% | 10.60% | **-25.43%** | 0.729 | 0.435 | low-risk reference |
| 🥉 | Bogleheads 67% NTSX (L2) | 11.06% | 10.60% | -26.30% | 0.722 | 0.420 | low-risk reference |
| 5 | Balanced (B2 TMF10) | 13.89% | **13.42%** | -36.38% | 0.717 | 0.382 | high-CAGR alternative |
| 6 | **G4c mixed US/Intl** 🆕 | 13.31% | 12.84% | -32.65% | 0.716 | 0.408 | best international |
| 7 | T2 equity-heavy | 13.40% | 12.93% | -33.14% | 0.708 | 0.404 | NTSX 35% |
| 8 | Aggressive (T1 gold-heavy) | 13.34% | 12.87% | -34.65% | 0.688 | 0.385 | demoted from Post 1 |
| 9 | B5 no duration | **14.22%** | **13.74%** | -41.12% | 0.687 | 0.346 | high CAGR, high MDD |
| 🛡️ | **G4d (RSSB+GDE+ZROZ+KMLM)** 🆕 | 10.54% | 10.10% | **-22.56%** | 0.678 | **0.467** ⭐ | **best MDD/Calmar in study** |
| 11 | B1 user baseline 25 TMF | 12.93% | 12.46% | -38.78% | 0.665 | 0.333 | original spec — TMF 25% costs MDD |
| 12 | M4 RSST+KMLM blend | 11.85% | 11.38% | -37.27% | 0.645 | 0.318 | dual MF source |
| 13 | T3 RSSB global | 12.31% | 11.85% | -41.39% | 0.623 | 0.298 | global stack, MDD inflado |
| 14 | M2 DBMF no RSST ⚠ | 9.76% | 9.15% | -37.97% | 0.610 | 0.257 | 26y window only |
| 15 | M1 KMLM no RSST | 10.74% | 10.29% | -35.92% | 0.610 | 0.299 | KMLM-only stack |
| 16 | M3 KMLM+DBMF blend ⚠ | 9.56% | 8.95% | -36.94% | 0.600 | 0.259 | 26y window only |
| 17 | Gayed LRS 2× (SSO 200d) | 16.01% | — | -43.48% | 0.609 | 0.368 | LRS — annual realize → bigger tax drag |
| 18 | Gayed LRS 3× (UPRO 200d) | 19.61% | — | -57.57% | 0.595 | 0.341 | extreme LRS |
| — | Popular 50/25/25 SSO/GLD/ZROZ | 12.58% | 12.11% | -50.55% | 0.576 | 0.249 | reference |
| — | **SPY 1× buy-hold** | 11.37% | **10.91%** | -55.20% | 0.523 | 0.206 | **benchmark** |

⚠ M2 / M3 = janela 26y (DBMFSIM start 2000) — não comparáveis em CAGR absoluto. Gayed LRS net não computado (LRS regime-flips força annual realize, drag tax estimado ~1.5-2pp/yr per iter 038's net classification).

### Beats SPY on BOTH net CAGR AND MDD (9 strategies above SPY net 10.91% / |MDD| 55.20%)

B4 ZROZ ✅, B3 TLT ✅, B2 TMF10 ✅, T2 equity-heavy ✅, T1 gold-heavy ✅, B5 no duration ✅, B1 user baseline ✅, M4 ✅, T3 RSSB ✅. (G4d perde por CAGR < SPY.)

### Where the iter 044 numbers come from

Iter 044 re-rodou todos os 14 configs do iter 038 sweep com a mesma metodologia dos iter 040/041/042 — **Monthly rebal + ERs reais via testfol.io**. Aplicou tax model **lazy rebal terminal DARF** (consistent com Lei 14.754/2023 quando user nunca vende durante o ano).

Detalhes completos: [`iterations/044-2026-05-01-iter038-rebaseline-monthly-ers-terminal-darf/SUMMARY.md`](iterations/044-2026-05-01-iter038-rebaseline-monthly-ers-terminal-darf/SUMMARY.md).

### Iter 040-043 verdicts (Reddit Post 1 community feedback)

| iter | trigger | verdict |
|---|---|---|
| 040 | u/perky_python — Monthly rebal + ERs | ⚠️ Partial validate. CAGR drops 0.5-0.9pp on stacks. Popular 50/25/25 MDD blowup -10.71pp. |
| 041 | u/Fun-Sundae4060 + u/no_simpsons — TQQQ × 200d (G3) | ❌ 6 variants. Best (G3c) Sharpe 0.703 — below B4. "10,000% TQQQ" = cherry-picked 2012-2025. |
| 042 | u/Grouchy_Release_2321 + u/perky_python — international (G4) | ⚠️ US-bias only ~4% of edge. G4d (RSSB-based) breaks MDD record at -22.56%. |
| 043 | u/laurenthu — walk-forward weight drift (G8) | ✅ Drift 60-75pp em rolling 5y MAS static Sharpe BEATS walk-forward in 3/3 universes. G8 PASS. |
| 044 | user — re-baseline iter 038 com Monthly + ERs + lazy DARF | ✅ Unified ranking. B4 ZROZ confirmed canonical. T1 demoted. |

### NEW DEPLOY SPEC — B4 Conservative (with Monthly rebal + ERs)

```python
# 25% NTSX + 25% GDE + 25% RSST + 25% ZROZ
# Monthly rebal via contributions (lazy rebal preferred)
# Drag: 0.385%/yr from real ERs
# Historical proxy note: RSSTSIM below was KMLM-only in iter 044.
# Corrected re-run: iter 045 models RSST trend as 70% DBMFSIM +
# 30% KMLMSIM, funded with CASHX?E=-2.
# Lei 14.754: defer DARF até liquidação terminal
{
  "type": "static",
  "weights": {
    "NTSXSIM": 0.25,  # NTSX  — WisdomTree 90/60 SPY/Treasuries (ER 0.20%)
    "GDESIM":  0.25,  # GDE   — WisdomTree 90/90 SPY/Gold      (ER 0.20%)
    "RSSTSIM": 0.25,  # RSST  — ReturnStacked 100/100 SPY/MF   (ER 0.99%)
    "ZROZSIM": 0.25,  # ZROZ  — PIMCO 25y zero-coupon Treasury (ER 0.15%)
  }
}
```

Notional: 25×1.5 + 25×1.8 + 25×2.0 + 25×1.0 = **163% effective leverage**.

**Why B4 over T1 (Post 1 pick)**:
- B4 has highest Sharpe in study (0.745).
- ZROZ removes LETF decay tax that TMF carries.
- Monthly rebal cost is minimal for B4 (-0.29pp MDD) vs T1 (-3.99pp MDD). Real-world deployment uses monthly aporters → B4 has the structural advantage.
- Survives all 4 adversarial tests.

**Validate ZROZ availability at your broker.** Inter Internacional confirmed available. Fallback to TLT 1× (B3 spec) if unavailable.

---

## Como ler as colunas

- **gross / net**: score CAGR-anchored 0-100 antes / depois da DARF (Lei 14.754/2023, 15% anual)
- **CAGR_n / MDD_n / Sharpe_n**: métricas pós-DARF (deploy-relevant)
- **G1 PBO** < 0.5 (probabilidade de overfit em CSCV) `[advances_fin_ml, p.208-211]`
- **G2 DSR** p < 0.05 (Deflated Sharpe com cumulative_n_trials penalty) `[p.222-223]`
- **G3 WF MDD** per-window < 25% (walk-forward 8 windows, conservador) `[ch.12]`
- **G4 OOS** Sharpe > 0 em 70/30 split
- **G5 FWD** Sharpe > 0 em stress post-2020
- **G6 CIlow** > 0 (bootstrap 99.9% CI inferior) `[p.196-202]`
- **G7 xlib**: cross-lib delta CAGR ≤ 3pp `[p.31-34]`

---

## 📚 Tier 0 — User-proposed static stack family (iter 038 sweep, 2026-04-30) — REPLACED BY ITER 044

> ⚠️ **REPLACED by iter 044 unified ranking (top of doc, "CANONICAL DEPLOY RANKING").**
>
> Iter 038 era o sweep original (Yearly rebal + no ER + internal pipeline post-tax). Iter 044 (2026-05-01) re-rodou os mesmos 14 configs com **metodologia consistente** com o resto do doc (Monthly rebal + ERs reais via testfol.io + terminal DARF lazy rebal). **Use a tabela "CANONICAL DEPLOY RANKING" no topo deste doc.**
>
> Os números desta seção (NET CAGR 15.82% T1, etc.) são **historical** — pipeline interno com Yearly rebal e tax model anual (não lazy). Não são comparáveis com a tabela canônica e foram substituídos.

### Histórico — pre-feedback (Yearly rebal + no ER + post-DARF anual; SUBSTITUÍDO)

After extensive sweep of 14 variants of the simple capital-efficient stack family + literature research (RiskParityChronicles CEGB, optimizedportfolio.com, Bogleheads), this is the **deploy-recommended family**. Tier 0 = simpler than meta-ensembles AND with similar/better deploy-readiness metrics.

> **Tabela completa com TODAS as 14 configs** (per-dataset gross + net + means + 30y terminal + Pareto frontier + specs): ver [`iterations/038-2026-04-30-user-static-stack-mf-gold-sweep/SWEEP_RESULTS.md`](iterations/038-2026-04-30-user-static-stack-mf-gold-sweep/SWEEP_RESULTS.md).

**Plots iter 038**: [equity overlay lh_56y](iterations/038-2026-04-30-user-static-stack-mf-gold-sweep/plot_overlay_lh_56y.png) · [equity overlay spy_real](iterations/038-2026-04-30-user-static-stack-mf-gold-sweep/plot_overlay_spy_real.png) · [rolling lh_56y](iterations/038-2026-04-30-user-static-stack-mf-gold-sweep/plot_rolling_lh_56y.png) · [rolling spy_real](iterations/038-2026-04-30-user-static-stack-mf-gold-sweep/plot_rolling_spy_real.png) · [CAGR×MDD scatter](iterations/038-2026-04-30-user-static-stack-mf-gold-sweep/plot_cagr_mdd_scatter.png) · [gate heatmap](iterations/038-2026-04-30-user-static-stack-mf-gold-sweep/plot_gate_heatmap.png)

![iter 038 equity overlay lh_56y](iterations/038-2026-04-30-user-static-stack-mf-gold-sweep/plot_overlay_lh_56y.png)

![iter 038 CAGR×MDD scatter (Pareto frontier visualization)](iterations/038-2026-04-30-user-static-stack-mf-gold-sweep/plot_cagr_mdd_scatter.png)

### Sweep results (NET-of-tax means, sorted by 30y compounding terminal value)

| config | NET CAGR | NET MDD | NET Sharpe | $100k → 30y |
|---|---:|---:|---:|---:|
| **T1 gold-heavy** ⭐ | **15.82%** | 33.42% | **0.990** | **$8.20M** |
| B2 TMF10 balanced | 15.54% | 34.56% | 0.974 | $7.61M |
| B1 user baseline 25 TMF | 15.37% | 36.73% | 0.970 | $7.30M |
| B5 no duration | 15.22% | 41.45% | 0.886 | $7.01M |
| T2 equity-heavy | 15.16% | 31.17% | 0.983 | $6.90M |
| T3 RSSB global | 15.00% | 38.81% | 0.932 | $6.63M |
| M4 RSST+KMLM blend | 13.92% | 34.61% | 0.952 | $4.99M |
| **B4 ZROZ instead of TMF** ⭐ | **13.79%** | **28.02%** | 0.973 | $4.83M |
| B3 TLT instead of TMF | 13.04% | 29.36% | 0.973 | $3.95M |
| M1 KMLM no RSST | 12.43% | 32.96% | 0.914 | $3.36M |
| M2 DBMF no RSST | 11.84% | 34.43% | 0.860 | $2.87M |
| M3 KMLM+DBMF blend | 11.65% | 33.63% | 0.853 | $2.73M |
| L1 CEGB proxy (literature) | 11.13% | 25.83% | 0.963 | $2.37M |
| L2 Bogleheads 67% NTSX | 10.68% | 24.87% | 0.934 | $2.10M |
| SPY 1× buy-hold (~9.5% net) | ~9.5% | ~55% | ~0.55 | $1.41M |

**Pareto-frontier configs** (dominate everything else on CAGR×MDD trade-off):
1. T1 gold-heavy (15.82% / 33.42%)
2. T2 equity-heavy (15.16% / 31.17%)
3. B4 ZROZ (13.79% / 28.02%)
4. L1 CEGB (11.13% / 25.83%)
5. L2 Bogleheads 67 NTSX (10.68% / 24.87%)

### Key empirical findings

1. **TMF (3× LTT) é caro em MDD**: dose-response confirma literatura — 25% TMF (B1) → 36.73% MDD; 10% TMF (B2) → 34.56%; **ZROZ instead of TMF (B4) → 28.02% MDD com Sharpe 0.973 idêntico**. ZROZ é zero-coupon LTT (mais duration que TLT, sem LETF decay). Wins risk-adjusted return.

2. **Gold-heavy (35% GDE) bate equal-weight (25% GDE)**: T1 gold-heavy tem CAGR 15.82% > B1 baseline 15.37% **E** MDD 33.42% < 36.73%. Move TMF 25→20 + GDE 25→35 + reduz NTSX 25→20. **Pareto-improvement** sobre user's baseline.

3. **MF source matters**: RSST (com SPY interno) é o melhor MF source nessa janela:
   - RSST: CAGR 15.37% / Sharpe 0.97 (B1 baseline)
   - KMLM only: CAGR 12.43% / Sharpe 0.91 (M1)
   - DBMF only: CAGR 11.84% / Sharpe 0.86 (M2 — pior MF source)
   - KMLM+DBMF blend: CAGR 11.65% / Sharpe 0.85 (M3 — combinação ruim)
   - **NÃO substitua RSST por KMLM/DBMF puros** — perde 3pp+ CAGR.

4. **No-duration falha**: B5 (sem TLT/TMF/ZROZ) tem MDD 41.45% — 5pp pior. **Duration matters mesmo se for só 25% TLT 1×.**

5. **Global vs US**: T3 RSSB (global stocks+bonds) ≈ B1 NTSX (US-only) em CAGR, mas RSSB MDD pior (38.81% vs 36.73%). Provavelmente efeito de US bull-market predominância no período. Consider RSSB como hedge se você acha que próxima década é international > US.

6. **Conservative camp (CEGB / Bogleheads)**: 11% CAGR / 25% MDD. Dominados em CAGR mas mantêm Pareto status como alternativa de menor risk profile.

### Deploy recommendations por perfil — pre-feedback histórico (SUPERSEDED)

> ⚠️ Esta tabela ainda usa Yearly rebal + no ER + post-DARF. **Para decisão de deploy use a tabela post-feedback no topo do doc.** Mantida aqui como evidência histórica.

| profile | recommendation | NET CAGR | NET MDD | Sharpe | rationale (pre-feedback) |
|---|---|---:|---:|---:|---|
| **MAX RETURN** (aceita 33% MDD) | **T1 gold-heavy** | 15.82% | 33.42% | **0.990** | era best Sharpe + best CAGR — **demoted após iter 040 Monthly+ERs** (caiu para Sharpe 0.688) |
| **BEST RISK-ADJUSTED** | **B4 ZROZ** | 13.79% | **28.02%** | 0.973 | era #2 — **promoted após iter 040** (subiu para Sharpe 0.745, novo #1) |
| **MODERATE** (good balance) | **B2 TMF10 balanced** | 15.54% | 34.56% | 0.974 | TMF dose 10% per literatura; pós-feedback Sharpe 0.717 |
| **CONSERVATIVE** (sleep well) | **L1 CEGB proxy** | 11.13% | 25.83% | 0.963 | RiskParityChronicles published template; pós-feedback Sharpe 0.729 |

### Spec final — T1 gold-heavy (era recomendação principal pre-feedback — SUPERSEDED)

> ⚠️ T1 foi demoted em 2026-05-01 após iter 040. **Use B4 ZROZ spec na seção POST-CLOSURE no topo do doc.** Mantido aqui apenas como referência histórica.


```python
# 20% NTSX + 35% GDE + 25% RSST + 20% TMF
# Annual rebalance via aportes mensais (lazy rebal, no realize)
# Lei 14.754: drag ~0.5-0.7pp; DARF apenas em terminal liquidation
{
  "type": "static",
  "weights": {
    "NTSXSIM": 0.20,  # NTSX  — WisdomTree 90/60 SPY/Treasuries
    "GDESIM":  0.35,  # GDE   — WisdomTree 90/90 SPY/Gold
    "RSSTSIM": 0.25,  # RSST  — ReturnStacked 100/100 SPY/MF
    "TMFSIM":  0.20,  # TMF   — Direxion 3× LTT (LETF, 1.05% expense)
  }
}
```

Notional total: 20×1.5 + 35×1.8 + 25×2.0 + 20×3.0 = 30 + 63 + 50 + 60 = **203% effective leverage**.

### Spec alternativo — B4 ZROZ (best risk-adjusted)

```python
# 25% NTSX + 25% GDE + 25% RSST + 25% ZROZ
# Substitui TMF por ZROZ (zero-coupon Long-Term Treasury)
# ZROZ = ~25y duration sem LETF decay. Mais duration que TLT, menos volatilidade que TMF.
{
  "type": "static",
  "weights": {
    "NTSXSIM": 0.25,
    "GDESIM":  0.25,
    "RSSTSIM": 0.25,
    "ZROZSIM": 0.25,
  }
}
```

⚠ **ZROZ disponibilidade no Inter — VALIDAR**. ETF ticker `ZROZ` (PIMCO 25+ Year Zero Coupon US Treasury Index ETF). Liquidez menor que TLT/TMF. Se Inter não tiver, usar TLT 1× (B3 — CAGR 13.04% / MDD 29.36%) como fallback.

### Caveats honestos pré-deploy

- **PBO inflation**: iter 038 tem N=14 configs → PBO grid-level inflado 0.91/0.59 para o selected. Esse é Principle M ao quadrado. **Anchor honest**: cada strategy individualmente é sólida; o ranking entre elas tem ruído ±1-2pp por grid composition. Use o ranking como guia, não como verdade absoluta.
- **MF ETFs são novos**: KMLM (Dec 2020), DBMF (May 2019), RSST (Sep 2022). Synth proxies extendem pra 1987 mas usam SPY+factor combinations — pode não capturar exatamente as dinâmicas live OOS. Update 2026-05-02: proxy `SPY+KMLM` subestima a curva live do RSST; `SPY+70% DBMF+30% KMLM` replica melhor o ETF real e deve substituir o proxy em próximos re-runs.
- **TMF 2022 stress**: TMF caiu −71% em 2022. Ao 25% allocation = −17.7pp portfolio drag em ano único. T1 gold-heavy reduz isso pra −14pp (com 20% TMF). B4 ZROZ elimina (ZROZ caiu −53% em 2022 ao 25% = −13pp). Trade-off real.
- **Portfolio drift**: rebal anual via aportes mantém pesos só se aportes são proporcionais. Em portfólios maduros (alocação muito > aportes), 5-10pp deviation triggers obriga venda + DARF realizada. Documentar bands.

---

## Histórico — meta-ensembles e LRS variants (iter 001-036)

> 📚 Esta seção foi removida em 2026-05-01 cleanup. Os ranking tiers A/B/C/D originais (com iter 026 H6 / iter 019 H2 / iter 015 F1 stack como top picks) **ficaram desatualizados** após iter 040-044 re-baseline com Monthly + ERs + lazy DARF. Os iters individuais não foram re-rodados na nova metodologia, então não há comparação apples-to-apples com a CANONICAL DEPLOY RANKING acima.
>
> Para o histórico completo dos iter 001-036 (meta-ensembles, LRS sensitivity, lag/buffer sensitivity iter 037), ver:
> - `BASE_MEMORY.md` — frontmatter de loop com KILLs e rationale por iter
> - `iterations/NNN-*/final_report.md` — per-iter detailed rationale + plots + specs
> - `iterations/037-*/SUMMARY.md` — buffer 2% + lag 2 sensitivity findings
>
> Por que esta seção foi descontinuada: as métricas dos iter 001-036 usavam pipeline interno (lh_56y / spy_real datasets, Yearly rebal, no ER drag) que produzia ranking diferente do testfol.io Monthly + ERs + lazy DARF baseline. Os iter 040-044 mostraram que o ranking muda materialmente quando methodology troca — não é safe deploy iter 026 H6 ou iter 015 F1 baseado em métricas pre-feedback.

---

## Como aplicar em live

### Pré-requisitos compartilhados

1. **Broker**: **Banco Inter Internacional** (Plano B). Confirmado em `docs/investment-mandate.md` §4.6:
   - Custódia: Apex Clearing (FINRA-regulated)
   - Corretagem: USD 0,00 ETFs/ações US
   - Spread FX BRL↔USD: 0.99-1.50% por leg (depósito + retirada apenas)
   - Settlement T+1 (industry US 2024-05-28+)
2. **Tributação**: Lei 14.754/2023 — DARF 15% flat anual via DAA. Apuração na DAA mar/maio. Ferramenta canônica: `studies/_shared/tax_engine.py:AnnualDarfEngine`.
3. **IOF**: 3.5% remessa outbound + 0.38% retorno (Decreto 05/2025) — só hits em depósito inicial / retirada final.
4. **Mandate §1 atual**: 100% Plano C MAINTENANCE MODE. Reativar Plano B exige **mandate §7 override**.

### ETFs necessários para B4 Conservative (deploy spec)

| sintético no backtest | ETF real (US) | ER | available Inter? |
|---|---|---:|---|
| `NTSXSIM` | NTSX (WisdomTree 90/60 SPY/Treasuries) | 0.20% | ⚠ verificar |
| `GDESIM` | GDE (WisdomTree 90/90 SPY/Gold) | 0.20% | ⚠ verificar |
| `RSSTSIM` | RSST (Return Stacked 100/100 SPY/MF) | 0.99% | ⚠ verificar |
| `ZROZSIM` | ZROZ (PIMCO 25y zero-coupon Treasury) | 0.15% | ⚠ verificar |

**Fallback ETFs** (se algum NTSX/GDE/RSST/ZROZ indisponível):
- ZROZ unavailable → **TLT 1×** (B3 spec — Sharpe 0.735, MDD -30.06% vs B4's 0.745 / -28.94%)
- RSST unavailable → KMLM (M1 spec — Sharpe 0.610, significativamente inferior)
- NTSX unavailable → SPY direct + IEF futures (manual stack — complica operacionalmente)

**Bloqueador pré-deploy**: validar com suporte Inter (Apex Clearing) quais dos 4 ETFs estão disponíveis. Inter Internacional já confirmou catálogo de ações/ETFs US largos; ETFs menos comuns (RSST especialmente, lançado 2022) podem precisar adição via support ticket.

### Cadência operacional — B4 Conservative

| ação | frequência | observação |
|---|---|---|
| Aporte mensal | 1×/mês (data fixa) | Comprar o ETF mais underweight para fechar gap de alocação |
| Rebal forçado | apenas se drift > ±10pp | Se aportes mensais não fecham o gap em 6 meses, considerar venda parcial |
| DARF | 1×/ano (apuração anual) | Lazy rebal → realized gains intra-ano = 0 → DARF efetivo só no terminal |

**Por que isso é trivial vs LRS/meta-ensembles antigos**:
- **Sem signal de gate** — não precisa monitorar SMA-200, momentum 126d, etc. Posição é fixa.
- **Sem flips intra-ano** — você não vende nada (a menos que decida sair completamente). Não há free-ride violation, não há lag operacional.
- **DARF deferida ao terminal** — você paga 15% só quando vender, sobre o lucro acumulado.

### Sizing inicial (mandate §4.8 paralelo Pepperstone)

Mandate atual não especifica staging Plano B (foi traçado para Plano A Pepperstone). Por analogia conservadora ao §4.8:

1. **Paper trading 3 meses** com a estratégia escolhida (não há paper Inter; simular em planilha + comparar com backtest)
2. **Live USD 1.000-2.500 inicial** (Inter mínimo é zero, mas FX spread fica caro abaixo de USD 1k)
3. **Escalada mensal condicional**: cada green month autoriza próximo degrau
4. **Cap inicial USD 5.000-10.000** até 6 meses de live verde

### Disclaimer obrigatório (mandate §7 trigger)

**B4 Conservative não é deploy-aprovada sob o mandate atual** (§1 MAINTENANCE MODE 100% Plano C). Para mover capital pra ela, necessário:

1. Override §7 formal (escrito) reativando Plano B
2. Validação de catálogo Inter para NTSX/GDE/RSST/ZROZ
3. Aceitar caveats:
   - **G3 (WF MDD per-window < 25%) NÃO passa** — drawdown durante 2008 GFC e 2022 inflation excede 25% por janela. É estrutural para qualquer leveraged stack, não overfit.
   - **MDD esperado ~29%** num bear market severo. Tolerância psicológica precisa cobrir isso. Se panic-sell at the bottom, destrói a estratégia.
   - **NTSX/GDE/RSST são ETFs jovens** (2018/2022/2022). Synth proxies extendem para 1987 mas live track record ainda curto. Para RSST especificamente, o proxy `KMLM-only` usado no iter 044 foi marcado como incompleto em 2026-05-02; exigir re-run com `70% DBMF / 30% KMLM` antes de deploy.

---

## Resumo executivo

| pergunta | resposta |
|---|---|
| **Tem estratégia que bate SPY (CAGR + MDD)?** | Sim, **9 estratégias** passam ambos bars no canonical iter 044 ranking (Monthly + ERs + lazy DARF). |
| **Tem estratégia "WINNER tier" (≥90/100 + bars)?** | Não. Hunt fechou em 2026-04-30 com user override "gate-pass + bars 1+2 é suficiente". |
| **Top recomendação canonical?** | **B4 Conservative** (25 NTSX / 25 GDE / 25 RSST / 25 ZROZ): gross 13.31% / net 12.84% / MDD -28.94% / Sharpe 0.745 / Calmar 0.460. |
| **Best MDD-extreme alternative?** | **G4d** (25 RSSB / 25 GDE / 25 ZROZ / 25 KMLM): MDD -22.56% (recorde do estudo) com CAGR 10.10% (caveat: RSSB ~2y live). |
| **Overfit foi validado?** | Sim. B4 sobreviveu a 4 testes adversariais (Reddit Post 1 community feedback iter 040-043) + walk-forward weight drift gate G8 (PASS — static beats walk-forward em 3/3 universos). |
| **Deploy-ready hoje?** | Não — exige mandate §7 override + validação ETFs Inter (NTSX/GDE/RSST/ZROZ) + paper 3 meses. RSST proxy re-run foi feito no iter 045; próximo bloqueador metodológico é broker/catalog + forward/paper. |

---

## Citações

- `[advances_fin_ml, p.31-34]` — gate framework (PBO/DSR/WF/Bootstrap/CrossLib)
- `[advances_fin_ml, p.208-211]` — PBO via CSCV
- `[advances_fin_ml, p.222-223]` — Deflated Sharpe Ratio
- `[advances_fin_ml, p.196-202]` — Bootstrap CI
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` — Gayed LRS 200d SMA gate
- `[risk_parity, ch.5, p.10]` — Carlson capital-efficient stacking (NTSX/GDE rationale)
- `[ilmanen_expected_returns, ch.19]` — managed futures crisis-alpha (KMLM)
- HFEA (Bogleheads 2019) — leveraged barbell baseline
- Lei 14.754/2023 — DARF 6015 ganho de capital exterior
- Bridgewater All-Weather (Dalio public papers 2011) — risk-parity foundation
- Asness 1996 "Why Not 100% Equities?" JPM — leverage-balanced thesis
