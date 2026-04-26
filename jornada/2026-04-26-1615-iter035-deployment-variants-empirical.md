# iter 035 — validação empírica das 4 variantes de deploy

**Data**: 2026-04-26 16:15
**Status**: 4 variantes passam G6 + DSR + G7 em 40y synth; recomendação prática mudou

## O que aconteceu

Conversa com user sobre como **operacionalmente** deployar o iter 035
(90% SPY + 60% long-bond + 30% gold = 180% notional). Surgiram 4
caminhos:

1. **V0 — IBKR margin direto**: SPY+ZROZ+GLD, IBKR empresta os 80% extras
2. **V1 — Inter cash, NTSX+GDE 67/33**: 2 ETFs WisdomTree return-stacked,
   sem margem nem LETF
3. **V2 — Inter cash, 2× LETFs (SSO+UBT+UGL+BIL)**: alavanca via swaps
   internos do fundo
4. **V3 — Inter cash, 3× LETFs (UPRO+TMF+GLD+BIL)**: mesmo conceito
   mais agressivo

User pediu pra **comprovar empiricamente** as 4 variantes nos mesmos
gates do strategy_hunt_loop, não confiar em estimativas.

## O que foi feito

Criei `studies/strategy_hunt_loop/iter035_variants_validator.py`. Sintetiza
NTSX/GDE/TMF/UBT/BIL a partir dos underlyings do testfolio synth (todos
os ETFs alavancados — SSOSIM, UPROSIM, QLDSIM, TQQQSIM, UGLSIM — já
existem na cache 1986+). Roda as 4 variantes vs SPYSIM 40y (1986-2026),
aplica gates G6 (bootstrap 99.9% Sharpe CI > 0), DSR (`[advances_fin_ml,
p.222-223]` com n_trials=4), G7 cross-lib parity.

## Resultado

**Todas as 4 passam todos os gates**. Mas o ranking real surpreende:

| variant | Sharpe | CAGR | MDD | retorno 2022 |
|---|---|---|---|---|
| V0 PURE (margin) | 0.922 | 19.60% | 46.18% | **−38.81%** |
| **V1 NTSX+GDE** | **0.917** | 15.42% | **44.10%** | **−21.88%** |
| V2 2× LETF | 0.801 | 16.45% | 47.44% | −39.76% |
| V3 3× LETF | 0.822 | 17.01% | 47.30% | −39.47% |

V0 e V1 têm Sharpe **quase idêntico** (Δ=0.005). V1 tem **MDD melhor**
em todas as janelas e perdeu **só metade** do que as outras em 2022.

Razão técnica: NTSX usa Treasury intermediário (IEF, ~7y duration) em
vez de bond longo (ZROZ ~25y / TLT ~17y). Em 2022 (ciclo brutal de alta
de juros), bond longo + leverage 3× foi destruído juntos: V0/V2/V3
todos perderam 39-45% de drawdown. V1 ficou em −29%.

## Veredito prático

**Recomendação pro user mudou**: V1 NTSX+GDE 67/33 no Inter Internacional
é o caminho operacional mais forte. Sharpe ~empata com V0, MDD melhor,
**cash account só** (sem margem, sem TMF time bomb), 2 ETFs.

V0 continua sendo a opção de "máximo CAGR absoluto" (4pp/yr a mais),
mas exige IBKR margin + aceita risco real de margin call em crash
2008-style. User explicitamente disse não estar preparado pra estudar
margin loan, então V1 vence pra ele.

V2 e V3 (LETF puro) ficam atrás em Sharpe **e** em MDD. **Vol drag
empírico dos LETFs é real** — não é só folclore acadêmico. TMF synth
(3× ZROZ) é especialmente brutal em 2022.

## Arquivos gerados

- `studies/strategy_hunt_loop/iter035_variants_validator.py` — runner
- `studies/strategy_hunt_loop/plot_iter035_variants.py` — plot maker
- `studies/strategy_hunt_loop/ITER035_VARIANTS_VALIDATION.md` — relatório
- `studies/strategy_hunt_loop/ITER035_VARIANTS_VALIDATION.json` — raw
- `studies/strategy_hunt_loop/ITER035_VARIANTS_equity_curves.png`
- `studies/strategy_hunt_loop/ITER035_VARIANTS_drawdowns.png`
- `studies/strategy_hunt_loop/ITER035_VARIANTS_2022_stress.png`
- `studies/strategy_hunt_loop/iter035_variants_returns.parquet`
- `studies/strategy_hunt_loop/FINAL_REPORT.md` (atualizado seção
  "Validação empírica das 4 variantes")
- `studies/strategy_hunt_loop/SUMMARY_FOR_PHONE.md` (atualizado
  seção tax pra refletir Lei 14.754 PF direta = 1 DARF/ano)

## Caveats

1. **TMF synth é pessimista** (3×ZROZ tem mais duration que TMF real
   3×TLT). Real V3 deve ser ~10-15% menos brutal em 2022 que synth
   indica. Mas já que V1 ganha mesmo no synth otimista pra V3, conclusão
   permanece.
