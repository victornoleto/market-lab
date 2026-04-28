# Bestfolio Hunt Loop — Lançamento + 4 entregas de encerramento do global_factor_tilt_loop

## O que aconteceu

Sessão de encerramento do `global_factor_tilt_loop` e preparação do próximo ciclo de busca.
Quatro entregas realizadas:

---

### 1. Plot unificado dos winners

Criado `studies/global_factor_tilt_loop/plot_winners_all.py` — gráfico comparativo com todas
as 3 estratégias Pareto frontier (iters 005, 009, 013) sobrepostas ao VT (VTSIM proxy) e ao
SPY (dados Tiingo) no mesmo eixo logarítmico. Dois datasets gerados:
- `plots/winners_comparison_vt_real.png`
- `plots/winners_comparison_ndx_real.png`

Cada linha tem Sharpe / CAGR / MDD na legenda. Painel inferior: rolling 1-year Sharpe
diferencial vs SPY. Iter 012 (net-of-tax) não tem série de retornos em results.json —
anotado como referência de texto no título do gráfico.

---

### 2. Correção do modelo tributário — AnnualDarfEngine

**Problema descoberto**: iters 011 e 012 usaram `DarfCostBasisEngine` que aplica DARF
*mensalmente* a cada rebalanceamento, com janela de 12 meses para compensar perdas.
Isso é **incorreto** per Lei 14.754/2023 (vigente jan/2024).

**Modelo correto** (Lei 14.754/2023):
- DARF apurado **anualmente** sobre ganho líquido do ano
- Perdas compensam ganhos dentro do mesmo ano calendário
- Saldo negativo (perda líquida) **carrega indefinidamente** (sem prazo de expiração)
- Taxa: **15% flat** (sem progressividade, sem isenção)
- Pagamento: via DIRPF (declaração março-maio do ano seguinte)

Criado `studies/global_factor_tilt_loop/tax_engine_v2.py` — classe `AnnualDarfEngine`
com `record_trade()`, `year_end_settlement()`, `apply_return()`, `settle_all_pending_years()`.
**Esta classe deve ser usada em todos os backtests futuros que modelam DARF.**

---

### 3. Iter 014 — rerun anual do híbrido

Criado `studies/global_factor_tilt_loop/iterations/014-2026-04-27-annual-darf-rerun/`
com re-run do iter 012 (híbrido 50/50 HAA+Plano C) usando `AnnualDarfEngine`.

**Resultado**:
- edu: S=0.9628 / C=12.36% / MDD=26.36% (vs iter 012: S=1.0212 — Δ **−0.058**)
- vt_real: S=1.0416 / C=13.85% (vs 1.0579 — Δ −0.016)
- ndx_real: S=0.9652 / C=11.77% (vs 0.9715 — Δ −0.006)
- Score 85 STRONG, winner_conditions_met=True, 7/7 gates × 3 datasets

**Achado importante**: o modelo anual não é universalmente melhor para HAA de alta
rotatividade. Mecanismo: quando HAA rebalanceia mensalmente e compra, o custo médio sobe
(porque compra em preço de mercado). Isso reduz o ganho realizado em vendas futuras —
parcialmente neutralizando o benefício do diferimento tributário. Resultado: timing-neutral
para estratégia consistentemente bull com alta rotatividade.

**Lição**: benefício do modelo anual aparece mais claramente em estratégias com perdas
substanciais (carry-forward indefinido) ou com turnover concentrado no início do período.
Para HAA puro, a diferença é marginal (≤ 0.06 Sharpe).

---

### 4. Lançamento do bestfolio_hunt_loop

Criada infraestrutura completa em `studies/bestfolio_hunt_loop/`:

| arquivo | propósito |
|---|---|
| `README.md` | missão + como rodar |
| `scoring.py` | benchmarks = iter 009 HAA+Gold (edu S=1.120) |
| `WINNER_AND_RANKING.md` | critérios: bater iter 009 por ≥ 0.10 Sharpe em ≥ 2 datasets |
| `BASE_MEMORY.md` | estado inicial + 6 hipóteses priorizadas |
| `INFRASTRUCTURE.md` | simuladores, cache, `AnnualDarfEngine` |
| `DEAD_ENDS.md` | DE-001 e DE-002 trazidos do predecessor |
| `EXTERNAL_INSTRUMENTS.md` | cópia com RSIT adicionado |
| `plot_helper.py` | gerador de gráficos por iter |
| `run_loop.sh` | orquestrador shell (branch: `bestfolio-hunt/iter-NNN`) |
| `PROMPT.md` | prompt por iter (template {{ITERATION_N}}) |

**Fila de hipóteses** (por prioridade):
1. **BAA-G12 Balanced** — Bold Asset Allocation 12-asset, canário dual (BIL+DBND).
   Bestfolio #5 reporta Sharpe 1.13. Candidato mais forte p/ fechar o gap.
2. **NTSX + GDE + KMLM static** — preferência explícita do usuário.
   40% NTSXSIM + 30% GDESIM + 30% KMLMSIM. Testa se static capital-efficient
   iguala HAA sem custo de rotatividade/DARF.
3. **NTSX + GDE + RSST static** — variante com RSST no lugar do KMLM.
4. **HAA + factor tilt internacional** — VEASIM → 70% VEASIM + 30% VBRSIM.
5. **Composite Momentum Standard** — bestfolio #2, Sharpe 1.17. Dual momentum multi-lookback.
6. **HAA + RSIT** — deferred; aguardar lançamento RSIT (~mai/2026). Synth disponível.

**Diferença crítica vs global_factor_tilt_loop**: benchmark de score é iter 009 (S=1.120),
não VTSIM (S=0.66). Bar subiu substancialmente — qualquer WINNER aqui é genuinamente
superior ao melhor resultado anterior.

**Validação**: `DRY_RUN=1 bash studies/bestfolio_hunt_loop/run_loop.sh` retorna prompt
corretamente. `from scoring import score_strategy` importa sem erros. 953 testes passam
(6 failures pré-existentes, não relacionadas).

---

### Atualização de documentação

- `docs/investment-mandate.md` §4.7.2: nota sobre correção do modelo DARF (Lei 14.754/2023).
- `studies/global_factor_tilt_loop/EXTERNAL_INSTRUMENTS.md`: linha RSIT adicionada na tabela
  RSS-family (ticker RSIT, SEC 485APOS 2026-02-18, Tidal Trust II, ~mai/2026 launch).
- Memory: `project_ntsd_etf_discovery.md` atualizado com detalhes confirmados do RSIT.

---

## O que vem a seguir

**bestfolio_hunt_loop** pronto para executar. Iniciar com:

```bash
MAX_ITER=6 CLAUDE_MODEL=opus bash studies/bestfolio_hunt_loop/run_loop.sh
```

Hipótese #1 (BAA-G12) é o candidato mais forte — bestfolio evidence diz Sharpe 1.13 vs
nosso gap de 0.06 para o alvo 1.18. Se BAA-G12 chegar perto, iter seguinte ajusta
parâmetros. Se NTSX+GDE+KMLM static (hipótese #2) igualar HAA sem rotatividade, tem
vantagem operacional enorme (sem DARF mensal, sem execução complexa).

**Mandate §7 deliberation** (global_factor_tilt_loop): aguarda decisão do usuário sobre
ativar Plano C 100% (status quo), 50/50 híbrido (iter 012 net), ou 100% HAA+Gold (iter 009).
