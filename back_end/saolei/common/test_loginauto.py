from unittest.mock import patch

from django.test import override_settings, TestCase

from userprofile.models import UserProfile


@override_settings(RATELIMIT_ENABLE=False)
class AutoLoginTests(TestCase):
    def test_startup_returns_all_anchors_for_guests_and_authenticated_users(self):
        anchors = {'std:et': {'value': 30000, 'sample_count': 20}, 'future': {'value': 1}}
        with patch('common.api.TopRankingCache.get_anchors', return_value=anchors):
            with self.assertNumQueries(0):
                response = self.client.get('/api/common/loginauto')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'user': None, 'top_anchors': anchors})
            self.assertIn('no-store', response['Cache-Control'])
            self.assertIn('private', response['Cache-Control'])
            user = UserProfile.objects.create_user(username='startup-user', password='test-password')
            self.client.force_login(user)
            response = self.client.get('/api/common/loginauto')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['user']['id'], user.pk)
            self.assertNotIn('password', response.json()['user'])
            self.assertEqual(response.json()['top_anchors'], anchors)
