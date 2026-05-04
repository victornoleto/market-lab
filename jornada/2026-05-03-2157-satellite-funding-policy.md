# Funding do satellite AVUV/SPMO/FMTM/BTC

Testei no iter 054 a ideia de usar 25% em satellites: 10% AVUV / 5% SPMO / 5%
FMTM / 5% BTC. Como FMTM limita a janela comum a 2025-03-20 -> 2026-05-01, isto
nao e validacao permanente; e apenas comparacao de mecanica de funding.

No periodo curto, tirar tudo de ZROZ venceu em retorno/Sharpe: 38.77% CAGR /
-15.15% MDD / Sharpe 1.603. Mesmo assim, rejeitei como recomendacao estrutural
porque zera a convexidade de duration longa que protege o B4 em crashes.

Melhor compromisso sugerido: 15% NTSX / 25% GDE / 25% RSST / 10% ZROZ / 10% AVUV
/ 5% SPMO / 5% FMTM / 5% BTC. Ele preserva GDE e RSST inteiros, mantem 10% ZROZ
e financia os ativos de risco principalmente de NTSX + parte de ZROZ. No periodo
curto fez 34.97% / -14.21% / 1.553.

Alternativa mais conservadora: 20% NTSX / 20% GDE / 25% RSST / 10% ZROZ / 10%
AVUV / 5% SPMO / 5% FMTM / 5% BTC, com 32.99% / -14.15% / 1.518 no mesmo periodo.
