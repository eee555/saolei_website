from datetime import timedelta
from urllib.parse import urlencode

from django.test import override_settings, TestCase
from django.utils import timezone

from msuser.models import UserMS
from userprofile.models import UserProfile


@override_settings(RATELIMIT_ENABLE=False)
class UserProfileAdminApiTests(TestCase):
    def setUp(self):
        self.staff = UserProfile.objects.create_user(
            username='profile_staff',
            email='profile_staff@example.com',
            password='password',
            is_staff=True,
            userms=UserMS.objects.create(),
        )
        self.userms = UserMS.objects.create(
            identifiers=['alpha', 'beta'],
            video_num_limit=100,
        )
        self.user = UserProfile.objects.create_user(
            username='profile_user',
            email='profile_user@example.com',
            password='password',
            realname='旧名',
            firstname='Old',
            lastname='Name',
            userms=self.userms,
        )
        self.client.force_login(self.staff)

    def patch_update(self, user_id, payload):
        return self.client.patch(
            f'/api/userprofile/admin/update/{user_id}',
            urlencode(payload),
            content_type='application/x-www-form-urlencoded',
        )

    def test_admin_get_user_profile(self):
        response = self.client.get(f'/api/userprofile/admin/detail/{self.user.id}')

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(data['username'], 'profile_user')
        self.assertEqual(data['firstname'], 'Old')
        self.assertEqual(data['lastname'], 'Name')
        self.assertEqual(data['userms_id'], self.userms.id)
        self.assertEqual(data['userms_identifiers'], ['alpha', 'beta'])
        self.assertEqual(data['userms_video_num_limit'], 100)

    def test_admin_update_user_profile(self):
        old_updated = timezone.now() - timedelta(days=1)
        UserProfile.objects.filter(id=self.user.id).update(date_updated=old_updated)

        response = self.patch_update(self.user.id, {
            'username': 'profile_user_new',
            'email': 'profile_user_new@example.com',
            'firstname': 'New',
            'lastname': 'Player',
            'realname': '新名',
            'signature': 'updated signature',
            'country': 'CN',
            'is_banned': True,
            'left_realname_n': 2,
            'left_avatar_n': 3,
            'left_signature_n': 4,
        })

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertEqual(data['username'], 'profile_user_new')
        self.assertEqual(data['firstname'], 'New')
        self.assertEqual(data['lastname'], 'Player')
        self.assertTrue(data['is_banned'])

        self.user.refresh_from_db()
        self.userms.refresh_from_db()
        self.assertEqual(self.user.email, 'profile_user_new@example.com')
        self.assertEqual(self.user.signature, 'updated signature')
        self.assertEqual(self.user.country, 'CN')
        self.assertEqual(self.user.left_realname_n, 2)
        self.assertEqual(self.user.left_avatar_n, 3)
        self.assertEqual(self.user.left_signature_n, 4)
        self.assertGreater(self.user.date_updated, old_updated)
        self.assertEqual(self.userms.video_num_limit, 100)

    def test_admin_update_writes_equal_value(self):
        old_updated = timezone.now() - timedelta(days=1)
        UserProfile.objects.filter(id=self.user.id).update(date_updated=old_updated)

        response = self.patch_update(self.user.id, {
            'realname': self.user.realname,
        })

        self.assertEqual(response.status_code, 200, response.content)
        self.user.refresh_from_db()
        self.assertGreater(self.user.date_updated, old_updated)

    def test_staff_cannot_update_another_staff_user(self):
        other_staff = UserProfile.objects.create_user(
            username='profile_other_staff',
            email='profile_other_staff@example.com',
            password='password',
            is_staff=True,
            userms=UserMS.objects.create(),
        )

        response = self.patch_update(other_staff.id, {
            'realname': 'blocked',
        })

        self.assertEqual(response.status_code, 403)
        other_staff.refresh_from_db()
        self.assertNotEqual(other_staff.realname, 'blocked')

    def test_non_staff_cannot_use_admin_api(self):
        self.client.force_login(self.user)

        get_response = self.client.get(f'/api/userprofile/admin/detail/{self.user.id}')
        patch_response = self.patch_update(self.user.id, {
            'realname': 'blocked',
        })

        self.assertEqual(get_response.status_code, 403)
        self.assertEqual(patch_response.status_code, 403)

    def test_legacy_staff_userprofile_urls_are_removed(self):
        get_response = self.client.get('/userprofile/get/', {'id': self.user.id})
        post_response = self.client.post('/userprofile/set/', {
            'id': self.user.id,
            'field': 'realname',
            'value': 'blocked',
        })

        self.assertEqual(get_response.status_code, 404)
        self.assertEqual(post_response.status_code, 404)
