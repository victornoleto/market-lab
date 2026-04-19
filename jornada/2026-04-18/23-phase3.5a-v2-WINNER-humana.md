# [SHORT-HOLD CFD] A jornada V1 → V2 em linguagem humana — achamos o Plano A

**Data:** 2026-04-18/19
**Narrativa:** complementar ao T7 técnico. Esta jornada é pra você ler em
6 meses e lembrar **o arc completo** — não só os números finais.

---

## O que aconteceu em 1 parágrafo

Comecei o dia com Plano B já validado (winner 3-leg EW, CAGR 25.56%,
Sharpe 2.25) mas sem Plano A. Lancei um loop autônomo (Phase 3.5a V1)
pra achar o Plano A em 1h FX retail — **deu 0 winners em 42 iters e 143
runs**. O agente concluiu "abandona Plano A". Eu quase aceitei. Mas
percebemos juntos que o framework V1 estava **estruturalmente errado**
(1h é o pior timeframe pra retail, hold curto **amplifica** custo em vez
de reduzir, universe pequeno demais). Corrigimos, redigimos Phase 3.5a
V2 como "última tentativa", lançamos outro loop autônomo com framework
novo. V2 rodou **82 iters e 58 runs** em 6 famílias diferentes —
**5 morreram, 1 venceu decisivamente**: `gayed_ema100_L2_off_gld`.
Sharpe OOS 2.285, CAGR 79% líquido, MaxDD -21%, passa todos os 13
gates (PBO, DSR, walk-forward, bootstrap). **Plano A sobrevive.**

---

## A parte mais importante: o erro de framing do V1

V1 rodou com premissas herdadas do mandate original:
- *"Plano A tem que ser 1h intraday"* (assumido, nunca testado)
- *"Hold curto pra evitar swap"* (intuição **errada** — explico abaixo)
- *"Universe pequeno = focado"* (fraco pra breadth Carver requer)
- *"CAGR 60-120%/yr é o target"* (fantasia)

V1 falhou — **corretamente**. Os gates fizeram o trabalho que deveriam.
O agente autônomo escreveu T6 "abandone Plano A" com razão: **no
framework V1, Plano A era impossível**.

O que mudou: **nossa conversa identificou que o problema era o framework,
não o Plano A.** V1 testou "1h FX com hold curto" e falhou. Mas nada no
mandate exigia 1h; era interpretação operacional herdada. Quando abri o
espaço pra **qualquer timeframe que passe gates**, V2 tinha uma chance.

---

## A intuição que estava invertida: "rápido = barato"

Antes do V1, eu acreditava:
> *"Holds curtos minimizam swap, que é o pior inimigo. Então 1h é ótimo."*

Isso parece senso comum. **Mas é matematicamente errado em retail.**

Decomposição do custo por trade:

| Componente | Aplica quando | Valor típico |
|------------|--------------|--------------|
| Spread (bid-ask) | Toda entrada+saída | 4-10 bps round-trip |
| Commission | Toda trade | 3-5 bps round-trip |
| Slippage | Toda execução | 1-3 bps round-trip |
| **Subtotal frictions** | **Por trade** | **~8-18 bps** |
| Swap overnight | Só se hold ≥ 1 dia útil | 0.5-2 bps/dia |

**Os primeiros 3 são FIXOS por trade, independente do hold.**
**Swap é o único que escala com tempo.**

Implicação:
- **1h hold:** frictions 8-18 bps vs edge médio 3-5 bps/trade → **edge negativo**
- **daily hold:** frictions 8-18 bps vs edge médio 50-150 bps/trade → **edge sobra**
- **weekly hold:** frictions 8-18 bps vs edge médio 200-500 bps/trade → **frictions viram ruído**

Carver `[systematic_trading, p.185-188]` diz isso **literalmente**:
> *"For retail systematic trading, the optimal hold is 1-4 weeks
> because that's where spread cost becomes negligible relative to
> move size."*

**O swap não é o inimigo principal — spread+commission é.** E eles
pesam MAIS quando hold é curto, não menos.

Esta foi **a descoberta conceitual mais importante da sessão.** V2
incorporou isso invertendo a regra: em vez de "hold ≤ 5 days", virou
"hold ≥ 3 days".

---

## O winner: "é um Plano B alavancado via CFD"

Vou ser honesto: o V2-L2 winner **não é alpha novo**. É o **Gayed
regime rotation** (mesma ideia do Plano B) aplicado em **SPY+QQQ via CFD**
com leverage 2×, em vez de LETFs (SSO/QLD) como Plano B faz.

### Como Plano A V2 difere do Plano B

