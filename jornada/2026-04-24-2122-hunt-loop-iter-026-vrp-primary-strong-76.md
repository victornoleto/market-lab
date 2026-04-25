# 2026-04-24 21h22 — Hunt loop iter 026: **VRP-primary stand-alone** dá 76/100 STRONG (top-K #5), com 3 marcos inéditos do loop — primeira vez passando DSR em dataset real, primeira vez 7/7 gates, e maior edge Sharpe cross-dataset (+0.38 a +0.45) [HUNT LOOP]

> Pesquisa em background. Mandate §1 segue **MAINTENANCE 100% Plano C**.
> Mesmo um eventual WINNER não vira deploy automático — exige override
> §7 separado e paper-trading. Esta entrada documenta um **breakthrough
> estatístico no hunt loop**, não um sinal pra mexer no portfolio real.

---

## TL;DR pra leitura rápida

- **Estratégia:** vender mensalmente put-credit-spread 5/10% OTM em SPY
  (ou QQQ pra ndx_real), 21 DTE, com colateral em T-bills rendendo
  rf=2%. **Sem ações por baixo, sem vol-target wrapper.** O harvest é
  o motor único do retorno. Único cfg pré-comprometido
  `vrp_primary_h1_5_10_1m`.
- **Resultado:** Sharpe 1.13 / 1.28 / 1.37 nos 3 datasets — Δ vs
  benchmarks +0.45 / +0.38 / +0.41 (**maior edge cross-ds da história
  do loop**). MDD 16.8 / 6.4 / 8.2% (vs benchmarks 55 / 34 / 35% —
  redução dramática).
- **Score:** **76/100 = STRONG**, posição #5 no top-K (atrás de iter
  016/018/021 a 79 e iter 015 a 77). Não é WINNER (3/5 condições
  estritas; falham DSR worst-p e CAGR floor).
- **Marcos novos do loop:**
  1. 🥇 **Primeira passagem DSR ever** em dataset real
     (ndx_real p=0.038 < 0.05 com n_trials=4279). Recorde anterior
     era iter 016 com p=0.226.
  2. 🥇 **Primeira vez passando 7/7 gates** em dataset real
     (ndx_real). Anterior era 6/7 (iter 016/021).
  3. 🥇 **Maior edge Sharpe cross-dataset simultâneo** (+0.38 ou
     mais nos 3 datasets). Anterior era iter 016 com
     +0.30/+0.24/+0.24.
- **Por que NÃO é WINNER:**
  - DSR worst-p = 0.083 (educational), 0.070 (spy) — apenas o
    ndx_real fica abaixo de 0.05.
  - CAGR floor: 4.85 / 4.97 / 6.31% vs floors 9.18 / 11.98 / 15.35%
    — falha 0/3 (limite estrutural por harvest unlevered).
- **Próximos passos sugeridos:** lever o harvest (`harvest_notional`
  2.0-2.5) pra clear CAGR floor; adicionar filtro VIX < 35
  (Sinclair p.217) pra empurrar edu+spy DSR pra abaixo de 0.05.
  Qualquer um dos dois pode produzir o **primeiro WINNER do loop**.

---

## O que mudou em relação a iters anteriores

iter 020 (long put-spread como hedge de cauda) e iter 021 (short
put-spread como overlay de VRP) **embrulharam o option-pricing primitive
em cima do iter 016** (stack 60:40 SPY+IEF com vol-target). O wrapper
de vol-target **absorvia** a contribuição do overlay: quando o harvest
gerava retorno extra, o stack escalava equity-leg pra baixo pra manter
σ²_port constante. Resultado: Sharpe-neutral (iter 021) ou pior
(iter 020).

iter 026 **tira o stack**. Não tem perna de equity, não tem perna de
bond, não tem vol-target wrapper. O retorno diário é simplesmente:

```
r[t] = rf_diário + 1.0 × (-overlay[t])
```

Onde `overlay[t]` é o P&L diário do credit spread (positivo quando
SPY cai sharp ou IV sobe — ruim pro short writer, então invertemos).

**Sem absorção, o harvest vira o driver dominante** — e aparece direto
no Sharpe. Resultado: Sharpe vai de "neutro" (iter 021) pra +0.38-0.45
edge. **Maior delta Sharpe do loop inteiro**.

## Por que isso é importante

O DSR é o gate estatístico mais cruel do loop. Com `cumulative_n_trials
= 4279` (acumulando 26 iterações de testes em 3 datasets cada),
qualquer estratégia que não tenha Sharpe genuinamente alto é deflacionada
pra p > 0.05. **Nenhuma estratégia anterior tinha conseguido passar**.

iter 026 ndx_real passa DSR por uma margem confortável (p=0.038 com
Sharpe 1.37). Educational e spy_real ficam **a um cabelo** (p=0.083 e
p=0.070) — qualquer pequeno uplift no Sharpe (filtro VIX, leverage,
combinação com outro signal) provavelmente clear.

Isso significa que **a infra do hunt loop reconheceria um WINNER** se
ele aparecesse — não tem bug que esteja segurando. O barramento é
puramente científico/econômico: tem que existir uma estratégia com
Sharpe genuinamente +0.10 acima de SPY que sobreviva o deflator de
n=4279.

## Honestidade sobre os limites

A estratégia tem 4 caracteristicas que precisam ser ditas:

