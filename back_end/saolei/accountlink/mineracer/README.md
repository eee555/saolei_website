# Mineracer Account Linking

This package contains Mineracer-specific account-linking code.

- `dtos.py` defines Mineracer status constants and transfer objects.
- `client.py` wraps Mineracer partner HTTP endpoints.
- `sessions.py` stores the short-lived account-link session in `caches['default']`, polls Mineracer when due, writes the final binding to database models, and emits audit logs through the `accountlink` logger.

Each start/poll request reads `mineracer_account_link_partner_key` directly from `secrets.json` at runtime. A missing file or key raises the underlying read exception; an empty key raises `mineracer/not_configured` (503). Key changes take effect without restarting the server. Do not log it, expose it to the frontend, or store the reusable `deviceCode` outside the Redis session.
