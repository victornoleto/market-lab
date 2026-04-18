"""Fan-out sweep registry.

One JSON file per sweep lead (``reports/<phase>/<lead_slug>/registry.json``)
tracks which tickers are pending, which are done, and what the aggregate
state machine looks like. The self-improve loop agent mutates it one
ticker at a time in SWEEP_MODE=fanout, with atomic writes so a timeout
mid-iter never corrupts the file.

See:

- ``specs/self_improve_fanout_mode.md`` — rationale and full spec.
- ``docs/self_improvement/fanout_protocol.md`` — agent handbook,
  including the exact on-disk schema.

The public surface is intentionally small so agents can reason about it
in a single prompt turn:

- ``load_registry`` / ``validate_schema_v1`` — read + check.
- ``atomic_write_registry`` — tmp→rename so readers never see a half
  file.
- ``pop_pending`` / ``append_done`` / ``mark_errored`` — the three
  legal state transitions inside a sweep iter.
- ``advance_status`` — helper for the status state machine.

Everything else (iter numbering, per-ticker file generation, commit
messages) is the caller's responsibility. We do not import pandas or
anything heavy here — this module is I/O + dict munging.
"""

from __future__ import annotations

import copy
import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

SCHEMA_VERSION = 1

_ALLOWED_STATUSES = frozenset({"pending", "sweeping", "aggregating", "done"})


class RegistryValidationError(ValueError):
    """Raised when a registry dict fails schema v1 validation."""


# ---------------------------------------------------------------------------
# Read / write


def load_registry(path: str | os.PathLike[str]) -> Dict[str, Any]:
    """Load the JSON registry at ``path`` and validate schema v1.

    Raises
    ------
    FileNotFoundError
        If the path does not exist.
    RegistryValidationError
        If the JSON is malformed or fails schema v1.
    """
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as exc:
            raise RegistryValidationError(
                f"registry at {path} is not valid JSON: {exc}"
            ) from exc
    validate_schema_v1(data)
    return data


def atomic_write_registry(
    path: str | os.PathLike[str], registry: Mapping[str, Any]
) -> None:
    """Atomically replace the file at ``path`` with the given registry.

    The file is written to a sibling ``.tmp`` file first (same directory,
    so rename is atomic on POSIX), fsynced, then renamed. Readers either
    see the old file or the fully-written new file — never a torn write.

    Validates the payload before touching disk so we never produce an
    invalid registry.
    """
    validate_schema_v1(registry)
    target = os.fspath(path)
    parent = os.path.dirname(target) or "."
    os.makedirs(parent, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        prefix=os.path.basename(target) + ".",
        suffix=".tmp",
        dir=parent,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, sort_keys=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, target)
    except Exception:
        # Best-effort cleanup; re-raise the original error.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Validation


