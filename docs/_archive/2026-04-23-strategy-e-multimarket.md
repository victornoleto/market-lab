# Mandate override proposal — Strategy E (multi-market extension of Strategy D)

**Data:** 2026-04-23
**Proposto por:** Claude Code (autônomo durante 8h offline do usuário)
**Status:** 🟡 Proposta — aguarda revisão e assinatura do usuário
**Afeta:** `docs/investment-mandate.md` §4b (Strategy D rules — extensão
opcional para multi-market); potencialmente novo `§4c` se Strategy E for
tratada como slot próprio.
**Reversível:** Sim. Até assinatura, o mandate permanece intocado.

---

## Por que este override

Strategy D (IBrX-100 only) falhou em 10/10 configs MVP com IS→OOS decay
−1.06 Sharpe. Root cause: regime break Brasil 2020-2023 destruiu
persistência cross-sectional que momentum depende (ver
`reports/phase_d_mvp/BREADTH_NO_WINNER_D.md`).

A hipótese extensora: **ampliar universo pra incluir ações US SP500
top-200** pode salvar a Strategy D's signal families (D1 Clenow, D4
low-vol+mom) porque:

1. **Cross-section 3× maior** — 100 BR → 300 combined = diversificação
   significativamente melhor.
2. **Literatura justificadora foi desenvolvida em US** — Clenow
   `[stocks_on_the_move]` explicitly US-based; Chan `[quant_trading_chan]`
   US-based; AFML US-based. Strategy D em BR-only foi extrapolação.
3. **Spreads menores** — SP500 top-200 ~1-3 bps vs IBrX-100 15-50 bps.
   Absorve menos edge retail.
4. **Regimes diferentes cross-market** — 2020-2023 US teve FAANG rally +
   AI bubble; BR teve commodity/banking inversion. Cross-sectional
   momentum global pode capturar dispersion que single-market colapsa.
5. **Já temos infra** — yfinance source suporta `.SA` e sem sufixo;
   Wikipedia SPX snapshot existe; engine cross-lib validated.

## Alterações propostas

### Opção A — Extensão de Strategy D (preferida, mínimo invasiva)

Editar `§4b.1 Universo`:

> De: "**IBrX-100** (B3 top ~100 ações por free-float liquidity)..."
>
> Para: "**Multi-market**: SP500 top-200 (yfinance sem sufixo) + IBrX-100
> (yfinance `.SA` suffix) = ~300 tickers combinados. Fase D-MVP (IBrX-100
> only) encerrada em 2026-04-23 com NO_WINNER_D. Fase E-MVP estende pro
> universo multi-market. Proxy dinâmico por liquidez (R$/USD equivalent)
> via `get_universe_on`."

Editar `§4b.5 Cost model BR` renomeando pra `§4b.5 Cost model multi-market`:

> Adicionar: "Per-ticker dispatch via `scripts/phase_e_mvp/cost_model.py`:
> BR sells check R$20k/mês exemption (regra BR original); US sells pagam
> **15% DARF unconditional** (rota Inter Internacional, §4.6). FX spread
> 100 bps one-way USD→BRL aplicado a US realized gains."

Sem mudanças em `§1` (capital allocation) — Strategy E permanece dentro
do slot Strategy D alocado 2026-04-22.

### Opção B — Strategy E como slot próprio (`§4c`)

Abrir slot novo Strategy E análogo a Strategy D, dilui alocação A/B/D
ainda mais. **Não recomendo** — ainda não temos winner em D; abrir slot
novo pra variação de D é over-proliferation.

---

## O que NÃO está mudando

- **Plano C passivo** 60-80% continua intacto.
- **Gates hard-block §2.4** inalterados.
- **Strategy A** (Pepperstone) + **Strategy B** (Inter LETF) continuam
  slots válidos com alocação zero-real até winner.
- **Tier framework §2.2/§2.3** — Strategy E herda comparador de Strategy D
  (CDI líquido ~11%/ano) com tier Válido 17-25% CAGR net.
- **Regra de citação** — Strategy E reusa mesmas citações de Strategy D
  (Clenow, Chan, AFML, Carver).

---

## Se Strategy E também falhar (72º honest FAIL)

**Recomendação oficial será consolidar Plano C passive** e parar active
alpha hunt. Justificativa estatística:

- 71 honest FAIL consecutivos em 2 semanas de grid search
- Literatura séria (Harvey & Liu 2015; de Prado 2018; Ilmanen 2011)
  prevê exatamente esse resultado pra retail com capital limitado
- B&H factor-tilted (`portfolio-aposentadoria.md`) é mathematically
  optimal quando active alpha não é encontrável

Isso não é "derrota" — é sinal honesto que a gente cumpriu o protocolo
rigoroso e o mercado mandou a resposta. Projeto ai-trade permanece valioso
como infra de **due diligence adversarial** pra proteger contra future
folclore.

---

## Assinatura

Este arquivo permanece PENDING até usuário responder explicitamente:

- **"aprovado"** → aplico as mudanças literais em `investment-mandate.md`
- **"aprovado opção B"** → abro slot `§4c` separado
- **"rejeitado"** → arquivo como rejeitado, recomendo consolidar Plano C
- **"ajustes: X"** → reescrevo override

Até então, `investment-mandate.md` permanece intocado. A implementação
técnica de Strategy E já está em `scripts/phase_e_mvp/` (não requer
mandate edit pra existir como código; só pra virar slot oficial).
