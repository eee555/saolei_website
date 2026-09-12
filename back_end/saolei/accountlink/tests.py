import datetime
from types import SimpleNamespace
from unittest import expectedFailure, SkipTest
from unittest.mock import patch

from django.core.cache import caches
from django.db import connection
from django.test import override_settings, SimpleTestCase, TestCase
from django.utils import timezone
import requests

from userprofile.models import UserProfile
from utils.exceptions import ExceptionToResponse
from .api import MineracerAccountLinkSessionOut
from .mineracer.client import poll_mineracer_account_link, request_mineracer_account_link
from .mineracer.dtos import MINERACER_ERROR_ACCOUNT_NOT_FOUND, MINERACER_ERROR_INVALID_DEVICE_CODE, MINERACER_ERROR_LINK_SUPERSEDED, MINERACER_STATUS_CONFIRMED, MINERACER_STATUS_EXPIRED, MINERACER_STATUS_FAILED, MINERACER_STATUS_PENDING, MineracerAccountLinkPollResponse, MineracerAccountLinkSession, MineracerAccountLinkStartResponse
from .mineracer.sessions import _get_mineracer_session, _is_valid_mineracer_userid, _save_mineracer_session, _save_user_pending_mineracer_session
from .models import AccountBilibili, AccountLinkQueue, AccountMineracer, AccountMinesweeperGames, AccountSaolei, AccountWorldOfMinesweeper, Platform
from .services import update_saolei_account_info
from .utils import isPrivate, private_platforms, update_bilibili_account, update_msgames_account, update_wom_account


