# Validation report — system 9607500

Generated: 2026-05-02T13:39:42+00:00
Elapsed: 645.1s

## Overall: ✅ PASS

- **Family:** `OVERLAP_NY_LONDON_RANGE` (confidence 0.48)
- **Reliability score:** **0.300 (LOW)**
- **Trades / pairs:** 1942 / 5
- **Last trade:** 2026-05-01 09:52:47+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 1942 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.480 |
| timing_concentration | 0.20 | 0.347 |
| sanity_pass | 0.10 | 0.000 |
| age_freshness | 0.10 | 0.999 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- sanity FAIL — martingale signature detected
- forced LOW: martingale/grid signature

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/9607500/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/9607500/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/9607500/signal_rule.md`

