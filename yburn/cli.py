"""CLI entry point for yburn.

Provides commands: audit, classify, convert, replace, list, test, rollback, version.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from yburn import __version__
from yburn.classifier import (
    Classification,
    classify_job,
    classify_jobs,
    print_summary,
)
from yburn.config import Config
from yburn.converter import (
    check_output_config,
    generate_script,
    load_templates,
    match_job_to_template,
    preview_conversion,
)
from yburn.replacer import (
    build_replacement_command,
    get_active_replacements,
    get_replacement_for_job,
    preview_replacement,
    record_replacement,
    rollback_replacement,
)
from yburn.scanner import scan_crons, scan_from_json

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def color(text, code):
    """Apply ANSI color if stdout is a terminal."""
    if sys.stdout.isatty():
        return f"{code}{text}{RESET}"
    return text


def cmd_audit(args):
    """Scan and classify all cron jobs."""
    config = Config.load()
    threshold = args.threshold or config.classification_threshold

    print(color("Scanning cron jobs...", BLUE))
    try:
        if args.file:
            with open(args.file) as f:
                data = json.load(f)
            if isinstance(data, dict) and "jobs" in data:
                data = data["jobs"]
            jobs = scan_from_json(data)
        else:
            jobs = scan_crons()
    except RuntimeError as e:
        print(color(f"Error: {e}", RED))
        return 1
    except FileNotFoundError:
        print(color(f"File not found: {args.file}", RED))
        return 1

    if not jobs:
        print(color("No cron jobs found.", YELLOW))
        return 0

    print(f"Found {len(jobs)} jobs. Classifying...\n")
    results = classify_jobs(jobs, threshold=threshold)

    mechanical = [(j, r) for j, r in results if r.classification == Classification.MECHANICAL]
    reasoning = [(j, r) for j, r in results if r.classification == Classification.REASONING]
    unsure = [(j, r) for j, r in results if r.classification == Classification.UNSURE]

    # Summary
    print(color(f"  Mechanical:  {len(mechanical)} jobs (convertible)", GREEN))
    print(color(f"  Reasoning:   {len(reasoning)} jobs (kept as-is)", RED))
    print(color(f"  Unsure:      {len(unsure)} jobs (need your input)", YELLOW))
    print()

    # Detailed listing
    if mechanical:
        print(color("--- MECHANICAL (convertible) ---", GREEN))
        templates = load_templates()
        for job, result in mechanical:
            match = match_job_to_template(job, templates)
            template_str = f" -> {match.template.name}" if match.template else " (no template match)"
            status = "enabled" if job.enabled else "disabled"
            print(f"  {color(job.name, GREEN)} [{status}]")
            print(f"    Score: mech={result.mechanical_score} reason={result.reasoning_score} conf={result.confidence}")
            print(f"    Template{template_str}")
        print()

    if unsure:
        print(color("--- UNSURE (manual review needed) ---", YELLOW))
        for job, result in unsure:
            print(f"  {color(job.name, YELLOW)}")
            print(f"    Score: mech={result.mechanical_score} reason={result.reasoning_score}")
            signals = ", ".join(result.signals_found[:5])
            print(f"    Signals: {signals}")
        print()

    if reasoning and args.verbose:
        print(color("--- REASONING (kept as-is) ---", RED))
        for job, result in reasoning:
            print(f"  {job.name}")
        print()

    # Token savings estimate
    if mechanical:
        # Rough estimate: each mechanical job fires ~1-2x/day, uses ~1000 tokens
        daily_fires = len(mechanical) * 1.5
        monthly_tokens = daily_fires * 30 * 1000
        monthly_cost = monthly_tokens / 1_000_000 * 0.25  # ~haiku pricing
        print(f"Estimated monthly savings: ~${monthly_cost:.2f} in tokens")
        print(f"Speed improvement: ~30s avg -> <1s per converted job")
        print()
        print(f"Run {color('yburn convert --all', BOLD)} to convert mechanical jobs.")

    return 0


def cmd_convert(args):
    """Convert a mechanical job to a local script."""
    config = Config.load()
    templates = load_templates()

    if args.job_id:
        # Convert specific job
        jobs = scan_crons()
        job = None
        for j in jobs:
            if j.id == args.job_id or j.name.lower() == args.job_id.lower():
                job = j
                break
        if not job:
            print(color(f"Job not found: {args.job_id}", RED))
            return 1
        return _convert_single(job, templates, config, args.dry_run, args.strict)

    elif args.all:
        # Convert all mechanical jobs
        jobs = scan_crons()
        results = classify_jobs(jobs, threshold=config.classification_threshold)
        mechanical = [(j, r) for j, r in results if r.classification == Classification.MECHANICAL]

        if not mechanical:
            print(color("No mechanical jobs found to convert.", YELLOW))
            return 0

        print(f"Converting {len(mechanical)} mechanical jobs...\n")
        success_count = 0
        for job, _ in mechanical:
            result = _convert_single(job, templates, config, args.dry_run, args.strict)
            if result == 0:
                success_count += 1
            print()

        print(f"\nConverted {success_count}/{len(mechanical)} jobs.")
        return 0
    else:
        print(color("Specify --job-id <id> or --all", RED))
        return 1


def _convert_single(job, templates, config, dry_run=False, strict=False):
    """Convert a single job."""
    match = match_job_to_template(job, templates)
    if not match.template:
        print(color(f"  No template match for: {job.name}", YELLOW))
        print(f"    Matched keywords: {match.matched_keywords}")
        print(f"    This job needs a custom template (Phase 2)")
        return 1

    # Show preview
    preview = preview_conversion(job, match.template)
    print(preview)

    if dry_run:
        print(color("  [DRY RUN] Would generate script but skipping.", BLUE))
        return 0

    configured, warnings = check_output_config()
    for warning in warnings:
        print(color(f"  Warning: {warning}", YELLOW))
    if strict and not configured:
        print(color("  Error: output channel configuration is required in strict mode.", RED))
        return 1

    # Generate script
    result = generate_script(job, match.template)
    if result.success:
        print(color(f"  Generated: {result.script_path}", GREEN))
        return 0
    else:
        print(color(f"  Failed: {result.error}", RED))
        return 1


def cmd_replace(args):
    """Replace an original cron with a script-based cron."""
    configured, warnings = check_output_config()
    for warning in warnings:
        print(color(f"Warning: {warning}", YELLOW))
    if args.strict and not configured:
        print(color("Error: output channel configuration is required in strict mode.", RED))
        return 1

    jobs = scan_crons()
    job = None
    for j in jobs:
        if j.id == args.job_id or j.name.lower() == args.job_id.lower():
            job = j
            break

    if not job:
        print(color(f"Job not found: {args.job_id}", RED))
        return 1

    # Check if already replaced
    existing = get_replacement_for_job(job.id)
    if existing:
        print(color(f"Job already replaced. Script: {existing.script_path}", YELLOW))
        print(f"Use 'yburn rollback {job.id}' to undo.")
        return 1

    # Find script
    from yburn.converter import SCRIPTS_DIR
    import re
    safe_name = re.sub(r'[^a-z0-9_-]', '-', job.name.lower())
    script_path = SCRIPTS_DIR / f"{safe_name}.py"

    if not script_path.exists():
        print(color(f"No generated script found at {script_path}", RED))
        print(f"Run 'yburn convert {job.id}' first.")
        return 1

    # Show preview
    spec = build_replacement_command(job.id, job.name, job.schedule, str(script_path))
    preview = preview_replacement(
        job.id, job.name, job.schedule, job.schedule_expr, str(script_path)
    )
    print(preview)

    if args.dry_run:
        print(color("[DRY RUN] Would replace but skipping.", BLUE))
        return 0

    # Confirm
    if not args.yes:
        resp = input("\nProceed with replacement? [y/N] ")
        if resp.lower() not in ("y", "yes"):
            print("Cancelled.")
            return 0

    # Record the replacement (actual cron creation/disabling done via openclaw)
    replacement = record_replacement(
        job.id, job.name, job.schedule,
        str(script_path), "manual",
    )
    print(color(f"Replacement recorded. Status: {replacement.status}", GREEN))
    print("\nTo complete the replacement manually:")
    print("  Add this line to your crontab (run: crontab -e)")
    print(f"  {spec['crontab_entry']}")
    print("  Disable the original OpenClaw job")
    print(f"  {spec['disable_command']}")
    return 0


def cmd_list(args):
    """Show converted jobs and their replacement status."""
    from yburn.converter import SCRIPTS_DIR

    replacements = get_active_replacements()
    if not replacements:
        # Check if scripts exist even without replacements
        if SCRIPTS_DIR.exists():
            scripts = list(SCRIPTS_DIR.glob("*.py"))
            if scripts:
                print(f"Found {len(scripts)} generated script(s) in {SCRIPTS_DIR}:")
                for s in sorted(scripts):
                    print(f"  {s.name}")
                print(f"\nNo active replacements tracked. Use 'yburn replace <job-id>' to activate.")
                return 0

        print(color("No converted jobs or replacements found.", YELLOW))
        return 0

    print(f"Active replacements: {len(replacements)}\n")
    for r in replacements:
        status_icon = "✅" if r.status == "active" else "⏪"
        print(f"  {status_icon} {r.original_job_name}")
        print(f"     Original ID: {r.original_job_id}")
        print(f"     Script: {r.script_path}")
        print(f"     Template: {r.template_name}")
        print(f"     Replaced: {r.replaced_at}")
        if r.new_cron_id:
            print(f"     New cron: {r.new_cron_id}")
        print()

    return 0


def cmd_test(args):
    """Run a converted script once and show output."""
    from yburn.converter import SCRIPTS_DIR
    import subprocess
    import re

    # Find the script
    if args.job_id:
        safe_name = re.sub(r'[^a-z0-9_-]', '-', args.job_id.lower())
        script_path = SCRIPTS_DIR / f"{safe_name}.py"
        if not script_path.exists():
            # Try finding by job ID in replacements
            r = get_replacement_for_job(args.job_id)
            if r:
                script_path = Path(r.script_path)
            else:
                print(color(f"No script found for: {args.job_id}", RED))
                return 1
    else:
        print(color("Specify a job ID or name to test.", RED))
        return 1

    if not script_path.exists():
        print(color(f"Script not found: {script_path}", RED))
        return 1

    print(f"Running: {script_path}\n")
    print("--- Output ---")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=False,
    )
    print("--- End ---")
    print(f"\nExit code: {result.returncode}")
    return result.returncode


def cmd_rollback(args):
    """Undo a replacement."""
    success = rollback_replacement(args.job_id)
    if success:
        print(color(f"Rolled back replacement for {args.job_id}", GREEN))
        print(f"To complete rollback:")
        print(f"  1. Re-enable original: openclaw cron update {args.job_id} --enable")
        print(f"  2. Disable/delete the yburn replacement cron")
    else:
        print(color(f"No active replacement found for: {args.job_id}", RED))
    return 0 if success else 1


def cmd_version(args):
    """Print version."""
    print(f"yburn {__version__}")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="yburn",
        description="Why burn tokens? Audit AI agent cron jobs and replace mechanical ones with local scripts.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # audit
    p_audit = subparsers.add_parser("audit", help="Scan and classify all cron jobs")
    p_audit.add_argument("-t", "--threshold", type=int, help="Classification threshold (default: 3)")
    p_audit.add_argument("--dry-run", action="store_true", help="Show results without making changes")
    p_audit.add_argument("-f", "--file", type=str, help="Read cron jobs from JSON file instead of CLI")
    p_audit.set_defaults(func=cmd_audit)

    # convert
    p_convert = subparsers.add_parser("convert", help="Convert a mechanical job to a local script")
    p_convert.add_argument("job_id", nargs="?", help="Job ID or name to convert")
    p_convert.add_argument("--all", action="store_true", help="Convert all mechanical jobs")
    p_convert.add_argument("--dry-run", action="store_true", help="Preview without generating")
    p_convert.add_argument("--strict", action="store_true", help="Require full output channel configuration")
    p_convert.set_defaults(func=cmd_convert)

    # replace
    p_replace = subparsers.add_parser("replace", help="Replace original cron with script-based cron")
    p_replace.add_argument("job_id", help="Job ID to replace")
    p_replace.add_argument("--dry-run", action="store_true", help="Preview without replacing")
    p_replace.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    p_replace.add_argument("--strict", action="store_true", help="Require full output channel configuration")
    p_replace.set_defaults(func=cmd_replace)

    # list
    p_list = subparsers.add_parser("list", help="Show converted jobs and replacement status")
    p_list.set_defaults(func=cmd_list)

    # test
    p_test = subparsers.add_parser("test", help="Run a converted script once, show output")
    p_test.add_argument("job_id", help="Job ID or name to test")
    p_test.set_defaults(func=cmd_test)

    # rollback
    p_rollback = subparsers.add_parser("rollback", help="Undo a replacement")
    p_rollback.add_argument("job_id", help="Original job ID to rollback")
    p_rollback.set_defaults(func=cmd_rollback)

    # version
    p_version = subparsers.add_parser("version", help="Print version")
    p_version.set_defaults(func=cmd_version)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    if hasattr(args, "func"):
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
