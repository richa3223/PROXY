"""
Collection of tests for the verify parameters lambda function.
"""

from uuid import UUID, uuid4

import pytest
from pytest_mock import MockerFixture

from lambdas.utils.pds import errors
from lambdas.utils.pds.nhsnumber import NHSNumber
from lambdas.verify_parameters.main import VerifyParameters, lambda_handler

# NHS number constants
STANDARD_NHS_NUMBER = "9730675929"
NHS_NUMBER_09 = "9000000009"
NHS_NUMBER_17 = "9000000017"


@pytest.fixture(name="sut")
def create_sut() -> VerifyParameters:
    """Returns an instance of the sut"""
    return VerifyParameters()


@pytest.fixture(name="event")
def create_event() -> dict:
    """Returns a valid event data"""
    return {
        VerifyParameters.PARAM_PROXY_NHS_NO: NHS_NUMBER_17,
        VerifyParameters.PARAM_PATIENT_NHS_NO: NHS_NUMBER_09,
        VerifyParameters.PARAM_HEADER_ORIGINAL_URL: "test-url",
        VerifyParameters.PARAM_HEADER_CORRELATION_ID: str(uuid4()),
        VerifyParameters.PARAM_HEADER_REQUEST_ID: str(uuid4()),
    }.copy()


# VerifyParameters.start
def test_start_when_parameters_are_supplied_then_output_matches(
    sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    When parameters are supplied
    Expected Result: parameters are supplied
    """
    # Arrange
    expected = {
        VerifyParameters.PARAM_PROXY_NHS_NO: event[VerifyParameters.PARAM_PROXY_NHS_NO],
        VerifyParameters.PARAM_PATIENT_NHS_NO: event[
            VerifyParameters.PARAM_PATIENT_NHS_NO
        ],
    }
    event[VerifyParameters.PARAM_HEADER_CORRELATION_ID] = correlation_id = str(uuid4())
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert (
        sut.response[VerifyParameters.PARAM_PROXY_NHS_NO]
        == expected[VerifyParameters.PARAM_PROXY_NHS_NO]
    )
    assert (
        sut.response[VerifyParameters.PARAM_PATIENT_NHS_NO]
        == expected[VerifyParameters.PARAM_PATIENT_NHS_NO]
    )
    assert sut.response[VerifyParameters.PARAM_HEADER_CORRELATION_ID] == correlation_id


def test_start_ensure_random_correlation_id_generated(event: dict):
    """
    Test Function: VerifyParameters.start
    Scenario: Given multiple requests are made to the lambda
    When no correlation id is supplied
    Expected Result: different correlation ids are returned
    """
    # Arrange
    sut1 = VerifyParameters()

    sut1.event = event

    # Act
    sut1.start()

    # Assert
    assert sut1.response[VerifyParameters.PARAM_HEADER_CORRELATION_ID] is not None
    try:
        UUID(sut1.response[VerifyParameters.PARAM_HEADER_CORRELATION_ID])
    except ValueError:
        assert False, "Correlation ID is not a valid UUID"


def test_start_when_proxy_number_is_supplied_then_output_matches(
    sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    When only proxy number is provided
    Expected Result: proxy number is present, patient number is null
    """
    # Arrange
    expected = {
        VerifyParameters.PARAM_PROXY_NHS_NO: event[VerifyParameters.PARAM_PROXY_NHS_NO],
        VerifyParameters.PARAM_PATIENT_NHS_NO: None,
        VerifyParameters.PARAM_HEADER_CORRELATION_ID: event[
            VerifyParameters.PARAM_HEADER_CORRELATION_ID
        ],
    }
    event.pop(VerifyParameters.PARAM_PATIENT_NHS_NO)
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert (
        sut.response[VerifyParameters.PARAM_PROXY_NHS_NO]
        == expected[VerifyParameters.PARAM_PROXY_NHS_NO]
    )
    assert (
        sut.response[VerifyParameters.PARAM_PATIENT_NHS_NO]
        == expected[VerifyParameters.PARAM_PATIENT_NHS_NO]
    )
    assert sut.response[VerifyParameters.PARAM_HEADER_CORRELATION_ID] is not None


def test_start_when_proxy_number_system_url_is_supplied_then_output_matches(
    sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    When only proxy number is provided via system URL
    Expected Result: proxy number is present, patient number is null
    """
    # Arrange
    expected = {
        VerifyParameters.PARAM_PROXY_NHS_NO: event[VerifyParameters.PARAM_PROXY_NHS_NO],
        VerifyParameters.PARAM_PATIENT_NHS_NO: None,
        VerifyParameters.PARAM_HEADER_CORRELATION_ID: event[
            VerifyParameters.PARAM_HEADER_CORRELATION_ID
        ],
        VerifyParameters.PARAM_HEADER_ORIGINAL_URL: event[
            VerifyParameters.PARAM_HEADER_ORIGINAL_URL
        ],
        VerifyParameters.PARAM_INCLUDE: "",
        VerifyParameters.PARAM_HEADER_REQUEST_ID: event[
            VerifyParameters.PARAM_HEADER_REQUEST_ID
        ],
    }
    event[VerifyParameters.PARAM_PROXY_NHS_NO] = (
        f"https://fhir.nhs.uk/Id/nhs-number|{NHS_NUMBER_17}"
    )
    event.pop(VerifyParameters.PARAM_PATIENT_NHS_NO)

    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response == expected


def test_start_when_proxy_patient_number_system_url_is_supplied_then_output_matches(
    sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    When proxy & patient number is provided via system URL
    Expected Result: proxy & patient number are present
    """
    # Arrange
    expected = {
        VerifyParameters.PARAM_PROXY_NHS_NO: event[VerifyParameters.PARAM_PROXY_NHS_NO],
        VerifyParameters.PARAM_PATIENT_NHS_NO: event[
            VerifyParameters.PARAM_PATIENT_NHS_NO
        ],
        VerifyParameters.PARAM_HEADER_CORRELATION_ID: event[
            VerifyParameters.PARAM_HEADER_CORRELATION_ID
        ],
        VerifyParameters.PARAM_HEADER_ORIGINAL_URL: event[
            VerifyParameters.PARAM_HEADER_ORIGINAL_URL
        ],
        VerifyParameters.PARAM_INCLUDE: "",
        VerifyParameters.PARAM_HEADER_REQUEST_ID: event[
            VerifyParameters.PARAM_HEADER_REQUEST_ID
        ],
    }
    event[VerifyParameters.PARAM_PROXY_NHS_NO] = (
        f"https://fhir.nhs.uk/Id/nhs-number|{NHS_NUMBER_17}"
    )
    event[VerifyParameters.PARAM_PATIENT_NHS_NO] = (
        f"https://fhir.nhs.uk/Id/nhs-number|{NHS_NUMBER_09}"
    )

    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response == expected


def test_start_when_include_is_supplied_then_output_matches(
    sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    Scenario: Given include parameter is supplied with acceptable resource
    Expected Result: include parameters contains correct value on output
    """
    # Arrange
    expected = {
        VerifyParameters.PARAM_PROXY_NHS_NO: event[VerifyParameters.PARAM_PROXY_NHS_NO],
        VerifyParameters.PARAM_PATIENT_NHS_NO: event[
            VerifyParameters.PARAM_PATIENT_NHS_NO
        ],
        VerifyParameters.PARAM_HEADER_CORRELATION_ID: event[
            VerifyParameters.PARAM_HEADER_CORRELATION_ID
        ],
        VerifyParameters.PARAM_HEADER_ORIGINAL_URL: event[
            VerifyParameters.PARAM_HEADER_ORIGINAL_URL
        ],
        VerifyParameters.PARAM_INCLUDE: VerifyParameters.RELATED_PERSON_RESOURCE_INCLUDE,
        VerifyParameters.PARAM_HEADER_REQUEST_ID: event[
            VerifyParameters.PARAM_HEADER_REQUEST_ID
        ],
    }
    event[VerifyParameters.PARAM_INCLUDE] = (
        VerifyParameters.RELATED_PERSON_RESOURCE_INCLUDE
    )

    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response == expected


def test_start_when_patient_number_is_supplied_then_output_matches(
    sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    When only patient number is provided
    Expected Result: error is raised
    """

    # Arrange
    expected = errors.MISSING_IDENTIFIER_VALUE
    event.pop(VerifyParameters.PARAM_PROXY_NHS_NO)
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["error"] == expected


def test_start_when_missing_parameters_then_error_raised(
    sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    When parameters are both missing
    Expected Result: error is raised
    """
    # Arrange
    expected = errors.MISSING_IDENTIFIER_VALUE
    event.pop(VerifyParameters.PARAM_PATIENT_NHS_NO)
    event.pop(VerifyParameters.PARAM_PROXY_NHS_NO)
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["error"] == expected


def test_start_when_missing_parameters_request_url_then_error_raised(
    sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    When parameter original request URL is missing
    Expected Result: error is raised
    """
    # Arrange
    expected = errors.INTERNAL_SERVER_ERROR
    event.pop(VerifyParameters.PARAM_HEADER_ORIGINAL_URL)
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["error"] == expected


def test_start_when_parameter_request_url_is_empty_then_error_raised(
    sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    When parameter original request URL is an empty string
    Expected Result: error is raised
    """
    # Arrange
    expected = errors.INTERNAL_SERVER_ERROR
    VerifyParameters.PARAM_HEADER_ORIGINAL_URL = ""
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["error"] == expected


def test_start_when_header_present_and_valid_then_returns_parameters(
    sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    Scenario: Given header check is enabled
    When headers are all present
    AND correlation id is supplied
    Expected Result: parameters are output
    and correlation id matches
    """
    # Arrange
    expected = {
        VerifyParameters.PARAM_PROXY_NHS_NO: event[VerifyParameters.PARAM_PROXY_NHS_NO],
        VerifyParameters.PARAM_PATIENT_NHS_NO: event[
            VerifyParameters.PARAM_PATIENT_NHS_NO
        ],
    }
    event[VerifyParameters.PARAM_HEADER_CORRELATION_ID] = correlation_id = str(uuid4())
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert (
        sut.response[VerifyParameters.PARAM_PROXY_NHS_NO]
        == expected[VerifyParameters.PARAM_PROXY_NHS_NO]
    )
    assert (
        sut.response[VerifyParameters.PARAM_PATIENT_NHS_NO]
        == expected[VerifyParameters.PARAM_PATIENT_NHS_NO]
    )
    assert sut.response[VerifyParameters.PARAM_HEADER_CORRELATION_ID] == correlation_id


@pytest.mark.parametrize("request_id", [None, ""])
def test_start_when_header_request_id_invalid_then_returns_error(
    request_id: str, sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    When headers request id is invalid
    Expected Result: header error returned
    """

    # Arrange
    expected = errors.HEADER_MISSING_REQUEST_ID
    event[VerifyParameters.PARAM_HEADER_REQUEST_ID] = request_id
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["error"] == expected


@pytest.mark.parametrize("request_id", [" ", "  ", "invalid", 3, 3.14, "test-id"])
def test_start_when_header_request_id_invalid_then_returns_error(
    request_id: str, sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    When headers request id is invalid
    Expected Result: header error returned
    """

    # Arrange
    expected = errors.HEADER_INVALID_REQUEST_ID
    event[VerifyParameters.PARAM_HEADER_REQUEST_ID] = request_id
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["error"] == expected


def test_start_when_unexpected_error_then_returns_internal_error(
    sut: VerifyParameters, event: dict, mocker: MockerFixture
):
    """
    Test Function: VerifyParameters.start
    Scenario: When exception is raised
    Expected Result: error results
    """
    # Arrange
    expected = errors.INTERNAL_SERVER_ERROR

    mock = mocker.patch.object(
        VerifyParameters, "_VerifyParameters__check_headers", return_value=None
    )
    mock.side_effect = Exception()

    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["error"] == expected


@pytest.mark.parametrize("correlation_id", [" ", "  ", "invalid", 3, 3.14, "test-id"])
def test_start_when_correlation_id_is_invalid_then_returns_error(
    correlation_id: str, sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    Scenario: When correlation id is invalid
    Expected Result: error results
    """
    # Arrange
    expected = errors.HEADER_INVALID_CORRELATION_ID
    event[VerifyParameters.PARAM_HEADER_CORRELATION_ID] = correlation_id
    sut.event = event
    # Act
    sut.start()
    # Assert
    assert sut.response["error"] == expected


def test_start_identifier_missing(sut: VerifyParameters, event: dict):
    """
    Test Function: VerifyParameters.start
    Scenario: When identifier is not in the event
    Expected Result: error results
    """
    # Arrange
    expected = errors.MISSING_IDENTIFIER_VALUE
    event[VerifyParameters.PARAM_PROXY_NHS_NO] = ""
    sut.event = event
    # Act
    sut.start()
    # Assert
    assert sut.response["error"] == expected


@pytest.mark.parametrize(
    "identifier_system",
    [
        "https://test",
        "http://fhir.nhs.uk/Id/nhs-number",
        "https://fhir.nhs.uk/ID/nhs-number",
        NHSNumber.NHS_NUMBER_SYSTEM_BASE_URL.upper(),
        NHSNumber.NHS_NUMBER_SYSTEM_BASE_URL.lower(),
    ],
)
def test_start_identifier_and_patient_identifier_system_invalid(
    identifier_system: str, sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    Scenario: When identifier and patient:identifier are not in the event
    Expected Result: error results
    """
    # Arrange
    expected = errors.INVALID_IDENTIFIER_SYSTEM
    event[VerifyParameters.PARAM_PROXY_NHS_NO] = (
        f"{identifier_system}|{STANDARD_NHS_NUMBER}"
    )
    event[VerifyParameters.PARAM_PATIENT_NHS_NO] = (
        f"{identifier_system}|{STANDARD_NHS_NUMBER}"
    )
    sut.event = event
    # Act
    sut.start()
    # Assert
    assert sut.response["error"] == expected


@pytest.mark.parametrize(
    "identifier_system",
    [
        "https://test",
        "http://fhir.nhs.uk/Id/nhs-number",
        "https://fhir.nhs.uk/ID/nhs-number",
        NHSNumber.NHS_NUMBER_SYSTEM_BASE_URL.upper(),
        NHSNumber.NHS_NUMBER_SYSTEM_BASE_URL.lower(),
    ],
)
def test_start_identifier_system_invalid(
    identifier_system: str, sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    Scenario: When identifier system is not valid
    Expected Result: error results
    """
    # Arrange
    expected = errors.INVALID_IDENTIFIER_SYSTEM
    event[VerifyParameters.PARAM_PROXY_NHS_NO] = (
        f"{identifier_system}|{STANDARD_NHS_NUMBER}"
    )
    sut.event = event
    # Act
    sut.start()
    # Assert
    assert sut.response["error"] == expected


@pytest.mark.parametrize(
    "identifier_system",
    [
        "https://test",
        "http://fhir.nhs.uk/Id/nhs-number",
        "https://fhir.nhs.uk/ID/nhs-number",
        NHSNumber.NHS_NUMBER_SYSTEM_BASE_URL.upper(),
        NHSNumber.NHS_NUMBER_SYSTEM_BASE_URL.lower(),
    ],
)
def test_start_patient_identifier_system_invalid(
    identifier_system: str, sut: VerifyParameters, event: dict
):
    """
    Test Function: VerifyParameters.start
    Scenario: When identifier system is not valid
    Expected Result: error results
    """
    # Arrange
    expected = errors.INVALID_IDENTIFIER_SYSTEM
    event[VerifyParameters.PARAM_PATIENT_NHS_NO] = (
        f"{identifier_system}|{STANDARD_NHS_NUMBER}"
    )
    sut.event = event
    # Act
    sut.start()
    # Assert
    assert sut.response["error"] == expected


@pytest.mark.parametrize(
    "identifier_value,with_system",
    [
        ["973067592", False],
        ["97306759290", False],
        ["973067592", False],
        ["9730675929a", False],
        ["730675929 ", False],
        [" 973067592", False],
        ["973067592", True],
        ["97306759290", True],
        ["9730675929a", True],
        ["730675929 ", True],
        [" 973067592", True],
    ],
)
def test_start_proxy_identifier_invalid(
    identifier_value: str,
    with_system: bool,
    sut: VerifyParameters,
    event: dict,
    mocker: MockerFixture,
):
    """
    Test Function: VerifyParameters.start
    Scenario: When proxy identifier is invalid
    Expected Result: Invalid identifier error returned.
    """
    # Arrange
    expected = errors.INVALID_IDENTIFIER_VALUE
    event[VerifyParameters.PARAM_PROXY_NHS_NO] = (
        f"https://fhir.nhs.uk/Id/nhs-number|{identifier_value}"
        if with_system
        else identifier_value
    )
    sut.event = event
    # Act
    sut.start()
    # Assert
    assert sut.response["error"] == expected


@pytest.mark.parametrize(
    "identifier_value,with_system",
    [
        ["973067592", False],
        ["97306759290", False],
        ["973067592", False],
        ["9730675929a", False],
        ["730675929 ", False],
        [" 973067592", False],
        ["9730675929", True],
        ["973067592", True],
        ["97306759290", True],
        ["973067592", True],
        ["9730675929a", True],
        ["730675929 ", True],
        [" 973067592", True],
    ],
)
def test_start_patient_identifier_invalid(
    identifier_value: str,
    with_system: bool,
    sut: VerifyParameters,
    event: dict,
):
    """
    Test Function: VerifyParameters.start
    Scenario: When patient identifier is invalid
    Expected Result: error results
    """
    # Arrange
    expected = errors.INVALID_PATIENT_IDENTIFIER_VALUE
    event[VerifyParameters.PARAM_PATIENT_NHS_NO] = (
        f"https://fhir.nhs.uk/Id/nhs-number/{identifier_value}"
        if with_system
        else identifier_value
    )
    sut.event = event
    # Act
    sut.start()
    # Assert
    assert sut.response["error"] == expected


# lambda_handler tests
def test_lambda_handler_when_invoked_then_calls_start_is_called(mocker: MockerFixture):
    """
    Test Function: lambda_handler
    Scenario: When function is invoked calls underlying class
    Expected Result: Underlying function invoked once only
    """
    # Arrange
    event = {}
    context = {}
    mock = mocker.patch.object(VerifyParameters, "start", return_value=None)

    # Act
    lambda_handler(event, context)

    # Assert
    mock.assert_called_once()