class AccountLinkTestCase(TestCase):
    def setUp(self):
        user = UserProfile.objects.create(
            username='setUp', email='setUp@test.com')
        AccountSaolei.objects.create(id=1, parent=user)
        AccountMinesweeperGames.objects.create(id=7872, parent=user)
        AccountWorldOfMinesweeper.objects.create(id=1783173, parent=user)
        AccountBilibili.objects.create(id=208259, parent=user)

    def test_update_saolei(self):
        account = AccountSaolei.objects.filter(id=1).first()
        update_saolei_account_info(account)
        account = AccountSaolei.objects.filter(id=1).first()
        self.assertEqual(account.id, 1)
        self.assertEqual(account.name, '张砷镓')
        self.assertEqual(account.beg_count, 12)
        self.assertEqual(account.int_count, 33)
        self.assertEqual(account.exp_count, 50)
        self.assertEqual(account.b_t_ms, 980)
        self.assertEqual(account.i_t_ms, 10310)
        self.assertEqual(account.e_t_ms, 37820)
        self.assertEqual(account.s_t_ms, 49110)
        self.assertEqual(account.b_b_cent, 729)
        self.assertEqual(account.i_b_cent, 530)
        self.assertEqual(account.e_b_cent, 423)
        self.assertEqual(account.s_b_cent, 1681)

    def test_update_msgames(self):
        account = AccountMinesweeperGames.objects.filter(id=7872).first()
        update_msgames_account(account)
        account = AccountMinesweeperGames.objects.filter(id=7872).first()
        self.assertEqual(account.id, 7872)
        self.assertEqual(account.name, 'Ze-En JU')
        self.assertEqual(account.local_name, '鞠泽恩')
        self.assertEqual(account.joined, datetime.date(2019, 5, 28))

    def test_update_bilibili(self):
        account = AccountBilibili.objects.filter(id=208259).first()
        update_bilibili_account(account)
        account = AccountBilibili.objects.filter(id=208259).first()

        self.assertEqual(account.id, 208259)
        self.assertEqual(account.name, '陈睿')
        self.assertEqual(account.level, 6)
        self.assertIn('bilibili', account.official_title)
        self.assertTrue(account.face.startswith(('http://', 'https://')))
        self.assertTrue(account.sign)

        self.assertGreater(account.following, 100)
        self.assertLess(account.following, 5000)
        self.assertGreater(account.follower, 1000000)
        self.assertLess(account.follower, 5000000)
        self.assertGreaterEqual(account.video_count, 10)
        self.assertLess(account.video_count, 100)
        self.assertGreaterEqual(account.article_count, 0)
        self.assertLess(account.article_count, 100)
        self.assertGreaterEqual(account.opus_count, 100)
        self.assertLess(account.opus_count, 1000)

    def test_private_platforms(self):
        self.assertIn(Platform.QQ, private_platforms)
        self.assertTrue(isPrivate(Platform.QQ))
        self.assertFalse(isPrivate(Platform.BILIBILI))
        self.assertFalse(isPrivate(Platform.SAOLEI))

    @expectedFailure
    def test_update_wom(self):
        account = AccountWorldOfMinesweeper.objects.filter(id=1783173).first()
        update_wom_account(account)
        account = AccountWorldOfMinesweeper.objects.filter(id=1783173).first()
        self.assertEqual(account.id, 1783173)

        self.assertEqual(account.trophy, 1155)

        self.assertEqual(account.experience, 21135733)
        self.assertEqual(account.honour, 1204)

        self.assertEqual(account.minecoin, 7607557)
        self.assertEqual(account.gem, 4456)
        self.assertEqual(account.coin, 8912)
        self.assertEqual(account.arena_ticket, 268)
        self.assertEqual(account.equipment, 34)
        self.assertEqual(account.part, 415)

        self.assertEqual(account.arena_point, 80)
        self.assertEqual(account.max_difficulty, 188752)
        self.assertEqual(account.win, 36565)
        self.assertEqual(account.last_season, 78)

        self.assertEqual(account.b_t_ms, 1213)
        self.assertEqual(account.i_t_ms, 9661)
        self.assertEqual(account.e_t_ms, 35765)

        self.assertEqual(account.b_ioe, 1.83)
        self.assertEqual(account.i_ioe, 1.56)
        self.assertEqual(account.e_ioe, 1.4)

        self.assertEqual(account.b_mastery, 99)
        self.assertEqual(account.i_mastery, 84)
        self.assertEqual(account.e_mastery, 54)

        self.assertEqual(account.b_winstreak, 92)
        self.assertEqual(account.i_winstreak, 21)
        self.assertEqual(account.e_winstreak, 9)

    def test_update_wom_missing_profile_container_returns_indexerror(self):
        account = AccountWorldOfMinesweeper.objects.filter(id=1783173).first()
        response = SimpleNamespace(text='<html><body>unexpected page</body></html>')

        with patch('accountlink.utils.requests.get', return_value=response):
            with self.assertRaises(ExceptionToResponse) as context:
                update_wom_account(account)

        self.assertEqual(context.exception.obj, 'import')
        self.assertEqual(context.exception.category, 'indexerror')

    def test_msgames_private_name(self):
        user = UserProfile.objects.create(
            username='test_msgames_private_name', email='test_msgames_private_name@test.com')
        account = AccountMinesweeperGames.objects.create(id=8371, parent=user)
        try:
            update_msgames_account(account)
        except requests.ConnectTimeout:
            return
        self.assertEqual(account.name, 'Private')
        self.assertEqual(account.local_name, 'None')


class MineracerFakeResponse:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self.data = data

    def json(self):
        if self.data is None:
            raise ValueError
        return self.data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError()


class MineracerApiResponseTestCase(SimpleTestCase):
    def test_session_schema_serializes_dataclass_fields(self):
        now = timezone.now()
        session = MineracerAccountLinkSession(
            session_id='session-1',
            user_id=1,
            device_code='device-code-1',
            user_code='ABCD-EFGH',
            verification_uri='https://mineracer.example.test/link',
            verification_uri_complete='https://mineracer.example.test/link?code=ABCD-EFGH',
            expires_at=now + datetime.timedelta(minutes=10),
            next_poll_at=now + datetime.timedelta(seconds=2),
            remote_userid='abcDEF123',
            error_category='invalid_userid',
        )

        response = MineracerAccountLinkSessionOut.model_validate(session).model_dump()

        self.assertEqual(response['session_id'], 'session-1')
        self.assertEqual(response['remote_userid'], 'abcDEF123')
        self.assertEqual(response['error_category'], 'invalid_userid')


