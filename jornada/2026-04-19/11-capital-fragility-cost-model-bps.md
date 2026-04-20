# Plano A — o abismo entre backtest bps e commission real em dólares

**Data:** 2026-04-19 (noite) · **Tipo:** descoberta crítica de pre-live · **Impacto:** bloqueia Plano A execution em conta <$5k; motiva investigação Caminho 3 (Index CFD).

## O que aconteceu

Usuário informou que quer começar com **$1.000 reais** na Pepperstone. Perguntou como o lot size funciona. Expliquei o backtest (100% notional por leg, 2× total leverage). Usuário sinalizou honestamente: "ainda não entendi 100%, preciso que você revise a estratégia porque vou aplicar com $1k".

Fui fazer a revisão crítica. Descobri um **buraco estrutural no cost model** do V2 que não é captado por nenhum gate PBO/DSR/WF porque o gate só valida **scaling em bps**, não **scaling em dólares**.

## A descoberta

O cost model do V2-L2 winner:
```
spread_half_bps: 2.0
commission_round_trip_bps: 6.6    ← CULPRIT
slippage_bps_round_trip: 3.0
swap_daily_pct_long: -0.005
```

Pepperstone Razor tier **não cobra commission em bps**. Cobra **$3.50/side em USD fixo** — ~$7 round-trip por ticker. Em bps, isso vira:

| Notional por trade | Commission RT real (bps) | Desvio vs modelo (6.6 bps) |
|---:|---:|---:|
| $1.000 | **70 bps** | +10× |
| $5.000 | 14 bps | +2× |
| $10.000 | 7 bps | ≈ modelo ✅ |
| $50.000 | 1.4 bps | −5× |

Para 309 round-trips risk-on observados no trade log (reconstruído em jornada 10), a $1k:
- Commission total 25y = 309 × 70 bps × $1000 = **$2.163 = 216% do equity inicial**
- CAGR modelado 79% líquido → CAGR real ≈ **negativo** após commission drag

Literalmente a estratégia morre em conta pequena. **Zero gate captou isso** porque PBO/DSR/bootstrap testam robustez *do sinal*, não *da economia operacional*.

## Por que eu não vi antes

O living strategy doc (`docs/strategies/plano_a_v2_l2_gayed_cfd.md`) escreveu **todos os exemplos** em conta $10k (§5.2), e §6.3 "escalação de capital" listou Phase 5.1 como "$1.000 real" sem checar consistência com o cost model — inconsistência que sobreviveu porque ninguém tinha feito a math em USD absoluto antes de eu ser questionado diretamente. Carver `[systematic_trading, p.185-188]` avisa explicitamente: "Fixed commission dominates at retail scale". Eu citei essa página em §6 do doc mas não apliquei a advertência a V2-L2.

## O que mudou nos docs (propagação hoje)

1. **`docs/strategies/plano_a_v2_l2_gayed_cfd.md`:**
   - **Novo §5.5** "Capital mínimo viável" — 5 sub-seções com a matemática completa do colapso, lot granularity em share CFD, thresholds operacionais ($5k/$10k/$25k), caminho alternativo Index CFD.
   - **§6.2 caveat #7** novo — flag crítico de backtest cost model breakdown.
   - **§6.3 tabela escalação** — Phase 5.1 fixada: **$5.000 share CFD** OU **$1.000 Index CFD** (condicional a Phase 4.0 validar).
   - **§9 update log** — entry novo 2026-04-19 documentando a correção.

2. **`specs/phase_4_paper_trading.md` §1** — sizing $10k paper reclassificado de "arbitrária" para "deliberadamente escolhida, é o threshold onde o cost model bps é representativo".

3. **`docs/investment-mandate.md` §3.6** — nova sub-seção "Capital mínimo viável por strategy" com tabela threshold cross-strategy: Plano A share CFD $5k / Plano A Index CFD $1k / Plano B sem mínimo.

4. **`reports/phase3_5a_v2/AGGREGATE.md` §7.5** — seção "Known execution limitations" escopando o 13/13 gate pass a capital ≥ $10k notional/trade. Não invalida o pass, só informa a envelope de aplicabilidade.

## O que isso significa pra $1k

Três caminhos analisados (resposta detalhada ao usuário em conversation log):

1. **Caminho 1 — Plano B only (recomendado):** $1k vai 100% Plano B (3-leg EW em SSO/QLD/UGL via Banco Inter Global). Zero corretagem, zero swap, commission bps → irrelevante porque Inter é flat-fee zero. Capital limitations de Plano B: nenhuma identificada.
2. **Caminho 2 — acumular $10k antes:** paper Plano A em cTrader Demo + Plano B ao vivo até $10k; depois abre Pepperstone com capital suficiente.
3. **Caminho 3 — Index CFDs em conta $1k:** substituir SPY/QQQ share CFD por US500/USTEC index CFD. Commission tipicamente zero em Razor Index; lot 0.01 permite granularidade. MAS: tracking error SPY→US500 não-validado (dividend adjustment mechanics, tax behavior em CFD Index, etc.). **Requer Phase 4.0 dedicada antes de Phase 4 paper start.**

Usuário escolheu **avaliar Caminho 3** — não se comprometeu ainda, quer ver o plano de validação.

## Próximos passos imediatos

- [ ] Escrever memo de análise do Caminho 3: memory.md compatibility check (V3 vs Phase 4 adaptation), critical unknowns (Pepperstone Razor Index commission structure, dividend adjustment mechanism), proposed validation tasks, tradeoffs vs C1 e C2.
- [ ] Draft `specs/phase_4_0_index_cfd_validation.md` (se Caminho 3 for aceito) — tasks pre-Phase 4 paper.
- [ ] Update `jornada/README.md` index com esta entry.

## Lições para futuros sessions

1. **Cost model em bps é uma ficção contábil** abaixo de certa escala. Sempre check commission em USD absoluto quando o broker cobra flat fee.
2. **Gates PBO/DSR/WF testam o sinal, não a economia.** Não confunda "strategy passes gates" com "strategy is executable at capital X".
3. **Carver `[systematic_trading, p.185-188]` é gospel, não folklore.** "Fixed commission dominates at retail scale" — relê antes de toda decisão de capital allocation.
4. **Se um doc tem exemplos só a $10k, flag essa lacuna explicitamente.** Extrapolation mental do usuário é onde bugs operacionais escondem.

## Citações

- Carver fixed commission dominance: `[systematic_trading, p.185-188]`.
- Kelly f/2 leverage cap preserved: `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`.
- V2-L2 gate robustez (intocada, só escopo de aplicabilidade adicionado): `[advances_fin_ml, ch.11, ch.14, p.196-211]`.

## Links

- Living strategy doc updated: `docs/strategies/plano_a_v2_l2_gayed_cfd.md`
- Mandate updated: `docs/investment-mandate.md §3.6`
- Phase 4 spec updated: `specs/phase_4_paper_trading.md §1`
- Winner AGGREGATE updated: `reports/phase3_5a_v2/AGGREGATE.md §7.5`
- Trade log referenced (389 trades): `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/trade_log.csv`
