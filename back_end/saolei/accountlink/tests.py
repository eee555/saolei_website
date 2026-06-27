import datetime
from unittest import expectedFailure

from django.test import TestCase
import requests

from userprofile.models import UserProfile
from .models import AccountBilibili, AccountMinesweeperGames, AccountSaolei, AccountWorldOfMinesweeper, Platform
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
