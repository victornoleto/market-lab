# Phase 4.0 T1 — Rate card empírico Pepperstone: commission-zero ✅, lot minimums ❌

**Data:** 2026-04-20 · **Tipo:** validação empírica pré-live · **Impacto:** threshold Index CFD revisado de $1k → $5k por lot granularity (não cost model).

## Contexto

Usuário informou que já tinha cTrader Open API app aprovada — desbloqueou Phase 4.0 T1 (rate card empirical) que na spec original dependia de "abrir conta demo + 1-2 dias de observação manual". Com API, a validação virou programática.

## Execução

Sequência:

1. Salvei OAuth credentials (client_id/secret) em `.env.local` (gitignored, confirmado via `.gitignore:22`).
2. Usuário autorizou app no Spotware Playground (`https://openapi.ctrader.com/apps/25702/playground`) — esse endpoint faz o OAuth exchange server-side e retorna access_token + refresh_token direto na página, pulando a parte interativa de extract `code=` da URL de redirect.
3. Testei tokens via REST `api.spotware.com/connect/tradingaccounts` — 2 contas descobertas:
   - **#1 live** (accountId 46981193, balance $0 nunca financiada — ignorado por segurança)
   - **#2 demo** (accountId 46981202, balance $50k virtual — usado pro T1)
4. Script `scripts/pull_ctrader_rate_card.py` conectou em `demo.ctraderapi.com:5035` via TLS+Protobuf, fez `ProtoOAApplicationAuthReq` + `ProtoOAAccountAuthReq` + `ProtoOASymbolsListReq` (1889 símbolos no catálogo Pepperstone), e por fim `ProtoOASymbolByIdReq` pros targets.
5. Descobri que `USTEC` não é o ticker correto no Pepperstone — fuzzy search encontrou `NAS100` (spot) e `NAS100-F` (futures). Adicionei ao script.
6. Script `scripts/search_ctrader_micro_symbols.py` varreu 1889 símbolos filtrando por keywords (US500, NAS, XAU, etc.) pra encontrar variantes micro. 17 matches.

## Descobertas

### ✅ Vitória: commission-zero empiricamente confirmado

Todos 3 símbolos alvo (US500, NAS100, XAUUSD) reportam `commission: 0`. Isso era a **principal incerteza** do Phase 4.0 — a sensibility matrix tinha mostrado que commission > 40 bps RT era o break point, e temos 0 bps. **Folga massiva.**

Bonus: descobri 2 variants futures (`US500-F`, `NAS100-F`) com **zero swap** além de commission-zero. Rolam trimestralmente; o custo vem do roll spread (não modelado ainda). Mas têm lot minimums proibitivos ($6k/$20k min notional) pra contas pequenas.

### ❌ Problema: lot granularity rompe target $1k

O gate que a sensibility matrix NÃO testou — porque é constraint do broker, não do cost model:

| Símbolo | Min lot | Notional min (preços atuais) | Target $1k | Verdict |
|---|---:|---:|---:|:--:|
| US500 | 0.1 lot | $600 | $1000 | ⚠️ 40% under rounding |
| NAS100 (spot) | 0.1 lot | **$2,000** | $1000 | ❌ 2× overshoot |
| NAS100-F (futures) | 1.0 lot | $20,000 | $1000 | ❌ 20× overshoot |
| XAUUSD | 0.01 lot (= 1 oz) | **$2,700** | $500 (50% risk-off) | ❌ 5× overshoot |

**A $1k você só consegue operar US500.** Perde as 2 outras pernas (QQQ = 50% do alpha via regime rotation, GLD = risk-off que reduz MDD).

Cross-FX gold pairs (XAUEUR, XAUAUD, etc.) têm min 1 oz ≈ $27 notional — granularidade OK — mas introduzem FX risk não-validado no backtest. Fora do escopo Caminho 3 atual.

### Decoded swap rates (com interpretation caveat)

Raw API values:
- US500: `swapLong -6.14` com `swapCalculationType=1` (PERCENTAGE) → **-6.14%/yr = -0.0168%/day**
- NAS100 (spot): idem, **-6.14%/yr** (se comportamento igual a US500)
- NAS100-F (futures): `swapLong 0.0` → **zero swap** (roll-based)
- XAUUSD: `swapLong -8.84` com `swapCalculationType=0` (PIPS) → **ambíguo 1.2-12%/yr**

Blended risk-on (assumindo substituir QQQ por NAS100 spot 50/50):
- 0.5 × (-6.14%/yr) + 0.5 × (-6.14%/yr) = **-6.14%/yr** risk-on weighted
- Com leverage 2× on-risk: -12.28%/yr on levered notional
- Aplicado 75% do tempo (risk-on frac): **-9.21%/yr effective swap drag**

vs baseline Phase 4.0 T3 model: `-0.008%/day × 252 × 2 × 0.75 = -3.02%/yr`

Gap: **real swap é 3× pior que modelado no T3** (pessimistically). Mas a sensibility matrix testou swap até -0.025%/day (=-9.5%/yr effective) e **passou**. Estamos no limite do envelope validado, mas ainda dentro.

