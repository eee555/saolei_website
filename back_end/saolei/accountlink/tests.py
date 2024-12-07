from django.test import TestCase
from .models import AccountSaolei, AccountMinesweeperGames, AccountWorldOfMinesweeper
from .utils import update_saolei_account, update_msgames_account, update_wom_account
from userprofile.models import UserProfile
import datetime
from unittest import skip, expectedFailure

class AccountLinkTestCase(TestCase):
    def setUp(self):
        user = UserProfile.objects.create(username='setUp', email='setUp@test.com')
        AccountSaolei.objects.create(id=1,parent=user)
        AccountMinesweeperGames.objects.create(id=7872, parent=user)
        AccountWorldOfMinesweeper.objects.create(id=1783173, parent=user)

    def test_update_saolei(self):
        account = AccountSaolei.objects.filter(id=1).first()
        self.assertEqual(update_saolei_account(account, 0), '',)
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

    @expectedFailure
    def test_update_msgames(self):
        account = AccountMinesweeperGames.objects.filter(id=7872).first()
        self.assertEqual(update_msgames_account(account, 0), '')
        account = AccountMinesweeperGames.objects.filter(id=7872).first()
        self.assertEqual(account.id, 7872)
        self.assertEqual(account.name, 'Ze-En JU')
        self.assertEqual(account.local_name, '鞠泽恩')
        self.assertEqual(account.joined, datetime.date(2019,5,28))

    def test_update_wom(self):
        account = AccountWorldOfMinesweeper.objects.filter(id=1783173).first()
        self.assertEqual(update_wom_account(account, 0), '')
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

    @expectedFailure
    def test_msgames_private_name(self):
        user = UserProfile.objects.create(username='test_msgames_private_name', email='test_msgames_private_name@test.com')
        account = AccountMinesweeperGames.objects.create(id=8371, parent=user)
        self.assertEqual(update_msgames_account(account, 0), '')
        self.assertEqual(account.name, 'Private')
        self.assertEqual(account.local_name, 'None')