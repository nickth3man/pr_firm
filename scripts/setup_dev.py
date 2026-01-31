#!/usr/bin/env python3
"""
Development setup script for PR Firm.
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, desc):
    """Run a command and print status."""
    print(f"Running: {desc}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("✓ Success")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {e}")
        sys.exit(1)


def main():
    """Set up development environment."""
    print("Setting up PR Firm development environment...")

    # Install dependencies
    run_command("pip install -e .[dev]", "Installing package and dev dependencies")

    # Install pre-commit hooks
    if Path(".pre-commit-config.yaml").exists():
        run_command("pre-commit install", "Installing pre-commit hooks")

    # Run initial checks
    run_command("python -m pytest --collect-only", "Checking test collection")
    run_command("python -m mypy src/pr_firm --ignore-missing-imports", "Running type check")

    print("\nDevelopment environment setup complete!")
    print("Run 'python cli.py' to start the application.")


if __name__ == "__main__":
    main()