# Validation report — system 1407880

Generated: 2026-05-02T03:27:45+00:00
Elapsed: 0.0s

## Overall: ✅ PASS

- **Family:** `LATE_NY_BREAKOUT` (confidence 0.72)
- **Reliability score:** **0.730 (HIGH)**
- **Trades / pairs:** 3304 / 6
- **Last trade:** 2021-06-16 00:46:00+00:00
- **Account type:** Demo

## Pipeline status

- Pre-check: ✅ — 3304 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 SKIP — artifacts present
- Stage 2 (LLM family naming): ✅ — Stage 2 SKIP — signal_rule.md present

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.653 |
| family_clarity | 0.20 | 0.720 |
| timing_concentration | 0.20 | 1.000 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.024 |
| vendor_quality | 0.10 | 0.700 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/1407880/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/1407880/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/1407880/signal_rule.md`

