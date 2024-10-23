"""
Test the start standard audit data crawler
"""

import logging
from os import getenv

import pytest

from ..helpers import ENVIRONMENT, WORKSPACE, Helpers

log = logging.getLogger(__name__)


@pytest.mark.skipif(
    getenv("GH_SKIP_TESTS") == "true",
    reason="Skipping test due to AWS Profile not available in GitHub Actions",
)
def test_standard_audit_data_crawler(helpers: Helpers) -> None:
    """
    Confirm we can run the standard data crawler Lambda and return a successful run
    """
    prefix2 = "standard"
    function_name = f"{WORKSPACE}-start_{prefix2}_audit_data_crawler"
    run_data_crawlers(helpers, function_name, prefix1="queryable", prefix2=prefix2)


@pytest.mark.skipif(
    getenv("GH_SKIP_TESTS") == "true",
    reason="Skipping test due to AWS Profile not available in GitHub Actions",
)
def test_sensitive_audit_data_crawler(helpers: Helpers) -> None:
    """
    Confirm we can run the sensitive data crawler Lambda and return a successful run
    """
    prefix2 = "sensitive"
    function_name = f"{WORKSPACE}-start_{prefix2}_audit_data_crawler"
    run_data_crawlers(helpers, function_name, prefix1="sensitive", prefix2=prefix2)


def run_data_crawlers(helpers: Helpers, function_name, prefix1, prefix2) -> None:
    """
    Function to run a data crawler
    """
    correlation_id = helpers.publish_event()
    crawler = f"{WORKSPACE}-{prefix1}_data_glue_crawler"

    helpers.wait_until_crawler_ready(crawler)
    payload = helpers.invoke_lambda_function(function_name, {})
    helpers.wait_until_crawler_ready(crawler)

    assert payload["message"] == "Lambda application stopped"

    data_catalogue = f"{WORKSPACE}-{prefix1}-data-catalogue"
    bucket = f"audit_{WORKSPACE}_{ENVIRONMENT}_{prefix1}_audit_events_bucket"
    output_location = f"s3://{WORKSPACE}-{ENVIRONMENT}-{prefix2}-query-results-bucket/"

    result = helpers.query_header_id(
        data_catalogue, bucket, output_location, correlation_id, "correlation-id"
    )
    assert helpers.result_contains_entry_with_header_id(
        result, correlation_id, "correlation-id"
    ), f"No event was found with the correlation id - {correlation_id}"
