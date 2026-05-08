# Validation report — system 7942220

Generated: 2026-05-02T11:32:09+00:00
Elapsed: 948.3s

## Overall: ✅ PASS

- **Family:** `MARTINGALE_GRID` (confidence 0.82)
- **Reliability score:** **0.300 (LOW)**
- **Trades / pairs:** 3910 / 25
- **Last trade:** 2021-06-16 21:40:37+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 3910 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.539 |
| family_clarity | 0.20 | 0.820 |
| timing_concentration | 0.20 | 0.651 |
| sanity_pass | 0.10 | 0.000 |
| age_freshness | 0.10 | 0.024 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- sanity FAIL — martingale signature detected
- forced LOW: martingale/grid signature

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/7942220/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/7942220/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/7942220/signal_rule.md`

