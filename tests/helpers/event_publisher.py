from dataclasses import dataclass

import boto3
import botocore.exceptions


@dataclass
class EventPublisher:
    """This class is responsible for publishing events to the event bridge."""

    eventbridge_client: boto3.client

    def __init__(self, eventbridge_client=None):
        self.eventbridge_client = (
            eventbridge_client
            if eventbridge_client is not None
            else self._create_eventbridge_client()
        )

    def publish(self, detail_type: str, detail: str, event_bus_name: str, source: str):
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

    def _create_eventbridge_client(
        self, client_region: str = "eu-west-2"
    ) -> boto3.client:
        return boto3.client("events", client_region)
