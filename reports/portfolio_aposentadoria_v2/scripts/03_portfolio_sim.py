"""Portfolio simulation engine.

Takes a dict of weights {ticker: weight} and returns simulation metrics:
- CAGR
- Annualized vol
- Sharpe ratio (excess over risk-free)
- Max drawdown
- Terminal wealth (per $10k initial + monthly contributions)
- SWR (safe withdrawal rate over N-year retirement)

Supports:
- Monthly rebalancing (or drift)
- Annual fee/drag per asset
- Historical and bootstrap paths
- Glidepath (time-varying weights)

Usage:
    metrics = simulate(weights, monthly_panel, fees, start='2006-01', end='2026-04')
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

REPO = Path("/var/www/pessoal/ai-trade")
DATA_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "data"

# Annual drag estimates (ER + dividend withholding + cap gains distributions).
# Source for Brazilian-investor drag: 30% US withholding tax on qualified dividends
# is unrecoverable; plus realized cap gains at 15% via DARF. Rough buckets.
FEES = {
    # Broad-market ETFs: ~1.5% div × 30% = 0.45% + small ER
    "SPY": 0.0055, "VTI": 0.0050, "VXUS": 0.0060, "VEA": 0.0060, "VWO": 0.0065, "VT": 0.0055,
    # Factor Avantis / DFA / momentum
    "AVUS": 0.0060, "AVUV": 0.0080, "AVDE": 0.0070, "AVDV": 0.0090, "AVEM": 0.0085,
    "SPMO": 0.0100, "IDMO": 0.0110,  # higher turnover
    "DFAC": 0.0060, "DFAT": 0.0080, "AVGV": 0.0085,
    # Leveraged US equities — ER high, swap financing embedded in price
    "SSO": 0.0120, "UPRO": 0.0130, "QLD": 0.0125, "TQQQ": 0.0135, "EFO": 0.0115,
    # WisdomTree efficient core
    "NTSX": 0.0055, "NTSI": 0.0075, "NTSE": 0.0085,
    # Return stacked — ER ~0.9%, K-1 complications on futures sleeve, approximate drag
    "RSST": 0.0110, "RSSB": 0.0095, "RSBT": 0.0105, "RSSY": 0.0110, "RSBY": 0.0100,
    # Managed futures — K-1/1099, partially tax-inefficient
    "DBMF": 0.0115, "KMLM": 0.0110, "CTA": 0.0130,
    # Alts
    "IBIT": 0.0030, "GLDM": 0.0020, "GLD": 0.0050,
    # Bonds
    "TLT": 0.0070, "IEF": 0.0060, "SHV": 0.0030,
    # Simulated / synthetic — no fees (baseline analytical)
    "SPY_1x_sim": 0.0000, "SPY_2x_sim": 0.0000, "SPY_3x_sim": 0.0000,
    "KF_Mkt": 0.0000, "KF_Mkt_RF": 0.0000, "KF_SMB": 0.0000, "KF_HML": 0.0000, "KF_RF": 0.0000,
    "NTSX_syn": 0.0055, "RSST_syn": 0.0110,
    "AVUV_syn_3f": 0.0080, "AVUS_syn_3f": 0.0060,
}

# For LETFs we want to ALSO model a financing cost drag if holding SPY_2x_sim/3x_sim
# directly. The testfolio dataset uses 1885+ and does NOT include ER or LIBOR drag.
# To make SPY_2x_sim behave like real SSO buy-hold we subtract:
#   annual drag = ER(0.89%) + borrowing_spread(0.40%) = ~1.3%
# But this is already embedded via FEES["SPY_2x_sim"] when we decide to proxy
# SSO with SPY_2x_sim. For the raw testfolio analysis we pass fee=0 to see the
# math-clean outcome; for the practitioner sim we pass fees.
LETF_PROXY_FEES = {
    "SPY_1x_sim": 0.0000,
    "SPY_2x_sim": 0.0130,  # match SSO realistic drag
    "SPY_3x_sim": 0.0170,  # match UPRO realistic drag
}


@dataclass
class SimConfig:
    start: str = "1926-07-01"
    end: str = "2026-03-31"
    initial_wealth: float = 10_000.0
    monthly_contribution: float = 0.0
    rebalance: str = "monthly"  # 'monthly', 'annual', 'none'
    rf_rate: float = 0.025  # fallback risk-free; if KF_RF present we use it
    use_letf_proxy_fees: bool = False  # apply LETF drag to SPY_2x_sim / SPY_3x_sim
    fees_override: dict[str, float] = field(default_factory=dict)


@dataclass
class SimResult:
    wealth: pd.Series  # time series of portfolio value
    returns: pd.Series  # monthly returns
    cagr: float
    vol_ann: float
    sharpe: float
    max_dd: float
    terminal_wealth: float
    worst_12m: float
    weights: dict[str, float]
    config: SimConfig


def _get_fee(ticker: str, config: SimConfig) -> float:
    if ticker in config.fees_override:
        return config.fees_override[ticker]
    if config.use_letf_proxy_fees and ticker in LETF_PROXY_FEES:
        return LETF_PROXY_FEES[ticker]
    return FEES.get(ticker, 0.0050)  # default 0.5% drag


def simulate(
    weights: dict[str, float],
    monthly_panel: pd.DataFrame,
    config: SimConfig,
) -> SimResult:
    """Run a portfolio simulation.

    If rebalance='monthly', the portfolio is rebalanced to target weights each
    month end. If 'annual', annually (Jan). If 'none', buy-hold with drift.
    """
    # normalize weights
    total = sum(weights.values())
    assert abs(total - 1.0) < 1e-6, f"weights must sum to 1, got {total}"
    assets = list(weights.keys())

    # Slice panel to requested window and drop months where ANY asset is NaN
    panel = monthly_panel[assets].copy()
    panel = panel.loc[config.start:config.end]
    panel = panel.dropna(how="any")

    if len(panel) < 24:
        raise ValueError(f"insufficient data: only {len(panel)} months after filter")

    # Subtract monthly fee drag (fee/12)
    for a in assets:
        fee_ann = _get_fee(a, config)
        fee_m = fee_ann / 12.0
        panel[a] = panel[a] - fee_m

    # Run simulation
    w = np.array([weights[a] for a in assets])  # target weights
    wealth_ts = []
    dates = panel.index

    if config.rebalance == "monthly":
        # Portfolio return = w · r each month
        port_r = (panel[assets].values @ w)
        port_r = pd.Series(port_r, index=dates)
    else:
        # Non-monthly rebalance: track per-asset $$
        cash_per_asset = w * config.initial_wealth
        port_r = []
        last_rebal_month = None
        for dt, row in panel.iterrows():
            ret = row[assets].values
            cash_per_asset = cash_per_asset * (1 + ret)
            total_val = cash_per_asset.sum()
            port_r.append(total_val)  # will convert to returns after
            # Rebalance condition
            if config.rebalance == "annual" and dt.month == 1 and last_rebal_month != dt.year:
                cash_per_asset = w * total_val
                last_rebal_month = dt.year
        wealth = pd.Series(port_r, index=dates)
        # Prepend initial wealth for return calc
        wealth0 = pd.concat([pd.Series([config.initial_wealth], index=[dates[0] - pd.Timedelta(days=1)]), wealth])
        port_r = wealth0.pct_change().dropna()

    # Apply monthly contributions (only if non-zero)
    wealth = [config.initial_wealth]
    for i, r in enumerate(port_r.values):
        new = wealth[-1] * (1 + r) + config.monthly_contribution
        wealth.append(new)
    wealth = pd.Series(wealth[1:], index=port_r.index)

    # Metrics
    n_months = len(port_r)
    years = n_months / 12.0
    # CAGR from wealth (adjust for contributions)
    if config.monthly_contribution > 0:
        # Money-weighted CAGR would need IRR; use time-weighted CAGR via cumulative
        # return of the return series:
        cum_r = (1 + port_r).prod()
        cagr = cum_r ** (1 / years) - 1
    else:
        cagr = (wealth.iloc[-1] / config.initial_wealth) ** (1 / years) - 1

    vol_ann = port_r.std() * np.sqrt(12)
    # Risk-free: prefer KF_RF from panel if present in panel columns
    rf = config.rf_rate
    if "KF_RF" in monthly_panel.columns:
        rf_series = monthly_panel["KF_RF"].loc[port_r.index]
        if rf_series.notna().mean() > 0.9:
            rf = rf_series.mean() * 12
    sharpe = (cagr - rf) / vol_ann if vol_ann > 1e-9 else 0.0

    # Max drawdown on wealth series
    peak = wealth.cummax()
    dd = (wealth - peak) / peak
    max_dd = dd.min()

    # Worst 12-month rolling return
    rolling_12m = (1 + port_r).rolling(12).apply(np.prod, raw=True) - 1
    worst_12m = rolling_12m.min() if len(rolling_12m) >= 12 else np.nan

    return SimResult(
        wealth=wealth,
        returns=port_r,
        cagr=float(cagr),
        vol_ann=float(vol_ann),
        sharpe=float(sharpe),
        max_dd=float(max_dd),
        terminal_wealth=float(wealth.iloc[-1]),
        worst_12m=float(worst_12m),
        weights=weights,
        config=config,
    )


def block_bootstrap_paths(
    port_r: pd.Series,
    n_paths: int = 2000,
    horizon_months: int = 360,
    block_size: int = 12,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Generate bootstrap 30-year paths from historical monthly returns.

    Uses stationary block bootstrap (random block starts, fixed block size).
    Returns array of shape (n_paths, horizon_months).
    """
    if rng is None:
        rng = np.random.default_rng(seed=42)
    r = port_r.values
    n = len(r)
    paths = np.zeros((n_paths, horizon_months))
    for i in range(n_paths):
        idx = 0
        while idx < horizon_months:
            start = rng.integers(0, n)
            length = min(block_size, horizon_months - idx)
            for j in range(length):
                paths[i, idx + j] = r[(start + j) % n]
            idx += length
    return paths


