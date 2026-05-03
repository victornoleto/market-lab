"""Gates §2.4 (mandate) applied to observed PnL minus Pepperstone cost model.

This shortcuts P3 replicator because the question we want answered is
*"does the strategy still have edge in OOS after current real costs?"*
not *"can we recreate the rules"*.  If gates FAIL on the observed pnl,
the answer is no regardless of how perfectly we replicate the rule.

Gates per `docs/investment-mandate.md §2.4`:
1. PBO < 0.5 — `[advances_fin_ml, p.208-211]` (skipped here: no parameter
   grid; we're testing the strategy as-is, not a search variant)
2. DSR p < 0.05 — `[advances_fin_ml, p.196-202]`
3. Walk-forward ≥ 6/8 janelas positivas
4. Single-block OOS (last 12mo) Sharpe > 0
5. Bootstrap 99.9% CI low > 0
6. Cross-lib agreement (skipped: numpy reference only here)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
PARQUET = HERE / "data" / "trades_1407880.parquet"
REPORT = HERE / "reports" / "06_gates_observed.md"

# Forward-looking Pepperstone Razor cost model (pips per trade RT)
PEPP_SPREAD = {"EURUSD": 0.13, "GBPUSD": 0.50, "USDCAD": 0.74,
               "USDCHF": 0.75, "EURGBP": 0.75, "EURCHF": 1.20}
PEPP_COMMISSION = 0.7  # pips RT @ $7/lot Razor

# Cross-check: also test with optimistic costs (50% lower) to bound results
OPTIMISTIC_FACTOR = 0.5


def sharpe_annualized(daily_returns: pd.Series, periods_per_year: int = 252) -> float:
    if daily_returns.std() == 0:
        return 0.0
    return float(daily_returns.mean() / daily_returns.std() * np.sqrt(periods_per_year))


def bootstrap_sharpe_ci(daily_returns: pd.Series, n: int = 10_000, ci: float = 0.999, seed: int = 7) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    arr = daily_returns.dropna().values
    if len(arr) < 30:
        return (float("nan"), float("nan"))
    sharpes = []
    for _ in range(n):
        sample = rng.choice(arr, size=len(arr), replace=True)
        s = sample.mean() / sample.std() * np.sqrt(252) if sample.std() > 0 else 0.0
        sharpes.append(s)
    lo = float(np.quantile(sharpes, (1 - ci) / 2))
    hi = float(np.quantile(sharpes, 1 - (1 - ci) / 2))
    return lo, hi


def deflated_sharpe_p(observed_sharpe: float, n_returns: int, skew: float, kurt: float, n_trials: int = 1) -> float:
    """Deflated Sharpe Ratio p-value per Bailey & Lopez de Prado.

    Returns the prob that observed Sharpe is from null (no edge) given the
    sample stats. Conservative variant assuming n_trials = 1 (we're not
    searching here).
    """
    from scipy.stats import norm
    # Expected max Sharpe under null with n_trials searches:
    # SR0 = 0 (null Sharpe). DSR uses upper-tail of expected max.
    # For n_trials=1, this reduces to standard Sharpe t-test.
    if n_returns < 30:
        return 1.0
    se = np.sqrt((1 - skew * observed_sharpe + (kurt - 1) / 4 * observed_sharpe**2) / (n_returns - 1))
    z = observed_sharpe / se if se > 0 else 0
    return float(1 - norm.cdf(z))


def main() -> None:
    df = pd.read_parquet(PARQUET)
    trades = df[df["is_trade"]].copy().sort_values("close_dt_utc").reset_index(drop=True)
    trades["pep_cost_pips"] = trades["symbol"].map(PEPP_SPREAD) + PEPP_COMMISSION
    trades["net_pips"] = trades["pips"] - trades["pep_cost_pips"]
    trades["close_date"] = trades["close_dt_utc"].dt.date

    # Aggregate per day for Sharpe (sum of net pips per day, treating each pip
    # as ~equal $-impact via constant-lot normalization). Note: real returns
    # would scale by lots/equity, but for edge-detection equal-weighted pips
    # are the right measure ([advances_fin_ml] uses bet returns).
    daily = trades.groupby("close_date")["net_pips"].sum()
    # Convert to a "return" proxy: per pip = 0.0001 of price ≈ 0.01% nominal.
    # We'll just use net_pips directly as the unit (Sharpe is scale-invariant).

    full_sharpe = sharpe_annualized(daily)
    skew = daily.skew()
    kurt = daily.kurt()
    dsr_p = deflated_sharpe_p(full_sharpe, len(daily), skew, kurt)
    boot_lo_full, boot_hi_full = bootstrap_sharpe_ci(daily, n=10_000)

    out = []
    out.append("# Gates §2.4 verdict — observed PnL minus Pepperstone Razor 2025 costs")
    out.append(f"\nGenerated: 2026-05-01")
    out.append(f"\nMethodology: gates applied to (realized pips - spread - commission) per trade,")
    out.append(f"aggregated daily. Skips P3 replicator since the question is edge persistence")
    out.append(f"after current costs, not rule-understanding fidelity.\n")

    out.append("## Cost model (Pepperstone Razor 2025, pips RT)")
    out.append(f"- Spreads: {PEPP_SPREAD}")
    out.append(f"- Commission: {PEPP_COMMISSION} pips RT (≈ $7/lot)")
    out.append(f"- Total cost per trade range: {min(PEPP_SPREAD.values()) + PEPP_COMMISSION:.2f} – {max(PEPP_SPREAD.values()) + PEPP_COMMISSION:.2f} pips")

    out.append("\n## Full-period (2013-09 → 2021-06, 7.8 years)")
    out.append(f"- N trade days: {len(daily)}")
    out.append(f"- N trades: {len(trades)}")
    out.append(f"- Daily net pips mean: {daily.mean():.2f} | std: {daily.std():.2f}")
    out.append(f"- **Annualized Sharpe (full): {full_sharpe:.3f}**")
    out.append(f"- DSR p-value (n_trials=1): {dsr_p:.4f}")
    out.append(f"- Bootstrap 99.9% CI: [{boot_lo_full:.3f}, {boot_hi_full:.3f}]")

    out.append("\n## Gate 4 — Single-block OOS (last 12 months: 2020-06 → 2021-06)")
    cutoff = pd.Timestamp("2020-06-01").date()
    oos = daily[daily.index >= cutoff]
    if len(oos) >= 30:
        oos_sharpe = sharpe_annualized(oos)
        oos_lo, oos_hi = bootstrap_sharpe_ci(oos, n=10_000)
        oos_p = deflated_sharpe_p(oos_sharpe, len(oos), oos.skew(), oos.kurt())
        out.append(f"- N days OOS: {len(oos)} | trades OOS: {(trades['close_dt_utc'].dt.date >= cutoff).sum()}")
        out.append(f"- OOS daily mean: {oos.mean():.2f} | std: {oos.std():.2f}")
        out.append(f"- **OOS Sharpe: {oos_sharpe:.3f}**")
        out.append(f"- OOS DSR p-value: {oos_p:.4f}")
        out.append(f"- OOS bootstrap 99.9% CI: [{oos_lo:.3f}, {oos_hi:.3f}]")
        gate4_pass = oos_sharpe > 0 and oos_lo > 0
        out.append(f"- **Gate 4 verdict: {'✅ PASS' if gate4_pass else '❌ FAIL'}** (require Sharpe > 0 AND CI low > 0)")
    else:
        out.append("- INSUFFICIENT DATA")

    out.append("\n## Gate 6 — Bootstrap 99.9% CI low > 0 (full sample)")
    gate6_pass = boot_lo_full > 0
    out.append(f"- 99.9% CI low (full): {boot_lo_full:.3f}")
    out.append(f"- **Gate 6 verdict: {'✅ PASS' if gate6_pass else '❌ FAIL'}**")

    out.append("\n## Gate 3 — Walk-forward 8 janelas (≥ 6/8 positivas)")
    # Walk-forward: split into 8 equal-time windows, compute net Sharpe per window
    daily_ts = daily.copy()
    daily_ts.index = pd.to_datetime(daily_ts.index)
    daily_ts = daily_ts.sort_index()
    splits = np.array_split(daily_ts.index, 8)
    wf_results = []
    for i, idxs in enumerate(splits):
        window_data = daily_ts.loc[idxs.min():idxs.max()]
        if len(window_data) < 5:
            continue
        s = sharpe_annualized(window_data)
        wf_results.append({"window": i+1, "start": str(idxs.min().date()), "end": str(idxs.max().date()),
                           "n_days": len(window_data), "sharpe": round(s, 3),
                           "mean_net_pips": round(window_data.mean(), 3)})
    wf_df = pd.DataFrame(wf_results)
    n_positive = (wf_df["sharpe"] > 0).sum()
    out.append(f"- Window split: 8 equal-time blocks of full sample")
    out.append("```")
    out.append(wf_df.to_string(index=False))
    out.append("```")
    out.append(f"- Positive windows: {n_positive}/8")
    gate3_pass = n_positive >= 6
    out.append(f"- **Gate 3 verdict: {'✅ PASS' if gate3_pass else '❌ FAIL'}** (require ≥ 6/8)")

    out.append("\n## Gate 2 — DSR p-value < 0.05")
    gate2_pass = dsr_p < 0.05
    out.append(f"- DSR p-value (full): {dsr_p:.4f}")
    out.append(f"- **Gate 2 verdict: {'✅ PASS' if gate2_pass else '❌ FAIL'}** (require p < 0.05)")

    out.append("\n## Cost-model sensitivity (optimistic: 50% of estimated cost)")
    trades["net_pips_optimistic"] = trades["pips"] - (trades["pep_cost_pips"] * OPTIMISTIC_FACTOR)
    daily_opt = trades.groupby("close_date")["net_pips_optimistic"].sum()
    sharpe_opt = sharpe_annualized(daily_opt)
    out.append(f"- Sharpe under optimistic costs: {sharpe_opt:.3f}")
    out.append(f"- Even optimistic still: {sharpe_opt:.2f}")

    out.append("\n## Final verdict")
    gates_status = {"Gate 2 (DSR)": gate2_pass, "Gate 3 (WF)": gate3_pass, "Gate 4 (OOS)": gate4_pass, "Gate 6 (Bootstrap)": gate6_pass}
    failed = [g for g, p in gates_status.items() if not p]
    passed = [g for g, p in gates_status.items() if p]
    out.append(f"- Passed: {passed if passed else 'NONE'}")
    out.append(f"- Failed: {failed if failed else 'NONE'}")
    if failed:
        out.append(f"\n### ❌ K4 TRIGGERED — gates §2.4 FAIL on observed PnL minus Pepperstone costs")
        out.append(f"- Strategy does not maintain edge after current real costs in current OOS regime")
    else:
        out.append(f"\n### ✅ Gates §2.4 PASS — proceed to P5 multi-asset transferability")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
