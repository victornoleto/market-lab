# 2026-04-24 17h29 — Hunt loop iter 016: static 60:40 × vol-target híbrido vira 79/100 STRONG, NOVO TOPO do loop, 4/5 winner conditions, DSR p cai pra 0.13 no melhor dataset [HUNT LOOP]

**Contexto:** Pesquisa em background (mandate §1 segue **MAINTENANCE 100% Plano C**). Loop rodando pra documentar teto de hunt ativo; nenhuma alocação real dessas estratégias.

## O que aconteceu

Iter 016 juntou os dois primitivos mais fortes do loop até agora:

- **Iter 015** (static NTSX synth 90:60, 77/100) — razão fixa entre SPY e IEF, alavancagem constante 1.5×. Primeiro mecanismo a escapar da armadilha de cointegração σ²_port que matou as 4 overlays seguintes (009/012/013/014).
- **Iter 008** (vol-managed SPY+TLT, 74/100) — pesos inversos-variância dinâmicos + escala Moreira-Muir (alvo de vol 0.15, lookback 21d, cap 2.0). Ajusta exposição total ao regime de vol.

Hipótese do 016: os dois capturam dimensões ORTOGONAIS, não redundantes. O 015 só capta diversificação cross-asset constante; o 008 capta adaptação a regime mas é vulnerável a choque assimétrico em uma perna (como 2022 quando bonds também caíram). Trancar a razão 60:40 do 015 **e** multiplicar pela escala vol-target do 008 deveria somar, não cancelar.

**Resultado:** fez mais do que somar.

| dataset | Sharpe (Δ vs frozen bench) | vs iter 015 | vs iter 008 | MDD |
|---|---|---|---|---|
| educational | **0.98** (+0.30) | +0.20 | +0.12 | **31.3%** (era 44.5 iter 015) |
| spy_real | **1.14** (+0.24) | +0.09 | +0.14 | **26.7%** (era 30.3) |
| ndx_real | **1.19** (+0.24) | +0.13 | +0.17 | **23.2%** (era 39.5) |

Edge em **3/3 datasets** bem acima do +0.10 estrito. MDD despencou no educational (−13pp) e ndx (−16pp). G3 Walk-Forward virou **8/8 em spy + ndx** (primeira vez no loop). 9/9 sub-janelas positivas. Kill criteria #1/#3/#4: **nenhum** triggered (Sharpe subiu, MDD melhorou, score subiu de 77 pra 79).

**Score:** 79/100 (= 25+19+0+15+15+5). **Novo topo do hunt loop** (era 77 do iter 015).

**Por que ainda não é WINNER?** DSR continua sendo o único gate que não passa. Mas os p-values despencaram:

| iter | DSR p (edu / spy / ndx) |
|---|---|
| 015 | 0.548 / 0.268 / 0.268 |
| **016** | **0.226 / 0.163 / 0.132** |

Aproximadamente metade dos p-values, **três datasets dentro de 1σ do corte**. Com n_trials cumulativo = 4261, DSR p<0.05 exige Sharpe observado ~1.5-1.6 no pior dataset; iter 016 está em 0.98 no pior, então ainda falta uns +0.30-0.50 de Sharpe. Não é pouco, mas é a 1ª vez no loop que DSR parece alcançável por um único acréscimo ortogonal.

## Análise de funding cost (robustez real-product)

Iter 015 tinha ressalva: o NTSX sintético não modela custo de funding nos 50% de notional extra via futuros (drag real ~75-100bps/ano). Pós-drag, edge do iter 015 caía pra +0.04-0.10 (BORDERLINE no gate estrito).

Iter 016 sofre a mesma hircuagem de ~75-100bps:

| dataset | synth Sharpe | pós-drag Sharpe | pós-drag edge |
|---|---|---|---|
| educational | 0.98 | ~0.91-0.94 | **+0.23 a +0.26** |
| spy_real | 1.14 | ~1.06-1.09 | **+0.16 a +0.19** |
| ndx_real | 1.19 | ~1.12-1.15 | **+0.17 a +0.20** |

**Os 3 datasets ainda passam folgado o +0.10 estrito pós-drag.** O layer de vol-management absorve a margem de otimismo que o static stack sozinho não aguentava. Robusto à premissa de cost-model.

## O que isso significa em linguagem humana

O hunt loop confirmou que **combinar razão fixa + escala dinâmica produz ganho aditivo genuíno**. Não é só "um pouco melhor do que a média dos dois" — é mais do que cada um sozinho, em todas as dimensões: Sharpe, CAGR, MDD, DSR, walk-forward.

É a primeira estratégia do loop que:
- Ganha do SPY 1x em Sharpe risk-adjusted com margem grande
- Perde MDD vs SPY 1x
- Sobrevive ao regime 2022 (stock-bond ρ virou positivo; vol-target automaticamente cortou exposição)
- Sobrevive ao funding cost real do produto listado (NTSX)
- Passa 6/7 dos gates anti-overfit cross-dataset

Falta só DSR pra virar WINNER. Iter 017 candidates (ranked):

1. **[OPTION R]** (primary): aplicar o iter 016 a 3 produtos stacked regionais (NTSX_synth US / NTSI_synth INTL / NTSE_synth EM), com 12-1 momentum absoluto selecionando qual região ou regiões ficar. Adiciona dimensão cross-sectional regional que é ortogonal a vol-target. Expected +0.10-0.25 Sharpe se dispersão regional > ruído. **NÃO é re-teste do iter 003** — lá foram 11 sector ETFs homogêneos; aqui são 3 regiões sobre primitivo stacked, estruturalmente diferente.
2. **[OPTION S]**: collar de put-spread + covered call na perna de equity do iter 016. Captura skewness tail-hedge. Expected +0.05-0.15. Mais cara de implementar (precisa dado de options).
3. **[OPTION T]**: HMM 2-state em ρ(SPY, IEF) 60d rolling → regime A usa 60:40, regime B vira defensive 30:70. Protege contra 2022-style flip de correlação.

Iter 017 pick provável: **Option R**. Cross-sectional regional rotation é o único mecanismo ortogonal barato disponível, e iter 016 validou que a base stacked+vol-managed é robusta o suficiente pra servir de primitivo.

## Estado do loop

- 16 iterations rodadas em ~2 semanas
- 0 winners ainda
- Top-K ranking atualizado: #1 iter 016 (79), #2 iter 015 (77), #3 iter 008 (74), #3 iter 010 (74), #5 iter 006 (67)
- `cumulative_n_trials` → 4261
- 775 pytest verdes + 5 skip (+ 14 novos specs do iter 016; zero regressão)
- **MAINTENANCE MODE continua** — nada disso muda mandate §1. Se eventualmente sair um WINNER do loop, ainda precisa de override §7 assinado pra sair da 100% Plano C. Loop produz CANDIDATOS, não posições ao vivo.

Ver `studies/strategy_hunt_loop/iterations/016-2026-04-24-1729-static-stack-vm-hybrid/final_report.md` pra o report completo.
