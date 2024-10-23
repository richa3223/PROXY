# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
"""
Step implementations for feature files.
"""

from datetime import datetime
from logging import INFO, basicConfig, getLogger
from time import sleep

from pytest_bdd import parsers, scenarios, then
from requests import Response

logger = getLogger(__name__)
basicConfig(level=INFO)

scenarios("../features/request_ids_audit_check.feature")


@then(parsers.parse("after {seconds:d} seconds have passed"))
def long_wait(seconds):
    logger.info("Waiting %d seconds", seconds)
    sleep(seconds)


@then(
    parsers.parse(
        "the request has been logged to the Audit Service using the {crawler}",
    )
)
def check_that_data_has_been_indexed(helpers, crawler, api_response: Response):
    response_body = api_response.json()
    timestamp = datetime.fromisoformat(response_body["timestamp"])
    helpers.index_data_from_api_call(crawler, timestamp)


@then(
    parsers.parse(
        "an entry with the specified {header_key} id can be found in the '{athena_table}' column {column_name}"
    ),
    target_fixture="header_id_table_query",
)
def query_athena_table_by_header_id(
    header_key, athena_table, column_name, headers, helpers
) -> dict:
    if athena_table == "main_audit_main_dev_queryable_audit_events_bucket":
        data_catalogue = "main-queryable-data-catalogue"
    elif athena_table == "main_audit_main_dev_sensitive_audit_events_bucket":
        data_catalogue = "main-sensitive-data-catalogue"
    else:
        raise ValueError(f"Unknown athena table: {athena_table}")
    output_location = "s3://main-dev-standard-query-results-bucket/"
    header_id = headers[header_key]
    response = helpers.query_header_id(
        data_catalogue, athena_table, output_location, header_id, column_name
    )
    assert helpers.result_contains_entry_with_header_id(
        response, header_id, column_name
    ), f"The expected header ID:{header_id} not found in the athena query response: '{response}'"
    return response


@then("all sensitive values are redacted")
def sensitive_values_redacted(header_id_table_query: dict):
    results = header_id_table_query["ResultSet"]["Rows"][1:]  # Remove header row
    for row in results:
        assert row["Data"][0]["VarCharValue"]["sensitive"] == "[REDACTED]"
