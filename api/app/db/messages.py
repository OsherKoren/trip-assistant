"""Message storage (DynamoDB) functions."""

from typing import Any

import aioboto3

from app.logger import logger

_session = aioboto3.Session()


async def store_message(table_name: str, region: str, item: dict[str, Any]) -> None:
    """Store message item in DynamoDB.

    Args:
        table_name: DynamoDB table name.
        region: AWS region.
        item: Message item to store.

    Raises:
        Exception: If DynamoDB put_item fails.
    """
    async with _session.resource("dynamodb", region_name=region) as dynamodb:
        table = await dynamodb.Table(table_name)
        await table.put_item(Item=item)
    logger.info("Message stored", message_id=item["id"])


async def get_message(table_name: str, region: str, message_id: str) -> dict[str, Any] | None:
    """Get message item from DynamoDB.

    Args:
        table_name: DynamoDB table name.
        region: AWS region.
        message_id: Message ID to look up.

    Returns:
        Message item dict, or None if not found.
    """
    async with _session.resource("dynamodb", region_name=region) as dynamodb:
        table = await dynamodb.Table(table_name)
        response = await table.get_item(Key={"id": message_id})
    item: dict[str, Any] | None = response.get("Item")
    return item
