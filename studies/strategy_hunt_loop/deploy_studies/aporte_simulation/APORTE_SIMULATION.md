# Aporte mensal simulation — $10k initial + $1.5k/month over 40y

Generated: 2026-04-26T21:51:57.962036

Parameters: BRL 50,000 initial + BRL 7,500/month, USD/BRL fixed at 5.00, window 40.3y (1986-01-03 → 2026-04-17).

## Cost structures

| broker | FX spread | IOF | fixed fee/aporte |
|---|---|---|---|
| Inter | 1.25% | 0.38% | $0.00 |
| IBKR_TransferBank | 0.30% | 0.38% | $2.00 |

## Results (sorted by final BRL)

| variant | broker | total invested | final BRL | multiplier | IRR ~ | FX cost % |
|---|---|---|---|---|---|---|
| `V0_PURE_no_margin_cost` | IBKR_TransferBank | BRL 3,672,500 | **BRL 558,954,302** | 152.20× | 15.25%/yr | 0.81% |
| `V3_LETF_3x_UPRO_TMF_GLD_BIL` | Inter | BRL 3,672,500 | **BRL 284,180,683** | 77.38× | 13.33%/yr | 1.63% |
| `V2_LETF_2x_SSO_UBT_UGL_BIL` | Inter | BRL 3,672,500 | **BRL 241,487,049** | 65.76× | 12.88%/yr | 1.63% |
| `V1_NTSX_GDE_67_33` | Inter | BRL 3,672,500 | **BRL 184,460,780** | 50.23× | 12.13%/yr | 1.63% |
| `V0_PURE_with_4pct_margin_drag` | IBKR_TransferBank | BRL 3,672,500 | **BRL 139,161,287** | 37.89× | 11.34%/yr | 0.81% |
| `BENCH_SPYSIM_buyhold` | Inter | BRL 3,672,500 | **BRL 59,205,856** | 16.12× | 9.01%/yr | 1.63% |

## Key observations

- **V1 NTSX+GDE vs SPY buy-hold (mesmo broker)**: V1 termina com **BRL 125,254,924** (+211.6%) a mais que SPY puro. Mesma cesta de cost (Inter 1.25% FX), V1 entrega ~12.1%/yr vs SPY 9.0%/yr.
- **V0 com margin cost honesto vs V1**: V0 entrega -24.6% vs V1 — diferença real após cobrar juros de margem 4%/yr sobre os 80% emprestados. (11.3%/yr vs 12.1%/yr).
- **Custo real do IBKR margin loan ao longo de 40y**: BRL 419,793,015 (75.1% do balance idealizado). Esse é o que IBKR cobra pra te emprestar 80%.

## Caveats

1. **Tax NÃO aplicado** — buy-and-hold investor com aportes mensais e sem vendas tem zero realização durante acumulação; Lei 14.754 PF direta defere tax até venda eventual (décadas no futuro). Pra estratégias com rotação (iter 079, iter 016 daily), haveria tax anual sobre realizações.
2. **USD/BRL fixo em 5.00** — desvalorização BRL não modelada. Real-world: BRL desvaloriza ~5-10%/yr historicamente, o que **aumenta** o BRL final (você compra USD barato no início e ele vale mais BRL no fim). Simulação é conservadora nesse aspecto.
3. **V0 sem margin cost é IRREALISTA** — kept como upper bound teórico. Use V0_with_margin pra comparação justa com V1.
4. **40y de aportes BRL 7.5k/mo cumulativo = BRL 3.6M** — magnitude bem acima do que single user provavelmente faz. Resultados escalam linearmente — pra ver perfil $10k+$500/mo, divide tudo por 3.
