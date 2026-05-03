# spy_beater_hunt — re-run do RSST 70/30 concluído

Rodei o rebaseline do `spy_beater_hunt` com o proxy corrigido do RSST: `SPY + 70% DBMF + 30% KMLM - cash`, financiado com `CASHX?E=-2`.

Correção posterior na mesma sessão: para cenários static buy-and-hold/lazy-rebal, não aplicamos DARF. Imposto fica reservado para estratégias swing/táticas que realizam ganho via trocas de posição.

Como DBMF só começa em 2000, forcei todos os portfólios para a mesma janela comum 2000-01-03 -> 2026-05-01. Isso evita comparar CAGR de janelas diferentes.

Resultado principal:

| estratégia | CAGR sem imposto | MDD | Sharpe |
|---|---:|---:|---:|
| L1 CEGB | 9.66% | -25.43% | 0.696 |
| B4 ZROZ | 11.00% | -29.60% | 0.671 |
| T1 gold-heavy | 11.65% | -35.80% | 0.643 |
| B2 TMF10 | 11.59% | -37.91% | 0.631 |
| B5 no-duration | 12.00% | -44.56% | 0.599 |
| SPY | 8.06% | -55.26% | 0.400 |

Leitura: B4 deixou de ser o maior Sharpe absoluto quando o RSST foi corrigido; L1 CEGB passou à frente. Mas B4 continua sendo o melhor compromisso entre CAGR e drawdown entre os stacks com RSST: entrega mais CAGR que L1 com MDD ainda abaixo de 30%. B5/T1/B2 entregam mais CAGR, mas com drawdowns na faixa de 36-45%.

Isso é correção de proxy, não nova otimização. A tese permanece baseada em return stacking `[risk_parity, ch.5, p.10]` e diversificação de managed-futures engines `[ilmanen_expected_returns, ch.19]`.

Capital permanece 100% Plano C. Nenhum deploy autorizado.
