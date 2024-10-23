"""
Test create email Lambda
"""

from ..helpers import WORKSPACE, Helpers

FUNCTION_NAME = f"{WORKSPACE}-get_email_template"


def test_adult_to_child_template(helpers: Helpers) -> None:
    """
    Lambda receives adult to child template
    Lambda returns successful response. No errors.
    """
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME, {"template_identifier": "adult_to_child"}
    )

    assert "Email Template" in str(payload)


def test_invalid_template_value(helpers: Helpers) -> None:
    """
    Lambda receives an invalid email template
    Lambda returns an error
    """
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME, {"template_identifier": "adult_2_child"}
    )

    assert payload["errorMessage"] == "Invalid template name"


def test_empty_json(helpers: Helpers) -> None:
    """
    Lambda receives empty json
    Lambda returns an error
    """
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, {})

    assert payload["errorMessage"] == "Invalid template name"
