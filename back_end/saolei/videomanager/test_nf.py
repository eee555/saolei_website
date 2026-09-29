from types import SimpleNamespace

from django.test import SimpleTestCase

from utils.parser import MSVideoParser


class VideoModeTests(SimpleTestCase):
    def test_parser_preserves_mode_independently_of_flags_and_right_ce(self):
        for mode in (0, 5, 10, 11):
            for flag, right_ce in ((0, 0), (1, 0), (0, 1), (1, 1)):
                with self.subTest(mode=mode, flag=flag, right_ce=right_ce):
                    video = SimpleNamespace(mode=mode, flag=flag, rce=right_ce)
                    self.assertEqual(MSVideoParser.get_mode_from_BaseVideo(video), f'{mode:02d}')
