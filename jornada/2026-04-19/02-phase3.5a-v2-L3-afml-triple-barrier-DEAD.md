# [SHORT-HOLD CFD] Phase 3.5a-V2 L3 — AFML triple-barrier + meta-label: DEAD END

**Data:** 2026-04-19 01:15
**Fase:** Phase 3.5a-V2 (Plano A LAST ATTEMPT)
**Lead:** V2-L3 — AFML triple-barrier + RandomForest meta-labeling
**Veredito:** ❌ DEAD END (0/12 tickers PASS 5-gate)
**Iters consumidos:** 45-57 (bootstrap + 12 sweep + aggregator)

## Resumo

A família AFML canônica (triple-barrier labeling + meta-filter
RandomForest sobre primary EMA-50 cross) foi transportada para 12
ETFs líquidos dos EUA (SPY/QQQ/EFA/GLD/TLT + 7 setores) com custos
reais Pepperstone Razor. **Nenhum ticker passa nenhum dos 5 gates
V2.** O melhor resultado do sweep é XLF com Sharpe OOS 1.21 e CAGR
apenas 2.50%/ano — uma ordem de magnitude abaixo do piso de 30%
exigido pelo spec §6.

A diagnóstica é clara e consistente com o próprio AFML
`[advances_fin_ml, p.50]`: meta-labeling **realça uma edge que já
existe, não fabrica edge**. O cross EMA-50 em ETF single-asset é
uma edge fina (~0.3-0.5 Sharpe bruto) que o filtro RF reduz ainda
mais em volume de trades (XLK ficou com 7 eventos OOS de 213 raw).
O resultado é precisão alta (MDD < 10% em 11/12 tickers, < 1% em
XLF) mas CAGR residual morre no custo (hold 6-14d × Razor RT
~11bps + swap × 20d ≈ 0.1% por trade). A matemática de Carver sobre
cost amortization `[systematic_trading, p.185-188]` explica o teto.

Aplicar alavancagem por cima não resolve: L=2 multiplicaria 2.5%
CAGR para ~5%, ainda muito abaixo de 30%, e arrebentaria o cap de
MaxDD 25% em XLE/XLY (que já estão em -9% e -13% unlevered). Spec
V2 §6 proíbe L>5.

Comparação com V2-L2 winner (`gayed_ema100_L2_off_gld` — Sharpe OOS
2.29, CAGR 79%, MDD -21%) confirma que o problema é o primário,
não o framework: um primário com edge real (regime rotation Gayed
SPY/GLD) sobe para 2.29 Sharpe; um primário fino (EMA-50 cross em
ETF isolado) fica ≤ 1.21 mesmo com meta-filter.

## Tabela cross-ticker (ranked by OOS Sharpe)

| Ticker | Window       | Sharpe OOS | CAGR OOS | MaxDD   | Med hold | Events taken | PASS |
|--------|--------------|-----------:|---------:|--------:|---------:|-------------:|:----:|
| XLF    | 2003-2026    | **1.213**  | 2.50%    | -0.76%  | 7.5d     | 14           | ❌   |
| XLI    | 2014-2026    | 0.945      | 3.55%    | -6.61%  | 8.5d     | 34           | ❌   |
| QQQ    | 2001-2026    | 0.924      | 2.46%    | -3.07%  | 6.5d     | —            | ❌   |
| XLE    | 2003-2026    | 0.789      | 6.90%    | -9.12%  | 9.0d     | —            | ❌   |
| EFA    | 2003-2026    | 0.645      | 2.16%    | -3.06%  | 6.0d     | —            | ❌   |
| XLU    | 2003-2026    | 0.445      | 3.18%    | -7.23%  | 14.0d    | 52           | ❌   |
| SPY    | 2001-2026    | 0.147      | 0.60%    | -6.76%  | 7.0d     | —            | ❌   |
| XLY    | 2014-2026    | 0.116      | 0.66%    | -13.22% | 6.0d     | 24           | ❌   |
| XLV    | 2014-2026    | 0.101      | 0.33%    | -5.87%  | 12.0d    | 17           | ❌   |
| XLK    | 2003-2026    | 0.000      | 0.00%    | 0.00%   | 7.0d     | 7            | ❌   |
| GLD    | 2004-2026    | -0.097     | -0.12%   | -2.17%  | 6.0d     | —            | ❌   |
| TLT    | 2002-2026    | -0.166     | -0.36%   | -4.14%  | 7.0d     | —            | ❌   |

## O que aprendi

1. Meta-labeling funciona como AFML promete — ele reduz MDD — mas
   exige um primário com Sharpe bruto > ~0.7 para entregar winner
   de produção. EMA-50 cross em ETF single não tem esse piso.
2. Hold 6-14d é zona de maior custo-por-$retorno no Pepperstone
   Razor (custo fixo round-trip ~11bps não amortiza com só 1-3
   trades/mês).
3. RF com `threshold p≥0.55` em 4 features simples é agressivo
   demais em ETFs defensivos (XLK 7 eventos OOS em 23 anos) — ou
   o sinal é realmente fraco, ou o threshold precisa ir para 0.50.
   Qualquer dos dois refuta o config como winner V2.

## Próximo passo

V2-L4 — Carver risk-parity multi-strategy blend. Pre-req original
("≥2 candidates com metrics não-NaN") está tecnicamente satisfeito
(V2-L2 entregou winner, V2-L3 entregou 12 configs com métricas
válidas mas nenhuma PASS). A próxima iter avaliará se L4 deve:
(a) blendar o V2-L2 winner com o melhor-Sharpe de V2-L3 (XLF),
(b) pular L4 e ir direto para V2-L5 (equity pairs daily), ou
(c) re-escopar L4 como robustness check do V2-L2 winner isolado.

## Referências

- Spec autoritativo: `specs/phase_3_5a_v2.md`
- Aggregate detalhado: `reports/phase3_5a_v2/v2_l3_afml_triple_barrier_meta/AGGREGATE.md`
- Registry: `reports/phase3_5a_v2/v2_l3_afml_triple_barrier_meta/registry.json`
- V2-L2 winner (contraste): `jornada/2026-04-19-0020-phase3.5a-v2-L2-gayed-transported-PASS.md`

## Citações

- `[advances_fin_ml, ch.3, p.45-54]` — triple-barrier + meta-labeling como filtro de precisão sobre edge existente.
- `[advances_fin_ml, ch.7, p.149-154]` — CPCV com embargo (correto aqui; não é a falha).
- `[systematic_trading, p.185-188]` — cost amortization por hold length.
- `[stocks_on_the_move, p.81]` — single-asset trend signal thinness.
