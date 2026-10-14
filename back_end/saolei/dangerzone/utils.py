import hashlib
import json
from pathlib import Path


DEFAULT_SNAPSHOT_DIR = Path(__file__).resolve().parents[1] / 'tmp' / 'public-data'


def read_json(path: Path):
    with path.open(encoding='utf-8') as file:
        return json.load(file)


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    with temporary.open('w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, allow_nan=False)
    temporary.replace(path)


def file_entry(root: Path, path: Path):
    return {'path': path.relative_to(root).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def snapshot_pages(root: Path, manifest: dict, kind: str):
    root = root.resolve()
    for entry in manifest[kind]:
        path = (root / entry['path']).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Snapshot path must stay inside its directory')
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError(f'Snapshot checksum mismatch: {path}')
        rows = read_json(path)
        if not isinstance(rows, list):
            raise ValueError(f'Expected a JSON array: {path}')
        yield rows


def validate_snapshot(root: Path):
    """在清库之前验证快照完整性、引用关系和重复 id。"""
    manifest = read_json(root / 'manifest.json')
    if manifest.get('version') != 1 or not manifest.get('complete'):
        raise ValueError('Snapshot download is incomplete or has an unsupported version')
    users = {}
    usernames = set()
    for rows in snapshot_pages(root, manifest, 'users'):
        for row in rows:
            if not isinstance(row.get('id'), int) or row['id'] <= 0 or row['id'] in users:
                raise ValueError('Invalid or duplicated user id')
            if not row.get('username') or row['username'] in usernames:
                raise ValueError('Invalid or duplicated username')
            users[row['id']] = row
            usernames.add(row['username'])
    video_ids = set()
    for rows in snapshot_pages(root, manifest, 'videos'):
        for row in rows:
            if not isinstance(row.get('id'), int) or row['id'] <= 0 or row['id'] in video_ids:
                raise ValueError('Invalid or duplicated video id')
            if row.get('player') not in users or row.get('ongoing_tournament'):
                raise ValueError(f'Invalid player or hidden video: {row["id"]}')
            for field in ('level', 'mode', 'state', 'software', 'timems', 'upload_time'):
                if field not in row:
                    raise ValueError(f'Video {row["id"]} is missing {field}')
            video_ids.add(row['id'])
    if len(users) != manifest['user_count'] or len(video_ids) != manifest['video_count']:
        raise ValueError('Snapshot row counts do not match its manifest')
    return manifest, users
