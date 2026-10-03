from io import StringIO
from unittest.mock import call, patch

from django.core.management import call_command, CommandError
from django.db import OperationalError
from django.test import SimpleTestCase

from utils.exceptions import ExceptionToResponse
from .models import VideoModel
from .utils import VideoParseError
from .view_utils import refresh_video


class RefreshVideosCommandTests(SimpleTestCase):
    def setUp(self):
        manager_patch = patch('videomanager.management.commands.refresh_videos.VideoModel.objects')
        self.manager = manager_patch.start()
        self.addCleanup(manager_patch.stop)
        refresh_patch = patch('videomanager.management.commands.refresh_videos.refresh_video')
        self.refresh = refresh_patch.start()
        self.addCleanup(refresh_patch.stop)
        self.videos = [
            VideoModel(pk=1, state='c', level='e', mode='00'),
            VideoModel(pk=2, state='b', level='c8_8_40', mode='10', ongoing_tournament=True),
        ]
        self.manager.select_related.return_value.order_by.return_value.iterator.return_value = iter(self.videos)

    def test_refreshes_each_instance_without_filtering_or_bulk_updates(self):
        output = StringIO()

        call_command('refresh_videos', stdout=output)

        self.manager.select_related.assert_called_once_with('video', 'player')
        self.manager.select_related.return_value.order_by.assert_called_once_with('pk')
        self.assertEqual(self.refresh.call_args_list, [call(video) for video in self.videos])
        self.manager.filter.assert_not_called()
        self.manager.update.assert_not_called()
        self.manager.bulk_update.assert_not_called()
        self.assertIn('2', output.getvalue())

    def test_parse_failure_is_skipped_and_later_videos_are_refreshed(self):
        self.refresh.side_effect = [VideoParseError('parse failed'), None]
        output = StringIO()
        errors = StringIO()

        call_command('refresh_videos', stdout=output, stderr=errors)

        self.assertEqual(self.refresh.call_args_list, [call(video) for video in self.videos])
        self.assertIn('录像#1解析失败，已跳过：parse failed', errors.getvalue())
        self.assertIn('已刷新 1 条录像，跳过 1 条', output.getvalue())

    def test_database_and_unclassified_errors_stop_refresh(self):
        for error in (OperationalError('connection lost'), ValueError('save failed')):
            with self.subTest(error=error):
                self.manager.select_related.return_value.order_by.return_value.iterator.return_value = iter(self.videos)
                self.refresh.reset_mock()
                self.refresh.side_effect = error

                with self.assertRaisesMessage(CommandError, f'录像#1刷新失败，已完成 0 条：{error}'):
                    call_command('refresh_videos', stdout=StringIO())
                self.refresh.assert_called_once_with(self.videos[0])


class RefreshVideoParseErrorTests(SimpleTestCase):
    def test_wraps_only_known_parser_errors_before_saving(self):
        for error in (ValueError('invalid data'), RuntimeError('analysis failed'), EOFError('truncated'), OverflowError('invalid timestamp'), ExceptionToResponse('file', 'type')):
            with self.subTest(error=error), patch('videomanager.view_utils.MSVideoParser', side_effect=error), patch.object(VideoModel, 'save') as save:
                with self.assertRaises(VideoParseError) as raised:
                    refresh_video(VideoModel(pk=1))
                self.assertIs(raised.exception.__cause__, error)
                save.assert_not_called()

    def test_serious_parser_stage_errors_are_not_wrapped(self):
        for error in (OperationalError('connection lost'), OSError('disk error'), MemoryError(), KeyboardInterrupt()):
            with self.subTest(error=error), patch('videomanager.view_utils.MSVideoParser', side_effect=error):
                with self.assertRaises(type(error)) as raised:
                    refresh_video(VideoModel(pk=1))
                self.assertIs(raised.exception, error)
