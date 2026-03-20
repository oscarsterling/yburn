"""Cron replacement logic for yburn.

Handles the 'last mile': creating new cron jobs that run generated scripts,
disabling originals, tracking replacements, and rollback.
"""

import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

STATE_DIR = Path.home() / ".yburn" / "state"
REPLACEMENTS_FILE = "replacements.json"


@dataclass
class Replacement:
    """Tracks a single cron job replacement."""
    original_job_id: str
    original_job_name: str
    original_schedule: dict
    script_path: str
    template_name: str
    replaced_at: str
    status: str  # "active", "rolled_back"
    new_cron_id: Optional[str] = None


def load_replacements() -> List[Replacement]:
    """Load replacement tracking data."""
    state_path = STATE_DIR / REPLACEMENTS_FILE
    if not state_path.exists():
        return []
    try:
        with open(state_path) as f:
            data = json.load(f)
        return [Replacement(**r) for r in data]
    except Exception:
        logger.exception("Failed to load replacements")
        return []


def save_replacements(replacements: List[Replacement]) -> None:
    """Save replacement tracking data."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_path = STATE_DIR / REPLACEMENTS_FILE
    data = []
    for r in replacements:
        data.append({
            "original_job_id": r.original_job_id,
            "original_job_name": r.original_job_name,
            "original_schedule": r.original_schedule,
            "script_path": r.script_path,
            "template_name": r.template_name,
            "replaced_at": r.replaced_at,
            "status": r.status,
            "new_cron_id": r.new_cron_id,
        })
    with open(state_path, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Saved %d replacement records", len(data))


def build_replacement_command(
    original_job_id: str,
    original_name: str,
    schedule: dict,
    script_path: str,
) -> Dict:
    """Build the replacement cron job specification.

    Returns a dict describing what the new cron job should look like.
    Does NOT create it (that requires user confirmation).

    Args:
        original_job_id: ID of the original cron job.
        original_name: Name of the original job.
        schedule: Original schedule dict.
        script_path: Path to the generated script.

    Returns:
        Dict with new cron job specification.
    """
    return {
        "name": f"[yburn] {original_name}",
        "schedule": schedule,
        "payload": {
            "kind": "agentTurn",
            "message": (
                f"Run the yburn-generated script:\n\n"
                f"python3 {script_path}\n\n"
                f"If exit code is non-zero, report the error. "
                f"Otherwise produce NO output."
            ),
            "model": "haiku",
            "timeoutSeconds": 60,
        },
        "sessionTarget": "isolated",
        "original_job_id": original_job_id,
    }


def preview_replacement(
    original_job_id: str,
    original_name: str,
    schedule: dict,
    schedule_expr: str,
    script_path: str,
) -> str:
    """Generate a preview of the replacement.

    Args:
        original_job_id: ID of the original cron job.
        original_name: Name of the original job.
        schedule: Original schedule dict.
        schedule_expr: Human-readable schedule.
        script_path: Path to the generated script.

    Returns:
        Formatted preview string.
    """
    spec = build_replacement_command(original_job_id, original_name, schedule, script_path)

    lines = [
        "=== Replacement Preview ===",
        "",
        "OLD JOB:",
        f"  Name: {original_name}",
        f"  ID: {original_job_id}",
        f"  Schedule: {schedule_expr}",
        f"  Action: Will be DISABLED (not deleted)",
        "",
        "NEW JOB:",
        f"  Name: {spec['name']}",
        f"  Schedule: {schedule_expr} (same)",
        f"  Runs: python3 {script_path}",
        f"  Model: haiku (minimal, just runs the script)",
        f"  Timeout: 60s",
        "",
        "ROLLBACK: yburn rollback {original_job_id}",
        "===========================",
    ]
    return "\n".join(lines)


def record_replacement(
    original_job_id: str,
    original_name: str,
    original_schedule: dict,
    script_path: str,
    template_name: str,
    new_cron_id: Optional[str] = None,
) -> Replacement:
    """Record a replacement in the tracking file.

    Args:
        original_job_id: ID of the original cron job.
        original_name: Name of the original job.
        original_schedule: Original schedule configuration.
        script_path: Path to the generated script.
        template_name: Name of the template used.
        new_cron_id: ID of the new cron job (if created).

    Returns:
        The recorded Replacement.
    """
    replacements = load_replacements()

    # Check for existing replacement
    for r in replacements:
        if r.original_job_id == original_job_id and r.status == "active":
            logger.warning(
                "Job %s already has an active replacement", original_job_id
            )
            return r

    replacement = Replacement(
        original_job_id=original_job_id,
        original_job_name=original_name,
        original_schedule=original_schedule,
        script_path=script_path,
        template_name=template_name,
        replaced_at=datetime.now(timezone.utc).isoformat(),
        status="active",
        new_cron_id=new_cron_id,
    )

    replacements.append(replacement)
    save_replacements(replacements)
    return replacement


def rollback_replacement(original_job_id: str) -> bool:
    """Mark a replacement as rolled back.

    This updates tracking state only. The actual cron enable/disable
    operations need to happen via the CLI.

    Args:
        original_job_id: ID of the original cron job.

    Returns:
        True if a replacement was found and rolled back.
    """
    replacements = load_replacements()
    found = False

    for r in replacements:
        if r.original_job_id == original_job_id and r.status == "active":
            r.status = "rolled_back"
            found = True
            logger.info("Rolled back replacement for %s", r.original_job_name)
            break

    if found:
        save_replacements(replacements)
    else:
        logger.warning("No active replacement found for %s", original_job_id)

    return found


def get_active_replacements() -> List[Replacement]:
    """Get all active (non-rolled-back) replacements."""
    return [r for r in load_replacements() if r.status == "active"]


def get_replacement_for_job(original_job_id: str) -> Optional[Replacement]:
    """Get the active replacement for a specific job, if any."""
    for r in load_replacements():
        if r.original_job_id == original_job_id and r.status == "active":
            return r
    return None
