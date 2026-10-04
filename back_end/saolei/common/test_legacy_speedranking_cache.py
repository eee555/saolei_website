from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase


class LegacySpeedrankingCacheTests(SimpleTestCase):
    def test_cleanup_preserves_unrelated_keys_and_supports_preview(self):
        legacy = {b'player_timems_std_12', b'player_bvs_nf_ids', b'news_queue'}
        unrelated = {
            b'player_profile_12', b'player_timems_std_12_extra', b'player_pluck_std_ids',
            b'customranking:pluck:c8_8_40:rank', b'tournament:normal', b'newest_queue',
        }
        stored = legacy | unrelated

        def unlink(*keys):
            keys = {key.encode() if isinstance(key, str) else key for key in keys}
            count = len(stored & keys)
            stored.difference_update(keys)
            return count

        with patch('common.management.commands.delete_legacy_speedranking_cache.get_redis_connection') as connection:
            cache = connection.return_value
            cache.scan_iter.side_effect = lambda **kwargs: iter(sorted(stored - {b'news_queue'}))
            cache.exists.side_effect = lambda key: key.encode() in stored
            cache.unlink.side_effect = unlink

            output = StringIO()
            call_command('delete_legacy_speedranking_cache', dry_run=True, stdout=output)
            cache.unlink.assert_not_called()
            self.assertEqual(stored, legacy | unrelated)
            self.assertIn('Matched 3 legacy Redis keys', output.getvalue())

            call_command('delete_legacy_speedranking_cache', stdout=StringIO())
            self.assertEqual(stored, unrelated)
            call_command('delete_legacy_speedranking_cache', stdout=StringIO())
            self.assertEqual(stored, unrelated)
