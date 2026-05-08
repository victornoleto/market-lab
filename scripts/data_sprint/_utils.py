"""Shared helpers for Phase 3.7-2 data sprint ingestion scripts.

Purpose: keep each ingest_*.py script short and focused. This module has
env loading, logging setup (append to unified log file), retry-with-backoff,
and a tiny parquet-write helper that preserves canonical OHLCV columns.

Citation: CLAUDE.md "prefere log unificado em scripts longos" — unified log
at logs/phase3_7_data_sprint.log alongside per-script file logs.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data" / "phase3_7"
LOG_PATH = REPO_ROOT / "logs" / "phase3_7_data_sprint.log"


def load_env() -> None:
    env_file = REPO_ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        if k and k not in os.environ:
            os.environ[k] = v.strip().strip('"').strip("'")


def setup_logger(name: str) -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    fh = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


def retry(
    fn: Callable[[], T],
    *,
    attempts: int = 5,
    base_delay: float = 1.0,
    log: logging.Logger | None = None,
) -> T:
    last: BaseException | None = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:
            last = exc
            delay = base_delay * (2**i)
            if log:
                log.warning("retry %d/%d after %.1fs: %s", i + 1, attempts, delay, exc)
            time.sleep(delay)
    assert last is not None
    raise last
