from unittest.mock import Mock, patch

from django.core.files.base import ContentFile
from django.test import SimpleTestCase

from config.text_choices import MS_TextChoices
from .exceptions import ExceptionToResponse
from .parser import MSVideoParser


class IncompleteVideoParserTests(SimpleTestCase):
    def test_incomplete_video_is_rejected_before_review_or_feature_analysis(self):
        for metadata_only in [False, True]:
            with self.subTest(metadata_only=metadata_only):
                video = Mock(is_completed=False)
                video.is_valid.return_value = 0
                parser_method = MSVideoParser.parse_video_metadata if metadata_only else MSVideoParser
                read_path = 'utils.parser.create_video_from_data' if metadata_only else 'utils.parser.MSVideoParser.read_file'
                with patch(read_path, return_value=(video, MS_TextChoices.Software.EVF)):
                    with self.assertRaises(ExceptionToResponse) as error:
                        parser_method(ContentFile(b'replay', name='incomplete.evf'))

                self.assertEqual(error.exception.body, {'type': 'error', 'object': 'file', 'category': 'incomplete'})
                video.is_valid.assert_not_called()
                video.analyse_for_features.assert_not_called()