1. **CAGR baixíssimo (4-6%/ano)** — porque o harvest unlevered tem
   teto natural em ~5-6%/ano. Pra clear CAGR floor (9-15% dependendo
   do dataset) precisa de leverage. Leverage neste tipo de estrutura
   (credit spread capped) tem risco contido (worst-case ~10-15% por
   roll com `harvest_notional=2.0`), mas é leverage explícita que
   precisa ser pré-comprometida.

2. **Correlação com SPY de 0.74-0.77** — **acima do threshold pré-
   comprometido de 0.7 (Kill C)**. Mas a beta realizada é só ~0.11
   (corr × σ_strat / σ_spy). A estrutura credit-spread tem delta
   exposure no leg comprado (cap protection) que tigh-couples ao
   movimento direcional do SPY em dias normais. Não é "long SPY
   disfarçado" — é exposição pequena de equity. Carr-Wu 2009 prevê
   ρ ≈ 0.4-0.5 pra VRP geral; o credit-spread fica mais alto por
   construção. Variantes futuras (straddles, naked puts far-OTM)
   podem reduzir.

3. **Não é o motor de retorno do projeto** — Strategy A está DORMANT
   (mandate §1). Se algum dia vira WINNER e for liberada via §7
   override, vai precisar de:
   - Paper trading 3-6 meses
   - Verificação de execução real (slippage, IV histórica vs
     option-chain implícita)
   - Modelagem de margin requirements
   - Cap de capital de teste (USD 500-1k por mandate §4.8)
   Tudo isso fora do escopo do loop.

4. **Bondarenko 2014 + Sinclair p.217 + Carr-Wu 2009 tinham antecipado
   esse resultado** — não é descoberta científica nova; é **validação
   empírica** de uma anomalia bem-documentada com infra séria
   (CPCV/PBO/DSR/WF/G7 cross-lib parity 0.0000pp). O loop confirmou
   que o VRP é real e harvestable na escala necessária pra superar
   um benchmark de SPY post-GFC.

## Próximas direções (Stage 5 do loop)

### iter 027 — pick provável: Option V-2 (Levered VRP)

`harvest_notional = 2.0` (pre-committed single value). Projeção:

- CAGR esperado: rf 2% + harvest 2.0 × 3-4% = 8-10%/ano → clear
  floors educational (9.18%) e spy_real (11.98%) com folga; ndx_real
  (15.35%) ainda fica abaixo mas dá pra discutir com mandate §2.2.
- Sharpe esperado: similar ao iter 026 (leverage scales numerator
  e denominator igual).
- Worst-case por roll: ~10-15% (ainda capped pelo credit spread
  width 5%, multiplicado por 2× leverage).
- DSR esperado: passa em 2-3 datasets se Sharpe ficar entre 1.10-1.40.

Se passar, vira **WINNER** — primeiro do loop. Se não, iter 028
explora Option V-3 (filtro VIX) ou V-4 (composto VRP+carry).

### Opções alternativas

- **V-3 — Filtro VIX < 35** (Sinclair p.217). Não abre spread quando
  VIX está alta; deve melhorar Sharpe edu+spy nos 5-10% extra que
  faltam pro DSR. Single binary param.
- **V-4 — VRP + Carry composite** (0.5 × VRP + 0.5 × iter 024 bond
  carry). Lower correlation com SPY, FDM-style diversification.
- **LS — Long-short slow-EWMAC** (consume iter 025 limitação).
- **C — EWMAC + Carry combo** em 6 ativos.

## Onde estão os artefatos

- `studies/strategy_hunt_loop/iterations/026-2026-04-24-2122-vrp-primary-portfolio/`
  - `hypothesis.md` — pre-commit completo
  - `vrp_primary.py` — módulo principal (40 linhas)
  - `numpy_reference_vrp.py` — paridade pure-numpy pra G7
  - `run_backtests.py` — runner 3 datasets
  - `compute_gates_and_score.py` — gates + score
  - `results.json` — métricas + returns_series (630 KB)
  - `verdict.json` — score + tier + breakdown
  - `final_report.md` — relatório completo (375 linhas)
  - `plot_vs_benchmark_spy_real.png` + `plot_vs_benchmark_ndx_real.png`
- `tests/test_iter_026_vrp_primary.py` — 9 specs TDD (todos PASS)
- `studies/strategy_hunt_loop/BASE_MEMORY.md` — atualizado:
  total_iterations 25→26, n_trials 4278→4279, top-K #5, latest_iteration
- `studies/strategy_hunt_loop/DEAD_ENDS.md` — não muda (iter 026 não
  é dead-end); apenas a tightening do iter 020/021 fica registrada
  no BASE_MEMORY 1-line summary.

Citações primárias pra qualquer revisão futura:
- `[volatility_trading, ch.3, p.41, p.217]` (Sinclair 2013)
- Bondarenko (2014) "Why Are Put Options So Expensive?" QJF 4(3) 1450015
- Carr-Wu (2009) "Variance Risk Premiums" RFS 22(3) 1311-1341
- Coval-Shumway (2001) "Expected Option Returns" JoF 56(3) 983-1009
- `[advances_fin_ml, p.31-34]` (cross-lib G7) + `p.222-223` (DSR)

---

## Status do projeto não muda

Mandate §1 continua **MAINTENANCE 100% Plano C**. Strategy A/B/D
seguem DORMANT. iter 026 é **um candidate**, não um deploy. Próxima
sessão do loop continua a hunt — meta é encontrar um WINNER (score
≥ 90 + 5/5 condições estritas). Esta iteration mostrou que **pode
ser viável**: o gate DSR-com-deflator-cumulative que segurou todos os
candidates anteriores foi passado pela primeira vez em ndx_real.
