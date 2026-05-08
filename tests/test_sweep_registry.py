"""Tests for market_lab.backtest.sweeps.registry.

Covers:

- schema v1 validation (happy path + every invariant violation)
- atomic_write + tmp→rename behavior (writer-crash safety)
- pop_pending / append_done / mark_errored state transitions
- advance_status state machine
- new_registry constructor round-trip

No network, no pandas — pure dict + I/O.
"""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict

import pytest

from market_lab.backtest.sweeps.registry import (
    SCHEMA_VERSION,
    RegistryValidationError,
    advance_status,
    append_done,
    atomic_write_registry,
    load_registry,
    mark_errored,
    new_registry,
    pop_pending,
    validate_schema_v1,
)


# ---------------------------------------------------------------------------
# Fixtures


def _valid_registry() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "phase": "phase3_5a",
        "lead_id": "T2",
        "lead_slug": "t2_donchian_breakout",
        "lead_title": "Donchian breakout 1h",
        "citations_seed": ["trading_systems_methods, p.353"],
        "started_at": "2026-04-18T00:00:00+00:00",
        "last_updated_at": "2026-04-18T00:00:00+00:00",
        "configs": [
            {
                "name": "donch_10_5_long",
                "type": "donchian",
                "entry_lookback": 10,
                "exit_lookback": 5,
            },
            {
                "name": "donch_20_10_long",
                "type": "donchian",
                "entry_lookback": 20,
                "exit_lookback": 10,
            },
        ],
        "tickers_pending": ["EURUSD", "GBPUSD", "USDJPY"],
        "tickers_done": [],
        "tickers_errored": [],
        "status": "pending",
        "aggregation_iter": None,
        "aggregate_file_md": None,
        "aggregate_jornada": None,
    }


def _done_entry(ticker: str) -> Dict[str, Any]:
    return {
        "ticker": ticker,
        "frequency": "1hour",
        "window_start": "2020-01-01",
        "window_end": "2026-04-17",
        "iter": 4,
        "n_configs_tested": 2,
        "best_config": "donch_20_10_long",
        "best_sharpe_oos": 0.42,
        "best_cagr": 0.08,
        "best_maxdd": -0.17,
        "any_pass_5gate": False,
        "median_hold_days": 2.1,
        "result_file_md": f"reports/phase3_5a/t2_donchian_breakout/{ticker}.md",
        "result_file_json": f"reports/phase3_5a/t2_donchian_breakout/{ticker}.json",
    }


# ---------------------------------------------------------------------------
# 1. Schema validation — happy path


def test_validate_schema_v1_accepts_canonical_registry() -> None:
    validate_schema_v1(_valid_registry())


def test_schema_version_constant_is_one() -> None:
    # Protects against silent bumps — schema changes need a migration.
    assert SCHEMA_VERSION == 1


# ---------------------------------------------------------------------------
# 2. Schema validation — invariant violations


@pytest.mark.parametrize(
    "field",
    ["schema_version", "phase", "lead_id", "lead_slug", "lead_title", "configs"],
)
def test_validate_missing_required_field_fails(field: str) -> None:
    reg = _valid_registry()
    del reg[field]
    with pytest.raises(RegistryValidationError, match=field):
        validate_schema_v1(reg)


def test_validate_wrong_schema_version_fails() -> None:
    reg = _valid_registry()
    reg["schema_version"] = 2
    with pytest.raises(RegistryValidationError, match="schema_version"):
        validate_schema_v1(reg)


def test_validate_rejects_empty_configs() -> None:
    reg = _valid_registry()
    reg["configs"] = []
    with pytest.raises(RegistryValidationError, match="configs"):
        validate_schema_v1(reg)


def test_validate_rejects_duplicate_config_names() -> None:
    reg = _valid_registry()
    reg["configs"].append(dict(reg["configs"][0]))  # duplicate
    with pytest.raises(RegistryValidationError, match="duplicate"):
        validate_schema_v1(reg)


def test_validate_rejects_overlap_pending_and_done() -> None:
    reg = _valid_registry()
    reg["tickers_done"] = [_done_entry("EURUSD")]
    # EURUSD also still in tickers_pending => invariant violation
    with pytest.raises(RegistryValidationError, match="overlap"):
        validate_schema_v1(reg)