def validate_schema_v1(registry: Mapping[str, Any]) -> None:
    """Validate a registry dict against schema v1.

    This is stricter than JSON-schema: we enforce invariants that matter
    for the state machine (no overlap between ``tickers_pending`` and
    ``tickers_done``, append-only uniqueness in ``tickers_done``, etc).

    Raises
    ------
    RegistryValidationError
        With a human-readable message pointing at the first invariant
        violation.
    """
    if not isinstance(registry, Mapping):
        raise RegistryValidationError(
            f"registry must be a mapping, got {type(registry).__name__}"
        )

    _require(registry, "schema_version", int)
    if registry["schema_version"] != SCHEMA_VERSION:
        raise RegistryValidationError(
            f"schema_version must be {SCHEMA_VERSION}, got {registry['schema_version']!r}"
        )

    _require_non_empty_str(registry, "phase")
    _require_non_empty_str(registry, "lead_id")
    _require_non_empty_str(registry, "lead_slug")
    _require_non_empty_str(registry, "lead_title")

    _require(registry, "citations_seed", list)
    _require(registry, "started_at", str)
    _require(registry, "last_updated_at", str)

    configs = registry.get("configs")
    if not isinstance(configs, list) or not configs:
        raise RegistryValidationError("configs must be a non-empty list")
    seen_names: set[str] = set()
    for i, cfg in enumerate(configs):
        if not isinstance(cfg, Mapping):
            raise RegistryValidationError(
                f"configs[{i}] must be a mapping, got {type(cfg).__name__}"
            )
        for field in ("name", "type"):
            if not isinstance(cfg.get(field), str) or not cfg[field]:
                raise RegistryValidationError(
                    f"configs[{i}].{field} must be a non-empty string"
                )
        if cfg["name"] in seen_names:
            raise RegistryValidationError(
                f"configs contains duplicate name {cfg['name']!r}"
            )
        seen_names.add(cfg["name"])

    pending = registry.get("tickers_pending")
    done = registry.get("tickers_done")
    errored = registry.get("tickers_errored", [])
    if not isinstance(pending, list):
        raise RegistryValidationError("tickers_pending must be a list")
    if not isinstance(done, list):
        raise RegistryValidationError("tickers_done must be a list")
    if not isinstance(errored, list):
        raise RegistryValidationError("tickers_errored must be a list")

    for i, t in enumerate(pending):
        if not isinstance(t, str) or not t:
            raise RegistryValidationError(
                f"tickers_pending[{i}] must be a non-empty string"
            )

    done_tickers: List[str] = []
    for i, entry in enumerate(done):
        if not isinstance(entry, Mapping):
            raise RegistryValidationError(
                f"tickers_done[{i}] must be a mapping"
            )
        ticker = entry.get("ticker")
        if not isinstance(ticker, str) or not ticker:
            raise RegistryValidationError(
                f"tickers_done[{i}].ticker must be a non-empty string"
            )
        done_tickers.append(ticker)

    # Uniqueness within tickers_done (append-only invariant).
    if len(set(done_tickers)) != len(done_tickers):
        raise RegistryValidationError(
            "tickers_done contains duplicate ticker entries (must be append-only unique)"
        )

    # Disjointness between pending and done.
    overlap = set(pending) & set(done_tickers)
    if overlap:
        raise RegistryValidationError(
            f"tickers_pending and tickers_done overlap: {sorted(overlap)}"
        )

    status = registry.get("status")
    if status not in _ALLOWED_STATUSES:
        raise RegistryValidationError(
            f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {status!r}"
        )

    # status-specific consistency.
    if status == "done":
        if not registry.get("aggregate_file_md"):
            raise RegistryValidationError(
                "status=done requires aggregate_file_md to be set"
            )
    if status == "aggregating" and pending:
        raise RegistryValidationError(
            "status=aggregating requires tickers_pending to be empty"
        )
    if status == "sweeping" and not done_tickers:
        # "sweeping" means at least one ticker done; spec §5 allows
        # "pending" to still be the status after bootstrap even though
        # this helper also accepts "sweeping" as the first-ticker status.
        # We tolerate sweeping with empty done only when pending is also
        # empty (pathological but not corrupt in isolation).
        pass  # leniency — exact state machine enforcement lives in the agent


# ---------------------------------------------------------------------------
# Mutations (return a new dict; never mutate caller's input)


def pop_pending(registry: Mapping[str, Any]) -> tuple[str, Dict[str, Any]]:
    """Remove and return the first pending ticker plus an updated registry.

    Returns
    -------
    (ticker, new_registry)
        ``ticker`` is ``registry.tickers_pending[0]``.
        ``new_registry`` is a deep copy with that ticker removed from
        ``tickers_pending`` and ``last_updated_at`` refreshed. Status is
        **not** advanced here — the caller decides whether to move to
        ``sweeping`` / ``aggregating`` after writing the per-ticker files.

    Raises
    ------
    RegistryValidationError
        If the registry is invalid or ``tickers_pending`` is empty.
    """
    validate_schema_v1(registry)
    pending = list(registry["tickers_pending"])
    if not pending:
        raise RegistryValidationError(
            "pop_pending called with empty tickers_pending"
        )
    new = copy.deepcopy(dict(registry))
    ticker = pending.pop(0)
    new["tickers_pending"] = pending
    new["last_updated_at"] = _now_iso()
    return ticker, new


def append_done(
    registry: Mapping[str, Any], summary: Mapping[str, Any]
) -> Dict[str, Any]:
    """Append a ticker summary to ``tickers_done``.

    The summary is validated against a minimal required-field list (full
    schema is in the fan-out protocol doc). The returned registry is a
    deep copy; the input is unchanged.

    If the summary's ticker is already in ``tickers_done``, raises — the
    registry is append-only.
    """
    validate_schema_v1(registry)
    if not isinstance(summary, Mapping):
        raise RegistryValidationError("summary must be a mapping")
    required = ("ticker", "iter", "best_config", "result_file_md", "result_file_json")
    for field in required:
        if field not in summary:
            raise RegistryValidationError(
                f"summary missing required field {field!r}"
            )
    ticker = summary["ticker"]
    if not isinstance(ticker, str) or not ticker:
        raise RegistryValidationError("summary.ticker must be a non-empty string")

    done_tickers = {entry["ticker"] for entry in registry["tickers_done"]}
    if ticker in done_tickers:
        raise RegistryValidationError(
            f"ticker {ticker!r} already in tickers_done (append-only)"
        )

    new = copy.deepcopy(dict(registry))
    new["tickers_done"] = list(new["tickers_done"]) + [dict(summary)]
    new["last_updated_at"] = _now_iso()
    return new


