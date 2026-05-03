# Validation report — system 10970107

Generated: 2026-05-02T06:00:58+00:00
Elapsed: 279.7s

## Overall: ✅ PASS

- **Family:** `MARTINGALE_GRID` (confidence 0.95)
- **Reliability score:** **0.300 (LOW)**
- **Trades / pairs:** 835 / 4
- **Last trade:** 2026-01-30 15:49:42+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 835 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.616 |
| family_clarity | 0.20 | 0.950 |
| timing_concentration | 0.20 | 0.825 |
| sanity_pass | 0.10 | 0.000 |
| age_freshness | 0.10 | 0.950 |
| vendor_quality | 0.10 | 0.850 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- sanity FAIL — martingale signature detected
- forced LOW: martingale/grid signature

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10970107/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10970107/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10970107/signal_rule.md`