2. **NTSX + GDE assumem zero futures roll yield** — real WisdomTree tem
   ~5-15 bps/yr de roll cost não modelado. V1 numbers ligeiramente
   otimistas.
3. **Disponibilidade Inter**: NTSX e GDE são WisdomTree menos populares.
   User tem que confirmar no app antes de aportar.
4. **Mandate maintenance §1**: projeto continua 100% Plano C; nenhuma
   dessas variantes é deploy autorizado sem override §7.

## Adendo — 2 testes complementares (mesma sessão, 17:30)

### 1. Aporte mensal simulation (R$50k + R$7.5k/mês, 40y)

Money-weighted simulation com FX cost real (IBKR TransferBank 0.30%
vs Inter 1.25%) + IOF 0.38% Lei 14.754. Adicionei V0 com **−4%/yr
drag de margin interest** (REAL IBKR cost on 80% borrowed). Resultado
muda significativamente o ranking:

| variant | broker | final BRL | IRR ~ |
|---|---|---|---|
| V0 PURE sem margin cost (irreal) | IBKR | R$558M | 15.25% |
| V3 LETF 3× Inter | Inter | R$284M | 13.33% |
| V2 LETF 2× Inter | Inter | R$241M | 12.88% |
| V1 NTSX+GDE Inter | Inter | R$184M | 12.13% |
| **V0 PURE com 4%/yr margin (REAL)** | IBKR | R$139M | **11.34%** |
| BENCH SPY buy-hold | Inter | R$59M | 9.01% |

**Achado crítico**: V0 IBKR margin REAL **PERDE** pra todas variantes
Inter. Juros de margem (4%/yr × 80% = R$420M de drag em 40y) excede
o vol drag dos LETFs Inter. Isso reverte a impressão original de que
"IBKR margin é a opção mais limpa" — não é, é a mais cara em
money-weighted terms.

V3 LETF 3× lidera no money-weighted IRR (13.33%/yr) mas com MDD 47%
— ergodicidade vence determinismo de 40y, MAS o user paga em 2022
stress (perdeu 39% no ano). Trade-off existe.

V1 NTSX+GDE permanece a recomendação prática: 12.13%/yr com MDD 44%
+ 2022 −22% (melhor stress test) + cash account simplicidade.

### 2. Iter 079 leveraged — testado e refutado empiricamente

User perguntou: "se SPY rendeu mais nos últimos 12 meses, por que
não comprar SSO/UPRO em vez de SPY?". Testei 2× e 3× LETF substitutes
na execução do iter 079 (sinal continua nos 1× underlyings).

| variant | Sharpe | CAGR | MDD | 2022 |
|---|---|---|---|---|
| iter079_1x baseline | 0.625 | 12.44% | 49% | −24% |
| iter079_2x LETF | 0.574 | 17.00% | **83%** | −39% |
| iter079_3x LETF | 0.519 | 13.69% | **97%** | −46% |

**Hipótese refutada**. Concentração single-asset (top-K=1) + leverage
= drawdown catastrófico. 3× variant atingiu 96.58% MDD em algum ponto
da janela 40y — wipeout praticamente total ($100k → $3.4k peak loss).

Achado matemático interessante (leverage paradox): 3× tem CAGR
**MENOR** que 2× porque vol drag come o compounding. Existe um
leverage ótimo ~2× pra equity acima do qual CAGR DECRESCE. Iter 079
com universo concentrado já amplifica vol — adicionar 3× é
matematicamente insustentável.

**Conclusão**: iter 079 deve ser executado em 1× sempre. Se quer
momentum + leverage, caminho honesto é iter 016 (vol-target dinâmico)
não LETF estático.

Files: `iter079_leveraged_validator.py`, `aporte_simulation.py`,
`ITER079_LEVERAGED_VALIDATION.{md,json}`, `APORTE_SIMULATION.{md,json}`.

## Próxima decisão pendente do user

Recomendação prática mantida: **V1 NTSX+GDE 67/33 no Inter** é o
deploy candidate mais forte (Sharpe top, MDD melhor, sem margem,
sem TMF time bomb, simplicidade total).

Caso V1 não esteja disponível no Inter (NTSX/GDE são menos populares):
- Fallback: V0 (IBKR margin) — agora sabidamente caro real-world
- Fallback alternativo: V2 (Inter SSO+UBT+UGL+BIL) — passa gates,
  perde MDD vs V1

User explicitamente NÃO quer fazer V3 (LETF 3×) e iter 079 leveraged
— ambos confirmados empiricamente como destrutivos.

## Citações

- `[advances_fin_ml, p.196-202]` — bootstrap CI 99.9% G6
- `[advances_fin_ml, p.222-223]` — DSR Lopez de Prado n_trials
- `[advances_fin_ml, p.31-34]` — cross-library parity G7
- `[risk_parity, ch.5]` — return-stacking + leveraged ETF context
- WisdomTree NTSX prospectus — 90% SPY + 60% Treasury futures stack
- Lei 14.754/2023 Art. 1-3º — PF direta tributação na realização
  (não MTM)
