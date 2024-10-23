""" Validation Event Publish Function """

import os
import uuid
from datetime import datetime
from typing import Optional

import lambdas.utils.validation.codes as code
from lambdas.utils.code_bindings.validation_result import (
    Detail,
    Detail_metadata,
    Detail_sensitive,
    Detail_standard,
)
from lambdas.utils.code_bindings.validation_result import Event as ValidationResultClass
from lambdas.utils.event_utilities.event_publisher import ValidationResultEventPublisher


def validation_result_event(
    proxy_id: str,
    patient_id: str,
    validation_code: code.ErrorProxyValidation,
    request_id: str,
    correlation_id: Optional[str] = None,
) -> None:
    """
    Publishes a validation result event to the ValidationResultEventPublisher.

    This function creates a validation result event using the provided parameters
    and publishes it using the ValidationResultEventPublisher.

    Args:
        proxy_id (str): The NHS Number for the proxy associated with the validation.
        patient_id (str): The NHS Number for the patient associated with the validation.
        validation_code (dict): A dictionary containing information related to the validation.
        request_id (str): The request id associated with the request.
        correlation_id (str): The correlation id associated with the request (default: None).
    """

    # Correlation id is being initialised as it might be None
    # Should the parameter change to required, it can be removed
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())

    event = ValidationResultClass(
        Detail(
            Detail_metadata(
                client_key=str(uuid.uuid4()),
                correlation_id=correlation_id,
                created=datetime.now(),
                request_id=request_id,
            ),
            Detail_sensitive(patient_identifier=patient_id, proxy_identifier=proxy_id),
            Detail_standard(
                proxy_identifier_type="NHS Number",
                relationship_type=validation_code["relationship_type"],
                validation_result_info={
                    validation_code["validation_code"]: validation_code["audit_msg"]
                },
            ),
        ),
        DetailType=validation_code["audit_details_type"],
        EventBusName=os.getenv("EVENT_BUS_NAME"),
        Source="Validation Service",
    )

    publisher = ValidationResultEventPublisher()
    publisher.publish(event)
