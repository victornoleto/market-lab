"""Plot top-K phase-1 winners vs phase-0 baseline + B&H benchmarks.

Reads ``sweep_top20.csv`` to find the K best configs per (on_leg) in the
``br_lei_14754`` (taxed) scenario, re-simulates each, and overlays them
against:

* B&H SPY (universal benchmark)
* B&H SSO and B&H UPRO (LETF references)
* Phase-0 LRS-SSO and LRS-UPRO using ``SMA200/CASH`` (the canonical
  Gayed config from phase-0, before this sweep widened the search)

Produces two plots under ``phases/phase_1/plots/``:

* ``top_k_equity_overlay.png`` — log-scale equity curves, all curves
  normalised to 1.0 at the scoring start (1980-01-02).
* ``top_k_ratio_to_spy.png`` — strategy / B&H SPY (log scale). Above 1.0
  = beating the benchmark.

Two scenarios are plotted side-by-side in each figure: tax-free and
br_lei_14754. The taxed view is the realistic one for a BR investor;
the tax-free view shows the gross signal edge.

Usage::

    uv run python -m studies.lrs.phases.phase_1.plot_top_curves
"""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from market_lab.backtest.strategies.letf_rotation import compute_regime_signal
from studies.lrs.scripts.data import MODERN_ERA_START, PHASE_1_TICKERS, load_modern_data
from studies.lrs.scripts.tax import simulate_rotation_with_annual_tax

log = logging.getLogger("studies.lrs.phase_1.plot_top_curves")

PHASE_DIR = Path(__file__).resolve().parent
PLOTS_DIR = PHASE_DIR / "plots"
RESULTS_DIR = PHASE_DIR / "results"

TAX_RATE = 0.15
BAND_PCT = 0.0
TOP_K_PER_ONLEG = 5

# Off-leg ticker mapping (matches run.py).
OFF_LEG_TICKER: dict[str, str | None] = {
    "CASH": None,
    "GLD":  "GLDSIM",
    "IEF":  "IEFSIM",
    "ZROZ": "ZROZSIM",
}
ON_LEG_TICKER: dict[str, str] = {"SSO": "SSOSIM", "UPRO": "UPROSIM"}


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

#: Each "kind" of curve gets a colour/linestyle so the plot reads at a glance:
#: gray = pure B&H references; orange/red = phase-0 LRS-SMA200/CASH baseline;
#: cool palette = phase-1 winners (deeper colours for higher ranks).
KIND_STYLES: dict[str, dict[str, object]] = {
    "bh_spy":  {"color": "#000000", "linestyle": "--", "linewidth": 1.6, "alpha": 0.85, "zorder": 4},
    "bh_sso":  {"color": "#888888", "linestyle": "-",  "linewidth": 1.2, "alpha": 0.70, "zorder": 2},
    "bh_upro": {"color": "#bb6666", "linestyle": "-",  "linewidth": 1.2, "alpha": 0.55, "zorder": 2},
    "p0_sso":  {"color": "#f59e0b", "linestyle": "--", "linewidth": 1.7, "alpha": 0.95, "zorder": 5},
    "p0_upro": {"color": "#dc2626", "linestyle": "--", "linewidth": 1.7, "alpha": 0.95, "zorder": 5},
    # Phase-1 SSO ranks (top-5): blues
    "p1_sso_1": {"color": "#0066ff", "linestyle": "-", "linewidth": 2.0, "alpha": 0.95, "zorder": 6},
    "p1_sso_2": {"color": "#3399ff", "linestyle": "-", "linewidth": 1.4, "alpha": 0.80, "zorder": 5},
    "p1_sso_3": {"color": "#66bbff", "linestyle": "-", "linewidth": 1.0, "alpha": 0.65, "zorder": 4},
    "p1_sso_4": {"color": "#99ccff", "linestyle": "-", "linewidth": 0.9, "alpha": 0.55, "zorder": 3},
    "p1_sso_5": {"color": "#cce0ff", "linestyle": "-", "linewidth": 0.8, "alpha": 0.50, "zorder": 3},
    # Phase-1 UPRO ranks (top-5): greens
    "p1_upro_1": {"color": "#16a34a", "linestyle": "-", "linewidth": 2.0, "alpha": 0.95, "zorder": 6},
    "p1_upro_2": {"color": "#22c55e", "linestyle": "-", "linewidth": 1.4, "alpha": 0.80, "zorder": 5},
    "p1_upro_3": {"color": "#4ade80", "linestyle": "-", "linewidth": 1.0, "alpha": 0.65, "zorder": 4},
    "p1_upro_4": {"color": "#86efac", "linestyle": "-", "linewidth": 0.9, "alpha": 0.55, "zorder": 3},
    "p1_upro_5": {"color": "#bbf7d0", "linestyle": "-", "linewidth": 0.8, "alpha": 0.50, "zorder": 3},
}


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------


