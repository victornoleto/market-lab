# spy_beater iter 020 — 4-way meta-ensemble derruba score, mas confirma teto em 71

Hoje rodei o iter 020 do `spy_beater_hunt`, que é o caçador de uma estratégia
única que bate o SPY ao mesmo tempo em CAGR (≥ 11.21%/ano) e em MDD (≤ 55.17%
de queda máxima) e ainda passa nos 7 gates estatísticos anti-overfit.

**Pergunta do iter**: estender o meta-ensemble (combinação ponderada de
estratégias-mãe) de 3-way para 4-way, adicionando o constituinte G1 IEF (que tem
o melhor Sharpe e o melhor MDD da história do hunt, mas SOZINHO falha o CAGR)
quebra o teto de 71 pontos do iter 019?

**Resposta empírica**: NÃO. O 4-way 25/25/25/25 (A2 + G1 IEF + G2 IEF + F1 stack)
caiu para 67/100 (PROMISING) — −4 pts vs iter 019. Mas com efeitos colaterais
interessantes: agora temos o **melhor mean Sharpe (1.058)** E o **melhor mean
MDD (26.17%)** entre todos os configs que também passam o bar de CAGR em 20 iters
e 68 trials. KILL #66 disparou (4-way ≤ 71 → teto consolida no iter 019). KILL
#70 disparou (Sharpe ≥ 1.05). 6/6 configs passaram todos os 3 bars — segundo
sweep 100% consecutivo.

**O que isto significa**: o rubric do hunt está **saturado** nas dimensões
Sharpe e MDD nos níveis do iter 019. Empiricamente o 4-way melhora ambos, mas
isso vira ZERO ponto extra na rubrica porque os anchor ranges já chegaram ao
máximo do bucket. O CAGR é o eixo que ainda mexe — e adicionar G1 IEF (CAGR solo
10.34%) puxou o aggregate para baixo. A trajetória meta-axis virou
**não-monotônica**: 70 → 71 → 67. O 3-way 33/33/34 do iter 019 é o ótimo local.

Outro achado: dropping F1 stack (all-gated 3-way) NÃO falha CAGR mas o score cai
~4 pts via Sharpe — confirma que F1 stack always-on contribui via diversificação
multi-asset permanente, não só via CAGR floor.

Status: meta-axis ceiling **consolidado empiricamente em 71**. Ainda 30 iters
sobrando até a meta de 50, mas qualquer ganho daqui pra frente provavelmente
será ≤ 1pt dentro da rubrica atual. F1+SPLIT continua como deploy-fallback
oficial (Plano C 100% mantido por mandate §1).

Citações: `[advances_fin_ml, ch.16, p.241-256]` (portfolio construction
multi-alpha), `[risk_parity, ch.5, p.10]` (Carlson stacking generalizado),
`[leverage_for_the_long_run, ch.3-4]` (Gayed gate em meta-ensemble).
