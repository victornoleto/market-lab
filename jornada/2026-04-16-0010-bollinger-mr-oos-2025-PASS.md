# 2026-04-16 00:10 — OOS 2025 Hold-out: Bollinger MR edge CONFIRMA em dados futuros

**Verdict: OOS PASS — zero decay, edge ligeiramente mais forte em 2025.**

Teste de robustez temporal mais severo possível: treinar em 2021-2024 (6252 bars), testar em 2025 puro (1560 bars) sem re-otimização. O config vencedor (window=20, std_mult=1.5) foi fixado a priori — zero data-snooping no período OOS.

## Resultado comparativo

| Metrica | Training (2021-2024) | OOS (2025) | Delta |
|---------|---------------------|------------|-------|
| Sharpe (anualizado) | 1.293 | **1.312** | +1.5% |
| CAGR | 16.16% | **17.01%** | +0.85pp |
| Max Drawdown | -13.49% | **-11.16%** | melhorou |
| Win rate | 73.4% | **74.4%** | +1.0pp |
| Trades | — | 43 | ~3.6/mês |

## O que isso significa

O edge de mean-reversion do Bollinger em SPY 1h **não é artefato do período de treinamento**. Em 2025, com condições de mercado diferentes (rates mais altos, volatilidade diferente), a estratégia performou igualmente bem — ou melhor.

Isso é incomum. Na maioria dos backtests, o Sharpe OOS cai 30-50% vs in-sample `[advances_fin_ml, p.208-211, ch.12]`. Aqui subiu 1.5%. Possíveis explicações:
- SPY tem micro-reversão estrutural em 1h (market makers sustentam o bid)
- O mecanismo é simples demais para over-fitar (2 params livres apenas)
- 2025 teve drawdowns que geraram mais oportunidades de dip-buying

## Validação cruzada: QQQ e IWM (iterações 3 e 4)

Para contexto — o loop também testou QQQ e IWM com os mesmos 4 configs:

| Ativo | Sharpe best | PBO | DSR p | WF | Verdict |
|-------|-------------|-----|-------|----|---------|
| **SPY** | **1.314** | 0.254 | **0.0305** | **7/8** | **PASS** |
| QQQ | 0.991 | 0.349 | 0.152 | 6/8 | FAIL (DSR) |
| IWM | 1.021 | 0.444 | 0.128 | 7/8 | FAIL (DSR) |

Edge existe nos 3 ativos (PBO e WF passam), mas só SPY tem Sharpe alto o suficiente para DSR. Estratégia é concentrada em SPY — o que é bom para produção (SPX500 é o CFD mais líquido na Pepperstone).

## Config usado

| Param | Valor |
|-------|-------|
| window | 20 |
| std_mult | 1.5 |
| stop_pct | 0.02 |
| max_hold | 24 bars (1 dia) |

## Arquivos

- Script OOS: `scripts/run_oos_bollinger_mr.py`
- Relatório original (training): `reports/grid_bollinger_mr_spy_1h_8wf_20260415-235041/summary.md`
- Diagnostics QQQ: `reports/grid_bollinger_mr_qqq_1h_8wf_20260415-235705/diagnostic.md`
- Diagnostics IWM: `reports/grid_bollinger_mr_iwm_1h_8wf_20260415-235909/diagnostic.md`

## Próximo passo

Sensibilidade a custos de transação (spread Pepperstone + comissão) — verificar se o CAGR de 17% sobrevive a fricção real. Depois: regime filter ablation e paper trading.
