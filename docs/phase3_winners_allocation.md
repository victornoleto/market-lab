# Phase 3 winners — allocation & multi-strategy clarification

**Path:** [SWING BROKER] (Plano B, broker BR, no swap, 15 % BR capital-gains tax).
**Scope:** how to deploy the three Phase 3 winners in production capital.
**Date:** 2026-04-17 (end of Phase 3.5b validation loop).
**Source of numbers:** `reports/phase3_5b/summary.json` (common window
`2004-11-18 → 2026-04-14`, 5 383 daily bars, tax-per-leg 15 %, real slippage 5 bp
round-trip, commission 10 bp round-trip).

---

## 1. User question and answer

> **"São 3 strategies paralelas?"**
>
> **Resposta curta: NÃO.** O alvo de produção é **UM portfólio 3-leg
> equal-weight (EW)**, rebalance diário a (1/3, 1/3, 1/3). Você vê até
> 3 ordens simultâneas (uma por perna), mas é **uma única decisão de
> allocation** — não 3 estratégias concorrendo por capital.

Rationale documentado em `reports/phase3_5b/robustness/allocation_comparison.md`
(Task 7d) e em `reports/phase3_5b/robustness/rolling_correlation.md` (Task 7e):

- A correlação rolling entre as 3 pernas nunca excedeu 0.70
  simultaneamente por ≥ 10 barras em 21 anos (2008, 2020, 2022 inclusos).
  **GLD é o diversificador real** (ρ_252d vs LETF ≤ 0.305; vs QQQ ≤ 0.228).
- EW venceu IVP / HRP / ERC / MV em OOS Sharpe (2.301 vs 2.024-2.283) e
  mantém o maior CAGR (25.56 % vs 15-21 %). DR sobe com HRP mas a
  margem dupla exigida (ΔSharpe ≥ +0.05 **E** ΔDR ≥ +0.05, regra
  `[advances_fin_ml, p.298-299]`) não foi superada — **EW é o incumbente
  de produção**.
- MV long-only zerou a perna LETF (caso de borda clássico do Markowitz
  com amostra ruidosa `[advances_fin_ml, p.271-273]`).

---

## 2. Números de referência (janela comum 2004-11-18 → 2026-04-14)

| Configuração                    | CAGR   | Sharpe | Max DD  | Trades | Observação                        |
| ------------------------------- | ------ | ------ | ------- | ------ | --------------------------------- |
| **Portfolio 3-leg EW (alvo)**   | 25.56 %| 2.108  | 10.86 % | 259    | produção                          |
| LETF rotation EMA100/2x (sozinho, mesma janela) | 29.06 %* | 1.724* | ~20 %  | ~200  | maior CAGR, Sharpe menor          |
| QQQ Donchian 20/10              | 17.40 %| 1.389  | 12.79 % | 107    | média perna                       |
| GLD Donchian 40/20              | 11.46 %| 0.937  | 14.35 % | 48     | perna "diversificadora"           |
| SPY buy & hold (benchmark)      | 10.66 %| 0.629  | 55.20 % | —      | referência                        |

\* LETF rotation na **janela longa** (1970 → 2026) tem CAGR 44.69 % e
Sharpe 1.85 `[reports/phase3_5b/letf_rotation_ema100_2x/summary.json]`; na
janela comum (desde 2004-11-18) os números caem para os valores acima
(OOS Sharpe 1.724 reportado em `jornada/2026-04-17-0055-b1c-letf-rotation-gates-PASS.md`).
Para comparação apples-to-apples com o portfólio, usar a janela comum.

O **excess CAGR do portfolio vs SPY é +14.90 pp** com Max DD −44.35 pp
(10.86 % vs 55.20 %). Information Ratio vs SPY = **0.722**; β_SPY = 0.321
(exposição direcional reduzida — o regime filter do LETF e a natureza
breakout de QQQ/GLD cortam parte do beta).

---

## 3. Alternativas consideradas (e por que não recomendadas)

### 3.1 Rodar **só LETF rotation EMA100/2x**

