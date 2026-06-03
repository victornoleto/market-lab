from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import math
import pandas as pd


ROOT = Path(__file__).resolve().parent
REDDIT = ROOT / "us_core"
GLOBAL = ROOT / "global_variant"
OUT_DIR = ROOT / "robustness_tables"
REPORT = ROOT / "ROBUSTNESS_REPORT.md"
TRADING_DAYS = 252


US_BENCH = "100% SPY"
US_CORE = "B4-v2 35/40/25"
US_ORIGINAL = "B4 original 25/25/25/25"

IMPL_BENCH = "100% SPY"
IMPL_VARIANTS = [
    "35/40/25 core",
    "35/20/20/25 MF split",
    "10% RSSX + MF split",
    "17.5% RSSX + MF split",
]

GLOBAL_BENCH = "66/34 VTI/VEA"
GLOBAL_VT = "100% VT"
GLOBAL_CANDIDATES = [
    "Global simple NTSD/RSIT",
    "Global 66/34 lead",
    "Global 60/40 lead",
    "US B4-v2 35/40/25",
]
GLOBAL_VT_CANDIDATES = [GLOBAL_BENCH, *GLOBAL_CANDIDATES]


@dataclass(frozen=True)
class SeriesMetrics:
    start: str
    end: str
    years: float
    cagr: float
    mdd: float
    sharpe: float
    sortino: float
    calmar: float
    terminal: float
    ulcer: float


