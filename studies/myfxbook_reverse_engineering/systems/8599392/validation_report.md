# Validation report — system 8599392

Generated: 2026-05-02T13:19:27+00:00
Elapsed: 412.0s

## Overall: ✅ PASS

- **Family:** `FACTOR_SCALPING` (confidence 0.38)
- **Reliability score:** **0.300 (LOW)**
- **Trades / pairs:** 4000 / 6
- **Last trade:** 2026-05-01 15:18:18+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 4000 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.372 |
| family_clarity | 0.20 | 0.380 |
| timing_concentration | 0.20 | 0.265 |
| sanity_pass | 0.10 | 0.000 |
| age_freshness | 0.10 | 0.999 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- sanity FAIL — martingale signature detected
- forced LOW: martingale/grid signature

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/8599392/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/8599392/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/8599392/signal_rule.md`

