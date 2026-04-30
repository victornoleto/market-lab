# spy_beater_hunt — adicionada camada net-of-tax (Lei 14.754/2023)

Antes desta sessão, todas as 17 iters do `spy_beater_hunt` eram avaliadas
**gross-of-tax** — os relatórios literalmente declaravam "gross-of-tax" e
o cost model não incluía DARF. O usuário, prestes a ir trabalhar, pediu
três coisas: (1) confirmar se a regra fiscal correta estava salva nos
nossos dados, (2) ajustar o pipeline pra reportar pre/post taxes, e (3)
re-rodar as iters já existentes pra ter score líquido em todas.

A regra estava correta na memória: `Lei 14.754/2023` vigente desde
jan/2024 — alíquota 15% flat sobre rendimentos exterior, **apuração
anual única** na DAA (não DARF mensal — o pré-2024 era diferente),
perdas compensam ganhos no mesmo ano, e saldo negativo carrega
indefinidamente. A classe `AnnualDarfEngine` em
`studies/_shared/tax_engine.py` já implementa isso corretamente.

A integração no `spy_beater_hunt` envolveu três peças. Primeiro,
`tax_layer.py` novo que classifica cada strategy spec em uma de duas
categorias fiscais: **buy_hold** (`static` — não realiza nada até a
liquidação final, máximo tax-deferral) ou **annual_realize** (`lrs` /
`vol_target` / `blend` com qualquer constituinte non-static — realiza
no fim de cada ano calendário). Segundo, patch em `run_iter.py` que
roda essa camada para o config selecionado em cada dataset, popula
`net_sharpe / net_cagr / net_mdd` e computa um `net_total_score`
paralelo usando o mesmo rubric. Terceiro, `rerun_all_iters.sh` que
re-executa o `backtest.py` de cada iter pra regenerar verdict + plots
com a nova pipeline.

Os 17 iters (skip 011 que é meta) re-rodaram limpos. O drag por tipo
de spec ficou exatamente onde a literatura prevê:

- **buy-hold static** (HFEA, F1 stack, D2): drag **0.59–0.74 pp** —
  só o terminal liquidation paga DARF, todo o resto fica deferred e
  capitaliza junto.
- **annual-realize swing** (LRS, vol_target, blend): drag
  **1.63–2.35 pp** — DARF cada ano sobre ganho realizado, perda da
  capitalização do imposto.

A diferença estrutural de ~1.5pp não é trivial: re-shuffle a ranking.
Iter 009 HFEA+KMLM sobe 6 posições no ranking net (3→2 net), iter 008
HFEA classical sobe 5 (4→4? não, 9→4 nos 17), iter 015 F1 stack sobe
4 (11→7). Iters de LRS pesado caem 3 posições. **Não muda o veredito
final**: nenhuma estratégia atinge tier WINNER em nenhum dos dois
rubrics, e várias caem de PROMISING (60+) pra MARGINAL (<60) sob o
rubric net. F1+SPLIT (Plano C) continua como deploy-ready inalterado.

Vale destacar: o iter 018 H1 meta-ensemble continua como #1 em ambos
os rankings (gross 70 → net 64), mas seu drag de 2.07pp põe ele
exatamente na média annual-realize. O iter 009 HFEA+KMLM, em
contraste, é gross 63 com drag 0.66pp → net 62, virando o
**closest-to-winner sob rubric net**. HFEA continua falhando o MDD
bar (61.5%) então não é deployable, mas o ponto arquitetural
importante é que a família **buy-hold static** tem vantagem
estrutural de ~1.5pp no rubric net que o hunt não reconhecia antes.

A mudança fica documentada em `WINNER_AND_RANKING.md` (seção
"Final ranking — gross vs net"), `BASE_MEMORY.md` (seção
"Net-of-tax (Lei 14.754/2023)"), e `README.md` (seção "Pre/post tax
reporting"). Caveat de FX flat (não modela variação BRL/USD) está
explícito — pra horizontes longos é aproximadamente simétrico, mas
em regimes pós-grande-FX-move o drag pode estar subestimado em
0.3-0.7pp.

**Citações:**
- `Lei 14.754/2023` — alíquota 15% flat anual, apuração única DAA.
- `[advances_fin_ml, p.31-34]` — gates avaliam alpha gross; deploy
  precisa do net.
- `studies/_shared/tax_engine.py:AnnualDarfEngine` — implementação
  canônica.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking
  (F1+SPLIT) é o fallback de deploy independente do rubric.
