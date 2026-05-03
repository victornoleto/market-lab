# Validation report — system 11155858

Generated: 2026-05-02T06:06:27+00:00
Elapsed: 329.1s

## Overall: ✅ PASS

- **Family:** `FACTOR_SCALPING` (confidence 0.38)
- **Reliability score:** **0.801 (HIGH)**
- **Trades / pairs:** 197 / 1
- **Last trade:** 2026-04-23 12:36:35+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 197 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.380 |
| timing_concentration | 0.20 | 0.802 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.995 |
| vendor_quality | 0.10 | 0.650 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/11155858/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/11155858/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/11155858/signal_rule.md`

