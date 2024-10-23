"""
Unit tests for the 'CachePDS' Lambda Function
"""

from copy import deepcopy
from json import dumps
from logging import getLogger

import pytest
import requests_mock
from botocore.exceptions import ClientError

from lambdas.cache_pds_response.main import (
    CACHE_HIT,
    CACHE_KEY_HEADER,
    CACHE_MISS,
    CACHE_STATUS_HEADER,
    CachePDSResponse,
    lambda_handler,
)

event = {
    "resource": "/{proxy+}",
    "path": "/FHIR/R4/Patient/9730675953/RelatedPerson",
    "httpMethod": "GET",
    "headers": {
        "Accept": "application/json",
        "X-Request-ID": "id",
        "Authorization": "Bearer auth",
    },
    "queryStringParameters": {},
}

mock_pds_response_body = {"key": "value"}
mock_pds_response_headers = {"key": "value"}

logger = getLogger(__name__)


def _mock_dynamodb(mocker, raise_error=False):
    # Create a mock for the boto3 client
    mock_dynamodb = mocker.patch("boto3.client")

    # Mock response for a successful get_item call
    mock_item = {
        "Item": {
            "CacheKey": {"S": "key"},
            "Body": {"S": dumps(mock_pds_response_body)},
            "Headers": {"S": '{"key": "value"}'},
            "StatusCode": {"N": 200},
            "TimeToLive": {"N": 1},
        }
    }

    # Configure the mock to return the mock response when get_item is called
    instance = mock_dynamodb.return_value
    instance.get_item.return_value = mock_item

    if raise_error:
        instance = mock_dynamodb.return_value
        instance.get_item.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Internal Server Error"}}, "GetItem"
        )

    return mock_dynamodb


@pytest.fixture(name="lambda_instance")
def setup_lambda_test_instance() -> CachePDSResponse:
    """Create and return an instance of the Lambda Function Class"""
    return CachePDSResponse("pds_cache_response")


def test_get_base_url_from_event(lambda_instance) -> None:
    """
    Extract the base url to send to PDS from the event
    """

    expected = "https://int.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9730675953/RelatedPerson"
    actual = lambda_instance.get_base_url_from_event(event)

    assert actual == expected


def test_create_cache_key(lambda_instance) -> None:
    """
    Create cache key from url
    """
    url = lambda_instance.get_base_url_from_event(event)
    key = lambda_instance.create_cache_key(url)
    assert key == "a4b043e3f9e82238d2808eea034203f6958afb1a33c5c09d9ed44a28509d3c7c"


def test_create_cache_key_from_url_and_query(lambda_instance) -> None:
    """
    Create cache key from url with query string
    """
    expected = "https://int.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9730675953/RelatedPerson?"

    url = lambda_instance.get_base_url_from_event(event)
    query_string_parameters = {"parameter1": "value1,value2", "parameter2": "value"}
    key = lambda_instance.create_cache_key(url, query_string_parameters)
    assert key == "3a17ce411335505bc893f2228099cbf719d2e4a49a0930428f25984938753e0f"


def test_get_response_from_cache(lambda_instance, mocker) -> None:
    """
    See if response is already cached
    """

    mock_dynamodb = _mock_dynamodb(mocker)
    item = lambda_instance.get_response_from_cache("key")
    assert item == mock_dynamodb.return_value.get_item.return_value["Item"]


def test_no_response_in_cache(lambda_instance, mocker) -> None:
    """
    Handle error when nothing found in cache
    """
    mock_dynamodb = _mock_dynamodb(mocker, True)
    item = lambda_instance.get_response_from_cache("key")
    assert item == None


def test_pass_request_to_pds(lambda_instance) -> None:
    """
    If response is not in the cache pass to target
    """

    with requests_mock.Mocker() as m:

        expected = mock_pds_response_body

        url = lambda_instance.get_base_url_from_event(event)
        m.get(url, json=mock_pds_response_body)

        actual = lambda_instance.request(event)
        assert actual.json() == expected


def test_store_response_in_cache(lambda_instance, mocker):
    """
    Test we can store the PDS response in the cache
    """

    mock_dynamodb = _mock_dynamodb(mocker)

    url = lambda_instance.get_base_url_from_event(event)
    key = lambda_instance.create_cache_key(url)

    with requests_mock.Mocker() as m:

        m.get(url, json=mock_pds_response_body)

        pds_response = lambda_instance.request(event)
        result = lambda_instance.cache_pds_response(key, pds_response)
        logger.info(result)


@pytest.mark.parametrize(
    "cached,cache_status", [(False, CACHE_MISS), (True, CACHE_HIT)]
)
def test_lambda_handler_response(cached, cache_status, mocker, lambda_instance) -> None:
    """
    Test the whole lambda
    """
    mock_dynamodb = _mock_dynamodb(mocker, not cached)

    context = {}

    url = lambda_instance.get_base_url_from_event(event)
    key = lambda_instance.create_cache_key(url, event["queryStringParameters"])

    expected = {
        "statusCode": 200,
        "body": dumps(mock_pds_response_body),
        "headers": {
            CACHE_STATUS_HEADER: cache_status,
            CACHE_KEY_HEADER: key,
            "Content-Type": "application/json",
        }
        | mock_pds_response_headers,
    }

    with requests_mock.Mocker() as m:

        m.get(url, json=mock_pds_response_body, headers=mock_pds_response_headers)

        actual = lambda_handler(event, context)
        assert actual == expected


def test_deal_with_missing_headers(mocker, lambda_instance):
    """
    Fail gracefully if mandatory headers are missing
    """
    mock_dynamodb = _mock_dynamodb(mocker, True)

    context = {}

    url = lambda_instance.get_base_url_from_event(event)
    key = lambda_instance.create_cache_key(url, event["queryStringParameters"])

    expected = {
        "statusCode": 200,
        "body": dumps(mock_pds_response_body),
        "headers": {
            CACHE_STATUS_HEADER: CACHE_MISS,
            CACHE_KEY_HEADER: key,
            "Content-Type": "application/json",
        }
        | mock_pds_response_headers,
    }

    missing_headers_event = deepcopy(event)
    missing_headers_event["headers"] = {}

    with requests_mock.Mocker() as m:

        m.get(url, json=mock_pds_response_body, headers=mock_pds_response_headers)

        actual = lambda_handler(missing_headers_event, context)
        assert actual == expected
