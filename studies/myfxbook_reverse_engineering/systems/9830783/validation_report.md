# Validation report — system 9830783

Generated: 2026-05-02T14:04:09+00:00
Elapsed: 1467.7s

## Overall: ✅ PASS

- **Family:** `OVERLAP_NY_LONDON_RANGE` (confidence 0.42)
- **Reliability score:** **0.547 (MEDIUM)**
- **Trades / pairs:** 4000 / 5
- **Last trade:** 2026-05-01 15:21:04+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 4000 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.241 |
| family_clarity | 0.20 | 0.420 |
| timing_concentration | 0.20 | 0.262 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.999 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/9830783/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/9830783/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/9830783/signal_rule.md`