def test_validate_rejects_duplicate_entries_in_done() -> None:
    reg = _valid_registry()
    reg["tickers_pending"] = []  # clear to avoid the overlap check firing first
    reg["tickers_done"] = [_done_entry("EURUSD"), _done_entry("EURUSD")]
    with pytest.raises(RegistryValidationError, match="duplicate"):
        validate_schema_v1(reg)


def test_validate_rejects_unknown_status() -> None:
    reg = _valid_registry()
    reg["status"] = "weird"
    with pytest.raises(RegistryValidationError, match="status"):
        validate_schema_v1(reg)


def test_validate_done_status_requires_aggregate_file() -> None:
    reg = _valid_registry()
    reg["tickers_pending"] = []
    reg["tickers_done"] = [_done_entry("EURUSD")]
    reg["status"] = "done"
    with pytest.raises(RegistryValidationError, match="aggregate_file_md"):
        validate_schema_v1(reg)


def test_validate_aggregating_requires_empty_pending() -> None:
    reg = _valid_registry()
    reg["status"] = "aggregating"
    # pending still has 3 tickers => invalid
    with pytest.raises(RegistryValidationError, match="aggregating"):
        validate_schema_v1(reg)


# ---------------------------------------------------------------------------
# 3. Atomic write + round-trip


def test_atomic_write_and_load_round_trip(tmp_path: Path) -> None:
    reg = _valid_registry()
    path = tmp_path / "registry.json"
    atomic_write_registry(path, reg)
    loaded = load_registry(path)
    assert loaded == reg


def test_atomic_write_rejects_invalid_registry(tmp_path: Path) -> None:
    reg = _valid_registry()
    reg["schema_version"] = 99
    path = tmp_path / "registry.json"
    with pytest.raises(RegistryValidationError):
        atomic_write_registry(path, reg)
    # The target file must NOT have been created.
    assert not path.exists()


