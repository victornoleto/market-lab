# Global Tilt Loop iter 006 — VAA SmartStack: STRONG 85/100

Testamos o VAA-G4 SmartStack (Vigilant Asset Allocation, Keller & Keuning 2017)
como alternativa ao HAA SmartStack que foi o vencedor do iter 005.

## O que foi testado

A ideia: em vez de um único "canário" global (VWOSIM) que aciona um switch binário
entre ofensivo/defensivo, o VAA usa um sistema de votos por amplitude de mercado —
cada um dos 4 ativos ofensivos vota se está em tendência positiva. Se 2 dos 4 têm
momentum positivo, apenas 50% do portfólio vai para ofensivo; o resto vai para defensivo.

Universo ofensivo: NTSXSIM (EUA 90/60 stackado), NTSI (internacional 90/60), NTSE
(mercados emergentes 90/60), BNDSIM (bonds 1×). Sinal: 13612W ponderado recente.
Sleeve fixo: 10% KMLMSIM (futuros gerenciados) + 5% GLDSIM (ouro) = 15%.

## Resultado: STRONG, não WINNER

| período | Sharpe | CAGR | Drawdown máximo | Gates |
|---|---|---|---|---|
| 31 anos (educacional) | 1.052 | 8.26% | 14.24% | 7/7 |
| 17 anos (vt_real) | 0.850 | 6.53% | 14.24% | 7/7 |
| 16 anos (ndx_real) | 0.733 | 5.23% | 14.24% | 7/7 |

**Comparação com o HAA (iter 005)**:
- Sharpe: 1.052 vs 1.112 → VAA inferior
- CAGR: 8.26% vs 14.14% → diferença de quase 6 pontos percentuais ao ano
- MDD: 14.24% vs 20.91% → VAA é ligeiramente melhor em drawdown

## Por que ficou abaixo

O problema central: colocar BNDSIM (bonds) como 4º ativo ofensivo cria
"sinal contaminado". Em períodos de bull market de ações onde bonds têm
retorno negativo (taxa subindo = preço do bond cai), o sistema interpreta
que apenas 3 de 4 ativos estão positivos e manda 25% para defensivo —
mesmo quando as 3 ações stacked estão voando. Isso sistematicamente
sacrifica CAGR sem reduzir muito o risco.

Resultado: CAGR de 6.53% no vt_real ficou abaixo do piso mínimo (7.04%)
pelo scoring — perdendo a condição 4 de vencedor.

## Decisão arquitetural confirmada

HAA com canário único é mais simples e mais eficaz para este universo.
A amplitude de breadth do VAA não agrega valor quando o universo tem bonds
como participante ativo na votação ofensiva.

O VAA tem UMA vantagem: MDD ainda mais baixo (14% vs 21% do HAA). Mas a
diferença não compensa a queda de 6pp de CAGR. HAA continua sendo o Pareto
frontier do loop.

## Próximos passos

Queue restante (iters 007 e 008):
- **Iter 007**: portfólio estático do usuário (9 sleeves RSSB/RSST/etc.) com gate G3' adaptado — verifica se iter 003 era escondido por calibração de gate errada
- **Iter 008**: WLDU (2× global equity ETF) + filtro SMA 200d estilo Gayed

Score: 85/100 → STRONG. Ocupa agora o rank 4 no Top-K do loop (acima do capital-efficient-static, abaixo dos 3 WINNERs).
