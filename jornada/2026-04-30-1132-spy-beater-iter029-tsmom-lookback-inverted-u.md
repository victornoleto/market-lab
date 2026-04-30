# spy_beater_hunt iter 029 — testando se mudar o "tempo de memória" do gate ajuda

Hoje rodei a iteração 29 do hunt. Já tinha gastado 28 das 50 iterações, e a última iteração interessante (iter 028) provou que **a posição em que cada peça aparece no portfólio não muda nada no score** — só importa o conjunto de peças e os pesos. Sobrou então uma única direção não-explorada: variar o **lookback** (janela de tempo) do gate de momentum.

Contexto: o gate "TSMOM-6m" decide se o portfólio fica em alavancagem ou em renda fixa, baseado no retorno acumulado dos últimos 6 meses. A literatura canônica (Moskowitz-Ooi-Pedersen 2012) usa 12 meses como referência primária; Faber GTAA usa 10 meses. Será que mudar de 6m para 12m ou 3m abre alguma janela de melhora?

**Resultado: 69/100 PROMISING**, mesmo tier de iter 028 mas levemente abaixo do teto histórico de 71. O config selecionado (E2 TSMOM-12m, 20% peso) tem o **melhor CAGR médio do hunt inteiro até agora — 16.23%**, mas perdeu 1 gate em cada dataset porque o lookback de 12 meses **demora mais a sair de regimes negativos**. O walk-forward gate (G3) puniu drawdowns por janela acima de 25% (12m: 30-32%; 6m baseline: < 25%).

**Achado novo**: a relação lookback × score forma um U-invertido com pico em ~6m. Mais curto (3m) é volátil demais (gate fica ligando/desligando); mais longo (12m) atrasa as saídas. **E uma decoupling crítica** que vou guardar como 7ª classe de saturação do rubric: métricas full-period (Sharpe, CAGR, MDD acumulado) podem **melhorar** mesmo quando métricas por-janela do gate-axis **pioram** — porque o full-period agrega regimes em uma média ponderada por compounding, enquanto o gate olha cada janela em isolamento.

Continuo recomendando fechar o hunt aqui. F1+SPLIT segue como deploy fallback, mandate §1 100% Plano C inalterado.
