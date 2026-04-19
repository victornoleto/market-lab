# Phase 3.5b addendum — Task C3: rebalance modes on 2-leg EW — comparativo completo

**Tag:** `[SWING BROKER]`  (Plano B — BR broker, 15 % IR realizado, sem swap)
**Scope:** Repetir o comparativo da Task C2 no 2-leg EW `{LETF 2x +
QQQ Donchian 20/10}` (Task A) na janela longest-common (QQQ-limited):
**2001-05-14 → 2026-04-14** (6266 bars, 24.87 anos). Checa a hipótese
"2-leg menos sensível a drift porque ρ=0.555 alta".
**Status:** ✅ DONE — 4 artefatos + sub-index + implementation notes.
**Pytest:** 698 passed (mantido).

---

## Metáforas primeiro

O 2-leg EW é uma versão enxuta do 3-leg: corta o descorrelator (GLD)
e deixa só o motor (LETF) + o foguete (QQQ). O problema é que ambas
as pernas são "motor da mesma cor" — as duas sobem e caem juntas em
regimes de crise. Rebalancear virou menos trabalhoso, mas o alívio
do drift e do imposto não veio na mesma proporção.

- **Daily (ref Task A):** idealização — equity recomputada a cada
  barra assumindo pesos 50/50 perfeitos. É a baseline Phase 3.5b.
- **Monthly sell:** só vende no último dia útil do mês; 15 % IR.
- **Monthly cashflow:** nunca vende; $500/mês vão 100 % para a
  perna mais magra. Tax-free.

A grande questão da C3 era operacional: num broker BR sem bot custom,
qual desses 3 modos preserva mais do Sharpe do winner?

---

## Números — 2-leg EW 24.87 anos

| Métrica | Daily (ref Task A) | Monthly sell | Monthly cashflow |
|---|---|---|---|
| Equity final | $92.08 M | $67.87 M | $940.7 M¹ |
| CAGR | 31.59 % | 29.94 % | 42.63 %¹ |
| Sharpe | **1.888** | 1.800 | 1.881 |
| Volatilidade ann | 15.16 % | 15.23 % | 21.26 % |
| MaxDD | **14.41 %** | 14.46 % | 18.15 % |
| Max drift (peak) | 0 % | 5.23 % | 49.30 % |
| Mean drift / bar | 0 % | 0.60 % | 32.69 % |
| Eventos tributários/ano | 0 | 12.1 | 0 |
| IR/ano (rebal layer) | $0 | **$144 794** | $0 |
| Depósito/ano | $0 | $0 | $6 033 |
| Depósitos totais | $0 | $0 | $150 k |

¹ CAGR do cashflow incha porque os $6 k/ano também compõem — **não é
alpha puro**. As outras duas colunas são deposit-free.

---

## 2-leg vs 3-leg — o teste da hipótese

| Métrica | 2-leg | 3-leg | Δ | Veredito |
|---|---|---|---|---|
| Mean drift, monthly_sell | 0.60 % | 0.82 % | −0.22 pp | ✅ 2-leg drifta menos em média |
| Max drift, monthly_sell  | 5.23 % | 4.81 % | +0.42 pp | ❌ 2-leg pica levemente mais alto |
| Mean drift, cashflow     | 32.69 % | 40.10 % | −7.41 pp | ✅ 2-leg corrige mais rápido |
| Max drift, cashflow      | 49.30 % | 65.05 % | −15.75 pp | ✅ grande: $500 em 2 legs > $500 dividido em 3 |
| IR/ano, monthly_sell     | $144 794 | $30 740 | +$114 054 | ❌ 2-leg paga 4.7× mais imposto |

**Conclusão da hipótese:** parcialmente confirmada.

- A correlação alta (ρ=0.555) **reduz o drift típico**, mas **não
  reduz o drift de cauda**: durante o dotcom bust (2001-2002) QQQ caiu
  muito enquanto o LETF filter mandava pra caixa, e as 2 legs
  decouplearam acima do pico 3-leg.
- O IR/ano explodiu no 2-leg porque: notional por perna é 50 % (vs
  33 % no 3-leg) ⇒ cada rebalance move ~1.5× mais dólares; janela
  é 3.5 anos mais longa e CAGR é 6 pp maior ⇒ ganho realizado por
  venda é materialmente maior; o GLD do 3-leg funciona como
  "drenador de ganhos" (CAGR baixo, rebals pegam pouca realização).

---

## Ranking por variante

- **3-leg (C2):** `daily > monthly_sell > monthly_cashflow` — daily é
  imbatível; sell perde 0.14 Sharpe com custo modesto; cashflow's
  CAGR é enganoso.
- **2-leg (C3):** `daily ≈ monthly_cashflow > monthly_sell` — daily
  1.888 e cashflow 1.881 são estatisticamente indistinguíveis; o
  cashflow adiciona $6 k/ano de poupança em cima — mas custa **+3.74
  pp de MaxDD** (18.15 % vs 14.41 %).

---

## Recomendação operacional (atualizada)

1. **Default:** daily rebal no 3-leg winner. Gate MaxDD 25 % passa
   com folga (10.86 %), Sharpe 2.108, CAGR 25.56 %.
2. **Operational fallback aceitável:** monthly_cashflow no 2-leg.
   Só se o usuário aceitar MaxDD 18 % e o incremento de Sharpe
   vier *de depósito externo*, não de alpha. Útil para quem faz
   DCA $500/mês e não quer script de venda.
3. **Rejeitar:** monthly_sell em qualquer variante. 2-leg sangra
   $145 k/ano só pra manter alvo; 3-leg perde 0.14 Sharpe vs daily
   sem ganho compensatório.

Winner 3-leg EW permanece **imutável e default de produção.**

---

## O que foi criado

### `reports/phase3_5b/variants/rebalance_modes/`
- `comparison_2leg.md` — tabela completa + interpretação + citações.
- `summary_2leg.json` — snapshot machine-readable.
- `drift_2leg.png` — time-series drift per-bar por modo.
- `equity_2leg.png` — overlay equity curves (log).
- `README.md` — sub-index 2-leg vs 3-leg (hipótese + delta drift/tax
  + ranking + recomendação).
- `implementation_notes.md` — decisões do módulo (cost basis
  proporcional, month-end detection, deposit allocation).

### `scripts/run_phase3_5b_task_c3_rebalance_2leg.py`
Mirror da C2 com TARGET_WEIGHTS={LETF_2x:1/2, QQQ:1/2}, sem GLD.
Janela QQQ-limited 2001-05-14 → 2026-04-14.

### `src/` e `tests/`
**Intactos.** Nenhuma lógica nova — apenas scripts e relatórios.
Módulo `rebalance_modes.py` + 28 tests já existem desde C1.

---

## Citações

- Baseline reset diário: `[advances_fin_ml, p.298-299]`.
- Drift vs tax tradeoff: `[leverage_for_the_long_run, p.17, Table 8]`.
- EW blend robustness: `[advances_fin_ml, p.298-299]`.
- BR 15 % IR: Investment Mandate §4.

---

## Próximo passo (Task D — último do addendum)

1. Criar `reports/phase3_5b/README.md` (main index) com TL;DR +
   tabela winners + links para todos os sub-reports.
2. Atualizar `jornada/2026-04-17-2045-phase3.5b-full-validation-summary.md`
   com seção "Operational variants (addendum 2026-04-17)".
3. Jornada `2026-04-17-2245-phase3.5b-addendum-summary.md`.
4. Flip `memory.md status: done`.

Após Task D, o loop fecha.
