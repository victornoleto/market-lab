"""studies.lrs — Leveraged Rotation Strategies.

Clean restart of the SMA-regime + LETF rotation lineage previously explored
in :mod:`studies.letf_rotation_hunt` (closed) and
:mod:`studies.spy_leveraged_rotation_hunt` (bootstrap).

Phase-by-phase layout: each phase lives under ``phases/phase_N/`` with its
own runner, report, plots, and results. Generic glue (data wrapper, binary
rotation simulator, BR annual-tax model) lives under ``scripts/`` so later
phases can reuse without duplicating.

Discovery-only under Investment Mandate §1 — no deploy, no production capital.
"""
