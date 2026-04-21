"""Tests for reports module."""
from ops.core import reports


def test_status_dashboard_empty(tmp_data_dir):
    out = reports.render_status_dashboard()
    assert "ops status" in out
    assert "(none)" in out


def test_monthly_report_no_trades(tmp_data_dir):
    out = reports.render_monthly_benchmark_report(2026, 4)
    assert "No plano_b trades yet" in out
