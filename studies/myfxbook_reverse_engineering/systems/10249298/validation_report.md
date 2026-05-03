# Validation report — system 10249298

Generated: 2026-05-02T04:45:35+00:00
Elapsed: 439.1s

## Overall: ✅ PASS

- **Family:** `UNCATEGORIZED` (confidence 0.38)
- **Reliability score:** **0.674 (HIGH)**
- **Trades / pairs:** 280 / 1
- **Last trade:** 2026-04-29 21:45:21+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 280 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.543 |
| family_clarity | 0.20 | 0.380 |
| timing_concentration | 0.20 | 0.689 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.999 |
| vendor_quality | 0.10 | 0.750 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10249298/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10249298/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10249298/signal_rule.md`