def _simulate_config(
    *,
    on_leg: str,
    filter_: str,
    lookback: int,
    risk_off: str,
    prices: pd.DataFrame,
    start_date: pd.Timestamp,
) -> tuple[pd.Series, pd.Series, int]:
    """Re-simulate one (filter, lookback, on_leg, risk_off) config.

    Returns ``(taxed_equity, tax_free_equity, n_switches)``.
    """
    spy_prices = prices["SPYSIM"]
    on_rets = prices[ON_LEG_TICKER[on_leg]].pct_change()
    off_ticker = OFF_LEG_TICKER[risk_off]
    off_rets = prices[off_ticker].pct_change() if off_ticker is not None else None

    signal = compute_regime_signal(
        spy_prices, filter=filter_, lookback=lookback, band_pct=BAND_PCT
    )
    sim = simulate_rotation_with_annual_tax(
        on_rets.loc[start_date:],
        signal.loc[start_date:],
        tax_rate=TAX_RATE,
        off_leg_returns=off_rets.loc[start_date:] if off_rets is not None else None,
    )
    return sim.equity, sim.pretax_equity, sim.n_switches


def _bh_curve(returns: pd.Series, start_date: pd.Timestamp) -> pd.Series:
    """Buy-and-hold equity starting at 1.0 on ``start_date``."""
    r = returns.loc[start_date:].astype(float).fillna(0.0)
    eq = (1.0 + r).cumprod()
    eq.iloc[0] = 1.0
    return eq


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def _normalise_at_start(eq: pd.Series, start: pd.Timestamp) -> pd.Series:
    """Renormalise an equity curve to 1.0 at ``start``."""
    eq = eq.dropna()
    if eq.empty:
        return eq
    base = eq.loc[eq.index >= start].iloc[0] if (eq.index >= start).any() else eq.iloc[0]
    return eq / float(base)


