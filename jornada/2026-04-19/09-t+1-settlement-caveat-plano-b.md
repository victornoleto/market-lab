# T+1 settlement — caveat operacional não modelado no backtest Plano B

> **Tipo:** caveat operacional registrado (não é bug, não é pivot).
> **Escopo:** Plano B (swing broker Inter Global) — Plano A (Pepperstone
> CFD) não tem o problema porque CFD fecha posição e devolve margin
> instantaneamente.
> **Status:** ciente, aceito como "ruído de fricção" pelo usuário.

---

## A questão levantada

Usuário perguntou: quando o Plano B emitir um **exit signal** (ex:
SPY cruza abaixo de EMA-100) ou disparar um **rebalance threshold >
10 pp**, não vai existir gap de alguns dias até o cash da venda
liquidar e poder ser reusado? O backtest contempla isso?

## Resposta curta

**Não, o motor do backtest ignora o gap T+1**, mas a decisão de
*cadence* da estratégia foi tomada ciente da fricção — o gap não
modelado é contabilizado como "ruído de friccção de ~0.01-0.02 no
Sharpe" e registrado como limitação conhecida em
`reports/phase3_5b/variants/rebalance_modes/implementation_notes.md`
§7.1-§7.2.

## O que o doc da estratégia *já* registra

1. **Inter = T+1** (`reports/phase3_5b/PRODUCTION.md:77`). Regra SEC
   pós-2024-05-28, vale pra toda operação US de equity/ETF.
2. **Rebalance diário** (Sharpe 2.108 de referência) está marcado
   como *teoricamente ótimo mas fisicamente impossível* devido a
   T+N settlement (`PRODUCTION.md:42-53`). Por isso o default
   produção é **threshold 10 pp** (~1.3 eventos/ano, compatível com
   T+1).
3. **Regime transition do leg LETF** modela rebal at close +
   settlement open seguinte (`src/ai_trade/backtest/strategies/
   letf_rotation.py:418-422`) seguindo a interpretação Gayed
   `[leverage_for_the_long_run, p.13, p.21]`.

## O que o motor NÃO modela (limitação reconhecida)

`reports/phase3_5b/variants/rebalance_modes/implementation_notes.md`
§7.1-§7.2 (textual):

> **§7.1 Re-entry timing:** the rebal fires on the *last bar* of the
> closing month, but a broker would execute on the *first bar* of
> the new month (T+1 settlement). **We ignore T+1 — a 1-day lag
> would likely reduce all three monthly-mode Sharpes by ~0.01-0.02
> at most.**
>
> **§7.2 Cash drag:** monthly_sell holds zero cash between rebal
> dates — every "sold" notional is immediately re-deployed. A real
> broker would have 1-2 days of settlement cash drag. **Not
> modeled.**

Ou seja: no engine, `sell(D) → buy(D)` com cash instantâneo. Na
vida real: `sell(D) → cash liquida D+1 → buy(D+1)`. O gap de 1 dia
pode ganhar ou perder conforme o movimento intraday do dia
seguinte.

## Decisão registrada

**Não re-rodar backtest com T+1 modelado.** O usuário aceitou a
fricção: "não acredito que no longo prazo seja essa diferença de
poucos dias que fará a diferença" (2026-04-19). A premissa tem
respaldo empírico:

- Estimativa `implementation_notes.md §7.1`: ΔSharpe ≤ -0.02
  (baseline Plano B V4 canonical 2.609 → piso ~2.589, ainda bem
  acima dos 5 gates).
- Janelas de 21.4 anos (V4 canonical) e 40 anos (V4 extended
  1986-2026) absorvem ruído de execução muito maior que 1 dia.
- Threshold 10 pp já limita eventos a ~1.3/ano → no máximo
  ~1.3 dias/ano de cash parado = ~0.35% do tempo. Impacto
  proporcional é desprezível.

## A verificar no onboarding Inter (não bloqueia nada)

- **Custodiante real.** Usuário mencionou "Apex" — doc fala em
  Inter&Co Securities (FINRA). Apex Clearing como sub-custodian é
  prática comum entre brokers US; confirmar não muda settlement
  (T+1 é SEC rule, não política de broker).
- **Unsettled funds policy.** Cash account normalmente NÃO permite
  reusar proceeds antes de D+1 (good-faith rule / free-riding SEC
  Reg T). Margin account permite, mas BR geralmente só abre cash.
  Confirmar com Inter não muda nada do backtest — só confirma o
  pior-case T+1 que já está implícito.

## Arquivos tocados

Só este. Nenhuma alteração de código ou doc de estratégia — é um
registro histórico no `jornada/`.

## Citações

- `[leverage_for_the_long_run, Gayed 2016/2020, p.13, p.21]` —
  modelo rebal-at-close + settle-next-day para LETF rotation.
- `[advances_fin_ml, López de Prado, p.275-278]` —
  drift-triggered trading rules (threshold rebalance
  institucional).
- Investment Mandate §4 — BR 15% IR em realized gains.
