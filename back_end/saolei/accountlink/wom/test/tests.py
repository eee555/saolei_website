from copy import deepcopy
import json
from pathlib import Path
import ssl
from unittest.mock import AsyncMock, MagicMock, patch

from django.test import SimpleTestCase, TestCase
from wom_api import AuthorizationError, ConnectionError as WomConnectionError, ProtocolError, RequestTimeout, ServerError

from accountlink.api import AccountWoMOut
from accountlink.models import AccountWorldOfMinesweeper
from accountlink.services import update_wom_account
from userprofile.models import UserProfile
from utils.exceptions import ExceptionToResponse
from ..client import fetch_wom_profile
from ..utils import normalize_wom_profile


def public_profile():
    return json.loads(Path(__file__).with_name('public_profile.json').read_text(encoding='utf-8'))


class WomProfileMappingTests(SimpleTestCase):
    def test_public_sample_preserves_existing_units_and_adds_statistics(self):
        data = normalize_wom_profile(public_profile(), 1783173)
        self.assertEqual(data['b_t_ms'], 1213)
        self.assertEqual(data['i_t_ms'], 9661)
        self.assertEqual(data['e_t_ms'], 35765)
        self.assertEqual([data[f'{level}_ioe'] for level in ('b', 'i', 'e')], [1.83, 1.56, 1.4])
        self.assertEqual(data['last_season'], 78)
        self.assertEqual(data['b_endurance_ms'], 582000)
        self.assertEqual(data['i_endurance_ms'], 2591000)
        self.assertEqual(data['e_endurance_ms'], 13888000)
        self.assertEqual([data[f'{level}_ng_t_ms'] for level in ('b', 'i', 'e')], [1282, 16720, 48877])
        self.assertEqual(data['experience_total'], 21163169)
        self.assertEqual(data['minecoin_total'], 3901062)
        self.assertEqual(data['gem_total'], 22780)
        self.assertEqual(data['arena_coin_total'], 0)
        self.assertEqual(data['game_count'], 111645)
        self.assertEqual(data['win_nf'], 16207)
        self.assertEqual(data['play_time_ms'], 2808349910)
        self.assertEqual(data['arena_play_time_ms'], 65626047)
        self.assertEqual(data['bbbv_total'], 5060476)
        self.assertEqual(data['season_count'], 16)
        self.assertEqual([data[f'{level}_win'] for level in ('b', 'i', 'e')], [12361, 4958, 2553])
        self.assertEqual([data[f'{level}_ng_win'] for level in ('b', 'i', 'e')], [245, 66, 548])

    def test_inventory_and_identity_text_are_never_imported(self):
        profile = public_profile()
        profile['user'].update({'username': 'Unreviewed name', 'country': 'XX'})
        profile['userStat'].update({'coins': 1, 'items': {'16': 2, '1': 3}, 'eq': {'0': '550'}})
        data = normalize_wom_profile(profile, 1783173)
        self.assertTrue({'honour', 'minecoin', 'gem', 'coin', 'arena_ticket', 'equipment', 'part', 'name', 'country', 'items', 'eq'}.isdisjoint(data))

    def test_absent_pb_is_null_and_missing_endurance_uses_default(self):
        profile = public_profile()
        profile['timeResults'].pop('12')
        profile['effResults'] = {}
        profile['userStat'].update({'end1': 0, 'end2': None, 'winsNf': 0})
        data = normalize_wom_profile(profile, 1783173)
        self.assertIsNone(data['i_ng_t_ms'])
        self.assertIsNone(data['b_ioe'])
        self.assertEqual(data['b_endurance_ms'], 86400000)
        self.assertEqual(data['i_endurance_ms'], 86400000)
        self.assertEqual(data['win_nf'], 0)

    def test_missing_statistics_do_not_clear_previous_values(self):
        profile = {'user': {'id': 1}, 'userStat': None, 'noUserStatExp': 42}
        self.assertEqual(normalize_wom_profile(profile, 1), {'experience': 42})
        profile['noUserStatExp'] = -1
        with self.assertRaises(ValueError):
            normalize_wom_profile(profile, 1)
        partial = {'user': {'id': 1}, 'userStat': {'winsAll': 0}}
        self.assertEqual(normalize_wom_profile(partial, 1), {'win': 0})

    def test_only_lifetime_durations_accept_64_bit_values(self):
        profile = public_profile()
        profile['userStat'].update({'timeAll': 2 ** 40, 'arenaDuration': 2 ** 39, 'coinsAll': 2 ** 32 - 1})
        data = normalize_wom_profile(profile, 1783173)
        self.assertEqual(data['play_time_ms'], 2 ** 40)
        self.assertEqual(data['arena_play_time_ms'], 2 ** 39)
        self.assertEqual(data['minecoin_total'], 2 ** 32 - 1)

    def test_narrowed_counter_limits_are_checked_before_saving(self):
        for key, value in [('games', 2 ** 32), ('bbbvAll', 2 ** 32), ('expAll', 2 ** 32), ('coinsAll', 2 ** 32), ('gemsAll', 2 ** 32), ('arenaCoinsAll', 2 ** 32), ('winsNf', 2 ** 32), ('wins1', 2 ** 32), ('seasons', 2 ** 16), ('timeAll', 2 ** 63), ('arenaDuration', 2 ** 63)]:
            profile = public_profile()
            profile['userStat'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                normalize_wom_profile(profile, 1783173)

    def test_malformed_identity_records_or_counters_are_rejected(self):
        original = public_profile()
        for key, value in [('games', True), ('games', 1.5), ('games', -1), ('games', 2 ** 63), ('end1', 86400001), ('lastSeason', 20000)]:
            profile = deepcopy(original)
            profile['userStat'][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                normalize_wom_profile(profile, 1783173)
        for user_id in (True, '1783173', 1):
            profile = deepcopy(original)
            profile['user']['id'] = user_id
            with self.subTest(user_id=user_id), self.assertRaises(ValueError):
                normalize_wom_profile(profile, 1783173)
        for records in ([], {'1': {}}):
            profile = deepcopy(original)
            profile['timeResults'] = records
            with self.subTest(records=records), self.assertRaises(ValueError):
                normalize_wom_profile(profile, 1783173)


class WomClientTests(SimpleTestCase):
    async def test_anonymous_client_fetches_once_and_closes(self):
        client = MagicMock()
        client.get_user_detail_data = AsyncMock(return_value=public_profile())
        manager = MagicMock()
        manager.__aenter__ = AsyncMock(return_value=client)
        manager.__aexit__ = AsyncMock(return_value=None)
        with patch('accountlink.wom.client.WomClient', return_value=manager) as constructor:
            data = await fetch_wom_profile(1783173)
        constructor.assert_called_once()
        self.assertEqual(constructor.call_args.kwargs['timeout'], 5)
        self.assertEqual(constructor.call_args.kwargs['ssl_context'].verify_mode, ssl.CERT_REQUIRED)
        client.get_user_detail_data.assert_awaited_once_with(userId=1783173, popupRandId=None)
        manager.__aexit__.assert_awaited_once()
        self.assertEqual(data['b_ng_t_ms'], 1282)

    async def test_external_errors_are_mapped_and_client_is_closed(self):
        for exception, category in [(RequestTimeout, 'timeout'), (AuthorizationError, 'requestexception'), (WomConnectionError, 'requestexception'), (ProtocolError, 'requestexception'), (ServerError, 'requestexception')]:
            client = MagicMock()
            client.get_user_detail_data = AsyncMock(side_effect=exception('test error'))
            manager = MagicMock()
            manager.__aenter__ = AsyncMock(return_value=client)
            manager.__aexit__ = AsyncMock(return_value=None)
            with self.subTest(exception=exception), patch('accountlink.wom.client.WomClient', return_value=manager):
                with self.assertRaises(ExceptionToResponse) as context:
                    await fetch_wom_profile(1783173)
            self.assertEqual(context.exception.category, category)
            manager.__aexit__.assert_awaited_once()

    async def test_invalid_response_maps_to_existing_parse_error(self):
        client = MagicMock()
        client.get_user_detail_data = AsyncMock(return_value={})
        manager = MagicMock()
        manager.__aenter__ = AsyncMock(return_value=client)
        manager.__aexit__ = AsyncMock(return_value=None)
        with patch('accountlink.wom.client.WomClient', return_value=manager):
            with self.assertRaises(ExceptionToResponse) as context:
                await fetch_wom_profile(1783173)
        self.assertEqual(context.exception.category, 'indexerror')


class WomAccountTests(TestCase):
    def setUp(self):
        user = UserProfile.objects.create(username='wom_test', email='wom_test@test.com')
        AccountWorldOfMinesweeper.objects.create(id=1783173, parent=user)

    def test_update_wom(self):
        account = AccountWorldOfMinesweeper.objects.filter(id=1783173).first()
        data = normalize_wom_profile(public_profile(), account.id)
        old_update_time = account.update_time
        data['play_time_ms'] = 2 ** 40
        with patch('accountlink.services.fetch_wom_profile', new=AsyncMock(return_value=data)):
            update_wom_account(account)
        account = AccountWorldOfMinesweeper.objects.filter(id=1783173).first()
        self.assertEqual(account.id, 1783173)
        self.assertEqual(account.trophy, 1130)
        self.assertEqual(account.experience, 21135733)
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
        self.assertEqual(account.e_mastery, 45)
        self.assertEqual(account.b_winstreak, 92)
        self.assertEqual(account.i_winstreak, 21)
        self.assertEqual(account.e_winstreak, 7)
        self.assertEqual(account.b_endurance_ms, 582000)
        self.assertEqual(account.e_ng_t_ms, 48877)
        self.assertEqual(account.play_time_ms, 2 ** 40)
        self.assertGreater(account.update_time, old_update_time)
        output = AccountWoMOut.from_orm(account).model_dump()
        self.assertEqual(output['e_ng_t_ms'], 48877)
        self.assertEqual(output['minecoin_total'], 3901062)
        self.assertTrue({'honour', 'minecoin', 'gem', 'coin', 'arena_ticket', 'equipment', 'part'}.isdisjoint(output))

    def test_wom_endurance_defaults_and_empty_api_records(self):
        account = AccountWorldOfMinesweeper.objects.get(id=1783173)
        endurance_fields = ['b_endurance_ms', 'i_endurance_ms', 'e_endurance_ms']
        self.assertEqual([getattr(account, field) for field in endurance_fields], [86400000] * 3)
        for field in endurance_fields:
            self.assertFalse(AccountWorldOfMinesweeper._meta.get_field(field).null)
            self.assertEqual(AccountWoMOut.model_json_schema()['properties'][field]['type'], 'integer')
        profile = public_profile()
        profile['userStat'].update({'end1': 0, 'end2': None, 'end3': 0})
        data = normalize_wom_profile(profile, account.id)
        with patch('accountlink.services.fetch_wom_profile', new=AsyncMock(return_value=data)):
            update_wom_account(account)
        account.refresh_from_db()
        output = AccountWoMOut.from_orm(account).model_dump()
        self.assertEqual([output[field] for field in endurance_fields], [86400000] * 3)

    def test_update_wom_counter_ranges(self):
        account = AccountWorldOfMinesweeper.objects.get(id=1783173)
        profile = public_profile()
        profile['userStat'].update({'coinsAll': 2 ** 32 - 1, 'bbbvAll': 2 ** 32 - 1, 'seasons': 2 ** 16 - 1, 'timeAll': 2 ** 40})
        data = normalize_wom_profile(profile, account.id)
        with patch('accountlink.services.fetch_wom_profile', new=AsyncMock(return_value=data)):
            update_wom_account(account)
        account.refresh_from_db()
        self.assertEqual(account.minecoin_total, 2 ** 32 - 1)
        self.assertEqual(account.bbbv_total, 2 ** 32 - 1)
        self.assertEqual(account.season_count, 2 ** 16 - 1)
        self.assertEqual(account.play_time_ms, 2 ** 40)

    def test_update_wom_failure_keeps_existing_data(self):
        account = AccountWorldOfMinesweeper.objects.filter(id=1783173).first()
        account.trophy = 123
        account.save(update_fields=['trophy'])
        old_update_time = account.update_time
        error = ExceptionToResponse(obj='import', category='timeout')
        with patch('accountlink.services.fetch_wom_profile', new=AsyncMock(side_effect=error)):
            with self.assertRaises(ExceptionToResponse):
                update_wom_account(account)
        account.refresh_from_db()
        self.assertEqual(account.trophy, 123)
        self.assertEqual(account.update_time, old_update_time)
