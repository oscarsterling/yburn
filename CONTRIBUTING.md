# Contributing to yburn

Thanks for wanting to help. This doc covers how to contribute without stepping on anything.

## Before You Start

- Open an issue first for anything non-trivial. Saves everyone time.
- Check open issues and PRs - someone may already be on it.
- For security issues, **do not open a public issue** - see [SECURITY.md](SECURITY.md).

## What We Want

- Bug fixes (with a test that proves it)
- New templates (see below)
- Platform support improvements (Windows native, systemd, launchd)
- Documentation fixes
- Performance improvements with benchmarks

## What We Don't Want (Yet)

- LLM integration features - the whole point is zero tokens
- Breaking changes to the CLI interface without prior discussion
- New external dependencies - stdlib only for the core engine

## Setup

```bash
git clone https://github.com/oscarsterling/yburn.git
cd yburn
pip install -e ".[dev]"
python3 -m pytest tests/ -q
```

All 287 tests should pass before you touch anything.

## Making a Change

1. Fork the repo
2. Create a branch: `git checkout -b fix/your-fix-name`
3. Make your change
4. Add or update tests - **no test, no merge**
5. Run the full suite: `python3 -m pytest tests/ -q`
6. Commit with a clear message: `fix: what you fixed` or `feat: what you added`
7. Open a PR against `main`

## Adding a Template

Templates live in `yburn/templates/<name>/`. Each needs:

- `script.py` - the generated script (stdlib only, no external deps)
- `template.yaml` - metadata (name, description, keywords, params)

The script must:
- Accept `--config` pointing to a YAML config file
- Support `--output json` for machine-readable output
- Exit 0 on success, 1 on warning, 2 on critical
- Work on macOS and Linux with Python 3.9+
- Send Telegram/Discord/Slack alerts if configured (optional)

Look at `yburn/templates/system-diagnostics/` as the reference implementation.

Open an issue describing your template before building it so we can confirm it fits.

## Code Style

- PEP 8, no formatter required (yet)
- Type hints where they add clarity
- Docstrings on public functions
- No f-strings with complex expressions - keep them readable

## PR Review

PRs are reviewed by the maintainer within a few days. We'll tell you clearly if something needs changes or won't be merged, and why.

## License

By contributing, you agree your work is licensed under the [MIT License](LICENSE).
