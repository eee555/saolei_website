from ninja.orm import create_schema

from .models import Identifier

IdentifierStr = create_schema(
    Identifier,
    fields=['identifier'],
)
