# Estado atual — ai-trade (2026-04-19)

> **Propósito:** onboard rápido para humanos e agentes. Após 0 e
> Phase 2/2.5/3/3.5a/3.5b completas, o projeto tem **dois winners
> production-ready** (Plano A e Plano B). Este doc é o índice de
> orientação — a verdade canônica vive nos arquivos referenciados.

---

## TL;DR

- **Plano A** (Path A, short-hold CFD) → `gayed_ema100_L2_off_gld`,
  CFD Pepperstone 2×, Sharpe 2.285, CAGR 79.14%, MDD -21.02%.
- **Plano B** (Path B, swing broker) → Portfolio 3-leg EW
  (SSO+QLD+UGL, threshold 10pp), Banco Inter Global, Sharpe 2.251
  em janela canônica (2.609 V4), CAGR 25.56%, MDD -10.86%.
- **Próximo:** Phase 4 — paper trading dual-path 3 meses
  (cTrader Demo A + Inter Global B).
- **Blocker operacional:** aprovação do OAuth Pepperstone
  (Spotware) para Plano A paper.

---

## Plano A — Pepperstone CFD (short-hold alavancado)

**Status:** WINNER confirmado em 2026-04-19 (Phase 3.5a-V2). 13/13 gates
passam com folga material. Pronto para paper trading.

**Config canônica:** `gayed_ema100_L2_off_gld`

| Dimensão | Valor |
|---|---|
| Sinal | Gayed LETF rotation transportada para CFD |
| Regime filter | EMA-100 sobre SPY close (daily) |
| Risk-on | SPY + QQQ equal-weight @ leverage 2× (CFD Pepperstone) |
| Risk-off | GLD (não cash, não TLT) |
| Hold median | 6 dias |
| Sharpe OOS (2018-2023) | 2.285 |
| CAGR OOS net | 79.14% |
| MaxDD OOS | -21.02% |
| IR vs SPY | 2.161 |
| PBO (10-block) | 0.103 |
| DSR p-value (N=27) | 0.000288 |
| Bootstrap 99.9% CI low | 0.962 |

**Base científica:** `[leverage_for_the_long_run, Gayed 2016/2020]` —
regime-on/off + leverage tática. Invariantes descobertas no L2 sweep:
(1) MDD super-linear em leverage (L2 ~21%, L3 ~30%, L5 ~49% — só L=2
passa gate); (2) adaptividade EMA-100 > LRS > SMA-200; (3) GLD > cash
> TLT como off-regime (TLT correlaciona com SPY em rate shocks).

**Leia mais:**
- Living strategy doc (autoritativo):
  [`docs/strategies/plano_a_v2_l2_gayed_cfd.md`](strategies/plano_a_v2_l2_gayed_cfd.md)
- Narrativa humana do arc V1→V2:
  [`jornada/2026-04-18/23-phase3.5a-v2-WINNER-humana.md`](../jornada/2026-04-18/23-phase3.5a-v2-WINNER-humana.md)
- Gate verdict PASS técnico:
  [`jornada/2026-04-19/01-phase3.5a-v2-L2-gayed-transported-PASS.md`](../jornada/2026-04-19/01-phase3.5a-v2-L2-gayed-transported-PASS.md)
- Summary T7 (fecho V2):
  [`jornada/2026-04-19/07-phase3.5a-v2-summary-WINNER-FOUND.md`](../jornada/2026-04-19/07-phase3.5a-v2-summary-WINNER-FOUND.md)
- Evidência bruta (winner config + AGGREGATE + registry):
  [`reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/`](../reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/)
- Preservação:
  [`reports/phase3_5a_v2/_DO_NOT_CLEANUP.md`](../reports/phase3_5a_v2/_DO_NOT_CLEANUP.md)
- Spec executada:
  [`specs/phase_3_5a_v2.md`](../specs/phase_3_5a_v2.md)

**V1 refutado (contexto histórico):** framework errado (1h FX retail,
hold ≤5d, universe pequeno) → 0/143 PASS em 6 famílias. Ver 7 jornadas
DEAD em `jornada/2026-04-18/` (slugs `T1-T5-*-DEAD.md` + `T6-*` + `T7-*`).

---

## Plano B — Banco Inter Global (swing LETF rotation)

**Status:** WINNER confirmado em 2026-04-17 (Phase 3.5b). 5 gates formais
passam em 2 janelas (21.4y canônica + 40y extended). Threshold 10pp
default revisto em 2026-04-18. SSO+QLD+UGL todos confirmados no catálogo
Inter Global.

**Config canônica:** Portfolio 3-leg EW, rebalance threshold 10pp

| Perna | LETF 2× | Sinal (no 1×) | Execução |
|---|---|---|---|
| 1 | SSO (S&P 2×) | EMA-100 regime sobre SPY | SSO quando close > EMA100 |
| 2 | QLD (NASDAQ 2×) | Donchian 20/10 sobre QQQ | QLD quando breakout 20d high |
| 3 | UGL (Gold 2×) | Donchian 40/20 sobre GLD | UGL quando breakout 40d high |

**Pesos alvo:** 1/3, 1/3, 1/3 — cada perna opera independente. Cash
dentro da perna quando filtro off; cross-leg rebalance só em evento
de threshold ≥10pp.

| Métrica | V4 canônica (2004-2026, 21.4y) | Extended (1986-2026, 40y) |
|---|---|---|
| Sharpe OOS | 2.609 (janela comum 2.251) | 2.320 |
| CAGR | 39.19% | 37.93% |
| MaxDD | -12.22% | -16.91% |
| vs SPY B&H | 10.66% CAGR, Sharpe 0.63, MDD -55% | (idem) |

