"""Integration test: T1a end-to-end deterministic.

Verifies that run_iter_t1.run() produces a schema-valid verdict.json with
correct keys and reproducible results.

Data requirement: testfolio cache must be present
(data/testfolio/cache/history.parquet).  If missing the test is skipped with
an informative reason so CI stays green on fresh checkouts.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml


_TESTFOLIO_CACHE = Path("data/testfolio/cache/history.parquet")
_SKIP_REASON = (
    "testfolio cache not found at data/testfolio/cache/history.parquet "
    "— T1a integration test skipped (data required)"
)


@pytest.fixture(scope="module")
def _data_available() -> bool:
    return _TESTFOLIO_CACHE.exists()


# ---------------------------------------------------------------------------
# Helper: minimal T1a config YAML
# ---------------------------------------------------------------------------

_T1A_CONFIG_YAML = """
iter: "900-2026-05-06-T1a-letf-sweep"
tier: "T1a"
hypothesis: "Test T1a sweep with 2 LETFs (UPRO+SSO SMA200 vs BIL)"
primary_citation: "[leverage_for_the_long_run, p.13]"
configs_tested:
  - {name: "upro_sma200_off_bil", on_asset: "UPRO", off_asset: "BIL", signal: "sma", period: 200}
  - {name: "sso_sma200_off_bil",  on_asset: "SSO",  off_asset: "BIL", signal: "sma", period: 200}
datasets: ["lh_56y"]
windows_used:
  lh_56y: "1885-03-20..2026-04-24"
