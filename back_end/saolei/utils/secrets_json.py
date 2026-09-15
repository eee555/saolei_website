from collections.abc import Mapping
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from django.conf import settings
from filelock import FileLock

SECRETS_JSON = Path('secrets.json')
SECRETS_JSON_LOCK_TIMEOUT = 10
_MISSING = object()


def read_secrets(path: str | Path = SECRETS_JSON) -> dict[str, Any]:
    return _read_secrets_unlocked(Path(path))


def write_secrets(secrets: Mapping[str, Any], path: str | Path = SECRETS_JSON):
    secret_path = Path(path)
    _ensure_secrets_writable()
    with _secrets_lock(secret_path):
        _write_secrets_unlocked(secrets, secret_path)


def read_secret(key: str, default: Any = _MISSING, *, path: str | Path = SECRETS_JSON) -> Any:
    try:
        return read_secrets(path)[key]
    except (FileNotFoundError, KeyError):
        if default is _MISSING:
            raise
        return default


def write_secret(key: str, value: Any, *, path: str | Path = SECRETS_JSON):
    secret_path = Path(path)
    _ensure_secrets_writable()
    with _secrets_lock(secret_path):
        try:
            data = _read_secrets_unlocked(secret_path)
        except FileNotFoundError:
            data = {}
        data[key] = value
        _write_secrets_unlocked(data, secret_path)


def _read_secrets_unlocked(secret_path: Path) -> dict[str, Any]:
    with secret_path.open('r', encoding='utf-8') as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError('secrets.json must contain a JSON object.')
    return data


def _write_secrets_unlocked(secrets: Mapping[str, Any], secret_path: Path):
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=secret_path.parent, prefix=f'.{secret_path.name}.', suffix='.tmp', delete=False) as file:
            temp_path = Path(file.name)
            json.dump(dict(secrets), file, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_path, secret_path)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def _secrets_lock(secret_path: Path) -> FileLock:
    return FileLock(f'{secret_path}.lock', timeout=SECRETS_JSON_LOCK_TIMEOUT)


def _ensure_secrets_writable():
    if settings.DEBUG:
        raise PermissionError('Writing secrets.json is disabled when DEBUG=True.')