| Dimensão | Plano B (3-leg EW) | Plano A V2 (winner) |
|----------|---------------------|---------------------|
| Signal | EMA-100 regime (SSO) + Donchian (QLD) + Donchian (UGL) | **EMA-100 regime** (SPY) apenas |
| Risk-on composição | SSO + QLD + UGL equal-weight (LETFs 2×) | SPY + QQQ 50/50 (CFD 2×) |
| Risk-off | Mantém 3-leg sempre (UGL carrega) | 100% GLD (sai de tudo mais) |
| Broker | Banco Inter Global (ETF shares reais) | Pepperstone SCB (contratos CFD) |
| Leverage mechanism | Embutido no LETF (SSO é 2× interno) | Margin CFD (deposita 5%, controla 2×) |
| Custo anual carry | ~1.4% (expense + drag) | ~4% (swap) |
| CAGR OOS | 25.56% | 79.14% |
| Sharpe OOS | 2.251 | 2.285 |
| MaxDD | -10.86% | -21.02% |

**O CAGR 3× maior do A sobre B vem de:**
1. **Sem LETF drag** — CFD é leverage linear, LETF tem path dependency
2. **2× em SPY+QQQ agregado** vs 2× em SSO (SPX só) + QLD (NAS só) separado
3. **Janela OOS 2018-2023** foi bull forte — amplifica leverage

**O Sharpe similar (2.28 vs 2.25)** é a pista crítica: **o edge fundamental
é o mesmo em ambos.** Gayed 2016. Só o mecanismo de alavancagem muda.

### Por que isso importa (caveat de portfolio)

Se você operar **A e B juntos** como mandate §1 prevê (50/50 do bucket
ativo), eles **não são 2 edges independentes** — são o mesmo edge
executado em 2 mecanismos diferentes. Em crash de mercado, ambos caem
juntos. A "diversificação dual-path" é operacional (2 brokers, 2 jurisdições)
mais que estatística.

V2 tentou achar um **segundo edge independente** (L3 AFML meta-label,
L5 equity pairs, L6 vol breakout — todos DEAD). **Não existe na janela
testada.** Então portfolio A+B não é ideal mas é o melhor que temos.

---

## CFD vs LETF — entender isso é crítico

Expliquei na conversa e documento em `docs/strategies/plano_a_v2_l2_gayed_cfd.md` §3,
mas vale repetir em linguagem simples.

### Plano B — LETF (Banco Inter)

Você **compra shares de verdade** do SSO. SSO é um ETF que internamente
usa swaps e futuros pra ter exposição dobrada a SPY.

```
Capital: $10.000
Comprou: $10.000 de SSO (shares reais, custody Apex Clearing)
Exposição efetiva: $20.000 (SSO é 2× internamente)
Você é dono das shares. Ninguém pode te tirar elas.
```

### Plano A V2 — CFD (Pepperstone)

Você **não compra nada** — abre um **contrato** com a Pepperstone que
espelha o preço de SPY.

```
Capital: $10.000
Abriu: CFD "SPY long" nominal $20.000 (alavancagem 2×)
Margem bloqueada: $1.000 (5% do nominal)
Capital livre na conta: $9.000 (buffer contra margin call)
Você tem um contrato, não shares. Pepperstone é tua contraparte.
```

### A diferença que importa pra você

- **Capital usado:** LETF bloqueia os $10k inteiros. CFD bloqueia só $1k.
  Com CFD você teria $9k livres na conta. Mais flexibilidade.
- **Custo de carry:** LETF tem drag embutido (~1.4%/yr). CFD tem swap
  diário (~4%/yr). **LETF é mais barato pra carry** em horizontes longos.
- **Risco de contraparte:** LETF você é dono das shares (se Inter quebra,
  você tem as shares em DTC custody). CFD você tem um passivo da
  Pepperstone (se Pepperstone quebra, você vira credor).

**Nem um nem outro é "melhor" — são trade-offs.** O V2-L2 escolhe CFD
porque libera capital pra flexibility + evita LETF vol decay em choppy markets.

---

## O que isso significa pra execução real

O Plano A V2 **não vai ser operado amanhã**. Phase 4 é paper trading
por 3 meses antes de qualquer dólar real. Razões:

1. **Gayed + leverage é matematicamente previsível, mas live ≠ backtest.**
   60-80% dos winners de backtest falham na primeira onda live (`[systematic_trading, ch.14-15]`).
   Gap vem de: slippage maior que modelado, latência de signal, whipsaws
   não-modelados, spread widening em news.
2. **Pepperstone swap real pode ser pior que modelado.**
   Backtest assumiu 0.005-0.02%/dia. Pepperstone 2026 em SPY share CFD
   é ~5.5%/yr = ~0.021%/dia, no topo do range. Se Fed eleva juros,
   swap sobe; strategy degrada.
3. **Preciso validar que SPY/QQQ share CFD está disponível na minha conta.**
   Alguns tiers Pepperstone Brasil só têm índices (US500/USTEC) — fiel
   ao backtest mas com dividend adjustment diferente.

