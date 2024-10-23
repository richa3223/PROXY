""" Unit tests for the 'PdsAccessToken' Lambda Function """

import json
from http import HTTPStatus

import jwt
import pytest
import requests
from pytest_mock import MockerFixture

from lambdas.pds_access_token.main import PdsAccessToken
from lambdas.utils.aws.secret_manager import SecretManager


@pytest.fixture(name="lambda_instance")
def setup_lambda_test_instance():
    """Create and return an instance of the Lambda Function Class"""
    return PdsAccessToken()


@pytest.mark.parametrize(
    "key",
    [
        pytest.param("private_key"),
        pytest.param("subject"),
        pytest.param("issuer"),
        pytest.param("key_id"),
    ],
)
def test_that_the_expected_secrets_loaders_are_invoked(mocker: MockerFixture, key: str):
    """Test to ensure that 'load_secrets' loads the expected secrets"""

    sut = PdsAccessToken()
    expected_value = "expectedsecretvalue"
    mocker.patch.object(SecretManager, "get_secret", return_value=expected_value)

    sut.load_secrets()

    assert expected_value == sut.SETTINGS[key]


def test_that_generate_response_returns_expected_data():
    """Test to ensure that generate response will return correct data"""

    sut = PdsAccessToken()
    status_code = HTTPStatus.OK
    tkn = "sometoken"
    expected_value = {
        "statusCode": status_code,
        "body": {"token": tkn},
    }

    sut.generate_response(status_code, tkn)

    assert sut.response == expected_value


def test_ensure_all_required_data_is_sent_when_requesting_token(mocker: MockerFixture):
    """Test to ensure that the request for token includes all fields"""

    content_string = '{ "some": "json"}'

    mock_response = mocker.Mock()
    mock_response.content = content_string
    mock_response.status_code = HTTPStatus.OK
    mocker.patch.object(requests, "post", return_value=mock_response)
    expected = {
        "statusCode": HTTPStatus.OK,
        "body": {"token": json.loads(mock_response.content)},
    }

    expected_value = "expectedsecretvalue"
    mocker.patch.object(SecretManager, "get_secret", return_value=expected_value)

    mocker.patch.object(jwt, "encode", return_value=expected_value)

    sut = PdsAccessToken()
    sut.start()

    assert sut.response == expected


def test_when_connection_error_returns_bad_result_result(mocker: MockerFixture):
    """Test to ensure that the request for token includes all fields"""
    patch_secret(mocker)

    mock_post = mocker.patch.object(requests, "post", return_value=None)
    mock_post.side_effect = requests.exceptions.ConnectionError()
    expected = {
        "statusCode": HTTPStatus.BAD_REQUEST,
        "body": {"token": None},
    }

    sut = PdsAccessToken()
    sut.start()

    assert sut.response == expected


def test_when_http_error_returns_bad_result_result(mocker: MockerFixture):
    """Test to ensure that the request for token includes all fields"""
    patch_secret(mocker)

    mock_post = mocker.patch.object(requests, "post", return_value=None)
    mock_post.side_effect = requests.exceptions.HTTPError()
    expected = {
        "statusCode": HTTPStatus.BAD_REQUEST,
        "body": {"token": None},
    }

    sut = PdsAccessToken()
    sut.start()

    assert sut.response == expected


def test_when_timeout_returns_timeout_result(mocker: MockerFixture):
    """Test to ensure that the request for token includes all fields"""
    patch_secret(mocker)

    mock_post = mocker.patch.object(requests, "post", return_value=None)
    mock_post.side_effect = requests.exceptions.Timeout()
    expected = {
        "statusCode": HTTPStatus.REQUEST_TIMEOUT,
        "body": {"token": None},
    }

    sut = PdsAccessToken()
    sut.start()

    assert sut.response == expected


def test_when_request_error_returns_internal_server_error_result(mocker: MockerFixture):
    """Test to ensure that the request for token includes all fields"""
    patch_secret(mocker)

    mock_post = mocker.patch.object(requests, "post", return_value=None)
    mock_post.side_effect = requests.exceptions.RequestException()
    expected = {
        "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
        "body": {"token": None},
    }

    sut = PdsAccessToken()
    sut.start()

    assert sut.response == expected


def test_when_unexpected_error_returns_internal_server_error_result(
    mocker: MockerFixture,
):
    """Test to ensure that the request for token includes all fields"""
    patch_secret(mocker)

    mock_post = mocker.patch.object(requests, "post", return_value=None)
    mock_post.side_effect = requests.exceptions.InvalidURL()  # Some reasonable error
    expected = {
        "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
        "body": {"token": None},
    }

    sut = PdsAccessToken()
    sut.start()

    assert sut.response == expected


def patch_secret(mocker: MockerFixture):
    """Creates a patch on get_secret to return a dummy result"""
    expected_value = "expectedsecretvalue"
    mocker.patch.object(SecretManager, "get_secret", return_value=expected_value)

    mocker.patch.object(jwt, "encode", return_value=expected_value)
