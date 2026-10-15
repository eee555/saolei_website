from contextlib import contextmanager

import httpx
from msgames_api import Client, MsgamesError, ParseError, RecordMetric, RequestError

from config.global_settings import MaxSizes
from utils.exceptions import ExceptionToResponse
from .utils import normalize_profile, normalize_replays


@contextmanager
def msgames_client():
    try:
        with Client(timeout=5, max_replay_bytes=MaxSizes.VIDEOFILE) as client:
            yield client
    except RequestError as exc:
        category = 'timeout' if isinstance(exc.__cause__, httpx.TimeoutException) else 'requestexception'
        raise ExceptionToResponse('import', category) from exc
    except (ParseError, ValueError) as exc:
        raise ExceptionToResponse('import', 'indexerror') from exc
    except MsgamesError as exc:
        raise ExceptionToResponse('import', 'requestexception') from exc


def fetch_profile(player_id: int) -> dict:
    with msgames_client() as client:
        return normalize_profile(client.get_profile(player_id), player_id)


def fetch_replays(player_id: int) -> list[dict]:
    with msgames_client() as client:
        records = [record for metric in RecordMetric for record in client.get_records(player_id, metric)]
        return normalize_replays(records, player_id)


def download_replay(url: str) -> bytes:
    with msgames_client() as client:
        return client.download_replay(url)
