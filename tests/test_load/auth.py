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


def get_bearer_token():
    developer_email = getenv("DEVELOPER_EMAIL")
    if not developer_email:
        raise ValueError("Environment variable DEVELOPER_EMAIL is not set")

    config = ApigeeNonProdCredentials()
    client = ApigeeClient(config=config)
    apps = DeveloperAppsAPI(client=client)
    app = apps.get_app_by_name(
        developer_email, "validated-relationships-service-client"
    )

    config = AuthorizationCodeConfig(
        environment="internal-qa",
        identity_service_base_url="https://internal-qa.api.service.nhs.uk/oauth2-mock",
        callback_url="https://oauth.pstmn.io/v1/browser-callback",
        client_id=app["credentials"][0]["consumerKey"],
        client_secret=app["credentials"][0]["consumerSecret"],
        scope="nhs-login",
        login_form={"username": "9730675953"},
    )

    authenticator = AuthorizationCodeAuthenticator(config=config)
    return authenticator.get_token()["access_token"]
