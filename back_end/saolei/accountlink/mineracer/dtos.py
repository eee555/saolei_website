from dataclasses import dataclass
from datetime import datetime

MINERACER_STATUS_PENDING = 'pending'
MINERACER_STATUS_CONFIRMED = 'confirmed'
MINERACER_STATUS_EXPIRED = 'expired'
MINERACER_STATUS_FAILED = 'failed'


@dataclass(frozen=True)
class MineracerAccountLinkStartResponse:
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_at: datetime
    poll_interval_ms: int


@dataclass(frozen=True)
class MineracerAccountLinkPollResponse:
    status: str
    userid: str = ''
    error_category: str = ''
    retry_after_ms: int | None = None


@dataclass
class MineracerAccountLinkSession:
    session_id: str
    user_id: int
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_at: datetime
    status: str = MINERACER_STATUS_PENDING
    remote_userid: str = ''
    last_polled_at: datetime | None = None
    next_poll_at: datetime | None = None
    error_category: str = ''
    created_at: datetime | None = None
    updated_at: datetime | None = None
