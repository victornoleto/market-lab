# Validation report — system 11206045

Generated: 2026-05-02T06:21:48+00:00
Elapsed: 503.9s

## Overall: ✅ PASS

- **Family:** `LATE_NY_BREAKOUT` (confidence 0.50)
- **Reliability score:** **0.737 (HIGH)**
- **Trades / pairs:** 212 / 1
- **Last trade:** 2026-05-01 09:47:20+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 212 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.453 |
| family_clarity | 0.20 | 0.500 |
| timing_concentration | 0.20 | 0.995 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 1.000 |
| vendor_quality | 0.10 | 0.750 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/11206045/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/11206045/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/11206045/signal_rule.md`

