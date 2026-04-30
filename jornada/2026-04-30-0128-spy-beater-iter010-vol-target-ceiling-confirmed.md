# spy_beater iter 010 — vol-targeted SPY confirma o teto arquitetural em 67

A iter 010 era o último arquétipo Tier 1-2 que ainda não tinha sido
testado: **vol-targeted SPY**, no estilo Carver canonical
(`weight_t = target_vol / (factor × realised_vol_signal_t)`). A
hipótese de salvação era que **leverage dinâmica baseada em vol
realizada** poderia escapar do teto de score 67 que já tinha sido
batido por todas as outras famílias (LRS regime gate, HFEA estático,
KMLM crisis-alpha). A diferença geométrica: ao invés de gate
binário on/off ou pesos fixos, a alocação ao ativo alavancado
(SSO 2× ou UPRO 3×) **se contrai automaticamente** quando o vol
realizado de SPY sobe, e expande quando ele cai.

Construímos a infraestrutura nova (`vol_target_engine.py` com
`realized_vol`, `vol_target_weight`, `vol_target_strategy_returns`)
e 7 testes TDD novos (755 → 762 testes, todos green). Rodamos 3
configs: `c1_vt20_sso` (target 20% no SSO, defensiva), `c1_vt22_upro`
(target 22% no UPRO, intermediária), `c1_vt25_upro` (target 25% no
UPRO, agressiva).

**Resultado: PROMISING 60/100, com a peculiaridade de que TODAS as
3 configs passaram TODOS os 3 strict bars** (CAGR ≥ 11.21%, MDD ≤
55.17%, gates ≥ 5+5 cross-met) — `winner_conditions_met = TRUE`,
um resultado raro (só iter 003-005 e 006/007 tinham conseguido).
Mas o score caiu de 63 (iter 009) para 60 e o closest-to-winner
não mexeu — iter 006 mantém os 67 pontos.

A surpresa foi a **KILL #32** disparar do jeito mais limpo
possível: Sharpe monotônico **NEGATIVO** através do dose
target_vol 20→22→25% nos DOIS datasets (lh_56y: 0.714→0.688→
0.659; spy_real: 0.728→0.707→0.686). Isso é o oposto do que a
literatura Carver `[systematic_trading, ch.10]` prediz: em
commodity/FX (onde o método foi desenvolvido), aumentar
target_vol melhora Sharpe porque você está usando mais
informação do sinal. Em SPY-via-LETF, o **daily-reset decay**
do UPRO/SSO (1-3%/y) fica grande demais quando o peso médio
sobe (de ~0.625 no SSO para ~0.521 no UPRO 3×), e o efeito
descarrila o ganho de Sharpe.

A descoberta secundária: **vol-target underperforma SPY em
janelas de bull market low-vol**. O multi-horizon 5y rolling
pass-rate caiu pra 75% (iter 006/007 tinha 100%). Mecanismo:
quando vol realizado é baixo, o weight clipa em 1.0 (full
SSO/UPRO), e aí o decay do LETF drena CAGR vs SPY 1× durante
rallies compounding-positivos prolongados (tipo 2017-2019).

**O teto arquitetural em 67 está agora empiricamente
confirmado** em 4 famílias de controle distintas:

| família | melhor iter | score | Sharpe |
|:--------|:------------|------:|-------:|
| A1/A3 SPY-track LRS | iter 004 | 66 | 0.74 |
| A2 TQQQ-track LRS | iter 006/007 | **67** | 0.80 |
| B1/B2 HFEA barbell | iter 008/009 | 63 | 0.77 |
| C1 vol-target | iter 010 | 60 | 0.72 |

O caminho pro score 90+ está **arquitetonicamente fechado**
dentro da rubrica spy_beater no framework gross-of-tax 2-dataset.
53 iters cumulativos (long_term_portfolio 43 + spy_beater 10)
honestamente buscaram e nenhuma estratégia consegue bater SPY em
**ambos** CAGR e MDD com score ≥ 90 simultaneamente.

**Próxima iter (011)**: declarar IMPOSSIBILITY_RESULT e escrever
FINAL_REPORT_spy_beater_failed.md. F1+SPLIT do
long_term_portfolio (NTSX 25 + GDE 25 + KMLM 17.5 + DBMF 17.5 +
TLT 15) segue como deploy fallback honesto. Mandate §1 100%
Plano C inalterado. O resultado negativo tem valor de política:
confirma que dentro do honest research framework não dá pra
prometer "uma estratégia de longo prazo que bata o SPY em CAGR
sem aumentar MDD" — psychological hard sell, mas a matemática
30y favorece F1+SPLIT por Sharpe e drawdown.

Citações: `[systematic_trading, ch.10]` Carver vol-target
canonical (Sharpe-improving NÃO transfere pra LETF-on-SPY por
causa de decay), `[advances_fin_ml, p.31-34]` factor framework
(vol como state variable distinta de trend signal),
`[risk_parity, ch.5, p.10]` Carlson stacking (dynamic weight
não desbloqueia capacidade extra de CAGR vs static stacking),
`[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed LETF decay
empiricamente confirmado (60d realised-vol lag ~1 mês em
inflexões 2008/2020), `[advances_fin_ml, p.222-223]` DSR n=35
worst p 5.02e-03.
