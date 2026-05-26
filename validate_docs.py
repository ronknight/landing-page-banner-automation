#!/usr/bin/env python3
"""
Documentation Compliance Validator

Checks that required documentation files are updated alongside code changes.
Designed to run as a pre-commit hook or standalone check.

Usage:
    python validate_docs.py              # Check staged changes
    python validate_docs.py --all        # Check all uncommitted changes
    python validate_docs.py --strict     # Fail on any missing doc update
    python validate_docs.py --fix        # Show what needs updating

Exit codes:
    0 = All checks passed
    1 = Documentation updates missing
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Tuple


# ── Configuration ──────────────────────────────────────────────────────────

# Files that count as "code changes" (trigger doc requirements)
CODE_PATTERNS = {
    "*.py",
    "*.html",
    "config*.json",
    "data/mapping.json",
    "requirements.txt",
}

# Files that are excluded from triggering doc requirements
EXCLUDE_PATTERNS = {
    "validate_docs.py",
    "v9-init.py",
    "migrate_env_to_json.py",
    "verify_data.py",
    "tests/*",
    "archive/*",
}

# Required documentation files and when they must be updated
DOC_REQUIREMENTS: Dict[str, Dict] = {
    "CHANGELOG.md": {
        "triggers": "any_code_change",
        "description": "Every code change needs a CHANGELOG entry",
        "severity": "error",
    },
    "README.md": {
        "triggers": "cli_or_usage_change",
        "watch_patterns": ["main.py", "requirements.txt", "config*.json"],
        "watch_content": ["argparse", "--", "sys.argv", "def main", "Usage"],
        "description": "CLI, config, or usage changes need README update",
        "severity": "warning",
    },
    "PRD.md": {
        "triggers": "feature_or_architecture_change",
        "watch_patterns": ["main.py", "pipeline.py", "*.py"],
        "watch_content": ["class ", "def main", "import", "new feature"],
        "description": "New features or architecture changes need PRD update",
        "severity": "warning",
    },
    "openspec/diagram/dataflow.md": {
        "triggers": "pipeline_or_data_change",
        "watch_patterns": [
            "pipeline.py", "csv_loader.py", "webjaguar_client.py",
            "json_storage.py", "email_generator.py", "main.py",
        ],
        "description": "Pipeline or data flow changes need diagram update",
        "severity": "warning",
    },
    "openspec/diagram/workflow.md": {
        "triggers": "cli_or_workflow_change",
        "watch_patterns": ["main.py"],
        "watch_content": ["sys.argv", "--", "argparse"],
        "description": "CLI or workflow changes need workflow diagram update",
        "severity": "warning",
    },
}

# ADR trigger patterns (content changes that warrant an ADR)
ADR_TRIGGERS = [
    "class ",        # New classes = architectural
    "import ",       # New dependencies
    "BREAKING",      # Breaking changes
    "def __init__",  # New components
]


# ── Git Helpers ────────────────────────────────────────────────────────────

def run_git(args: List[str]) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True, text=True, cwd=Path(__file__).parent
    )
    return result.stdout.strip()


def get_changed_files(staged_only: bool = True) -> List[str]:
    """Get list of changed files from git."""
    if staged_only:
        return run_git(["diff", "--cached", "--name-only"]).splitlines()
    else:
        # All uncommitted changes (staged + unstaged)
        staged = run_git(["diff", "--cached", "--name-only"]).splitlines()
        unstaged = run_git(["diff", "--name-only"]).splitlines()
        untracked = run_git(["ls-files", "--others", "--exclude-standard"]).splitlines()
        return list(set(staged + unstaged + untracked))


def get_diff_content(filepath: str, staged_only: bool = True) -> str:
    """Get the diff content for a specific file."""
    if staged_only:
        return run_git(["diff", "--cached", filepath])
    else:
        return run_git(["diff", filepath])


def matches_pattern(filepath: str, patterns: Set[str]) -> bool:
    """Check if a filepath matches any glob-like pattern."""
    from fnmatch import fnmatch
    return any(fnmatch(filepath, p) for p in patterns)


# ── Validation Logic ──────────────────────────────────────────────────────

def classify_changes(changed_files: List[str]) -> Dict[str, bool]:
    """Classify what types of changes are present."""
    classification = {
        "any_code_change": False,
        "cli_or_usage_change": False,
        "feature_or_architecture_change": False,
        "pipeline_or_data_change": False,
        "cli_or_workflow_change": False,
        "needs_adr": False,
    }

    code_files = [
        f for f in changed_files
        if matches_pattern(f, CODE_PATTERNS)
        and not matches_pattern(f, EXCLUDE_PATTERNS)
    ]

    if not code_files:
        return classification

    classification["any_code_change"] = True

    # Check for CLI/usage changes
    cli_files = {"main.py", "requirements.txt"}
    if cli_files & set(code_files):
        classification["cli_or_usage_change"] = True
        classification["cli_or_workflow_change"] = True

    # Check for pipeline/data changes
    pipeline_files = {
        "pipeline.py", "csv_loader.py", "webjaguar_client.py",
        "json_storage.py", "email_generator.py", "main.py",
    }
    if pipeline_files & set(code_files):
        classification["pipeline_or_data_change"] = True

    # Check for feature/architecture changes (new files or significant changes)
    py_files = [f for f in code_files if f.endswith(".py")]
    if py_files:
        classification["feature_or_architecture_change"] = True

    # Check for config changes
    config_files = [f for f in code_files if "config" in f.lower() and f.endswith(".json")]
    if config_files:
        classification["cli_or_usage_change"] = True

    return classification


def check_adr_needed(changed_files: List[str], staged_only: bool = True) -> bool:
    """Check if an ADR should be created for these changes."""
    adr_dir = Path(__file__).parent / "docs" / "adr"
    today = datetime.now().strftime("%Y%m%d")

    # If an ADR was already created today, skip
    if adr_dir.exists():
        for f in adr_dir.iterdir():
            if f.name.startswith(today):
                return False

    # Check diff content for ADR triggers
    for filepath in changed_files:
        if filepath.endswith(".py") and not matches_pattern(filepath, EXCLUDE_PATTERNS):
            diff = get_diff_content(filepath, staged_only)
            added_lines = [
                line[1:] for line in diff.splitlines()
                if line.startswith("+") and not line.startswith("+++")
            ]
            for line in added_lines:
                for trigger in ADR_TRIGGERS:
                    if trigger in line:
                        return True
    return False


def validate(
    staged_only: bool = True,
    strict: bool = False,
) -> Tuple[List[str], List[str], List[str]]:
    """
    Validate documentation compliance.

    Returns:
        (errors, warnings, passes) - lists of message strings
    """
    errors: List[str] = []
    warnings: List[str] = []
    passes: List[str] = []

    changed_files = get_changed_files(staged_only)
    if not changed_files:
        passes.append("No changes detected")
        return errors, warnings, passes

    classification = classify_changes(changed_files)
    if not classification["any_code_change"]:
        passes.append("No code changes detected (docs-only or excluded files)")
        return errors, warnings, passes

    # Check each required doc file
    doc_files_changed = set(changed_files)
    for doc_file, config in DOC_REQUIREMENTS.items():
        trigger_type = config["triggers"]

        if not classification.get(trigger_type, False):
            continue

        if doc_file in doc_files_changed:
            passes.append(f"  PASS  {doc_file} — updated")
        else:
            msg = f"  MISS  {doc_file} — {config['description']}"
            if config["severity"] == "error" or strict:
                errors.append(msg)
            else:
                warnings.append(msg)

    # Check ADR requirement
    if check_adr_needed(changed_files, staged_only):
        today = datetime.now().strftime("%Y%m%d")
        adr_created = any(
            f.startswith(f"docs/adr/{today}") for f in doc_files_changed
        )
        if adr_created:
            passes.append("  PASS  docs/adr/ — ADR created for today")
        else:
            msg = "  MISS  docs/adr/ — Architectural change detected, ADR recommended"
            if strict:
                errors.append(msg)
            else:
                warnings.append(msg)

    # Check archive (only warn if no recent archive exists)
    archive_dir = Path(__file__).parent / "archive"
    if archive_dir.exists():
        today_str = datetime.now().strftime("%Y-%m-%d")
        has_today_archive = any(
            d.name.startswith(today_str) for d in archive_dir.iterdir() if d.is_dir()
        )
        if has_today_archive:
            passes.append("  PASS  archive/ — Today's archive exists")
        else:
            warnings.append("  MISS  archive/ — No archive created today (run archive-project.ps1)")

    return errors, warnings, passes


# ── CLI ────────────────────────────────────────────────────────────────────

def main() -> int:
    staged_only = "--all" not in sys.argv
    strict = "--strict" in sys.argv
    fix_mode = "--fix" in sys.argv

    print()
    print("=" * 60)
    print("  Documentation Compliance Check")
    print("=" * 60)
    print()

    errors, warnings, passes = validate(staged_only=staged_only, strict=strict)

    # Print results
    for msg in passes:
        print(f"\033[92m{msg}\033[0m")  # Green
    for msg in warnings:
        print(f"\033[93m{msg}\033[0m")  # Yellow
    for msg in errors:
        print(f"\033[91m{msg}\033[0m")  # Red

    print()

    if fix_mode and (errors or warnings):
        print("Suggested actions:")
        print("-" * 40)
        all_issues = errors + warnings
        for issue in all_issues:
            if "CHANGELOG" in issue:
                print("  - Add entry to CHANGELOG.md:")
                print(f"    #### {datetime.now().strftime('%Y-%m-%d')} - <Feature/Fix Name>")
                print("    - Description of change")
            elif "README" in issue:
                print("  - Update README.md usage/features if CLI or config changed")
            elif "PRD" in issue:
                print("  - Update PRD.md sections for new/modified features")
            elif "dataflow" in issue:
                print("  - Update openspec/diagram/dataflow.md if data flow changed")
            elif "workflow" in issue:
                print("  - Update openspec/diagram/workflow.md if user workflow changed")
            elif "adr" in issue:
                today = datetime.now().strftime("%Y%m%d")
                print(f"  - Create docs/adr/{today}-<decision-name>.md")
            elif "archive" in issue:
                print("  - Run: .\\archive-project.ps1")
        print()

    total = len(errors) + len(warnings) + len(passes)
    print(f"Results: {len(passes)} passed, {len(warnings)} warnings, {len(errors)} errors")
    print()

    if errors:
        print("\033[91mCOMMIT BLOCKED: Fix documentation gaps above before committing.\033[0m")
        print("Use --fix for suggestions. Use --all to check unstaged changes too.")
        print()
        return 1

    if warnings:
        print("\033[93mWARNINGS: Consider updating the files above.\033[0m")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
