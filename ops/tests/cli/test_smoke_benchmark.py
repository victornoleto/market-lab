"""Smoke tests for ops benchmark + ops status."""
from typer.testing import CliRunner

from ops.cli.main import app

runner = CliRunner()


def test_status_empty(tmp_data_dir):
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "ops status" in result.output


def test_benchmark_report_no_data(tmp_data_dir):
    result = runner.invoke(app, ["benchmark", "report",
                                  "--year", "2026", "--month", "4"])
    assert result.exit_code == 0
    assert "No plano_b trades yet" in result.output
