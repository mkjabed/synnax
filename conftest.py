import sys
from pathlib import Path

# Ensures `from src.ast.nodes import ...` etc. resolve regardless of the
# directory pytest is invoked from. Deliberately adds the PROJECT ROOT,
# not src/ itself — adding src/ directly would make "ast" importable as
# a bare top-level name, shadowing Python's own built-in ast module.
sys.path.insert(0, str(Path(__file__).parent))
