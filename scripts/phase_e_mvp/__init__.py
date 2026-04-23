"""Phase E-MVP — Strategy E (multi-market cross-sectional ranking).

Extension of Strategy D's signal families (Clenow momentum, low-vol+mom
hybrid) to a **larger cross-sectional universe** combining US and BR
markets. Motivation: Strategy D MVP failed in 10/10 IBrX-100 configs
with −1.06 median IS→OOS Sharpe decay (see
``reports/phase_d_mvp/BREADTH_NO_WINNER_D.md``). The literature that
justifies these signals (Clenow, Chan, AFML) was developed on the US
universe with ~500-2000 tickers; Strategy D's 83-ticker BR subset is
below the cross-section density these papers assume.

Entry points:
- ``universe.py``        — SP500 top-200 + IBrX-100 = ~300 tickers
- ``download.py``        — yfinance fetch for the combined universe
- ``cost_model.py``      — per-ticker cost/tax (US 15% DARF / BR R$20k exempt)
- ``run_engine.py``      — one-config backtest with PRELOADED data (no I/O)
- ``orchestrator.py``    — grid loop, preloads data once, reuses across runs
- ``analyze.py``         — PBO/DSR + SUMMARY writer
- ``run_end_to_end.py``  — autonomous pipeline (download → grid → verdict)

Key optimization vs Phase D: ``load_ohlcv`` runs ONCE at orchestrator
start. Each config run receives the in-memory dict — eliminates the I/O
gargalo that made Phase D-MVP take 17-20h (now estimated ~4-5h).
"""
