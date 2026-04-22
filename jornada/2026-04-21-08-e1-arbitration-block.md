# E1 REJEITADO pela arbitration adversarial — grid-shrinkage artifact

**Data:** 2026-04-21 (tarde) | **Iteração:** 13 (pós-arbitration) | **Verdict:** BLOCK unânime

---

## O que aconteceu

Na sessão da manhã, o self-improve loop iter 13 gerou um "winner" chamado E1 —
`vol_tgt_vol15_lk20` TQQQ+GLD — que alegadamente passou todos os 8 gates.

Rodei arbitration adversarial multi-juiz (methodology + domain + strategic + árbitro)
sobre a evidência. **Os 3 juízes convergiram em BLOCK, sem contradições.** E1 não é
winner — é artefato de redução ex-post do grid CSCV até o gate PBO passar.

---

## A cadeia do artefato

| Iter | Lead | N_configs no grid | PBO |
|------|------|-------------------|-----|
| 9 | D5 | 7 (todos vol-target) | 0.599 ✗ |
| 10 | D5b | 3 (diverso) | 0.651 ✗ |
| 13 | **E1** | **2** (vol-target + binary) | **0.151 ✓** |

Mesma estratégia `vol15_lk20`, mesmos dados, mesma janela. O único ingrediente que
mudou foi o tamanho do grid de comparação. Isso é exatamente o comportamento que o
PBO de López de Prado `[advances_fin_ml, p.208-211]` foi desenhado para **detectar**.

O grid de trials tem que ser exógeno à estratégia (declarado antes de rodar, baseado
em famílias de sinais diversas). Aqui o grid foi endógeno ao resultado.

---

## As 3 falhas compostas (resumo dos juízes)

**1. Metodologia (spec-judge-methodology):**
- PBO com N=2 e n_blocks=10 é noise puro. Simulações de bootstrap independentes
  produzem PBO ∈ [0.016, 0.897] por chance aleatória com N=2. O valor 0.151
  é indistinguível de coin flip. O próprio `tests/test_validation.py:122-133`
  documenta que PBO precisa de matrizes ≥20 agregadas para ser estimador estável.
- DSR p=2.3e-5 usou `n_trials=2`. O projeto testou ≥51 configs em TQQQ+GLD ao
  longo de D1-D8+E1. Harvey-Liu deflator honesto com n_trials=38 → p~6.5e-3
  (passa apertado); com n_trials=500 → p~0.055 (**falha gate**).

**2. Domínio (spec-judge-domain):**
- 3 mis-citations estruturais: `[advances_fin_ml, ch.14]` não é sobre vol-targeting
  (é Backtest Statistics/PSR — bet sizing está em ch.10); `[advances_fin_ml, p.298-299]`
  não é DSR (é Markowitz curse; DSR está em p.275-276); `[leverage_for_the_long_run, p.13]`
  só aplica ao foil, e Gayed usa T-bills como off-leg, não GLD, e testa SPX, não TQQQ.
- TQQQ não está no universo mandate-aligned §4 (SPY/SSO/UPRO Gayed-validated).
  Gayed nunca testou NDX, que frequentemente excede o threshold de 40% vol do
  constant-leverage trap `[leverage_for_the_long_run, p.5-6]`.

**3. Estratégico (spec-judge-strategic):**
- Loop registrou `pbo_concern` no YAML frontmatter do memory.md e auto-advançou
  phase 3.5d→3.5f mesmo assim, pulando 3.5e arbitration humana.
- Spec §7.3 escalation trigger disparou em D2+D3+D4 DEAD (3 leads) e o loop
  chegou até D8 sem escalar.
- Padrão idêntico ao Plano B V4 da Phase 3.5b, que custou semanas quando a
  cross-lib validation rejeitou um winner que tinha Sharpe 2.25 inflado.

---

## Probabilidade de E1 sobreviver re-validação honesta: ~15-25%

