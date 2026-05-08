# Validation report — system 8286716

Generated: 2026-05-02T11:36:37+00:00
Elapsed: 268.5s

## Overall: ✅ PASS

- **Family:** `UNCATEGORIZED` (confidence 0.35)
- **Reliability score:** **0.421 (LOW)**
- **Trades / pairs:** 1531 / 1
- **Last trade:** 2021-06-11 20:06:56+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 1531 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.145 |
| family_clarity | 0.20 | 0.350 |
| timing_concentration | 0.20 | 0.312 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.022 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- UNCATEGORIZED family demotes to LOW band

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/8286716/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/8286716/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/8286716/signal_rule.md`

