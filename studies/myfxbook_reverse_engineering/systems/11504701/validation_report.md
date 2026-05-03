# Validation report — system 11504701

Generated: 2026-05-02T06:34:42+00:00
Elapsed: 255.5s

## Overall: ✅ PASS

- **Family:** `MARTINGALE_GRID` (confidence 0.92)
- **Reliability score:** **0.300 (LOW)**
- **Trades / pairs:** 314 / 5
- **Last trade:** 2026-04-23 11:30:01+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 314 trades, pair coverage 99%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.705 |
| family_clarity | 0.20 | 0.920 |
| timing_concentration | 0.20 | 0.803 |
| sanity_pass | 0.10 | 0.000 |
| age_freshness | 0.10 | 0.995 |
| vendor_quality | 0.10 | 0.750 |
| pair_coverage | 0.05 | 0.994 |

## Notes

- sanity FAIL — martingale signature detected
- forced LOW: martingale/grid signature

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/11504701/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/11504701/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/11504701/signal_rule.md`

