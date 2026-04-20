# Plataforma operacional `ops/` entregue — controle de trades, DARFs e benchmarks para o Plano B

> **Tipo:** Entrega de infraestrutura (arquitetura + código).
> **Escopo:** Novo módulo `ops/` no repo. Foco no Plano B; schema já
> pronto pra Planos A e C.
> **Status:** Merged e pushed em `main` (commit `a528f02`, 2026-04-20).
> Pytest 796 → 854 (+58 testes), zero regressão.

---

## O que é isso em uma frase

O ai-trade agora tem um app de linha de comando chamado `ops` que
registra cada trade/dividendo do Plano B, calcula o DARF a pagar
(nos dois regimes fiscais possíveis), mantém o saldo de prejuízo
acumulado para abater em ganhos futuros, e compara meu desempenho
contra SP500/IBOV/IPCA/SELIC — tudo em R$.

Exemplo de uso depois da primeira compra real:

```
ops trade add --ticker SSO --side buy --qty 10 --price 52.30
ops status                # cadê eu agora
ops darf preview          # vou pagar quanto de imposto esse mês?
ops benchmark report ...  # como meu retorno compara com mercado?
```

## Por que isso existiu

O Plano B (portfolio 3-leg SSO+QLD+UGL no Banco Inter Global) já
está autorizado pra deploy desde 2026-04-18. Sem uma ferramenta
como essa, cada trade vira uma entrada manual em planilha, cada
DARF exige recalcular prejuízo acumulado de cabeça, e comparação
contra benchmark depende de CTRL-C/CTRL-V em sites da B3/BCB. Com
ops/, tudo vira comando CLI reprodutível e auditável.

Mais importante: **a Receita não aceita o informe do broker como
única evidência fiscal** (Lei 14.754 transfere a responsabilidade
de apuração pro investidor). Logo, um journal próprio não é opção,
é obrigação.

## O dilema fiscal que moldou o design

No meio do brainstorm descobri uma inconsistência crítica no projeto:
o `investment-mandate.md` cita Lei 14.754/2023 (regime novo, anual)
mas descreve operacionalmente o regime antigo mensal DARF 6015. Os
dois são incompatíveis:

- **Antigo (Lei 11033):** 12+ DARFs/ano, carryforward mês-a-mês,
  dividendos via Carnê-Leão separado (código 0190).
- **Novo (Lei 14.754):** 1 DARF/ano junto com IRPF, carryforward
  ilimitado entre anos, dividendos somam no bucket de rendimentos.

Qual se aplica de fato ao Inter Global depende de como o Inter
emite o "Informe de Rendimentos" — a gente só vai saber com o
primeiro informe real. Então o `ops/` implementa **os dois regimes
como plugins** (`ops/core/tax/regime_monthly_6015.py` e
`regime_annual_14754.py`) e você escolhe via `--regime`. Durante
2026 eu vou rodar `ops darf preview --regime=...` em ambos e
comparar, antes de fechar o primeiro DARF real em 2027-04.

## Decisões que ficaram gravadas

Durante o brainstorm foram 6 perguntas com trade-offs, todas com
racional no `ops/README.md`:

1. **Schema multi-account desde o dia 1** — não só Plano B; adicionar
   A ou C no futuro não requer migração.
2. **Auto-PTAX via BCB** — fetch automático da API do Banco Central;
   fallback manual pra offline/backfill.
3. **CSVs planos (não SQLite)** — pro volume esperado (~500 trades
   em 10 anos), flat files são suficientes e human-editable. YAGNI.
4. **Carryforward completo** — perdas nunca se perdem; sistema
   rastreia saldo por (regime, tipo de stream) e abate em ganhos
   futuros.
5. **Dividendos registrados, Carnê-Leão manual** — sistema registra
   valor bruto + PTAX correto, mas a alíquota progressiva (7.5-27.5%)
   fica com contador/Excel pessoal.
6. **Benchmarks em R$ com hybrid CLI** — `ops status` é dashboard
   rápido, `ops benchmark report` gera markdown mensal completo.

## O custo humano de construir isso

11 tasks em modo **subagent-driven-development** (plugin superpowers):
implementer dispara código + testes por task, dois reviewers
adversariais (spec compliance + code quality) vão atrás. Nos pontos
fiscais críticos (FX, regime mensal, regime anual, FIFO, CLI de
darf close) os reviewers pegaram **bugs reais** antes de virarem
history:

