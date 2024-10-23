"""This script is for getting a bearer token for the API. It uses the Authorization Code flow to get the token.

The script uses the following environment variables:
- DEVELOPER_EMAIL: The email of the developer to get the token for.

To run the script, execute the following command:
APIGEE_ACCESS_TOKEN=`get_token` DEVELOPER_EMAIL=xxx poetry run python get_api_access_token.py
"""

from os import getenv

from pytest_nhsd_apim.apigee_apis import (
    ApigeeClient,
    ApigeeNonProdCredentials,
    DeveloperAppsAPI,
)
from pytest_nhsd_apim.identity_service import (
    AuthorizationCodeAuthenticator,
    AuthorizationCodeConfig,
)

DEVELOPER_EMAIL = getenv("DEVELOPER_EMAIL")
if not DEVELOPER_EMAIL:
    raise ValueError("Environment variable DEVELOPER_EMAIL is not set")

config = ApigeeNonProdCredentials()
client = ApigeeClient(config=config)
apps = DeveloperAppsAPI(client=client)
app = apps.get_app_by_name(DEVELOPER_EMAIL, "validated-relationships-service-client")

config = AuthorizationCodeConfig(
    environment="internal-dev",
    identity_service_base_url="https://internal-dev.api.service.nhs.uk/oauth2-mock",
    callback_url="https://oauth.pstmn.io/v1/browser-callback",
    client_id=app["credentials"][0]["consumerKey"],
    client_secret=app["credentials"][0]["consumerSecret"],
    scope="nhs-login",
    login_form={"username": "9912003071"},
)

authenticator = AuthorizationCodeAuthenticator(config=config)
token_response = authenticator.get_token()

print(token_response["access_token"])
