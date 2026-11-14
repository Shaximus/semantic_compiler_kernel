# Compatibility layer for imports
import sys
from pathlib import Path

# Ensure the package root is on path
_ROOT = Path(__file__).parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
