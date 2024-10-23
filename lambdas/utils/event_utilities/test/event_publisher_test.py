import uuid
from datetime import datetime

import botocore.exceptions
import pytest
from botocore.stub import Stubber

from lambdas.utils.code_bindings.validation_result import (
    Detail,
    Detail_metadata,
    Detail_sensitive,
    Detail_standard,
)
from lambdas.utils.code_bindings.validation_result import Event as ValidationResult
from lambdas.utils.event_utilities.event_publisher import ValidationResultEventPublisher


@pytest.fixture
def eventbridge_stub():
    with Stubber(
        ValidationResultEventPublisher()._create_eventbridge_client()
    ) as stubber:
        yield stubber


@pytest.fixture
def mock_validation_result_event():
    return ValidationResult(
        Detail(
            Detail_metadata(
                client_key=str(uuid.uuid4()),
                correlation_id=str(uuid.uuid4()),
                created=datetime.now(),
                request_id=str(uuid.uuid4()),
            ),
            Detail_sensitive(
                patient_identifier="9435797881", proxy_identifier="9435775039"
            ),
            Detail_standard(
                proxy_identifier_type="NHS Number",
                relationship_type="GESTM",
                validation_result_info={
                    "VALIDATED_RELATIONSHIP": "Validated relationship"
                },
            ),
        ),
        DetailType="Validation Successful",
        EventBusName="dev-event-bus",
        Source="Validation Service",
    )


def test_publish_validation_result_event(
    eventbridge_stub, mock_validation_result_event
):
    # Arrange
    eventbridge_stub.add_response("put_events", {"Entries": [{"EventId": "123"}]})

    # Act
    publisher = ValidationResultEventPublisher(
        eventbridge_client=eventbridge_stub.client
    )
    result = publisher.publish(mock_validation_result_event)

    # Assert
    assert result
    eventbridge_stub.assert_no_pending_responses()


def test__marshall_format_checker(mock_validation_result_event):
    # Act & Assert - will fail if error
    ValidationResultEventPublisher()._try_marshall(mock_validation_result_event)


def test_publish_event(eventbridge_stub, mock_validation_result_event):
    # Arrange
    eventbridge_stub.add_response("put_events", {"Entries": [{"EventId": "123"}]})

    # Act
    publisher = ValidationResultEventPublisher(
        eventbridge_client=eventbridge_stub.client
    )
    result = publisher.publish(mock_validation_result_event)

    # Assert
    assert result
    eventbridge_stub.assert_no_pending_responses()


def test_create_eventbridge_client():
    # Act
    client = ValidationResultEventPublisher()._create_eventbridge_client()

    # Assert
    assert client.meta.service_model.service_name == "events"


def test_event_publisher_raises_client_error(
    eventbridge_stub, mock_validation_result_event
):
    # Arrange
    eventbridge_stub.add_client_error("put_events", "MockError")

    # Act & Assert
    with pytest.raises(botocore.exceptions.ClientError, match="MockError"):
        with eventbridge_stub:
            publisher = ValidationResultEventPublisher(
                eventbridge_client=eventbridge_stub.client
            )
            publisher.publish(mock_validation_result_event)
