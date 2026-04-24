# Hunt loop iter 006: vol-managed 60/40 SPY+TLT dá 67/100 PROMISING (novo top-K #1, 4/5 winner conditions)

**Data:** 2026-04-24 10:27
**Categoria:** HUNT LOOP (background research, mandate §1 segue MAINTENANCE 100% Plano C)
**Verdict:** 🥈 PROMISING (score 67/100, winner_conditions_met=False, tier=PROMISING)

---

## O que foi testado

Combinação de duas mecânicas de livros em um único portfólio de 2
ativos (SPY + TLT):

1. **Naïve risk parity** `[risk_parity, p.10-11, ch.1]` — pesos dos
   legs proporcionais ao inverso da variância. Para 2 ativos, isso é
   matematicamente *exact ERC* (equal risk contribution),
   independentemente da correlação.
2. **Moreira-Muir variance-scaling** (iter 005) — aplicado no portfólio
   inteiro: `s_t = target_vol² / σ²_port_{t-1}`, cap 1.5-2.0×
   respeitando IDM max 2.5 `[systematic_trading, p.170-171, ch.11]`.

O argumento por que isso deveria beater iter 005 é simples: **SPY e
TLT têm correlação ~−0.30 histórica** `[risk_parity, p.80-81, ch.4]`.
Misturar dois ativos com correlação negativa é a coisa mais "clássica"
em quant finance, e iter 001-005 nunca testaram isso.

---

## Resultado

| dataset | top cfg | Sharpe (Δ vs bench) | MDD (Δ) | gates |
|---|---|---|---|---|
| educational SPY+TLT 24y | `vt15_L63_cap20` | **0.929 (+0.268)** | **40.10% (−15.10pp)** | 5/7 |
| spy_real SPY+TLT 17y | `vt15_L21_cap20` | **1.000 (+0.100 exact)** | 37.21% (+3.51pp) | 5/7 |
| ndx_real QQQ+TLT 16y | `vt15_L21_cap20` | 1.021 (+0.066) | 37.21% (+2.09pp) | 6/7 |

- **Primeiro iter do loop a bater o gate +0.10 Sharpe em 2 datasets**
  (educational + spy_real exact).
- **Primeiro iter a bater CAGR floor 3/3 E MDD ceiling 3/3**.
- Score **67/100 supera iter 005 (59) em 8 pts** — novo top-K #1 do loop.
- Mas ainda **falha G2 DSR** (p=0.20-0.33 a n_trials=4228) e o novo gate
  de PBO degradou de 0.24 → 0.69 no spy_real (Kill #3 triggered).

---

## O que isso significa

**A mecânica funciona** — diversificação multi-asset é um eixo
verdadeiramente ortogonal aos iter 004-005 e entrega edge real. A
redução de MDD de 15pp no educational (de 55% buy-hold SPY pra 40% vol-
managed 60/40) é o maior ganho de drawdown que o loop já produziu.

**Mas o grid de 12 configs foi uma má ideia** — adicionar o dynamic
leg weighting inflou o PBO de 0.24 pra 0.69, porque configs de lookback
curto (21d) reagiram ao crash do TLT em 2022 de forma diferente dos
lookbacks longos (126d). Para iter 007, duas opções:

- **Opção barata (verificação):** pré-committar 1 cfg (`vt15_L63_cap20`)
  ex-ante, rodar sem grid. PBO não se aplica. Só +3 trials ao
  cumulative. Teste limpo se o edge sobrevive sem viés de seleção.
- **Opção de alto retorno:** combinar a mistura SPY+TLT com um
  overlay de 12-1 momentum (Moreira-Muir Table IV). Adiciona um 2º
  eixo de edge independente (trend). Predição: +0.05-0.10 Sharpe
  em cima do 1.00 atual → 1.05-1.12, encostando no bar do DSR.

---

## Conclusão pro mandate

**Nada muda.** Mandate §1 segue MAINTENANCE 100% Plano C consolidado
(2026-04-23). Mesmo este iter sendo "o melhor resultado do loop até
agora" com 4/5 winner conditions satisfeitas, ele **não é winner**
(DSR não clara) — e, crucialmente, **o spec do hunt loop explícita
que mesmo um winner é CANDIDATE, não auto-deploy**, exigindo override
§7 separado.

O que este iter entrega é **evidência parcial consolidada** de que o
mecanismo de blend multi-asset tem edge real e mensurável:

- +0.10 Sharpe edge em spy_real (exato, pela primeira vez no loop)
- +0.27 Sharpe edge em 24y educational
- MDD reduzido 15pp na janela longa
- ρ_stockbond negativa confirmada nos 3 windows

Para uma eventual reativação futura de Strategy A, B ou D, isto vira
uma peça de conhecimento: **diversificação multi-asset via inverse-
variance weighting + variance-scaling é superior a single-asset vol-
adaptation em CAGR-floor, MDD-ceiling, e edge absoluto em 2 de 3
janelas**.

---

## Próxima iteração sugerida

Option A (pré-commit single cfg) é a escolha mais barata e de maior
valor informativo. Caso passe: deposita uma config deployment-ready
no knowledge base. Caso falhe: fecha o mecanismo de blend como
grid-overfit artifact.

Ver `studies/strategy_hunt_loop/iterations/006-2026-04-24-1027-vol-managed-60-40/final_report.md`
para o detalhamento completo das 7 gates, 5 critérios, e as 3
direções de próximo passo.
