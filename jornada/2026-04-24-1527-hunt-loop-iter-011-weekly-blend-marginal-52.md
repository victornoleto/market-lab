# Hunt loop iter 011: weekly rebalance 3-leg blend dá 52/100 MARGINAL, Kill #1 + #3 TRIGGERED

**Data:** 2026-04-24 15h27
**Contexto:** Iteração 011 do `studies/strategy_hunt_loop/` (mandate §1
segue 100% Plano C; hunt loop é pesquisa em background).

---

## Pergunta da iteração

Depois que iter 008 (2-leg SPY+TLT) e iter 010 (3-leg SPY+TLT+GLD)
empataram em 74/100 com DSR como único killer, a memória do loop
sugeria três caminhos pra quebrar o teto: (F) mudar o timeframe
(weekly rebalance), (C) meta-labeling, (B') overlay assimétrico.
Priorizou-se **Option F** por ser a mais barata de testar e ter o
ataque teórico mais direto ao DSR.

A tese era: weekly rebalance (a) alinha com o regime canônico
mensal do Moreira-Muir 2017, (b) reduz a penalidade DSR porque
menos observações × mesmo n_trials cumulativo, (c) corta turnover
e custo de transação.

## O que aconteceu

**Todas as três pernas da tese caíram empiricamente**:

1. **Sharpe regrediu em TODOS os 3 datasets** vs iter 010 daily.
   - edu 0.989 → 0.942 (−0.047)
   - spy 1.040 → **1.019** (−0.021)
   - ndx 0.995 → **0.898** (−0.097)

2. **MDD explodiu +10 a +14 pp** (o achado mais contundente):
   - edu 33.67% → 47.19%
   - spy 33.67% → 47.19%
   - ndx 37.43% → 48.99%

   Causa estrutural: o mecanismo `target_var² / σ²_port` precisa de
   **cadência diária** pra reagir a mudança de regime de vol. No
   timeframe semanal, qualquer mudança de regime entre sextas
   acontece **inteiramente sem hedge dentro da semana**. A
   cap-hit frequency subiu de 86% → 95% — a restrição de vol-target
   deixou de ser efetiva na maioria dos bars.

3. **DSR ficou PIOR, não melhor** (a conjectura teórica também
   falhou):
   - pior p-value edu/spy/ndx: 0.368 (iter 010) → **0.515** (iter 011)
   - Motivo: a fórmula DSR avalia PSR em benchmark
     `E[SR_max] ≈ a × √(1/(T-1))`. Reduzir T de ~4280 pra ~880
     infla o benchmark em √5 ≈ 2.24×. O Sharpe periódico observado
     também cresce em √5× (porque anualização muda de √252 pra √52),
     então o efeito de primeira ordem se cancela. Efeitos de segunda
     ordem (margem mais estreita no G6, artefatos de autocorrelação
     semanal) pioram o p-value marginalmente.

4. **Turnover aumentou**, não diminuiu: 10/yr por perna (daily) →
   **13.6/yr por perna** (weekly). Motivo: com lookback de 4 semanas,
   cada rebalance move os pesos ~25%/step (vs ~5%/step no daily).
   Passou-se de rebalanceamentos freqüentes e pequenos pra
   infreqüentes e grandes.

5. **Correlação SPY-TLT é MAIS FRACA em escala semanal** (−0.24)
   vs diária (−0.30). O "flight-to-quality" stock-bond é concentrado
   em dias específicos de stress e suaviza no compound semanal. A
   diversification return — `[risk_parity, p.5, p.109-110]` — cai.

## Score e winner conditions

| métrica | iter 010 | iter 011 | Δ |
|---|---|---|---|
| Score total | 74/100 | **52/100** | **−22** |
| Tier | 🥈 PROMISING | 🥉 **MARGINAL** | regressão |
| Winner conditions | 4/5 | 3/5 | −1 |
| Sharpe edge 2/3+ datasets | ✅ | ❌ (só edu) | regressão |
| Gates cross-dataset | ✅ | ✅ | held |
| DSR p<0.05 | ❌ | ❌ (pior) | worse |
| CAGR floor 2/3+ | ✅ | ✅ | held |
| MDD ceiling 2/3+ | ✅ (3/3) | ❌ (só edu) | regressão |

**Kill criteria pré-committed**:
- ✅ Kill #1 TRIGGERED (regressão de Sharpe em AMBOS slots reais)
- ✅ Kill #3 TRIGGERED (score 52 < 70)
- ❌ Kill #2 (CAGR < 0.75 × bench 2+) — 3/3 passam 0.8× floor
- ❌ Kill #4 (qualquer dataset < 5/7 gates) — min é 5/7
- ❌ Kill #5 (G7 xlib > 3pp) — max 0.20 pp

## Lição (vai pra BASE_MEMORY)

**Vol-managed variance-targeting REQUER cadência diária — NÃO é
cadence-agnostic.** O edge vem da reação rápida a mudanças de regime
de vol. Cadências mais lentas surrenderam a habilidade de de-lever
antes que o regime compounde em drawdown. Isso é
**estruturalmente diferente** de momentum cross-sectional
(Jegadeesh-Titman 1993 funciona mensalmente) ou value (funciona
anual): **variance-scaling tem uma escala de tempo intrínseca ao sinal**.

**Corolário**: o empate iter 008 = iter 010 = 74/100 **NÃO é um
teto cadence-independent** — é um **teto específico ao daily**. Semanal,
mensal, trimestral cada um marca progressivamente pior. A blend family
tem um teto daily de 74/100 e cadências mais lentas caem.

**Corolário 2 para o DSR**: ataques ao teto DSR via "reduzir n_trials
/ reduzir T via sampling mais lento" são **estruturalmente
indisponíveis** pra variance-targeting blends. A fórmula DSR cancela
esse trade em primeira ordem. Pra quebrar DSR precisa aumentar o
Sharpe observado (via informação ortogonal) — não dá pra reduzir
o benchmark.

## Dead ends novos

Adicionado à `DEAD_ENDS.md`:
- Weekly (ou mais lento) rebalance de vol-managed multi-leg blend
- Qualquer ataque DSR baseado em "reduzir T via sampling mais lento"
  pra mecanismos variance-targeting

**Não re-testar com variações de param**: outros W-XXX cadência
(W-MON/W-WED), outros lookback (2/8/12 semanas), outros target_vol
(0.10/0.20). O gargalo é estrutural, não paramétrico.

## Próxima iteração (iter 012)

Duas direções remanescentes, AMBAS preservam cadência diária:

1. **Option B' (pick-first)**: overlay assimétrico T10Y3M na blend
   iter 008 — sinal raw (≤ 5d smoothing) + haircut na PERNA DE EQUITY
   SOMENTE (bond mantém peso full). Endereça os dois modos de falha
   do iter 009 (21d EMA destruiu lead-time, haircut simétrico perdeu
   flight-to-quality). Implementação barata ~30min, uplift esperado
   +0.03-0.08 Sharpe.

2. **Option C**: meta-labeling AFML ch.3 na blend iter 008. Modelo ML
   secundário prediz profitability bar-a-bar usando features cross-
   sectional / macro que a blend não vê. Única direção que adiciona
   informação estruturalmente independente do regime de vol. Custo
   alto ~2-3h, uplift esperado +0.20-0.30 Sharpe.

Backlog: Option E (EBP macro overlay), Option G (return-stacked NTSX
rotation), HMM regime-switching.

## Estado do hunt loop

- total iterations: 11
- cumulative n_trials: 4249
- top-K inalterado (iter 011 score 52 está abaixo do iter 005 ranking #5 com 59)
- pytest baseline: 720 tests passing (8 novos TDD specs iter 011 todos verdes)
- mandate §1: **unchanged, 100% Plano C maintenance mode**. Hunt loop
  continua em background; iter 011 é mais uma confirmação de que
  alpha hunting daily em 3-leg blend tem teto estrutural de 74/100.

**Citação primária**: `[systematic_trading, p.144, p.170-171, ch.11]`
+ `[risk_parity, p.10-11, ch.1]` + Moreira-Muir 2017 *JoF* 72(4)
DOI 10.1111/jofi.12513.

Final report completo em
`studies/strategy_hunt_loop/iterations/011-2026-04-24-1527-weekly-three-leg-blend/final_report.md`.
