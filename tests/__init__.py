from pathlib import Path
import sys

# project root
path: Path = Path(__file__).parent.parent
sys.path.insert(0, str(path))