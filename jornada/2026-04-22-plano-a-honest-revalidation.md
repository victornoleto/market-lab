# Plano A re-validado sob engine honest — 6 leads, 0 winners

**Data:** 2026-04-22
**Fase:** 3.5f F3 (fechada)
**Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`
**Status:** re-validação concluída; Plano A sem winner honest; escalação ao usuário.

---

## O que aconteceu

Depois do fix da engine (commit `7b90a8f`, contexto em
`jornada/2026-04-22-engine-lookahead-bug.md`), a Phase 3.5f F3
re-avaliou as 6 leads do Plano A V2 contra as 13 gates do mandate
sob a engine honest. **Nenhuma passou.**

A tabela-resumo:

| Lead | Módulo | Engine pré-fix | Honest OOS Sharpe | Honest OOS CAGR | Honest OOS MDD | Veredito |
|---|---|---|---:|---:|---:|---|
| V2-L1 TSMOM | `tsmom_multi_asset.py` | já limpa | −0.21 | −0.49% | −10.24% | FAIL |
| V2-L2 Gayed | `plano_a_leveraged_rotation.py` | buggy → F2 fixou | 0.56 | 12.58-14.29% | −37% | FAIL |
| V2-L3 AFML | `afml_tb_meta.py` | já limpa | 1.21 | 2.50% | −0.76% | FAIL |
| V2-L4 Carver RP | blend (L1+L2+L3) | L2 sleeve buggy → fixou | 0.62 | 4.99% | −12.77% | FAIL |
| V2-L5 Kalman | `kalman_pair_cointegration.py` | já limpa | — | — | — | FAIL (estrutural) |
| V2-L6 vol-breakout | `donchian_breakout.py` | já limpa | −0.22 a −0.73 (12/12 neg) | — | — | FAIL |

---

## Lead a lead — uma frase cada

- **V2-L1 TSMOM.** Já estava morto antes (swap drag consumia alpha em
  holds 40-160d). Engine limpa desde sempre. Veredito confirmado:
  Sharpe OOS negativo em todos os configs `[systematic_trading, p.185-188]`.

- **V2-L2 Gayed.** O "winner" de 79% CAGR vira ~14% CAGR quando você
  tira a clarividência. 14% ao ano é comparável ao CDI BR — para uma
  estratégia leveraged 2× com MDD −37%, não vale o risco. O edge
  regime-rotation é real, só que muito menor do que o papel dizia.

- **V2-L3 AFML meta-label.** Sharpe 1.21 no melhor ticker (XLF), mas
  CAGR de 2.5%/ano. Meta-labeling é filtro de precisão, não gerador
  de edge `[advances_fin_ml, p.50]` — e o primário EMA-50 que ele
  filtra é fino demais.

- **V2-L4 Carver RP.** O plano apostava que talvez o L2 "diluído" no
  blend pudesse passar porque mesmo honest ainda carregaria algum
  alpha. **Não foi isso que aconteceu.** O blend é ponderado por
  risk-parity (inverso da volatilidade IS). L2 tem volatilidade alta
  (35%/ano), então pesa **4.8%** no blend, não 66-75% como o plano
  chutou. O peso real ficou em L3 (66%, baixa vol) e L1 (29%). O
  blend herda o CAGR anêmico do L3, não o "alpha reduzido" do L2.
  Conclusão: a hipótese de rescue via blend nunca foi numericamente
  compatível com Carver's own math `[systematic_trading, ch.11]`.

- **V2-L5 Kalman pairs.** Zero pairs ADF-cointegrados na amostra
  testada. Não é falha de engine — é estrutural. ETFs líquidos
  perderam relações de pair-arb tradicionais nos anos 2010+.

- **V2-L6 Donchian vol-breakout.** 12/12 OOS Sharpe negativos em clean
  engine. Universo pequeno (10 ETFs) — Covel exige 30+ instrumentos
  (de preferência futures) para trend-follow puro
  `[trend_following_covel, ch.4]`.

---

## Por que a hipótese "L2 dilui em L4" estava errada

O plano §F3 item 2 supunha: "se L2's honest alpha cai de 79% pra 15%,
o blend L4 pode ficar comparável ou até melhor que L2 sozinho, porque
ele pondera com L3 e L1 que talvez tenham edge próprio."

Duas coisas estavam erradas nessa suposição:

1. **L2 não pesa 66-75% do blend.** O Carver RP pondera *inversamente
   à volatilidade IS* de cada lead. L2 (2× leveraged Gayed) tem vol
   anualizada de ~35%; L3 (AFML XLF) tem vol de ~4%; L1 (TSMOM) tem
   vol de ~8%. O inverso normalizado dá weights **L3 = 66%, L1 = 29%,
   L2 = 4.8%**. L2 contribui pouquíssimo pro perfil do blend,
   independente de estar buggy ou fixed.

2. **L3 não tem edge suficiente pra carregar o blend.** Com 66% do
   risco alocado a uma estratégia de 2.5% CAGR, o blend herda esse
   piso. Adicionar L1 (que tem Sharpe −0.21) só piora. O blend nunca
   foi matemática de "se algum componente for bom, o blend melhora";
   é ponderação por risco, e a gente acabou ponderando pesado em
   CAGR-pobre.

Então L4 não é um winner "diluído" — é uma mediocridade bem
calibrada `[advances_fin_ml, ch.16]`.

---

## F3 gate (c) — escalação ao usuário

Per plano §F3 gate (c): "se todas 6 leads falham, STOP e escalate com
4 opções explícitas." Resumidas aqui; pros/cons completos estão no
`reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md §6`.

### Opção A — Desenhar V3 (7ª família)

Nova lead science-based que não repita as 6 testadas. Candidatos:
vol-surface skew signals, event-study pre-earnings, cross-asset
lead-lag. **Custo:** 4-8 semanas spec + build + validate.

### Opção B — Phase-6 fallback (Gayed 1× unleveraged)

Gayed honest sem alavancagem: ~11%/ano CAGR, MDD ~16%, passa gate de
MDD, abaixo do CDI. Aceitar como "passive-like active" sem claim de
alpha. **Custo:** dias.

### Opção C — Abandonar Plano A permanente

Invoca regra `project_plano_a_v2_last_attempt` (user-memory).
Realocação per mandate §4.7: bucket A vai tudo pra Plano C buy-hold.
Honest, encerra o experimento. **Custo:** horas (só docs).

### Opção D — Freezar Plano A, finalizar Plano B c06-c12

Plano B engine limpa (F1 confirmou). 7 families untested no grid
Phase 3.5e. Fora do escopo atual — exige usuário tirar Plano B do
stand-by. **Custo:** 1-2 semanas de iter budget.

---

## O que está pronto e o que está em `.pending`

Feito e commitado:
- 4 testes cirúrgicos (`tests/test_plano_a_lookahead_bias.py`).
- Engine fix (`src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py`).
- Scope audit (`docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md`).
- 6 AGGREGATE.md per lead em `reports/phase_3_5f/honest_revalidation/<lead>/`.
- BREADTH_SUMMARY.md cross-lead.
- Banners forensic em phase3_5a_v2/v2_l2, v2_l4, phase4_0.

Aguardando decisão do usuário (staged em `docs/.pending/`):
- Entry em `docs/investment-mandate.md §7`.
- Banner no `docs/strategies/plano_a_v2_l2_gayed_cfd.md`.
- Rewrite do "Onde estamos hoje" + "O que vem a seguir" em
  `jornada/README.md`.

Nenhum doc canonical foi tocado. O usuário escolhe uma das 4 opções
no §6 do BREADTH_SUMMARY, e então os files de `.pending/` viram
canonical (ou são descartados, se a escolha mudar a narrativa).

---

## Referências

- `[advances_fin_ml, p.31-34]` — bias definition.
- `[advances_fin_ml, p.50]` — meta-labeling role.
- `[advances_fin_ml, p.196-202]` — DSR / bootstrap.
- `[advances_fin_ml, p.208-211]` — PBO CSCV.
- `[advances_fin_ml, ch.11]` — walk-forward.
- `[advances_fin_ml, ch.16]` — blend construction.
- `[systematic_trading, ch.11]` — risk-parity weighting.
- `[systematic_trading, p.185-188]` — retail CFD cost model.
- `[leverage_for_the_long_run, Gayed, p.11-14, p.16-17, p.21]` —
  V2-L2 regime rotation thesis.
- `[trend_following_covel, ch.4]` — trend-follow universe size.
- Mandate §2 (CDI floor), §2.5 (zero bypass), §4.7 (abandonment
  allocation rule), §7 (decision history).

---

**Leitura recomendada em seguida:**

1. `reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md` —
   detalhes das 4 opções.
2. `jornada/2026-04-23-0700-overnight-summary.md` — o formato para
   usuário escolher.
