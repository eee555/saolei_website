from datetime import datetime, timezone as datetime_timezone
from typing import Annotated, Literal, TypeVar

from django.conf import settings
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
import requests

from utils.exceptions import ExceptionToResponse
from .dtos import MINERACER_ERROR_ACCOUNT_NOT_FOUND, MINERACER_ERROR_INVALID_DEVICE_CODE, MINERACER_ERROR_LINK_SUPERSEDED, MINERACER_STATUS_CONFIRMED, MINERACER_STATUS_EXPIRED, MINERACER_STATUS_FAILED, MINERACER_STATUS_PENDING, MineracerAccountLinkPollResponse, MineracerAccountLinkStartResponse

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
PositiveInt = Annotated[int, Field(gt=0)]


class MineracerStartPayload(BaseModel):
    model_config = ConfigDict(strict=True, extra='ignore')
    deviceCode: NonEmptyString
    userCode: NonEmptyString
    verificationUri: NonEmptyString
    verificationUriComplete: NonEmptyString
    intervalMs: PositiveInt
    expiresAt: PositiveInt


class MineracerPendingPayload(BaseModel):
    model_config = ConfigDict(strict=True, extra='ignore')
    status: Literal['pending']
    intervalMs: PositiveInt


class MineracerLinkedPayload(BaseModel):
    model_config = ConfigDict(strict=True, extra='ignore')
    status: Literal['linked']
    userId: NonEmptyString


class MineracerPollErrorPayload(BaseModel):
    model_config = ConfigDict(strict=True, extra='ignore')
    error: NonEmptyString


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
        payload = MineracerStartPayload.model_validate(response.json())
    except requests.exceptions.Timeout:
        raise ExceptionToResponse('mineracer', 'timeout')
    except requests.exceptions.RequestException:
        raise ExceptionToResponse('mineracer', 'requestexception')
    except ValueError:
        raise ExceptionToResponse('mineracer', 'response')

    return MineracerAccountLinkStartResponse(
        device_code=payload.deviceCode,
        user_code=payload.userCode,
        verification_uri=payload.verificationUri,
        verification_uri_complete=payload.verificationUriComplete,
        expires_at=_parse_expires_at(payload.expiresAt),
        poll_interval_ms=payload.intervalMs,
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
            payload = MineracerPendingPayload.model_validate(response.json())
            return MineracerAccountLinkPollResponse(status=MINERACER_STATUS_PENDING, retry_after_ms=payload.intervalMs)

        if response.status_code == 200:
            payload = MineracerLinkedPayload.model_validate(response.json())
            return MineracerAccountLinkPollResponse(status=MINERACER_STATUS_CONFIRMED, userid=payload.userId)

        error = MineracerPollErrorPayload.model_validate(response.json()).error

        if response.status_code == 410 and error == 'code-expired':
            return MineracerAccountLinkPollResponse(status=MINERACER_STATUS_EXPIRED)

        if response.status_code == 404 and error == 'account-not-found':
            return MineracerAccountLinkPollResponse(status=MINERACER_STATUS_FAILED, 
            error_category=MINERACER_ERROR_ACCOUNT_NOT_FOUND)

        if response.status_code == 409 and error == 'link-superseded':
            return MineracerAccountLinkPollResponse(status=MINERACER_STATUS_FAILED, error_category=MINERACER_ERROR_LINK_SUPERSEDED)

        if response.status_code in [400, 404] and error == 'invalid-device-code':
            return MineracerAccountLinkPollResponse(status=MINERACER_STATUS_FAILED, error_category=MINERACER_ERROR_INVALID_DEVICE_CODE)

        response.raise_for_status()
        raise ExceptionToResponse('mineracer', 'response')
    
    except requests.exceptions.Timeout:
        raise ExceptionToResponse('mineracer', 'timeout')
    except requests.exceptions.RequestException:
        raise ExceptionToResponse('mineracer', 'requestexception')
    except ValueError:
        raise ExceptionToResponse('mineracer', 'response')


def _get_authorization_headers(partner_key: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {partner_key}'}


def _parse_expires_at(timestamp_ms: int) -> datetime:
    try:
        return datetime.fromtimestamp(timestamp_ms / 1000, tz=datetime_timezone.utc)
    except (ValueError, OSError):
        raise ExceptionToResponse('mineracer', 'response')
