#!/usr/bin/env python3
"""Iter 053 — rigorous validation of SPMO sleeve on B4+BTC5.

Pre-registered candidate: 25% NTSX / 25% GDE / 25% RSST / 15% ZROZ /
5% BTC / 5% SPMO. Momentum is allowed as a factor sleeve because price
momentum is a documented anomaly `[stocks_on_the_move, ch.4]`, but promotion
requires out-of-sample and bootstrap evidence rather than recent popularity
`[advances_fin_ml, p.196-202]`. Parameter snooping is controlled by testing a
small fixed neighborhood and reporting failures `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).parent
SOURCE_052 = SCRIPT_DIR.parent / "052-2026-05-03-momentum-scv-sleeves" / "testfolio_data"
SOURCE_046 = SCRIPT_DIR.parent / "046-2026-05-03-factor-tilt-and-ndx-deleveraged" / "testfolio_data"
INITIAL = 10_000.0
TRADING_DAYS = 252


def curve_metrics(values: pd.Series) -> dict[str, float | str]:
    values = values.dropna()
    rets = values.pct_change().dropna()
    years = (values.index[-1] - values.index[0]).days / 365.25
    cagr = (values.iloc[-1] / values.iloc[0]) ** (1 / years) - 1
    dd = values / values.cummax() - 1
    sharpe = math.sqrt(TRADING_DAYS) * rets.mean() / rets.std(ddof=0)
    return {
        "window": f"{values.index[0].date()} -> {values.index[-1].date()} ({years:.2f}y)",
        "years": years,
        "cagr_pct": cagr * 100,
        "mdd_pct": dd.min() * 100,
        "sharpe": sharpe,
        "end_val": values.iloc[-1],
    }


def load_group(group: str) -> dict[str, pd.Series]:
    payload = json.loads((SOURCE_052 / f"{group}.json").read_text())
    response = payload["response"]
    portfolios = payload["portfolios"]
    timestamps = pd.to_datetime(response["charts"]["history"][0], unit="s", utc=True).tz_convert(None)
    curves = {}
    for i, p in enumerate(portfolios, start=1):
        curves[p["slug"]] = pd.Series(response["charts"]["history"][i], index=timestamps, name=p["slug"]).astype(float)
    return curves


def rolling_stats(candidate: pd.Series, baseline: pd.Series, years: int) -> dict[str, Any]:
    frame = pd.concat([candidate, baseline], axis=1, join="inner").dropna()
    window = int(TRADING_DAYS * years)
    if len(frame) <= window:
        return {"years": years, "n_windows": 0, "cagr_win_rate": None, "mdd_no_worse_rate": None}
    cand = frame.iloc[:, 0]
    base = frame.iloc[:, 1]
    cand_cagr = (cand / cand.shift(window)) ** (TRADING_DAYS / window) - 1
    base_cagr = (base / base.shift(window)) ** (TRADING_DAYS / window) - 1
    cand_mdd = cand.rolling(window).apply(lambda x: float((x / np.maximum.accumulate(x) - 1).min()), raw=True)
    base_mdd = base.rolling(window).apply(lambda x: float((x / np.maximum.accumulate(x) - 1).min()), raw=True)
    valid = pd.concat([cand_cagr, base_cagr, cand_mdd, base_mdd], axis=1).dropna()
    return {
        "years": years,
        "n_windows": int(len(valid)),
        "cagr_win_rate": float((valid.iloc[:, 0] > valid.iloc[:, 1]).mean()),
        "mdd_no_worse_rate": float((valid.iloc[:, 2] >= valid.iloc[:, 3]).mean()),
        "both_rate": float(((valid.iloc[:, 0] > valid.iloc[:, 1]) & (valid.iloc[:, 2] >= valid.iloc[:, 3])).mean()),
    }


def split_stats(candidate: pd.Series, baseline: pd.Series) -> dict[str, Any]:
    frame = pd.concat([candidate, baseline], axis=1, join="inner").dropna()
    split = int(len(frame) * 0.70)
    out: dict[str, Any] = {}
    for name, part in [("train70", frame.iloc[:split]), ("oos30", frame.iloc[split:])]:
        cand_m = curve_metrics(part.iloc[:, 0])
        base_m = curve_metrics(part.iloc[:, 1])
        out[name] = {
            "candidate": cand_m,
            "baseline": base_m,
            "delta_cagr_pct": cand_m["cagr_pct"] - base_m["cagr_pct"],
            "delta_sharpe": cand_m["sharpe"] - base_m["sharpe"],
            "mdd_improved_pp": abs(base_m["mdd_pct"]) - abs(cand_m["mdd_pct"]),
        }
    return out


def block_bootstrap_excess(candidate: pd.Series, baseline: pd.Series, *, block: int = 21, reps: int = 5000) -> dict[str, float]:
    frame = pd.concat([candidate.pct_change(), baseline.pct_change()], axis=1, join="inner").dropna()
    excess = (frame.iloc[:, 0] - frame.iloc[:, 1]).to_numpy()
    rng = np.random.default_rng(53053)
    n = len(excess)
    samples = np.empty(reps)
    starts = np.arange(0, max(1, n - block + 1))
    for i in range(reps):
        picked: list[np.ndarray] = []
        while sum(len(x) for x in picked) < n:
            start = int(rng.choice(starts))
            picked.append(excess[start : start + block])
        path = np.concatenate(picked)[:n]
        samples[i] = path.mean() * TRADING_DAYS
    return {
        "mean_annual_excess_pct": float(samples.mean() * 100),
        "ci_5_pct": float(np.quantile(samples, 0.05) * 100),
        "ci_1_pct": float(np.quantile(samples, 0.01) * 100),
        "ci_0p1_pct": float(np.quantile(samples, 0.001) * 100),
        "prob_excess_gt_0": float((samples > 0).mean()),
        "block_days": block,
        "reps": reps,
    }


def year_table(candidate: pd.Series, baseline: pd.Series) -> list[dict[str, Any]]:
    frame = pd.concat([candidate, baseline], axis=1, join="inner").dropna()
    rows = []
    for year, part in frame.groupby(frame.index.year):
        if len(part) < 20:
            continue
        cand_ret = part.iloc[-1, 0] / part.iloc[0, 0] - 1
        base_ret = part.iloc[-1, 1] / part.iloc[0, 1] - 1
        rows.append({"year": int(year), "candidate_return_pct": cand_ret * 100, "baseline_return_pct": base_ret * 100, "delta_pct": (cand_ret - base_ret) * 100})
    return rows


def long_proxy_results() -> dict[str, Any]:
    curves: dict[str, pd.Series] = {}
    for filename in ["static_backtest_a.json", "static_backtest_b.json"]:
        payload = json.loads((SOURCE_046 / filename).read_text())
        response = payload["response"]
        portfolios = payload["portfolios"]
        timestamps = pd.to_datetime(response["charts"]["history"][0], unit="s", utc=True).tz_convert(None)
        for i, p in enumerate(portfolios, start=1):
            if p["slug"] in {"B4_rsst7030_baseline", "B4_mtum10_from_zroz", "B4_scv10_from_zroz", "B4_scv10_from_ntsx"}:
                curves[p["slug"]] = pd.Series(response["charts"]["history"][i], index=timestamps, name=p["slug"]).astype(float)
    base = curves["B4_rsst7030_baseline"]
    rows = []
    for slug, curve in curves.items():
        m = curve_metrics(curve)
        rows.append({"slug": slug, **m})
    return {
        "rows": rows,
        "bootstrap_mtum10_vs_base": block_bootstrap_excess(curves["B4_mtum10_from_zroz"], base),
        "source": "iter046 cached testfol.io curves; no BTC; MTUMSIM proxy over 2000+ common window",
    }


def main() -> int:
    live_curves = load_group("b4_btc_screen_a")
    standalone = load_group("standalone_spmo_live")
    candidate = live_curves["B4_btc5_spmo5_from_zroz"]
    baseline = live_curves["B4_btc5"]
    neighbor_slugs = ["B4_btc5", "B4_btc5_spmo2p5_from_zroz", "B4_btc5_spmo5_from_zroz", "B4_btc5_mtum5_from_zroz", "B4_btc5_vbr5_from_zroz"]
    neighbor_rows = [{"slug": slug, **curve_metrics(live_curves[slug])} for slug in neighbor_slugs]
    neighbor_rows = sorted(neighbor_rows, key=lambda r: (-float(r["sharpe"]), -float(r["cagr_pct"])))

    standalone_rows = [{"slug": slug, **curve_metrics(curve)} for slug, curve in standalone.items()]
    standalone_rows = sorted(standalone_rows, key=lambda r: (-float(r["sharpe"]), -float(r["cagr_pct"])))

    result = {
        "verdict": "research_promising_not_gate_equivalent",
        "reason": "SPMO live and B4+BTC5 sleeve improve the observed windows, but live sleeve window is 2022+ and bootstrap 99.9% / full PBO-DSR cannot be honestly satisfied.",
        "candidate_slug": "B4_btc5_spmo5_from_zroz",
        "candidate_allocation": {"NTSX": 0.25, "GDE": 0.25, "RSST": 0.25, "ZROZ": 0.15, "BTC": 0.05, "SPMO": 0.05},
        "live_candidate": curve_metrics(candidate),
        "live_baseline": curve_metrics(baseline),
        "live_delta": {
            "cagr_pct": curve_metrics(candidate)["cagr_pct"] - curve_metrics(baseline)["cagr_pct"],
            "mdd_improved_pp": abs(curve_metrics(baseline)["mdd_pct"]) - abs(curve_metrics(candidate)["mdd_pct"]),
            "sharpe": curve_metrics(candidate)["sharpe"] - curve_metrics(baseline)["sharpe"],
        },
        "standalone_spmo_window": standalone_rows,
        "neighborhood_rank_live": neighbor_rows,
        "split_stats": split_stats(candidate, baseline),
        "rolling_1y": rolling_stats(candidate, baseline, 1),
        "rolling_2y": rolling_stats(candidate, baseline, 2),
        "rolling_3y": rolling_stats(candidate, baseline, 3),
        "bootstrap_live_excess": block_bootstrap_excess(candidate, baseline),
        "calendar_years_live": year_table(candidate, baseline),
        "long_proxy_no_btc": long_proxy_results(),
        "gates": {
            "G1_PBO": "not_applicable_single_predeclared_candidate; neighborhood reported instead",
            "G2_DSR": "not_claimed; live candidate has only 4.12y due SPMO inception/availability in B4+BTC window",
            "G3_WF": "partial; rolling windows reported, no enough independent 5y folds",
            "G4_OOS_70_30": "reported",
            "G5_recent_forward": "reported via OOS30 and calendar years",
            "G6_bootstrap_99p9_low_gt_0": "reported; promote only if ci_0p1_pct > 0",
            "G7_cross_lib": "not_run; source is testfol.io only",
        },
    }
    result["gates"]["G6_pass"] = result["bootstrap_live_excess"]["ci_0p1_pct"] > 0
    result["overall_gate_equivalent"] = False

    (SCRIPT_DIR / "verdict.json").write_text(json.dumps(result, indent=2))
    write_summary(result)
    print(json.dumps({
        "verdict": result["verdict"],
        "live_delta": result["live_delta"],
        "bootstrap_live_excess": result["bootstrap_live_excess"],
        "G6_pass": result["gates"]["G6_pass"],
    }, indent=2))
    return 0


def fmt_metric(row: dict[str, Any]) -> str:
    return f"{row['cagr_pct']:.2f}% / {row['mdd_pct']:.2f}% / {row['sharpe']:.3f}"


def write_summary(result: dict[str, Any]) -> None:
    lines = [
        "# Iter 053 — SPMO rigorous validation",
        "",
        "**Date:** 2026-05-03",
        "**Candidate:** 25% NTSX / 25% GDE / 25% RSST / 15% ZROZ / 5% BTC / 5% SPMO.",
        "**Verdict:** research-promising, not gate-equivalent.",
        "",
        "## Live Candidate",
        "",
        f"Window: {result['live_candidate']['window']}",
        "",
        "| row | CAGR | MDD | Sharpe |",
        "|---|---:|---:|---:|",
        f"| B4+BTC5+5% SPMO | {result['live_candidate']['cagr_pct']:.2f}% | {result['live_candidate']['mdd_pct']:.2f}% | {result['live_candidate']['sharpe']:.3f} |",
        f"| B4+BTC5 baseline | {result['live_baseline']['cagr_pct']:.2f}% | {result['live_baseline']['mdd_pct']:.2f}% | {result['live_baseline']['sharpe']:.3f} |",
        "",
        "Delta versus baseline:",
        "",
        f"- CAGR: +{result['live_delta']['cagr_pct']:.2f}pp",
        f"- MDD: {result['live_delta']['mdd_improved_pp']:.2f}pp improvement",
        f"- Sharpe: +{result['live_delta']['sharpe']:.3f}",
        "",
        "## Bootstrap Excess Return",
        "",
        "Block bootstrap on daily excess returns versus B4+BTC5 baseline.",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    boot = result["bootstrap_live_excess"]
    for key in ["mean_annual_excess_pct", "ci_5_pct", "ci_1_pct", "ci_0p1_pct", "prob_excess_gt_0"]:
        val = boot[key]
        suffix = "%" if key != "prob_excess_gt_0" else ""
        lines.append(f"| {key} | {val:.4f}{suffix} |")
    lines += [
        "",
        "## OOS Split",
        "",
        "| split | candidate | baseline | delta CAGR | delta Sharpe | MDD improvement |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for split_name in ["train70", "oos30"]:
        row = result["split_stats"][split_name]
        lines.append(
            f"| {split_name} | {fmt_metric(row['candidate'])} | {fmt_metric(row['baseline'])} | "
            f"{row['delta_cagr_pct']:.2f}pp | {row['delta_sharpe']:.3f} | {row['mdd_improved_pp']:.2f}pp |"
        )
    lines += [
        "",
        "## Rolling Windows",
        "",
        "| window | n | CAGR win-rate | MDD no-worse rate | both rate |",
        "|---:|---:|---:|---:|---:|",
    ]
    for key in ["rolling_1y", "rolling_2y", "rolling_3y"]:
        row = result[key]
        if row["n_windows"] == 0:
            lines.append(f"| {row['years']}y | 0 | n/a | n/a | n/a |")
        else:
            lines.append(f"| {row['years']}y | {row['n_windows']} | {row['cagr_win_rate']:.2%} | {row['mdd_no_worse_rate']:.2%} | {row['both_rate']:.2%} |")
    lines += [
        "",
        "## Neighborhood Rank",
        "",
        "| rank | strategy | CAGR | MDD | Sharpe |",
        "|---:|---|---:|---:|---:|",
    ]
    for i, row in enumerate(result["neighborhood_rank_live"], 1):
        lines.append(f"| {i} | {row['slug']} | {row['cagr_pct']:.2f}% | {row['mdd_pct']:.2f}% | {row['sharpe']:.3f} |")
    lines += [
        "",
        "## Long Proxy Without BTC",
        "",
        "Uses local testfol.io synthetic cache with MTUMSIM as a longer momentum proxy. This does not prove SPMO and excludes BTC, but it tests whether momentum survives outside the short live SPMO window.",
        "",
        "| strategy | window | CAGR | MDD | Sharpe |",
        "|---|---|---:|---:|---:|",
    ]
    for row in result["long_proxy_no_btc"]["rows"]:
        lines.append(f"| {row['slug']} | {row['window']} | {row['cagr_pct']:.2f}% | {row['mdd_pct']:.2f}% | {row['sharpe']:.3f} |")
    lines += [
        "",
        "## Decision",
        "",
        "The candidate improves the observed live B4+BTC5 window and ranks best in the small fixed neighborhood. However, it is not a formal winner because SPMO constrains the actual sleeve test to 2022+ and the full 7-gate battery cannot be honestly completed. Keep as a pre-registered research candidate, not as an automatic replacement for the current B4+BTC5 live candidate.",
    ]
    (SCRIPT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
