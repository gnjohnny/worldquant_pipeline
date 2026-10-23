"""CLI entrypoint script for worldquant_pipeline."""
import sys
from pathlib import Path

# Add src to pythonpath
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.cli.main import app

if __name__ == "__main__":
    app()
