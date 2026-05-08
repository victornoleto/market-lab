# Validation report — system 10281851

Generated: 2026-05-02T05:03:35+00:00
Elapsed: 486.0s

## Overall: ✅ PASS

- **Family:** `OVERLAP_NY_LONDON_RANGE` (confidence 0.62)
- **Reliability score:** **0.782 (HIGH)**
- **Trades / pairs:** 652 / 1
- **Last trade:** 2026-04-30 11:04:07+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 652 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.620 |
| timing_concentration | 0.20 | 0.367 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.999 |
| vendor_quality | 0.10 | 0.850 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10281851/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10281851/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10281851/signal_rule.md`

