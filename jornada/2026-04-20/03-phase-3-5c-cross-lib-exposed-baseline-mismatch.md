# Phase 3.5c cross-lib validation — descobriu que baseline não é comparável

## O que aconteceu

Rodamos a cross-lib validation (Phase 3.5c) pela primeira vez. Ela foi construída pra responder "o winner Plano B V4 do Phase 3.5b é real ou é artifact?" — reimplementando a mesma estratégia em 4 libs Python independentes (bt, vectorbt, backtrader, quantstats) e vendo se todas concordam com o baseline.

Resultado: as 4 libs **concordam entre si** (dentro de 1-2pp de CAGR), mas **discordam fortemente do baseline Phase 3.5b**. O baseline diz CAGR=37.92% / max_dd=-16.91% pra Plano B V4. As 4 libs dizem CAGR≈11.6% / max_dd≈-28.8%.

## O que isso quer dizer

A primeira leitura seria "Plano B V4 é folclore". Mas investigando mais fundo, descobri que a comparação **não é apples-to-apples**:

1. **Phase 3.5b usou dados terceiros proprietários** (testfol.io SSOSIM/QLDSIM/UGLSIM). Nossa stack reimplementa do zero usando `synthesize_letf_returns_ffr_aware` + yfinance. **Modelos sintéticos de LETF diferentes** podem dar CAGR materialmente diferente ao longo de 20-40 anos.

2. **Windows não batem.** O baseline diz `plano_b_v4_threshold_10["canonical"]` = 37.92%, mas no arquivo-fonte Phase 3.5b essa métrica é pra 1986-2026 (40 anos). Nossa cross-lib canonical é 2004-2026 (21.5 anos). **Não é a mesma série.**

3. **Leg baselines usam instrumentos errados.** `leg_qld_only` tem baseline CAGR=17.40% porque o arquivo-fonte é `qqq_donchian_20_10` — **QQQ unleveraged**, não QLD (2× LETF). Idem pra GLD/UGL. Então REFUTES nos legs é esperado — baseline aponta pro instrumento errado.

4. **Extended window nossa é degenerada.** Pra 1986-1999, Tiingo não tem QQQ e não tem GLD. Só SPY-TR. Então durante 13 anos da extended window, a "3-leg EW portfolio" tem só 1 leg ativa. Phase 3.5b com testfol.io teria tido dados de NDX-TR de 1985+ e ouro spot de 1968+ — que nossa stack não tem.

## O que ficou provado

- **Nossa engine de 3-leg EW rebalance está correta.** 3 implementações paradigmaticamente diferentes (vectorizado, NumPy compilado, event-driven) batem dentro de 2pp de CAGR. Isso é forte.
- **Dois bugs reais foram descobertos e consertados:**
  - Seam stitching em `reference_prices.py` — synthetic ia até 154.94 e depois caía pra 3.65 real na inception date (42× de salto fantasma). Corrigido com scaling.
  - Ring-buffer em backtrader adapter — `feed.datetime.date(i)` em `__init__` retorna index 0 = último bar, scrambling as datas do signal. Corrigido com pre-build via pandas Series.

## O que não ficou provado

- **Se Plano B V4 é real.** Pra responder precisa rodar a cross-lib usando dados testfol.io SSOSIM/QLDSIM/UGLSIM (mesma fonte que Phase 3.5b). Se as libs baterem em ~37.92% usando esses dados, nossa engine está certa e a divergência é 100% modelo synthetic. Se baterem em ~11.6%, Phase 3.5b tinha bug na engine dela.
- **Se nossa `synthesize_letf_returns_ffr_aware` é fiel a realidade.** Pode tá conservadora ou otimista demais comparado a testfol.io.

## Próximo passo

Ainda **não decidido**. Três caminhos possíveis:

- **A — Obter CSVs testfol.io** (1-2 sessões). Exportar SSOSIM/QLDSIM/UGLSIM da UI, construir fetcher alternativo, rodar cross-lib contra testfol.io data. Separar diagnóstico: engine bug vs synthetic model divergence.
- **B — Head-to-head synthetic pós-inception** (1 sessão). Comparar nossa SSO pós-2006-06-21 (que usa yfinance real) com SSOSIM testfol.io pós-mesma data. Se bate, synthetic model é equivalente. Se não bate, LETF model nosso difere mesmo com dado real.
- **C — Reabrir Phase 3.5b** (2-3 sessões). Rodar `letf_rotation.py` + `portfolio_3leg_ew` em cima da nossa `reference_prices.parquet` (não testfol.io). Se sair ~11.6%, confirma que Phase 3.5b só "validou" contra testfol.io, nunca contra nossa data pipeline.

Minha recomendação: **começar pela Ação B** (mais barato) e depois A se necessário.

## Status Phase 4

**HOLD.** Não ir pra paper trading com Plano B V4 até a divergência estar entendida. Se o winner só existe em testfol.io data e nossa realidade produz 11.6% CAGR / -28.8% max_dd, isso está **abaixo** do gate CDI (~14%) e **acima** do gate max_dd (25%) — folclore, não winner.

## Arquivos

- `reports/phase_3_5c/cross_lib/VERDICT.md` — matrix com todos REFUTES/BLOCKED
- `docs/superpowers/findings/2026-04-20-phase-3-5c-baseline-mismatch.md` — análise técnica detalhada
- Commits: `9cc2e36` (initial BLOCKED), `b27ccb0` (fixes + revertido parcial), `393dc8b` (baseline restaurado), `0feb4fb` (findings doc)

## Citações

- `[advances_fin_ml, p.31-34]` — two-stage replication protocol
- `[advances_fin_ml, p.208-211]` — PBO, rejeição de winners não reproduzíveis
- `[leverage_for_the_long_run, p.16]` — synthetic LETF formula (não cobre validação cross-source)
