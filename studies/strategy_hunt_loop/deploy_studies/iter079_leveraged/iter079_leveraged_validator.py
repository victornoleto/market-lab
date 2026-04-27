"""Iter 079 leveraged variants — substitute winning asset by 2×/3× LETF.

User's hypothesis: when iter 079's top-K=1 momentum signal selects SPY for
the next month, instead of holding SPY (1×), hold SSO (2×) or UPRO (3×).
Same logic for QQQ→QLD/TQQQ, GLD→UGL (only 2× available), TLT→UBT/TMF
(synthesized from ZROZSIM since no TLT-LETF synth in cache). EFA stays 1×
(no LETF synth available). AGG fallback stays 1×.

Mechanism:
  1. Compute trailing 12-month return per UNDERLYING asset (SPY/QQQ/EFA/TLT/GLD)
  2. Pick top-K = 1 by momentum (same as iter 079)
  3. If picked asset has lookback ≥ 0%: hold its LEVERAGED version next month
  4. If picked asset has lookback < 0%: route to AGG fallback (1×, unchanged)

The momentum signal sees the underlying performance; execution swaps to LETF.
This is the natural reading of "se SPY rendeu mais, comprar SSO/UPRO".

Variants
--------
  iter079_1x  — baseline, all 1× (matches original iter 079)
  iter079_2x  — substitute SPY→SSO, QQQ→QLD, GLD→UGL, TLT→UBT (synth 2×ZROZ)
  iter079_3x  — substitute SPY→UPRO, QQQ→TQQQ, TLT→TMF (synth 3×ZROZ);
                EFA and GLD stay 1× (no widely-available 3× LETF)

Citations
---------
* `[stocks_on_the_move, p.21-30]` — Clenow momentum framework.
* Antonacci 2014/2017 — GEM dual-momentum primary source.
* Faber 2007 — abs-mom filter.
* `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead).
* `[advances_fin_ml, p.196-202]` — bootstrap CI G6.
* `[advances_fin_ml, p.222-223]` — DSR with n_trials.
* `[risk_parity, ch.5]` — leveraged ETF context (vol drag warning).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
TF_PATH = ROOT / "data/testfolio/cache/history.parquet"
OUT_DIR = Path(__file__).resolve().parent

TRADING_DAYS = 252
LOOKBACK_MONTHS = 12  # iter 079 best cfg lookback
TRANS_COST_BPS = 5.0   # iter 079 standard

# LETF expense ratios
ER_TMF = 0.0105 / TRADING_DAYS
ER_UBT = 0.0095 / TRADING_DAYS

SELECTABLE = ["SPY", "QQQ", "EFA", "TLT", "GLD"]
ALL_SLEEVES = SELECTABLE + ["AGG"]


# --- Asset return mapping per variant ---------------------------------------


def returns_1x(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Underlying 1× returns (matches original iter 079)."""
    return {
        "SPY": df["SPYSIM"].pct_change().dropna(),
        "QQQ": df["QQQSIM"].pct_change().dropna(),
        "EFA": df["VEASIM"].pct_change().dropna(),  # VEA is intl developed analog
        "TLT": df["ZROZSIM"].pct_change().dropna(),  # ZROZ as long-bond proxy
        "GLD": df["GLDSIM"].pct_change().dropna(),
        "AGG": df["BNDSIM"].pct_change().dropna(),
    }


def returns_2x(df: pd.DataFrame) -> dict[str, pd.Series]:
    """2× LETFs where available; signal still on 1× underlyings."""
    r_zroz = df["ZROZSIM"].pct_change().dropna()
    return {
        "SPY": df["SSOSIM"].pct_change().dropna(),  # 2× SPY
        "QQQ": df["QLDSIM"].pct_change().dropna(),  # 2× QQQ
        "EFA": df["VEASIM"].pct_change().dropna(),  # no 2× EFA synth — stays 1×
        "TLT": (2.0 * r_zroz - ER_UBT).dropna(),    # synth UBT (2× long bond)
        "GLD": df["UGLSIM"].pct_change().dropna(),  # 2× gold
        "AGG": df["BNDSIM"].pct_change().dropna(),  # fallback stays 1×
    }


