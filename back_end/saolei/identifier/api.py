from typing import Literal

from django.db import DatabaseError
from django.db.models.functions import Collate
from django_ratelimit.decorators import ratelimit
from ninja import Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.orm import create_schema

from .models import Identifier

router = Router()
IdentifierMatch = Literal['exact', 'iexact', 'contains', 'icontains', 'startswith', 'istartswith', 'endswith', 'iendswith', 'regex']
QUERY_MATCH_LIMIT = 1000


class IdentifierOutBase(Schema):
    @staticmethod
    def resolve_user_id(identifier: Identifier) -> int | None:
        if identifier.userms_id is None:
            return None
        user = getattr(identifier.userms, 'parent', None)
        return user.id if user else None


IdentifierOut = create_schema(
    Identifier,
    fields=['identifier'],
    custom_fields=[('user_id', int | None, None)],
    base_class=IdentifierOutBase,
)


class IdentifierQueryOut(Schema):
    items: list[IdentifierOut]


class IdentifierQueryError(Schema):
    code: Literal['too_many_matches']
    detail: str


QUERY_RESPONSES = {200: IdentifierQueryOut, 400: IdentifierQueryError}


def _query_identifiers(request, identifier: str, mode: IdentifierMatch):
    """
    Search approved identifiers using native Django/MySQL lookups. Returns all matches, up to 1000 items.
    Queries matching over 1000 items return HTTP 400 without partial results. No server pagination.
    Case-insensitive non-regex modes use utf8mb4_0900_as_ci; accents remain significant.
    Regex uses MySQL ICU syntax, including inline flags such as (?i), and native resource limits.
    """
    if getattr(request, 'limited', False):
        raise HttpError(429, 'Identifier query rate limit exceeded. Please try again later.')
    if not 1 <= len(identifier) <= 128:
        raise HttpError(400, 'Invalid identifier length.')
    identifiers = Identifier.objects.filter(safe=True)
    field = 'identifier'
    if mode in {'iexact', 'icontains', 'istartswith', 'iendswith'}:
        # The stored column is case-sensitive. MySQL LIKE alone does not make these lookups case-insensitive.
        identifiers = identifiers.alias(search_text=Collate('identifier', 'utf8mb4_0900_as_ci'))
        field = 'search_text'
    identifiers = identifiers.filter(**{f'{field}__{mode}': identifier})
    try:
        items = list(identifiers.select_related('userms__parent').order_by('id')[:QUERY_MATCH_LIMIT + 1])
    except DatabaseError as exc:
        # MySQL 8 ICU errors cover invalid patterns and regex resource limits. Preserve unrelated database errors.
        if mode == 'regex' and exc.args and 3684 <= exc.args[0] <= 3700:
            raise HttpError(400, 'Invalid regular expression or regular expression resource limit exceeded.') from exc
        raise
    if len(items) > QUERY_MATCH_LIMIT:
        return 400, {'code': 'too_many_matches', 'detail': f'Identifier query matches more than {QUERY_MATCH_LIMIT} results. Please narrow your search.'}
    return {'items': items}


@router.get('/query/exact', response=QUERY_RESPONSES)
@decorate_view(ratelimit(key='ip', rate='2/s', group='identifier-exact', block=False))
def query_identifier_exact(request, identifier: str):
    """
    - ratelimit(key='ip', rate='2/s', group='identifier-exact', block=False)

    exact matching. Returns all matches, up to 1000 items; more matches return HTTP 400. Rate limit: HTTP 429.
    """
    return _query_identifiers(request, identifier, 'exact')


@router.get('/query/iexact', response=QUERY_RESPONSES)
@decorate_view(ratelimit(key='ip', rate='6/m', group='identifier-text', block=False))
def query_identifier_iexact(request, identifier: str):
    """
    - ratelimit(key='ip', rate='6/m', group='identifier-text', block=False)

    iexact matching. Returns all matches, up to 1000 items; more matches return HTTP 400. Rate limit: HTTP 429.
    """
    return _query_identifiers(request, identifier, 'iexact')


@router.get('/query/contains', response=QUERY_RESPONSES)
@decorate_view(ratelimit(key='ip', rate='6/m', group='identifier-text', block=False))
def query_identifier_contains(request, identifier: str):
    """
    - ratelimit(key='ip', rate='6/m', group='identifier-text', block=False)

    contains matching. Returns all matches, up to 1000 items; more matches return HTTP 400. Rate limit: HTTP 429.
    """
    return _query_identifiers(request, identifier, 'contains')


@router.get('/query/icontains', response=QUERY_RESPONSES)
@decorate_view(ratelimit(key='ip', rate='6/m', group='identifier-text', block=False))
def query_identifier_icontains(request, identifier: str):
    """
    - ratelimit(key='ip', rate='6/m', group='identifier-text', block=False)

    icontains matching. Returns all matches, up to 1000 items; more matches return HTTP 400. Rate limit: HTTP 429.
    """
    return _query_identifiers(request, identifier, 'icontains')


@router.get('/query/startswith', response=QUERY_RESPONSES)
@decorate_view(ratelimit(key='ip', rate='10/m', group='identifier-prefix', block=False))
def query_identifier_startswith(request, identifier: str):
    """
    - ratelimit(key='ip', rate='10/m', group='identifier-prefix', block=False)

    startswith matching. Returns all matches, up to 1000 items; more matches return HTTP 400. Rate limit: HTTP 429.
    """
    return _query_identifiers(request, identifier, 'startswith')


@router.get('/query/istartswith', response=QUERY_RESPONSES)
@decorate_view(ratelimit(key='ip', rate='6/m', group='identifier-text', block=False))
def query_identifier_istartswith(request, identifier: str):
    """
    - ratelimit(key='ip', rate='6/m', group='identifier-text', block=False)

    istartswith matching. Returns all matches, up to 1000 items; more matches return HTTP 400. Rate limit: HTTP 429.
    """
    return _query_identifiers(request, identifier, 'istartswith')


@router.get('/query/endswith', response=QUERY_RESPONSES)
@decorate_view(ratelimit(key='ip', rate='6/m', group='identifier-text', block=False))
def query_identifier_endswith(request, identifier: str):
    """
    - ratelimit(key='ip', rate='6/m', group='identifier-text', block=False)

    endswith matching. Returns all matches, up to 1000 items; more matches return HTTP 400. Rate limit: HTTP 429.
    """
    return _query_identifiers(request, identifier, 'endswith')


@router.get('/query/iendswith', response=QUERY_RESPONSES)
@decorate_view(ratelimit(key='ip', rate='6/m', group='identifier-text', block=False))
def query_identifier_iendswith(request, identifier: str):
    """
    - ratelimit(key='ip', rate='6/m', group='identifier-text', block=False)

    iendswith matching. Returns all matches, up to 1000 items; more matches return HTTP 400. Rate limit: HTTP 429.
    """
    return _query_identifiers(request, identifier, 'iendswith')


@router.get('/query/regex', response=QUERY_RESPONSES)
@decorate_view(ratelimit(key='ip', rate='2/m', group='identifier-regex', block=False))
def query_identifier_regex(request, identifier: str):
    """
    - ratelimit(key='ip', rate='2/m', group='identifier-regex', block=False)

    regex matching. Returns all matches, up to 1000 items; more matches return HTTP 400. Rate limit: HTTP 429.
    """
    return _query_identifiers(request, identifier, 'regex')
