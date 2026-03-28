"""Tests for the yburn converter."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from yburn.converter import (
    ConversionResult,
    MatchResult,
    TemplateManifest,
    generate_script,
    load_templates,
    match_job_to_template,
    preview_conversion,
    _apply_config_overrides,
    TEMPLATES_DIR,
)
from yburn.scanner import CronJob, scan_from_json


# --- Helpers ---

def make_job(name="test-job", payload_text="", payload_kind="agentTurn", model=""):
    return CronJob(
        id="test-id-123",
        name=name,
        schedule={"kind": "cron", "expr": "0 * * * *"},
        schedule_expr="0 * * * *",
        payload_kind=payload_kind,
        payload_text=payload_text,
        delivery_config={},
        enabled=True,
        last_run_status="ok",
        consecutive_errors=0,
        session_target="isolated",
        model=model,
    )


@pytest.fixture
def templates():
    """Load real templates."""
    return load_templates()


@pytest.fixture
def sample_jobs():
    fixture_path = Path(__file__).parent.parent / "sample-crons.json"
    with open(fixture_path) as f:
        data = json.load(f)
    return scan_from_json(data)


def find_job(jobs, name_fragment):
    for job in jobs:
        if name_fragment.lower() in job.name.lower():
            return job
    raise ValueError(f"No job matching '{name_fragment}'")


# --- TestLoadTemplates ---

class TestLoadTemplates:
    def test_loads_all_templates(self, templates):
        assert len(templates) == 5

    def test_template_names(self, templates):
        names = {t.name for t in templates}
        assert "system-diagnostics" in names
        assert "cron-health-report" in names
        assert "git-backup-status" in names
        assert "api-endpoint-check" in names
        assert "file-watcher" in names

    def test_template_has_keywords(self, templates):
        for t in templates:
            assert len(t.match_keywords) > 0

    def test_template_has_path(self, templates):
        for t in templates:
            assert t.path.exists()
            assert (t.path / "script.py").exists()


# --- TestMatchJobToTemplate ---

class TestMatchJobToTemplate:
    def test_system_diagnostics_match(self, templates):
        job = make_job(
            name="Nightly System Diagnostic",
            payload_text="check disk usage cpu memory uptime health",
        )
        result = match_job_to_template(job, templates)
        assert result.template is not None
        assert result.template.name == "system-diagnostics"
        assert result.score >= 2

    def test_cron_health_match(self, templates):
        job = make_job(
            name="Daily Cron Health Report",
            payload_text="list all cron jobs and report health status",
        )
        result = match_job_to_template(job, templates)
        assert result.template is not None
        assert result.template.name == "cron-health-report"

    def test_git_backup_match(self, templates):
        job = make_job(
            name="Git Backup Status",
            payload_text="check git commit push status for repos",
        )
        result = match_job_to_template(job, templates)
        assert result.template is not None
        assert result.template.name == "git-backup-status"

    def test_api_endpoint_match(self, templates):
        job = make_job(
            name="API Health Check",
            payload_text="check api endpoint url status uptime ping",
        )
        result = match_job_to_template(job, templates)
        assert result.template is not None
        assert result.template.name == "api-endpoint-check"

    def test_file_watcher_match(self, templates):
        job = make_job(
            name="File Monitor",
            payload_text="watch for file changes modified track diff",
        )
        result = match_job_to_template(job, templates)
        assert result.template is not None
        assert result.template.name == "file-watcher"

    def test_no_match_for_unrelated_job(self, templates):
        job = make_job(
            name="Random Task",
            payload_text="something completely unrelated to any template",
        )
        result = match_job_to_template(job, templates)
        assert result.template is None

    def test_min_score_respected(self, templates):
        job = make_job(
            name="Disk Check",
            payload_text="check disk",
        )
        result = match_job_to_template(job, templates, min_score=100)
        assert result.template is None

    def test_require_pattern_match_rejects_keyword_only(self, templates):
        """When require_pattern_match=True, keyword-only matches return None."""
        job = make_job(
            name="API Health Check",
            payload_text="check api endpoint url status uptime ping",
        )
        result = match_job_to_template(job, templates, require_pattern_match=True)
        assert result.template is None

    def test_require_pattern_match_allows_pattern_match(self, templates):
        """When require_pattern_match=True, matches with patterns still work."""
        job = make_job(
            name="Nightly System Diagnostic",
            payload_text="check disk usage cpu memory uptime",
        )
        result = match_job_to_template(job, templates, require_pattern_match=True)
        assert result.template is not None
        assert result.template.name == "system-diagnostics"

    def test_generic_job_no_longer_matches_system_diagnostics(self, templates):
        """Jobs with only generic words like 'health' or 'status' should not match."""
        job = make_job(
            name="OAuth Token Health Check",
            payload_text="check oauth token health status",
        )
        result = match_job_to_template(job, templates)
        assert result.template is None or result.template.name != "system-diagnostics"

    def test_unrelated_job_no_longer_matches_system_diagnostics(self, templates):
        """DB maintenance is not system diagnostics."""
        job = make_job(
            name="DB Maintenance - Daily Full",
            payload_text="vacuum analyze reindex database tables",
        )
        result = match_job_to_template(job, templates)
        assert result.template is None or result.template.name != "system-diagnostics"

    def test_real_job_nightly_diagnostic(self, templates, sample_jobs):
        job = find_job(sample_jobs, "Nightly System Diagnostic")
        result = match_job_to_template(job, templates)
        assert result.template is not None
        assert result.template.name == "system-diagnostics"

    def test_real_job_cron_health(self, templates, sample_jobs):
        job = find_job(sample_jobs, "Daily Cron Health Report")
        result = match_job_to_template(job, templates)
        assert result.template is not None
        assert result.template.name == "cron-health-report"


# --- TestGenerateScript ---

class TestGenerateScript:
    def test_generates_script_file(self, templates):
        job = make_job(name="Test Diagnostic", payload_text="system health check")
        template = [t for t in templates if t.name == "system-diagnostics"][0]

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_script(job, template, output_dir=Path(tmpdir))
            assert result.success
            assert result.script_path.exists()
            assert os.access(result.script_path, os.X_OK)

    def test_script_has_header(self, templates):
        job = make_job(name="My Check", payload_text="health")
        template = [t for t in templates if t.name == "system-diagnostics"][0]

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_script(job, template, output_dir=Path(tmpdir))
            assert "Generated by yburn" in result.script_content
            assert "My Check" in result.script_content
            assert job.id in result.script_content

    def test_script_filename_sanitized(self, templates):
        job = make_job(name="My Fancy Check!!!", payload_text="health")
        template = [t for t in templates if t.name == "system-diagnostics"][0]

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_script(job, template, output_dir=Path(tmpdir))
            assert "!" not in result.script_path.name
            assert result.script_path.name == "my-fancy-check---.py"

    def test_config_overrides_applied(self, templates):
        job = make_job(name="Diag", payload_text="health")
        template = [t for t in templates if t.name == "system-diagnostics"][0]

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_script(
                job, template,
                config_overrides={"disk_threshold_pct": 95},
                output_dir=Path(tmpdir),
            )
            assert result.success
            assert "95" in result.script_content

    def test_missing_template_script(self):
        fake_template = TemplateManifest(
            name="fake", description="", version="1.0",
            match_keywords=[], replaces_patterns=[],
            parameters=[], output_format="plain", requires=[],
            path=Path("/nonexistent/path"),
        )
        job = make_job(name="test")
        result = generate_script(job, fake_template)
        assert not result.success
        assert "not found" in result.error


# --- TestPreviewConversion ---

class TestPreviewConversion:
    def test_preview_contains_job_info(self, templates):
        job = make_job(name="My Health Check", payload_text="check health")
        template = [t for t in templates if t.name == "system-diagnostics"][0]
        preview = preview_conversion(job, template)
        assert "My Health Check" in preview
        assert "system-diagnostics" in preview
        assert "test-id-123" in preview

    def test_preview_shows_parameters(self, templates):
        job = make_job(name="Check", payload_text="health")
        template = [t for t in templates if t.name == "system-diagnostics"][0]
        preview = preview_conversion(job, template)
        assert "disk_threshold_pct" in preview
        assert "80" in preview  # default value

    def test_preview_shows_overrides(self, templates):
        job = make_job(name="Check", payload_text="health")
        template = [t for t in templates if t.name == "system-diagnostics"][0]
        preview = preview_conversion(job, template, config_overrides={"disk_threshold_pct": 95})
        assert "95" in preview
        assert "custom" in preview


# --- TestApplyConfigOverrides ---

class TestApplyConfigOverrides:
    def test_replaces_int_value(self):
        script = '    "disk_threshold_pct": 80,\n'
        result = _apply_config_overrides(script, {"disk_threshold_pct": 95})
        assert "95" in result

    def test_replaces_list_value(self):
        script = '    "processes_to_check": [],\n'
        result = _apply_config_overrides(script, {"processes_to_check": ["node", "python3"]})
        assert '["node", "python3"]' in result

    def test_no_match_leaves_unchanged(self):
        script = '    "something_else": 42,\n'
        result = _apply_config_overrides(script, {"nonexistent": 99})
        assert result == script
