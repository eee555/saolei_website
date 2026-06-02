"""
Tests for the mine-sweeper captcha (userprofile.utils.judge_captcha and
userprofile.views.refresh_captcha).

Uses django.test.TestCase to match the project's existing test style
(see tests/test_dangerzone.py).
"""
from django.test import Client, TestCase
from django_redis import get_redis_connection

from userprofile.mine_captcha_puzzles import PUZZLES
from userprofile.utils import judge_captcha


REDIS_KEY_PREFIX = 'mine_captcha:'
_WIDTH = 5  # bottom row size (matches PUZZLES today)


def _set_puzzle(hashkey: str, puzzle_idx: int, ttl: int = 900) -> None:
    conn = get_redis_connection('saolei_website')
    conn.set(f'{REDIS_KEY_PREFIX}{hashkey}', str(puzzle_idx), ex=ttl)


def _redis_has(hashkey: str) -> bool:
    conn = get_redis_connection('saolei_website')
    return conn.exists(f'{REDIS_KEY_PREFIX}{hashkey}') == 1


def _safe_answer(puzzle_idx: int) -> str:
    """Build the correct answer string (non-mine indices, sorted)."""
    mines = set(PUZZLES[puzzle_idx][1])
    safe = sorted(set(range(_WIDTH)) - mines)
    return ','.join(str(i) for i in safe)


class _RedisCleanupMixin:
    """Wipe test_* keys before and after every test."""
    def setUp(self):
        super().setUp()
        conn = get_redis_connection('saolei_website')
        for key in conn.scan_iter(f'{REDIS_KEY_PREFIX}test_*'):
            conn.delete(key)

    def tearDown(self):
        conn = get_redis_connection('saolei_website')
        for key in conn.scan_iter(f'{REDIS_KEY_PREFIX}test_*'):
            conn.delete(key)
        super().tearDown()


class JudgeCaptchaTests(_RedisCleanupMixin, TestCase):
    # PUZZLES[0]: mines=[0,2,4]  ->  safe answer = "1,3"

    def test_correct_answer_returns_true_and_deletes_key(self):
        _set_puzzle('test_a', 0)
        self.assertTrue(judge_captcha('1,3', 'test_a'))
        self.assertFalse(_redis_has('test_a'))

    def test_correct_answer_order_independent(self):
        _set_puzzle('test_b', 0)
        self.assertTrue(judge_captcha('3,1', 'test_b'))

    def test_missing_one_returns_false_and_deletes_key(self):
        _set_puzzle('test_c', 0)
        self.assertFalse(judge_captcha('1', 'test_c'))
        self.assertFalse(_redis_has('test_c'))

    def test_extra_open_including_mine_returns_false(self):
        _set_puzzle('test_d', 0)
        # Opening a mine cell (0) plus the safe cells must fail.
        self.assertFalse(judge_captcha('0,1,3', 'test_d'))

    def test_unknown_hashkey_returns_false(self):
        self.assertFalse(judge_captcha('1,3', 'test_does_not_exist'))

    def test_empty_input_returns_false(self):
        _set_puzzle('test_e', 0)
        self.assertFalse(judge_captcha('', 'test_e'))

    def test_dirty_input_returns_false_without_exception(self):
        _set_puzzle('test_f', 0)
        # Non-numeric token must NOT raise; it must be rejected.
        self.assertFalse(judge_captcha('1,abc,3', 'test_f'))

    def test_out_of_range_returns_false(self):
        _set_puzzle('test_g', 0)
        self.assertFalse(judge_captcha('1,5', 'test_g'))

    def test_negative_index_returns_false(self):
        _set_puzzle('test_h', 0)
        self.assertFalse(judge_captcha('-1,1,3', 'test_h'))

    def test_all_puzzles_have_correct_safe_answer(self):
        for idx in range(len(PUZZLES)):
            key = f'test_p{idx}'
            _set_puzzle(key, idx)
            self.assertTrue(
                judge_captcha(_safe_answer(idx), key),
                msg=f'puzzle {idx} safe answer failed',
            )


class RefreshCaptchaTests(_RedisCleanupMixin, TestCase):
    def test_refresh_returns_hashkey_and_top(self):
        resp = self.client.get('/userprofile/refresh_captcha/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 100)
        self.assertIn('hashkey', data)
        self.assertGreater(len(data['hashkey']), 8)
        self.assertIsInstance(data['top'], list)
        self.assertEqual(len(data['top']), _WIDTH)

        # The redis key exists with TTL close to 900s
        conn = get_redis_connection('saolei_website')
        ttl = conn.ttl(f"{REDIS_KEY_PREFIX}{data['hashkey']}")
        self.assertGreater(ttl, 800)
        self.assertLessEqual(ttl, 900)

        # Cleanup (TTL pattern: hashkey is a uuid, not test_*, so clean explicitly)
        conn.delete(f"{REDIS_KEY_PREFIX}{data['hashkey']}")

    def test_returned_top_matches_a_known_puzzle(self):
        resp = self.client.get('/userprofile/refresh_captcha/')
        top = tuple(resp.json()['top'])
        known = {tuple(p[0]) for p in PUZZLES}
        self.assertIn(top, known)

        # Cleanup
        conn = get_redis_connection('saolei_website')
        conn.delete(f"{REDIS_KEY_PREFIX}{resp.json()['hashkey']}")
