"""
Test relationship lookup
"""

import pytest

from ..helpers import WORKSPACE, Helpers

FUNCTION_NAME = f"{WORKSPACE}-relationship_lookup"


@pytest.mark.pds_api_call
def test_valid_nhs_number_multiple_relationships(helpers: Helpers) -> None:
    """
    Confirm we can retrieve PDS patient multiple relationship details
    """
    access_token = helpers.get_pds_access_token()
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME, {"nhsNumber": "9730675988", "authToken": access_token}
    )

    assert payload["statusCode"] == 200


@pytest.mark.pds_api_call
def test_valid_nhs_number_single_relationship(helpers: Helpers) -> None:
    """
    Confirm we can retrieve PDS patient single relationship details
    """
    access_token = helpers.get_pds_access_token()
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME, {"nhsNumber": "9730675929", "authToken": access_token}
    )

    assert payload["statusCode"] == 200


@pytest.mark.pds_api_call
def test_valid_nhs_number_no_relationships(helpers: Helpers) -> None:
    """
    Check we can retrieve PDS patient with no relationship details
    """
    access_token = helpers.get_pds_access_token()
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME, {"nhsNumber": "9730423199", "authToken": access_token}
    )

    assert payload["statusCode"] == 200
    assert len(payload["body"]["pdsRelationshipRecord"]) == 0
    assert payload["body"]["error"] is None


@pytest.mark.pds_api_call
def test_no_nhs_number(helpers: Helpers) -> None:
    """
    Confirm no NHS number returns 400
    """
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME, {"nhsNumber": "", "authToken": "token12345"}
    )

    assert payload["statusCode"] == 400
    assert payload["body"]["pdsRelationshipRecord"] is None
    assert payload["body"]["error"] == "NHS Number is not valid."


@pytest.mark.pds_api_call
def test_invalid_nhs_number(helpers: Helpers) -> None:
    """
    Confirm an invalid NHS number returns 400
    """
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME, {"nhsNumber": "9000000000", "authToken": "token12345"}
    )

    assert payload["statusCode"] == 400
    assert payload["body"]["pdsRelationshipRecord"] is None
    assert payload["body"]["error"] == "NHS Number is not valid."


@pytest.mark.pds_api_call
def test_valid_nhs_number_no_pds_record(helpers: Helpers) -> None:
    """
    Confirm a valid NHS number with no pds record returns 404
    """
    access_token = helpers.get_pds_access_token()
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME, {"nhsNumber": "7966022757", "authToken": access_token}
    )

    assert payload["statusCode"] == 404
    assert payload["body"]["pdsRelationshipRecord"] is None
    assert payload["body"]["error"] == "Record Not Found."
