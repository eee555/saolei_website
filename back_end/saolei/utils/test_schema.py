from django.test import SimpleTestCase
from pydantic import TypeAdapter, ValidationError

from utils.schema import MySQLPositiveInteger


class MySQLPositiveIntegerTests(SimpleTestCase):
    def test_accepts_mysql_positive_integer_field_range(self):
        adapter = TypeAdapter(MySQLPositiveInteger)
        for value in (0, 1, 2147483648, 4294967295):
            with self.subTest(value=value):
                self.assertEqual(adapter.validate_python(value), value)

    def test_rejects_out_of_range_and_non_integer_values(self):
        adapter = TypeAdapter(MySQLPositiveInteger)
        for value in (-1, 4294967296, '1', 1.0, True, False, None):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    adapter.validate_python(value)
