import os
import re
import pathlib
import sys
import importlib
import builtins
import ast
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


def get_view_functions():
    views_path = pathlib.Path(__file__).parent.parent / "dangerzone" / "views.py"
    with open(views_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(views_path))

    functions = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            decorators = [d.id if isinstance(d, ast.Name) else
                          d.attr if isinstance(d, ast.Attribute) else None
                          for d in node.decorator_list]
            functions.append((node.name, decorators))
    return functions


def test_all_dangerzone_views_are_local_only():
    funcs = get_view_functions()
    missing = [name for name, decorators in funcs
               if "local_only" not in decorators]
    assert not missing, f"These views are missing @local_only: {missing}"
