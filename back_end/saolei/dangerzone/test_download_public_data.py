from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from .download_public_data import download, PublicClient
from .public_snapshot import video_from_snapshot
from .utils import snapshot_pages, validate_snapshot


class PublicSnapshotNFTests(SimpleTestCase):
    def test_video_list_requests_wait_after_the_previous_response(self):
        client = PublicClient('https://example.invalid', interval=0.01)
        now = 1000.0
        starts = []
        completions = []
        durations = iter((2.0, 0.1, 0.1))
        response = Mock(status_code=200)
        response.json.return_value = []

        def sleep(seconds):
            nonlocal now
            self.assertGreaterEqual(seconds, 0)
            now += seconds

        def get(*args, **kwargs):
            nonlocal now
            starts.append(now)
            now += next(durations)
            completions.append(now)
            return response

        with patch('dangerzone.download_public_data.time.monotonic', side_effect=lambda: now), patch('dangerzone.download_public_data.time.sleep', side_effect=sleep), patch.object(client.session, 'get', side_effect=get):
            for user_id in (2, 48, 99):
                self.assertEqual(client.get('/api/userprofile/videolist', {'user_id': user_id}), [])
        self.assertEqual(client.interval, 1.25)
        for start, previous_completion in zip(starts[1:], completions):
            self.assertAlmostEqual(start - previous_completion, 1.25)

    def test_download_and_import_preserve_list_right_ce_without_inventing_missing_values(self):
        videos = [
            {'id': video_id, 'level': 'b', 'mode': '00', 'state': 'c', 'software': 'e', 'timems': 1000, 'bv': 4, 'upload_time': '2026-10-05T12:34:00Z', **fields}
            for video_id, fields in enumerate(({'right_ce': 0}, {'right_ce': 3}, {}), start=1)
        ]

        def get(path, params):
            if path.endswith('/infoupdated'):
                return [2, 48]
            if path.endswith('/infobulk'):
                return [{'id': 2, 'username': 'admin'}, {'id': 48, 'username': 'user'}]
            if path.endswith('/videolist'):
                return videos if params['user_id'] == 48 else []
            self.assertEqual(path, '/api/video/detailbulk')
            return [{**row, 'player': 48, 'right_ce': 2 if row['id'] == 2 else None} for row in videos]

        for skip_details in (False, True):
            with self.subTest(skip_details=skip_details), TemporaryDirectory() as directory:
                root = Path(directory)
                client = PublicClient('https://example.invalid')
                with patch.object(client, 'get', side_effect=get) as request, redirect_stdout(StringIO()):
                    download(root, client, skip_details=skip_details)
                manifest, _ = validate_snapshot(root)
                rows = next(snapshot_pages(root, manifest, 'videos'))
                self.assertEqual([row['right_ce'] for row in rows], [0, 3 if skip_details else 2, None])
                self.assertEqual([video_from_snapshot(row).right_ce for row in rows], [0, 3 if skip_details else 2, None])
                self.assertEqual(manifest['missing_detail_video_ids'], [1, 2, 3] if skip_details else [])
                if skip_details:
                    self.assertNotIn('/api/video/detailbulk', [call.args[0] for call in request.call_args_list])
