# Bestfolio iter 008: dual-canary HAA nao venceu

O bestfolio_hunt_loop testou uma mudanca bem estreita: manter todos os ativos
do HAA+Gold iguais e mexer apenas no canario que decide risco ligado/desligado.
A ideia era combinar `VWOSIM` com `VTISIM` para evitar falsos periodos
defensivos.

Resultado: **PROMISING 73/100, nao winner**. A propria regra original
`vwo_only` venceu as variantes com `VTISIM`, com Sharpe liquido
**0.983 / 0.954 / 0.860** em educational / vt_real / ndx_real. Isso fica
abaixo do benchmark iter 009 HAA+Gold **1.120 / 1.061 / 0.954**, e zero
datasets bateram por +0.10 Sharpe. O kill criterion disparou.

Licao em linguagem simples: o problema nao era falta de um segundo canario de
acoes amplas. O `VWOSIM` continua sendo o melhor gatilho simples neste
universo; a proxima tentativa precisa usar um sinal de regime diferente, como
uma tendencia tipo Gayed/SPY/VT, nao outro indice de acoes com momentum
absoluto. `[stocks_on_the_move, ch.6]`; `[stocks_on_the_move, p.63-65]`.