random_seed: 42
cumulative_n_trials_at_iter: 0
tier_inheritance: null
"""


def test_t1a_full_run_deterministic(tmp_path: Path) -> None:
    """Run T1a end-to-end; verify verdict.json schema + result count + reproducibility."""
    if not _TESTFOLIO_CACHE.exists():
        pytest.skip(_SKIP_REASON)

    from studies.letf_rotation_hunt.run_iter import main

    config_path = tmp_path / "test_t1a.yaml"
    config_path.write_text(_T1A_CONFIG_YAML)

    out_dir = tmp_path / "out"
    rc = main(
        [
            "--iter", "900-2026-05-06-T1a-letf-sweep",
            "--config", str(config_path),
            "--out-dir", str(out_dir),
        ]
    )

    assert rc == 0, f"run_iter.main returned non-zero exit code {rc}"

    verdict_path = out_dir / "verdict.json"
    assert verdict_path.exists(), "verdict.json not written"

    verdict = json.loads(verdict_path.read_text())

    # --- schema fields ---
    assert verdict["iter"] == "900-2026-05-06-T1a-letf-sweep"
    assert verdict["tier"] == "T1a"
    assert verdict["hypothesis"].startswith("Test T1a")
    assert verdict["primary_citation"] == "[leverage_for_the_long_run, p.13]"
    assert len(verdict["results"]) == 2, (
        f"Expected 2 results, got {len(verdict['results'])}"
    )

    # --- results have required keys ---
    for r in verdict["results"]:
        assert "config_name" in r
        if "error" not in r:
            assert "metrics_gross" in r
            assert "lh_56y" in r["metrics_gross"]
            assert "sharpe" in r["metrics_gross"]["lh_56y"]
            assert "tier_label" in r

    # --- at least one valid result (no errors) ---
    valid = [r for r in verdict["results"] if "error" not in r]
    assert len(valid) >= 1, f"All configs errored: {[r.get('error') for r in verdict['results']]}"

    # --- best_config is populated ---
    assert verdict["best_config"] != "" or len(valid) == 0
    assert isinstance(verdict["best_score"], (int, float))
    assert verdict["best_tier"] in (
        "WINNER", "STRONG", "PROMISING", "MARGINAL", "NEAR_FAIL", "FAIL", "ERROR"
    )
    # KILL T0 is evaluated in T1a (spec §3.4): PASS if best Sharpe ≥ SPY+0.05,
    # else FIRES. Both are valid outcomes for synthetic small-window data;
    # N/A only when no valid results.
    assert verdict["kill_rule_status"] in {"PASS", "FIRES", "N/A"}
    assert verdict["advance_to_next_tier"] is True

    # --- reproducibility: re-run produces same best_config ---
    out_dir2 = tmp_path / "out2"
    rc2 = main(
        [
            "--iter", "900-2026-05-06-T1a-letf-sweep",
            "--config", str(config_path),
            "--out-dir", str(out_dir2),
        ]
    )
    assert rc2 == 0
    verdict2 = json.loads((out_dir2 / "verdict.json").read_text())
    assert verdict2["best_config"] == verdict["best_config"], (
        "Non-deterministic: best_config changed between runs"
    )
    assert abs(verdict2["best_score"] - verdict["best_score"]) < 1e-9, (
        "Non-deterministic: best_score changed between runs"
    )


def test_t1a_unknown_asset_raises(tmp_path: Path) -> None:
    """Verify that an unknown on_asset raises a ValueError gracefully."""
    if not _TESTFOLIO_CACHE.exists():
        pytest.skip(_SKIP_REASON)

    from studies.letf_rotation_hunt.run_iter_t1 import _run_single_config
    from studies.letf_rotation_hunt.data_loader import load_ffr_daily

    ffr = load_ffr_daily()
    with pytest.raises(ValueError, match="No testfolio mapping for on_asset"):
        _run_single_config(
            {
                "name": "bad_asset",
                "on_asset": "UNKNOWNETF",
                "off_asset": "BIL",
                "signal": "sma",
                "period": 200,
            },
            ["lh_56y"],
            ffr,
        )


def test_t1a_unknown_signal_raises(tmp_path: Path) -> None:
    """Verify that an unknown signal name raises a ValueError gracefully."""
    if not _TESTFOLIO_CACHE.exists():
        pytest.skip(_SKIP_REASON)

    from studies.letf_rotation_hunt.run_iter_t1 import _run_single_config
    from studies.letf_rotation_hunt.data_loader import load_ffr_daily

    ffr = load_ffr_daily()
    with pytest.raises(ValueError, match="Unknown signal"):
        _run_single_config(
            {
                "name": "bad_signal",
                "on_asset": "UPRO",
                "off_asset": "BIL",
                "signal": "rsi",  # not implemented
                "period": 14,
            },
            ["lh_56y"],
            ffr,
        )


def test_t1a_ema_signal_works(tmp_path: Path) -> None:
    """Verify EMA signal variant runs without error."""
    if not _TESTFOLIO_CACHE.exists():
        pytest.skip(_SKIP_REASON)

    from studies.letf_rotation_hunt.run_iter_t1 import _run_single_config
    from studies.letf_rotation_hunt.data_loader import load_ffr_daily

    ffr = load_ffr_daily()
    result = _run_single_config(
        {
            "name": "upro_ema200_off_bil",
            "on_asset": "UPRO",
            "off_asset": "BIL",
            "signal": "ema",
            "period": 200,
        },
        ["lh_56y"],
        ffr,
    )
    assert "error" not in result
    assert result["metrics_gross"]["lh_56y"]["sharpe"] > 0


def test_t1a_soxl_tmf_synth_works(tmp_path: Path) -> None:
    """Verify SOXL (re-synthesised from QQQSIM) and TMF (from TLTSIM) run."""
    if not _TESTFOLIO_CACHE.exists():
        pytest.skip(_SKIP_REASON)

    from studies.letf_rotation_hunt.run_iter_t1 import _run_single_config
    from studies.letf_rotation_hunt.data_loader import load_ffr_daily

    ffr = load_ffr_daily()

    # SOXL re-synthesised from QQQSIM
    result_soxl = _run_single_config(
        {
            "name": "soxl_sma200_off_bil",
            "on_asset": "SOXL",
            "off_asset": "BIL",
            "signal": "sma",
            "period": 200,
        },
        ["lh_56y"],
        ffr,
    )
    assert "error" not in result_soxl, f"SOXL failed: {result_soxl.get('error')}"

    # TMF re-synthesised from TLTSIM
    result_tmf = _run_single_config(
        {
            "name": "tmf_sma200_off_bil",
            "on_asset": "TMF",
            "off_asset": "IEF",
            "signal": "sma",
            "period": 200,
        },
        ["lh_56y"],
        ffr,
    )
    assert "error" not in result_tmf, f"TMF failed: {result_tmf.get('error')}"
