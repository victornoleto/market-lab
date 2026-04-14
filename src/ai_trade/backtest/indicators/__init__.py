"""Ehlers DSP primitives for swing trading (Cycle Analytics / Rocket Science).

Each filter is a pure function over ``pandas.Series`` producing a new series
of the same length and index. Filters are stateful (IIR) — the first bars of
each output are warm-up transients. Rules of thumb from the book:

* Warm-up ≈ 2·period bars for SuperSmoother/HP (2-pole recursions).
* Combine HP + SuperSmoother = **roofing filter**, mandatory preprocessing
  before any Ehlers indicator [cycle_analytics, p.88-89, ch.7].

Primary references
------------------
* Ehlers, *Cycle Analytics for Traders*, 2013 — ``cycle_analytics``
* Ehlers, *Rocket Science for Traders*, 2001 — ``rocket_science``
"""
