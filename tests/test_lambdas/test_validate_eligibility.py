"""
Test validate patient eligibility
"""

from ..helpers import WORKSPACE, Helpers

FUNCTION_NAME = f"{WORKSPACE}-validate_eligibility"


def test_happy_path_identifier_received(helpers: Helpers) -> None:
    """
    Lambda receives an identifier NHS number for a patient who has a PDS record,
    is not deceased and is not restricted.
    The Lambda returns successful response. No errors.
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_eligibility/test1_input.json",
    )

    assert payload["statusCode"] == 200
    assert payload["body"]["eligibility"] is True


def test_happy_path_identifier_and_patient_identifier_received(
    helpers: Helpers,
) -> None:
    """
    Lambda receives an identifier and patient:identifier NHS number for a patient
    who has a PDS record, is not deceased and is not restricted.
    The Lambda returns successful response. No errors.
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_eligibility/test2_input.json",
    )

    assert payload["statusCode"] == 200
    assert payload["body"]["eligibility"] is True


def test_identifier_no_pds_record(helpers: Helpers) -> None:
    """
    Lambda receives an identifier NHS number for a patient who has no PDS record.
    The Lambda returns:
    Status code is 200
    Eligibility is false
    Empty relationship array
    An event is published stating no PDS record found
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_eligibility/test3_input.json",
    )

    assert payload["statusCode"] == 200
    assert payload["body"]["eligibility"] is False
    assert payload["body"]["relationshipArr"] is None


def test_identifier_deceased(helpers: Helpers) -> None:
    """
    Lambda receives an identifier NHS number for a patient who is marked as deceased
    on their PDS record.
    The Lambda returns:
    Status code is 200
    Eligibility is false
    Empty relationship array
    An event is published stating identifier is deceased
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_eligibility/test4_input.json",
    )

    assert payload["statusCode"] == 200
    assert payload["body"]["eligibility"] is False
    assert payload["body"]["relationshipArr"] is None


def test_identifier_restricted(helpers: Helpers) -> None:
    """
    Lambda receives an identifier NHS number for a patient who is marked as
    restricted on their PDS record.
    The Lambda returns:
    Status code is 200
    Eligibility is false
    Empty relationship array
    An event is published stating identifier is restricted
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_eligibility/test5_input.json",
    )

    assert payload["statusCode"] == 200
    assert payload["body"]["eligibility"] is False
    assert payload["body"]["relationshipArr"] is None


def test_identifier_deceased_and_restricted(helpers: Helpers) -> None:
    """
    Lambda receives an identifier NHS number for a patient who is marked as
    deceased and restricted on their PDS record.
    The Lambda returns:
    Status code is 200
    Eligibility is false
    Empty relationship array
    An event is published stating identifier is deceased
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_eligibility/test6_input.json",
    )

    assert payload["statusCode"] == 200
    assert payload["body"]["eligibility"] is False
    assert payload["body"]["relationshipArr"] is None


def test_no_input(helpers: Helpers) -> None:
    """
    Lambda receives no input
    The Lambda returns:
    Status code is 400
    Error stating PDS status code is required
    """
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, {})

    assert payload["statusCode"] == 400
    assert payload["body"]["error"] == "PDS Status Code (Proxy) is required"


def test_proxy_status_400(helpers: Helpers) -> None:
    """
    Lambda receives a proxy status code that is not 200
    The Lambda returns:
    Status code is 400
    Error stating PDS status code is invalid
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_eligibility/test8_input.json",
    )

    assert payload["statusCode"] == 400
    assert payload["body"]["error"] == "PDS Status Code is invalid"


def test_relationship_status_400(helpers: Helpers) -> None:
    """
    Lambda receives a relationship status code that is not 200
    The Lambda returns:
    Status code is 400
    Error stating PDS relationship status code is invalid
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_eligibility/test9_input.json",
    )
    assert payload["statusCode"] == 400
    assert payload["body"]["error"] == "PDS Relationship Lookup Status Code is invalid"


def test_relationship_lookup_status_code_404(helpers: Helpers) -> None:
    """
    Lambda receives a relationship status code that is 404
    The Lambda returns:
    Status code is 200
    Eligibility is false
    Empty relationship array
    An event is published stating no proxy relationships on PDS
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_eligibility/test13_input.json",
    )

    assert payload["statusCode"] == 200
    assert payload["body"]["eligibility"] is False
    assert payload["body"]["relationshipArr"] is None
