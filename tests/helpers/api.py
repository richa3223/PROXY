"""
API related helper functions
"""

from json import loads
from logging import getLogger
from typing import Union
from urllib.parse import unquote

from requests import Request, Response, Session

TIMEOUT = 20
logger = getLogger(__name__)

# Optional parameters to add to API request. This is a global
# variable so the pytest_bdd_before_scenario hook and step
# definitions can access it.
# pylint: disable=global-statement
optional_parameters = {}


def set_optional_parameter(parameter, value):
    """
    Wrapper function to set global optional parameters
    variable from step definitions
    """
    optional_parameters[parameter] = value


def get_optional_parameters() -> dict:
    """
    Wrapper function to get global optional parameters
    variable from step definitions
    """
    return optional_parameters


def clear_optional_parameters():
    """
    Wrapper function to clear global optional parameters
    at the end of each scenario
    """
    global optional_parameters
    optional_parameters = {}


# pylint: disable=too-many-arguments
def call_api(
    nhsd_apim_proxy_url: str,
    path: str,
    headers: dict,
    parameters: dict,
    verb: str = "GET",
    request_body: Union[str, dict, None] = None,
) -> Response:
    """
    Call the VRS API
    """
    if isinstance(request_body, dict):
        kwargs = {"json": request_body}
    elif isinstance(request_body, str):
        kwargs = {"data": request_body}
    else:
        kwargs = {}

    api_request = Request(
        method=verb,
        url=f"{nhsd_apim_proxy_url}{path}",
        params=parameters | get_optional_parameters(),
        headers=headers,
        **kwargs,
    )
    session = Session()
    prepped = session.prepare_request(api_request)
    try:
        api_response = session.send(prepped, timeout=TIMEOUT)
        if "_ping" in api_response.request.url:
            logger.info(
                "*********************** Call to check API is available ***********************"
            )
        else:
            logger.info(
                "************************** Call to API test scenario *************************"
            )
        logger.info(f"Request URL: {unquote(api_response.request.url)}")
        logger.info(f"Request VERB: {api_response.request.method}")
        logger.info(f"Request Headers: {api_response.request.headers}")
        logger.info(f"Response Headers: {api_response.headers}")
        logger.info(f"Response Status Code: {api_response.status_code}")
        logger.info(f"Response Body: {api_response.text.strip()}")
    except ConnectionError as error:
        logger.warning(f"API call failed with exception: {error}")
        logger.info(f"Failed Request Headers: {prepped.headers}")
        logger.info(f"Failed Request Body: {prepped.body}")
        logger.warning("Retrying the API Request")
        return call_api(
            nhsd_apim_proxy_url, path, headers, parameters, verb, request_body
        )

    return api_response
