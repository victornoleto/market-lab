# D2 Lead: EW UPRO+TQQQ com filtro MA — quase passou [SWING BROKER]

**Data:** 2026-04-21 (iter 3 do loop Phase 3.5d)
**Lead:** D2 — MA Regime Filter Homogêneo (Gayed canonical)
**Ticket:** EW_UPRO_TQQQ (50% UPRO + 50% TQQQ)
**Citações:** `[leverage_for_the_long_run, p.13, p.16, p.60]`

---

## O que testamos

Pegamos o portfólio **50% UPRO + 50% TQQQ** (os dois maiores 3× LETFs do
mercado) e aplicamos um filtro de tendência por cima: quando o SPY está
acima da sua média móvel, seguramos o UPRO; quando o QQQ está acima da sua,
seguramos o TQQQ. Quando qualquer um sai do regime de alta, a metade desse
ETF vai para um substituto defensivo.

Testamos 6 combinações:
- Média simples 200 dias (SMA200) ou exponencial 100 dias (EMA100)
- Substituto defensivo: caixa (zero rendimento), TMF (bonds 3×), ou GLD (ouro)

Janela: **2010-02-11 a 2026-04-17** (16.1 anos, Stage 1 + Stage 2 yfinance concordam).

---

## Resultados

| Config | CAGR_liq | Sharpe_liq | MaxDD | Calmar | WF | OOS Sharpe | FWD Sharpe |
|--------|----------|------------|-------|--------|----|------------|------------|
| sma200_cash | 21.7% | 0.680 | -51.0% | 0.502 | 7/8 | 1.141 | **-0.087** |
| ema100_cash | 19.9% | 0.650 | -47.0% | 0.498 | 7/8 | 1.106 | -0.341 |
| sma200_tmf  | 17.3% | 0.544 | -83.8% | 0.243 | 7/8 | 1.069 | +0.062 |
| ema100_tmf  | 16.0% | 0.522 | -82.3% | 0.229 | 6/8 | 0.882 | -0.098 |
| **sma200_gld** | **26.7%** | **0.773** | -56.3% | **0.559** | **7/8** | **1.276** | **+0.264** |
| ema100_gld  | 24.0% | 0.731 | -46.7% | 0.606 | 7/8 | 1.132 | -0.891 |

**SPY B&H líquido: 10.38%/ano.** Todas as configs superam por margem ampla.

---

## Diagnóstico — por que "quase"

O **sma200_gld** passou em 8 dos 9 gates:

| Gate | Resultado |
|------|-----------|
| PBO < 0.5 | ✓ 0.119 |
| DSR p < 0.05 | ✓ 0.011 |
| WF ≥ 6/8 | ✓ 7/8 |
| OOS hold-out Sharpe ≥ 0.5×IS | ✓ 1.276 (muito forte) |
| FWD stress (último trimestre) | ✓ +0.264 (positivo) |
| Beat SPY líquido | ✓ 26.7% vs 10.38% |
| Calmar > 0.5 | ✓ 0.559 |
| Sharpe líquido > 0.8 | **✗ 0.773** (falta 0.027) |

O filtro SMA200 reduz o MaxDD de 73.5% (buy-and-hold EW) para 56.3%, mas
o CAGR bruto cai de 36.2% para 31.5%. Resultado: Sharpe_net acaba em 0.773
— 0.027 abaixo do limiar de 0.8.

**Revelação importante:** TMF como off-leg é desastroso (MaxDD explode para
-83%!). Isso porque na janela 2022-2023, taxas subiram e TMF caiu 70%+.
Quando o regime de LETFs é "flat" (mercado em baixa), o TMF também estava
em queda — off-leg e portfólio principal sofrendo juntos. GLD como off-leg
é muito mais eficaz porque ouro tende a subir em crises.

---

## Cross-lib e Stage-2: replicação perfeita

Todos os 6 configs concordam entre pandas vectorizado e biblioteca `bt`:
| Config | ΔCAGR bt | ΔCAGR yfinance |
|--------|----------|---------------|
| sma200_gld | 0.58pp ✓ | 1.36pp ✓ |
| ema100_gld | 1.51pp ✓ | 1.36pp ✓ |
| sma200_cash | 0.54pp ✓ | 1.86pp ✓ |

(Limite do gate: ≤ 3pp — todos dentro.)

Isso diferencia Phase 3.5d da Phase 3.5b que falhou nesse teste.

---

## O que vem a seguir

- **Iter 4 — TQQQ single-leg:** TQQQ sozinho (sem UPRO) com filtro MA regime
  e off=GLD. TQQQ puro tem Sharpe 0.873 (D1); se o filtro MA reduzir o MaxDD
  sem derrubar muito o CAGR, pode passar o gate Sharpe_net > 0.8.
- **Iter 5 — UPRO single-leg:** similar, mas mais conservador (S&P 500 3×).
- **Aggregator D2 (iter 6):** consolidar todos 3 tickers, decidir PASS ou DEAD.

O sinal do `sma200_gld` é encorajador: FWD_Sharpe positivo em 2026 Q1 (período
de incerteza Trump + tarifas) indica que o filtro está funcionando mesmo agora.

Links:
- Relatório técnico: `reports/phase_3_5d/d2_ma_regime_gayed/EW_UPRO_TQQQ.md`
- Registry: `reports/phase_3_5d/d2_ma_regime_gayed/registry.json`