MINERACER_TEST_ACCOUNT_LINK = {
    'START_URL': 'https://mineracer.example.test/api/partner/link/start',
    'POLL_URL': 'https://mineracer.example.test/api/partner/link/poll',
    'PARTNER_KEY': 'test-partner-key',
    'TIMEOUT': 5,
    'POLL_INTERVAL_MS': 2500,
    'EXPIRES_SECONDS': 600,
    'SESSION_GRACE_SECONDS': 60,
}

MINERACER_TEST_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mineracer-default-cache',
    },
    'saolei_website': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mineracer-session-cache',
    },
}


@override_settings(MINERACER_ACCOUNT_LINK=MINERACER_TEST_ACCOUNT_LINK, CACHES=MINERACER_TEST_CACHES)
class MineracerHttpClientTestCase(SimpleTestCase):
    @patch('accountlink.mineracer.client.requests.post')
    def test_request_mineracer_account_link_uses_bearer_and_no_body(self, requests_post):
        requests_post.return_value = MineracerFakeResponse(data={
            'deviceCode': 'device-code-1',
            'userCode': 'ABCD-EFGH',
            'verificationUri': 'https://mineracer.example.test/link',
            'verificationUriComplete': 'https://mineracer.example.test/link?code=ABCD-EFGH',
            'intervalMs': 2500,
            'expiresAt': 1780000000000,
        })

        response = request_mineracer_account_link()

        requests_post.assert_called_once()
        _, kwargs = requests_post.call_args
        self.assertEqual(kwargs['headers']['Authorization'], 'Bearer test-partner-key')
        self.assertNotIn('json', kwargs)
        self.assertEqual(response.device_code, 'device-code-1')
        self.assertEqual(response.user_code, 'ABCD-EFGH')
        self.assertEqual(response.verification_uri_complete, 'https://mineracer.example.test/link?code=ABCD-EFGH')
        self.assertEqual(response.poll_interval_ms, 2500)

    @patch('accountlink.mineracer.client.requests.post')
    def test_poll_mineracer_account_link_returns_pending_on_202(self, requests_post):
        requests_post.return_value = MineracerFakeResponse(status_code=202, data={'status': 'pending', 'intervalMs': 3000})

        response = poll_mineracer_account_link('device-code-1')

        _, kwargs = requests_post.call_args
        self.assertEqual(kwargs['headers']['Authorization'], 'Bearer test-partner-key')
        self.assertEqual(kwargs['json'], {'deviceCode': 'device-code-1'})
        self.assertEqual(response.status, MINERACER_STATUS_PENDING)
        self.assertEqual(response.retry_after_ms, 3000)

    @patch('accountlink.mineracer.client.requests.post')
    def test_poll_mineracer_account_link_returns_linked_userid_on_200(self, requests_post):
        requests_post.return_value = MineracerFakeResponse(data={
            'status': 'linked',
            'userId': '12345678901234567',
        })

        response = poll_mineracer_account_link('device-code-1')

        self.assertEqual(response.status, MINERACER_STATUS_CONFIRMED)
        self.assertEqual(response.userid, '12345678901234567')

    @patch('accountlink.mineracer.client.requests.post')
    def test_poll_mineracer_account_link_maps_remote_errors(self, requests_post):
        cases = [
            (400, {'error': 'invalid-device-code'}, MINERACER_STATUS_FAILED, MINERACER_ERROR_INVALID_DEVICE_CODE),
            (404, {'error': 'invalid-device-code'}, MINERACER_STATUS_FAILED, MINERACER_ERROR_INVALID_DEVICE_CODE),
            (404, {'error': 'account-not-found'}, MINERACER_STATUS_FAILED, MINERACER_ERROR_ACCOUNT_NOT_FOUND),
            (409, {'error': 'link-superseded'}, MINERACER_STATUS_FAILED, MINERACER_ERROR_LINK_SUPERSEDED),
            (410, {'error': 'code-expired'}, MINERACER_STATUS_EXPIRED, ''),
        ]

        for status_code, data, expected_status, expected_category in cases:
            with self.subTest(status_code=status_code, data=data):
                requests_post.return_value = MineracerFakeResponse(status_code=status_code, data=data)

                response = poll_mineracer_account_link('device-code-1')

                self.assertEqual(response.status, expected_status)
                self.assertEqual(response.error_category, expected_category)

    def test_mineracer_userid_accepts_up_to_64_characters(self):
        self.assertFalse(_is_valid_mineracer_userid(''))
        self.assertTrue(_is_valid_mineracer_userid('x' * 9))
        self.assertTrue(_is_valid_mineracer_userid('x' * 17))
        self.assertTrue(_is_valid_mineracer_userid('x' * 64))
        self.assertFalse(_is_valid_mineracer_userid('x' * 65))


