# c01 SMA200 Binary Regime — Agregador: DEAD END (0/12) [SWING BROKER]

**Fase:** 3.5e breadth-hunt | **Lead:** c01_sma200_binary_regime | **Iter:** 19

---

## O que foi testado

A config c01 é o "canônico do Gayed": quando o SPY fecha acima da sua média móvel de 200 dias (SMA200), o portfólio fica 100% no LETF escolhido; quando cai abaixo, migra para o "off-leg" (caixa, ouro ou TLT). Testamos todas as combinações possíveis dentro do universo do Phase 3.5e:

- **4 ativos:** QLD (2×QQQ), SSO (2×SPX), TQQQ (3×QQQ), UPRO (3×SPX)
- **3 off-legs:** cash, GLD, TLT
- **12 trials no total** — janela comum 2004-2026 (~21 anos)

## O que encontramos

**PBO agregado (N=12): 0.139 — PASS.** O sinal SMA200 não é ruído: há consistência real entre IS e OOS ao longo dos 12 trials. A família não está "overfitada". `[advances_fin_ml, p.208-211]`

**Resultado econômico: 0/12 pre-pass.** Todo trial falha em pelo menos FWD + Calmar + Sharpe_net.

| Ativo | Melhor off-leg | CAGR_net | Sharpe_net | Calmar | Gate crítico |
|-------|----------------|----------|------------|--------|--------------|
| QLD   | GLD            | 17.5%    | 0.660      | 0.400  | FWD=-0.25 ✗ |
| TQQQ  | GLD            | 22.2%    | 0.642      | 0.409  | FWD=-0.40 ✗ |
| SSO   | GLD            | 11.8%    | 0.550      | 0.326  | FWD=-0.49 ✗ |
| UPRO  | GLD            | 14.6%    | 0.536      | 0.323  | FWD=-0.72 ✗ |

## Por que tudo falha: o choque de tarifas de 2026

O gate FWD mede o desempenho nos últimos 63 dias de pregão (~1 trimestre). Em Jan-Apr 2026, Trump anunciou tarifas agressivas que causaram uma queda brusca no SPX. O sinal SMA200 ativou a saída do LETF — correto pelo design — mas o mercado caiu tão rápido que o off-leg também sofreu. Resultado: todos os 12 FWD Sharpes negativos (pior: UPRO/TLT a -1.12).

**Isso é falha da estratégia ou falha estatística?**

O WF (walk-forward) passa em 7-8/8 splits para todos os configs — ou seja, o sinal gerou alpha consistente em 8 janelas diferentes ao longo de 21 anos. O FWD é um stress test do trimestre mais recente, que coincidiu com uma das maiores crises de política comercial da década. A estratégia funciona como projetada; o problema é que o choque de 2026 é um evento tail que qualquer estratégia de longa vai sofreR.

**Implicação prática:** a estratégia c01 tem edge econômico real (CAGR_net 12-22%, consistente) mas não sobrevive ao gate FWD no período atual. Isso não invalida a família — significa que próximos configs com MAs mais curtas (c02 SMA150, c03 EMA100) podem sair mais rápido e talvez sobreviver ao choque.

## Padrões identificados

1. **GLD é o melhor off-leg** em todas as 4 assets — consistente com Gayed `[leverage_for_the_long_run, ch.2]`.
2. **TLT é o pior off-leg** — adiciona falhas de OOS e DSR por cima da falha FWD (crash de bonds 2022).
3. **QQQ-based (QLD/TQQQ) > SPX-based (SSO/UPRO)** em Sharpe_net — NDX outperforms SPX com SMA200 signal.
4. **2× ≈ 3×** no gap de Sharpe_net: QLD (0.660) vs TQQQ (0.642), diferença de apenas 0.018.
5. **Calmar universalmente <0.5** — o problema não é só FWD, é que as drawdowns absolutas dos LETFs (40-72%) tornam o ratio CAGR/MaxDD baixo mesmo quando o sinal funciona.

## Próximo passo

**c02 — sma150_cash:** MA mais curta (150 dias) com off-leg em caixa. Hipótese: saída mais rápida reduz as drawdowns em crises rápidas como 2026. Mais noise (mais toggling), mas talvez salva o Calmar. `[leverage_for_the_long_run, p.30]`

---

Relatório completo: `reports/phase_3_5e/c01_sma200_binary_regime/AGGREGATE.md`
