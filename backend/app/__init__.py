import sys
from pathlib import Path

app_dir = Path(__file__).resolve().parent
backend_dir = app_dir.parent
repo_root = backend_dir.parent

for p in [str(repo_root), str(backend_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)