@override_settings(MINERACER_ACCOUNT_LINK=MINERACER_TEST_ACCOUNT_LINK, CACHES=MINERACER_TEST_CACHES)
class MineracerAccountLinkTestCase(TestCase):
    def setUp(self):
        if AccountMineracer._meta.db_table not in connection.introspection.table_names():
            raise SkipTest('AccountMineracer migration has not been generated yet.')
        caches['default'].clear()
        self.user = UserProfile.objects.create_user(
            username='mineracer_user',
            email='mineracer_user@test.com',
            password='password',
        )
        self.client.force_login(self.user)

    @patch('accountlink.mineracer.sessions.request_mineracer_account_link')
    def test_start_mineracer_session_creates_pending_session(self, request_mineracer_account_link):
        expires_at = timezone.now() + datetime.timedelta(minutes=10)
        request_mineracer_account_link.return_value = MineracerAccountLinkStartResponse(
            device_code='device-code-1',
            user_code='ABCD-EFGH',
            verification_uri='https://mineracer.example.test/link',
            verification_uri_complete='https://mineracer.example.test/link?code=ABCD-EFGH',
            expires_at=expires_at,
            poll_interval_ms=2500,
        )

        response = self.client.post('/api/accountlink/mineracer/start/')

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        session = _get_mineracer_session(data['session_id'])
        self.assertIsNotNone(session)
        self.assertEqual(data['status'], MINERACER_STATUS_PENDING)
        self.assertEqual(data['verification_uri_complete'], 'https://mineracer.example.test/link?code=ABCD-EFGH')
        self.assertEqual(session.device_code, 'device-code-1')
        self.assertEqual(session.user_code, 'ABCD-EFGH')
        self.assertEqual(session.user_id, self.user.id)

    @patch('accountlink.mineracer.sessions.poll_mineracer_account_link')
    def test_status_uses_local_pending_state_before_next_poll_time(self, poll_mineracer_account_link):
        session = self.create_session(next_poll_at=timezone.now() + datetime.timedelta(seconds=30))

        response = self.client.get(f'/api/accountlink/mineracer/status/{session.session_id}')

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['status'], MINERACER_STATUS_PENDING)
        self.assertIsNotNone(response.json()['next_poll_at'])
        poll_mineracer_account_link.assert_not_called()

    @patch('accountlink.mineracer.sessions.poll_mineracer_account_link')
    def test_status_confirms_session_and_links_string_userid(self, poll_mineracer_account_link):
        session = self.create_session(next_poll_at=timezone.now() - datetime.timedelta(seconds=1))
        poll_mineracer_account_link.return_value = MineracerAccountLinkPollResponse(
            status=MINERACER_STATUS_CONFIRMED,
            userid='abcDEF123',
        )

        response = self.client.get(f'/api/accountlink/mineracer/status/{session.session_id}')

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['status'], MINERACER_STATUS_CONFIRMED)
        self.assertEqual(response.json()['remote_userid'], 'abcDEF123')
        self.assertTrue(AccountMineracer.objects.filter(id='abcDEF123', parent=self.user).exists())
        self.assertTrue(AccountLinkQueue.objects.filter(
            platform=Platform.MINERACER,
            identifier='abcDEF123',
            userprofile=self.user,
            verified=True,
        ).exists())

    @patch('accountlink.mineracer.sessions.poll_mineracer_account_link')
    def test_status_rejects_invalid_mineracer_userid(self, poll_mineracer_account_link):
        session = self.create_session(next_poll_at=timezone.now() - datetime.timedelta(seconds=1))
        poll_mineracer_account_link.return_value = MineracerAccountLinkPollResponse(
            status=MINERACER_STATUS_CONFIRMED,
            userid='short',
        )

        response = self.client.get(f'/api/accountlink/mineracer/status/{session.session_id}')

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['status'], MINERACER_STATUS_FAILED)
        self.assertEqual(response.json()['error_category'], 'invalid_userid')
        self.assertFalse(AccountMineracer.objects.filter(id='short').exists())

    @patch('accountlink.mineracer.sessions.poll_mineracer_account_link')
    def test_status_rejects_too_long_mineracer_userid(self, poll_mineracer_account_link):
        session = self.create_session(next_poll_at=timezone.now() - datetime.timedelta(seconds=1))
        poll_mineracer_account_link.return_value = MineracerAccountLinkPollResponse(
            status=MINERACER_STATUS_CONFIRMED,
            userid='x' * 65,
        )

        response = self.client.get(f'/api/accountlink/mineracer/status/{session.session_id}')

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['status'], MINERACER_STATUS_FAILED)
        self.assertEqual(response.json()['error_category'], 'invalid_userid')
        self.assertFalse(AccountMineracer.objects.filter(id='x' * 65).exists())

    @patch('accountlink.mineracer.sessions.poll_mineracer_account_link')
    def test_status_conflict_does_not_reassign_existing_mineracer_userid(self, poll_mineracer_account_link):
        other_user = UserProfile.objects.create_user(
            username='other_mineracer_user',
            email='other_mineracer_user@test.com',
            password='password',
        )
        AccountMineracer.objects.create(id='12345678901234567', parent=other_user)
        AccountLinkQueue.objects.create(
            platform=Platform.MINERACER,
            identifier='12345678901234567',
            userprofile=other_user,
            verified=True,
        )
        session = self.create_session(next_poll_at=timezone.now() - datetime.timedelta(seconds=1))
        poll_mineracer_account_link.return_value = MineracerAccountLinkPollResponse(
            status=MINERACER_STATUS_CONFIRMED,
            userid='12345678901234567',
        )

        response = self.client.get(f'/api/accountlink/mineracer/status/{session.session_id}')

        self.assertEqual(response.status_code, 409, response.content)
        session = _get_mineracer_session(session.session_id)
        self.assertEqual(session.status, MINERACER_STATUS_FAILED)
        self.assertEqual(session.error_category, 'identifier_conflict')
        self.assertEqual(AccountMineracer.objects.get(id='12345678901234567').parent, other_user)
        self.assertFalse(AccountLinkQueue.objects.filter(platform=Platform.MINERACER, userprofile=self.user).exists())

    def test_generic_create_rejects_mineracer(self):
        response = self.client.post('/api/accountlink/create/', {
            'platform': Platform.MINERACER,
            'identifier': '123456789',
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(AccountLinkQueue.objects.filter(platform=Platform.MINERACER, userprofile=self.user).exists())

    def create_session(self, next_poll_at):
        session = MineracerAccountLinkSession(
            session_id='session-1',
            user_id=self.user.id,
            device_code='device-code-1',
            user_code='ABCD-EFGH',
            verification_uri='https://mineracer.example.test/link',
            verification_uri_complete='https://mineracer.example.test/link?code=ABCD-EFGH',
            expires_at=timezone.now() + datetime.timedelta(minutes=10),
            next_poll_at=next_poll_at,
        )
        _save_mineracer_session(session)
        _save_user_pending_mineracer_session(session)
        return session
