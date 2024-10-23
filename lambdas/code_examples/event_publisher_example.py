import uuid
from datetime import datetime

from lambdas.utils.code_bindings.validation_result import (
    Detail,
    Detail_metadata,
    Detail_sensitive,
    Detail_standard,
)
from lambdas.utils.code_bindings.validation_result import Event as ValidationResult
from lambdas.utils.code_bindings.validation_result import (
    Marshaller as ValidationResultMarshaller,
)
from lambdas.utils.event_utilities.event_publisher import ValidationResultEventPublisher


class GenerateAuditEvents:
    def publish_dummy_event(self):
        publisher = ValidationResultEventPublisher()
        dummy_event = self.populate_dummy_validation_result_event()
        return publisher.publish(dummy_event)

    @staticmethod
    def populate_dummy_validation_result_event():
        dummy_result = ValidationResult()
        dummy_result.DetailType = "Validation Successful"
        dummy_result.EventBusName = "dev-event-bus"
        dummy_result.Source = "Validation Service"

        dummy_detail_metadata = Detail_metadata()
        dummy_detail_metadata.request_id = str(uuid.uuid4())
        dummy_detail_metadata.created = datetime.now()
        dummy_detail_metadata.correlation_id = str(uuid.uuid4())
        dummy_detail_metadata.client_key = str(uuid.uuid4())

        dummy_detail_sensitive = Detail_sensitive()
        dummy_detail_sensitive.patient_identifier = "9435797881"
        dummy_detail_sensitive.proxy_identifier = "9435775039"

        dummy_detail_standard = Detail_standard()
        dummy_detail_standard.proxy_identifier_type = "NHS Number"
        dummy_detail_standard.relationship_type = "GESTM"
        dummy_detail_standard.validation_result_info = {
            "VALIDATED_RELATIONSHIP": "Validated relationship"
        }

        dummy_detail = Detail(
            dummy_detail_metadata, dummy_detail_sensitive, dummy_detail_standard
        )
        dummy_result.Detail = dummy_detail
        return dummy_result

    # alternate method for creating an event
    @staticmethod
    def validation_result_event():
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
            EventBusName="main-event-bus",
            Source="Validation Service",
        )


generate_audit_events = GenerateAuditEvents()


def lambda_handler(event: dict, context: dict) -> dict:
    return generate_audit_events.publish_dummy_event()
