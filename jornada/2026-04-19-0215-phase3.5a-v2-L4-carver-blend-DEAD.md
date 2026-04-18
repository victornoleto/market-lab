# [SHORT-HOLD CFD] V2-L4 — Carver risk-parity blend DEAD: L2 standalone remains the Plano A answer

**Data:** 2026-04-19 02:15 (iter 58, loop `phase3.5a-v2/plano-a-last-attempt-20260418`)
**Lead:** V2-L4 (atomic) — Carver multi-strategy risk-parity.
**Verdict:** ❌ DEAD (blend fails V2 winner criteria: CAGR, Sharpe, IR-vs-SPY).

---

## O que fizemos

V2-L4 é a quarta cabeça do Plano A V2. Ideia: os leads anteriores
(L1 TSMOM multi-asset, L2 Gayed transportado para CFD, L3 AFML
triple-barrier + meta) deixaram três séries diárias diferentes no
disco. A promessa de Carver `[systematic_trading, ch.8-9]` é que, se
você normalizar cada uma para um target de vol e combinar em risco
parity, o resultado deveria ter mais Sharpe por unidade de risco do
que qualquer leg isolada — porque a diversificação abate variância e
nenhuma das três é capaz, sozinha, de empurrar o blend a risco.

Peguei o *melhor-por-Sharpe-OOS* de cada lead (o que a spec manda):
- **L1:** `tsmom_lb12m_vt10` — Sharpe OOS −0.21 (o melhor dentre 12
  losers).
- **L2:** `gayed_ema100_L3_off_gld` — Sharpe OOS +2.29, CAGR 129%,
  MDD −30%.
- **L3:** `XLF` (AFML triple-barrier) — Sharpe OOS +1.21, CAGR 2.5%,
  MDD −0.8%.

Escalei cada um para 15% vol anualizado usando a std *do IS* apenas
(sem look-ahead), fiz equal-weight, rodei IS/OOS/FWD + as 5 portas do
framework V2.

## O que encontramos

| Dimensão | Valor | Passa? |
|----------|-------|:------:|
| PBO (4-col matrix) | 0.000 | ✅ |
| DSR p-value | 0.0014 | ✅ |
| Walk-forward | 7/8 (MDD 23.78%) | ✅ |
| Bootstrap 99.9% CI low | 0.489 | ✅ |
| OOS Sharpe | **1.856** | ❌ (< 2.0) |
| OOS CAGR | **16.14%** | ❌ (< 30%) |
| OOS MaxDD | −8.44% | ✅ |
| IR vs SPY | **0.106** | ❌ (< 0.5) |
| FWD Sharpe | 0.594 | ✅ |

Passa todas as portas estatísticas de robustez (PBO, DSR, WF,
bootstrap) mas **não passa três critérios de winner duros**:
retorno, Sharpe e IR contra o benchmark. O blend tem risco baixo e
é robusto — mas dilui demais o alpha.

## Por que dilui

Os pesos implícitos após vol-target:
- L1 TSMOM → 29% do risk budget
- L2 Gayed → **4.9%** (!) do risk budget
- L3 AFML XLF → 66% do risk budget

L3 domina porque tem vol quase zero (o filtro meta joga fora 95% dos
eventos, então a sequência é quase uma reta com pequenos pulos). Ao
escalar para 15% vol, L3 recebe um múltiplo enorme. L2, que é o único
alpha de verdade, fica com 5% de peso — insuficiente pra sua
Sharpe 2.29 sobreviver no blend.

Isso é exatamente o que AFML ch.16 e Carver ch.9 dizem: risk-parity
melhora quando **todas as pernas têm edge positivo**. Se metade delas
é ruído ou perdedora, a matemática reverte o benefício.

### Diagnóstico extra — 2-leg (L2 + L3, drop L1 negativo)

Pra checar se o problema é só L1: fiz um blend alternativo só com
L2+L3 (deixa L1 de fora porque é OOS-negativo).

- Sharpe OOS: **2.021**
- CAGR OOS: **25.77%**
- MDD OOS: −12.66%
- WF: 8/8
- IR vs SPY: **0.574**

Quase lá, mas ainda CAGR < 30% (falha winner criterion). E o mais
importante: **metade do CAGR do L2 standalone foi para o lixo** em
troca de −17pp de MDD. Não vale a pena trocar o L2 original por isso.

## Conclusão

O winner Plano A continua sendo **`gayed_ema100_L2_off_gld`** sozinho
(Sharpe 2.285, CAGR 79.14%, MDD −21.02%, já registrado em
`winners_short_hold:` em 2026-04-19 00:20 pela iter 43 da V2-L2).
Nenhum blend Carver sobre L1+L2+L3 melhora esse resultado nas métricas
que V2 exige.

V2-L4 é atomic: 1 iter, verdict dado. O lead seguinte é V2-L5
(equity pairs, Kalman dynamic beta sobre 6 pares pré-selecionados).

## Próximo passo

Iter 59 (bootstrap V2-L5 registry para 6 pairs + sweep-tickers).

## Referências

- `reports/phase3_5a_v2/v2_l4_carver_risk_parity/AGGREGATE.md`
- `reports/phase3_5a_v2/v2_l4_carver_risk_parity/AGGREGATE.json`
- `reports/phase3_5a_v2/v2_l4_carver_risk_parity/carver_rp_blend_daily_returns.parquet`
- `specs/phase_3_5a_v2.md` §4 V2-L4
- `jornada/2026-04-19-0020-phase3.5a-v2-L2-gayed-transported-PASS.md` (winner base)
- `[systematic_trading, ch.8-9]` — Carver risk budgeting
- `[advances_fin_ml, ch.16]` — AFML portfolio construction