**Base científica:** `[leverage_for_the_long_run]` + extensão multi-asset
`[advances_fin_ml, ch.11, ch.14]`. Rebalance threshold escolhido por
sweep completo (5/10/15/25/100pp) — 10pp domina 5pp em operabilidade
(metade das DARFs, Sharpe dentro do ruído).

**Broker:** Banco Inter Global (zero corretagem + spread FX 0.99-1.50%
+ T+1 liquidation). SSO/QLD/UGL todos confirmados no catálogo
(user validou 2026-04-18). 15% IR BR por venda lucrativa via DARF 6015;
~12-15 DARFs/ano.

**Fallback documentado:** V1 (SSO+QQQ+GLD) — se Inter delistar QLD ou
UGL, degrade pra V1. Sharpe 2.478, CAGR 26.53%, MDD -9.39%.

**Leia mais:**
- Living strategy doc (autoritativo — inclui V1-V8 completo + rationale V4 default):
  [`docs/strategies/plano_b_3leg_letf_rotation.md`](strategies/plano_b_3leg_letf_rotation.md)
- Runbook de produção (operacional canônico):
  [`reports/phase3_5b/PRODUCTION.md`](../reports/phase3_5b/PRODUCTION.md)
- Index técnico dos sleeves:
  [`reports/phase3_5b/README.md`](../reports/phase3_5b/README.md)
- V4 gate verdict formal:
  [`reports/phase3_5b/variants_letf_execution/`](../reports/phase3_5b/variants_letf_execution/)
- Extended window 1986-2026:
  [`reports/phase3_5b/extended_window_1986_2026/`](../reports/phase3_5b/extended_window_1986_2026/)
- Threshold sweep completo:
  [`reports/phase3_5b/threshold_sweep_full/`](../reports/phase3_5b/threshold_sweep_full/)
- Rejeição SSO+ZROZ+GLD (decisão negativa documentada):
  [`reports/phase3_5b/rejected_alternatives/static_sso_zroz_gld/`](../reports/phase3_5b/rejected_alternatives/static_sso_zroz_gld/)
- Jornada V4 promoted (2026-04-18):
  [`jornada/2026-04-18/08-phase3.5b-V4-promoted-gate-verdict.md`](../jornada/2026-04-18/08-phase3.5b-V4-promoted-gate-verdict.md)
- Preservação:
  [`reports/phase3_5b/_DO_NOT_CLEANUP.md`](../reports/phase3_5b/_DO_NOT_CLEANUP.md)

---

## Próxima fase — Phase 4 paper trading dual-path

**Spec autoritativo:**
[`specs/phase_4_paper_trading.md`](../specs/phase_4_paper_trading.md)

**Duração:** 3 meses calendário (mínimo). Paralelo A + B.

**Path A paper** → cTrader Demo Pepperstone (bloqueado pelo OAuth
approval Spotware). Sinal diário via `scripts/live_plano_a_paper_daily.py`
(a construir). Zero capital real.

**Path B paper** → Inter Global com capital real **mínimo** (sanidade
operacional). Sinal emitido + planilha manual; user executa ordens.

**Gates paper → live:**

| Métrica | Gate |
|---|---|
| Realized Sharpe | ≥ 0.7 × backtest (A: ≥1.60, B: ≥1.58) |
| MaxDD realizado | ≤ 1.5 × backtest (A: ≤31.5%, B: ≤16.3%) |
| Slippage médio | ≤ 30 bps/trade |
| Latency signal→fill | ≤ 5 min |

**Zona proibida (contrato V2):**
- V3 do Plano A (a busca está fechada).
- Re-otimizar parâmetros winners em Phase 4 — só teste de fidelidade.
- Expansão de universe ou features nas strategies winners.

---

## Regras invioláveis (lembrete)

Todas as 7 regras do Investment Mandate continuam valendo. Sumário:

1. Capital: 60-80% passivo (aposentadoria) + 20-40% ativas split 50/50
   A+B dentro do bucket ativo.
2. CAGR mínimo = CDI BR (~13-14%/ano). Ambos os winners superam por 2-5×.
3. Plano A é multi-asset (SPY+QQQ+GLD via CFD); Plano B é multi-LETF
   (SSO+QLD+UGL).
4. Gates sempre (PBO < 0.5, DSR p < 0.05, WF ≥ 6/8, single-block OOS,
   forward-window stress). Zero bypass.
5. Threading model live: 1 thread/ativo.
6. Dynamic sizing: fase agressiva → preservação conforme equity cresce.
7. Citação obrigatória em toda decisão técnica: `[book.slug, p.X]`.

**Leia mais:** [`docs/investment-mandate.md`](investment-mandate.md).

---

## Referências cruzadas

- **Roadmap técnico detalhado (fases + decisões diferidas):**
  [`ROADMAP.md`](../ROADMAP.md)
- **Setup + arquitetura do repo:**
  [`README.md`](../README.md)
- **Narrativa humana (newest first):**
  [`jornada/README.md`](../jornada/README.md)
- **Mandate completo (regras + §7 histórico):**
  [`docs/investment-mandate.md`](investment-mandate.md)
- **Knowledge base (34 livros, 16 active):**
  [`books/MAPPING.md`](../books/MAPPING.md)
  + Skill agregada [`knowledge/SKILL.md`](../knowledge/SKILL.md)
- **Convenções do projeto:**
  [`CLAUDE.md`](../CLAUDE.md)

---

## Changelog deste doc

- **2026-04-19:** versão inicial — criado pós-cleanup, após V2 winner
  found + Phase 3.5b final. Orienta para Phase 4 paper trading.
