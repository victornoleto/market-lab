"""Carrega ``config/base.yaml`` com todas as premissas do estudo.

Diferente de outros estudos, aqui não há merge por universo: uma única
``base.yaml`` carrega taxas, spreads, IOF e tributos. Ver SPEC.md para as
fontes de cada número.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

STUDY_DIR = Path(__file__).resolve().parent
CONFIG_DIR = STUDY_DIR / "config"
BASE_CONFIG = CONFIG_DIR / "base.yaml"
OUTPUT_DIR = STUDY_DIR / "outputs"


def load_config(base_path: str | Path = BASE_CONFIG) -> dict[str, Any]:
    """Lê a YAML de premissas e devolve o dicionário validado."""
    cfg = yaml.safe_load(Path(base_path).read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        raise ValueError(f"config deve ser um mapping YAML: {base_path}")
    return cfg


def _as_date(value: Any, default: date) -> date:
    if value is None:
        return default
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def window(config: dict[str, Any], exposicao: str, *, today: date) -> tuple[date, date]:
    """Janela (início, fim) para uma exposição ('sp500' | 'mundo')."""
    janela = config.get("janela", {})
    chave = "inicio_sp500" if exposicao == "sp500" else "inicio_mundo"
    inicio = _as_date(janela.get(chave), date(2004, 1, 1))
    fim = _as_date(janela.get("fim"), today)
    return inicio, fim
