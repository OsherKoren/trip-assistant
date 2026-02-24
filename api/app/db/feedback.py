"""Feedback storage (DynamoDB) and notification (SES) functions."""

from typing import Any

import aioboto3

from app.logger import logger

_session = aioboto3.Session()


async def store_feedback(table_name: str, region: str, item: dict[str, Any]) -> None:
    """Store feedback item in DynamoDB.

    Args:
        table_name: DynamoDB table name.
        region: AWS region.
        item: Feedback item to store.

    Raises:
        Exception: If DynamoDB put_item fails.
    """
    async with _session.resource("dynamodb", region_name=region) as dynamodb:
        table = await dynamodb.Table(table_name)
        await table.put_item(Item=item)
    logger.info("Feedback stored", feedback_id=item["id"])


async def send_feedback_email(email: str, region: str, item: dict[str, Any]) -> None:
    """Send feedback notification email via SES (non-blocking, best-effort).

    Uses self-notify pattern: same source and destination email.
    Errors are logged but not raised.

    Args:
        email: Verified SES email address (source and destination).
        region: AWS region.
        item: Feedback item for email body.
    """
    try:
        rating = item.get("rating", "unknown")
        message_id = item.get("message_id", "N/A")
        message_preview = item.get("message_preview", "")
        comment = item.get("comment", "")

        subject = f"Trip Assistant Feedback: {rating}"
        body = (
            f"Rating: {rating}\n"
            f"Message ID: {message_id}\n"
            f"Message Preview: {message_preview}\n"
            f"Comment: {comment}\n"
            f"Feedback ID: {item.get('id', 'unknown')}\n"
            f"Time: {item.get('created_at', 'unknown')}"
        )

        async with _session.client("ses", region_name=region) as ses:
            await ses.send_email(
                Source=email,
                Destination={"ToAddresses": [email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}},
                },
            )
        logger.info("Feedback email sent", feedback_id=item.get("id"))
    except Exception:
        logger.exception("Failed to send feedback email", feedback_id=item.get("id"))
