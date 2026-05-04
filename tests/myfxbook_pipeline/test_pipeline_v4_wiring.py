from __future__ import annotations

import json

import pandas as pd

from studies.myfxbook_reverse_engineering.scripts import run_replicator_batch
from studies.myfxbook_reverse_engineering.shared.pre_decode_screen import PreScreenResult
from studies.myfxbook_reverse_engineering.workbench import pipeline


def test_parse_args_accepts_system_id_alias_and_flags() -> None:
    args = pipeline.parse_args(
        [
            "--system-id",
            "1407880",
            "--enable-pre-screen",
            "--enable-adversarial",
            "--out-dir",
            "/tmp/v4_smoke_1407880",
        ]
    )

    assert args.account_oid == "1407880"
    assert args.enable_pre_screen is True
    assert args.enable_adversarial is True
    assert args.out_dir == "/tmp/v4_smoke_1407880"


def test_batch_parse_args_accepts_fase1_flags() -> None:
    args = run_replicator_batch._parse_args(
        ["--only", "1407880", "--enable-pre-screen", "--enable-adversarial"]
    )

    assert args.only == ["1407880"]
    assert args.enable_pre_screen is True
    assert args.enable_adversarial is True


def test_pre_screen_stop_aborts_without_extra_flag(monkeypatch, tmp_path) -> None:
    trades = pd.DataFrame({"is_trade": [True], "pips": [1.0]})
    args = pipeline.parse_args(
        [
            "--system-id",
            "11504701",
            "--enable-pre-screen",
            "--out-dir",
            str(tmp_path),
        ]
    )

    monkeypatch.setattr(pipeline, "parse_cached_raw_if_needed", lambda system_id: None)
    monkeypatch.setattr(pipeline, "_load_trades", lambda system_id: trades)
    monkeypatch.setattr(
        pipeline,
        "screen_system",
        lambda *args, **kwargs: PreScreenResult(
            system_id="11504701",
            decision="STOP",
            k1_sanity_pass=False,
            mcpt_p=1.0,
            psr_p=1.0,
            concentration_top5=0.0,
            is_live=True,
            n_trades=1,
            sharpe_per_trade=0.0,
            notes=["K1 sanity FAIL"],
        ),
    )
    monkeypatch.setattr(
        pipeline,
        "run_stage1",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("Stage 1 should not run")),
    )
    monkeypatch.setattr(
        pipeline,
        "run_candidate_backtest",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("backtest should not run")),
    )

    out_dir = pipeline.run_pipeline(args)
    summary = json.loads((out_dir / "pipeline_summary.json").read_text())

    assert summary["status"] == "PRE_SCREEN_STOP"
    assert summary["pre_screen_decision"] == "STOP"
    assert "EA rejeitado pelo pre-screen" in summary["message"]


def test_adversarial_summary_empty_synthetic_is_non_fatal() -> None:
    summary = pipeline._adversarial_summary(pd.DataFrame(), pd.DataFrame())

    assert summary["adversarial_auc"] is None
    assert summary["adversarial_top_features"] == []
    assert summary["adversarial_notes"]


def test_mandate_24_summary_uses_passes_mandate(monkeypatch) -> None:
    class DummyStats:
        def passes_mandate_24(self) -> tuple[bool, list[str]]:
            return False, ["dsr_p"]

    def fake_compute_gates(*args, **kwargs):
        return DummyStats()

    monkeypatch.setattr(pipeline.gates, "compute_gates", fake_compute_gates)
    synth = pd.DataFrame(
        {
            "symbol": ["EURUSD"],
            "pips": [1.0],
            "close_dt_utc": ["2026-01-01T00:00:00Z"],
        }
    )

    summary = pipeline._mandate_24_summary("1407880", synth)

    assert summary == {"mandate_24_pass": False, "mandate_24_failed": ["dsr_p"]}
