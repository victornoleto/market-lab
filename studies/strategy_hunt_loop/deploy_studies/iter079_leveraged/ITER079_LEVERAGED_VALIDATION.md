# iter 079 leveraged variants — momentum signal × LETF execution

Generated: 2026-04-26T18:16:01.221512

**Hipótese do user**: quando iter 079 escolhe SPY (1×) pelo momentum 12m, comprar SSO (2×) ou UPRO (3×) no lugar. Mesmo critério pra QQQ→QLD/TQQQ, TLT→UBT/TMF, GLD→UGL. EFA e AGG fallback ficam 1× por falta de LETF.

Sinal de momentum **idêntico** aos 3 variants — computado nos UNDERLYINGS (SPYSIM/QQQSIM/VEASIM/ZROZSIM/GLDSIM). Apenas a EXECUÇÃO muda.

Window: 1986-12-11 → 2026-04-17 (9912 bars). Lookback 12 meses, trans cost 5.0 bps.

## Substituições por variant

| asset (signal) | iter079_1x | iter079_2x | iter079_3x |
|---|---|---|---|
| SPY | SPYSIM | **SSOSIM** | **UPROSIM** |
| QQQ | QQQSIM | **QLDSIM** | **TQQQSIM** |
| EFA | VEASIM | VEASIM (no LETF) | VEASIM (no LETF) |
| TLT | ZROZSIM | **2×ZROZ synth** | **3×ZROZ synth** |
| GLD | GLDSIM | **UGLSIM** | GLDSIM (no 3×) |
| AGG fallback | BNDSIM | BNDSIM | BNDSIM |

## Benchmark

SPYSIM b&h: Sharpe 0.666 | CAGR 11.21% | MDD 55.14%

## Results (40y synth)

| variant | Sharpe (Δvs SPY) | CAGR (Δ) | MDD (Δ) | G6 99.9% CI | DSR p |
|---|---|---|---|---|---|
| `iter079_1x_baseline` | 0.625 (-0.041) | 12.44% (+1.22pp) | 49.47% (-5.67pp) | [0.19, 1.09] ✅ | 0.0011 ✅ |
| `iter079_2x_LETF_substitute` | 0.574 (-0.092) | 17.00% (+5.78pp) | 82.58% (+27.44pp) | [0.14, 1.04] ✅ | 0.0030 ✅ |
| `iter079_3x_LETF_substitute` | 0.519 (-0.147) | 13.69% (+2.48pp) | 96.58% (+41.44pp) | [0.09, 1.00] ✅ | 0.0081 ✅ |

## 2022 stress test

| variant | retorno 2022 | MDD 2022 |
|---|---|---|
| `iter079_1x_baseline` | -23.98% | -27.44% |
| `iter079_2x_LETF_substitute` | -39.28% | -42.37% |
| `iter079_3x_LETF_substitute` | -45.62% | -48.68% |

## Caveats

1. **TMF/UBT synth = 3×/2× ZROZ** — duration ~25y maior que TLT real ~17y → vol drag superestimado. Real performance levemente melhor.
2. **EFA stays 1×** em 2× e 3× — não há LETF EFA-targeted no synth (e mesmo no real-world, EFO 2× ProShares tem AUM mínimo). Quando momentum escolhe EFA, as 3 variantes performam IDENTICAMENTE nesse mês.
3. **GLD stays 1× em 3× variant** — não há 3× gold widely-available. Quando momentum escolhe GLD, iter079_3x performa como iter079_1x nesse mês.
4. **Sinal sempre nos 1× underlyings** — não testamos versão 'sinal nos LETFs', que poderia mudar quem ganha o ranking (LETF retorno cumulativo ≠ underlying × leverage por causa de daily reset).
