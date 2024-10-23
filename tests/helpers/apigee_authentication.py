"""
Authenticate with APIM Apigee Proxy.

This is a replacement for the marker decorator as it does not play well
with pytest-bdd when using the `test_` prefix for function names.
"""

from typing import NamedTuple, Optional

import requests
from pytest_nhsd_apim.identity_service import (
    KeycloakUserAuthenticator,
    KeycloakUserConfig,
    TokenExchangeAuthenticator,
    TokenExchangeConfig,
)

APIGEE_ENVIRONMENT = "internal-dev"


class AuthenticationResult(NamedTuple):
    """Result of an authentication flow."""

    id_token: str
    token_response: Optional[str]
    status_code: str


def ping_keycloak_server() -> requests.Response:
    """Ping the NHS Login mock keycloak server."""
    return requests.get(
        f"https://identity.ptl.api.platform.nhs.uk/realms/NHS-Login-mock-{APIGEE_ENVIRONMENT}",
        timeout=6,
    )


def ping_authentication_server() -> requests.Response:
    """Ping the NHS Login mock keycloak server."""
    return requests.get(
        f"https://{APIGEE_ENVIRONMENT}.api.service.nhs.uk/oauth2-mock/_ping", timeout=6
    )


def authenticate_client(
    _test_app_credentials,
    apigee_environment,
    _jwt_keys,
    _keycloak_client_credentials,
    client_nhs_number="9730675929",
) -> AuthenticationResult:
    """Authenticate with APIM Apigee Proxy

    Args:
        _test_app_credentials (dict): Credentials of desired products based on the api
            name provided when executing the tests.
        apigee_environment (str): The name of the Apigee environment under test.
        _jwt_keys (dict): A dict containing the key to use during the token exchange
            based on the key id provided when executing the tests.
        _keycloak_client_credentials (dict): The client credentials obtains from the
            mock credentials server.
        client_nhs_number (str, optional): The NHS number of the client to be
            authenticated. Defaults to "9912003071", which is a P9 verified mock user.

    Returns:
        AuthenticationResult: The id token, token from the token exchange and the
            status code of the token exchange.

    .._Testing with mock auth:
        https://nhsd-confluence.digital.nhs.uk/display/APM/Testing+with+mock+auth#Testingwithmockauth-Testingwithseperate-authusingPostman

    .._test_token_exchange_authenticator example:
        https://github.com/NHSDigital/pytest-nhsd-apim/blob/main/tests/test_examples.py#L370
    """
    keycloak_config = KeycloakUserConfig(
        realm=f"NHS-Login-mock-{APIGEE_ENVIRONMENT}",
        client_id=_keycloak_client_credentials["nhs-login"]["client_id"],
        client_secret=_keycloak_client_credentials["nhs-login"]["client_secret"],
        login_form={"username": str(client_nhs_number)},
    )
    authenticator = KeycloakUserAuthenticator(config=keycloak_config)
    id_token = authenticator.get_token()["id_token"]

    config = TokenExchangeConfig(
        environment=APIGEE_ENVIRONMENT,
        identity_service_base_url=f"https://{apigee_environment}.api.service.nhs.uk/oauth2-mock",
        client_id=_test_app_credentials["consumerKey"],
        jwt_private_key=_jwt_keys["private_key_pem"],
        jwt_kid="test-1",
        id_token=id_token,
    )

    authenticator = TokenExchangeAuthenticator(config=config)

    try:
        token = authenticator.get_token()
        return AuthenticationResult(
            id_token,
            token,
            "200",  # get_token only succeeds if the response is 200
        )
    except RuntimeError as e:
        return AuthenticationResult(
            id_token,
            None,
            e.args[0][:3],  # get status code from error message
        )
