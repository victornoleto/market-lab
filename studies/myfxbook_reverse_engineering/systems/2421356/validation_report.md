# Validation report — system 2421356

Generated: 2026-05-02T09:30:47+00:00
Elapsed: 992.6s

## Overall: ✅ PASS

- **Family:** `FACTOR_SCALPING` (confidence 0.72)
- **Reliability score:** **0.784 (HIGH)**
- **Trades / pairs:** 1763 / 2
- **Last trade:** 2026-04-30 11:04:08+00:00
- **Account type:** Demo

## Pipeline status

- Pre-check: ✅ — 1763 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.720 |
| timing_concentration | 0.20 | 0.352 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.999 |
| vendor_quality | 0.10 | 0.700 |
| pair_coverage | 0.05 | 0.999 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/2421356/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/2421356/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/2421356/signal_rule.md`

