from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import override_settings, SimpleTestCase

from utils.secrets_json import read_secret, read_secrets, write_secret, write_secrets


class SecretsJsonTests(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_read_and_write_secrets_file(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'secrets.json'

            write_secrets({'django_secret_key': 'secret', 'nested': {'enabled': True}}, path=path)

            self.assertEqual(read_secrets(path), {
                'django_secret_key': 'secret',
                'nested': {'enabled': True},
            })

    @override_settings(DEBUG=False)
    def test_read_secret_uses_default_for_missing_key(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'secrets.json'
            write_secrets({'exists': 'value'}, path=path)

            self.assertEqual(read_secret('missing', 'fallback', path=path), 'fallback')

    @override_settings(DEBUG=False)
    def test_write_secret_updates_existing_file(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'secrets.json'
            write_secrets({'client_id': 'id'}, path=path)

            write_secret('token', 'token-value', path=path)

            self.assertEqual(read_secrets(path), {
                'client_id': 'id',
                'token': 'token-value',
            })

    @override_settings(DEBUG=False)
    def test_write_secret_creates_missing_file(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'secrets.json'

            write_secret('token', 'token-value', path=path)

            self.assertEqual(read_secret('token', path=path), 'token-value')

    @override_settings(DEBUG=False)
    def test_write_secret_serializes_concurrent_updates(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'secrets.json'
            write_secrets({'initial': 'value'}, path=path)

            def write_index(index: int):
                write_secret(f'key_{index}', f'value_{index}', path=path)

            with ThreadPoolExecutor(max_workers=8) as executor:
                list(executor.map(write_index, range(20)))

            data = read_secrets(path)
            self.assertEqual(data['initial'], 'value')
            for index in range(20):
                self.assertEqual(data[f'key_{index}'], f'value_{index}')

    @override_settings(DEBUG=True)
    def test_write_secrets_rejects_debug(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'secrets.json'

            with self.assertRaises(PermissionError):
                write_secrets({'token': 'token-value'}, path=path)

            self.assertFalse(path.exists())

    @override_settings(DEBUG=True)
    def test_write_secret_rejects_debug(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'secrets.json'

            with self.assertRaises(PermissionError):
                write_secret('token', 'token-value', path=path)

            self.assertFalse(path.exists())
