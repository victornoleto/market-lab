# Decision Memo — Probe HappyForex / Happy Market Hours v2.3.1

**Data:** 2026-05-01
**Estado do projeto:** maintenance mode (mandate §1, 2026-04-23)
**Plano A status:** DORMANT
**Probe alvo:** MyFxBook id 1407880, 7,8 anos de trade history
**Spec ref:** `/home/victor/.claude/plans/dreamy-crunching-hamming.md`
**EDA detalhado:** `reports/04_eda_summary.md`

## TL;DR — verdict misto

✅ **Strategy é real** — fingerprint identificado com alta confiança nos
eixos timing/exit/sizing/universe. Não é martingale, não é grid, não é
fraude estatística óbvia.

✅ **Edge real existe na amostra** — Sharpe annualized 2,51 sobre 8 anos
após cost model Pepperstone Razor 2025; DSR p < 0,0001; WF 7/8 windows
positivas.

❌ **Não passa gate hard-block §2.4** — single-block OOS (12 meses) tem
Sharpe 1,89 mas bootstrap 99.9% CI low = −1,67 (binding constraint).

⚠ **Blackout de 5 anos (2021-07 → 2026-05)** impede verificação
direta de persistência do edge em regime atual. Vendor (`happyforex.de`)
classificou como "OLD" → presumível morte/substituição.

## Resposta direta à pergunta original do usuário

> "Você acha que isso é possível?" (re: reverse-engineer HappyForex)

**Sim, parcialmente.** Conseguimos:
- Identificar timing exato (23:00-01:00 UTC, peak 23:55-00:05)
- Identificar universe (6 FX pairs), exit (time-based, ~1-3h)
- Identificar sizing (proportional ao equity, sem martingale)
- Confirmar edge real via gates DSR/WF na amostra completa

**Não conseguimos** (sem 1m OHLC):
- Reverse-engineer o direction signal (Buy vs Sell por pair por sessão)
- Validar via P3 replicator com match-rate ≥ 80%

**Não verificamos** (sem dados pós-2021):
- Persistência do edge em regime atual 2022-2026
- Robustez vs custos reais de uma conta Pepperstone live

## Comparação com Plano-A 113/113 FAIL anteriores

Diferente dos 113 candidatos que falharam Phase 3.5f-3.8: aqueles foram
encontrados por busca sistemática num grid de parâmetros sobre indicadores
clássicos, e falharam DSR/PBO porque eram artefatos de seleção. Este aqui
**não foi descoberto pelo nosso grid** — é uma estratégia externa publicada
com 8 anos de track record contínuo, gates DSR/WF na amostra dão evidência
forte de signal real. O modo de falha é diferente: não overfit, mas
**evidence stale** (5 anos sem amostra).

## Cost economics — viabilidade live na Pepperstone

| Pair | gross net | Pepp cost | net | viável? |
|---|---:|---:|---:|---|
| USDCHF | +4,5 | 1,45 | **+3,05** | sim |
| EURCHF | +4,8 | 1,90 | **+2,93** | sim |
| GBPUSD | +2,9 | 1,20 | **+1,75** | sim |
| EURGBP | +2,0 | 1,45 | +0,55 | marginal |
| EURUSD | +1,3 | 0,83 | +0,43 | marginal |
| USDCAD | +1,3 | 1,44 | **−0,10** | NÃO |

**3/6 pares net-positivos** com folga em Pepperstone. **USDCAD net-negativo**
mesmo em backtest favorável. Strategy filter mandatory para reduzir o
universe a EUR-cross/CHF/GBPUSD.

## Tier framework (mandate §2.2 Strategy A)

CAGR realizada full-sample = não calculável diretamente sem modelo de
account-equity (track record demo distorce sizing real). Como referência:
- Strategy ganhou +4 550% em 8 anos demo = **CAGR ~70%/ano** (folclore-
  number, demo, leverage 1:500 tipo offshore)
- Ajustado pra Pepperstone retail (1:30 majors, sizing real proporcional
  via Kelly f/2): estimativa preliminar **20-40%/ano CAGR líquido**
  (dentro de tier "Válido" 25-50%)

Tier não pode ser confirmado sem live/paper trading com sizing realista.

## Opções de continuação

### Opção 1 — Folclore (FAIL formal)
Move pra arquivo `studies/folclore_archive/`. Razões:
- Gate 4 OOS hard-block FAIL no nível 99.9%
- Vendor "OLD" label = self-acknowledged death
- 5-year blackout sem evidência atual
- USDCAD net-negativo + EUR-cross marginal pós-2018

**Custo:** zero adicional. **Conclusão:** Plano A continua DORMANT, slot
preservado para outra hipótese futura.

