"""Tests for yburn CLI helpers and new audit/report behavior."""

import json
from argparse import Namespace
from pathlib import Path

from yburn.classifier import Classification, ClassificationResult
from yburn.cli import (
    _classify_with_manual_overrides,
    _write_manual_classification,
    cmd_report,
)
from yburn.scanner import CronJob


def make_job(name="test-job", payload_text="", job_id="job-1"):
    return CronJob(
        id=job_id,
        name=name,
        schedule={"kind": "cron", "expr": "0 * * * *", "tz": "America/New_York"},
        schedule_expr="0 * * * * (America/New_York)",
        payload_kind="agentTurn",
        payload_text=payload_text,
        delivery_config={},
        enabled=True,
        last_run_status="ok",
        consecutive_errors=0,
        session_target="isolated",
        model="haiku",
    )


class TestManualClassifications:
    def test_persisted_override_applies(self, monkeypatch, tmp_path):
        path = tmp_path / "manual-classifications.json"
        monkeypatch.setattr("yburn.cli.MANUAL_CLASSIFICATIONS_FILE", path)

        job = make_job(name="Manual Job", payload_text="analyze strategy", job_id="abc")
        _write_manual_classification(job, "mechanical")
        results = _classify_with_manual_overrides([job], threshold=3)

        _, result = results[0]
        assert result.classification == Classification.MECHANICAL
        payload = json.loads(path.read_text())
        assert payload["jobs"][0]["decision"] == "mechanical"


class TestReportCommand:
    def test_report_command_writes_output(self, monkeypatch, tmp_path, capsys):
        jobs = [make_job(name="Report Job", payload_text="check health", job_id="report-1")]
        output_path = tmp_path / "report.md"
        auto_report_path = tmp_path / "auto.md"

        monkeypatch.setattr("yburn.cli.Config.load", staticmethod(lambda: Namespace(classification_threshold=3)))
        monkeypatch.setattr("yburn.cli._load_jobs", lambda args: jobs)
        monkeypatch.setattr(
            "yburn.cli._classify_with_manual_overrides",
            lambda jobs, threshold: [(
                jobs[0],
                ClassificationResult(
                    classification=Classification.MECHANICAL,
                    mechanical_score=4,
                    reasoning_score=0,
                    confidence=1.0,
                    signals_found=["manual:mechanical"],
                ),
            )],
        )

        class StubReport:
            def render(self, fmt):
                return "stub-output"

            def auto_save_markdown(self):
                auto_report_path.write_text("auto")
                return auto_report_path

            def save(self, path, fmt):
                path.write_text("explicit")
                return path

        monkeypatch.setattr("yburn.cli.load_templates", lambda: [])
        monkeypatch.setattr("yburn.cli._build_report", lambda jobs, results, templates: StubReport())

        args = Namespace(format="markdown", output=str(output_path), threshold=None, file=None)
        code = cmd_report(args)

        assert code == 0
        assert output_path.read_text() == "explicit"
        assert auto_report_path.read_text() == "auto"
        assert "Auto-saved markdown report" in capsys.readouterr().out