- Storage: arquivo vazio crashava em vez de retornar lista vazia;
  `.tmp` órfão em falha de write.
- FX: body de erro do BCB como dict (não lista) bypassava guard.
- Tax: zero-tax gerava DARF fantasma; carry_in negativo virava
  imposto a mais.
- Positions: `drift_vs_target` não sortia trades → FIFO silenciosamente
  errado em entrada fora de ordem.
- CLI trade: input inválido (qty="abc") crashava com traceback em
  vez de erro amigável; race condition no `trade_id` entre dois
  terminais.
- CLI darf: idempotency check fora do lock (TOCTOU); private API
  leak no comando `paid`.

Cada um desses foi fix-cycle dentro da task antes de mergear.

## E o T+1? (resposta à sua pergunta original)

A pergunta que abriu essa sessão era sobre T+1 settlement: "o
backtest considera o delay de 1 dia entre venda e reuso do cash?"
Resposta: **não modela o gap, mas a decisão de cadence (threshold
10pp ~1.3 eventos/ano) foi T+1-aware**. Impacto estimado: ΔSharpe
≤ -0.02 — desprezível no longo prazo. Registrado em
`jornada/2026-04-19/09-t+1-settlement-caveat-plano-b.md`.

Essa conversa derivou naturalmente pra "ok, então me ajuda a
construir o controle operacional disso" — e daí veio o `ops/`.

## O que muda na prática

**Antes:** Plano B seria operado via planilha Google Sheets + sites
externos (Banco Central, B3, sicalcnet, informe Inter).

**Depois:** Plano B é operado via CLI reprodutível com dados
gitignored em `ops/data/`, auditável via git, com fiscal-correctness
testada em 18 cenários automatizados (entre swing/daytrade
positivo/negativo, carryforward, dividendos, rate clamping).

A primeira compra real do SSO vai testar o fluxo completo pela
primeira vez:

```
ops trade add --ticker SSO --side buy --qty X --price Y --date ZZZZ
```

→ valida PTAX fetch, criação de cost basis em R$, append atômico
ao trades.csv, schema_version marker, lock file. Se alguma coisa
explodir na primeira compra real, esse é o momento de descobrir —
antes de escalar capital.

## Pendências explícitas

- **Scripts de monitoramento diário** (signal check SPY EMA-100 /
  QQQ Donchian 20/10 / GLD Donchian 40/20) — **não entraram** no
  MVP. PRODUCTION.md §7.7 já lista `scripts/plano_b_daily_check.py`
  como placeholder Phase 4.
- **Backup criptografado** (`ops export backup --password`) — também
  Phase 4; hoje o backup é `tar czf ...` manual do `ops/data/`.
- **Integração automática com API do Inter** — se existir; por ora
  tudo é entrada manual (`ops trade add`).
- **Plano A tax model** — CFD tem regime fiscal próprio (ganho por
  fechamento de posição, não FIFO de lote). Adicionar quando Plano A
  sair do paper trading.
- **Plano C** — buy-hold ETF factor-based. Schema já aceita; falta
  só decidir broker e tickers específicos.

## Artefatos que ficaram vivos

- `ops/` — módulo Python + CLI, 41 arquivos.
- `docs/superpowers/specs/2026-04-20-ops-platform-plano-b-design.md`
  — spec técnico com Q1-Q6 e racional completo.
- `docs/superpowers/plans/2026-04-20-ops-platform-plano-b.md` —
  plano de implementação de 11 tasks (referência pra construir
  plataformas similares no futuro).
- `ops/README.md` — documentação end-user: workflow típico, tabela
  comparativa dos dois regimes, DARF codes, legislação.

Tudo pushed em `main` (commit `a528f02`).

## Citações

- **Lei 11033/2004** — regime mensal pré-2024 de renda variável.
- **Lei 14.754/2023** — regime anual atual de aplicações no exterior.
- **IN RFB 1.585/2015, Art. 58** — FIFO lot matching obrigatório.
- `books/summaries/advances_fin_ml.md, p.275-278` — threshold
  rebalance rationale (fundamenta por que a cadence default é
  threshold 10pp, não diário).
- `docs/investment-mandate.md` §4.7 — fatos operacionais Inter
  Global.
- `reports/phase3_5b/PRODUCTION.md` — runbook produção Plano B.
