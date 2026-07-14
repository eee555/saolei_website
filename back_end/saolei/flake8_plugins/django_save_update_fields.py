import ast


class DjangoSaveUpdateFieldsChecker:
    """Require explicit update_fields on Django model save() calls."""

    name = 'django-save-update-fields'
    version = '0.1.0'
    _error = 'DJM100 Django model save() call must pass update_fields'

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        for node in ast.walk(self.tree):
            if not self._is_save_call_without_update_fields(node):
                continue

            yield node.lineno, node.col_offset, self._error, type(self)

    @classmethod
    def _is_save_call_without_update_fields(cls, node):
        if not isinstance(node, ast.Call):
            return False

        if not isinstance(node.func, ast.Attribute) or node.func.attr != 'save':
            return False

        if cls._is_form_commit_false_save(node):
            return False

        return not any(keyword.arg == 'update_fields' for keyword in node.keywords)

    @staticmethod
    def _is_form_commit_false_save(node):
        for keyword in node.keywords:
            if keyword.arg != 'commit':
                continue

            value = keyword.value
            return isinstance(value, ast.Constant) and value.value is False

        return False
