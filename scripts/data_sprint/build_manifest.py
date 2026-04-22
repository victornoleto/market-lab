"""Walk data/phase3_7/, compute sha256 + shape for each parquet/csv, write MANIFEST.json.

The parquets themselves are gitignored (per Phase 3.7-2 prompt §T4); the
MANIFEST lets future sessions verify they have the same data by hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _utils import DATA_DIR, setup_logger  # noqa: E402


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def describe(path: Path) -> dict:
    entry: dict = {
        "size_bytes": path.stat().st_size,
        "sha256": sha256_of(path),
    }
    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
        entry["n_rows"] = int(len(df))
        entry["n_cols"] = int(len(df.columns))
        entry["columns"] = list(df.columns)
        if hasattr(df.index, "min") and len(df):
            entry["index_first"] = str(df.index.min())
            entry["index_last"] = str(df.index.max())
            entry["index_monotonic_increasing"] = bool(df.index.is_monotonic_increasing)
            entry["index_duplicates"] = int(df.index.duplicated().sum())
    return entry


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--root", default=str(DATA_DIR))
    ap.add_argument("--output", default=str(DATA_DIR / "MANIFEST.json"))
    args = ap.parse_args()

    log = setup_logger("build_manifest")
    root = Path(args.root)
    manifest: dict = {}
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        if path.name == "MANIFEST.json":
            continue
        rel = str(path.relative_to(root))
        log.info("describing %s", rel)
        manifest[rel] = describe(path)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    log.info("wrote manifest %s (%d entries)", out, len(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