def read_equity(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    return df.astype(float)


def normalize(frame: pd.DataFrame) -> pd.DataFrame:
    return frame / frame.iloc[0]


def first_on_or_after(index: pd.DatetimeIndex, date: str) -> pd.Timestamp | None:
    eligible = index[index >= pd.Timestamp(date)]
    if len(eligible) == 0:
        return None
    return eligible[0]


def drawdown(equity: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    return equity / equity.cummax() - 1.0


def metrics(equity: pd.Series) -> SeriesMetrics:
    clean = equity.dropna().astype(float)
    clean = clean / clean.iloc[0]
    returns = clean.pct_change().dropna()
    start = clean.index[0]
    end = clean.index[-1]
    years = (end - start).days / 365.25
    dd = drawdown(clean)
    vol = returns.std(ddof=0)
    downside = returns[returns < 0.0].std(ddof=0)
    cagr = clean.iloc[-1] ** (1.0 / years) - 1.0 if years > 0 else math.nan
    mdd = float(dd.min())
    sharpe = float(returns.mean() / vol * math.sqrt(TRADING_DAYS)) if vol and vol > 0 else math.nan
    sortino = float(returns.mean() / downside * math.sqrt(TRADING_DAYS)) if downside and downside > 0 else math.nan
    ulcer = float(((dd * dd).mean()) ** 0.5)
    return SeriesMetrics(
        start=str(start.date()),
        end=str(end.date()),
        years=float(years),
        cagr=float(cagr),
        mdd=mdd,
        sharpe=sharpe,
        sortino=sortino,
        calmar=float(cagr / abs(mdd)) if mdd < 0 else math.nan,
        terminal=float(clean.iloc[-1]),
        ulcer=ulcer,
    )


def fmt_pct(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return "n/a"
    return f"{x * 100:.{digits}f}%"


def fmt_pp(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return "n/a"
    sign = "+" if x >= 0 else ""
    return f"{sign}{x * 100:.{digits}f}pp"


def fmt_num(x: float, digits: int = 3) -> str:
    if pd.isna(x):
        return "n/a"
    return f"{x:.{digits}f}"


def fmt_x(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return "n/a"
    return f"{x:.{digits}f}x"


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._\n"
    header = "| " + " | ".join(columns) + " |"
    sep = "|" + "|".join(["---" for _ in columns]) + "|"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join([header, sep, *body]) + "\n"


def save_table(name: str, rows: list[dict[str, object]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_DIR / f"{name}.csv", index=False)


def report_path(path: Path) -> str:
    return str(path.relative_to(ROOT))


def start_date_table(
    frame: pd.DataFrame,
    benchmark: str,
    candidates: list[str],
    starts: list[str],
    table_name: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for requested_start in starts:
        actual_start = first_on_or_after(frame.index, requested_start)
        if actual_start is None:
            continue
        subset = frame.loc[actual_start:, [benchmark, *candidates]].dropna()
        if len(subset) < TRADING_DAYS:
            continue
        bench_metrics = metrics(subset[benchmark])
        for candidate in candidates:
            candidate_metrics = metrics(subset[candidate])
            rows.append(
                {
                    "requested_start": requested_start,
                    "actual_start": candidate_metrics.start,
                    "end": candidate_metrics.end,
                    "years": round(candidate_metrics.years, 2),
                    "portfolio": candidate,
                    "benchmark": benchmark,
                    "portfolio_cagr": candidate_metrics.cagr,
                    "benchmark_cagr": bench_metrics.cagr,
                    "cagr_spread": candidate_metrics.cagr - bench_metrics.cagr,
                    "portfolio_mdd": candidate_metrics.mdd,
                    "benchmark_mdd": bench_metrics.mdd,
                    "portfolio_terminal": candidate_metrics.terminal,
                    "benchmark_terminal": bench_metrics.terminal,
                    "terminal_vs_benchmark": candidate_metrics.terminal / bench_metrics.terminal,
                    "portfolio_calmar": candidate_metrics.calmar,
                    "benchmark_calmar": bench_metrics.calmar,
                }
            )
    save_table(table_name, rows)
    return rows


def formatted_start_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        out.append(
            {
                "Start": row["actual_start"],
                "Years": row["years"],
                "Portfolio": row["portfolio"],
                "CAGR": fmt_pct(float(row["portfolio_cagr"])),
                "Bench CAGR": fmt_pct(float(row["benchmark_cagr"])),
                "Spread": fmt_pp(float(row["cagr_spread"])),
                "MDD": fmt_pct(float(row["portfolio_mdd"])),
                "Bench MDD": fmt_pct(float(row["benchmark_mdd"])),
                "Terminal": fmt_x(float(row["portfolio_terminal"])),
                "Terminal/Bench": fmt_x(float(row["terminal_vs_benchmark"])),
                "Calmar": fmt_num(float(row["portfolio_calmar"]), 3),
            }
        )
    return out


def rolling_summary(
    frame: pd.DataFrame,
    benchmark: str,
    candidates: list[str],
    horizons: list[int],
    table_name: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    aligned = frame[[benchmark, *candidates]].dropna()
    for years in horizons:
        periods = years * TRADING_DAYS
        bench_window = aligned[benchmark] / aligned[benchmark].shift(periods)
        bench_cagr = bench_window ** (1.0 / years) - 1.0
        for candidate in candidates:
            cand_window = aligned[candidate] / aligned[candidate].shift(periods)
            rel = cand_window / bench_window - 1.0
            spread = (cand_window ** (1.0 / years) - 1.0) - bench_cagr
            valid_rel = rel.dropna()
            valid_spread = spread.dropna()
            if valid_rel.empty:
                continue
            rows.append(
                {
                    "horizon_years": years,
                    "portfolio": candidate,
                    "benchmark": benchmark,
                    "n_windows": int(len(valid_rel)),
                    "hit_rate_rel_wealth_gt_0": float((valid_rel > 0).mean()),
                    "rel_wealth_min": float(valid_rel.min()),
                    "rel_wealth_p10": float(valid_rel.quantile(0.10)),
                    "rel_wealth_median": float(valid_rel.quantile(0.50)),
                    "rel_wealth_p90": float(valid_rel.quantile(0.90)),
                    "rel_wealth_latest": float(valid_rel.iloc[-1]),
                    "cagr_spread_p10": float(valid_spread.quantile(0.10)),
                    "cagr_spread_median": float(valid_spread.quantile(0.50)),
                    "cagr_spread_latest": float(valid_spread.iloc[-1]),
                }
            )
    save_table(table_name, rows)
    return rows


def formatted_rolling_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        out.append(
            {
                "Horizon": f"{row['horizon_years']}y",
                "Portfolio": row["portfolio"],
                "Windows": row["n_windows"],
                "Hit rate": fmt_pct(float(row["hit_rate_rel_wealth_gt_0"])),
                "Rel min": fmt_pct(float(row["rel_wealth_min"])),
                "Rel p10": fmt_pct(float(row["rel_wealth_p10"])),
                "Rel median": fmt_pct(float(row["rel_wealth_median"])),
                "Rel latest": fmt_pct(float(row["rel_wealth_latest"])),
                "CAGR spread p10": fmt_pp(float(row["cagr_spread_p10"])),
                "CAGR spread median": fmt_pp(float(row["cagr_spread_median"])),
                "CAGR spread latest": fmt_pp(float(row["cagr_spread_latest"])),
            }
        )
    return out


def relative_underperformance(
    frame: pd.DataFrame,
    benchmark: str,
    candidates: list[str],
    table_name: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    aligned = normalize(frame[[benchmark, *candidates]].dropna())
    for candidate in candidates:
        ratio = aligned[candidate] / aligned[benchmark]
        below = ratio < 1.0
        longest = 0
        current = 0
        for flag in below.to_numpy():
            if flag:
                current += 1
                longest = max(longest, current)
            else:
                current = 0
        rel_dd = ratio / ratio.cummax() - 1.0
        rows.append(
            {
                "portfolio": candidate,
                "benchmark": benchmark,
                "start": str(aligned.index[0].date()),
                "end": str(aligned.index[-1].date()),
                "pct_days_below_benchmark": float(below.mean()),
                "longest_below_benchmark_days": int(longest),
                "max_deficit_vs_benchmark": float(ratio.min() - 1.0),
                "latest_relative_wealth": float(ratio.iloc[-1] - 1.0),
                "max_relative_drawdown": float(rel_dd.min()),
            }
        )
    save_table(table_name, rows)
    return rows


def formatted_under_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        out.append(
            {
                "Portfolio": row["portfolio"],
                "Days below bench": fmt_pct(float(row["pct_days_below_benchmark"])),
                "Longest below": row["longest_below_benchmark_days"],
                "Max deficit": fmt_pct(float(row["max_deficit_vs_benchmark"])),
                "Latest rel wealth": fmt_pct(float(row["latest_relative_wealth"])),
                "Max rel DD": fmt_pct(float(row["max_relative_drawdown"])),
            }
        )
    return out


def apply_drag(equity: pd.Series, annual_drag_bps: float) -> pd.Series:
    clean = equity.dropna().astype(float)
    returns = clean.pct_change().fillna(0.0)
    daily_drag = annual_drag_bps / 10_000.0 / TRADING_DAYS
    stressed_returns = (1.0 + returns) * (1.0 - daily_drag) - 1.0
    return (1.0 + stressed_returns).cumprod()


def fee_drag_stress(
    frame: pd.DataFrame,
    benchmark: str,
    candidates: list[str],
    drags_bps: list[int],
    table_name: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    aligned = frame[[benchmark, *candidates]].dropna()
    bench_metrics = metrics(aligned[benchmark])
    for candidate in candidates:
        for drag in drags_bps:
            stressed = apply_drag(aligned[candidate], drag)
            m = metrics(stressed)
            rows.append(
                {
                    "portfolio": candidate,
                    "benchmark": benchmark,
                    "extra_drag_bps_per_year": drag,
                    "portfolio_cagr": m.cagr,
                    "benchmark_cagr": bench_metrics.cagr,
                    "cagr_spread": m.cagr - bench_metrics.cagr,
                    "portfolio_mdd": m.mdd,
                    "terminal_vs_benchmark": m.terminal / bench_metrics.terminal,
                    "portfolio_calmar": m.calmar,
                }
            )
    save_table(table_name, rows)
    return rows


def formatted_drag_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        out.append(
            {
                "Portfolio": row["portfolio"],
                "Extra drag": f"{row['extra_drag_bps_per_year']} bps/yr",
                "CAGR": fmt_pct(float(row["portfolio_cagr"])),
                "Bench CAGR": fmt_pct(float(row["benchmark_cagr"])),
                "Spread": fmt_pp(float(row["cagr_spread"])),
                "MDD": fmt_pct(float(row["portfolio_mdd"])),
                "Terminal/Bench": fmt_x(float(row["terminal_vs_benchmark"])),
                "Calmar": fmt_num(float(row["portfolio_calmar"]), 3),
            }
        )
    return out


def regime_stress(
    frame: pd.DataFrame,
    benchmark: str,
    candidates: list[str],
    regimes: dict[str, tuple[str, str]],
    table_name: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for regime, (start, end) in regimes.items():
        actual_start = first_on_or_after(frame.index, start)
        if actual_start is None:
            continue
        subset = frame.loc[actual_start : pd.Timestamp(end), [benchmark, *candidates]].dropna()
        if len(subset) < 5:
            continue
        norm = normalize(subset)
        bench_total = norm[benchmark].iloc[-1] - 1.0
        bench_mdd = float(drawdown(norm[benchmark]).min())
        for candidate in candidates:
            cand_total = norm[candidate].iloc[-1] - 1.0
            cand_mdd = float(drawdown(norm[candidate]).min())
            rows.append(
                {
                    "regime": regime,
                    "start": str(norm.index[0].date()),
                    "end": str(norm.index[-1].date()),
                    "portfolio": candidate,
                    "benchmark": benchmark,
                    "portfolio_total_return": float(cand_total),
                    "benchmark_total_return": float(bench_total),
                    "return_spread": float(cand_total - bench_total),
                    "portfolio_mdd": cand_mdd,
                    "benchmark_mdd": bench_mdd,
                }
            )
    save_table(table_name, rows)
    return rows


def formatted_regime_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        out.append(
            {
                "Regime": row["regime"],
                "Window": f"{row['start']}..{row['end']}",
                "Portfolio": row["portfolio"],
                "Return": fmt_pct(float(row["portfolio_total_return"])),
                "Bench return": fmt_pct(float(row["benchmark_total_return"])),
                "Spread": fmt_pp(float(row["return_spread"])),
                "MDD": fmt_pct(float(row["portfolio_mdd"])),
                "Bench MDD": fmt_pct(float(row["benchmark_mdd"])),
            }
        )
    return out


def load_mc_table(path: Path, table_name: str) -> list[dict[str, object]]:
    df = pd.read_csv(path)
    rows = df.to_dict(orient="records")
    save_table(table_name, rows)
    return rows


def formatted_mc_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        prob = float(row["prob_terminal_under_benchmark"])
        out.append(
            {
                "Portfolio": row["portfolio"],
                "Paths": int(row["n_paths"]),
                "Years": int(row["years"]),
                "Terminal p10": fmt_x(float(row["terminal_p10"])),
                "Terminal median": fmt_x(float(row["terminal_median"])),
                "Terminal p90": fmt_x(float(row["terminal_p90"])),
                "CAGR p10": fmt_pct(float(row["cagr_p10"])),
                "CAGR median": fmt_pct(float(row["cagr_median"])),
                "MDD median": fmt_pct(float(row["mdd_median"])),
                "Prob < bench": "n/a" if prob == 0.0 and row["portfolio"] in {US_BENCH, GLOBAL_BENCH} else fmt_pct(prob, 1),
            }
        )
    return out


SECTION_NOTES = {
    "US 35/40/25 Start-Date Sensitivity": (
        "Analysis: The no-margin `35/40/25` core is clearly stronger than the original B4 over the full sample and across most start dates. The important caveat is that the post-2010 edge versus SPY is much narrower, including one 2013 start where CAGR trails SPY by `0.44pp`, while drawdown remains materially better.\n\n"
        "Conclusion: Keep `35/40/25` as the clean US anchor, but present it as a drawdown-efficient SPY challenger rather than a guaranteed CAGR beater in every modern start window."
    ),
    "US Implementation Variant Start-Date Sensitivity": (
        "Analysis: The implementation variants improve the 2010 inception cohort, especially the `RSSX` versions, but their advantage is not uniform. The same variants lose momentum in later starts such as 2020 and 2022, where higher RSSX weight increases drawdown and can trail SPY on CAGR.\n\n"
        "Conclusion: Treat `CTAP` and `RSSX` as optional implementation enhancements, not as a replacement for the simpler `35/40/25` core. The `RSSX` rows need stronger assumption disclosure because they are more path and BTC-proxy sensitive."
    ),
    "Global Variant Start-Date Sensitivity vs 66/34 VTI/VEA": (
        "Analysis: The global variants beat `66/34 VTI/VEA` over long histories and reduce drawdowns substantially, but the advantage compresses after 2010. RSC-US remains the highest-return row in nearly every start window, so global diversification is buying smoother geographic exposure at the cost of absolute return.\n\n"
        "Conclusion: The global set is a defensible diversification sleeve, not the lead portfolio. Use `66/34 VTI/VEA` as the primary global balanced benchmark because it is tougher than `100% VT` in several modern windows."
    ),
    "Global Variant Start-Date Sensitivity vs 100% VT": (
        "Analysis: Against `100% VT`, the global variants look much stronger because VT suffered deeper full-history drawdowns and lower long-run CAGR. Even so, the recent windows show a more nuanced result: `Global 60/40 lead` can trail VT on CAGR, while `Global simple NTSD/RSIT` and `Global 66/34 lead` mostly preserve drawdown advantages.\n\n"
        "Conclusion: `100% VT` is useful as a public baseline, but it is not sufficient alone. The stronger conclusion comes from surviving both VT and the tougher `66/34 VTI/VEA` comparison."
    ),
    "US Rolling Relative Wealth Summary": (
        "Analysis: Rolling windows show the core trade-off better than the full-period CAGR. `35/40/25` wins most 5y, 10y and 15y windows and has positive 15y p10 relative wealth, but short 3y and some 10y windows still underperform SPY.\n\n"
        "Conclusion: The edge is long-horizon and patience-dependent. It should not be marketed as a short-horizon SPY replacement."
    ),
    "US Implementation Rolling Relative Wealth Summary": (
        "Analysis: The implementation rows are less stable than the full-period table implies. RSSX-heavy variants improve median and hit-rate statistics over 10y windows, but their latest rolling windows are negative versus SPY, which matters for current investor expectations.\n\n"
        "Conclusion: The implementation variants are promising but not clean enough to become the headline. They belong in an implementation appendix or optional variant discussion."
    ),
    "Global Rolling Relative Wealth Summary vs 66/34": (
        "Analysis: Global variants have strong long-horizon hit rates versus `66/34`, especially at 10y and 15y, but recent relative wealth is weak for the global-only rows. RSC-US remains the strongest rolling performer, including a 100% 15y hit rate in this table.\n\n"
        "Conclusion: Global diversification improves robustness optics, but the current cycle has penalized non-US exposure. The report should frame global as diversification insurance, not as recent-performance leadership."
    ),
    "Global Rolling Relative Wealth Summary vs 100% VT": (
        "Analysis: The same global variants look more favorable versus VT, with very high 10y and 15y hit rates. However, recent 3y, 5y and 10y relative wealth is still negative for the global-only rows, so the benchmark choice changes the apparent strength of the result.\n\n"
        "Conclusion: VT confirms the long-horizon diversification case, while `66/34` keeps the conclusion honest. Both benchmarks should remain in the report."
    ),
    "US Relative Underperformance Episodes": (
        "Analysis: Full-history underperformance episodes are short and rare for both B4 rows. The core spends only `2.60%` of days below SPY and has a latest relative wealth of `+325.96%`, which is a strong robustness point.\n\n"
        "Conclusion: The US core has strong long-run relative persistence, but the max relative drawdown around `-33%` means investors still need tolerance for multi-year relative pain."
    ),
    "US Implementation Relative Underperformance Episodes": (
        "Analysis: Since the implementation table starts in 2010, the simple core spends much more time below SPY, while RSSX variants dramatically reduce days below benchmark. This is the main empirical argument for RSSX, but it is also tied to the specific proxy and period.\n\n"
        "Conclusion: RSSX improves this relative-underperformance diagnostic, but that improvement should be treated as provisional until the BTC/RSSX assumptions are independently stress-tested."
    ),
    "Global Relative Underperformance Episodes vs 66/34": (
        "Analysis: The global variants spend only about `3%` of days below `66/34`, but their max relative drawdowns remain meaningful. RSC-US has the highest latest relative wealth, while global rows trade some upside for geographic diversification.\n\n"
        "Conclusion: Relative persistence is acceptable for all global candidates, with the strongest practical case for the variants that reduce drawdown without giving up too much terminal wealth."
    ),
    "Global Relative Underperformance Episodes vs 100% VT": (
        "Analysis: Versus VT, all B4-style variants show very large latest relative wealth, but the max relative drawdown is still non-trivial. `66/34 VTI/VEA` itself also beats VT over the sample, which shows that VT is a soft benchmark for this design.\n\n"
        "Conclusion: The VT comparison is useful for public communication, but the investment-quality conclusion should lean more on the `66/34` benchmark."
    ),
    "US Fee/Drag Stress": (
        "Analysis: The US core remains ahead of SPY even after `150 bps/yr` of extra drag, though the terminal advantage compresses materially. This means the full-history result is not purely an artifact of zero-friction assumptions.\n\n"
        "Conclusion: Fee/drag resilience is good for the US core, but realistic implementation costs still matter and should be explicitly modeled before any future mandate discussion."
    ),
    "US Implementation Fee/Drag Stress": (
        "Analysis: Post-2010 implementation variants have much less fee headroom than the full-history US core. The simple core loses its SPY spread with only `25 bps/yr` extra drag, while RSSX variants keep a positive spread longer but take higher drawdown.\n\n"
        "Conclusion: Implementation details can erase the modern edge. If this ever moves beyond research, expense ratios, trading costs and tax drag must be modeled as first-class assumptions."
    ),
    "Global Fee/Drag Stress vs 66/34": (
        "Analysis: Global variants remain ahead of `66/34` under the tested drag levels, but the margin narrows as expected. `Global 66/34 lead` has the cleanest drawdown profile among global variants, while `Global simple NTSD/RSIT` keeps slightly higher return with deeper drawdown.\n\n"
        "Conclusion: The global variants have acceptable drag tolerance versus `66/34`, but the best choice depends on whether the objective is return or drawdown control."
    ),
    "Global Fee/Drag Stress vs 100% VT": (
        "Analysis: Against VT, every global variant keeps a positive spread even at `150 bps/yr` extra drag. This confirms that the global B4-style construction is not fragile versus a broad global equity baseline.\n\n"
        "Conclusion: VT drag stress is supportive but not decisive. The tougher `66/34` drag test should remain the primary implementation hurdle."
    ),
    "US Named-Regime Stress": (
        "Analysis: The US core improves materially over SPY in the dot-com bust, GFC, Covid crash and 2022 rates shock. The weak spot is the recent recovery, where SPY rebounds harder and the core trails by `3.18pp`.\n\n"
        "Conclusion: The core is a crisis-dampening design, not a maximum-beta recovery vehicle. That is consistent with the role of managed futures, gold and long-duration exposure."
    ),
    "US Implementation Named-Regime Stress": (
        "Analysis: Implementation variants also reduce crash-period losses versus SPY, but each additional sleeve split or RSSX allocation worsens the Covid and 2022 drawdowns relative to the simple core. In the recent recovery, all variants trail SPY, with RSSX-heavy rows trailing most.\n\n"
        "Conclusion: The implementation variants add complexity and return potential, but the simple core has the cleaner regime profile."
    ),
    "Global Named-Regime Stress vs 66/34": (
        "Analysis: Global variants improve outcomes across the large stress regimes versus `66/34`, especially GFC and Covid. The cost appears in the recent recovery, where global rows lag the benchmark by large margins.\n\n"
        "Conclusion: The global designs are defensive and diversifying, but they can lag badly when US/global equities rebound strongly. That trade-off must be explicit."
    ),
    "Global Named-Regime Stress vs 100% VT": (
        "Analysis: The same regime pattern holds versus VT: strong crisis protection, weaker recent recovery capture. `Global 66/34 lead` and `Global 60/40 lead` show the cleanest crisis drawdowns, while RSC-US keeps better recovery participation.\n\n"
        "Conclusion: Global variants are best framed as drawdown-control portfolios. If the user wants maximum recovery capture, the US core remains superior."
    ),
    "US Monte Carlo Sequence-Risk Summary": (
        "Analysis: The 20-year block Monte Carlo shows much stronger p10 and median terminal wealth for RSC-US than SPY, with lower median max drawdown. The probability of terminal wealth below SPY is `6.2%` for the core, which is low but not zero.\n\n"
        "Conclusion: Sequence-risk evidence supports the US core, but it is a diagnostic simulation, not formal proof of future superiority."
    ),
    "Global Monte Carlo Sequence-Risk Summary": (
        "Analysis: Global variants also improve p10 terminal wealth and median drawdown versus `66/34`, but underperformance probabilities are higher than the US core. RSC-US remains the strongest Monte Carlo candidate in this table.\n\n"
        "Conclusion: Global Monte Carlo results support diversification, not replacement. The global rows are viable if drawdown smoothing and geographic breadth are worth lower expected terminal wealth."
    ),
}


def rows_to_section(title: str, rows: list[dict[str, object]], columns: list[str]) -> str:
    note = SECTION_NOTES.get(title, "")
    note_block = f"{note}\n\n" if note else ""
    return f"## {title}\n\n" + note_block + md_table(rows, columns) + "\n"


def generate() -> None:
    full = read_equity(REDDIT / "series" / "full_equity_curves.csv")
    impl = read_equity(REDDIT / "series" / "implementation_equity_curves.csv")
    glob = read_equity(GLOBAL / "series" / "global_selected_equity.csv")

    us_starts = ["1988-01-04", "1994-01-03", "2000-01-03", "2003-01-02", "2008-01-02", "2010-01-04", "2010-10-18", "2013-01-02", "2020-01-02"]
    impl_starts = ["2010-10-18", "2013-01-02", "2016-01-04", "2020-01-02", "2022-01-03"]
    global_starts = us_starts
    horizons = [3, 5, 10, 15]
    regimes = {
        "Dot-com bust": ("2000-03-24", "2002-10-09"),
        "GFC": ("2007-10-09", "2009-03-09"),
        "Covid crash": ("2020-02-19", "2020-03-23"),
        "Inflation/rates shock": ("2022-01-03", "2022-10-14"),
        "Recent recovery": ("2022-10-14", "2026-05-21"),
    }

    us_start = start_date_table(full, US_BENCH, [US_CORE, US_ORIGINAL], us_starts, "us_start_date_sensitivity")
    impl_start = start_date_table(impl, IMPL_BENCH, IMPL_VARIANTS, impl_starts, "implementation_start_date_sensitivity")
    global_start = start_date_table(glob, GLOBAL_BENCH, GLOBAL_CANDIDATES, global_starts, "global_start_date_sensitivity")
    global_vt_start = start_date_table(glob, GLOBAL_VT, GLOBAL_VT_CANDIDATES, global_starts, "global_vt_start_date_sensitivity")

    us_roll = rolling_summary(full, US_BENCH, [US_CORE, US_ORIGINAL], horizons, "us_rolling_summary")
    impl_roll = rolling_summary(impl, IMPL_BENCH, IMPL_VARIANTS, [3, 5, 10], "implementation_rolling_summary")
    global_roll = rolling_summary(glob, GLOBAL_BENCH, GLOBAL_CANDIDATES, horizons, "global_rolling_summary")
    global_vt_roll = rolling_summary(glob, GLOBAL_VT, GLOBAL_VT_CANDIDATES, horizons, "global_vt_rolling_summary")

    us_under = relative_underperformance(full, US_BENCH, [US_CORE, US_ORIGINAL], "us_underperformance_episodes")
    impl_under = relative_underperformance(impl, IMPL_BENCH, IMPL_VARIANTS, "implementation_underperformance_episodes")
    global_under = relative_underperformance(glob, GLOBAL_BENCH, GLOBAL_CANDIDATES, "global_underperformance_episodes")
    global_vt_under = relative_underperformance(glob, GLOBAL_VT, GLOBAL_VT_CANDIDATES, "global_vt_underperformance_episodes")

    us_drag = fee_drag_stress(full, US_BENCH, [US_CORE, US_ORIGINAL], [0, 25, 50, 100, 150], "us_fee_drag_stress")
    impl_drag = fee_drag_stress(impl, IMPL_BENCH, IMPL_VARIANTS, [0, 25, 50, 100, 150], "implementation_fee_drag_stress")
    global_drag = fee_drag_stress(glob, GLOBAL_BENCH, GLOBAL_CANDIDATES, [0, 25, 50, 100, 150], "global_fee_drag_stress")
    global_vt_drag = fee_drag_stress(glob, GLOBAL_VT, GLOBAL_VT_CANDIDATES, [0, 25, 50, 100, 150], "global_vt_fee_drag_stress")

    us_regime = regime_stress(full, US_BENCH, [US_CORE, US_ORIGINAL], regimes, "us_regime_stress")
    impl_regime = regime_stress(impl, IMPL_BENCH, IMPL_VARIANTS, regimes, "implementation_regime_stress")
    global_regime = regime_stress(glob, GLOBAL_BENCH, GLOBAL_CANDIDATES, regimes, "global_regime_stress")
    global_vt_regime = regime_stress(glob, GLOBAL_VT, GLOBAL_VT_CANDIDATES, regimes, "global_vt_regime_stress")

    us_mc = load_mc_table(REDDIT / "monte_carlo_sequence_risk.csv", "us_monte_carlo_sequence_risk")
    global_mc = load_mc_table(GLOBAL / "global_monte_carlo_sequence_risk.csv", "global_monte_carlo_sequence_risk")

    sections: list[str] = []
    sections.append(
        "# Return-Stacked Core Robustness Execution Report\n\n"
        "Status: research-only robustness execution. This report does not authorize deployment, paper trading, or mandate change. The goal is to stress the RSC-US and RSC-Global variants after the publication-draft work.\n\n"
        "Method references: start-date sensitivity, rolling-window checks, parameter/implementation stress and sequence-risk tests are used as robustness diagnostics rather than promotion gates `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`. Stacked ETF leverage and risk-parity interpretation follow `[leverage_for_the_long_run, p.13]`, `[risk_parity, p.80-81]`.\n\n"
        "## Source Data And Scope\n\n"
        "Analysis: This report is built from saved portfolio equity curves and Monte Carlo summaries, so the displayed tables are reproducible from the RSC artifacts without re-running the original portfolio search. The trade-off is that sleeve-level attribution is limited where only final equity curves are available.\n\n"
        "Conclusion: Use this report as an audit and communication layer over the existing RSC outputs. Do not infer exact rebalance-frequency, sleeve-removal or threshold-band behavior from these portfolio-level curves alone.\n\n"
        "| Item | Detail |\n|---|---|\n"
        f"| US full curves | `{report_path(REDDIT / 'series' / 'full_equity_curves.csv')}` |\n"
        f"| US implementation curves | `{report_path(REDDIT / 'series' / 'implementation_equity_curves.csv')}` |\n"
        f"| Global selected curves | `{report_path(GLOBAL / 'series' / 'global_selected_equity.csv')}` |\n"
        f"| Monte Carlo summaries | `{report_path(REDDIT / 'monte_carlo_sequence_risk.csv')}`, `{report_path(GLOBAL / 'global_monte_carlo_sequence_risk.csv')}` |\n"
        f"| CSV audit tables | `{report_path(OUT_DIR)}/` |\n\n"
        "Executed analyses: start-date sensitivity, rolling relative wealth/CAGR spread, relative-underperformance episodes, fee/drag stress, named-regime stress and Monte Carlo sequence-risk summaries. Global sections are benchmarked against both `66/34 VTI/VEA` and `100% VT`.\n\n"
        "Not executed exactly: rebalance-frequency and remove-one-sleeve tests require sleeve-level daily return series for `RSSTSIM`, `ZROZSIM`, `CTAPSIM`, `RSSX_RP`, `NTSD`, `RSIT`, etc. The RSC folder currently preserves portfolio equity curves and limited remote price proxies, so exact rebalance/remove-one attribution would be under-specified. This is documented as a data blocker rather than approximated.\n"
    )

    sections.append(
        "## Executive Read\n\n"
        "- US `35/40/25` remains the clean anchor: strong full-history edge versus SPY, and post-2010 results are closer to SPY on CAGR but materially better on drawdown.\n"
        "- Implementation variants with `CTAP`/`RSSX` improve post-2010 terminal wealth in the existing proxy table, but the RSSX rows remain BTC-assumption-sensitive and should stay optional.\n"
        "- Global variants improve drawdown versus `66/34 VTI/VEA` and `VT`, but they give up return versus RSC-US. Treat global as a diversification variant, not a replacement.\n"
        "- Extra drag stress is important: the strategy survives moderate incremental drag, but high extra drag compresses the edge, especially for global variants.\n"
        "- Sequence-risk Monte Carlo supports the same qualitative conclusion: RSC variants show better downside terminal wealth than benchmarks, but this is not a formal validation gate.\n"
    )

    sections.append(rows_to_section("US 35/40/25 Start-Date Sensitivity", formatted_start_rows(us_start), ["Start", "Years", "Portfolio", "CAGR", "Bench CAGR", "Spread", "MDD", "Bench MDD", "Terminal", "Terminal/Bench", "Calmar"]))
    sections.append(rows_to_section("US Implementation Variant Start-Date Sensitivity", formatted_start_rows(impl_start), ["Start", "Years", "Portfolio", "CAGR", "Bench CAGR", "Spread", "MDD", "Bench MDD", "Terminal", "Terminal/Bench", "Calmar"]))
    sections.append(rows_to_section("Global Variant Start-Date Sensitivity vs 66/34 VTI/VEA", formatted_start_rows(global_start), ["Start", "Years", "Portfolio", "CAGR", "Bench CAGR", "Spread", "MDD", "Bench MDD", "Terminal", "Terminal/Bench", "Calmar"]))
    sections.append(rows_to_section("Global Variant Start-Date Sensitivity vs 100% VT", formatted_start_rows(global_vt_start), ["Start", "Years", "Portfolio", "CAGR", "Bench CAGR", "Spread", "MDD", "Bench MDD", "Terminal", "Terminal/Bench", "Calmar"]))

    sections.append(rows_to_section("US Rolling Relative Wealth Summary", formatted_rolling_rows(us_roll), ["Horizon", "Portfolio", "Windows", "Hit rate", "Rel min", "Rel p10", "Rel median", "Rel latest", "CAGR spread p10", "CAGR spread median", "CAGR spread latest"]))
    sections.append(rows_to_section("US Implementation Rolling Relative Wealth Summary", formatted_rolling_rows(impl_roll), ["Horizon", "Portfolio", "Windows", "Hit rate", "Rel min", "Rel p10", "Rel median", "Rel latest", "CAGR spread p10", "CAGR spread median", "CAGR spread latest"]))
    sections.append(rows_to_section("Global Rolling Relative Wealth Summary vs 66/34", formatted_rolling_rows(global_roll), ["Horizon", "Portfolio", "Windows", "Hit rate", "Rel min", "Rel p10", "Rel median", "Rel latest", "CAGR spread p10", "CAGR spread median", "CAGR spread latest"]))
    sections.append(rows_to_section("Global Rolling Relative Wealth Summary vs 100% VT", formatted_rolling_rows(global_vt_roll), ["Horizon", "Portfolio", "Windows", "Hit rate", "Rel min", "Rel p10", "Rel median", "Rel latest", "CAGR spread p10", "CAGR spread median", "CAGR spread latest"]))

    sections.append(rows_to_section("US Relative Underperformance Episodes", formatted_under_rows(us_under), ["Portfolio", "Days below bench", "Longest below", "Max deficit", "Latest rel wealth", "Max rel DD"]))
    sections.append(rows_to_section("US Implementation Relative Underperformance Episodes", formatted_under_rows(impl_under), ["Portfolio", "Days below bench", "Longest below", "Max deficit", "Latest rel wealth", "Max rel DD"]))
    sections.append(rows_to_section("Global Relative Underperformance Episodes vs 66/34", formatted_under_rows(global_under), ["Portfolio", "Days below bench", "Longest below", "Max deficit", "Latest rel wealth", "Max rel DD"]))
    sections.append(rows_to_section("Global Relative Underperformance Episodes vs 100% VT", formatted_under_rows(global_vt_under), ["Portfolio", "Days below bench", "Longest below", "Max deficit", "Latest rel wealth", "Max rel DD"]))

    sections.append(rows_to_section("US Fee/Drag Stress", formatted_drag_rows(us_drag), ["Portfolio", "Extra drag", "CAGR", "Bench CAGR", "Spread", "MDD", "Terminal/Bench", "Calmar"]))
    sections.append(rows_to_section("US Implementation Fee/Drag Stress", formatted_drag_rows(impl_drag), ["Portfolio", "Extra drag", "CAGR", "Bench CAGR", "Spread", "MDD", "Terminal/Bench", "Calmar"]))
    sections.append(rows_to_section("Global Fee/Drag Stress vs 66/34", formatted_drag_rows(global_drag), ["Portfolio", "Extra drag", "CAGR", "Bench CAGR", "Spread", "MDD", "Terminal/Bench", "Calmar"]))
    sections.append(rows_to_section("Global Fee/Drag Stress vs 100% VT", formatted_drag_rows(global_vt_drag), ["Portfolio", "Extra drag", "CAGR", "Bench CAGR", "Spread", "MDD", "Terminal/Bench", "Calmar"]))

    sections.append(rows_to_section("US Named-Regime Stress", formatted_regime_rows(us_regime), ["Regime", "Window", "Portfolio", "Return", "Bench return", "Spread", "MDD", "Bench MDD"]))
    sections.append(rows_to_section("US Implementation Named-Regime Stress", formatted_regime_rows(impl_regime), ["Regime", "Window", "Portfolio", "Return", "Bench return", "Spread", "MDD", "Bench MDD"]))
    sections.append(rows_to_section("Global Named-Regime Stress vs 66/34", formatted_regime_rows(global_regime), ["Regime", "Window", "Portfolio", "Return", "Bench return", "Spread", "MDD", "Bench MDD"]))
    sections.append(rows_to_section("Global Named-Regime Stress vs 100% VT", formatted_regime_rows(global_vt_regime), ["Regime", "Window", "Portfolio", "Return", "Bench return", "Spread", "MDD", "Bench MDD"]))

    sections.append(rows_to_section("US Monte Carlo Sequence-Risk Summary", formatted_mc_rows(us_mc), ["Portfolio", "Paths", "Years", "Terminal p10", "Terminal median", "Terminal p90", "CAGR p10", "CAGR median", "MDD median", "Prob < bench"]))
    sections.append(rows_to_section("Global Monte Carlo Sequence-Risk Summary", formatted_mc_rows(global_mc), ["Portfolio", "Paths", "Years", "Terminal p10", "Terminal median", "Terminal p90", "CAGR p10", "CAGR median", "MDD median", "Prob < bench"]))

    sections.append(
        "## Data Blockers And Next Execution Step\n\n"
        "Analysis: The blocked checks are not failed robustness tests; they are data-granularity limitations. Exact rebalance frequency, remove-one-sleeve and threshold-band analysis require daily constituent or sleeve return series, not just completed portfolio equity curves.\n\n"
        "Conclusion: The next useful engineering artifact is a canonical sleeve-return matrix. Once that exists, this report can be rerun with exact implementation sensitivity instead of approximations.\n\n"
        "| Check | Status | Reason | Required artifact |\n|---|---|---|---|\n"
        "| Rebalance frequency: monthly vs quarterly/semiannual/annual | Blocked | Current RSC exports store portfolio equity curves, not all underlying sleeve daily returns for each implementation variant. | Aligned daily return matrix for `GDE`, `RSST`, `ZROZ`, `CTAP`, `RSSX_RP`, `NTSD`, `RSIT`, `NTSI`, `VTI/VEA/VT`. |\n"
        "| Remove-one-sleeve test | Blocked | Cannot recompute portfolio without a sleeve from only final equity curves. | Same aligned sleeve return matrix plus rebalance engine. |\n"
        "| Exact rebalance threshold/tolerance bands | Blocked | Requires constituent-level drift and rebalance logic. | Same aligned sleeve return matrix plus weight-drift simulator. |\n\n"
        "Recommended next step: export a canonical `return_stacked_core_sleeve_returns.parquet` with all sleeves used in US and global variants, then rerun this report with exact rebalance and remove-one sections.\n"
    )

    REPORT.write_text("\n".join(sections), encoding="utf-8")


if __name__ == "__main__":
    generate()
