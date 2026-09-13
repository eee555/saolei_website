from datetime import datetime, timezone as datetime_timezone
from typing import Any

from django.conf import settings
import requests

from utils.exceptions import ExceptionToResponse
from .dtos import MINERACER_ERROR_ACCOUNT_NOT_FOUND, MINERACER_ERROR_INVALID_DEVICE_CODE, MINERACER_ERROR_LINK_SUPERSEDED, MINERACER_STATUS_CONFIRMED, MINERACER_STATUS_EXPIRED, MINERACER_STATUS_FAILED, MINERACER_STATUS_PENDING, MineracerAccountLinkPollResponse, MineracerAccountLinkStartResponse

MINERACER_POLL_ERROR_CATEGORIES = {
    'account-not-found': MINERACER_ERROR_ACCOUNT_NOT_FOUND,
    'invalid-device-code': MINERACER_ERROR_INVALID_DEVICE_CODE,
    'link-superseded': MINERACER_ERROR_LINK_SUPERSEDED,
}


def request_mineracer_account_link() -> MineracerAccountLinkStartResponse:
    partner_key = settings.MINERACER_PARTNER_KEY
    if not partner_key:
        raise ExceptionToResponse('mineracer', 'not_configured', status_code=503)

    try:
        response = requests.post(
            settings.MINERACER_START_URL,
            headers=_get_authorization_headers(partner_key),
            timeout=settings.MINERACER_TIMEOUT,
        )
        response.raise_for_status()
        data = _get_response_data(response)
    except requests.exceptions.Timeout:
        raise ExceptionToResponse('mineracer', 'timeout')
    except requests.exceptions.RequestException:
        raise ExceptionToResponse('mineracer', 'requestexception')
    except ValueError:
        raise ExceptionToResponse('mineracer', 'response')

    return MineracerAccountLinkStartResponse(
        device_code=_get_required_string(data, 'deviceCode'),
        user_code=_get_required_string(data, 'userCode'),
        verification_uri=_get_required_string(data, 'verificationUri'),
        verification_uri_complete=_get_required_string(data, 'verificationUriComplete'),
        expires_at=_parse_expires_at(data),
        poll_interval_ms=_get_required_interval_ms(data),
    )


def poll_mineracer_account_link(device_code: str) -> MineracerAccountLinkPollResponse:
    partner_key = settings.MINERACER_PARTNER_KEY
    if not partner_key:
        raise ExceptionToResponse('mineracer', 'not_configured', status_code=503)

    try:
        response = requests.post(
            settings.MINERACER_POLL_URL,
            headers=_get_authorization_headers(partner_key),
            json={'deviceCode': device_code},
            timeout=settings.MINERACER_TIMEOUT,
        )
        if response.status_code == 202:
            return _get_pending_poll_response(response)
        if response.status_code == 200:
            return _get_linked_poll_response(response)
        if response.status_code >= 400:
            return _get_poll_error_response(response)
        raise ExceptionToResponse('mineracer', 'response')
    except requests.exceptions.Timeout:
        raise ExceptionToResponse('mineracer', 'timeout')
    except requests.exceptions.RequestException:
        raise ExceptionToResponse('mineracer', 'requestexception')
    except ValueError:
        raise ExceptionToResponse('mineracer', 'response')


def _get_authorization_headers(partner_key: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {partner_key}'}


def _get_response_data(response: requests.Response) -> dict[str, Any]:
    data = response.json()
    if not isinstance(data, dict):
        raise ExceptionToResponse('mineracer', 'response')
    return data


def _get_required_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise ExceptionToResponse('mineracer', 'response')
    value = value.strip()
    if not value:
        raise ExceptionToResponse('mineracer', 'response')
    return value


def _parse_expires_at(data: dict[str, Any]) -> datetime:
    try:
        return datetime.fromtimestamp(int(data['expiresAt']) / 1000, tz=datetime_timezone.utc)
    except (KeyError, TypeError, ValueError, OSError):
        raise ExceptionToResponse('mineracer', 'response')


def _get_pending_poll_response(response: requests.Response) -> MineracerAccountLinkPollResponse:
    data = _get_response_data(response)
    if _get_required_string(data, 'status') != 'pending':
        raise ExceptionToResponse('mineracer', 'response')
    return MineracerAccountLinkPollResponse(status=MINERACER_STATUS_PENDING, retry_after_ms=_get_required_interval_ms(data))


def _get_linked_poll_response(response: requests.Response) -> MineracerAccountLinkPollResponse:
    data = _get_response_data(response)
    if _get_required_string(data, 'status') != 'linked':
        raise ExceptionToResponse('mineracer', 'response')
    return MineracerAccountLinkPollResponse(status=MINERACER_STATUS_CONFIRMED, userid=_get_required_string(data, 'userId'))


def _get_poll_error_response(response: requests.Response) -> MineracerAccountLinkPollResponse:
    if response.status_code not in [400, 404, 409, 410]:
        response.raise_for_status()
        raise ExceptionToResponse('mineracer', 'response')

    data = _get_response_data(response)
    error = _get_required_string(data, 'error')
    if response.status_code == 410 and error == 'code-expired':
        return MineracerAccountLinkPollResponse(status=MINERACER_STATUS_EXPIRED)
    if error in MINERACER_POLL_ERROR_CATEGORIES and (
        (response.status_code in [400, 404] and error == 'invalid-device-code')
        or (response.status_code == 404 and error == 'account-not-found')
        or (response.status_code == 409 and error == 'link-superseded')
    ):
        return MineracerAccountLinkPollResponse(status=MINERACER_STATUS_FAILED, error_category=MINERACER_POLL_ERROR_CATEGORIES[error])
    raise ExceptionToResponse('mineracer', 'response')


def _get_required_interval_ms(data: dict[str, Any]) -> int:
    try:
        value = int(data['intervalMs'])
    except (KeyError, TypeError, ValueError):
        raise ExceptionToResponse('mineracer', 'response')
    if value < 1:
        raise ExceptionToResponse('mineracer', 'response')
    return value
