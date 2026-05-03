# Validation report — system 6603448

Generated: 2026-05-02T10:39:28+00:00
Elapsed: 282.5s

## Overall: ✅ PASS

- **Family:** `MARTINGALE_GRID` (confidence 0.72)
- **Reliability score:** **0.300 (LOW)**
- **Trades / pairs:** 920 / 3
- **Last trade:** 2021-06-11 20:08:14+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 920 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.104 |
| family_clarity | 0.20 | 0.720 |
| timing_concentration | 0.20 | 0.280 |
| sanity_pass | 0.10 | 0.000 |
| age_freshness | 0.10 | 0.022 |
| vendor_quality | 0.10 | 0.850 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- sanity FAIL — martingale signature detected
- forced LOW: martingale/grid signature

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/6603448/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/6603448/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/6603448/signal_rule.md`

