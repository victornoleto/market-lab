# Validation report — system 10251631

Generated: 2026-05-02T04:55:29+00:00
Elapsed: 594.0s

## Overall: ✅ PASS

- **Family:** `FACTOR_SCALPING` (confidence 0.38)
- **Reliability score:** **0.585 (MEDIUM)**
- **Trades / pairs:** 461 / 1
- **Last trade:** 2024-08-07 02:32:52+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 461 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.447 |
| family_clarity | 0.20 | 0.380 |
| timing_concentration | 0.20 | 0.536 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.653 |
| vendor_quality | 0.10 | 0.750 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10251631/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10251631/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10251631/signal_rule.md`

