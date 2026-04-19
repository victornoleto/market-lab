# A3c portfolio LETF + QQQ Donchian — PASS Sharpe, FAIL DR

`[SWING BROKER]` — Phase 3 Lead A3c, iter 37 (2026-04-17 00:30).

## TL;DR

Combinei as duas strategies PASS de Path B num único portfolio Path B e testei
se a soma vira maior que a parte. **O blend equal-weight aumenta o OOS Sharpe
de 1.990 (LETF sozinho) para 2.098 — uma melhora consistente** — mas a
**diversification ratio parou em 1.12, abaixo do threshold mandate de 1.2**.
Portanto o portfolio `{LETF EMA100/2x, QQQ Donchian 20/10}` **não qualifica
como "winner de portfolio"** pela regra do mandate: ganha Sharpe marginal, mas
as duas pernas são correlacionadas demais (Pearson ρ=0.555, ambas são trend-
following em equity US) pra pagar o custo de complexidade operacional.

**Recomendação de produção:** rodar **só a LETF rotation EMA100/2x** até
aparecer uma segunda Path B genuinamente descorrelacionada (candidatos: TLT
MA rotation, gold momentum, bond-equity regime switch). A QQQ Donchian fica
como *cross-check científico* — o edge existe mas não adiciona diversificação
material a quem já tem LETF rotation.

## O que fiz

Escrevi o módulo `src/ai_trade/backtest/grid/portfolio_combiner.py` que:

1. Alinha duas séries diárias de retorno líquido em dates comuns.
2. Testa 4 famílias de blend, cada uma com justificativa citada:
   - `equal_weight` 50/50 — naive benchmark, imune a estimation error
     `[advances_fin_ml, p.298-299]`.
   - `ivp_static` — Inverse Variance Portfolio com σ calculado apenas na
     janela IS. Para 2 ativos, HRP colapsa para IVP (um split apenas),
     logo a fórmula é `w₁ = σ²₂ / (σ²₁ + σ²₂)`
     `[advances_fin_ml, p.307-308]`.
   - `ivp_rolling` — IVP com σ rolling 63d usando janela passada (`shift(1)`
     pra evitar look-ahead).
   - `mvp_static` — minimum-variance 2-asset long-only com σ/ρ do IS.
3. Calcula Diversification Ratio `DR = (w₁σ₁ + w₂σ₂) / σₚ` (Choueifaty-
   Coignard 2008, prática padrão no arcabouço HRP/IVP do AFML ch.16).
4. Aplica a bateria de gates A3c: OOS Sharpe > max(leg OOS), DR > 1.2, DSR
   p<0.05 (n_trials=4), WF ≥6/8 + MaxDD≤25% por janela, OOS>0, Stress>0,
   bootstrap 99.9% CI lower > 0.

Testes: `tests/test_portfolio_combiner.py` — 18 testes (align, blends,
weights, DR properties, gate serialization). Pytest baseline 517 → 535.

Script: `scripts/run_a3c_portfolio.py` orquestra LETF rotation (EMA100 band
0% lev 2x, Lead B1c winner iter 32) + QQQ Donchian (entry 20, exit 10, Lead
A3b winner iter 36) na janela comum.

## Dados e janela

Hard rule Phase 3 — usar o maior histórico disponível. A LETF rotation roda
sobre SPX TR 1970-01-02 → 2026-04-14 (Kalman + Tiingo stitched, 14191 bars).
A QQQ Donchian roda sobre Tiingo daily 2001-05-14 → 2026-04-14 (6266 bars).
**Janela comum = QQQ Tiingo start ⇒ 2001-05-14 → 2026-04-14 (6266 bars,
~24.9 anos).**

Splits mutuamente exclusivos (60/25/15, mesma convenção A3b):
- IS: 2001-05-14 → 2016-04-25
- OOS: 2016-04-26 → 2022-07-18
- Stress: 2022-07-19 → 2026-04-14

## Resultados

### Pernas sozinhas na janela comum OOS

| Leg                     | IS Sharpe | OOS Sharpe | Stress Sharpe | OOS CAGR |
|-------------------------|-----------|------------|----------------|-----------|
| LETF EMA100 band=0 lev=2x | 1.754   | **1.990**  | 1.968          | 51.21%    |
| QQQ Donchian 20/10      | 1.180     | 1.738      | 1.710          | 20.38%    |

**Baseline OOS Sharpe = 1.990** (LETF domina; o "1.738" da A3b era na janela
A3b, não na comum — janela fair-play muda o baseline para 1.990).

### Blends na mesma janela

| Blend            | Weights (LETF, QQQ) | OOS Sharpe | Str Sh | OOS CAGR | DR    | ρ(full) | DSR p  | WF     | MDD(OOS) | Verdict            |
|------------------|---------------------|------------|--------|-----------|-------|---------|--------|--------|-----------|--------------------|
| equal_weight     | (0.500, 0.500)      | **2.098**  | 2.063  | 35.45%    | 1.121 | 0.555   | 0.0001 | 8/8    | -14.41%   | FAIL (DR ≤ 1.2)    |
| ivp_static       | (0.250, 0.750)      | 2.042      | 1.996  | 27.82%    | 1.124 | 0.555   | 0.0001 | 8/8    | -12.44%   | FAIL (DR ≤ 1.2)    |
| ivp_rolling      | (0.249, 0.751) avg  | 1.876      | 1.921  | 25.05%    | 1.124 | 0.555   | 0.0004 | 8/8    | -12.77%   | FAIL (Sharpe, DR)  |
| mvp_static       | (0.047, 0.953)      | 1.820      | 1.784  | 21.76%    | 1.035 | 0.555   | 0.0004 | 8/8    | -10.83%   | FAIL (Sharpe, DR)  |

