"""Phase 1 — sweep of (SMA/EMA) × lookback {20..300 step 5} × risk-off {CASH, GLD, IEF, ZROZ}.

912 configs per on-leg × 2 on-legs (SSO, UPRO) × 2 tax scenarios = 1,824 scored
strategies. Discovery-only; top-N candidates feed a separate phase-2 honest
walk-forward + bootstrap validation pass.
"""
