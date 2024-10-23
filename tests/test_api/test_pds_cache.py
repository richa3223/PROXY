# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
import uuid
from pytest_bdd import given, parsers, scenarios, then, when
import requests
from ..helpers.helpers import Helpers
from ..helpers.environment_variables import WORKSPACE
import boto3
from logging import INFO, basicConfig, getLogger

logger = getLogger(__name__)
basicConfig(level=INFO)

scenarios(
    "./features/PDSCache/1_pds_cache.feature",
)


FUNCTION_NAME = f"{WORKSPACE}-pds_access_token"


@given("a unique value is created for query parameter", target_fixture="header_uuid")
def check_cached_PDS_response():
    return uuid.uuid4()


@given(parsers.parse("base url is {base_url}"), target_fixture="base_url")
def set_base_url(base_url):
    return base_url


@when(
    parsers.parse(
        "client makes a http GET request to cache for patient {patient_id} and resource {resource} with unique query param"
    ),
    target_fixture="response_returned",
)
def client_makes_get_request(
    patient_id, helpers: Helpers, header_uuid: uuid, resource, base_url
):
    access_token = helpers.invoke_lambda_function(FUNCTION_NAME, {})
    header = {
        "X-Request-ID": str(header_uuid),
        "Authorization": f"Bearer {access_token['body']['token']['access_token']}",
    }
    if resource != "empty_value":
        url = base_url + "/" + patient_id + "/" + resource
        response = requests.get(url, headers=header, params=str(header_uuid))
        return response
    else:
        url = base_url + "/" + patient_id
        response = requests.get(url, headers=header, params=str(header_uuid))
        return response


@then(parsers.parse("cache returns {status_code} status"))
def cache_return_200_status(response_returned: str, status_code):
    # assert that the cache returns 200 status code
    assert response_returned.status_code == int(status_code)


@then(
    parsers.parse(
        "the response includes X-Cache-Status header with a value {Cache_value}"
    )
)
def response_includes_hit_in_x_cache_status_header(response_returned, Cache_value: str):
    # assert that the response is returned from cache or not
    assert response_returned.headers["X-Cache-Status"] == Cache_value


@given(parsers.parse("the dynamodb record will be cleared for X-Cache-Key"))
def dynamodb_record_will_have_expected_status(cache_key_value):
    # deletes the record from dynamodb for the provide cache key
    client = boto3.client("dynamodb", region_name="eu-west-2")
    # cache_key_value = response_returned.headers[cachekey]
    key = {"CacheKey": {"S": cache_key_value}}
    DYNAMODB_TABLE_NAME = f"{WORKSPACE}-pvrs-pds-response-cache"
    rtn = client.delete_item(TableName=DYNAMODB_TABLE_NAME, Key=key)
    logger.info(f"cache key {cache_key_value} is deleted from {DYNAMODB_TABLE_NAME}")
    assert rtn["ResponseMetadata"]["HTTPStatusCode"] == 200


@then(parsers.parse("{cachekey} header is present in response"), target_fixture="cache_key_value")
def check_required_header_is_present_in_response(response_returned: str, cachekey):
        cache_key_value = response_returned.headers[cachekey]
        print(f"cache_key_value{cache_key_value}")
        return cache_key_value
