#!/usr/bin/env python3
"""
Command-line interface for PR Firm.
"""
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pr_firm.main import main, launch_gradio


def main_cli():
    """Main CLI entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "ui":
        launch_gradio()
    else:
        main()


if __name__ == "__main__":
    main_cli()