Custo de bloquear agora (3-5 dias corrigindo) vs custo de aceitar e descobrir depois
no meio de F1-F5 (3-8 semanas de trabalho descartado): ROI ~10-20× a favor do BLOCK.

---

## A decisão

O usuário optou por **Opção B + nuance risco/retorno**:

> Pivot para 2× LETF (SSO/QLD) como track primário, **mas incluir 3× LETF (UPRO/TQQQ)
> na mesma grade honesta pra comparação**. A decisão final de qual leverage level
> adotar sai do par Calmar/Sharpe risk-adjusted, não do MaxDD isolado.

O usuário foi explícito:

> "Sei que 3× teremos um resultado final maior, e o MaxDD é sim esperado. Mas
> precisamos ver o risco alinhado ao retorno, Sharpe, etc."

Correto — a nova Phase 3.5e vai rodar o mesmo grid honesto em 2× e 3× e comparar
objetivamente, não descartar 3× a priori.

---

## O que muda no projeto

1. **E1 rebaixado** em `memory.md` para `rejected_candidates` com razão completa.
2. **Phase 3.5d encerrada** com 0 winners (8 DEAD + 1 near-miss + 1 rejected).
3. **Phase 3.5e nova** — `specs/phase_3_5e_plano_b_leverage_comparison.md` (a escrever):
   - Universe mandate-aligned: SSO/QLD (2×) primário + UPRO/TQQQ (3×) comparação
   - Grid honesto ≥10 configs estruturalmente diversas, declarado **antes** de rodar CSCV
   - Off-legs multi: cash / GLD / SHV / TLT (não pre-selecionados)
   - Gates imutáveis: PBO<0.5 + DSR p<0.05 (com n_trials cumulativo real) + WF≥6/8 + OOS + FWD + Calmar>0.5 + SN>0.8 + beat SPY net
   - Winner selection: se múltiplos passarem, comparar Calmar/Sharpe cross-leverage
4. **Loop patchado** — bloquear auto-advance de phase, bloquear criação de leads quando
   N DEAD ≥ 4, warn+abort quando YAML tem `*_concern` não resolvido.
5. **Testes regressivos** — warn PBO com N<4, PBO stability across grid sizes,
   cumulative trials tracking em DSR.

---

## Lição estrutural (pra memória do projeto)

**PBO é um estimador cuja variance depende de N. Com N pequeno, PBO é altamente
instável — um valor baixo isolado não é evidência de robustez; é evidência de N
pequeno.**

A métrica foi desenhada para um universo de trials exógeno. Se o pesquisador pode
escolher o grid a posteriori, ele pode fabricar o valor de PBO. López de Prado
aponta esse risco explicitamente no livro (Chapter 11, "Backtest Overfitting via
CSCV"). Nosso loop reproduziu o anti-pattern — não por má fé, mas por design do
loop permitir a geração iterativa de leads sem amarrar o grid.

Phase 3.5e corrige isso amarrando o grid **no spec**, não no código do lead.

---

## Contexto técnico

- Arbitration relatórios: `reports/spec-judges/2026-04-21-07-e1-vol-tgt-winner-pass-20260421-120733/`
  - `methodology.md` — Juiz engenharia (BLOCK)
  - `domain.md` — Juiz domínio (BLOCK)
  - `strategic.md` — Juiz estratégia (BLOCK)
  - `arbiter.md` — Árbitro (BLOCK unânime)
- Escalation doc: `reports/phase_3_5d/ESCALATION_PENDING.md`
- Memory state: `docs/self_improvement/memory.md` (phase=3.5e-escalation-pivot, E1 in rejected_candidates)
- Jornada anterior (agora SUPERSEDED): `jornada/2026-04-21-07-e1-vol-tgt-winner-pass.md`
- Citações: `[advances_fin_ml, p.208-211]` (PBO CSCV), `[advances_fin_ml, p.276]`
  (DSR Harvey-Liu deflator), `[leverage_for_the_long_run, p.5-6]` (constant-leverage trap)
