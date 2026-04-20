"""Smoke tests for `ops darf` + `ops dividend` CLI."""
from typer.testing import CliRunner

from ops.cli.main import app

runner = CliRunner()
BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"


def _bcb(mock, date_str: str, value: str) -> None:
    mock.get(BCB_URL, json=[{"data": date_str, "valor": value}])


def test_darf_preview_no_trades(tmp_data_dir):
    result = runner.invoke(app, ["darf", "preview", "--regime", "monthly_6015"])
    assert result.exit_code == 0
    assert "nenhum DARF" in result.output


def test_darf_close_full_cycle_monthly(tmp_data_dir, requests_mock):
    _bcb(requests_mock, "01/04/2026", "5.0000")
    _bcb(requests_mock, "15/04/2026", "5.1000")
    r1 = runner.invoke(app, [
        "trade", "add", "--ticker", "SSO", "--side", "buy",
        "--qty", "10", "--price", "50", "--date", "2026-04-01",
    ])
    assert r1.exit_code == 0, r1.output
    r2 = runner.invoke(app, [
        "trade", "add", "--ticker", "SSO", "--side", "sell",
        "--qty", "10", "--price", "55", "--date", "2026-04-15",
    ])
    assert r2.exit_code == 0, r2.output
    r3 = runner.invoke(app, [
        "darf", "close", "--regime", "monthly_6015", "--period", "2026-04",
    ])
    assert r3.exit_code == 0, r3.output
    assert "DARF-M-202604" in r3.output
    r4 = runner.invoke(app, ["darf", "list"])
    assert "PENDING" in r4.output


def test_dividend_add_then_list(tmp_data_dir, requests_mock):
    _bcb(requests_mock, "15/06/2026", "5.2000")
    r1 = runner.invoke(app, [
        "dividend", "add", "--ticker", "SSO", "--gross-usd", "10",
        "--withheld-usd", "3", "--date", "2026-06-15",
    ])
    assert r1.exit_code == 0, r1.output
    assert "Dividend D-20260615-001" in r1.output
    r2 = runner.invoke(app, ["dividend", "list"])
    assert "SSO" in r2.output