def returns_3x(df: pd.DataFrame) -> dict[str, pd.Series]:
    """3× LETFs where available."""
    r_zroz = df["ZROZSIM"].pct_change().dropna()
    return {
        "SPY": df["UPROSIM"].pct_change().dropna(),   # 3× SPY
        "QQQ": df["TQQQSIM"].pct_change().dropna(),   # 3× QQQ
        "EFA": df["VEASIM"].pct_change().dropna(),    # no 3× EFA — stays 1×
        "TLT": (3.0 * r_zroz - ER_TMF).dropna(),      # synth TMF (3× long bond)
        "GLD": df["GLDSIM"].pct_change().dropna(),    # no widely-available 3× gold
        "AGG": df["BNDSIM"].pct_change().dropna(),
    }


# --- Iter 079 mechanism (signal on underlyings, exec on LETF returns) ------


def compute_monthly_lookback(prices: dict[str, pd.Series],
                              lookback_months: int) -> pd.DataFrame:
    """N-month trailing return per asset, indexed on month-end dates.

    Signal computed on UNDERLYING prices (always SPYSIM, QQQSIM, etc.) so
    the momentum signal is identical across 1×/2×/3× variants — only the
    EXECUTION asset return changes.
    """
    out = {}
    common_idx = None
    for asset in SELECTABLE:
        p = prices[asset]
        # Resample to month-end last business day
        monthly = p.resample("BME").last()
        lb = monthly / monthly.shift(lookback_months) - 1.0
        out[asset] = lb
        common_idx = lb.index if common_idx is None else common_idx.intersection(lb.index)
    df = pd.DataFrame({a: out[a].reindex(common_idx) for a in SELECTABLE})
    return df


def topk_signal(lookback_df: pd.DataFrame, top_k: int = 1,
                abs_threshold: float = 0.0) -> pd.DataFrame:
    """Top-K equal-weight with per-leg AGG routing on negative momentum."""
    out = pd.DataFrame(0.0, index=lookback_df.index, columns=ALL_SLEEVES)
    weight_per_leg = 1.0 / top_k
    for ts, row in lookback_df.iterrows():
        if row.isna().any():
            continue
        sorted_assets = sorted(row.index, key=lambda a: (-row[a], a))
        picks = sorted_assets[:top_k]
        for asset in picks:
            if row[asset] >= abs_threshold:
                out.at[ts, asset] = weight_per_leg
            else:
                out.at[ts, "AGG"] += weight_per_leg
    return out


def compute_topk_returns(daily_returns: dict[str, pd.Series],
                          signal_df: pd.DataFrame,
                          trans_cost_bps: float) -> pd.Series:
    """Apply monthly signal to daily returns with T-1 lag + cost."""
    spy_idx = daily_returns["SPY"].index
    common_idx = spy_idx
    for a in ALL_SLEEVES[1:]:
        common_idx = common_idx.intersection(daily_returns[a].index)
    daily_idx = common_idx

    sig = signal_df.reindex(columns=ALL_SLEEVES, fill_value=0.0)
    rebal_dates = sig.index.sort_values()
    sig_sorted = sig.loc[rebal_dates]

    n_days = len(daily_idx)
    n_sleeves = len(ALL_SLEEVES)
    w_mat = np.zeros((n_days, n_sleeves), dtype=float)
    if len(rebal_dates) > 0:
        rebal_arr = rebal_dates.values
        days_arr = daily_idx.values
        ins = np.searchsorted(rebal_arr, days_arr, side="left")
        rebal_idx = ins - 1
        sig_arr = sig_sorted.values
        valid = rebal_idx >= 0
        w_mat[valid] = sig_arr[rebal_idx[valid]]

    w_prev = np.vstack([np.zeros((1, n_sleeves)), w_mat[:-1]])
    turnover = np.abs(w_mat - w_prev).sum(axis=1)
    cost = turnover * (trans_cost_bps / 10000.0)

    ret_mat = np.column_stack([daily_returns[a].reindex(daily_idx).fillna(0.0).values
                                for a in ALL_SLEEVES])
    gross = (w_mat * ret_mat).sum(axis=1)
    net = gross - cost
    return pd.Series(net, index=daily_idx, name="iter079_topk")


def run_variant(df: pd.DataFrame, prices: dict[str, pd.Series],
                exec_returns: dict[str, pd.Series], label: str) -> pd.Series:
    """Run iter 079 logic with given execution returns dict."""
    lookback = compute_monthly_lookback(prices, LOOKBACK_MONTHS)
    signal = topk_signal(lookback, top_k=1, abs_threshold=0.0)
    return compute_topk_returns(exec_returns, signal, TRANS_COST_BPS).rename(label)


