# Validation report — system 10563761

Generated: 2026-05-02T05:18:42+00:00
Elapsed: 536.8s

## Overall: ✅ PASS

- **Family:** `FACTOR_SCALPING` (confidence 0.55)
- **Reliability score:** **0.757 (HIGH)**
- **Trades / pairs:** 436 / 1
- **Last trade:** 2026-01-29 16:36:11+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 436 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.550 |
| timing_concentration | 0.20 | 0.385 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.949 |
| vendor_quality | 0.10 | 0.750 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10563761/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10563761/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10563761/signal_rule.md`

