"""Command-line interface for yburn."""

import argparse
import logging
import sys

from yburn import __version__
from yburn.scanner import scan_crons, CronJob
from typing import List


def main(argv: list = None) -> None:
    """Main entry point for the yburn CLI."""
    parser = argparse.ArgumentParser(
        prog="yburn",
        description="Why burn tokens? Audit AI agent cron jobs and replace mechanical ones with local scripts.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    subparsers = parser.add_subparsers(dest="command")

    # yburn audit
    subparsers.add_parser("audit", help="Scan and audit cron jobs")

    # yburn version
    subparsers.add_parser("version", help="Print version")

    # yburn classify (stub)
    subparsers.add_parser("classify", help="Classify cron jobs (not yet implemented)")

    # yburn convert (stub)
    subparsers.add_parser("convert", help="Convert mechanical jobs to scripts (not yet implemented)")

    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    if args.command == "version":
        print(f"yburn {__version__}")
    elif args.command == "audit":
        _cmd_audit()
    elif args.command == "classify":
        print("Not yet implemented")
    elif args.command == "convert":
        print("Not yet implemented")
    else:
        parser.print_help()
        sys.exit(1)


def _cmd_audit() -> None:
    """Run the audit command: scan cron jobs and print a summary."""
    try:
        jobs = scan_crons()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not jobs:
        print("No cron jobs found.")
        return

    _print_job_table(jobs)


def _print_job_table(jobs: List[CronJob]) -> None:
    """Print a formatted table of cron jobs."""
    print(f"\n{'NAME':<35} {'KIND':<14} {'SCHEDULE':<30} {'STATUS':<8} {'MODEL'}")
    print("-" * 100)
    for job in jobs:
        status = "OK" if job.last_run_status == "ok" else job.last_run_status.upper()
        if not job.enabled:
            status = "DISABLED"
        model = job.model or "-"
        print(f"{job.name:<35} {job.payload_kind:<14} {job.schedule_expr:<30} {status:<8} {model}")
    print(f"\nTotal: {len(jobs)} jobs")
