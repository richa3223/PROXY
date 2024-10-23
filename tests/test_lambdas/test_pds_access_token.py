"""
Test get PDS Access Token
"""

from ..helpers import WORKSPACE, helpers

FUNCTION_NAME = f"{WORKSPACE}-pds_access_token"


def test_return_pds_access_token(helpers: helpers):
    """
    Confirm we can return a pds access token
    """
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, {})

    assert payload["statusCode"] == 200
    assert payload["body"]["token"]["access_token"] is not None
    assert payload["body"]["token"]["expires_in"] == "599"
    assert payload["body"]["token"]["token_type"] == "Bearer"
    assert payload["body"]["token"]["issued_at"] is not None
