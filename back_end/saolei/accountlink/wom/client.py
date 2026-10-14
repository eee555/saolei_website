import logging
import ssl

import truststore
from wom_api import RequestTimeout, WomClient, WomError

from utils.exceptions import ExceptionToResponse
from .utils import normalize_wom_profile

logger = logging.getLogger('accountlink')


async def fetch_wom_profile(user_id: int) -> dict:
    try:
        context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        async with WomClient(timeout=5, ssl_context=context) as client:
            profile = await client.get_user_detail_data(userId=user_id, popupRandId=None)
        return normalize_wom_profile(profile, user_id)
    except RequestTimeout:
        raise ExceptionToResponse(obj='import', category='timeout') from None
    except WomError as error:
        logger.warning('WOM profile request failed for user #%s: %s', user_id, type(error).__name__)
        raise ExceptionToResponse(obj='import', category='requestexception') from None
    except ValueError:
        raise ExceptionToResponse(obj='import', category='indexerror') from None