- **Pró:** maior CAGR isolado (janela comum ~29 %, janela longa ~44.69 %).
- **Contra:** Sharpe cai de 2.108 → 1.724-1.85; Max DD sobe de 10.86 %
  → 20.55 % (janela longa). Exposição concentrada em 1 único factor
  (equity on-regime com alavancagem 2×).
- **Veredito:** **não recomendado** — perde diversificação e sofre mais
  em 2008/2020 isolado (ver `reports/phase3_5b/robustness/stress_isolated.md`).
  O prêmio de +3.5 pp CAGR não compensa a degradação de Sharpe e DD.

### 3.2 Rodar as 3 pernas como **3 contas separadas** (sem rebalance)

- **Pró:** operacionalmente mais simples — cada perna é uma conta de
  broker independente.
- **Contra:** você **perde o benefício de rebalance diário**. Sem
  rebalance, a perna mais performática (LETF) domina o capital ao
  longo do tempo, e o portfólio converge para 100 % LETF — exatamente
  o caso 3.1 com disfarce.
- **Veredito:** **não recomendado** — apenas simula o caso 3.1 com
  drift.

### 3.3 Promover **HRP ou ERC** em vez de EW

- **Pró:** DR ligeiramente maior (HRP 1.456 vs EW 1.376).
- **Contra:** OOS Sharpe fica ≤ EW (HRP 2.186, ERC 2.283, EW 2.301) e
  CAGR cai 4-10 pp (pesos defensivos concentram em GLD). Margem dupla
  exigida `[advances_fin_ml, p.298-299]` **não disparou**.
- **Veredito:** **não recomendado** — estimation noise no Σ fitado em
  IS pequena compensa o ganho de DR. EW é o default robusto.

### 3.4 Vol-target 10 % no portfolio

- **Pró:** configuração `L63_cap3.0` entrega OOS Sharpe +0.18 e CAGR
  +0.26 pp vs EW.
- **Contra:** MaxDD −32 % — i.e., pior (portfolio já vive em
  volatilidade anualizada ~11 %, o alvo 10 % apenas deforma sizing sem
  ganho de risco-ajustado). Margem dupla não atingida.
- **Veredito:** **não recomendado como padrão**, mas pode ser
  variante defensiva opcional para agressão-controlada `[systematic_trading_carver, p.107-111]`.

---

## 4. Proporção no capital total (mandate rule 1)

O **Investment Mandate** (`docs/investment-mandate.md`, §1) define:

- **60-80 % do capital** em passive buy & hold (Plano C, aposentadoria —
  ver `portfolio-aposentadoria.md`).
- **20-40 % do capital** é o bolso ativo, dividido entre:
  - **Strategy A (Plano A)** — Pepperstone CFD short-hold, agressiva
    alavancada (target 5-10 %/mês, **Phase 3.5a** ainda caçando).
  - **Strategy B (Plano B, ESTE doc)** — swing broker BR, moderada.

Dentro da **quota de Plano B** → **100 % no portfolio 3-leg EW**. O
EW (1/3, 1/3, 1/3) é **dentro do portfolio**, não do capital total.

A divisão A/B dentro da quota ativa é decisão separada (depende do
Sharpe relativo e da correlação entre A e B; Plano A ainda está em
exploração). Default conservador enquanto A não tem winner: **100 %
da quota ativa em Plano B** (3-leg EW). Migrar parcial para Plano A
assim que Phase 3.5a entregar um winner com Sharpe > 1.5 e
ρ_252d < 0.4 vs este portfolio.

---

## 5. Exemplo numérico — $10 000 de capital total

Supondo 30 % em Plano B (ponto médio da banda 20-40 % do mandate):

| Nível                        | Alocação                      | $ em USD |
| ---------------------------- | ----------------------------- | -------- |
| Capital total                | —                             | 10 000   |
| Plano C (aposentadoria B&H)  | 70 %                          |  7 000   |
| **Plano B (portfolio 3-leg)**| **30 %**                      | **3 000**|
| ↳ perna LETF (UPRO/SSO)      | 33.3 % de $3 000              |  1 000   |
| ↳ perna QQQ Donchian 20/10   | 33.3 % de $3 000              |  1 000   |
| ↳ perna GLD Donchian 40/20   | 33.3 % de $3 000              |  1 000   |