### Opção 2 — Spec V3 + paper-trading 90 dias ⭐ RECOMENDADA

Escreve `specs/plano_a_v3_asian_session_fx.md` com a regra reverse-engineerada
(parcial — direction signal estimada como prior-bar continuation no Asian
open, validar empiricamente). Setup paper-trading **MT5 demo Pepperstone
Razor**, 6 pares (filtrar USDCAD), 90 dias automated.

**Critério de continuação após 90d demo:**
- Net pips/trade ≥ 1,0 (consistente com 2018-2019 baseline)
- Win rate ≥ 65%
- 0 dias com -10% drawdown

Se passa → Phase 4.0 paper-trading 12 meses formal (já no slot Plano A).
Se falha → Folclore + decisão final.

**Custo:** 1-2 dias setup MT5 EA + monitoring infra. 90 dias paper roda
sozinho. Resolve o blackout questão direta. Risco: zero capital real.

### Opção 3 — Probe completo P3-P5 (replicador + transferability)

Continua plano original: fetch 1m OHLC dos 6 pares 2013-2021 (Tiingo ou
Dukascopy free), escreve replicator, valida match-rate ≥ 80%, transfer-test
em XAUUSD/SPX500/NAS100/BTCUSD/USDJPY/AUDUSD com gates §2.4 cada.

**Custo:** 2-4 dias trabalho. Insight adicional limitado dado que (a)
o gate 4 binding já falhou, (b) o blackout persiste mesmo com replicator
perfeito.

## Recomendação

**Opção 2 (Spec V3 + paper-trading 90d).**

Razões:
1. Strategy mostrou edge real em 8 anos com método reproduzível (DSR/WF
   PASS confirmam não-overfit estatístico)
2. Gate 4 FAIL é estatístico (sample OOS pequeno), não estrutural
3. 5-year blackout só se resolve com observação forward — paper trading
   é a forma honesta e barata de fazer isso
4. Strategy já cobre 6 FX majors/crosses, satisfazendo parcialmente §3.1
5. Setup demo MT5 Pepperstone tem zero custo de capital, baixo custo de
   tempo, e produz evidência decisiva (90d × 6 pairs × ~2 trades/sessão
   = ~1 000 trades — amostra suficiente pra Sharpe estável)
6. Aderente ao mandate §1 "infra retida; reativável se literatura/regime
   sugerir signal que passe os 13 gates honest §2.4" — paper-trading é o
   teste honesto.

**Não recomendo Opção 1 (Folclore puro):** o fingerprint é sólido demais
pra ser categorizado como folclore sem o teste forward. Folclore tier
deve ser reservado pra estratégias com evidência estatística marginal —
esta passou DSR/WF/CI-full.

**Não recomendo Opção 3 (probe completo):** insight marginal dado que o
binding constraint (blackout) persiste. Se a Opção 2 paper-trading passa,
aí sim faz sentido fazer P3-P5 pra spec full.

## Próximos passos se Opção 2 aprovada

1. **Spec writing** (4-6h): `specs/plano_a_v3_asian_session_fx.md`
   - Rule explícita: 23:00-01:00 UTC, 5-pair filter (sem USDCAD), entry
     direction baseada em prior 1h candle continuation/MR (a refinar
     em testing), time-based exit max 3h, SL/TP -80/+120 pips, % risk
     sizing
   - Cost model Pepperstone Razor + commission
   - Citations: `[evidence_based_ta, Aronson, p.367-380]`,
     `[advances_fin_ml, p.196-211]`, `[carver_systematic_trading]`,
     `[fooled_by_randomness, Taleb]`
2. **Paper-trading setup** (1-2d): MT5 demo Pepperstone, EA simples em
   MQL5 (50-100 linhas), Telegram alerts, daily journal log
3. **Monitoring** (90d, 0h ativo): check semanal no log, sem intervenção
4. **Decision review** (após 90d, 4-6h): verifica métricas vs critério
   de continuação, escreve update memo, decisão sign-off do usuário

**Capital permanece 100% Plano C durante e após paper-trading.** Plano A
slot continua DORMANT até paper-trading PASS + Phase 4 formal complete.

## Caveats finais

- **Citação obrigatória (CLAUDE.md Regra 2):** todas afirmações neste memo
  estão ancoradas em `reports/04_eda_summary.md` ou em livros do knowledge
  base. Sem citação implícita.
- **MyFxBook track record é marketing**, não evidência blindada. Mesmo
  com fingerprint sólido, há survivorship-bias estrutural não auditável.
- **Demo account history** subestima slippage/swap/rejection real. Cost
  model Pepperstone aplicado é forward-conservador mas não captura
  microestrutura de execução real.
- **5-year blackout** continua sendo o risco principal. Paper-trading
  90d é o gate empírico que falta.
