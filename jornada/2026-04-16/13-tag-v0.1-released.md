# Tag v0.1-phase-2.5-winners liberado: marco Phase 2.5 fechado

**Tag:** [RELEASE / GOVERNANCE] · commit `2e48880` (cleanup merge)

Fechamento oficial da Phase 2.5. A tag `v0.1-phase-2.5-winners` aponta
para `2e48880` — o merge do cleanup pós-winners em `main`. Todo o
repositório nesse ponto reproduz os 2 winners production-ready
(BollingerMR GARCH SPY 1h e ETF Rotation monthly top-1) com 345 testes
verdes e 16 books ativos no knowledge base.

A decisão GO/NO-GO por winner + correlação ρ=0.252 + cost-ablation com
swap real Pepperstone + 15% IR BR tax estão documentados em
[2026-04-16-1600-production-readiness-summary.md](2026-04-16-1600-production-readiness-summary.md).

A partir daqui o projeto entra em **Phase 3** (branch
`phase3/letf-and-multi-asset-20260416`): 5 leads derivados do
Investment Mandate, começando por Lead A1 (BollingerMR leverage sweep)
e Lead B1 (LETF rotation design from scratch base Gayed). Main fica
congelada como snapshot reprodutível; qualquer desenvolvimento novo
roda em feature branches.