Correção do T3 necessária? Provavelmente não — a sensibility matrix já cobre essa magnitude de swap drag e passou. Mas vou flagar como refinamento potencial pra Phase 4.

## Mudanças propagadas nos docs

1. `docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md` — **novo arquivo**, template filled com dados empíricos, threshold revisado $1k→$5k.
2. `docs/strategies/plano_a_v2_l2_gayed_cfd.md` §5.5.4 — corrigido com lot minimum real; §6.3 Phase 5.1 atualizada ($1k Index CFD não é viável, mínimo $5k); §9 update log nova entrada.
3. `docs/investment-mandate.md` §3.6 — Plano A Index CFD threshold corrigido de $1k pra $5k com justificativa lot-granularity-bound.
4. `reports/phase3_5a_v2/AGGREGATE.md` §7.5 — confirm commission-zero, adicionar lot minimum caveat, link pro rate card.

## Addendum — T1.2 spread live quotes (mesma noite, 23:00 UTC)

Extendi o script pra subscribe em `ProtoOASubscribeSpotsReq` e capturar 30 segundos de ticks bid/ask. Resultados (after-hours, US cash market fechou 21:00 UTC):

| Symbol | Ticks | Median half-spread | Baseline modelado | Delta |
|---|---:|---:|---:|---:|
| XAUUSD | 55 | **0.25 bps** | 5.0 bps | 20× tighter |
| NAS100 | 31 | **0.30 bps** | 5.0 bps | 17× tighter |
| US500 | 4 | **0.32 bps** | 5.0 bps | 16× tighter |

**All pass gate ≤15 bps by ~15-20× margin.** Pepperstone Razor Index tem
spreads extremamente competitivos porque é sua principal forma de
monetização (commission zero em Index). Modelar 5 bps half era
pessimismo conservador; realidade é desprezível em comparação.

**Caveat importante:** captura foi **off-hours** (23:00 UTC, 2h após US close
21:00 UTC). Spreads em Index CFDs podem widenear 2-5× no primeiro minuto da
sessão US (14:30 UTC) por price discovery gap. Precisa re-check em
open-hours ou FOMC/NFP days pra validar worst-case. Script `measure_ctrader_spread.py`
é reusável a qualquer hora.

Script: `scripts/measure_ctrader_spread.py`. Data raw: `reports/phase4_0/index_cfd_validation/spread_measurements.json`.

## Próximos pendentes

**T1.2 — Spread em live quotes:** posso adicionar `ProtoOASubscribeSpotsReq` ao script pra medir bid/ask spread real durante US hours. Refina `spread_half_bps` no cost model. Iniciar esta noite mesmo que mercado esteja closed — Index CFDs normalmente têm cotações 23h por overlap com futures.

**T2 — Dividend adjustment:** precisa 1 ciclo ex-div SPY pra observar. Próximo ex-div SPY ~mid-Jun 2026. Procedimento: abrir 0.1 lot long US500 pelo menos 5 dias antes, observar cash adjustment no transaction history.

**T1.3 — Modelar roll cost em futures variants:** US500-F / NAS100-F têm zero swap mas rolam trimestralmente. Roll cost = spread entre contrato expirando e próximo. Se < 5 bps por roll × 4 rolls/yr = < 20 bps/yr drag, seriam **melhores que spot CFDs com swap 6%/yr**. Mas lot minimums proíbem uso a <$6k capital.

## Lição meta

1. **Cost model bps é só metade do retail constraint.** Lot granularity é a outra metade, e não cabe em nenhum gate de backtest porque é broker-specific.
2. **Sensibility matrix cobre cost model, não execution constraints.** Precisa estender o framework pra incluir "min notional per leg" como gate separado.
3. **Pepperstone é generoso em commission (zero Index CFD), mas exige escala em lot size.** Trade-off clássico: fees baixas mas tickets altos. Razão pela qual pequenos traders são empurrados pra share CFDs (commission + share granularity) ou ETFs (expense ratio, sem commission).

## Citações

- `[systematic_trading, Carver, p.185-188]` — fixed commission + lot size dominance.
- Phase 4.0 spec: `specs/phase_4_0_index_cfd_validation.md`.
- Sensibility matrix: `reports/phase4_0/index_cfd_validation/cost_sensitivity.md`.

## Links

- Rate card: `docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md`
- Raw API data: `reports/phase4_0/index_cfd_validation/ctrader_rate_card_raw.json`
- Catalog variants: `reports/phase4_0/index_cfd_validation/pepperstone_catalog_variants.json`
- Scripts: `scripts/pull_ctrader_rate_card.py`, `scripts/search_ctrader_micro_symbols.py`
- Jornada anterior (Caminho 3 backtest validated): `jornada/2026-04-19/12-phase4_0-index-cfd-validated.md`
- Jornada anterior (capital fragility discovery): `jornada/2026-04-19/11-capital-fragility-cost-model-bps.md`
