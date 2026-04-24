# Hunt loop iter 015 — Static synth NTSX (90/60 SPY+IEF) é o NOVO TOPO do loop: 77/100 STRONG, 4/5 winner conditions, DSR é o único bloqueio

**Data:** 2026-04-24 17h04
**Tipo:** Pesquisa em background (mandate §1 segue 100% Plano C; este é
um candidato científico, NÃO autoriza desvio de alocação)
**Iteração:** 015 — Hunt Loop
**Slug:** `return-stacked-static-ntsx`

---

## TL;DR (uma linha)

Pela primeira vez em 15 iterações, uma estratégia bate **+0.10 Sharpe
sobre SPY em TODOS os 3 datasets**, com 9/9 sub-janelas positivas e
estouro de 4 das 5 condições estritas de WINNER — só o gate DSR (com
n_trials cumulativo de 4258) impede WINNER status oficial.

---

## O que mudou na rotina do loop

Depois de 4 overlays consecutivos morrendo na mesma armadilha de
**cointegração com σ²_port** (iter 009 T10Y3M-21d simétrico, iter 012
T10Y3M-5d assimétrico, iter 013 LR meta-label, iter 014 EBP credit),
o BASE_MEMORY já dizia: "iter 015 PRECISA mudar de mecanismo, não
decorar iter 008 de novo". A escolha foi a recomendação primária:
**Option G — Return-Stacked ETF**, na forma mais simples possível:

- **Synth NTSX = 0.90 × SPY + 0.60 × IEF**, peso fixo, rebalanceamento
  diário, single config, NADA de overlay/vol-management/rotação.
- Inspiração: NTSX (WisdomTree, 2018) que empacota 90% S&P 500 + 60%
  futuros UST em um único ETF — alavancagem intrínseca de 1.5×.
- Tese: Asness-Frazzini-Pedersen (2012) — alavancar a base
  diversificada captura mais Sharpe por unidade de risco total do que
  deixá-la sem alavanca. `[risk_parity, p.5]`.

Por construção, o synth NTSX **NÃO TEM σ²_port self-adjustment** (pesos
constantes, nada que reaja a variância). Logo, não pode cointegrar com
nada — a armadilha que matou os 4 overlays anteriores fica inacessível.

---

## Resultado: explosivo nos números, freado pelo DSR

### Sharpe edge (winner condição #1: ≥ +0.10 em pelo menos 2 ds)

| dataset | NTSX synth Sharpe | benchmark | Δ |
|---|---|---|---|
| educational | **0.78** | 0.68 (SPYSIM 40y) | **+0.10** ✓ |
| spy_real | **1.04** | 0.90 (SPY 17y) | **+0.14** ✓ |
| ndx_real | **1.06** | 0.955 (QQQ 16y) | **+0.11** ✓ |

Primeira iteração do hunt loop a bater +0.10 nos **3 de 3 datasets**
(o anterior máximo era 2/3 — iter 006 e iter 008).

### Robustez (G6 + sub-janelas)

| métrica | iter 015 | máximo anterior |
|---|---|---|
| Sub-janelas com Sharpe > 0 | **9/9** | 9/9 (iter 008/010, mas com Sharpe edge 1/3) |
| Bootstrap 99.9% CI low (spy_real) | +0.31 | +0.29 (iter 008) |
| Cross-lib parity G7 (worst) | 0.087 pp | 0.12 pp (iter 010) |

### Score breakdown

| critério | iter 015 | máximo anterior |
|---|---|---|
| 1 Sharpe edge | **25/25** | 20/25 (iter 008/010) |
| 2 Gates | 17/25 | 19/25 (iter 008) |
| 3 DSR | 0/15 | 0/15 (todas as iters) |
| 4 CAGR floor | 15/15 | 15/15 (iter 006+) |
| 5 MDD ceiling | 15/15 | 15/15 (iter 006+) |
| 6 Robustness | **5/5** | 5/5 (iter 008/010) |
| **Total** | **77/100 🥇 STRONG** | 74/100 PROMISING |

**Tier STRONG (75-89)** — primeira vez no loop. Anterior teto era
PROMISING (60-74).

### Winner conditions (estrito)

4 de 5 condições passam:
1. ✅ Sharpe edge em ≥ 2 ds (passa em 3/3)
2. ✅ Gates por ds (5/7, 6/7, 6/7)
3. ❌ **DSR worst p < 0.05** — falha (worst p = 0.548 educational com
   n_trials = 4258)
4. ✅ CAGR floor em ≥ 2 ds (passa em 3/3)
5. ✅ MDD ceiling em ≥ 2 ds (passa em 3/3, ndx por 0.61 pp de margem)

---

## Por que não é WINNER ainda

**Único bloqueio: o DSR (Deflated Sharpe Ratio) com n_trials acumulado
4258.** A fórmula Bailey-López de Prado infla o benchmark de Sharpe
proporcional a √log(N_trials); com 4258 hipóteses já testadas no loop,
o "Sharpe que valeria a pena" exige observar SR ≳ 1.30-1.40 anualizado
no pior dataset. NTSX synth entrega 1.04 no spy_real (melhor real-data).

