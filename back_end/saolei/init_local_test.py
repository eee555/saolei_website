# e2e测试时用于初始化数据库
# 清空数据，注册一个管理员账号和一个普通账号
# 管理员账号：admin, admin123456
# 普通账号：user, user123456

import argparse
import json
import sys
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = 'http://127.0.0.1:8000/dangerzone/'
DEFAULT_TIMEOUT = 10


@dataclass(frozen=True)
class Account:
    user_id: int
    username: str
    email: str
    password: str


def post_json(base_url: str, path: str, payload: dict | None = None, timeout: int = DEFAULT_TIMEOUT) -> bytes:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'

    request = Request(
        urljoin(base_url, path),
        data=data,
        headers=headers,
        method='POST',
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read()
    except HTTPError as error:
        body = error.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'POST {request.full_url} failed with HTTP {error.code}: {body}') from error
    except URLError as error:
        raise RuntimeError(f'POST {request.full_url} failed: {error.reason}') from error


def register(base_url: str, account: Account, timeout: int) -> None:
    post_json(
        base_url,
        'register',
        {
            'id': account.user_id,
            'username': account.username,
            'email': account.email,
            'password': account.password,
        },
        timeout,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Flush local database through dangerzone APIs and create default users.',
    )
    parser.add_argument('--base-url', default=DEFAULT_BASE_URL)
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument('--admin-id', type=int, default=1)
    parser.add_argument('--admin-username', default='admin')
    parser.add_argument('--admin-email', default='admin@example.com')
    parser.add_argument('--admin-password', default='admin123456')
    parser.add_argument('--user-id', type=int, default=2)
    parser.add_argument('--user-username', default='user')
    parser.add_argument('--user-email', default='user@example.com')
    parser.add_argument('--user-password', default='user123456')
    args = parser.parse_args()

    base_url = args.base_url.rstrip('/') + '/'
    admin = Account(args.admin_id, args.admin_username, args.admin_email, args.admin_password)
    user = Account(args.user_id, args.user_username, args.user_email, args.user_password)

    try:
        print(f'Flushing database via {base_url}flush_database')
        post_json(base_url, 'flush_database', timeout=args.timeout)

        print(f'Registering staff user: {admin.username} ({admin.email})')
        register(base_url, admin, args.timeout)
        post_json(base_url, 'setstaff', {'id': admin.user_id}, args.timeout)

        print(f'Registering normal user: {user.username} ({user.email})')
        register(base_url, user, args.timeout)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1

    print('Done.')
    print(f'Admin: id={admin.user_id}, username={admin.username}, password={admin.password}')
    print(f'User: id={user.user_id}, username={user.username}, password={user.password}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
