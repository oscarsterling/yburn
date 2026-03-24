# yburn

**Why burn tokens on tasks that don't think?**

Audit your AI agent cron jobs, identify the ones that never needed an LLM, and replace them with local scripts that run in under a second and cost nothing.

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Build](https://img.shields.io/badge/build-passing-brightgreen)

---

## The Problem

If you run an AI agent with scheduled cron jobs, a significant portion of those jobs are probably doing mechanical work: running a script, checking an endpoint, pushing a git backup, rotating a log file. They do not reason. They do not need context. They just execute the same deterministic steps every time.

But they still call the LLM. Every run. Every day.

Real numbers from a live 92-cron OpenClaw setup (M10 audit, March 2026):

- **44 of 92 crons (48%) were mechanical** - the LLM was doing nothing a Python script couldn't do faster
- **15-25% of daily cron token spend** is recoverable by converting the clearest mechanical jobs
- **30-second average execution time** per mechanical LLM cron drops to **under 1 second** with a local script
- Common culprits: DB maintenance, OAuth health checks, git backups, system diagnostics, update checkers

The community has been finding this manually. A developer at Moltbook AI manually replaced two OpenClaw crons (CLAW token minting, crypto price reporting) with Python scripts and dropped those jobs to zero tokens. Cyfrin documented a 21,000-token charge for a one-word typo fix. nickbuilds.ai cut their OpenClaw costs by 60% by auditing crons and switching models. Yburn automates the audit-to-replacement workflow they all did by hand.

---

## The Solution

Yburn is a CLI tool that:

- **Scans** your agent cron configuration and extracts every scheduled job
- **Classifies** each job as `MECHANICAL` (no reasoning needed), `REASONING` (keep the LLM), or `UNSURE` (needs your call)
- **Converts** mechanical jobs to local Python scripts using a built-in template library
- **Replaces** the original cron with a script-based equivalent and tracks the swap so you can roll back

Classification is deterministic keyword scoring - no LLM required to classify. The tool that finds your LLM waste does not itself create LLM waste.

---

## Quick Demo

```
$ yburn audit

Scanning cron jobs...
Found 92 jobs. Classifying...

  Mechanical:  44 jobs (convertible)
  Reasoning:   14 jobs (kept as-is)
  Unsure:      34 jobs (need your input)

--- MECHANICAL (convertible) ---
  DB Maintenance - Daily Full [enabled]
    Score: mech=18 reason=2 conf=1.00
    Template -> system-diagnostics

  OAuth Token Health Check [enabled]
    Score: mech=16 reason=1 conf=1.00
    Template -> api-endpoint-check

  Pre-Dream Git Snapshot [enabled]
    Score: mech=15 reason=0 conf=1.00
    Template -> git-backup-status

  OpenClaw Update Check [enabled]
    Score: mech=12 reason=3 conf=0.82
    Template -> api-endpoint-check

Estimated monthly savings: ~$4.20 in tokens
Speed improvement: ~30s avg -> <1s per converted job

Run yburn convert --all to convert mechanical jobs.
```

---

## Installation

Requires Python 3.9 or higher. A virtual environment is strongly recommended.

```bash
# Create and activate a venv (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install from source
git clone https://github.com/oscarsterling/yburn.git
cd yburn
pip install -e .

# Install with dev dependencies (for testing)
pip install -e '.[dev]'
```

Verify:

```bash
yburn version
# yburn 0.1.0
```

---

## Usage

### `yburn audit`

Scan and classify all cron jobs. This is the starting point. Read-only, no changes made.

```bash
# Audit your live cron setup
yburn audit

# Verbose mode (shows reasoning jobs too)
yburn audit --verbose

# Lower the classification threshold (more jobs classified)
yburn audit --threshold 2

# Audit from a JSON file (useful for testing or CI)
yburn audit --file jobs.json
```

### `yburn convert`

Generate a local Python replacement script for a mechanical job.

```bash
# Convert a specific job (by name or ID)
yburn convert "OAuth Token Health Check"

# Preview without writing any files
yburn convert "OAuth Token Health Check" --dry-run

# Convert all mechanical jobs at once
yburn convert --all

# Preview all conversions without writing
yburn convert --all --dry-run
```

### `yburn replace`

Swap the original LLM cron for the generated script-based cron.

```bash
# Replace with confirmation prompt
yburn replace <job-id>

# Skip confirmation
yburn replace <job-id> --yes

# Preview the replacement without making changes
yburn replace <job-id> --dry-run
```

### `yburn list`

Show all converted jobs and their replacement status.

```bash
yburn list
```

### `yburn test`

Run a converted script once and display the output. Confirm it works before replacing.

```bash
yburn test "OAuth Token Health Check"
```

### `yburn rollback`

Undo a replacement and restore the original cron configuration.

```bash
yburn rollback <job-id>
```

### `yburn version`

```bash
yburn version
```

---

## How It Works

```
scan -> classify -> convert -> replace
```

1. **Scan:** Reads your cron configuration (OpenClaw via `openclaw cron list`, or a JSON file). Extracts job name, schedule, model, payload text, and tool calls.

2. **Classify:** Scores each job against weighted keyword sets. Mechanical signals: shell commands, script invocations, file operations, exit-on-result patterns. Reasoning signals: synthesis, analysis, research, creative tasks, decision language. Score delta determines classification.

3. **Convert:** Matches the mechanical job to a built-in template by keyword overlap. Generates a standalone Python script that replicates the job's behavior without an LLM call.

4. **Replace:** Records the replacement, disables the original LLM cron, and activates the script-based equivalent. Tracks the swap in a local database so rollback is always available.

---

## Template Library

Yburn ships with five built-in templates covering the most common mechanical cron patterns:

| Template | What It Replaces |
|---|---|
| `system-diagnostics` | Disk, CPU, memory, uptime, process health checks |
| `api-endpoint-check` | HTTP health checks, OAuth token validation, status pings |
| `cron-health-report` | Cron job status audits, failure counts, schedule compliance |
| `git-backup-status` | Git add/commit/push automations, repo state reporting |
| `file-watcher` | File existence checks, size monitors, rotation triggers |

If no template matches your job, Yburn flags it for manual review. Custom templates can be added to `~/.yburn/templates/`. Template spec: `yburn/templates/TEMPLATE_SPEC.md`.

The M10 audit identified two high-value templates not yet built: `script-runner` (for jobs that already wrap an existing Python/bash script) and `model-setter` (for jobs that only call session_status to set model overrides). These are on the roadmap.

---

## Supported Platforms

**OpenClaw (primary integration)**

Yburn reads from `openclaw cron list` JSON output and writes back to the OpenClaw cron system. Native support for OpenClaw's job schema (`sessionTarget`, `payload.kind`, `delivery`, `schedule`).

**Extensible**

The scanner accepts any JSON array of job objects via `--file`. If your agent framework can export cron jobs to JSON, Yburn can classify them. Replacement script generation is framework-agnostic.

Planned integrations: Claude Code (AGENTS.md cron annotations), AutoGen scheduled agents, LangGraph cron nodes.

---

## Test Suite

```
$ pytest

platform darwin -- Python 3.14.2
collected 124 items

tests/test_classifier.py    46 passed
tests/test_converter.py     33 passed
tests/test_replacer.py      23 passed
tests/test_scanner.py       37 passed
tests/test_telegram.py      15 passed
============================== 124 passed in 0.06s
```

---

## Contributing

Contributions welcome, especially:

- New templates for common mechanical cron patterns
- Scanner adapters for other agent frameworks
- Classification signal improvements (see `M10-RESULTS.md` for known edge cases)

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=yburn
```

Please open an issue before submitting a large PR. The classification engine is the core of the tool - changes to scoring weights need evidence from real cron audits.

---

## License

MIT. See `LICENSE`.

---

*Built because the blog posts all found the same fix. Someone had to automate it.*