**Winner blend:** nenhum (4/4 FAIL).

### Gates detalhados

| Gate                     | equal_weight | ivp_static | ivp_rolling | mvp_static |
|---------------------------|--------------|------------|-------------|------------|
| OOS Sharpe > 1.990        | ✅ 2.098     | ✅ 2.042   | ❌ 1.876    | ❌ 1.820   |
| DR > 1.2                  | ❌ 1.121     | ❌ 1.124   | ❌ 1.124    | ❌ 1.035   |
| DSR p < 0.05              | ✅ 0.0001    | ✅ 0.0001  | ✅ 0.0004   | ✅ 0.0004  |
| WF ≥ 6/8 + MDD ≤ 25%      | ✅ 8/8       | ✅ 8/8     | ✅ 8/8      | ✅ 8/8     |
| OOS Sharpe > 0            | ✅           | ✅         | ✅          | ✅         |
| Stress Sharpe > 0         | ✅           | ✅         | ✅          | ✅         |
| Bootstrap 99.9% CI > 0    | skip (earlier fail) | skip | skip | skip |

## Interpretação

### Boa notícia

O blend equal-weight aumenta o OOS Sharpe de 1.990 para 2.098 (+5.4%) e a
MaxDD cai de um número alto (LETF -23% histórico) pra -14.41%. O blend NÃO
destrói alpha — produz Sharpe > melhor perna e MDD menor. **Isso contradiz
a conclusão B2 iter 34 que dizia "blend destroys alpha"**: o blend B2 era
LETF vs ETFRotation-top1 (ρ=0.44), e lá o ETFRotation era leg fraca. Aqui
as duas pernas são fortes independentemente.

### Má notícia

A diversification ratio fica em 1.12, abaixo do 1.2 do mandate. O motivo é
direto: **LETF é SPX ×2, QQQ é tech-heavy NASDAQ, ambos long-biased trend-
following em equity US**. ρ=0.555 é moderada, e como DR = (w₁σ₁+w₂σ₂)/σₚ,
com ρ~0.55 o ganho de diversificação é de ~12%, não chega a 20%.

### O que o mandate exige

`[advances_fin_ml, p.302-313, ch.16]` — "Markowitz's curse" e HRP — dá o
contexto de por que DR > 1.2 é um gate razoável: portfolios com diversifi-
cação marginal têm ganho OOS que pode ser artefato de noise no σ estimado.
O gate de 1.2 é conservador; abaixo disso, o custo operacional de rodar
2 strategies em paralelo (capital split, reconciliation, monitoring) costuma
superar o ganho.

### Onde procurar o par faltante

Pra atingir DR > 1.2, precisamos de uma Path B descorrelacionada do S&P.
Candidatos testáveis na próxima iteração:
- **TLT MA rotation** (bond momentum) — negativamente correlacionado com
  equity em regimes risk-off.
- **Gold trend-follow** (GLD Donchian 55/20) — tenho dados Tiingo daily.
- **HY spread momentum** — not implemented.
- **VIX-filtered equity** (short vol premium) — não temos dados.

Dos acima, TLT Donchian é fácil de implementar (mesmo módulo TSMOM). GLD
Donchian idem. Ambos prompts pra próxima iter A3d (nova, substitui a A3d
obsoleta).

## Decisão operacional

**Path B operacional = LETF rotation EMA100 band=0 lev=2x (Lead B1c winner
iter 32).** A QQQ Donchian (A3b winner iter 36) fica como cross-check
científico mas NÃO entra em produção como segunda perna — não oferece
diversificação material suficiente.

## Follow-ups

- Adicionar lead **A3d novo (não-obsoleto)** — "3rd-leg candidate" —
  testar TLT/GLD Donchian e medir ρ vs LETF. Meta: encontrar perna com
  |ρ| < 0.2 pra DR > 1.3.
- Se nenhuma 3ª perna aparecer, aceitar Path B = LETF-only e focar Phase 4
  (live) na LETF rotation.

## Artefatos

- Módulo: `src/ai_trade/backtest/grid/portfolio_combiner.py`
- Testes: `tests/test_portfolio_combiner.py` (18 testes; total 535 passed)
- Script: `scripts/run_a3c_portfolio.py`
- Relatório: `reports/a3c_portfolio_verdict.json`

## Citações

- HRP/IVP framework + Markowitz instability: `[advances_fin_ml, p.298-313,
  ch.16]`, RULE `[p.313]`.
- IVP 2-asset formula: `[advances_fin_ml, p.307-308]`.
- Gayed LRS (perna 1): `[leverage_for_the_long_run, p.13-17, Table 5-8]`.
- Donchian 20/10 (perna 2): `[trading_systems_methods, p.353]`.
- PBO/DSR/WF gate: `[advances_fin_ml, p.196-211, p.273-275]`.
- BR 15% tax: Investment Mandate §4.
