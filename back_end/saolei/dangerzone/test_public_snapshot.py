from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from django.core.management import call_command, get_commands
from django.core.management.base import CommandError
from django.test import override_settings, SimpleTestCase, TestCase
from download_public_data import download, PublicClient

from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel
from .public_snapshot import import_snapshot_rows, initialize_local_data, snapshot_datetime, validate_import
from .utils import file_entry, read_json, validate_snapshot, write_json


def make_snapshot(root):
    users = [
        {'id': user_id, 'username': f'player-{user_id}', 'is_staff': True, 'last_change_avatar': '2025-01-02T03:04:05Z'}
        for user_id in (2, 48, 80)
    ]
    video = {
        'id': 501, 'player': 48, 'level': 'e', 'mode': '12', 'state': 'd', 'software': 'e',
        'timems': 50000, 'bv': 100, 'left': 120, 'right': 2, 'double': 3,
        'left_ce': 100, 'right_ce': 0, 'double_ce': 0,
        'pluck': 0.125, 'upload_time': '2025-01-02T03:04:05.123456Z',
        'end_time': '2025-01-02T02:00:00Z', 'video__identifier': 'public identifier',
        'bvs': -1, 'iqg': -1, 'cl': -1,
    }
    write_json(root / 'users.json', users)
    write_json(root / 'videos.json', [video])
    manifest = {
        'version': 1, 'complete': True, 'user_count': len(users), 'video_count': 1,
        'users': [file_entry(root, root / 'users.json')], 'videos': [file_entry(root, root / 'videos.json')],
    }
    write_json(root / 'manifest.json', manifest)
    return video


class SnapshotDownloadTests(SimpleTestCase):
    def test_import_command_is_not_registered(self):
        get_commands.cache_clear()
        self.assertNotIn('import_public_data', get_commands())

    def test_skip_details_reuses_cached_lists_without_network(self):
        with TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            root = Path(directory)
            video = make_snapshot(root)
            manifest = read_json(root / 'manifest.json')
            manifest['complete'] = False
            write_json(root / 'manifest.json', manifest)
            write_json(root / 'user-ids.json', [2, 48, 80])
            write_json(root / 'users/000000.json', read_json(root / 'users.json'))
            for user_id in (2, 80):
                write_json(root / f'indexes/{user_id}.json', [])
            write_json(root / 'indexes/48.json', [{**video, 'id': 501}, {**video, 'id': 502}])
            write_json(root / 'raw-videos/000000501.json', [{**video, 'timems': 40000}])
            client = PublicClient('https://example.invalid')
            client.get = Mock(side_effect=AssertionError('Unexpected network request'))
            download(root, client, skip_details=True)
            manifest, _ = validate_snapshot(root)
            self.assertEqual(manifest['video_count'], 2)
            self.assertEqual(manifest['missing_detail_video_ids'], [502])
            self.assertEqual(manifest['unavailable_video_ids'], [])
            rows = read_json(root / 'videos/000000501.json')
            self.assertEqual([row['timems'] for row in rows], [40000, 50000])
            client.get.assert_not_called()

    def test_download_resumes_and_keeps_sparse_ids(self):
        client = PublicClient('https://example.invalid', interval=0)
        self.assertEqual(client.interval, 1.25)
        self.assertIsInstance(client.session.verify, str)
        client.get = Mock(side_effect=[
            [2, 48], [{'id': 2, 'username': 'admin'}, {'id': 48, 'username': 'user'}],
            [], [{'id': 1001, 'pluck': 0.2}, {'id': 2001, 'pluck': 0.3}],
            [{'id': 1001, 'player': 48, 'level': 'e', 'mode': '00', 'state': 'd', 'software': 'e', 'timems': 10000, 'upload_time': '2025-01-02T00:00:00Z'}],
            [],
        ])
        with TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            root = Path(directory)
            download(root, client)
            manifest, users = validate_snapshot(root)
            self.assertEqual(set(users), {2, 48})
            self.assertEqual(manifest['video_count'], 1)
            self.assertEqual(manifest['unavailable_video_ids'], [2001])
            self.assertEqual(read_json(root / 'videos/000001001.json')[0]['pluck'], 0.2)
            client.get.assert_any_call('/api/video/detailbulk', {'first': 2001, 'count': 250})
            client.get.reset_mock()
            download(root, client)
            client.get.assert_not_called()

    def test_rate_limit_retries_without_disabling_tls(self):
        client = PublicClient('https://example.invalid')
        retry = Mock(status_code=429, headers={'Retry-After': '3'})
        success = Mock(status_code=200)
        success.json.return_value = [2, 48]
        client.session.get = Mock(side_effect=[retry, success])
        with patch('download_public_data.time.sleep') as sleep:
            self.assertEqual(client.get('/users', {}), [2, 48])
        sleep.assert_any_call(3.0)
        self.assertEqual(client.session.get.call_count, 2)


class SnapshotImportTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.video = make_snapshot(self.root)

    def test_import_preserves_ids_times_and_recomputes_generated_fields(self):
        manifest, users = validate_snapshot(self.root)
        validate_import(self.root, manifest, users)
        with patch.object(VideoModel, 'save') as save:
            import_snapshot_rows(self.root, manifest, users, 'admin-secret', 'user-secret')
        save.assert_not_called()
        admin = UserProfile.objects.get(pk=2)
        user = UserProfile.objects.get(pk=48)
        other = UserProfile.objects.get(pk=80)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.check_password('admin-secret'))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password('user-secret'))
        self.assertFalse(other.is_staff)
        self.assertFalse(other.has_usable_password())
        self.assertEqual(user.email, 'user-48@example.invalid')
        self.assertEqual(user.last_change_avatar, snapshot_datetime(users[48]['last_change_avatar']))
        video = VideoModel.objects.get(pk=501)
        self.assertEqual(video.player_id, 48)
        self.assertEqual(video.upload_time, snapshot_datetime(self.video['upload_time']))
        self.assertEqual(video.mode, '00')
        self.assertEqual(video.right_ce, 0)
        self.assertEqual(video.bvs, 2)
        self.assertAlmostEqual(video.iqg, 100 / (50 ** 1.7))
        self.assertEqual(video.cl, 125)
        self.assertEqual(video.pluck, 0.125)
        self.assertEqual(ExpandVideoModel.objects.get(pk=501).identifier, 'public identifier')
        call_command('refresh_video_counts', stdout=StringIO())
        user.userms.refresh_from_db()
        self.assertEqual(user.userms.video_num_total, 1)
        self.assertEqual(user.userms.video_num_nf, 1)

    def test_import_list_only_leaves_missing_metrics_null(self):
        fields = {'id', 'player', 'level', 'mode', 'state', 'software', 'timems', 'bv', 'pluck', 'upload_time', 'end_time', 'cl'}
        row = {key: value for key, value in self.video.items() if key in fields}
        write_json(self.root / 'videos.json', [row])
        manifest = read_json(self.root / 'manifest.json')
        manifest['videos'] = [file_entry(self.root, self.root / 'videos.json')]
        write_json(self.root / 'manifest.json', manifest)
        manifest, users = validate_snapshot(self.root)
        validate_import(self.root, manifest, users)
        import_snapshot_rows(self.root, manifest, users, 'admin-secret', 'user-secret')
        video = VideoModel.objects.get(pk=501)
        self.assertEqual(video.bvs, 2)
        self.assertEqual(video.pluck, 0.125)
        for field in ('left', 'right', 'double', 'left_ce', 'right_ce', 'double_ce', 'cl', 'ce', 'ioe', 'cell0'):
            self.assertIsNone(getattr(video, field), field)
        self.assertEqual(video.video.identifier, '')
        for url, params in (
            ('/api/userprofile/videolist', {'user_id': 48}),
            ('/api/video/infobulk', {'first': 501, 'count': 1}),
            ('/api/video/detailbulk', {'first': 501, 'count': 1}),
        ):
            with self.subTest(url=url):
                response = self.client.get(url, params)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()[0]['id'], 501)
                self.assertIsNone(response.json()[0]['cl'])

    @override_settings(DEBUG=True, E2E_TEST=True)
    def test_bad_snapshot_cannot_trigger_reset(self):
        write_json(self.root / 'videos.json', [])
        with patch('dangerzone.public_snapshot.call_command') as reset:
            with self.assertRaisesMessage(CommandError, 'checksum mismatch'):
                initialize_local_data(self.root, 'admin-secret', 'user-secret', stdout=StringIO())
        reset.assert_not_called()

    @override_settings(DEBUG=False, E2E_TEST=True)
    def test_production_cannot_trigger_reset(self):
        with patch('dangerzone.public_snapshot.call_command') as reset:
            with self.assertRaisesMessage(CommandError, 'never use on production'):
                initialize_local_data(self.root, 'admin-secret', 'user-secret', stdout=StringIO())
        reset.assert_not_called()

    @override_settings(DEBUG=True, E2E_TEST=True)
    def test_production_marker_blocks_import_even_with_debug_enabled(self):
        marker = self.root / '.production'
        marker.touch()
        with override_settings(PRODUCTION_MARK=marker):
            with patch('dangerzone.public_snapshot.call_command') as reset, patch('dangerzone.public_snapshot.get_local_snapshot_cache') as cache:
                with self.assertRaisesMessage(CommandError, 'never use on production'):
                    initialize_local_data(self.root, 'admin-secret', 'user-secret', stdout=StringIO())
            reset.assert_not_called()
            cache.assert_not_called()
