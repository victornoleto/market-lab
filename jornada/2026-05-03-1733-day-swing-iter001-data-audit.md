# Day/swing strategy hunt — iteracao 001 auditou dados e baselines

Rodei a primeira iteracao do loop `studies/day_swing_strategy_hunt/` sem testar uma estrategia completa. O objetivo foi apenas verificar se existe base operacional para comecar a Familia A, Time-Series Momentum H4/D1.

Resultado: `positive` para infraestrutura/auditoria. A fonte Dukascopy BID retornou dados D1 e H4 para EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD, XAUUSD, BTCUSD e ETHUSD na janela 2018-01-01 a 2026-05-01. Foram gravados `PRE_REG.md`, `DATA_AUDIT.csv`, `RESULTS.json`, `SUMMARY.md` e o script reproduzivel da iteracao.

Os baselines mostram que buy-and-hold multi-asset ficou forte nessa janela, muito por Gold/Crypto, e que H4 sofre bastante com custos: controles random/uniform matched-turnover ficam negativos no stress. Portanto a proxima estrategia precisa vencer baselines multi-asset e controles de turnover, nao apenas encontrar um single-asset winner.

Capital segue 100% Plano C; Plano A segue DORMANT; sem paper/live. Nao houve mudanca em `docs/investment-mandate.md` nem em `frozen_rules/`.
