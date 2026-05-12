import os
import sys
from pathlib import Path

# 确保 backend 在 Python 路径中
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
