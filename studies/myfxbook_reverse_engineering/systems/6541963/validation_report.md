# Validation report — system 6541963

Generated: 2026-05-02T10:34:45+00:00
Elapsed: 338.7s

## Overall: ✅ PASS

- **Family:** `FACTOR_SCALPING` (confidence 0.62)
- **Reliability score:** **0.760 (HIGH)**
- **Trades / pairs:** 2213 / 1
- **Last trade:** 2026-04-30 11:04:07+00:00
- **Account type:** Demo

## Pipeline status

- Pre-check: ✅ — 2213 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.620 |
| timing_concentration | 0.20 | 0.329 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.999 |
| vendor_quality | 0.10 | 0.700 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/6541963/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/6541963/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/6541963/signal_rule.md`