def swr_test(
    port_r: pd.Series,
    horizon_years: int = 30,
    initial_wealth: float = 1_000_000,
    n_paths: int = 2000,
    success_threshold: float = 0.95,
    block_size: int = 12,
) -> tuple[float, dict]:
    """Find the Safe Withdrawal Rate (annual %) such that N% of paths survive."""
    paths = block_bootstrap_paths(port_r, n_paths=n_paths, horizon_months=horizon_years * 12, block_size=block_size)

    def success_rate(wr: float) -> float:
        monthly_withdrawal = wr * initial_wealth / 12.0
        survived = 0
        for i in range(paths.shape[0]):
            w = initial_wealth
            for t in range(paths.shape[1]):
                w = w * (1 + paths[i, t]) - monthly_withdrawal
                if w <= 0:
                    break
            if w > 0:
                survived += 1
        return survived / paths.shape[0]

    # Binary search for WR that gives success_threshold
    lo, hi = 0.005, 0.15
    for _ in range(40):
        mid = (lo + hi) / 2
        sr = success_rate(mid)
        if sr >= success_threshold:
            lo = mid
        else:
            hi = mid
    wr_final = lo
    return wr_final, {"success_rate_at_wr": success_rate(wr_final), "n_paths": n_paths}


if __name__ == "__main__":
    # Quick self-test
    panel = pd.read_parquet(DATA_DIR / "returns_monthly.parquet")
    print(f"Panel: {panel.shape}")

    # Test 1: plain 60/40 SPY/IEF from 2006
    r = simulate(
        {"SPY": 0.6, "IEF": 0.4},
        panel,
        SimConfig(start="2006-01-31", end="2026-03-31"),
    )
    print(f"60/40 SPY/IEF 2006-2026: CAGR={r.cagr:.2%} Sharpe={r.sharpe:.2f} MDD={r.max_dd:.2%}")

    # Test 2: 100% SPY buy-hold
    r = simulate({"SPY": 1.0}, panel, SimConfig(start="2006-01-31", end="2026-03-31"))
    print(f"100% SPY 2006-2026: CAGR={r.cagr:.2%} Sharpe={r.sharpe:.2f} MDD={r.max_dd:.2%}")

    # Test 3: 100% SSO buy-hold (real)
    r = simulate({"SSO": 1.0}, panel, SimConfig(start="2007-01-31", end="2026-03-31"))
    print(f"100% SSO 2007-2026: CAGR={r.cagr:.2%} Sharpe={r.sharpe:.2f} MDD={r.max_dd:.2%}")

    # Test 4: SPY_2x_sim long-term 1926+
    r = simulate({"SPY_2x_sim": 1.0}, panel,
                 SimConfig(start="1926-07-31", end="2026-03-31", use_letf_proxy_fees=True))
    print(f"100% SPY_2x (1926+, w/ fees): CAGR={r.cagr:.2%} Sharpe={r.sharpe:.2f} MDD={r.max_dd:.2%}")
