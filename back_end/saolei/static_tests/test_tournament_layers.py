import ast
from pathlib import Path


def test_tournament_production_code_does_not_import_common():
    tournament = Path(__file__).resolve().parents[1] / 'tournament'
    violations = []
    for path in tournament.rglob('*.py'):
        if {'tests', 'migrations'}.intersection(path.relative_to(tournament).parts):
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                modules = [node.module]
            else:
                continue
            if any(module.split('.')[0] == 'common' for module in modules):
                violations.append(f'{path.relative_to(tournament)}:{node.lineno}')
    assert not violations, f'tournament must not depend on the top-level common app: {violations}'
