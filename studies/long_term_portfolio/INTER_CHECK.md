# Inter Internacional ETF Availability Check

**Date:** 2026-04-29  
**Purpose:** Verify deployability of all ETFs in the 7-finalist sweep (`SWEEP_PLAN_iter_027_to_039.md`) before scoring multi-criteria C7 Deploy ease.

**Hard rule (per spec §Phase 4 multi-criteria scoring)**: if ANY ETF in a finalist's composition is unavailable on Inter Internacional, that finalist's **C7 score = 0** (drags total ~15pts).

---

## How to fill

1. Log into Inter Internacional account.
2. Search each ticker below.
3. Mark `Inter available?` column with ✅ (available) or ❌ (not available).
4. Save and commit. **This is async — does not block iters 027-038 from running.** Required before Task 23 final report.

---

## Target ETFs

| Ticker | Used in finalists | Inter available? | AUM (approx) | TER | Notes |
|---|---|:---:|---:|---:|---|
| **NTSX** | F1, F3, F4, F6, F7 | ? | ~$1.7B | 0.20% | WisdomTree US 90/60 |
| **NTSD** | F4, F6 | ? | ~$1M | 0.35% | WisdomTree US+Intl 90/60, launched 2026-03-19 |
| **GDE** | F1, F2, F3, F4, F6, F7 | ? | ~$300M | 0.20% | WisdomTree S&P+Gold |
| **KMLM** | F1, F2, F3, F4, F5, F6, F7 | ? | ~$600M | 0.92% | KFA Mt Lucas MF |
| **DBMF** | iter 039 alt | ? | ~$3.2B | 0.85% | iMGP DBi MF (alternative for sleeve sensitivity) |
| **TLT** | all finalists | ? | ~$60B | 0.15% | iShares 20+y Treasury |
| **GLD** | F2, F5 | ? | ~$60B | 0.40% | SPDR Gold |
| **VTI** | F2, F5 | ? | ~$400B | 0.03% | Vanguard Total US |
| **VEA** | F5 | ? | ~$130B | 0.05% | Vanguard FTSE Developed |
| **VWO** | F5 | ? | ~$80B | 0.08% | Vanguard FTSE EM |
| **AVUV** | F2, F3, F5, F6 | ? | ~$11B | 0.25% | Avantis US SCV |
| **AVDV** | F5, F6 | ? | ~$8B | 0.36% | Avantis Intl SCV |
| **AVEM** | F5, F6 | ? | ~$1.5B | 0.33% | Avantis EM |
| **SPMO** | F2, F3, F5, F6 | ? | ~$5B | 0.13% | Invesco S&P 500 Momentum |
| **IDMO** | F5, F6 | ? | ~$1B | 0.25% | Invesco Intl Momentum |
| **RSST** | F7 | ? | ~$400M | 0.98% | Return Stacked US Stocks + MF |

---

## Finalist deploy ease summary (auto-derived from above when filled)

| Finalist | All ETFs available? | C7 score eligibility |
|---|:---:|:---:|
| F1 US-Stk (NTSX/GDE/KMLM/TLT) | ? | ? |
| F2 US-Fct (VTI/AVUV/SPMO/KMLM/TLT/GLD) | ? | ? |
| F3 US-Hyb (NTSX/GDE/KMLM/TLT/AVUV/SPMO) | ? | ? |
| F4 Gl-Stk (NTSX/NTSD/GDE/KMLM/TLT) | ? | ? |
| F5 Gl-Fct (VTI/VEA/VWO/AVUV/AVDV/AVEM/SPMO/IDMO/KMLM/TLT) | ? | ? |
| F6 Gl-Hyb (NTSX/NTSD/GDE/KMLM/TLT/AVUV/AVDV/AVEM/SPMO/IDMO) | ? | ? |
| F7 US-StkMF (NTSX/RSST/GDE/KMLM/TLT) | ? | ? |

A finalist with even ONE ❌ ETF in its components has C7=0 (~15pt drag on multi-criteria score).

---

## Citation

`SWEEP_PLAN_iter_027_to_039.md` §Risks/caveats — Deploy ease HARD GATE.
