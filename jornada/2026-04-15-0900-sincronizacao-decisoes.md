# 2026-04-15 (manhã) — Sincronização geral + decisões de arquitetura

**O que aconteceu nessa sessão:**

1. **Diagnóstico pós-Runs 1-3.** Os três ciclos de backtest falham o
   gate DSR (0 de 24-30 configurações passam o p<0.05). Não é ruído —
   é "edge real mas insuficiente" dado o tamanho da amostra.
2. **Auditoria do Tiingo.** O bulk de ontem (22:05) terminou com 1660
   tickers em 145 MB de backup (`tiingo_backup_20260415-0958.tar.gz`).
   Decidido **manter a arquitetura atual** (parquet per-ticker +
   manifest JSON). Request-on-demand seria pior (latência + rate
   limits). Subscription do Tiingo Power fica ativa por +30 dias
   (até ~2026-05-15), depois cancela e roda offline do backup.
3. **Auditoria do knowledge base.** 33 livros é quantidade saudável.
   Gaps reais (Crypto 0 livros, Forex 0 livros) mas **não são
   blockers** agora — o foco da Phase 2.5 Run 4 é SPY (cobertura
   sobrando). Conflitos entre livros (ex.: Carver defende stop-loss
   discreto; Chan diz pra *nunca* usar stop em mean-reversion) são
   construtivos: escolas diferentes, não erro.
4. **Criação deste arquivo (`JORNADA.md`).** Pra sincronizar o usuário
   sem precisar ler `ROADMAP.md`/`specs/`. Instrução adicionada em
   `.claude/CLAUDE.md` pra manter atualizado a cada sessão.
5. **Próximo passo (ainda esta sessão):** implementar AFML rescue na
   Ehlers SPY. Código novo em
   `src/ai_trade/backtest/strategies/ehlers_meta.py` +
   `scripts/run_grid_ehlers_meta.py`. Meta: passar o DSR em ao menos
   1 configuração.

**Lembretes ativos:**
- ⏰ **~2026-05-15:** data-limite pra decidir se cancelamos Tiingo Power.
- 📧 **cTrader OAuth:** ainda aguardando aprovação da Spotware. Sem
  esse e-mail, Fase 1 continua bloqueada — por isso o foco segue em
  backtests.
- 📖 **Regra inalterada:** toda decisão técnica cita livro (`[slug, p.X]`).
