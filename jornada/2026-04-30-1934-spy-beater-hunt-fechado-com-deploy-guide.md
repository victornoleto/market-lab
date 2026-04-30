# spy_beater_hunt fechado em 30 iters com guia de deploy escrito

Tarde de 2026-04-30: o usuário voltou do almoço pedindo pra fechar a hunt
formalmente. Após eu apontar que muitas estratégias passam todos os bars
(CAGR > SPY + MDD < SPY) mas não atingem tier WINNER (≥90/100) por causa
do peso CAGR-anchored do rubric, ele simplificou: **"se passaram nos
gates, por mim tudo certo"**. Isso reframou completamente o veredito —
de "nenhuma estratégia foi vencedora" para "várias estratégias estão
deploy-ready desde que o usuário aceite o compromisso CAGR×MDD que elas
apresentam".

Construí o `TOP_STRATEGIES.md` como doc canônico pós-fechamento. Ele
ranqueia 30 iters pela combinação de gate-pass strict (1 ponto por gate
individual) + score net + perfil de risco. Categoriza em **Tier A** (6/7
strict gates passam, PBO ≤ 0.20), **Tier B** (6/7 com PBO 0.20-0.50),
**Tier C** (warning: PBO > 0.50, cumulative trials inflation), e **Tier
D** (não recomendados). Nenhuma estratégia atinge Tier S (7/7) — o gate
G3 (Walk-Forward MDD < 25% per-window) falha estruturalmente para
qualquer leverage moderado-alto durante 2008/2022 stress, o que é uma
limitação física do trade-off CAGR-vs-MDD não uma falha do hunt.

Top 3 picks pra deploy se mandate §7 reativar Plano B:

1. **Iter 026 H6** (4-way meta-ensemble): PBO 0.00 em ambos datasets,
   net CAGR 13.83% / MDD 33.6% / Sharpe 0.84. Gross score 71, net 66.
   Combina os 4 melhores constituintes single-axis (TQQQ-LRS + F1-LETF
   gated + F1 stack always-on + TSMOM-126d) com gate-source diversity
   máxima. **Anchor honesto** — não tem inflation de cumulative trials
   manchando.

2. **Iter 019 H2** (3-way meta): mesmo perfil mas só 3 sleeves. PBO
   0.00, net CAGR 13.11% / MDD 30.33% / Sharpe **0.90 (melhor Sharpe
   net entre top 6)**. Implementação mais simples. Trade-off: 0.72pp
   menos CAGR que iter 026.

3. **Iter 015 F1 stack** (static buy-hold): NTSX 35 + GDE 30 + TLT 20
   + KMLM 15. Sharpe 0.95 net (melhor entre passers), MDD 26.82%
   (melhor net entre passers). **Caveat real**: CAGR margem só 0.14pp
   acima do SPY no rubric net — qualquer FX move adverso elimina a
   margem. Para perfil **simples + tax-efficient**.

A questão do overfit foi auditada em todos os top 14: **G2 DSR**, **G4
OOS**, **G5 FWD**, **G6 Bootstrap CI**, **G7 cross-lib** TODOS passam
em todas as 14. O **G3 WF** falha em todas (per-window MDD 27-50%) —
inerente ao leverage durante stress periods, não overfit. O **G1 PBO**
passa em iters 026/019/028/027/034 (Tier A) mas falha em iters
030-036/018/021/025/029 (Tier C — cumulative trials inflation).

A iter 035 H15.2 tem o gross score mais alto da hunt (74) com CAGR
17.09% e MDD 30.22% — números **excelentes**. Mas PBO 0.56 em
spy_real é overfit warning grid-level porque o iter 035 foi a 19ª
variante meta-ensemble testada e o ranking grid começa a refletir
variação aleatória. O **principle M** (iter 034) demonstrou que o mesmo
spec exato pode receber score 73 ou 72 dependendo do grid em que é
avaliado — o ruído do rubric é ±1pt no nível de grid-composition.
Anchor a iter 026 H6 (PBO 0.00) é o caminho honesto.

A decisão estratégica fica clara: **F1+SPLIT (Plano C atual) continua
incumbente**. Para reativar Plano B com qualquer dessas top 3, exige
mandate §7 override formal escrito + validação de catálogo Inter
(NTSX/GDE/KMLM/UPRO/TMF/TQQQ — várias precisam ser confirmadas via
suporte) + 3 meses paper trading simulado em planilha (Inter não tem
paper) + staging USD 1k → 10k em degraus mensais condicionais.

Atualizei `WINNER_AND_RANKING.md` (deprecando como canônico, apontando
pra `TOP_STRATEGIES.md`), `BASE_MEMORY.md` (seção CLOSURE no top do
body), `README.md` (status closed + file index update). Nenhum código
mudou — `tax_layer.py` integration de manhã + 30 iters re-rodadas
mantêm 768 testes baseline + tudo commitado.

**Citações:**
- `[advances_fin_ml, p.31-34]` — gate framework (PBO/DSR/WF/Bootstrap/CrossLib)
- `[advances_fin_ml, p.208-211]` — PBO via CSCV; iter 026 PBO 0.00 = best honest anchor
- `[advances_fin_ml, p.222-223]` — DSR cumulative_n_trials = 140 inflation
- `[leverage_for_the_long_run, ch.3-4]` — Gayed LRS underlying iter 026 A2 constituent
- `[risk_parity, ch.5, p.10]` — Carlson stacking underlying F1 stack
- Lei 14.754/2023 — DARF 6015 modelado em todas as 30 iters
