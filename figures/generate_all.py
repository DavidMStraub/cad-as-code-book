"""Regenerate every figure in figures/generated/ from scratch.

Run as `python3 figures/generate_all.py` from the repo root (or `make figures`).
"""

import runpy
import sys
from pathlib import Path

FIGURES_DIR = Path(__file__).parent

if __name__ == "__main__":
    sys.path.insert(0, str(FIGURES_DIR))
    for script in sorted(FIGURES_DIR.glob("ch*.py")):
        runpy.run_path(str(script), run_name="__main__")
