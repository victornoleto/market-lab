"""End-to-end test: buys → sell → DARF close → status."""
from typer.testing import CliRunner

from ops.cli.main import app

runner = CliRunner()
BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"


def test_e2e_plano_b_two_buys_one_sell_monthly_darf(tmp_data_dir, requests_mock):
    """Simulate April 2026: buy SSO twice, sell 15 shares, close monthly DARF."""
    # All PTAX fetches mocked to fixed rate for simplicity
    requests_mock.get(BCB_URL, json=[{"data": "15/04/2026", "valor": "5.0"}])

    # Buy 1
    r = runner.invoke(app, [
        "trade", "add", "--ticker", "SSO", "--side", "buy",
        "--qty", "10", "--price", "50", "--date", "2026-04-05",
    ])
    assert r.exit_code == 0, r.output

    # Buy 2
    r = runner.invoke(app, [
        "trade", "add", "--ticker", "SSO", "--side", "buy",
        "--qty", "10", "--price", "55", "--date", "2026-04-10",
    ])
    assert r.exit_code == 0, r.output

    # Sell 15 shares at $60 (FIFO: 10 from B1 @ $50 + 5 from B2 @ $55)
    r = runner.invoke(app, [
        "trade", "add", "--ticker", "SSO", "--side", "sell",
        "--qty", "15", "--price", "60", "--date", "2026-04-20",
    ])
    assert r.exit_code == 0, r.output

    # Preview April DARF (monthly regime)
    r = runner.invoke(app, ["darf", "preview", "--regime", "monthly_6015",
                            "--date", "2026-04-15"])
    assert r.exit_code == 0
    assert "DARF-M-202604" in r.output
    assert "Tax due" in r.output

    # Close April DARF
    r = runner.invoke(app, ["darf", "close", "--regime", "monthly_6015",
                            "--period", "2026-04"])
    assert r.exit_code == 0
    assert "criado" in r.output

    # List shows pending DARF
    r = runner.invoke(app, ["darf", "list", "--unpaid"])
    assert "PENDING" in r.output

    # Status
    r = runner.invoke(app, ["status"])
    assert r.exit_code == 0
    assert "SSO" in r.output
