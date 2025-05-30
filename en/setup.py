import sys
from pathlib import Path

def add_lib_path():
    posix_path = Path(__file__).parent.parent / "shared" / "lib"
    sys.path.append(str(posix_path))