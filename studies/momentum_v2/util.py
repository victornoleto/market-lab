"""Formatting and JSON-safety helpers (ported from momentum_13612 run.py)."""

from __future__ import annotations

import math

import numpy as np


def fmt_pct(value: float, digits: int = 2) -> str:
    if not math.isfinite(float(value)):
        return "n/a"
    return f"{100.0 * float(value):.{digits}f}%"


def fmt_num(value: float, digits: int = 3) -> str:
    if not math.isfinite(float(value)):
        return "n/a"
    return f"{float(value):.{digits}f}"


def safe_filename(value: str) -> str:
    """Return a conservative filename stem for generated plot artifacts."""
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)


def json_safe(value: object) -> object:
    """Convert non-finite numeric values to strict JSON-compatible nulls."""
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def md_value(value: object) -> str:
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float) and not math.isfinite(value):
        return "n/a"
    return str(value)


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._\n"
    header = "| " + " | ".join(columns) + " |"
    sep = "|" + "|".join("---" for _ in columns) + "|"
    body = [
        "| " + " | ".join(md_value(row.get(col, "")) for col in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, sep, *body]) + "\n"
