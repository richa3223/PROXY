"""Unit tests for the Validation Event Publish Function """

from pytest_mock import MockerFixture

import lambdas.utils.validation.codes as code
from lambdas.utils.code_bindings.validation_result import Event as ValidationResultClass
from lambdas.utils.event_utilities.event_publisher import ValidationResultEventPublisher
from lambdas.utils.validation.publish_validation_audit_event import (
    validation_result_event,
)


def test_validation_result_event_publish_called(mocker: MockerFixture) -> None:
    """Test that the 'publish' method of ValidationResultEventPublisher is called"""

    # Arrange
    correlation_id = "some correlation id"
    request_id = "some request id"
    mock_publish_method = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )

    # Act
    validation_result_event(
        "proxy_id", "patient_id", code.VALIDATED_PROXY, request_id, correlation_id
    )

    # Assert
    mock_publish_method.assert_called_once()

    # Check to ensure the correlation id is passed through
    assert (
        mock_publish_method.call_args_list[0].args[0].Detail.metadata.correlation_id
        == correlation_id
    )
    assert (
        mock_publish_method.call_args_list[0].args[0].Detail.metadata.request_id
        == request_id
    )


def test_validation_result_event_correct_event_structure(mocker: MockerFixture):
    """Test that the correct event structure is passed to the 'publish' method"""

    # Arrange
    correlation_id = "some correlation id"
    request_id = "some request id"
    mock_publish_method = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )

    # Act
    validation_result_event(
        "proxy_id", "patient_id", code.VALIDATED_PROXY, request_id, correlation_id
    )

    # Assert - correct event argument structure was passed
    published_event = mock_publish_method.call_args[0][0]
    assert isinstance(published_event, ValidationResultClass)
