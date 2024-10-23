from logging import getLogger

from boto3 import client

log_client = client("logs")
logger = getLogger(__name__)


def create_log_group(log_group: str, tags: dict) -> str:
    """Create a log group."""
    log_client.create_log_group(logGroupName=log_group, tags=tags)
    log_client.put_retention_policy(logGroupName=log_group, retentionInDays=1)
    logger.info(f"Log group created: {log_group}")


def create_log_stream(log_group: str, log_stream: str) -> None:
    """Create a log stream."""
    log_client.create_log_stream(logGroupName=log_group, logStreamName=log_stream)
    logger.info(f"Log stream created: {log_stream}")


def delete_log_group(log_group: str) -> None:
    """Delete a log group."""
    log_client.delete_log_group(logGroupName=log_group)
    logger.info(f"Log group deleted: {log_group}")
