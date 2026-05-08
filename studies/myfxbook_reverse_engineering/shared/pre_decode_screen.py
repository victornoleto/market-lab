"""Pre-decode screening — Pipeline v4 Redesign module (task 002).

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task spec: studies/myfxbook_reverse_engineering/v4_redesign/tasks/002-pre-decode-screen.md

Five gates that reject EAs lacking real edge BEFORE compute is spent decoding:

1. K1 sanity (martingale signature) — reuses sanity.compute_sanity (lot-doubling
   after losses within 24h). `[advances_fin_ml, ch.13]` overbetting/martingale.
2. MCPT (Monte Carlo Permutation Test) — sign-flip permutation on per-trade
   pips, fraction of permuted Sharpes >= observed. Preserves marginal
   distribution, destroys sequencing. `[evidence_based_ta, p.325-328]`,
   `[testing_tuning, p.310-322]`.
3. PSR (Probabilistic Sharpe Ratio) on the vendor track record. We use PSR
   (not DSR) because the EA is a single series with M=1 — DSR presupposes
   ex-post selection between M trials, which only applies in Phase 3a after
   LightGBM mining. `[advances_fin_ml, p.260-263]` (PSR formula). DEAD_ENDS.md
   entry "DSR com M=1" documents this rejection from the GPT-5.5 review.
4. Concentration test — top-5% trades vs total |PnL|. >0.50 = curve-fit or
   news-luck. Analogue of Calmar fragility `[machine_trading, p.13-14]`.
5. is_live flag — Real vs Demo from system_info.account.account_type. Logged
   to notes but NOT a hard gate (5/52 systems are Demo; blocking would discard
   decodable material; mandate §3 only requires Real for downstream Plano A
   reactivation). `DEAD_ENDS.md` -> "is_live como hard gate (rejeitado)".

Decision rule (decision="GO"): K1 pass AND mcpt_p<0.05 AND psr_p<0.05 AND
concentration_top5<0.50. is_live is warning-only.

Output: pre_decode_screen.json per system; written next to other system reports.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats

from . import config
from .sanity import compute_sanity

DEFAULT_SEED = 20260503
DEFAULT_N_PERM = 2000
MCPT_THRESHOLD = 0.05
PSR_THRESHOLD = 0.05
CONCENTRATION_TOP5_THRESHOLD = 0.50


@dataclass(frozen=True)
class PreScreenResult:
    """Per-system pre-screen verdict.

    PSR replaces DSR here on purpose — see module docstring and DEAD_ENDS.md.
    `is_live` is informational; it never participates in `decision`.
    """

    system_id: str
    decision: str  # "GO" | "STOP"
    k1_sanity_pass: bool
    mcpt_p: float
    psr_p: float
    concentration_top5: float
    is_live: bool
    n_trades: int
    sharpe_per_trade: float
    notes: list[str] = field(default_factory=list)


def _sharpe_per_trade(returns: np.ndarray) -> float:
    """Per-trade Sharpe = mean / std (no annualization).

    No annualization here: MCPT permutes the same N samples, so the sqrt(N)
    factor cancels in the ratio between observed and permuted statistics.
    PSR uses sr_benchmark=0 and is invariant to the annualization factor.
    """
    if returns.size < 2:
        return 0.0
    sd = float(returns.std(ddof=1))
    if sd == 0.0 or not np.isfinite(sd):
        return 0.0
    return float(returns.mean()) / sd


def _mcpt_p_value(returns: np.ndarray, n_permutations: int, seed: int) -> float:
    """Sign-flip MCPT.

    Permutes the sign of each trade return, recomputes Sharpe, returns the
    fraction (count_better+1)/(n_permutations+1) of permuted Sharpes >=
    observed. Preserves marginal distribution (heavy-tail intact), destroys
    sequencing — H0: returns are sign-symmetric noise. Reject if p < 0.05.
    `[evidence_based_ta, p.325-328]`.
    """
    if returns.size < 2:
        return 1.0
    observed = _sharpe_per_trade(returns)
    rng = np.random.default_rng(seed)
    count_better = 0
    for _ in range(n_permutations):
        signs = rng.choice([-1.0, 1.0], size=returns.size)
        permuted = returns * signs
        if _sharpe_per_trade(permuted) >= observed:
            count_better += 1
    return (count_better + 1) / (n_permutations + 1)


def _psr_p_value(returns: np.ndarray, sr_benchmark: float = 0.0) -> float:
    """Probabilistic Sharpe Ratio p-value (track record, M=1).

    `[advances_fin_ml, p.260-263]`. p = 1 - Phi(z) where
        z = (SR - SR_b) * sqrt(T-1) / sqrt(1 - skew*SR + (kurt-1)/4 * SR^2)
    SR is per-trade. kurt is non-Fisher (3 for gaussian, matches AFML p.262).

    H0: true SR <= SR_b. Reject if p < 0.05 (i.e. true SR statistically > 0).
    """
    T = returns.size
    if T < 4:
        return 1.0
    sr = _sharpe_per_trade(returns)
    skew = float(scipy.stats.skew(returns, bias=False))
    kurt = float(scipy.stats.kurtosis(returns, fisher=False, bias=False))
    denom_sq = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr * sr
    if denom_sq <= 0.0 or not np.isfinite(denom_sq):
        return 1.0
    z = (sr - sr_benchmark) * np.sqrt(T - 1) / np.sqrt(denom_sq)
    if not np.isfinite(z):
        return 1.0
    return float(1.0 - scipy.stats.norm.cdf(z))


def _concentration_top5(returns: np.ndarray) -> float:
    """Share of |total PnL| explained by the top-5% trades by |return|.

    >0.50 means the track record is dominated by a handful of trades —
    likely curve-fit or news-luck rather than reproducible edge.
    `[machine_trading, p.13-14]` Calmar fragility analogue.
    """
    n = returns.size
    if n == 0:
        return 0.0
    total_abs = float(np.abs(returns).sum())
    if total_abs == 0.0:
        return 0.0
    k = max(1, int(np.ceil(0.05 * n)))
    top_k = np.sort(np.abs(returns))[-k:]
    return float(top_k.sum() / total_abs)


def _load_trades(system_id: int | str) -> pd.DataFrame:
    """Load parser output and return the trade-only subset."""
    path = config.trades_parquet_path(system_id)
    if not path.exists():
        raise FileNotFoundError(f"trades.parquet not found at {path}")
    df = pd.read_parquet(path)
    if "is_trade" not in df.columns:
        raise ValueError(f"trades parquet at {path} lacks 'is_trade' column")
    return df[df["is_trade"]].copy().sort_values("close_dt_utc").reset_index(drop=True)


def _load_account_type(system_id: int | str) -> str | None:
    """Return account_type ('Real' | 'Demo') from system_info.json or None."""
    path = config.system_info_json_path(system_id)
    if not path.exists():
        return None
    try:
        info = json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
    account = info.get("account") or {}
    value = account.get("account_type")
    if isinstance(value, str) and value:
        return value
    return None


def screen_system(
    system_id: int | str,
    *,
    n_permutations: int = DEFAULT_N_PERM,
    seed: int = DEFAULT_SEED,
    trades_df: pd.DataFrame | None = None,
    account_type: str | None = None,
) -> PreScreenResult:
    """Run all 5 gates on `system_id` and return the verdict.

    Loads trades.parquet from `data/trades/<id>/` and system_info.json from
    `systems/<id>/` by default; both can be overridden via kwargs (used by
    tests to inject synthetic data).
    """
    sid = str(system_id)
    notes: list[str] = []

    trades = _load_trades(system_id) if trades_df is None else trades_df.copy()
    n_trades = len(trades)
    if n_trades == 0:
        return PreScreenResult(
            system_id=sid,
            decision="STOP",
            k1_sanity_pass=False,
            mcpt_p=1.0,
            psr_p=1.0,
            concentration_top5=0.0,
            is_live=False,
            n_trades=0,
            sharpe_per_trade=0.0,
            notes=["empty trade history"],
        )

    if "pips" not in trades.columns:
        raise ValueError("trades_df missing 'pips' column required for return series")
    returns = trades["pips"].to_numpy(dtype=float)
    returns = returns[np.isfinite(returns)]

    # Gate 1 — K1 sanity (reuse existing module to keep the contract identical
    # to the rest of the pipeline)
    sanity_stats = compute_sanity(trades, sid)
    k1_pass = bool(sanity_stats.k1_pass)
    if not k1_pass:
        notes.append("K1 sanity FAIL: " + "; ".join(sanity_stats.k1_flags))

    # Gate 2 — MCPT
    mcpt_p = _mcpt_p_value(returns, n_permutations=n_permutations, seed=seed)
    if mcpt_p >= MCPT_THRESHOLD:
        notes.append(f"MCPT p={mcpt_p:.4f} >= {MCPT_THRESHOLD}")

    # Gate 3 — PSR
    psr_p = _psr_p_value(returns)
    if psr_p >= PSR_THRESHOLD:
        notes.append(f"PSR p={psr_p:.4f} >= {PSR_THRESHOLD}")

    # Gate 4 — concentration
    conc = _concentration_top5(returns)
    if conc >= CONCENTRATION_TOP5_THRESHOLD:
        notes.append(f"concentration top-5%={conc:.3f} >= {CONCENTRATION_TOP5_THRESHOLD}")

    # Gate 5 — is_live (warning-only)
    if account_type is None:
        account_type = _load_account_type(system_id)
    is_live = account_type == "Real"
    if not is_live:
        notes.append(f"is_live=False (account_type={account_type!r}); warning-only, does not block")

    sr = _sharpe_per_trade(returns)
    decision = (
        "GO"
        if (k1_pass and mcpt_p < MCPT_THRESHOLD and psr_p < PSR_THRESHOLD and conc < CONCENTRATION_TOP5_THRESHOLD)
        else "STOP"
    )

    return PreScreenResult(
        system_id=sid,
        decision=decision,
        k1_sanity_pass=k1_pass,
        mcpt_p=mcpt_p,
        psr_p=psr_p,
        concentration_top5=conc,
        is_live=is_live,
        n_trades=n_trades,
        sharpe_per_trade=sr,
        notes=notes,
    )


def screen_batch(
    system_ids: list[int | str],
    *,
    n_permutations: int = DEFAULT_N_PERM,
    seed: int = DEFAULT_SEED,
) -> list[PreScreenResult]:
    """Sequential map of `screen_system` over a list of ids.

    No multiprocessing here: callers may parallelize externally; keeping this
    simple avoids surprises in tests and reuses the pipeline's process-level
    isolation.
    """
    return [screen_system(sid, n_permutations=n_permutations, seed=seed) for sid in system_ids]


def pre_screen_json_path(system_id: int | str) -> Path:
    return config.system_report_dir(system_id) / "pre_decode_screen.json"


def write_pre_screen_json(result: PreScreenResult, *, output_path: Path | None = None) -> Path:
    """Persist a PreScreenResult to JSON next to other system reports.

    Schema (parseable):
        {
          "system_id": str,
          "decision": "GO" | "STOP",
          "k1_sanity_pass": bool,
          "mcpt_p": float, "psr_p": float, "concentration_top5": float,
          "is_live": bool, "n_trades": int, "sharpe_per_trade": float,
          "notes": list[str]
        }
    """
    path = output_path or pre_screen_json_path(result.system_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(result), indent=2))
    return path
