# Long-Term Portfolio — Final Pick: F1 + SPLIT MF

Após **17 sweep iters** (027-043, n_trials=156) sobre o iter 023 baseline, o portfolio escolhido pra deploy 20-30y de aposentadoria é **F1 (iter 023) com MF SPLIT**:

## Composição final (5 ETFs)

| Ticker | % | Papel | Issuer | TER |
|---|---:|---|---|---:|
| **NTSX** | 25% | 90/60 US equity + Treasury stack (1.5×) | WisdomTree | 0.20% |
| **GDE** | 25% | 90/90 US equity + gold stack (1.5×) | WisdomTree | 0.20% |
| **KMLM** | 17.5% | KFA Mt Lucas managed futures trend (engine #1) | KFA Funds | 0.92% |
| **DBMF** | 17.5% | iMGP DBi managed futures CTA-replication (engine #2) | iMGP DBi | 0.85% |
| **TLT** | 15% | iShares 20+y Treasury (duração / drawdown insurance) | iShares | 0.15% |

**Notional total**: 132%. **TER ponderado**: ~0.45%/y. **Score multi-critério**: 62.07/100.

## Por que esse e não outro

Após 16+1 iters testando 6 sleeves (NTSD, AVUV, AVDV, AVEM, SPMO, IDMO) em substituição source variada + 4 finalists distintos + sensitivity de MF + variação de TLT slot, a evidência empírica converge:

1. **iter 023 architecture é estruturalmente ótimo** no testfolio universe pra capital-efficient stacking. 12 iters de Phase 1+1B não conseguiram melhorá-lo substantivamente.

2. **Apenas SPMO (US momentum) tem +signal robusto** entre os 6 sleeves testados — Δ +0.044 ndx_real máximo. Mas só beneficia ndx_real, não lh_56y.

3. **Avantis SCV family (AVUV/AVDV/AVEM) é estruturalmente subordinada** em regime US-large-cap-dominante 2010-2024. Não há substitution source que rescue.

4. **NTSD não passa** — confirma direção A.1-A.3 do loop anterior (iter 014/015 já mostraram o mesmo padrão).

5. **F1+SPLIT vence em multi-critério**:
   - **Mean Sharpe 1.109** — maior dos 4 finalists
   - **Mean MDD 16.76%** — menor dos 4 finalists
   - **5 ETFs** (4+1 do SPLIT) — empate em simplicidade com F3/F7 mas com Sharpe + MDD melhores
   - **All-major-issuer composition** com SPLIT resolvendo concentração single-engine

6. **MF SPLIT (50/50 KMLM+DBMF) validado em iter 042** — Sharpe 1.0004 (vs KMLM puro 0.9626, DBMF puro 0.9947) em janela 26y intersection. AUM diversification ($600M KMLM + $3.2B DBMF) reduz closure risk pra 30y deploy.

7. **TLT 15% NÃO é redundante** (iter 043) — tentar remover TLT pra +equity ou +MF degradou Sharpe (-0.04 a -0.11) ou explodiu MDD (+7pp). Em uma carteira que já satura equity via NTSX+GDE stacking, TLT é o seguro de drawdown mais barato disponível.

## Trade-offs aceitos

- **CAGR esperado ~10-11.5%** (vs SPY 13.8% no melhor window; vs F7 stacked-MF 12.5%). Dado capital-efficient stack alavancado, o trade é Sharpe + MDD por CAGR — explícito no design.
- **TER 0.45%** drag anual (vs F2 pure factor 0.30%) é o custo das ETFs alavancadas.
- **132% notional** significa exposição maior que capital — em crash extremo (>40% equity drawdown), MDD do portfolio pode ir a 25-30% mesmo com proteção MF+TLT.
- **Survivorship/regime risk**: portfolio é otimizado pra regime mixed (validado em 56y window). Se regime futuro for radicalmente diferente (e.g., negative-yield permanente pra TLT), thesis precisa revisão.

## Achados importantes do sweep (registro pro futuro)

12 iters comprovaram empiricamente o que **não funciona** em cima do iter 023:
- ❌ NTSD (ex-US developed equity stack)
- ❌ AVUV / AVDV / AVEM (Avantis SCV/profitability/value family)
- ❌ IDMO (intl momentum)
- ⚠️ SPMO (US momentum) tem signal modesto, mas não justifica complexidade adicional vs F1 baseline
- ❌ RSSB substituindo TLT
- ❌ Remover TLT pra mais equity ou MF

Isso é **knowledge negativo valioso** — fecha direções de exploração futuras e confirma que iter 023 é a baseline pra qualquer extensão.

## Próximos passos (deploy execution)

1. **Preencher INTER_CHECK.md** — verificar disponibilidade dos 5 ETFs (NTSX, GDE, KMLM, DBMF, TLT) na Inter Internacional. Se DBMF não estiver disponível, fallback é F1 sem SPLIT (4 ETFs, KMLM 35% concentrado em single issuer — aceitável).

2. **Mandate §7 override request** (draft já em FINAL_REPORT_seven_portfolios.md §8) — formalmente autorizar deploy desta composição substituindo Plano C strict.

3. **Setup execution**:
   - Abrir/confirmar conta Inter Internacional (Inter&Co Securities FINRA)
   - Comprar ETFs em proporção 25/25/17.5/17.5/15
   - Definir cronograma rebalance (anual recomendado, threshold ±5pp)
   - Definir gatilhos de revisão (regime change, ETF closure, AUM drop <$50M)

4. **Monitor permanente**:
   - DBMF / KMLM AUM trimestralmente
   - Tracking error real vs sintético em testfolio
   - Regime indicators (CAPE, T10Y3M, EBP) — sem rebalance automático, só awareness

## Citações

- `[risk_parity, ch.5, p.10]` — Carlson cap-efficient stacking (tese matriz)
- `[risk_parity, ch.2, p.37-41]` — Fama-French factor framework (justifica AVUV/AVDV/AVEM closure)
- `[stocks_on_the_move, p.21-30]` — Clenow momentum (SPMO retention rationale)
- `[ilmanen_expected_returns, ch.19]` — intl + EM diversification + MF crisis-alpha
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1 gate)
- `[advances_fin_ml, p.222-223]` — DSR (n_trials=156 cumulative)
- `[advances_fin_ml, p.196-202]` — bootstrap CI (G6)
- `[advances_fin_ml, p.31-34]` — cross-lib + factor framework
- WisdomTree NTSX/GDE prospectus
- KFA MLM Index + iMGP DBi DBMF prospectus
- ReSolve/Newfound Return Stacked methodology (2023) — RSSB/RSST conceptual
- Frazzini-Israel-Moskowitz 2018 — UMD long-only capture rate

## Específico vs Plano C anterior

Plano C strict (mandate §1 MAINTENANCE) era 100% passivo factor-tilted. F1+SPLIT é **substantivamente diferente**:
- **Capital efficiency**: 132% notional via NTSX/GDE futures overlay vs 100% notional Plano C
- **Crisis-alpha**: 35% MF (KMLM+DBMF) vs 0% MF Plano C
- **Duration hedge**: 15% TLT vs ~30% AGG-style bonds Plano C
- **Sharpe esperado**: 1.1+ gross vs ~0.67 Plano C V3_1
- **Trade**: complexity (5 ETFs vs 3-4 Plano C), TER 0.45% vs 0.20%, mandate §7 override required vs §1 default

A decisão de deploy F1+SPLIT é **explicitamente uma aposta** que capital efficiency stacking + crisis-alpha diversification supera passive factor-tilted em horizon 20-30y. A evidência (16-iter sweep, multi-criteria scoring) suporta essa aposta com confidence empírica > Plano C original.

---

**Status**: pick_complete. Aguardando INTER_CHECK.md fill + mandate §7 override formalization.
