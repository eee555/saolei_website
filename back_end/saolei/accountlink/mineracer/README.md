# Mineracer Account Linking

This package contains Mineracer-specific account-linking code.

- `dtos.py` defines Mineracer status constants and transfer objects.
- `client.py` wraps Mineracer partner HTTP endpoints.
- `sessions.py` stores the short-lived account-link session in `caches['default']`, polls Mineracer when due, writes the final binding to database models, and emits audit logs through the `accountlink` logger.

The partner key is read only from server settings. Do not log it, expose it to the frontend, or store the reusable `deviceCode` outside the Redis session.
