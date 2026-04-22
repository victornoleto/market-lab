# [SWING BROKER] D2 — MA Regime Gayed: agregado DEAD END (0/3 pass)

**Data:** 2026-04-21 | **Lead:** D2 | **Iter:** 6 | **Verdict:** DEAD END

O lead D2 testou o filtro de regime MA canônico do Gayed
`[leverage_for_the_long_run, p.13, p.16]` sobre os três portfolios-alvo —
TQQQ (3× QQQ), UPRO (3× SPY), e EW 50/50 UPRO+TQQQ — com 6 configurações
(SMA200/EMA100 × cash/TMF/GLD) na janela máxima disponível (2010-02-11 →
2026-04-17, 16.2 anos). Validação cross-lib (bt + yfinance independente)
em todos os 18 runs.

## Resultado: 0 de 18 runs passaram todos os 5 gates

| Ticker | Melhor config | Sharpe bruto | Sharpe_net | MaxDD% | Calmar | Pass? |
|--------|---------------|-------------|------------|--------|--------|-------|
| TQQQ | sma200_gld | 0.918 | 0.780 | -60.3 | 0.608 | **NÃO** |
| EW_UPRO_TQQQ | sma200_gld | 0.909 | 0.773 | -56.3 | 0.559 | **NÃO** |
| UPRO | sma200_gld | 0.807 | 0.686 | -53.2 | 0.458 | **NÃO** |

SPY B&H (referência): CAGR_net 10.38%, Sharpe 0.756, MaxDD -34.1%

## O que aprendemos

**O filtro funciona — o bloqueador é o imposto.** PBO ≈ 0.115 (longe do limite 0.5), WF 7/8,
DSR_p < 0.011 para TQQQ e EW. O regime MA reduz o MaxDD de ~73% (buy-and-hold TQQQ) para
~53–60%. O problema é o IR BR 15%: converte Sharpe bruto 0.918 em Sharpe líquido 0.780 — a
barreira é 0.800. O gap é de apenas **0.020 pontos** no melhor caso (TQQQ sma200_gld), mas o
gate não tem ceder. "Quase" não passa.

**TMF está fora definitivamente.** A terceira perna bonds-3× gerou MaxDD de -82% a -87% em
2022 (ciclo de alta de juros). Estruturalmente incompatível com portfolios 3× leverage
`[leverage_for_the_long_run, p.60]`.

**TQQQ > UPRO.** Em todos os 18 runs, TQQQ supera UPRO. O NASDAQ-100 é o ativo-longo de 3×
preferível para esta família de estratégia. UPRO ficou fora de próximos leads.

**Stress forward positivo.** Mesmo sem passar os gates, a janela de stress forward
(trimestre mais recente) foi positiva para sma200_gld: TQQQ +0.38, EW +0.26, UPRO +0.11.
Isso indica que o edge não deteriorou recentemente — o problema é o custo tributário,
não a quebra do sinal.

## Próximo: D3 Donchian breakout em TQQQ

D3 testa uma família de sinal diferente: breakout de canal de Donchian
`[trading_systems_methods, p.353]`, `[stocks_on_the_move, p.81]`. O universo é TQQQ-first
(UPRO skip). Se D3 produzir gross Sharpe ≥ 0.94 (o suficiente para Sharpe_net ≥ 0.80 após
15% IR), seria um candidato.

→ Relatório completo: `reports/phase_3_5d/d2_ma_regime_gayed/AGGREGATE.md`
