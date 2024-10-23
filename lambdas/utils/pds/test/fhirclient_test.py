""" Unit tests for the 'PDSFHIRClient' module """

from http import HTTPStatus

import pytest
from fhirclient import client
from pytest_mock import MockerFixture
from requests import Session

from lambdas.utils.pds.pdsfhirclient import PDSFHIRClient


@pytest.fixture(name="fhirclient")
def setup_pdsfhirclient_instance() -> PDSFHIRClient:
    """Returns an instance of PDSFHIRClient fake patient infromation object"""
    settings = {"app_id": "some web app", "api_base": "https://someurl"}
    smart = client.FHIRClient(settings=settings)

    return PDSFHIRClient(smart, settings["api_base"])


@pytest.fixture(name="fake_response")
def setup_fake_response(mocker: MockerFixture):
    """Returns a fake patient infromation json string"""

    fake_resp = mocker.Mock()
    fake_resp.json = mocker.Mock(return_value="{}")
    fake_resp.status_code = HTTPStatus.OK

    return fake_resp


def test_request_header_is_added_when_using_pdsfhirclient(
    mocker: MockerFixture, fhirclient: PDSFHIRClient, fake_response
):
    """Test that the X-Request-ID header is included in any requests"""

    # Arrange
    fakeresource = "someresource"
    mocked_get = mocker.patch.object(Session, "get", return_value=fake_response)

    # Act
    fhirclient.request_json(fakeresource)

    # Assert
    my_args = mocked_get.call_args
    headers = my_args[1]["headers"]
    assert "X-Request-ID" in headers


def test_additional_headers_are_included_when_using_pdsfhirclient(
    mocker: MockerFixture, fhirclient: PDSFHIRClient, fake_response
):
    """Test that any additional headers added to header collection are included in any requests"""

    # Arrange
    fakeresource = "someresource"
    fakeheader = "someheader"
    fakebody = "somebody"

    mocked_get = mocker.patch.object(Session, "get", return_value=fake_response)
    fhirclient.headers[fakeheader] = fakebody

    # Act
    fhirclient.request_json(fakeresource)

    # Assert
    my_args = mocked_get.call_args
    headers = my_args[1]["headers"]
    assert "someheader" in headers