def test_atomic_write_leaves_no_tmp_files_on_success(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    atomic_write_registry(path, _valid_registry())
    remaining = sorted(os.listdir(tmp_path))
    assert remaining == ["registry.json"]


def test_load_registry_rejects_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(RegistryValidationError, match="JSON"):
        load_registry(path)


def test_load_registry_rejects_old_schema(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    bad = _valid_registry()
    bad["schema_version"] = 0
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(RegistryValidationError, match="schema_version"):
        load_registry(path)


def test_atomic_write_concurrent_writers_never_tear(tmp_path: Path) -> None:
    """Two threads racing to write different registries must leave the
    file in exactly one consistent state — not a half-written mix."""
    path = tmp_path / "registry.json"
    reg_a = _valid_registry()
    reg_b = _valid_registry()
    reg_b["lead_id"] = "T3"  # distinguishable payload
    reg_b["lead_slug"] = "t3_pairs_stat_arb"
    reg_b["lead_title"] = "Stat-arb pairs"

    # Seed the file so readers always see something valid.
    atomic_write_registry(path, reg_a)

    errors: list[BaseException] = []
    barrier = threading.Barrier(2)

    def writer(payload: Dict[str, Any]) -> None:
        try:
            barrier.wait(timeout=2.0)
            for _ in range(20):
                atomic_write_registry(path, payload)
                time.sleep(0.001)
        except BaseException as exc:  # pragma: no cover — surfaced via asserts
            errors.append(exc)

    ta = threading.Thread(target=writer, args=(reg_a,))
    tb = threading.Thread(target=writer, args=(reg_b,))
    ta.start()
    tb.start()

    # Concurrent reader: must always see a valid registry.
    reader_errors: list[BaseException] = []
    for _ in range(40):
        try:
            load_registry(path)
        except (FileNotFoundError, RegistryValidationError) as exc:
            reader_errors.append(exc)
        time.sleep(0.001)

    ta.join()
    tb.join()

    assert not errors, f"writer errors: {errors}"
    assert not reader_errors, f"reader saw torn state: {reader_errors}"
    # Final file must be one of the two known payloads — never a hybrid.
    final = load_registry(path)
    assert final["lead_id"] in {"T2", "T3"}


# ---------------------------------------------------------------------------
# 4. Mutations: pop_pending / append_done / mark_errored


def test_pop_pending_removes_head_and_leaves_original_untouched() -> None:
    reg = _valid_registry()
    ticker, new = pop_pending(reg)
    assert ticker == "EURUSD"
    assert new["tickers_pending"] == ["GBPUSD", "USDJPY"]
    # Original dict must be unchanged (no accidental aliasing).
    assert reg["tickers_pending"] == ["EURUSD", "GBPUSD", "USDJPY"]


def test_pop_pending_raises_on_empty() -> None:
    reg = _valid_registry()
    reg["tickers_pending"] = []
    reg["status"] = "aggregating"  # keep validator happy
    with pytest.raises(RegistryValidationError, match="empty"):
        pop_pending(reg)


def test_append_done_adds_entry_and_preserves_append_only() -> None:
    reg = _valid_registry()
    # Simulate a sweep iter: first pop EURUSD, then record it done.
    _ticker, reg2 = pop_pending(reg)
    reg3 = append_done(reg2, _done_entry("EURUSD"))
    assert [entry["ticker"] for entry in reg3["tickers_done"]] == ["EURUSD"]
    # Re-appending the same ticker must fail.
    with pytest.raises(RegistryValidationError, match="append-only"):
        append_done(reg3, _done_entry("EURUSD"))


def test_append_done_requires_minimum_fields() -> None:
    reg = _valid_registry()
    _ticker, reg2 = pop_pending(reg)
    with pytest.raises(RegistryValidationError, match="required"):
        append_done(reg2, {"ticker": "EURUSD"})  # missing iter / best_config / etc


def test_mark_errored_moves_ticker_from_pending_to_errored() -> None:
    reg = _valid_registry()
    new = mark_errored(reg, "GBPUSD", "data missing", iter_num=5)
    assert "GBPUSD" not in new["tickers_pending"]
    assert new["tickers_pending"] == ["EURUSD", "USDJPY"]
    assert new["tickers_errored"] == [
        {"ticker": "GBPUSD", "iter": 5, "error_msg": "data missing"}
    ]


def test_mark_errored_rejects_unknown_ticker() -> None:
    reg = _valid_registry()
    with pytest.raises(RegistryValidationError, match="not in tickers_pending"):
        mark_errored(reg, "ZZZZZZ", "unknown", iter_num=1)


# ---------------------------------------------------------------------------
# 5. Status state machine


def test_advance_status_pending_with_done_goes_to_sweeping() -> None:
    reg = _valid_registry()
    _ticker, reg = pop_pending(reg)
    reg = append_done(reg, _done_entry("EURUSD"))
    reg = advance_status(reg)
    assert reg["status"] == "sweeping"


def test_advance_status_sweeping_with_empty_pending_goes_to_aggregating() -> None:
    reg = _valid_registry()
    # Drain all pending tickers; record each as done.
    tickers = list(reg["tickers_pending"])
    for t in tickers:
        _popped, reg = pop_pending(reg)
        assert _popped == t
        reg = append_done(reg, _done_entry(t))
        reg = advance_status(reg)  # pending->sweeping after first, then stays
    # Last advance should flip sweeping -> aggregating.
    assert reg["status"] == "aggregating"
    assert reg["tickers_pending"] == []
    assert [e["ticker"] for e in reg["tickers_done"]] == tickers


def test_advance_status_done_is_noop() -> None:
    reg = _valid_registry()
    reg["tickers_pending"] = []
    reg["tickers_done"] = [_done_entry("EURUSD")]
    reg["status"] = "done"
    reg["aggregate_file_md"] = "reports/phase3_5a/t2/AGGREGATE.md"
    advanced = advance_status(reg)
    assert advanced["status"] == "done"


# ---------------------------------------------------------------------------
# 6. Constructor


def test_new_registry_round_trip(tmp_path: Path) -> None:
    reg = new_registry(
        phase="phase3_5a",
        lead_id="T4",
        lead_slug="t4_session_breakout",
        lead_title="London-open breakout",
        configs=[{"name": "london_30m", "type": "session"}],
        tickers_pending=["EURUSD", "GBPUSD"],
        citations_seed=["quant_trading_chan, ch.3"],
    )
    assert reg["status"] == "pending"
    assert reg["tickers_done"] == []
    path = tmp_path / "registry.json"
    atomic_write_registry(path, reg)
    loaded = load_registry(path)
    assert loaded["lead_id"] == "T4"
