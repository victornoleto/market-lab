"""Phase 0 — SMA200 SPY-regime rotation into SSO/UPRO.

5 equity curves on the common testfolio history:
B&H SPY, B&H SSO, B&H UPRO, LRS-SSO, LRS-UPRO.

Signal: SPY close > SMA200(SPY) on day T → exposure on T+1.
Tax: BR 15% on year's realized gains, applied annually.
"""
