# Validation report — system 10192401

Generated: 2026-05-02T04:19:45+00:00
Elapsed: 543.8s

## Overall: ✅ PASS

- **Family:** `FACTOR_SCALPING` (confidence 0.52)
- **Reliability score:** **0.712 (HIGH)**
- **Trades / pairs:** 420 / 1
- **Last trade:** 2024-08-01 18:17:03+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 420 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.520 |
| timing_concentration | 0.20 | 0.338 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.650 |
| vendor_quality | 0.10 | 0.750 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10192401/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10192401/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10192401/signal_rule.md`

