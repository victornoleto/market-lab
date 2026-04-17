# Task B3 — LETF 3× synthetic (leverage_comparison) [SWING BROKER] [PLANO B]

**Data:** 2026-04-17 21:45
**Fase:** Phase 3.5b-addendum
**Iter:** 19
**Tag:** [PLANO B] [SWING BROKER] [⚠️ FAIL MaxDD gate]
**Duração wallclock:** ~1 min (SPX TR cache hit + reuso do script B2)
**Pytest:** 670 passed (baseline mantido — zero código novo, só script
            CLI param `--leverage 3.0`)

---

## O que aconteceu

Task B3 do `specs/phase_3_5b_addendum_operational.md` fecha a tabela
side-by-side **2×/2.5×/3×** que a Phase 3 Lead B1c (`reports/letf_rotation_b1c_verdict.json`)
deixou em aberto. O B1c rejeitou o 3× pelo gate **MaxDD ≤ 25% por janela
walk-forward**; o addendum re-executa, **publica o report mesmo com FAIL
sinalizado**, e fornece a evidência numérica que o usuário precisa para
decidir se aceita o tradeoff (mais CAGR a custa de gate-failure).

Implementação:

1. Reuso integral do script `scripts/run_phase3_5b_letf_leverage_variant.py`
   criado em B2 — basta `--leverage 3.0`. Zero código novo.
2. Config: `LETFRotationConfig(filter="EMA", lookback=100, band_pct=0.0,
   leverage=3.0, annual_fee=0.01, tax_rate=0.15)` — único delta vs winner
   2× é a alavancagem (mesmo princípio de B2).
3. Cost model: Gayed flat-fee (`r_synth[t] = 3·r_SPX_TR[t] - 0.01/252`)
   `[leverage_for_the_long_run, p.16]`. ETF real: **UPRO** (ProShares,
   2009-06-23+) e **SPXL** (Direxion, 2008-11-05+) — ambos disponíveis
   em broker BR via BDR/swap, sem necessidade de instrumento sintético
   para deploy moderno.
4. Janela: LONGEST available per CLAUDE.md hard rule — 14 191 bars
   SPX TR stitched (KF pré-2001-05-14, Tiingo SPY-TR pós).

## Métricas 3× (full-window 1970-01-02 → 2026-04-14)

| Métrica | L=2× (winner) | L=2.5× (sintético) | **L=3× (este)** |
|---------|--------------:|-------------------:|----------------:|
| CAGR | 44.69% | 58.89% | **74.17%** |
| Sharpe | 1.848 | 1.882 | **1.910** |
| MaxDD full | 20.55% | 24.65% | **28.45%** ⚠️ |
| Vol annual | 21.23% | 26.48% | **31.72%** |
| IR vs SPY | 1.601 | 1.837 | **1.963** |
| n_trades | 296 | 296 | 296 |
| WF MaxDD ≤ 25% (8 windows) | ✅ 8/8 | ✅ 8/8 (margem 0.35pp WF1) | ❌ **5/8** |

## Walk-forward MaxDD por janela

A MaxDD por janela isolada (o gate B1c) falha em 3 das 8 janelas:

| Window | Period | 2× | 2.5× | **3×** |
|--------|--------|---:|----:|------:|
| WF1 | 1970-01 → 1977-12 | -20.55% | -24.65% | **-28.45%** ⚠️ |
| WF2 | 1978-01 → 1985-12 | -19.39% | -23.38% | **-27.20%** ⚠️ |
| WF3 | 1986-01 → 1993-12 | -16.80% | -20.17% | -23.32% |
| WF4 | 1994-01 → 2001-12 | -17.56% | -21.14% | -24.49% |
| WF5 | 2002-01 → 2009-12 | -13.91% | -16.74% | -19.39% |
| WF6 | 2010-01 → 2017-12 | -15.79% | -19.07% | -22.17% |
| WF7 | 2018-01 → 2025-12 | -18.36% | -22.58% | **-26.67%** ⚠️ |
| WF8 | 2026-Q1 (parcial) | -8.90% | -10.80% | -12.64% |

Padrão: **drawdown escala quase-linearmente** com a alavancagem
(~1.4× por +0.5x de leverage), enquanto **Sharpe estanca** (+0.06 entre
2× e 3×). Os anos 70/80 e o ciclo 2018-25 são os mais voláteis dentro
das janelas "on-regime" — o EMA100 corta para CASH antes dos crashes
maiores (2008/2020), por isso WF5 é o **menor** drawdown apesar de
conter GFC.

## Verdict

**❌ FAIL gate B1c** — MaxDD por janela > 25% em WF1 / WF2 / WF7.
Configuração **NÃO promove ao winner list** Plano B. Continuamos com
**L=2× (SSO) como production default**, conforme acordado em iter 17
(jornada B1).

3× permanece como **escalation lever opcional** caso o usuário decida
abrir mão dos gates Phase 3 e gerenciar risco com overlays manuais
(Kelly < 0.5×, regime-conditional sizing). A documentação completa
agora existe; a decisão é dele.

## O que B3 entrega

1. `reports/phase3_5b/variants/letf_leverage_comparison/letf_ema100_3x/`
   com 6 artefatos: `standard_report.md`, `trade_log.csv`, `trade_log.md`,
   `summary.json`, `equity_curve.png`, `flags.md`.
2. `reports/phase3_5b/variants/letf_leverage_comparison/README.md` (sub-index)
   com tabela side-by-side **2×/2.5×/3×** + WF MaxDD detalhado +
   recomendação de production default. Cumpre spec §2 Task B último item.
3. Esta jornada [PLANO B].

## Estado da Phase 3.5b-addendum

Tasks completed:
- ✅ A — 2-leg LETF+QQQ EW report (iter 16)
- ✅ B1 — LETF 2× baseline reuse (iter 17)
- ✅ B2 — LETF 2.5× synthetic (iter 18)
- ✅ **B3 — LETF 3× (esta iter 19)**

Pendente (4 iters restantes):
- C1 — `rebalance_modes.py` module + ≥15 testes
- C2 — comparison_3leg.md
- C3 — comparison_2leg.md + sub-index rebalance_modes/README.md
- D — main `reports/phase3_5b/README.md` + `variants/README.md` all-in
       table + summary jornada update + `status: done` flip

## Citações

- Synthetic LETF formula: `[leverage_for_the_long_run, p.16]`
- Leverage Table 8 (1.25×/2×/3× — sem 2.5× listado):
  `[leverage_for_the_long_run, p.17]`
- WF MaxDD ≤ 25% gate: Phase 3 Lead B1c
  (`reports/letf_rotation_b1c_verdict.json`) + Investment Mandate §5
- Vol-drag escalando com L²: `[leverage_for_the_long_run, p.7-9]`
- Winner immutability: `docs/self_improvement/memory.md` §Constraints §4