**Operacionalmente:** 1 conta de broker BR, 3 tickers acompanhados
diariamente. Quando o regime filter ou o Donchian dispara → 1 ordem
na perna relevante. Rebalance diário significa que ao fim de cada dia
os pesos voltam a (1/3, 1/3, 1/3) dentro da parcela de $3 000 — se o
rebalance diário for operacionalmente inviável, rebalance **semanal**
é aceitável com degradação mínima (backtest não cobre weekly, mas a
teoria de rebalance `[expected_returns_ilmanen, p.482-485]` diz que
weekly ≈ daily para vol baixo).

**Proporção do capital total efetivo em cada perna: 10 %** ($1 000 de
$10 000). Para quem opera $1 000 (mandate: capital mínimo viável),
Plano B = $300, ou seja **$100 por perna** — abaixo do lot size
prático de alguns brokers BR. Nesse regime, **colapsa para só LETF
rotation** (o winner isolado), aceitando a degradação de Sharpe até
o capital crescer para >$3 000 em Plano B.

---

## 6. IR 15 % BR e swap — modelagem

- **15 % de IR sobre venda lucrativa** é aplicado **por venda**, não
  por agregado mensal. Perdas não compensam no modelo (worst-case;
  real BR compensa intra-mês, pode melhorar ~0.5-1 pp CAGR).
- **Swap = 0** — broker BR não cobra overnight; é a principal razão
  de o LETF rotation funcionar no Plano B (em Pepperstone CFD o swap
  mataria o hold ≤ dias, por isso LETF vive no Plano B e não no A).
- **Slippage 5 bps + commission 10 bps round-trip** já modelados.
  Sensitivity em `reports/phase3_5b/robustness/slippage_sensitivity.md`
  mostra −0.005 Sharpe/bp até 10 bps (imune operacionalmente).

---

## 7. Checklist operacional para go-live Plano B

- [ ] Abrir conta broker BR (XP, Clear, Inter, BTG — qualquer um com
      ETFs listados ou acesso a US via BDR/corretora internacional BR).
- [ ] Confirmar acesso a: **UPRO ou SSO** (LETF perna), **QQQ** (ou QQQM),
      **GLD** (ou IAU). BDRs BR cobrem QQQ/GLD; SPY leverage via BDR não
      existe — usar corretora internacional ou SSO via BDR se disponível.
- [ ] Script diário que computa sinal (≤ 1 minuto wallclock) e emite
      ordens de rebalance.
- [ ] Monitorar correlação rolling 63d/252d (alerta se 3 ρ ≥ 0.70 por
      ≥ 10 barras — evento inédito nos 21 anos de backtest).
- [ ] Reavaliar allocation a cada 12 meses com margem dupla
      `[advances_fin_ml, p.298-299]` sobre última janela disponível.

---

## 8. Referências internas

- Winner config cards:
  - `jornada/2026-04-17-0055-b1c-letf-rotation-gates-PASS.md`
  - `jornada/2026-04-17-0120-a3b-tsmom-donchian-per-asset-PASS.md`
  - `jornada/2026-04-17-0040-a3d-3leg-letf-qqq-gld-PASS.md`
- Reports full Phase 3.5b: `reports/phase3_5b/{letf_rotation_ema100_2x, qqq_donchian_20_10, gld_donchian_40_20, portfolio_3leg_ew}/`
- Robustness: `reports/phase3_5b/robustness/` (stress, slippage,
  allocation, correlation, vol-target).
- Book pillars: `books/summaries/leverage_for_the_long_run.md` (LETF
  rotation), `books/summaries/stocks_on_the_move.md` +
  `books/summaries/following_the_trend.md` (Donchian breakout), e
  `books/summaries/advances_fin_ml.md` (gates, PBO/DSR/WF,
  margem-dupla).
