# Validation report — system 9841939

Generated: 2026-05-02T14:11:21+00:00
Elapsed: 431.8s

## Overall: ✅ PASS

- **Family:** `FACTOR_SCALPING` (confidence 0.38)
- **Reliability score:** **0.490 (MEDIUM)**
- **Trades / pairs:** 4000 / 1
- **Last trade:** 2026-05-01 09:51:51+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 4000 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.045 |
| family_clarity | 0.20 | 0.380 |
| timing_concentration | 0.20 | 0.266 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.999 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/9841939/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/9841939/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/9841939/signal_rule.md`

