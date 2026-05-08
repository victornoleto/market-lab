# data/

This directory is for local market-data caches, manifests and small reference
files used by studies.

Generated datasets are intentionally gitignored:

- parquet/SQLite/cache files;
- Tiingo and testfolio downloads;
- raw external exports;
- backup archives.

Public commits should include only lightweight manifests or documentation needed
to regenerate the data.
