"""Smoke tests for `ops trade ...` CLI."""
from typer.testing import CliRunner

from ops.cli.main import app

runner = CliRunner()


def test_trade_add_buy(tmp_data_dir, requests_mock):
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados",
        json=[{"data": "20/04/2026", "valor": "5.1234"}],
    )
    result = runner.invoke(app, [
        "trade", "add",
        "--ticker", "SSO", "--side", "buy", "--qty", "10",
        "--price", "52.30", "--date", "2026-04-20",
    ])
    assert result.exit_code == 0, result.output
    assert "Trade T-20260420-001 registrado" in result.output
    assert "PTAX      : 5.1234" in result.output


def test_trade_list_empty(tmp_data_dir):
    result = runner.invoke(app, ["trade", "list"])
    assert result.exit_code == 0
    assert "(no trades)" in result.output


def test_trade_show_missing(tmp_data_dir):
    result = runner.invoke(app, ["trade", "show", "T-NOTEXIST-001"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_trade_add_then_list(tmp_data_dir, requests_mock):
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados",
        json=[{"data": "20/04/2026", "valor": "5.1234"}],
    )
    runner.invoke(app, [
        "trade", "add",
        "--ticker", "SSO", "--side", "buy", "--qty", "10",
        "--price", "52.30", "--date", "2026-04-20",
    ])
    result = runner.invoke(app, ["trade", "list"])
    assert result.exit_code == 0
    assert "T-20260420-001" in result.output
    assert "SSO" in result.output


def test_trade_add_invalid_qty(tmp_data_dir, requests_mock):
    """Bad --qty produces clean error, not traceback."""
    result = runner.invoke(app, [
        "trade", "add",
        "--ticker", "SSO", "--side", "buy", "--qty", "not_a_number",
        "--price", "52.30", "--date", "2026-04-20",
    ])
    assert result.exit_code == 1
    assert "--qty" in result.output
    assert "not_a_number" in result.output


def test_trade_add_invalid_date(tmp_data_dir, requests_mock):
    """Bad --date produces clean error."""
    result = runner.invoke(app, [
        "trade", "add",
        "--ticker", "SSO", "--side", "buy", "--qty", "10",
        "--price", "52", "--date", "not-a-date",
    ])
    assert result.exit_code == 1
    assert "--date" in result.output