def mark_errored(
    registry: Mapping[str, Any],
    ticker: str,
    error_msg: str,
    iter_num: int,
) -> Dict[str, Any]:
    """Record a ticker-level failure in ``tickers_errored`` and pop it
    from ``tickers_pending``.

    This is used when the backtest raises, data is missing, or the
    sweep produces obviously corrupt output for a specific ticker. The
    aggregator decides later whether to manually re-queue.
    """
    validate_schema_v1(registry)
    if not isinstance(ticker, str) or not ticker:
        raise RegistryValidationError("ticker must be a non-empty string")
    if ticker not in registry["tickers_pending"]:
        raise RegistryValidationError(
            f"ticker {ticker!r} not in tickers_pending"
        )

    new = copy.deepcopy(dict(registry))
    new["tickers_pending"] = [t for t in new["tickers_pending"] if t != ticker]
    new["tickers_errored"] = list(new.get("tickers_errored", [])) + [
        {"ticker": ticker, "iter": int(iter_num), "error_msg": str(error_msg)}
    ]
    new["last_updated_at"] = _now_iso()
    return new


def advance_status(registry: Mapping[str, Any]) -> Dict[str, Any]:
    """Advance the status field based on the current pending/done lists.

    Transition rules (from spec §3):

    - ``pending`` + any ``tickers_done`` → ``sweeping``
    - ``sweeping`` + empty ``tickers_pending`` → ``aggregating``
    - any other state → unchanged

    The caller is still responsible for flipping to ``done`` after the
    aggregator runs (requires ``aggregate_file_md``), via
    ``atomic_write_registry`` directly.
    """
    validate_schema_v1(registry)
    new = copy.deepcopy(dict(registry))
    status = new["status"]
    if status == "pending" and new["tickers_done"]:
        new["status"] = "sweeping"
    if new["status"] == "sweeping" and not new["tickers_pending"]:
        new["status"] = "aggregating"
    if status != new["status"]:
        new["last_updated_at"] = _now_iso()
    return new


# ---------------------------------------------------------------------------
# Constructors (helpers for bootstrap)


def new_registry(
    *,
    phase: str,
    lead_id: str,
    lead_slug: str,
    lead_title: str,
    configs: List[Mapping[str, Any]],
    tickers_pending: List[str],
    citations_seed: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a fresh schema-v1 registry in ``pending`` status.

    Convenience for the bootstrap iter — the agent can also build the
    dict by hand if it needs fields this helper doesn't expose. The
    output is validated before return.
    """
    now = _now_iso()
    reg = {
        "schema_version": SCHEMA_VERSION,
        "phase": phase,
        "lead_id": lead_id,
        "lead_slug": lead_slug,
        "lead_title": lead_title,
        "citations_seed": list(citations_seed or []),
        "started_at": now,
        "last_updated_at": now,
        "configs": [dict(c) for c in configs],
        "tickers_pending": list(tickers_pending),
        "tickers_done": [],
        "tickers_errored": [],
        "status": "pending",
        "aggregation_iter": None,
        "aggregate_file_md": None,
        "aggregate_jornada": None,
    }
    validate_schema_v1(reg)
    return reg


# ---------------------------------------------------------------------------
# Internal helpers


def _require(mapping: Mapping[str, Any], field: str, expected_type: type) -> None:
    if field not in mapping:
        raise RegistryValidationError(f"missing required field {field!r}")
    if not isinstance(mapping[field], expected_type):
        raise RegistryValidationError(
            f"field {field!r} must be {expected_type.__name__}, "
            f"got {type(mapping[field]).__name__}"
        )


def _require_non_empty_str(mapping: Mapping[str, Any], field: str) -> None:
    _require(mapping, field, str)
    if not mapping[field]:
        raise RegistryValidationError(f"field {field!r} must be non-empty")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
