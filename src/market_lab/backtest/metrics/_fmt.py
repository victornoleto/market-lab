"""Markdown formatting helpers shared by report generators.

Minimal primitives used by both single-result reports (``metrics/report.py``)
and grid reports (``grid/report.py``). Kept as a private module to avoid
pulling in optional deps like ``tabulate``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _fmt_pct(x: float, decimals: int = 2) -> str:
    """Format as percentage with ``decimals`` digits."""
    if not np.isfinite(x):
        return "∞" if x > 0 else "−∞"
    return f"{x * 100:.{decimals}f}%"


def _fmt_num(x: float, decimals: int = 2) -> str:
    if not np.isfinite(x):
        return "∞" if x > 0 else "−∞"
    return f"{x:.{decimals}f}"


def _dataframe_to_markdown(frame: pd.DataFrame) -> str:
    """Minimal GFM table writer — avoids pulling in the optional ``tabulate`` dep."""
    cols = list(frame.columns)
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    rows = [
        "| " + " | ".join(str(v) for v in row) + " |"
        for row in frame.itertuples(index=False, name=None)
    ]
    return "\n".join([header, sep, *rows])
