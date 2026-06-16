"""Runner do estudo "Investir no Exterior — Brasil vs. Dólar".

Uso:
    uv run python -m studies.investir_exterior.run            # gera o relatório
    uv run python -m studies.investir_exterior.run --open     # gera e tenta abrir

Pipeline: carrega premissas (config/base.yaml) -> baixa/atualiza séries (yfinance,
com cache) -> simula custos/tributos -> gera outputs/relatorio.html (autossuficiente).
Não é estratégia de investimento; ver SPEC.md.
"""

from __future__ import annotations

import argparse
import logging
from datetime import date, datetime, timezone

from . import config as cfg
from . import data as D
from . import report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Comparação: investir no exterior pelo Brasil vs. dólar.")
    parser.add_argument("--config", default=str(cfg.BASE_CONFIG), help="caminho do base.yaml")
    parser.add_argument("--today", default=None, help="data de corte (YYYY-MM-DD); padrão = hoje")
    parser.add_argument("--format", choices=["html", "md", "all"], default="all",
                        help="quais relatórios gerar (padrão: all)")
    parser.add_argument("--open", action="store_true", help="abre o HTML no navegador ao final")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format="%(levelname)s %(name)s: %(message)s")

    today = date.fromisoformat(args.today) if args.today else datetime.now(timezone.utc).date()
    config = cfg.load_config(args.config)

    print("Baixando/atualizando séries (yfinance, com cache)...")
    bundle = D.build(config, today)
    for nome, e in bundle.exposicoes.items():
        print(f"  {nome:6s}: {e.index[0].date()} → {e.index[-1].date()} ({len(e.index)} pregões)")

    print("Simulando e gerando relatório(s)...")
    formats = ("html", "md") if args.format == "all" else (args.format,)
    outputs = report.generate_all(config, bundle, today, formats=formats)
    for fmt, path in outputs.items():
        print(f"OK [{fmt}] -> {path}")

    if args.open and "html" in outputs:
        import webbrowser
        webbrowser.open(outputs["html"].as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
