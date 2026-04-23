# Reprodução do pipeline

Execute os scripts na ordem (todos tomam ~10-15 min no total):

```bash
# Requer TIINGO_API_KEY no .env do projeto
cd /var/www/pessoal/ai-trade

# 1) Baixa ETFs via yfinance (fallback) e existing Tiingo parquets
python3 reports/portfolio_aposentadoria_v2/scripts/01_download_etfs.py

# 2) Baixa ETFs faltantes via Tiingo REST API direto
python3 reports/portfolio_aposentadoria_v2/scripts/01b_download_tiingo_direct.py

# 3) Corrige bug de adj_close nos parquets do projeto
python3 reports/portfolio_aposentadoria_v2/scripts/01c_fix_adj_close.py

# 4) Constrói panel unificado mensal 1926-2026 com sintéticos
python3 reports/portfolio_aposentadoria_v2/scripts/02_build_returns_panel.py

# 5) (Opcional) Self-test do engine de simulação
python3 reports/portfolio_aposentadoria_v2/scripts/03_portfolio_sim.py

# 6) Backtests das 12 carteiras candidatas + bootstrap + SWR
python3 reports/portfolio_aposentadoria_v2/scripts/05_run_backtests.py

# 7) Backtests das 4 carteiras finais
python3 reports/portfolio_aposentadoria_v2/scripts/06_final_portfolios.py
```

## Dependências

- `yfinance>=0.2` (fallback)
- `pandas`, `numpy` (core)
- `requests`, `python-dotenv` (Tiingo REST)
- `pyarrow` (parquet)

## Arquivos produzidos

- `data/*.parquet` — 37 ETFs + sintéticos (1885-2026) — **não versionados** (`.gitignore`)
- `data/returns_daily.parquet`, `returns_monthly.parquet` — panel unificado
- `data/_sources.json` — metadata de cada ticker (inception, fonte)
- `data/_panel_meta.json` — metadata do panel unificado
- `data/web_research.md` — pesquisa web 2024-2026 (versionado)
- `results/backtest_summary.csv` — 36 linhas (12 carteiras × 3 janelas)
- `results/portfolio_details.json` — detalhes completos (bootstrap, SWR)
- `results/final_portfolios.json` — as 4 carteiras otimizadas finais

## Estrutura do código

- `03_portfolio_sim.py` — engine de simulação reutilizável
  - `SimConfig` / `SimResult` dataclasses
  - `simulate(weights, panel, config)` — backtest determinístico
  - `block_bootstrap_paths()` — stationary block bootstrap
  - `swr_test()` — busca binária por SWR
- `04_candidate_portfolios.py` — define 12 carteiras-candidatas com
  `weights_real` (ETFs reais) e `weights_proxy` (substitutos long-history)
- `06_final_portfolios.py` — as 4 carteiras finais sintetizadas + runs

## Notas

- Panel usa 30% withholding em dividendos sem compensação (conservador).
- Rebalanceamento mensal (trabalho real = por aportes, zero DARF).
- LETF proxy fees (`SPY_2x_sim`, `SPY_3x_sim`) deduzem 1.3%/1.7%/ano para
  aproximar SSO/UPRO realistas incluindo borrow cost implícito.
- Return Stacked proxies (`RSST_syn`) usam `1.0 * SPY + 1.0 * DBMF` — imperfeito
  pra janelas longas (DBMF só vai a 2019).

## Caveats

- AVUV_syn_3f / AVUS_syn_3f usam factor loadings **literatura** (não
  refitted). Podem superestimar ou subestimar o fator específico.
- NTSX_syn (0.9 SPY + 0.6 IEF) é proxy; o NTSX real usa Treasury futures
  com duração variável.
- Managed futures long-run proxy (`SPY_1x_sim`) subestima MF em janelas
  pre-2019 — use janela 2006-2026 como referência primária.
