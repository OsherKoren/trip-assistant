"""Question cache storage (DynamoDB) functions."""

from typing import Any

import aioboto3

from app.logger import logger

_session = aioboto3.Session()


async def get_cached_response(
    table_name: str, region: str, question_hash: str
) -> dict[str, Any] | None:
    """Look up a cached response by question hash.

    Returns None when table_name is empty (local dev / tests without DynamoDB).

    Args:
        table_name: DynamoDB table name (empty string to skip).
        region: AWS region.
        question_hash: SHA-256 hash of the normalized question.

    Returns:
        Cached item dict, or None if not found.
    """
    if not table_name:
        return None
    async with _session.resource("dynamodb", region_name=region) as dynamodb:
        table = await dynamodb.Table(table_name)
        response = await table.get_item(Key={"question_hash": question_hash})
    item: dict[str, Any] | None = response.get("Item")
    if item:
        logger.info("Cache hit", question_hash=question_hash[:12])
    return item


async def store_cached_response(table_name: str, region: str, item: dict[str, Any]) -> None:
    """Store a response in the question cache.

    No-op when table_name is empty (local dev / tests without DynamoDB).

    Args:
        table_name: DynamoDB table name (empty string to skip).
        region: AWS region.
        item: Cache item to store (must include question_hash key).

    Raises:
        Exception: If DynamoDB put_item fails.
    """
    if not table_name:
        return
    async with _session.resource("dynamodb", region_name=region) as dynamodb:
        table = await dynamodb.Table(table_name)
        await table.put_item(Item=item)
    logger.info("Cache stored", question_hash=item["question_hash"][:12])