Por isso Phase 4 é 3 meses paper: valida que todos esses são ±20%
do backtest antes de live.

---

## O que V2 provou que é estrutural (não só este winner)

Três lições meta do loop V2 que vão além do winner específico:

### 1. Especificar o espaço certo > varrer mais configs

V1 varreu 143 configs em 5 famílias, zero PASS. V2 varreu 58 configs em
6 famílias, 1 PASS. **V2 usou MENOS configs e achou winner.** Diferença:
V2 especificou o espaço correto antes de varrer (timeframe livre, hold
correto, universe amplo). Lição: quando você está zero em N iters,
**pare de varrer e revise o espaço de busca.**

### 2. Regime-driven é a única família viável em Plano A retail

Das 6 famílias V2 testadas:
- ✅ Regime rotation (V2-L2) — 1 PASS
- ❌ TSMOM (V2-L1) — swap drag 74-166%
- ❌ AFML meta-label (V2-L3) — meta é filtro, não edge
- ❌ Carver RP blend (V2-L4) — só L2 positivo, blend dilui
- ❌ Kalman pairs (V2-L5) — 0/6 cointegrados no universe Pepperstone
- ❌ Vol breakout (V2-L6) — 12/12 OOS Sharpe NEGATIVO em 2022-2024

Combina com V1 (onde BollingerMR GARCH — uma variante de regime-like
vol-size — foi a única que mostrou edge). **Para retail CFD daily-to-weekly,
só regime-driven passa.** Isso é uma descoberta estrutural valiosa.

### 3. Gates PBO/DSR funcionam — não são só "academia"

Em V1: 143 runs, PBO e DSR rejeitaram 100% dos "best" candidates. Em V2: 58 runs, PBO 0.103 e DSR p 0.000288 do winner ainda passaram **com folga material** (5-170× abaixo dos thresholds). Isso **não é sorte** — é o gate working as designed. Configs que não passam merecem ser rejeitadas.

**Sem esses gates, eu teria declarado winner 10× na V1** com base em backtests IS-limpos que não sobrevivem deflation. O gates são a razão de eu poder confiar no V2 winner.

---

## Próximo passo concreto

1. **Phase 4 paper trading** — `specs/phase_4_paper_trading.md` (escrito pelo agente T7)
2. **4 meses calendário** (1 build + 3 observation paper)
3. **Se paper passa gates:** Phase 5 live com capital pequeno ($1k → $5k → escala)
4. **Se paper falha:** diagnosticar (bug? cost mis-calibrado? signal lag?) + 1 mês fix re-paper + se falhar de novo → abandono Plano A, foco em Plano B
5. **Proibido V3** por contrato — V2 é a última tentativa de busca

---

## Lição meta pessoal

Eu quase aceitei o "abandon Plano A" autônomo do V1. A conversa que
tivemos — questionando o framing, desconstruindo a intuição "hold curto
= barato", identificando os erros herdados do mandate original —
**salvou o Plano A**. O agente autônomo é bom em executar specs, mas
ruim em **questionar o próprio spec**. Essa camada de reflexão é
humana + assistant-em-diálogo, não autônoma.

Guardar pra futuro: **quando um loop autônomo te der veredict
definitivo de "desista", pergunte antes 'isso é verdade no espaço
correto?'**. Às vezes o que falha é o espaço especificado, não a tese.

---

## Artefatos gerados nesta jornada

**Specs:**
- `specs/phase_3_5a_v2.md` (522 linhas — escrito pelo assistente em diálogo com usuário)
- `specs/phase_4_paper_trading.md` (270 linhas — escrito pelo agente autônomo T7)

**Strategies:**
- `docs/strategies/plano_a_v2_l2_gayed_cfd.md` (living doc — didático + operacional)

**Jornadas:**
- `2026-04-19-0020-phase3.5a-v2-L2-gayed-transported-PASS.md` (winner PASS — escrito pelo agente)
- `2026-04-19-0510-phase3.5a-v2-summary-WINNER-FOUND.md` (summary técnico — escrito pelo agente)
- `2026-04-18-1900-phase3.5a-v2-WINNER-humana.md` (**este arquivo** — jornada humana complementar)

**Reports:**
- `reports/phase3_5a_v2/AGGREGATE.md` (cross-lead)
- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/AGGREGATE.md` (L2 details)
- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_gld.{json,md}` (winner metrics)

**Code:**
- `src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` (strategy impl)
- `src/ai_trade/backtest/sweeps/registry.py` (fan-out infra, reusado em V2)

**Documentos updated:**
- `docs/investment-mandate.md §7` (3 entries novas: V1 close, V2 launch, V2 close com winner)
- `docs/self_improvement/memory.md` (`winners_short_hold` ganhou entry V2-L2, status done, phase 3.5a-v2-COMPLETE)

---

**Plano A encontrado. Plano B permanece. Phase 4 começa.**
