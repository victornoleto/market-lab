# ops/ — Operational platform for Plano B (MVP)

> Plataforma CLI para journal de trades, DARFs (dois regimes), dividendos,
> posições FIFO e comparação contra benchmarks (S&P500 em BRL, IBOV, IPCA,
> SELIC). Schema multi-account pronto para Planos A e C.
>
> **Source spec:** `docs/superpowers/specs/2026-04-20-ops-platform-plano-b-design.md`.
> **Strategy doc:** `docs/strategies/plano_b_3leg_letf_rotation.md`.

## Design decisions (Q1-Q6 locked)

### Q1 — Multi-account schema from day 1

`broker`, `account_id`, `strategy`, `instrument_domicile` em todo trade.
Plano A (Pepperstone CFD, futuro) e Plano C (buy-hold ETF factor)
entram adicionando linhas, zero migration.

### Q2 — Auto-PTAX via BCB SGS série 1

`get_ptax(date)` primeiro consulta cache local, depois API Banco
Central (série 1 = PTAX venda USD/BRL). Feriado/fim-de-semana:
fallback ao último dia útil anterior (convenção Receita). Manual
override via `--ptax 5.1234`.

### Q3 — Flat CSV files

7 arquivos em `ops/data/` (gitignored), schema_version + atomic
writes + flock. Volume esperado: ~500 trades em 10 anos.

### Q4 — Loss carryforward completo

Perdas acumuladas compensam ganhos futuros:

- **Monthly 6015:** swing e daytrade em streams independentes,
  carryforward mês-a-mês.
- **Annual 14754:** stream unificada `rendimentos`, carryforward
  ILIMITADO entre anos (Lei 14.754/2023, Art. 3°, §5).

### Q5 — Dividend tracking sem auto-Carnê-Leão

`ops dividend add` registra bruto + withholding IRS 30% + PTAX.
Alíquota progressiva (7.5%-27.5%) fica com contador/Excel no regime
mensal. No regime anual Lei 14.754, dividendos entram no bucket
rendimentos automaticamente.

### Q6 — Benchmarks hybrid

- `ops status` — tabela rápida.
- `ops benchmark report --year Y --month M` — markdown completo.
- Séries: **spy_usd** (Tiingo cache reuse) × PTAX, **ivvb11_brl**
  (yfinance), **ibov_brl** (yfinance ^BVSP), **ipca_pct_monthly**
  (BCB 433), **selic_daily_pct** (BCB 11), **selic_meta_annual**
  (BCB 1178). Todos rebased a 100 no inception.

## Tax regimes — qual usar?

Depende de como o **Informe de Rendimentos do Inter Global** classifica
os trades. Confirmar com contador antes do primeiro DARF real.

| Característica | monthly_6015 (legacy) | annual_14754 (Lei 14.754/2023, atual) |
|---|---|---|
| Cadence | mensal (12+/ano) | anual (1/ano) |
| DARF code | 6015 swing / 8523 daytrade | 0211 (ou 4600 legacy) |
| Isenção R$35k/mês | ❌ não aplica a ETF | ❌ não existe no regime novo |
| Dividendos | Carnê-Leão separado (código 0190) | incluídos no bucket rendimentos |
| Carryforward | mensal, por stream (swing/daytrade) | ilimitado entre anos, stream unificada |
| Vencimento | último útil do mês seguinte | último útil de abril ano seguinte (IRPF) |
| Alíquota | 15% swing / 20% daytrade | 15% flat |

**Recomendação:** default `annual_14754`; rodar `ops darf preview` em
ambos durante 2026 e comparar antes do primeiro DARF real em 2027-04.

## Workflow típico Plano B

```bash
# 1. Primeira compra
ops trade add --ticker SSO --side buy --qty 10 --price 52.30 --date 2026-04-20

# 2. Após rebalance ou exit, registrar venda
ops trade add --ticker SSO --side sell --qty 5 --price 55.00 --date 2026-05-15

# 3. Ao receber dividendo
ops dividend add --ticker SSO --gross-usd 12.50 --withheld-usd 3.75 --date 2026-06-15

# 4. Fim de período: preview DARF
ops darf preview --regime annual_14754 --date 2026-12-31
ops darf preview --regime monthly_6015 --date 2026-05-31

# 5. Se confirmado, fechar DARF
ops darf close --regime monthly_6015 --period 2026-05

# 6. Recolher via sicalcnet, depois marcar pago
ops darf paid DARF-M-202605-SW --date 2026-06-28 --proof ~/darfs/202605.pdf

# 7. Mensal: benchmark report
ops benchmark fetch
ops benchmark report --year 2026 --month 5 --out reports/2026-05.md

# 8. Quick status
ops status
```

## Adicionar Planos A/C no futuro

- **Plano A (Pepperstone CFD):** `--broker pepperstone --strategy plano_a
  --instrument-type cfd`. Tax model CFD: requer adição de regime
  próprio (Phase 5).
- **Plano C (buy-hold factor):** `--strategy plano_c --broker <br_broker>
  --instrument-type etf --domicile br` (BR ETFs) ou `--domicile us`
  (US ETFs). Regime fiscal igual Plano B se ETF no exterior.

## DARF codes — referência

| Código | Regime | Uso |
|---|---|---|
| **6015** | monthly_6015 | Ganhos líquidos swing em renda variável (bolsa) |
| **8523** | monthly_6015 | Ganhos líquidos day-trade |
| **0190** | legacy | Carnê-Leão — rendimentos exterior (dividendos) |
| **0211** | annual_14754 | Cota única IRPF anual |
| **4600** | legacy | Ganho capital ativos moeda estrangeira (pré-14.754) |

## Legislação

- **Lei 11033/2004** — regime mensal de renda variável (swing 15%,
  daytrade 20%, compensação de prejuízo mês a mês).
- **Lei 14.754/2023** — regime anual atual de aplicações no exterior
  para residentes BR. Art. 2° (15% flat), Art. 3° §5 (carryforward
  ilimitado).
- **IN RFB 1.585/2015, Art. 58** — FIFO lot matching obrigatório.

## Tests

```bash
.venv/bin/pytest ops/tests/ -v
```

## Citations

- `docs/investment-mandate.md` §4.7 — Inter Global operational facts.
- `reports/phase3_5b/PRODUCTION.md` — runbook produção Plano B.
- `books/summaries/advances_fin_ml.md, p.275-278` — threshold
  rebalance rationale.
- `jornada/2026-04-19/09-t+1-settlement-caveat-plano-b.md` — T+1
  caveat registrado.
