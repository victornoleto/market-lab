# Frozen rules — read-only contract

Cópia congelada dos `signal_rule.md` produzidos pelo Stage 2 (Sonnet via `/decode-system <id>`) na rodada overnight 2026-05-01/02.

## Contrato

- **Read-only** (`chmod 444`). Não editar manualmente.
- Replicator-lite (Etapa 1) e frozen-rule cross-system (Etapa 2) leem **exclusivamente** desta pasta.
- Re-mining, re-fitting ou re-tuning de regras é **proibido** — qualquer ajuste invalida o pré-registro de `specs/replicator_lite_pre_reg.md`.
- Se uma regra estiver malformada (YAML inválido, thresholds ausentes), reportar fail no replicator-lite, não tentar consertar.

## Inventário

12 regras congeladas:

**Top-10 DECODED (Etapa 1)**:
- `10224499.md` — Happy Market Hours FM REAL (LATE_NY_BREAKOUT, 221 trades)
- `11171596.md` — Happy Algorithm PRO FM REAL SET1 (NY_SESSION_REVERSAL, 1083)
- `11155858.md` — Happy Brexit FM HR (FACTOR_SCALPING, 197)
- `8647517.md` — Happy Gold VTMarkets M30 (FACTOR_SCALPING, 1024)
- `2421356.md` — Happy Gold ICMarkets M30 (FACTOR_SCALPING, 1763, Demo)
- `10281851.md` — Happy Gold Eightcap M30 (OVERLAP_NY_LONDON_RANGE, 652)
- `9912554.md` — Happy Brexit FM REAL (OVERLAP_NY_LONDON_RANGE, 103, low_n)
- `11207608.md` — Happy Gold BBM (FACTOR_SCALPING, 202)
- `11628637.md` — Happy Bitcoin VM (FACTOR_SCALPING, 232)
- `9375654.md` — Happy Gold TMGM M30 (NY_SESSION_REVERSAL, 915)

**Etapa 2 — par primário (LATE_NY_BREAKOUT)**:
- `1407880.md` — OLD Happy Market Hours v2.3.1 (3304 trades, blackout 2021)
- (NEW) `10224499.md` — já listado acima

**Etapa 2 — par diagnóstico (Algorithm PRO)**:
- `2373850.md` — OLD Happy Algorithm PRO v1.4 SET1 (1691 trades, blackout)
- (NEW) `11171596.md` — já listado acima

## Notas

- `10224499.md` e `1407880.md` são o teste decisivo da Etapa 2 par primário. Mesma família independentemente classificada por Sonnet sem usar nome/vendor como feature.
- `2373850.md` e `11171596.md` divergem em família (UNCATEGORIZED vs NY_SESSION_REVERSAL). Par 2 é diagnóstico complementar; não derruba o estudo se falhar isolado.
