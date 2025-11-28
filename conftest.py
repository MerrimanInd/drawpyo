import sys
from pathlib import Path

# Ensure `src` directory is on sys.path so tests can `import drawpyo`
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
