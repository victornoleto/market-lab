# Validation report — system 8599269

Generated: 2026-05-02T13:12:35+00:00
Elapsed: 226.2s

## Overall: ✅ PASS

- **Family:** `UNCATEGORIZED` (confidence 0.28)
- **Reliability score:** **0.300 (LOW)**
- **Trades / pairs:** 1123 / 1
- **Last trade:** 2026-04-29 21:44:22+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 1123 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.397 |
| family_clarity | 0.20 | 0.280 |
| timing_concentration | 0.20 | 0.230 |
| sanity_pass | 0.10 | 0.000 |
| age_freshness | 0.10 | 0.999 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- sanity FAIL — martingale signature detected
- forced LOW: martingale/grid signature
- UNCATEGORIZED family demotes to LOW band

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/8599269/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/8599269/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/8599269/signal_rule.md`