Isso é o **mesmo teto que segurou iter 008/010 em 74/100**. A diferença
agora é que iter 015 é o primeiro que demonstra que **mudança de
mecanismo escapa da cointegração de variância** — o problema agora é
puramente o accumulator do DSR, não mais a estrutura do mecanismo.

---

## A pegadinha honesta — funding cost

**A NTSX sintética é otimista demais.** O produto real usa futuros UST
para o leg de bonds (não holding direto IEF), o que cobra um custo
implícito de financiamento de ~50-100 bps/ano sobre os 50% de notional
adicional. A versão sintética não modela isso — ela permite que a
perna IEF capture o RETORNO TOTAL do bond ETF, quando na realidade só
captura o RETORNO DO EXCESSO.

Sensibilidade estimada:

| dataset | Sharpe sintético | drag estimado | Sharpe pós-drag | edge pós-drag |
|---|---|---|---|---|
| educational | 0.78 | ~75-100 bps | ~0.71-0.74 | ~+0.03 a +0.06 (ABAIXO de +0.10) |
| spy_real | 1.04 | ~75-100 bps | ~0.97-1.00 | ~+0.07 a +0.10 (BORDERLINE) |
| ndx_real | 1.06 | ~75-100 bps | ~0.99-1.02 | ~+0.04 a +0.07 (ABAIXO de +0.10) |

**Pós custo de financiamento, o produto real provavelmente NÃO bate o
gate +0.10 estrito.** Iter 015 ainda fica como nova alta histórica do
loop, mas a robustez à premissa de funding cost zero é frágil em 2 de
3 datasets.

Iter 016 deve **modelar funding cost explicitamente** (subtrair `0.5 ×
DGS3MO_daily_return`) e re-testar; se o edge pós-cost cai abaixo de
+0.05, o primitivo precisa de uma camada de timing para virar
deployable.

---

## O que isso ensina (a lição que vai pra BASE_MEMORY)

**O teto estrutural do hunt loop não é mais a cointegração — é o
acumulador DSR.** Iter 015 prova:

1. ✅ Mudança de mecanismo PODE escapar da armadilha σ²_port
   (cointegração desaparece quando não existe σ²_port pra cointegrar
   com nada).
2. ❌ Mas o DSR penaliza TODAS as iterações do loop, independente do
   mecanismo. A barreira agora é puramente estatística (n_trials
   acumulado), não mais arquitetural.

Para virar WINNER, precisa-se de:
- **Sharpe uplift adicional** de ~+0.30 sobre o melhor real (1.04 →
  1.34 no spy_real); ou
- **Reset de n_trials** via teste pre-registrado isolado (1 cfg × 1
  dataset, n_trials=1) — não é uma iteração do loop em si, mas uma
  validação de deployabilidade.

---

## Próximas direções (iter 016+)

O BASE_MEMORY já registrou as 3 candidatas, ranqueadas por chance de
clarear o DSR sem reabrir cointegração:

1. **Option P — Static stack × vol-management hybrid** (PRIMARY rec).
   Multiplica o vol-target scaling do iter 008 sobre o peso 90/60 do
   iter 015. Vol-target infla exposição em regime calmo (onde 1.5× é
   conservador) e contrai em estresse. Single cfg pré-comitado;
   uplift esperado +0.05-0.15 Sharpe/ds.
2. **Option Q — Static stack + funding-cost modeling** (ROBUSTNESS).
   Subtrair `0.5 × DGS3MO_daily_return`. Verifica se o edge resiste à
   premissa real do produto NTSX.
3. **Option R — NTSX/NTSI/NTSE regional rotation**. Extensão para 3
   stacked ETFs sintéticos (US/Intl/EM); 12-1 momentum no leg de
   equity de cada. Adiciona eixo regional ortogonal; NÃO é re-teste
   do iter 003 (sectores eram homogêneos; equities regionais têm
   heterogeneidade genuína).

---

## Resumo em uma frase final

**Iter 015 é o primeiro mecanismo do hunt loop que clareia o gate
+0.10 Sharpe em todos os 3 datasets — 4/5 condições estritas de
WINNER passam, score 77/100 STRONG (novo recorde, anterior era 74
PROMISING) — mas o DSR cumulativo continua bloqueando WINNER status
oficial, e a sensibilidade ao funding cost (não modelado) sugere
edge real do produto está mais perto de +0.05 que +0.10.** Próximo
passo: combinar o static stacking com vol-management (Option P) pra
atacar o DSR via uplift de Sharpe.

Mandate §1 inalterado: 100% Plano C MAINTENANCE. Esta iteração produz
**candidato científico**, não autoriza desvio de alocação. Override
permanece exigido por mandate §7.

Ver `studies/strategy_hunt_loop/iterations/015-2026-04-24-1704-return-stacked-static-ntsx/`
para detalhes técnicos completos (hypothesis.md, results.json,
verdict.json, final_report.md).
