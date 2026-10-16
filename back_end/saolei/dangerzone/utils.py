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


def validate_identifiers(identifiers, seen):
    if not isinstance(identifiers, list):
        raise ValueError('Expected a JSON array of identifiers')
    for identifier in identifiers:
        if not isinstance(identifier, str) or not 1 <= len(identifier) <= 128:
            raise ValueError('Invalid identifier')
        if identifier in seen:
            raise ValueError(f'Duplicated identifier: {identifier}')
        seen.add(identifier)


def validate_snapshot(root: Path):
    """在清库之前验证快照完整性、引用关系和重复 id。"""
    manifest = read_json(root / 'manifest.json')
    if manifest.get('version') not in (1, 2) or not manifest.get('complete'):
        raise ValueError('Snapshot download is incomplete or has an unsupported version')
    users = {}
    usernames = set()
    for rows in snapshot_pages(root, manifest, 'users'):
        for row in rows:
            if not isinstance(row.get('id'), int) or row['id'] <= 0 or row['id'] in users:
                raise ValueError('Invalid or duplicated user id')
            if not row.get('username') or row['username'] in usernames:
                raise ValueError('Invalid or duplicated username')
            users[row['id']] = {**row, 'identifiers': []}
            usernames.add(row['username'])
    if manifest['version'] == 2:
        if not isinstance(manifest.get('identifiers'), list):
            raise ValueError('Snapshot is missing identifier files')
        identifier_users = set()
        identifiers_seen = set()
        for entry, identifiers in zip(manifest['identifiers'], snapshot_pages(root, manifest, 'identifiers')):
            user_id = entry.get('user_id')
            if type(user_id) is not int or user_id not in users or user_id in identifier_users:
                raise ValueError('Invalid or duplicated identifier user id')
            validate_identifiers(identifiers, identifiers_seen)
            users[user_id]['identifiers'] = identifiers
            identifier_users.add(user_id)
        if identifier_users != users.keys() or len(identifiers_seen) != manifest.get('identifier_count'):
            raise ValueError('Snapshot identifier coverage or count does not match its manifest')
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
