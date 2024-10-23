"""Test Slack alerts."""

from ..helpers import Helpers, WORKSPACE

FUNCTION_NAME = f"{WORKSPACE}-slack_alerts"

# Note: A successful test is run in the test_weekly directory


def test_empty_json_payload(helpers: Helpers) -> None:
    """
    Lambda receives empty json payload
    Lambda returns an error
    """
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, {})

    assert (
        payload["errorMessage"]
        == "Slack alert failed with response.status_code=400 response.reason='Bad Request'"
    )


def test_broken_json_payload(helpers: Helpers) -> None:
    """
    Lambda receives broken json payload
    Lambda returns an error
    """
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME,
        {"Records": [{}]},
    )

    assert (
        payload["errorMessage"]
        == "Slack alert failed with response.status_code=400 response.reason='Bad Request'"
    )
