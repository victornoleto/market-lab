# Probe HappyForex — edge real na amostra, mas blackout de 5 anos impede verificação

**Data**: 2026-05-01 01h05
**Vertente**: studies/myfxbook_reverse_engineering (1ª iteração)
**Tier**: PARTIAL PASS — gates 3/4 ✅ na amostra, gate 4 ❌ por sample-size,
mas dados pós-2021-06 inexistentes
**Strategy alvo**: MyFxBook id 1407880 — "OLD Happy Market Hours v2.3.1"
do vendor `happyforex.de`

## O que foi feito

Usuário pediu pra "reviver Plano A" (DORMANT desde 2026-04-23) usando
reverse-engineering de um perfil MyFxBook que parecia promissor, com
entrega de cookies de sessão pra acessar trade history privado. Sistema-
alvo: `OLD Happy Market Hours v2.3.1`, 7,8 anos de track record demo,
+4 550% gain reportado, DD 10,16%.

Probe contido sob mandate §3 (multi-asset obrigatório, gates §2.4
hard-block) com kill-switches K1-K5 explícitos pra abortar cedo se
sinal de fraude/martingale aparecer. Capital permanece 100% Plano C
durante o probe.

## Achados (de fora pra dentro)

### Identidade do perfil — vendor de EAs, não trader
- HappyForex é loja de Expert Advisors (Alemanha), motto "EAs, VIP
  Offers, Promotions, Bonus"
- 10+ produtos comercializados, stack auto-declarado: "Scalping, Trend,
  Correlation, Grid, Martingale, Hedge, News" — lista canônica do que
  o knowledge base do projeto identifica como armadilha
- Múltiplos sistemas com DD reais 62-74% no catálogo (martingale grid em
  blowup terminal)

Mas o sistema escolhido pelo usuário (Market Hours v2.3.1) tem DD apenas
10% — incompatível com martingale. Mereceu probe.

### K1 (martingale) — não triggered
- 3 305 trades scrapeados (170 páginas via Playwright + cookies do
  usuário; cf_clearance bypassed pelo browser context)
- Lots crescem 0,25 → 17 ao longo de 8 anos = % risk sizing
  proporcional ao equity (compound growth +4 550%)
- 0 trades com lot ≥ 1,7× anterior em janela < 24h
- Per-month max/median ratio: 1,06 — lots dentro do mesmo mês são
  basicamente idênticos
- Critério inicial P95/P50 = 4,03 era falso positivo (refletia
  equity-scaling, não martingale)

### Strategy fingerprint (alta confiança)
- **Tempo:** 99,97% das entradas em 23:00-01:00 UTC, peak 23:55-00:05
  (Asian session opening / NY post-close window)
- **Universe:** 6 pares — GBPUSD, USDCAD, EURUSD, EURCHF, USDCHF, EURGBP
- **Exit:** 94,1% time-based; SL hit 5,8%, TP hit 0,1% (TP +100 pips
  nunca disparou em 8 anos)
- **Sizing:** proporcional ao equity, sem martingale
- **Hold time:** P50 1h, P95 3,2h, P99 4,8h — todos intraday
- **Direction:** signal-driven mas não-determinado sem 1m OHLC (54% all-
  same-direction quando há 2+ trades por sessão-pair, 46% mixed)

### Edge real, mas com decay
- Full-sample annualized Sharpe **2,51** após cost model Pepperstone
  Razor 2025
- DSR p < 0,0001 (gate 2 PASS)
- WF 7/8 windows positivas (gate 3 PASS) — só window 7 (2019-10 →
  2020-08, COVID) negativa
- Bootstrap full-sample 99,9% CI: [+1,07, +4,01] (gate 6 PASS)
- **Mas:** OOS single-block (last 12mo, 2020-06 → 2021-06): Sharpe 1,89
  com bootstrap 99,9% CI [-1,67, +8,11] — lower bound NEGATIVO
  (gate 4 FAIL — estatístico, não estrutural)

### Yearly decay reveladora
| Year | gross avg pips | net pips | sharpe net |
|---|---:|---:|---:|
| 2016 | 4,03 | **2,64** | **0,25** ← peak |
| 2018 | 3,11 | 1,69 | 0,19 |
| 2019 | 1,43 | 0,26 | 0,04 |
| 2020 | 1,20 | **0,04** | **0,00** ← morte
| 2021 | 1,38 | 0,25 | 0,04 |

E vendor classificou esse sistema como "OLD" — substituído internamente
no catálogo provavelmente porque parou de funcionar na regime atual.

### Cost economics — USDCAD net-negativo na Pepperstone
- USDCHF +3,05 pips/trade líquido ✓
- EURCHF +2,93 ✓
- GBPUSD +1,75 ✓
- EURGBP +0,55 marginal
- EURUSD +0,43 marginal
- **USDCAD −0,10** — perde dinheiro mesmo em backtest favorável (cost >
  gross). Strategy precisa filtrar pair pra ser viável live

## Verdict misto

A pergunta original era **"é possível reverse-engineer?"** — sim, parcialmente.
Conseguimos timing/exit/sizing/universe com altíssima confiança; falta
o direction signal (precisaria de 1m OHLC).

A pergunta secundária implícita **"vale ativar Plano A?"** — não com os
dados disponíveis. O gate 4 §2.4 falha por amostra OOS pequena demais
pra confiança 99,9%, e há **5 anos de blackout (2021-07 → 2026-05)** que
não temos como verificar.

## Recomendação ao usuário (Opção 2 do decision memo)

Em vez de aceitar Folclore puro (Opção 1) ou continuar probe replicador
+ transferability sem resolver o blackout (Opção 3), recomendei:

**Setup paper-trading 90 dias na MT5 demo Pepperstone** com a regra
parcial reverse-engineerada (5 pares filtrados, 23:00-01:00 UTC, time-
based exit, % risk sizing). Critério de continuação após 90d: net pips
≥ 1,0 + win rate ≥ 65% + 0 dias com -10% drawdown.

Custo: 1-2 dias setup MQL5 EA + monitoring. 90 dias rodando sozinho.
Resolve o blackout question diretamente. Capital permanece 100% Plano C.
Se passa, vai pra Phase 4.0 paper formal. Se falha, Folclore.

## Decisão pendente

Aguardando sign-off do usuário entre as 3 opções (memo completo em
`studies/myfxbook_reverse_engineering/2026-05-01-happy_market_hours_v231/decision_memo.md`).
EDA detalhado: `reports/04_eda_summary.md`.

## Por que isso importa pro projeto

Antes deste probe, "Plano A DORMANT" significava manter infra retida e
esperar literatura/regime nova (mandate §1). Este episódio mostra um
caso intermediário: literatura externa existe (track record público de
8 anos com gates DSR/WF passando), mas verificação atual está bloqueada
por blackout. A resposta natural é o **paper-trading como gate empírico
forward** — mais barato que probe completo, mais informativo que Folclore
prematuro. Pode virar um padrão pra futuros probes externos.
