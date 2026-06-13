"""
_bootstrap.py
Path setup for app entry scripts.

Every script in apps/ should `import _bootstrap` as its first project import.
This inserts <project_root>/classes and <project_root>/apps into sys.path so
existing flat imports (`from cls_foo import ...`, `from md_widget import ...`,
`from single_agent_gui import launch`) continue to work after the
apps/ + classes/ reorganization.

By Juan B. Gutierrez, Professor of Mathematics
University of Texas at San Antonio.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_CLASSES = os.path.join(_ROOT, "classes")

for _path in (_CLASSES, _HERE, _ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Several modules still load files with literal relative paths (config.json,
# providers.json, the chats/ folder named by config["CWD"]). Chdir into the
# FOO root so those resolutions work whether the user launches the script as
# `python apps/foo_gui.py` from the root or as `python foo_gui.py` from inside
# apps/. Without this, single_agent_gui.py's `open("config.json")` and
# similar lines raise FileNotFoundError depending on the cwd.
os.chdir(_ROOT)
