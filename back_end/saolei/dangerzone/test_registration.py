from django.db import IntegrityError
from django.test import override_settings, TestCase
from ninja.testing import TestClient

from msuser.models import UserMS
from userprofile.models import UserProfile
from .api import api


@override_settings(E2E_TEST=True, DEBUG=False, PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class RegistrationTests(TestCase):
    def setUp(self):
        self.api_client = TestClient(api)

    def user_data(self, user_id, **fields):
        return {'id': user_id, 'username': f'user{user_id}', 'email': f'user{user_id}@example.com', 'password': f'password{user_id}', **fields}

    def test_bulk_registration_preserves_order_fields_passwords_and_separate_userms(self):
        users = [self.user_data(user_id) for user_id in range(121, 100, -1)]
        users[0]['realname'] = '测试选手'

        response = self.api_client.post('/register_bulk', json={'users': users})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [user['id'] for user in users])
        self.assertEqual(UserMS.objects.count(), len(users))
        profiles = UserProfile.objects.in_bulk()
        self.assertEqual(len(profiles), len(users))
        self.assertEqual(len({profile.userms_id for profile in profiles.values()}), len(users))
        for data in users:
            profile = profiles[data['id']]
            self.assertEqual(profile.username, data['username'])
            self.assertEqual(profile.email, data['email'])
            self.assertEqual(profile.realname, data.get('realname', '匿名'))
            self.assertIsNotNone(profile.userms_id)
            self.assertTrue(profile.check_password(data['password']))

    def test_bulk_registration_rolls_back_users_and_userms_on_database_conflict(self):
        users = [self.user_data(101), self.user_data(102, username='user101')]

        with self.assertRaises(IntegrityError):
            self.api_client.post('/register_bulk', json={'users': users})

        self.assertFalse(UserProfile.objects.exists())
        self.assertFalse(UserMS.objects.exists())

    def test_reserved_name_rejected_for_single_and_bulk_registration(self):
        invalid = self.user_data(102, realname=' hidden ')
        for path, body in [('/register', invalid), ('/register_bulk', {'users': [self.user_data(101), invalid]})]:
            with self.subTest(path=path):
                response = self.api_client.post(path, json=body)
                self.assertEqual(response.status_code, 400)
                self.assertFalse(UserProfile.objects.exists())
                self.assertFalse(UserMS.objects.exists())

    def test_bulk_registration_rejects_empty_or_incomplete_input(self):
        for users in ([], [self.user_data(101), {'id': 102}]):
            with self.subTest(users=users):
                response = self.api_client.post('/register_bulk', json={'users': users})
                self.assertEqual(response.status_code, 422)
                self.assertFalse(UserProfile.objects.exists())
                self.assertFalse(UserMS.objects.exists())

    def test_bulk_registration_requires_e2e_mode_and_local_address(self):
        body = {'users': [self.user_data(101)]}
        with self.settings(E2E_TEST=False):
            self.assertEqual(self.api_client.post('/register_bulk', json=body).status_code, 403)
        self.assertEqual(self.api_client.post('/register_bulk', json=body, META={'REMOTE_ADDR': '203.0.113.5'}).status_code, 403)
        self.assertFalse(UserProfile.objects.exists())
        self.assertFalse(UserMS.objects.exists())

    def test_single_registration_keeps_its_existing_response_and_defaults(self):
        response = self.api_client.post('/register', json=self.user_data(101))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json())
        profile = UserProfile.objects.get(pk=101)
        self.assertEqual(profile.realname, '匿名')
        self.assertTrue(profile.check_password('password101'))
        self.assertEqual(UserMS.objects.count(), 1)
