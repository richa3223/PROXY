import json

import boto3
import botocore.exceptions

from lambdas.utils.code_bindings.validation_result import (
    Marshaller as ValidationResult_Marshaller,
)


class EventPublisher:
    def __init__(self, eventbridge_client=None):
        self.eventbridge_client = (
            eventbridge_client
            if eventbridge_client is not None
            else self._create_eventbridge_client()
        )

    def publish(self, detail_type, detail, event_bus_name, source):
        try:
            result = self.eventbridge_client.put_events(
                Entries=[
                    {
                        "DetailType": detail_type,
                        "Detail": detail,
                        "EventBusName": event_bus_name,
                        "Source": source,
                    }
                ]
            )
            # Check if the event was sent/received by event bridge by seeing if the response includes an event id
            for result_entry in result.get("Entries", []):
                if "EventId" in result_entry:
                    return True
                else:
                    raise Exception(
                        "Event failed to send or be received by Event Bridge with error:",
                        result_entry.get("ErrorCode"),
                    )
        except botocore.exceptions.ClientError as error:
            raise error

        except botocore.exceptions.ParamValidationError as error:
            raise ValueError(
                "The parameters you provided are incorrect: {}".format(error)
            )

        finally:
            self.eventbridge_client.close()

    def _create_eventbridge_client(self, client_region="eu-west-2"):
        return boto3.client("events", client_region)


class ValidationResultEventPublisher(EventPublisher):
    def publish(self, validation_result):
        self._try_marshall(validation_result)
        event_detail_string = json.dumps(
            ValidationResult_Marshaller.marshall(validation_result.Detail)
        )
        return super().publish(
            validation_result.DetailType,
            event_detail_string,
            validation_result.EventBusName,
            validation_result.Source,
        )

    def _try_marshall(self, validation_result):
        try:
            # Try to serialise the object to JSON to validate its in the correct format
            ValidationResult_Marshaller.marshall(validation_result)
        except Exception as e:
            # Failed to serialise the object, it does not match the event schema
            raise Exception("Event object invalid, Exception encountered:" + e)
