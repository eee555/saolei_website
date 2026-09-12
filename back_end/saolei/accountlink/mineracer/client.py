from datetime import datetime, timedelta, timezone as datetime_timezone
from typing import Any

from django.conf import settings
from django.utils import timezone
import requests

from utils.exceptions import ExceptionToResponse
from .dtos import MINERACER_STATUS_CONFIRMED, MINERACER_STATUS_EXPIRED, MINERACER_STATUS_FAILED, MINERACER_STATUS_PENDING, MineracerAccountLinkPollResponse, MineracerAccountLinkStartResponse

MINERACER_START_URL = 'https://mineracer.com/api/partner/link/start'
MINERACER_POLL_URL = 'https://mineracer.com/api/partner/link/poll'


def get_mineracer_account_link_poll_interval_ms() -> int:
    return max(1, int(_get_config_value('POLL_INTERVAL_MS', 2500)))


def request_mineracer_account_link() -> MineracerAccountLinkStartResponse:
    config = _get_config()
    partner_key = _get_partner_key(config)
    if not partner_key:
        raise ExceptionToResponse('mineracer', 'not_configured', status_code=503)

    try:
        response = requests.post(
            config.get('START_URL') or MINERACER_START_URL,
            headers=_get_authorization_headers(partner_key),
            timeout=_get_timeout(config),
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        raise ExceptionToResponse('mineracer', 'timeout')
    except requests.exceptions.RequestException:
        raise ExceptionToResponse('mineracer', 'requestexception')
    except ValueError:
        raise ExceptionToResponse('mineracer', 'response')

    now = timezone.now()
    device_code = _get_required_string(data, ['deviceCode'])
    user_code = _get_required_string(data, ['userCode'])
    verification_uri = _get_required_string(data, ['verificationUri'])
    verification_uri_complete = _get_required_string(data, ['verificationUriComplete'])
    expires_at = _parse_expires_at(data, now)
    poll_interval_ms = _get_interval_ms(data) or get_mineracer_account_link_poll_interval_ms()
    return MineracerAccountLinkStartResponse(
        device_code=device_code,
        user_code=user_code,
        verification_uri=verification_uri,
        verification_uri_complete=verification_uri_complete,
        expires_at=expires_at,
        poll_interval_ms=poll_interval_ms,
    )


def poll_mineracer_account_link(device_code: str) -> MineracerAccountLinkPollResponse:
    config = _get_config()
    partner_key = _get_partner_key(config)
    if not partner_key:
        raise ExceptionToResponse('mineracer', 'not_configured', status_code=503)

    try:
        response = requests.post(
            config.get('POLL_URL') or config.get('STATUS_URL') or MINERACER_POLL_URL,
            headers=_get_authorization_headers(partner_key),
            json={'deviceCode': device_code},
            timeout=_get_timeout(config),
        )
        if response.status_code == 202:
            return MineracerAccountLinkPollResponse(status=MINERACER_STATUS_PENDING, retry_after_ms=_get_response_interval_ms(response))
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        raise ExceptionToResponse('mineracer', 'timeout')
    except requests.exceptions.RequestException:
        raise ExceptionToResponse('mineracer', 'requestexception')
    except ValueError:
        raise ExceptionToResponse('mineracer', 'response')

    status = _normalize_status(_get_optional_string(data, ['status', 'state']))
    userid = _get_optional_string(data, ['userId', 'Userid', 'userid', 'user_id', 'remote_userid'])
    if status == MINERACER_STATUS_CONFIRMED or userid:
        if not userid:
            raise ExceptionToResponse('mineracer', 'response')
        return MineracerAccountLinkPollResponse(status=MINERACER_STATUS_CONFIRMED, userid=userid, retry_after_ms=_get_interval_ms(data))
    if status == '':
        raise ExceptionToResponse('mineracer', 'response')
    return MineracerAccountLinkPollResponse(status=status, error_category=_get_optional_string(data, ['error_category', 'error', 'category']), retry_after_ms=_get_interval_ms(data))


def _get_config() -> dict[str, Any]:
    return getattr(settings, 'MINERACER_ACCOUNT_LINK', {})


def _get_config_value(key: str, default: Any) -> Any:
    return _get_config().get(key, default)


def _get_timeout(config: dict[str, Any]) -> float:
    return float(config.get('TIMEOUT', 5))


def _get_partner_key(config: dict[str, Any]) -> str:
    return str(config.get('PARTNER_KEY') or config.get('PRIVATE_KEY') or '').strip()


def _get_authorization_headers(partner_key: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {partner_key}'}


def _get_required_string(data: dict[str, Any], keys: list[str]) -> str:
    value = _get_optional_string(data, keys)
    if not value:
        raise ExceptionToResponse('mineracer', 'response')
    return value


def _get_optional_string(data: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = data.get(key)
        if value is not None:
            return str(value).strip()
    return ''


def _parse_expires_at(data: dict[str, Any], now: datetime) -> datetime:
    expires_at_timestamp_ms = data.get('expiresAt')
    if expires_at_timestamp_ms is not None:
        try:
            return datetime.fromtimestamp(int(expires_at_timestamp_ms) / 1000, tz=datetime_timezone.utc)
        except (TypeError, ValueError, OSError):
            raise ExceptionToResponse('mineracer', 'response')

    expires_at = _get_optional_string(data, ['expires_at', 'expires'])
    if expires_at:
        try:
            parsed = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        except ValueError:
            raise ExceptionToResponse('mineracer', 'response')
        return parsed if timezone.is_aware(parsed) else timezone.make_aware(parsed, datetime_timezone.utc)

    expires_in = data.get('expires_in')
    if expires_in is not None:
        try:
            return now + timedelta(seconds=int(expires_in))
        except (TypeError, ValueError):
            raise ExceptionToResponse('mineracer', 'response')

    return now + timedelta(seconds=int(_get_config_value('EXPIRES_SECONDS', 600)))


def _get_response_interval_ms(response: requests.Response) -> int | None:
    try:
        data = response.json()
    except ValueError:
        return None
    return _get_interval_ms(data)


def _get_interval_ms(data: dict[str, Any]) -> int | None:
    value = data.get('intervalMs') or data.get('interval_ms') or data.get('retry_after_ms')
    if value is None:
        return None
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        raise ExceptionToResponse('mineracer', 'response')


def _normalize_status(status: str) -> str:
    value = status.lower()
    if value in ['pending', 'wait', 'waiting', 'authorization_pending']:
        return MINERACER_STATUS_PENDING
    if value in ['confirmed', 'linked', 'success', 'successful', 'complete', 'completed', 'authorized']:
        return MINERACER_STATUS_CONFIRMED
    if value in ['expired', 'expired_token']:
        return MINERACER_STATUS_EXPIRED
    if value in ['failed', 'error', 'denied', 'rejected', 'cancelled', 'canceled']:
        return MINERACER_STATUS_FAILED
    return ''
