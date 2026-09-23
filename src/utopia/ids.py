"""UUID helpers for the historical Utopia implementation.

The project originally used uuid-utils for UUIDv7 generation while the ORM
and Pydantic schemas were typed against the standard-library uuid.UUID.
Normalize at generation time so UUIDv7 semantics are preserved without
leaking a second UUID runtime type through service boundaries.
"""

import uuid

from uuid_utils import uuid7 as _uuid7


def new_uuid7() -> uuid.UUID:
    """Generate a UUIDv7 represented as a standard-library UUID."""
    return uuid.UUID(str(_uuid7()))