# --- Metrics + gates ---------------------------------------------------------


def metrics(r: pd.Series, name: str = "") -> dict:
    eq = (1.0 + r).cumprod()
    years = len(r) / TRADING_DAYS
    sd = r.std(ddof=1)
    sharpe = float(np.sqrt(TRADING_DAYS) * r.mean() / sd) if sd > 0 else float("nan")
    cagr = float(eq.iloc[-1] ** (1 / years) - 1) if years > 0 else float("nan")
    mdd = float((1 - eq / eq.cummax()).max())
    return {"name": name, "n_bars": len(r), "sharpe": sharpe, "cagr": cagr, "mdd": mdd,
            "start": str(r.index[0].date()), "end": str(r.index[-1].date())}


def bootstrap_sharpe_ci(r: pd.Series, n_boot: int = 5000,
                        ci=(0.0005, 0.9995), seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    n = len(r)
    block = max(1, int(np.sqrt(n)))
    arr = r.values
    out = np.empty(n_boot)
    for i in range(n_boot):
        idx = []
        while len(idx) < n:
            start = rng.integers(0, n)
            length = rng.geometric(1.0 / block)
            idx.extend(range(start, min(start + length, n)))
        idx = np.array(idx[:n])
        sample = arr[idx]
        sd = sample.std(ddof=1)
        out[i] = (np.sqrt(TRADING_DAYS) * sample.mean() / sd) if sd > 0 else 0.0
    low = float(np.quantile(out, ci[0]))
    high = float(np.quantile(out, ci[1]))
    return {"sharpe_low": low, "sharpe_high": high, "passes_g6": low > 0.0,
            "n_boot": n_boot, "block": block}


def deflated_sharpe(r: pd.Series, n_trials: int) -> dict:
    from scipy import stats
    n = len(r)
    sharpe = np.sqrt(TRADING_DAYS) * r.mean() / r.std(ddof=1)
    skew = stats.skew(r.values)
    kurt = stats.kurtosis(r.values, fisher=False)
    emax = ((1 - np.euler_gamma) * stats.norm.ppf(1 - 1.0 / n_trials)
            + np.euler_gamma * stats.norm.ppf(1 - 1.0 / (n_trials * np.e)))
    se_sharpe = np.sqrt((1 - skew * (sharpe / np.sqrt(TRADING_DAYS))
                         + ((kurt - 1) / 4.0) * (sharpe / np.sqrt(TRADING_DAYS)) ** 2)
                        / (n - 1)) * np.sqrt(TRADING_DAYS)
    z = (sharpe - emax * se_sharpe) / se_sharpe if se_sharpe > 0 else 0.0
    p_value = float(1 - stats.norm.cdf(z))
    return {"sharpe": float(sharpe), "p_value": p_value, "n_trials": n_trials,
            "passes_dsr": p_value < 0.05}


# --- Main --------------------------------------------------------------------


def main() -> None:
    df = pd.read_parquet(TF_PATH)
    df.index = pd.to_datetime(df.index)

    # Drop rows where any required column is NaN — start from earliest common date
    required_cols = ["SPYSIM", "QQQSIM", "VEASIM", "ZROZSIM", "GLDSIM", "BNDSIM",
                     "SSOSIM", "QLDSIM", "UGLSIM", "UPROSIM", "TQQQSIM"]
    df_aligned = df[required_cols].dropna()
    print(f"Aligned data: {df_aligned.index.min().date()} → "
          f"{df_aligned.index.max().date()} ({len(df_aligned)} bars)")

    # Underlying prices for signal computation (always 1×)
    prices_underlying = {
        "SPY": df_aligned["SPYSIM"],
        "QQQ": df_aligned["QQQSIM"],
        "EFA": df_aligned["VEASIM"],
        "TLT": df_aligned["ZROZSIM"],
        "GLD": df_aligned["GLDSIM"],
    }

    # Benchmark
    spy_r = df_aligned["SPYSIM"].pct_change().dropna()
    bench = metrics(spy_r, "SPYSIM b&h")
    print(f"\nBenchmark SPYSIM b&h: Sharpe {bench['sharpe']:.3f} | "
          f"CAGR {bench['cagr']*100:.2f}% | MDD {bench['mdd']*100:.2f}%")

    # Run 3 variants
    variants = {
        "iter079_1x_baseline": returns_1x(df_aligned),
        "iter079_2x_LETF_substitute": returns_2x(df_aligned),
        "iter079_3x_LETF_substitute": returns_3x(df_aligned),
    }

    n_trials = len(variants)
    rows = []
    series_dict = {}
    for label, exec_ret in variants.items():
        r = run_variant(df_aligned, prices_underlying, exec_ret, label).dropna()
        m = metrics(r, label)
        boot = bootstrap_sharpe_ci(r)
        dsr = deflated_sharpe(r, n_trials=n_trials)
        rows.append({**m,
                     "sharpe_delta_vs_spy": m["sharpe"] - bench["sharpe"],
                     "cagr_delta_pp_vs_spy": (m["cagr"] - bench["cagr"]) * 100,
                     "mdd_delta_pp_vs_spy": (m["mdd"] - bench["mdd"]) * 100,
                     "g6_bootstrap": boot, "dsr": dsr})
        series_dict[label] = r
        print(f"\n  {label}:")
        print(f"     Sharpe {m['sharpe']:.3f} (Δvs SPY {m['sharpe']-bench['sharpe']:+.3f}) | "
              f"CAGR {m['cagr']*100:.2f}% | MDD {m['mdd']*100:.2f}%")
        print(f"     G6 99.9% Sharpe CI [{boot['sharpe_low']:.3f}, "
              f"{boot['sharpe_high']:.3f}] → {'✅' if boot['passes_g6'] else '❌'}")
        print(f"     DSR p={dsr['p_value']:.4f} → {'✅' if dsr['passes_dsr'] else '❌'}")

    # Save
    out_json = OUT_DIR / "ITER079_LEVERAGED_VALIDATION.json"
    out_json.write_text(json.dumps({
        "benchmark": bench,
        "variants": rows,
        "n_trials": n_trials,
        "lookback_months": LOOKBACK_MONTHS,
        "trans_cost_bps": TRANS_COST_BPS,
        "synth_substitutions": {
            "iter079_2x": {"SPY": "SSOSIM", "QQQ": "QLDSIM", "EFA": "VEASIM (no 2× synth)",
                            "TLT": "2 × ZROZSIM - 0.95%/yr ER", "GLD": "UGLSIM",
                            "AGG_fallback": "BNDSIM (1×)"},
            "iter079_3x": {"SPY": "UPROSIM", "QQQ": "TQQQSIM",
                            "EFA": "VEASIM (no 3× synth)",
                            "TLT": "3 × ZROZSIM - 1.05%/yr ER",
                            "GLD": "GLDSIM (no widely-available 3×)",
                            "AGG_fallback": "BNDSIM (1×)"},
        },
    }, indent=2, default=str))

    pd.DataFrame(series_dict).to_parquet(OUT_DIR / "iter079_leveraged_returns.parquet")

    # Compute 2022 stress
    print("\n=== 2022 stress test ===")
    for label, r in series_dict.items():
        y22 = r.loc["2022-01-01":"2022-12-31"]
        if len(y22) > 0:
            ret_22 = (1 + y22).prod() - 1
            eq_22 = (1 + y22).cumprod()
            mdd_22 = (eq_22 / eq_22.cummax() - 1).min()
            print(f"  {label}: 2022 return {ret_22*100:+.2f}% | MDD {mdd_22*100:.2f}%")

    # Markdown
    out_md = OUT_DIR / "ITER079_LEVERAGED_VALIDATION.md"
    with out_md.open("w") as fh:
        fh.write("# iter 079 leveraged variants — momentum signal × LETF execution\n\n")
        fh.write(f"Generated: {pd.Timestamp.now().isoformat()}\n\n")
        fh.write("**Hipótese do user**: quando iter 079 escolhe SPY (1×) pelo momentum 12m, "
                 "comprar SSO (2×) ou UPRO (3×) no lugar. Mesmo critério pra QQQ→QLD/TQQQ, "
                 "TLT→UBT/TMF, GLD→UGL. EFA e AGG fallback ficam 1× por falta de LETF.\n\n")
        fh.write(f"Sinal de momentum **idêntico** aos 3 variants — computado nos UNDERLYINGS "
                 f"(SPYSIM/QQQSIM/VEASIM/ZROZSIM/GLDSIM). Apenas a EXECUÇÃO muda.\n\n")
        fh.write(f"Window: {df_aligned.index.min().date()} → {df_aligned.index.max().date()} "
                 f"({len(df_aligned)} bars). Lookback {LOOKBACK_MONTHS} meses, "
                 f"trans cost {TRANS_COST_BPS} bps.\n\n")

        fh.write("## Substituições por variant\n\n")
        fh.write("| asset (signal) | iter079_1x | iter079_2x | iter079_3x |\n|---|---|---|---|\n")
        fh.write("| SPY | SPYSIM | **SSOSIM** | **UPROSIM** |\n")
        fh.write("| QQQ | QQQSIM | **QLDSIM** | **TQQQSIM** |\n")
        fh.write("| EFA | VEASIM | VEASIM (no LETF) | VEASIM (no LETF) |\n")
        fh.write("| TLT | ZROZSIM | **2×ZROZ synth** | **3×ZROZ synth** |\n")
        fh.write("| GLD | GLDSIM | **UGLSIM** | GLDSIM (no 3×) |\n")
        fh.write("| AGG fallback | BNDSIM | BNDSIM | BNDSIM |\n\n")

        fh.write(f"## Benchmark\n\n")
        fh.write(f"SPYSIM b&h: Sharpe {bench['sharpe']:.3f} | CAGR {bench['cagr']*100:.2f}% | "
                 f"MDD {bench['mdd']*100:.2f}%\n\n")

        fh.write("## Results (40y synth)\n\n")
        fh.write("| variant | Sharpe (Δvs SPY) | CAGR (Δ) | MDD (Δ) | G6 99.9% CI | DSR p |\n")
        fh.write("|---|---|---|---|---|---|\n")
        for r in rows:
            sh = f"{r['sharpe']:.3f} ({r['sharpe_delta_vs_spy']:+.3f})"
            cg = f"{r['cagr']*100:.2f}% ({r['cagr_delta_pp_vs_spy']:+.2f}pp)"
            md = f"{r['mdd']*100:.2f}% ({r['mdd_delta_pp_vs_spy']:+.2f}pp)"
            g6 = f"[{r['g6_bootstrap']['sharpe_low']:.2f}, {r['g6_bootstrap']['sharpe_high']:.2f}] " \
                 f"{'✅' if r['g6_bootstrap']['passes_g6'] else '❌'}"
            dsr = f"{r['dsr']['p_value']:.4f} {'✅' if r['dsr']['passes_dsr'] else '❌'}"
            fh.write(f"| `{r['name']}` | {sh} | {cg} | {md} | {g6} | {dsr} |\n")

        fh.write("\n## 2022 stress test\n\n")
        fh.write("| variant | retorno 2022 | MDD 2022 |\n|---|---|---|\n")
        for label, r in series_dict.items():
            y22 = r.loc["2022-01-01":"2022-12-31"]
            ret_22 = (1 + y22).prod() - 1 if len(y22) > 0 else 0
            eq_22 = (1 + y22).cumprod()
            mdd_22 = (eq_22 / eq_22.cummax() - 1).min() if len(y22) > 0 else 0
            fh.write(f"| `{label}` | {ret_22*100:+.2f}% | {mdd_22*100:.2f}% |\n")

        fh.write("\n## Caveats\n\n")
        fh.write("1. **TMF/UBT synth = 3×/2× ZROZ** — duration ~25y maior que TLT real ~17y → "
                 "vol drag superestimado. Real performance levemente melhor.\n")
        fh.write("2. **EFA stays 1×** em 2× e 3× — não há LETF EFA-targeted no synth (e mesmo "
                 "no real-world, EFO 2× ProShares tem AUM mínimo). Quando momentum escolhe EFA, "
                 "as 3 variantes performam IDENTICAMENTE nesse mês.\n")
        fh.write("3. **GLD stays 1× em 3× variant** — não há 3× gold widely-available. Quando "
                 "momentum escolhe GLD, iter079_3x performa como iter079_1x nesse mês.\n")
        fh.write("4. **Sinal sempre nos 1× underlyings** — não testamos versão 'sinal nos LETFs', "
                 "que poderia mudar quem ganha o ranking (LETF retorno cumulativo ≠ underlying × "
                 "leverage por causa de daily reset).\n")

    print(f"\nWrote {out_md}")
    print(f"Wrote {out_json}")


if __name__ == "__main__":
    main()