def _plot_panel(
    ax,
    curves: dict[str, tuple[pd.Series, str, str]],   # label → (equity, kind_key, terminal_text)
    *,
    title: str,
    ylabel: str,
    reference_line: float | None = None,
    show_legend: bool = True,
) -> None:
    """Plot one panel (one ax) with a dict of (equity, kind, terminal_str)."""
    if reference_line is not None:
        ax.axhline(reference_line, color="black", linestyle=":", linewidth=0.7, alpha=0.7, zorder=1)

    for label, (eq, kind, terminal_text) in curves.items():
        eq_clean = eq.dropna()
        if eq_clean.empty:
            continue
        style = KIND_STYLES.get(kind, {"color": "#666666", "linewidth": 1.0})
        ax.plot(eq_clean.index, eq_clean.values, label=f"{label}  {terminal_text}", **style)

    ax.set_yscale("log")
    ax.set_title(title, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(True, which="both", linewidth=0.3, alpha=0.35)
    if show_legend:
        ax.legend(loc="upper left", fontsize=7, framealpha=0.85, ncol=1)


def _render_overlay(
    panels: dict[str, dict[str, tuple[pd.Series, str, str]]],
    out_path: Path,
    title: str,
    ylabel: str,
    reference_line: float | None = None,
) -> None:
    """Two side-by-side panels (tax-free | taxed), shared y-scale via log."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.5), sharey=True)
    for ax, (scenario, curves) in zip(axes, panels.items()):
        _plot_panel(ax, curves, title=scenario, ylabel=ylabel,
                    reference_line=reference_line, show_legend=True)
    fig.suptitle(title, fontsize=11)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.96))
    fig.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Public API (callable from run.py)
# ---------------------------------------------------------------------------


def render_top_k_comparison(
    prices: pd.DataFrame,
    start_date: pd.Timestamp,
    sweep_top_df: pd.DataFrame,
    *,
    plots_dir: Path = PLOTS_DIR,
    k_per_on_leg: int = TOP_K_PER_ONLEG,
) -> list[dict]:
    """Render the top-K equity-comparison plots and return the terminal table.

    Caller is responsible for having ``prices`` (the full DataFrame with the
    six PHASE_1_TICKERS) and ``sweep_top_df`` (typically ``sweep_top20.csv``
    loaded as a DataFrame). This function:

    1. Re-simulates phase-0 references (SMA200/CASH) on both on-legs.
    2. Re-simulates top-``k_per_on_leg`` phase-1 configs per on-leg, ranked
       by final_score in the ``br_lei_14754`` scenario.
    3. Renders ``top_k_equity_overlay.png`` and ``top_k_ratio_to_spy.png``
       into ``plots_dir``.
    4. Returns a list of dicts (one per curve) suitable for embedding as a
       markdown table — ``[{"label", "kind", "tax_free_terminal",
       "taxed_terminal", "taxed_ratio_to_spy"}, ...]``.
    """
    plots_dir.mkdir(parents=True, exist_ok=True)

    spy_rets = prices["SPYSIM"].pct_change()
    sso_rets = prices["SSOSIM"].pct_change()
    upro_rets = prices["UPROSIM"].pct_change()

    spy_eq = _bh_curve(spy_rets, start_date)
    sso_eq = _bh_curve(sso_rets, start_date)
    upro_eq = _bh_curve(upro_rets, start_date)

    log.info("simulating phase-0 references (SMA200/CASH)...")
    p0_sso_taxed, p0_sso_free, _ = _simulate_config(
        on_leg="SSO", filter_="SMA", lookback=200, risk_off="CASH",
        prices=prices, start_date=start_date,
    )
    p0_upro_taxed, p0_upro_free, _ = _simulate_config(
        on_leg="UPRO", filter_="SMA", lookback=200, risk_off="CASH",
        prices=prices, start_date=start_date,
    )

    log.info("re-simulating top-%d phase-1 configs per on-leg...", k_per_on_leg)
    taxed_df = sweep_top_df[sweep_top_df["tax_scenario"] == "br_lei_14754"].copy()
    top_sso = taxed_df[taxed_df["on_leg"] == "SSO"].sort_values(
        "final_score", ascending=False
    ).head(k_per_on_leg).reset_index(drop=True)
    top_upro = taxed_df[taxed_df["on_leg"] == "UPRO"].sort_values(
        "final_score", ascending=False
    ).head(k_per_on_leg).reset_index(drop=True)

    p1_sso: list[tuple[str, pd.Series, pd.Series, dict]] = []
    for rank, row in top_sso.iterrows():
        taxed_eq, free_eq, n_sw = _simulate_config(
            on_leg="SSO", filter_=row["filter"], lookback=int(row["lookback"]),
            risk_off=row["risk_off"], prices=prices, start_date=start_date,
        )
        label = f"P1 #{rank+1} SSO/{row['filter']}{int(row['lookback'])}/{row['risk_off']}"
        p1_sso.append((label, taxed_eq, free_eq, {"rank": rank+1, "score": float(row["final_score"]), "n_sw": n_sw}))
        log.info("  %s  taxed_final=%+.4f  switches=%d", label, row["final_score"], n_sw)

    p1_upro: list[tuple[str, pd.Series, pd.Series, dict]] = []
    for rank, row in top_upro.iterrows():
        taxed_eq, free_eq, n_sw = _simulate_config(
            on_leg="UPRO", filter_=row["filter"], lookback=int(row["lookback"]),
            risk_off=row["risk_off"], prices=prices, start_date=start_date,
        )
        label = f"P1 #{rank+1} UPRO/{row['filter']}{int(row['lookback'])}/{row['risk_off']}"
        p1_upro.append((label, taxed_eq, free_eq, {"rank": rank+1, "score": float(row["final_score"]), "n_sw": n_sw}))
        log.info("  %s  taxed_final=%+.4f  switches=%d", label, row["final_score"], n_sw)

    # Render plots (delegates to the existing _render_overlay helper below).
    _render_top_k_plots(
        spy_eq=spy_eq, sso_eq=sso_eq, upro_eq=upro_eq,
        p0_sso_taxed=p0_sso_taxed, p0_sso_free=p0_sso_free,
        p0_upro_taxed=p0_upro_taxed, p0_upro_free=p0_upro_free,
        p1_sso=p1_sso, p1_upro=p1_upro,
        plots_dir=plots_dir,
    )

    # Build the terminal-multiples table for report.md.
    def _terminal(eq: pd.Series) -> float:
        return float(eq.dropna().iloc[-1])

    spy_t = _terminal(spy_eq)
    table: list[dict] = [
        {"label": "B&H SPY",  "kind": "benchmark",
         "tax_free_terminal": spy_t,             "taxed_terminal": spy_t,
         "taxed_ratio_to_spy": 1.0},
        {"label": "B&H SSO",  "kind": "benchmark",
         "tax_free_terminal": _terminal(sso_eq), "taxed_terminal": _terminal(sso_eq),
         "taxed_ratio_to_spy": _terminal(sso_eq) / spy_t},
        {"label": "B&H UPRO", "kind": "benchmark",
         "tax_free_terminal": _terminal(upro_eq), "taxed_terminal": _terminal(upro_eq),
         "taxed_ratio_to_spy": _terminal(upro_eq) / spy_t},
        {"label": "P0 LRS-SSO (SMA200/CASH)",  "kind": "phase0",
         "tax_free_terminal": _terminal(p0_sso_free),  "taxed_terminal": _terminal(p0_sso_taxed),
         "taxed_ratio_to_spy": _terminal(p0_sso_taxed) / spy_t},
        {"label": "P0 LRS-UPRO (SMA200/CASH)", "kind": "phase0",
         "tax_free_terminal": _terminal(p0_upro_free), "taxed_terminal": _terminal(p0_upro_taxed),
         "taxed_ratio_to_spy": _terminal(p0_upro_taxed) / spy_t},
    ]
    for label, taxed_eq, free_eq, _meta in p1_sso:
        table.append({
            "label": label, "kind": "phase1",
            "tax_free_terminal": _terminal(free_eq),
            "taxed_terminal": _terminal(taxed_eq),
            "taxed_ratio_to_spy": _terminal(taxed_eq) / spy_t,
        })
    for label, taxed_eq, free_eq, _meta in p1_upro:
        table.append({
            "label": label, "kind": "phase1",
            "tax_free_terminal": _terminal(free_eq),
            "taxed_terminal": _terminal(taxed_eq),
            "taxed_ratio_to_spy": _terminal(taxed_eq) / spy_t,
        })
    return table


def _render_top_k_plots(
    *,
    spy_eq: pd.Series,
    sso_eq: pd.Series,
    upro_eq: pd.Series,
    p0_sso_taxed: pd.Series,
    p0_sso_free: pd.Series,
    p0_upro_taxed: pd.Series,
    p0_upro_free: pd.Series,
    p1_sso: list[tuple[str, pd.Series, pd.Series, dict]],
    p1_upro: list[tuple[str, pd.Series, pd.Series, dict]],
    plots_dir: Path,
) -> None:
    """Render top_k_equity_overlay.png and top_k_ratio_to_spy.png."""

    # ---------- Plot 1: equity overlay (tax-free vs taxed) ----------

    def _term(eq: pd.Series) -> str:
        return f"({float(eq.dropna().iloc[-1]):.1f}×)"

    panels: dict[str, dict[str, tuple[pd.Series, str, str]]] = {}
    for scenario_label, choose_eq in (
        ("tax-free (pretax_equity)", lambda free, taxed: free),
        ("br_lei_14754 (15% annual)", lambda free, taxed: taxed),
    ):
        scenario_curves: dict[str, tuple[pd.Series, str, str]] = {}
        scenario_curves["B&H SPY"] = (spy_eq, "bh_spy", _term(spy_eq))
        scenario_curves["B&H SSO"] = (sso_eq, "bh_sso", _term(sso_eq))
        scenario_curves["B&H UPRO"] = (upro_eq, "bh_upro", _term(upro_eq))
        p0_sso_eq = choose_eq(p0_sso_free, p0_sso_taxed)
        p0_upro_eq = choose_eq(p0_upro_free, p0_upro_taxed)
        scenario_curves["P0 LRS-SSO (SMA200/CASH)"] = (p0_sso_eq, "p0_sso", _term(p0_sso_eq))
        scenario_curves["P0 LRS-UPRO (SMA200/CASH)"] = (p0_upro_eq, "p0_upro", _term(p0_upro_eq))
        for label, taxed_eq, free_eq, meta in p1_sso:
            eq = choose_eq(free_eq, taxed_eq)
            scenario_curves[label] = (eq, f"p1_sso_{meta['rank']}", _term(eq))
        for label, taxed_eq, free_eq, meta in p1_upro:
            eq = choose_eq(free_eq, taxed_eq)
            scenario_curves[label] = (eq, f"p1_upro_{meta['rank']}", _term(eq))
        panels[scenario_label] = scenario_curves

    overlay_path = plots_dir / "top_k_equity_overlay.png"
    log.info("rendering %s ...", overlay_path.name)
    _render_overlay(
        panels,
        overlay_path,
        title=("studies/lrs phase-1 — top-5 winners per on-leg vs phase-0 baseline (SMA200/CASH) "
               "and B&H benchmarks  ·  1980-01-02 → 2026-05-21  ·  log scale"),
        ylabel="Equity growth (normalised to 1.0 at start)",
    )

    # ---------- Plot 2: ratio to B&H SPY ----------

    def _ratio_term(eq: pd.Series, bench: pd.Series) -> str:
        ec, bc = eq.dropna(), bench.dropna()
        common = ec.index.intersection(bc.index)
        if len(common) < 2:
            return "(n/a)"
        r = (ec.loc[common] / float(ec.loc[common].iloc[0])) / (
            bc.loc[common] / float(bc.loc[common].iloc[0])
        )
        return f"({float(r.iloc[-1]):.2f}× SPY)"

    def _ratio(eq: pd.Series, bench: pd.Series) -> pd.Series:
        ec, bc = eq.dropna(), bench.dropna()
        common = ec.index.intersection(bc.index)
        if len(common) < 2:
            return pd.Series(dtype=float)
        return (ec.loc[common] / float(ec.loc[common].iloc[0])) / (
            bc.loc[common] / float(bc.loc[common].iloc[0])
        )

    ratio_panels: dict[str, dict[str, tuple[pd.Series, str, str]]] = {}
    for scenario_label, choose_eq in (
        ("tax-free (pretax_equity)", lambda free, taxed: free),
        ("br_lei_14754 (15% annual)", lambda free, taxed: taxed),
    ):
        scenario_curves = {}
        scenario_curves["B&H SSO"] = (_ratio(sso_eq, spy_eq), "bh_sso", _ratio_term(sso_eq, spy_eq))
        scenario_curves["B&H UPRO"] = (_ratio(upro_eq, spy_eq), "bh_upro", _ratio_term(upro_eq, spy_eq))
        p0_sso_eq = choose_eq(p0_sso_free, p0_sso_taxed)
        p0_upro_eq = choose_eq(p0_upro_free, p0_upro_taxed)
        scenario_curves["P0 LRS-SSO (SMA200/CASH)"] = (_ratio(p0_sso_eq, spy_eq), "p0_sso", _ratio_term(p0_sso_eq, spy_eq))
        scenario_curves["P0 LRS-UPRO (SMA200/CASH)"] = (_ratio(p0_upro_eq, spy_eq), "p0_upro", _ratio_term(p0_upro_eq, spy_eq))
        for label, taxed_eq, free_eq, meta in p1_sso:
            eq = choose_eq(free_eq, taxed_eq)
            scenario_curves[label] = (_ratio(eq, spy_eq), f"p1_sso_{meta['rank']}", _ratio_term(eq, spy_eq))
        for label, taxed_eq, free_eq, meta in p1_upro:
            eq = choose_eq(free_eq, taxed_eq)
            scenario_curves[label] = (_ratio(eq, spy_eq), f"p1_upro_{meta['rank']}", _ratio_term(eq, spy_eq))
        ratio_panels[scenario_label] = scenario_curves

    ratio_path = plots_dir / "top_k_ratio_to_spy.png"
    log.info("rendering %s ...", ratio_path.name)
    _render_overlay(
        ratio_panels,
        ratio_path,
        title=("studies/lrs phase-1 — top-5 winners ratio to B&H SPY "
               "(above 1.0 = beating SPY)  ·  log scale"),
        ylabel="Strategy / B&H SPY (renormalised)",
        reference_line=1.0,
    )


# ---------------------------------------------------------------------------
# Standalone CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """Re-run the top-K comparison off an existing ``sweep_top20.csv``.

    Allows regenerating the plots without re-running the 4.5-minute sweep.
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    log.info("loading testfolio data (modern era from %s)...", MODERN_ERA_START.date())
    modern = load_modern_data(MODERN_ERA_START, tickers=PHASE_1_TICKERS)
    prices = modern.full
    start_date = modern.scoring_start

    sweep_top_df = pd.read_csv(RESULTS_DIR / "sweep_top20.csv")
    table = render_top_k_comparison(prices, start_date, sweep_top_df, plots_dir=PLOTS_DIR)

    log.info("terminal multiples (sorted by taxed ratio to SPY):")
    for row in sorted(table, key=lambda r: -r["taxed_ratio_to_spy"]):
        log.info(
            "  %-40s  tax-free=%8.1fx  taxed=%8.1fx  =%6.2fx SPY",
            row["label"], row["tax_free_terminal"],
            row["taxed_terminal"], row["taxed_ratio_to_spy"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
