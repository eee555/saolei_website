import os
import re
import pathlib
import sys
import importlib
import builtins
import inspect
from unittest import mock

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
DANGERZONE_APP = "dangerzone"

def _scan_static_imports():
    """
    Scan Python source files for any imports of the dangerzone app
    outside its own folder.
    """
    pattern = re.compile(rf"^\s*(from|import)\s+{DANGERZONE_APP}(\.|$)")
    violations = []

    for root, _, files in os.walk(PROJECT_ROOT):
        if DANGERZONE_APP in root:  # allow self-imports
            continue
        if any(skip in root for skip in ("venv", ".venv", "__pycache__", "migrations")):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = pathlib.Path(root) / file
                with open(filepath, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, start=1):
                        if pattern.search(line):
                            violations.append(f"{filepath}:{i}: {line.strip()}")

    return violations


def _scan_dynamic_imports():
    """
    Monkeypatch __import__ and importlib.import_module to detect
    any runtime imports of the dangerzone app outside its folder.
    """
    violations = []

    real_import = builtins.__import__
    real_import_module = importlib.import_module

    def tracking_import(name, *args, **kwargs):
        if name == DANGERZONE_APP or name.startswith(f"{DANGERZONE_APP}."):
            caller_file = sys._getframe(1).f_code.co_filename
            if DANGERZONE_APP not in caller_file:  # block if not inside app
                violations.append(f"Dynamic import of dangerzone in {caller_file}")
        return real_import(name, *args, **kwargs)

    def tracking_import_module(name, *args, **kwargs):
        if name == DANGERZONE_APP or name.startswith(f"{DANGERZONE_APP}."):
            caller_file = sys._getframe(1).f_code.co_filename
            if DANGERZONE_APP not in caller_file:
                violations.append(f"Dynamic import_module of dangerzone in {caller_file}")
        return real_import_module(name, *args, **kwargs)

    with mock.patch("builtins.__import__", side_effect=tracking_import), \
         mock.patch("importlib.import_module", side_effect=tracking_import_module):
        # Import all project modules to trigger dynamic import checks
        for root, _, files in os.walk(PROJECT_ROOT):
            if any(skip in root for skip in ("venv", ".venv", "__pycache__", "migrations", DANGERZONE_APP)):
                continue
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    rel_path = pathlib.Path(root, file).relative_to(PROJECT_ROOT)
                    module_name = ".".join(rel_path.with_suffix("").parts)
                    try:
                        importlib.import_module(module_name)
                    except Exception:
                        pass  # ignore unrelated import errors

    return violations


def test_no_dangerzone_imports():
    static_violations = _scan_static_imports()
    dynamic_violations = _scan_dynamic_imports()

    all_violations = static_violations + dynamic_violations

    assert not all_violations, (
        "Forbidden dangerzone imports found:\n" + "\n".join(all_violations)
    )


def test_all_dangerzone_views_are_local_only():
    # Import the dangerzone/views module
    views_module = importlib.import_module("dangerzone.views")

    missing = []
    for name, obj in inspect.getmembers(views_module, inspect.isfunction):
        # Skip private functions (starting with _)
        if name.startswith("_"):
            continue
        # Check if it's missing the _local_only marker
        if not getattr(obj, "_local_only", False):
            missing.append(name)

    assert not missing, (
        "The following view functions in dangerzone/views.py are missing @local_only:\n"
        + "\n".join(missing)
    )