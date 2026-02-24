"""Shared test helpers for mocking AWS services."""

from unittest.mock import AsyncMock, MagicMock


class AsyncContextManagerStub:
    """Minimal async context manager stub for aioboto3 resource/client."""

    def __init__(self, return_value: AsyncMock) -> None:
        self._return_value = return_value

    async def __aenter__(self) -> AsyncMock:
        return self._return_value

    async def __aexit__(self, *args: object) -> bool:
        return False


def make_mock_boto3_session(
    *, resource: AsyncMock | None = None, client: AsyncMock | None = None
) -> MagicMock:
    """Build a mock aioboto3 session for resource() and/or client() context manager.

    Uses MagicMock (not AsyncMock) so that session.resource(...) returns the
    context manager stub synchronously — matching how ``async with session.resource(...)``
    works in aioboto3.

    Args:
        resource: Mock to return from ``session.resource(...)`` context manager.
        client: Mock to return from ``session.client(...)`` context manager.

    Returns:
        MagicMock session with the appropriate context managers wired.
    """
    session = MagicMock()
    if resource is not None:
        session.resource.return_value = AsyncContextManagerStub(resource)
    if client is not None:
        session.client.return_value = AsyncContextManagerStub(client)
    return session
