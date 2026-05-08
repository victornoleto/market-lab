# Validation report — system 10734338

Generated: 2026-05-02T05:47:29+00:00
Elapsed: 248.5s

## Overall: ✅ PASS

- **Family:** `FACTOR_SCALPING` (confidence 0.52)
- **Reliability score:** **0.734 (HIGH)**
- **Trades / pairs:** 591 / 1
- **Last trade:** 2026-05-01 15:33:53+00:00
- **Account type:** Demo

## Pipeline status

- Pre-check: ✅ — 591 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.520 |
| timing_concentration | 0.20 | 0.374 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 1.000 |
| vendor_quality | 0.10 | 0.550 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10734338/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10734338/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10734338/signal_rule.md`

